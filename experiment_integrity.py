#!/usr/bin/env python3
"""Shared experiment integrity, reproducibility, and resource-logging helpers.

Place this file beside the RNN server, CNN server, and poisoning proxy.  The
canonical ndarray SHA-256 routine is intentionally shared across all three so a
proxy-generated poisoned update can be matched exactly to the server-received
update after the experiment.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

try:
    from jtop import jtop
except Exception:  # pragma: no cover
    jtop = None


CANONICAL_HASH_SCHEME = "fl_ndarray_bundle_sha256_v1"


def file_sha256(path: Path | str) -> str:
    source = Path(path)
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def optional_file_sha256(path: Path | str | None) -> str:
    if not path:
        return ""
    source = Path(path)
    try:
        return file_sha256(source) if source.is_file() else ""
    except Exception:
        return ""


def _canonical_array(array: Any):
    if np is None:
        raise RuntimeError("NumPy is required for canonical ndarray hashing")
    value = np.asarray(array)
    dtype = np.dtype(value.dtype)
    # Normalize multi-byte numeric arrays to little-endian so hashes are stable
    # across hosts with different native byte order. Byte-order-independent
    # one-byte/string-like dtypes keep their natural representation.
    if dtype.itemsize > 1 and dtype.byteorder not in {"|", "<"}:
        dtype = dtype.newbyteorder("<")
        value = value.astype(dtype, copy=False)
    elif dtype.itemsize > 1 and dtype.byteorder == "=":
        dtype = dtype.newbyteorder("<")
        value = value.astype(dtype, copy=False)
    value = np.ascontiguousarray(value)
    return value, np.dtype(value.dtype)


def canonical_ndarrays_sha256(arrays: Sequence[Any]) -> str:
    """Return a deterministic SHA-256 over tensor index, dtype, shape, and bytes.

    Tensor names are intentionally excluded because the transparent proxy does
    not know framework-level parameter names.  Both proxy and server therefore
    hash the ordered tensor sequence using exactly the same contract.
    """
    if np is None:
        raise RuntimeError("NumPy is required for canonical ndarray hashing")
    digest = hashlib.sha256()
    digest.update((CANONICAL_HASH_SCHEME + "\0").encode("ascii"))
    digest.update(struct.pack(">Q", len(arrays)))
    for index, array in enumerate(arrays):
        value, dtype = _canonical_array(array)
        dtype_text = dtype.str.encode("ascii", errors="strict")
        digest.update(struct.pack(">Q", index))
        digest.update(struct.pack(">I", len(dtype_text)))
        digest.update(dtype_text)
        digest.update(struct.pack(">I", value.ndim))
        for dimension in value.shape:
            digest.update(struct.pack(">q", int(dimension)))
        raw = value.tobytes(order="C")
        digest.update(struct.pack(">Q", len(raw)))
        digest.update(raw)
    return digest.hexdigest()


def set_global_reproducibility(seed: int) -> Dict[str, Any]:
    """Seed Python, NumPy and PyTorch without changing model architecture."""
    seed = int(seed)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    torch_deterministic = False
    cuda_available = False
    if torch is not None:
        torch.manual_seed(seed)
        cuda_available = bool(torch.cuda.is_available())
        if cuda_available:
            torch.cuda.manual_seed_all(seed)
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
            torch_deterministic = True
        except Exception:
            pass
        try:
            if hasattr(torch.backends, "cudnn"):
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
        except Exception:
            pass
    return {
        "experiment_seed": seed,
        "python_random_seed": seed,
        "numpy_seed": seed if np is not None else None,
        "torch_seed": seed if torch is not None else None,
        "cuda_seed": seed if cuda_available else None,
        "torch_deterministic_algorithms": torch_deterministic,
        "pythonhashseed_environment": os.environ.get("PYTHONHASHSEED", ""),
    }


def collect_dependency_versions(names: Optional[Sequence[str]] = None) -> Dict[str, str]:
    candidates = list(names or [
        "flwr", "numpy", "torch", "torchvision", "scikit-learn", "hdbscan",
        "psutil", "redis", "jetson-stats", "scipy", "pandas",
    ])
    versions: Dict[str, str] = {}
    for name in candidates:
        try:
            versions[name] = importlib.metadata.version(name)
        except Exception:
            versions[name] = "unavailable"
    return versions


def collect_code_fingerprints(paths: Iterable[Path | str]) -> Dict[str, Dict[str, str]]:
    output: Dict[str, Dict[str, str]] = {}
    for raw in paths:
        path = Path(raw).expanduser()
        key = path.name
        try:
            resolved = path.resolve()
            if resolved.is_file():
                output[key] = {
                    "path": str(resolved),
                    "sha256": file_sha256(resolved),
                }
            else:
                output[key] = {"path": str(resolved), "sha256": "missing"}
        except Exception as exc:
            output[key] = {"path": str(path), "sha256": f"error:{type(exc).__name__}"}
    return output


def _run_text(command: Sequence[str], timeout: float = 2.0) -> str:
    try:
        return subprocess.check_output(
            list(command), stderr=subprocess.STDOUT, encoding="utf-8", timeout=timeout
        ).strip()
    except Exception:
        return ""


def collect_clock_sync_metadata() -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "host": socket.gethostname(),
        "timezone": time.tzname[0] if time.tzname else "",
        "utc_offset_seconds": -time.timezone,
        "captured_at_epoch_ns": time.time_ns(),
        "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ntp_synchronized": None,
        "clock_source": "",
        "clock_offset_ms": None,
    }
    timedatectl = _run_text(["timedatectl", "show", "-p", "NTPSynchronized", "--value"])
    if timedatectl:
        result["ntp_synchronized"] = timedatectl.lower() == "yes"
        result["clock_source"] = "timedatectl"
    tracking = _run_text(["chronyc", "tracking"])
    if tracking:
        result["chrony_tracking"] = tracking
        result["clock_source"] = "chrony"
        for line in tracking.splitlines():
            if "System time" in line and "seconds" in line:
                try:
                    # Example: System time : 0.000001234 seconds fast of NTP time
                    seconds = float(line.split(":", 1)[1].strip().split()[0])
                    result["clock_offset_ms"] = seconds * 1000.0
                except Exception:
                    pass
    return result


def runtime_environment_snapshot(seed_metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "dependencies": collect_dependency_versions(),
        "clock": collect_clock_sync_metadata(),
    }
    if seed_metadata:
        result["reproducibility"] = dict(seed_metadata)
    return result


def atomic_json_dump(path: Path | str, payload: Mapping[str, Any]) -> None:
    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, destination)


def _safe_float(value: Any) -> Optional[float]:
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except Exception:
        return None


class ResourceCSVMonitor(threading.Thread):
    """Low-overhead periodic process/system resource logger.

    GPU/power values are opportunistic: Jetson uses jtop when available;
    conventional NVIDIA hosts fall back to nvidia-smi.  Missing values are
    logged as blanks rather than failing the experiment.
    """

    HEADER = [
        "timestamp_utc", "ts_wall_ns", "ts_mono_ns", "host", "pid",
        "process_cpu_percent", "system_cpu_percent", "process_rss_mb",
        "system_memory_percent", "gpu_percent", "gpu_memory_mb",
        "power_watts", "temperature_c",
    ]

    def __init__(self, path: Path | str, interval_s: float = 1.0):
        super().__init__(daemon=True, name="experiment-resource-monitor")
        self.path = Path(path).expanduser().resolve()
        self.interval_s = max(0.2, float(interval_s))
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._jtop = None
        self._process = psutil.Process(os.getpid()) if psutil is not None else None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=self.HEADER).writeheader()

    def _jetson(self):
        gpu = memory = power = temperature = None
        if self._jtop is None:
            return gpu, memory, power, temperature
        try:
            stats = self._jtop.stats
            gpu = _safe_float(stats.get("GPU") or stats.get("GR3D_FREQ"))
            power_mw = _safe_float(stats.get("Power TOT") or stats.get("Power POM_5V_IN"))
            if power_mw is not None:
                power = power_mw / 1000.0 if power_mw > 100 else power_mw
            temperature = _safe_float(stats.get("Temp GPU") or stats.get("Temp CPU"))
        except Exception:
            pass
        return gpu, memory, power, temperature

    def _nvidia(self):
        gpu = memory = power = temperature = None
        query = "utilization.gpu,memory.used,power.draw,temperature.gpu"
        output = _run_text([
            "nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"
        ])
        if output:
            try:
                first = output.splitlines()[0]
                parts = [part.strip() for part in first.split(",")]
                gpu = _safe_float(parts[0]) if len(parts) > 0 else None
                memory = _safe_float(parts[1]) if len(parts) > 1 else None
                power = _safe_float(parts[2]) if len(parts) > 2 else None
                temperature = _safe_float(parts[3]) if len(parts) > 3 else None
            except Exception:
                pass
        return gpu, memory, power, temperature

    def run(self) -> None:
        if jtop is not None:
            try:
                self._jtop = jtop()
                self._jtop.start()
            except Exception:
                self._jtop = None
        if self._process is not None:
            try:
                self._process.cpu_percent(interval=None)
            except Exception:
                pass
        while not self._stop_event.is_set():
            now = time.time_ns()
            row: Dict[str, Any] = {
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now / 1e9)),
                "ts_wall_ns": now,
                "ts_mono_ns": time.monotonic_ns(),
                "host": socket.gethostname(),
                "pid": os.getpid(),
                "process_cpu_percent": "",
                "system_cpu_percent": "",
                "process_rss_mb": "",
                "system_memory_percent": "",
                "gpu_percent": "",
                "gpu_memory_mb": "",
                "power_watts": "",
                "temperature_c": "",
            }
            if psutil is not None:
                try:
                    row["system_cpu_percent"] = psutil.cpu_percent(interval=None)
                    row["system_memory_percent"] = psutil.virtual_memory().percent
                    if self._process is not None:
                        row["process_cpu_percent"] = self._process.cpu_percent(interval=None)
                        row["process_rss_mb"] = self._process.memory_info().rss / (1024 * 1024)
                except Exception:
                    pass
            gpu, memory, power, temperature = (
                self._jetson() if self._jtop is not None else self._nvidia()
            )
            row["gpu_percent"] = "" if gpu is None else gpu
            row["gpu_memory_mb"] = "" if memory is None else memory
            row["power_watts"] = "" if power is None else power
            row["temperature_c"] = "" if temperature is None else temperature
            with self._lock:
                try:
                    with self.path.open("a", newline="", encoding="utf-8") as handle:
                        writer = csv.DictWriter(handle, fieldnames=self.HEADER)
                        writer.writerow(row)
                        handle.flush()
                except Exception:
                    pass
            self._stop_event.wait(self.interval_s)
        if self._jtop is not None:
            try:
                self._jtop.stop()
            except Exception:
                pass

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self.is_alive():
            self.join(timeout=timeout)


def extract_client_training_metadata(metrics: Mapping[str, Any] | None) -> Dict[str, Any]:
    source = metrics if isinstance(metrics, Mapping) else {}
    aliases = {
        "logical_client_id": ("logical_client_id", "stable_client_id", "device_id"),
        "device_hostname": ("device_hostname", "hostname"),
        "device_uuid": ("device_uuid", "device_uid"),
        "dataset_name": ("dataset_name", "dataset"),
        "partition_id": ("partition_id", "data_partition_id"),
        "partition_sha256": ("partition_sha256", "partition_hash", "dataset_partition_sha256"),
        "partition_hash_scheme": ("partition_hash_scheme",),
        "num_train_samples": ("num_train_samples", "train_samples"),
        "num_test_samples": ("num_test_samples", "test_samples"),
        "partition_seed": ("partition_seed",),
        "shuffle_seed": ("shuffle_seed",),
        "training_seed": ("training_seed", "seed"),
        "optimizer": ("optimizer", "optimizer_name"),
        "learning_rate": ("learning_rate", "lr"),
        "batch_size": ("batch_size",),
        "local_epochs": ("local_epochs", "epochs"),
        "weight_decay": ("weight_decay",),
        "momentum": ("momentum",),
    }
    output: Dict[str, Any] = {}
    for destination, names in aliases.items():
        value: Any = ""
        for name in names:
            if name in source and source[name] not in (None, ""):
                value = source[name]
                break
        output[destination] = value
    return output
