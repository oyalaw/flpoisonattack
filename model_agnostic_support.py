#!/usr/bin/env python3
"""Architecture-neutral transport and model-contract helpers for the FL proxy.

The module intentionally knows nothing about RNNs, CNNs, autoencoders, or
transformers.  It reasons only about:

* tensor contracts: ordered shape/dtype/byte-layout metadata,
* declared gRPC message sizes,
* bounded memory/disk resources,
* HTTP/2 flow-control credit while a DATA stream is withheld for rewriting.

The proxy can therefore discover and match arbitrary transmitted model objects
without a model-name switch or a fixed tensor count.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

MODEL_CONTRACT_HASH_SCHEME = "fl_tensor_contract_sha256_v1"
HTTP2_WINDOW_UPDATE = 0x8
HTTP2_MAX_WINDOW_INCREMENT = (1 << 31) - 1


def _canonical_dtype(dtype: np.dtype) -> str:
    """Return a byte-order-explicit canonical NumPy dtype string."""
    dt = np.dtype(dtype)
    # Normalize native byte order to explicit little/big endian so contracts
    # remain stable across equivalent hosts.
    if dt.byteorder == "=":
        byteorder = "<" if np.little_endian else ">"
        dt = dt.newbyteorder(byteorder)
    return dt.str


def tensor_contract(block: Sequence[np.ndarray]) -> Dict[str, object]:
    tensors: List[Dict[str, object]] = []
    total_elements = 0
    total_bytes = 0
    for index, array in enumerate(block):
        value = np.asarray(array)
        nbytes = int(value.nbytes)
        elements = int(value.size)
        tensors.append(
            {
                "index": index,
                "shape": [int(v) for v in value.shape],
                "dtype": _canonical_dtype(value.dtype),
                "elements": elements,
                "nbytes": nbytes,
                "c_contiguous": bool(value.flags.c_contiguous),
                "f_contiguous": bool(value.flags.f_contiguous),
            }
        )
        total_elements += elements
        total_bytes += nbytes
    payload = {
        "scheme": MODEL_CONTRACT_HASH_SCHEME,
        "tensor_count": len(tensors),
        "total_elements": total_elements,
        "total_bytes": total_bytes,
        "tensors": tensors,
    }
    # Structural matching intentionally ignores transient C/F contiguity flags.
    # Two semantically identical model tensors must match even if one NumPy
    # array was copied into a different host-memory layout.
    canonical_payload = {
        "scheme": MODEL_CONTRACT_HASH_SCHEME,
        "tensor_count": len(tensors),
        "total_elements": total_elements,
        "total_bytes": total_bytes,
        "tensors": [
            {
                "index": item["index"],
                "shape": item["shape"],
                "dtype": item["dtype"],
                "elements": item["elements"],
                "nbytes": item["nbytes"],
            }
            for item in tensors
        ],
    }
    canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def contract_summary_fields(block: Sequence[np.ndarray]) -> Dict[str, object]:
    contract = tensor_contract(block)
    tensors = contract["tensors"]
    return {
        "model_contract_hash_scheme": MODEL_CONTRACT_HASH_SCHEME,
        "model_contract_sha256": contract["sha256"],
        "model_contract_tensor_count": contract["tensor_count"],
        "model_contract_total_elements": contract["total_elements"],
        "model_contract_total_bytes": contract["total_bytes"],
        "model_contract_shapes_json": json.dumps(
            [item["shape"] for item in tensors], separators=(",", ":")
        ),
        "model_contract_dtypes_json": json.dumps(
            [item["dtype"] for item in tensors], separators=(",", ":")
        ),
    }


@dataclass(frozen=True)
class MessagePolicyDecision:
    allowed: bool
    reason: str
    declared_bytes: int
    memory_threshold_bytes: int
    hard_limit_bytes: int
    available_disk_bytes: int
    buffer_mode: str


class MessageSizePolicy:
    """Resource safety policy that is independent of model architecture.

    `max_message_mb == 0` means there is no model-size-specific soft cap.  A
    separate hard safety ceiling remains to protect the host from malformed
    length prefixes.  Large messages are spooled to disk once they exceed the
    memory threshold.
    """

    def __init__(
        self,
        *,
        max_message_mb: int = 0,
        hard_max_message_gb: float = 8.0,
        spool_threshold_mb: int = 64,
        spool_dir: Union[str, os.PathLike] = ".proxy_spool",
        disk_reserve_mb: int = 1024,
    ) -> None:
        self.max_message_mb = max(0, int(max_message_mb))
        self.hard_max_message_gb = max(0.25, float(hard_max_message_gb))
        self.spool_threshold_mb = max(1, int(spool_threshold_mb))
        self.spool_dir = Path(spool_dir).expanduser().resolve()
        self.disk_reserve_mb = max(0, int(disk_reserve_mb))
        self.spool_dir.mkdir(parents=True, exist_ok=True)

    @property
    def memory_threshold_bytes(self) -> int:
        return self.spool_threshold_mb * 1024 * 1024

    @property
    def hard_limit_bytes(self) -> int:
        hard = int(self.hard_max_message_gb * 1024 * 1024 * 1024)
        if self.max_message_mb > 0:
            hard = min(hard, self.max_message_mb * 1024 * 1024)
        return max(1, hard)

    def decide(self, declared_bytes: int) -> MessagePolicyDecision:
        declared = int(declared_bytes)
        try:
            available_disk = int(shutil.disk_usage(self.spool_dir).free)
        except Exception:
            available_disk = 0
        if declared <= 0:
            return MessagePolicyDecision(
                False,
                "nonpositive_declared_length",
                declared,
                self.memory_threshold_bytes,
                self.hard_limit_bytes,
                available_disk,
                "reject",
            )
        if declared > self.hard_limit_bytes:
            return MessagePolicyDecision(
                False,
                "declared_length_exceeds_hard_safety_limit",
                declared,
                self.memory_threshold_bytes,
                self.hard_limit_bytes,
                available_disk,
                "reject",
            )
        mode = "memory" if declared <= self.memory_threshold_bytes else "disk_spool"
        if mode == "disk_spool":
            reserve = self.disk_reserve_mb * 1024 * 1024
            # Need enough room for input spool plus some operational reserve.
            if available_disk and available_disk < declared + reserve:
                return MessagePolicyDecision(
                    False,
                    "insufficient_disk_for_spool",
                    declared,
                    self.memory_threshold_bytes,
                    self.hard_limit_bytes,
                    available_disk,
                    "reject",
                )
        return MessagePolicyDecision(
            True,
            "allowed",
            declared,
            self.memory_threshold_bytes,
            self.hard_limit_bytes,
            available_disk,
            mode,
        )


def build_http2_frame_header(length: int, frame_type: int, flags: int, stream_id: int) -> bytes:
    return (
        int(length).to_bytes(3, "big")
        + bytes([frame_type & 0xFF, flags & 0xFF])
        + (int(stream_id) & 0x7FFFFFFF).to_bytes(4, "big")
    )


def build_window_update_frame(stream_id: int, increment: int) -> bytes:
    value = int(increment)
    if value <= 0 or value > HTTP2_MAX_WINDOW_INCREMENT:
        raise ValueError(f"invalid HTTP/2 WINDOW_UPDATE increment: {value}")
    payload = (value & HTTP2_MAX_WINDOW_INCREMENT).to_bytes(4, "big")
    return build_http2_frame_header(4, HTTP2_WINDOW_UPDATE, 0, stream_id) + payload


def split_window_increment(total: int) -> Iterable[int]:
    remaining = int(total)
    while remaining > 0:
        part = min(remaining, HTTP2_MAX_WINDOW_INCREMENT)
        yield part
        remaining -= part


class FlowControlBridge:
    """Balances synthetic HTTP/2 credit used while withholding upload DATA.

    The client->server rewriter may need the complete gRPC message before any
    DATA is forwarded.  A large sender would otherwise stall when its HTTP/2
    stream window is exhausted.  This bridge grants temporary connection- and
    stream-level WINDOW_UPDATE credit directly to the client.  Later, when the
    real server emits WINDOW_UPDATE frames after receiving the rewritten DATA,
    equivalent credit is suppressed so the client does not receive double
    credit.
    """

    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.client_send_lock = threading.RLock()
        self.synthetic_connection_credit = 0
        self.synthetic_stream_credit: Dict[int, int] = defaultdict(int)
        self.total_granted = 0
        self.total_suppressed = 0

    def grant(self, client_sock, stream_id: int, byte_count: int) -> int:
        amount = max(0, int(byte_count))
        if amount <= 0 or int(stream_id) <= 0:
            return 0
        frames: List[bytes] = []
        for part in split_window_increment(amount):
            frames.append(build_window_update_frame(0, part))
            frames.append(build_window_update_frame(int(stream_id), part))
        with self.lock:
            self.synthetic_connection_credit += amount
            self.synthetic_stream_credit[int(stream_id)] += amount
            self.total_granted += amount
        with self.client_send_lock:
            for frame in frames:
                client_sock.sendall(frame)
        return amount

    def adjust_server_window_update(self, stream_id: int, increment: int) -> int:
        sid = int(stream_id)
        value = max(0, int(increment))
        if value <= 0:
            return 0
        with self.lock:
            if sid == 0:
                available = self.synthetic_connection_credit
                consumed = min(value, available)
                self.synthetic_connection_credit -= consumed
            else:
                available = self.synthetic_stream_credit.get(sid, 0)
                consumed = min(value, available)
                remaining_credit = available - consumed
                if remaining_credit:
                    self.synthetic_stream_credit[sid] = remaining_credit
                else:
                    self.synthetic_stream_credit.pop(sid, None)
            self.total_suppressed += consumed
        return value - consumed

    def snapshot(self) -> Dict[str, object]:
        with self.lock:
            return {
                "synthetic_connection_credit_outstanding": self.synthetic_connection_credit,
                "synthetic_stream_credit_outstanding": dict(self.synthetic_stream_credit),
                "flow_control_synthetic_credit_bytes": self.total_granted,
                "flow_control_server_credit_suppressed_bytes": self.total_suppressed,
            }


@dataclass
class _BytesSegment:
    data: bytes
    offset: int = 0

    @property
    def remaining(self) -> int:
        return len(self.data) - self.offset

    def read(self, size: int) -> bytes:
        take = min(self.remaining, int(size))
        out = self.data[self.offset : self.offset + take]
        self.offset += take
        return out

    def close(self) -> None:
        return None


@dataclass
class _FileSegment:
    path: Path
    size: int
    delete_on_close: bool = True
    offset: int = 0
    _handle: object = None

    @property
    def remaining(self) -> int:
        return self.size - self.offset

    def _ensure_open(self):
        if self._handle is None:
            self._handle = self.path.open("rb")
        return self._handle

    def read(self, size: int) -> bytes:
        take = min(self.remaining, int(size))
        handle = self._ensure_open()
        handle.seek(self.offset)
        out = handle.read(take)
        self.offset += len(out)
        return out

    def close(self) -> None:
        try:
            if self._handle is not None:
                self._handle.close()
        finally:
            self._handle = None
            if self.delete_on_close:
                try:
                    self.path.unlink(missing_ok=True)
                except Exception:
                    pass


class AdaptiveOutputQueue:
    """FIFO output stream that can mix RAM bytes and file-backed segments."""

    def __init__(self) -> None:
        self._segments: Deque[object] = deque()
        self._available = 0

    @property
    def available(self) -> int:
        return self._available

    def append_bytes(self, data: bytes) -> None:
        if not data:
            return
        payload = bytes(data)
        self._segments.append(_BytesSegment(payload))
        self._available += len(payload)

    def append_file(self, path: Union[str, os.PathLike], size: int, *, delete_on_close: bool = True) -> None:
        size = int(size)
        if size <= 0:
            if delete_on_close:
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception:
                    pass
            return
        self._segments.append(_FileSegment(Path(path), size, delete_on_close=delete_on_close))
        self._available += size

    def read(self, size: int) -> bytes:
        need = min(max(0, int(size)), self._available)
        parts: List[bytes] = []
        while need > 0 and self._segments:
            segment = self._segments[0]
            chunk = segment.read(need)
            if not chunk:
                segment.close()
                self._segments.popleft()
                continue
            parts.append(chunk)
            consumed = len(chunk)
            self._available -= consumed
            need -= consumed
            if segment.remaining <= 0:
                segment.close()
                self._segments.popleft()
        return b"".join(parts)

    def close(self) -> None:
        while self._segments:
            segment = self._segments.popleft()
            try:
                segment.close()
            except Exception:
                pass
        self._available = 0
