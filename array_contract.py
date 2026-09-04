#!/usr/bin/env python3
"""Array/block utilities shared by the live FL poisoning proxy.

V27 notes
---------
The proxy operates on ordered lists of NumPy arrays. Every transformation must
preserve tensor count, tensor order, shapes, dtypes, and serialized byte length.

This revision keeps the original API but makes the geometry helpers memory-aware:
large blocks are processed chunk-by-chunk instead of first concatenating every
tensor into a single float64 vector. ``flatten_block`` remains available for
callers that explicitly need a dense vector and now accepts a dtype override.
"""
from __future__ import annotations

import hashlib
import json
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

import numpy as np

Block = List[np.ndarray]

DEFAULT_CHUNK_ELEMENTS = 1_000_000


def clone_block(block: Sequence[np.ndarray]) -> Block:
    return [np.array(arr, copy=True) for arr in block]


def tensor_signature(block: Sequence[np.ndarray]) -> Tuple[Tuple[Tuple[int, ...], str, int], ...]:
    return tuple((tuple(int(x) for x in arr.shape), np.dtype(arr.dtype).str, int(arr.nbytes)) for arr in block)


def signature_json(block: Sequence[np.ndarray]) -> str:
    return json.dumps(
        [
            {"shape": list(arr.shape), "dtype": np.dtype(arr.dtype).str, "nbytes": int(arr.nbytes)}
            for arr in block
        ],
        separators=(",", ":"),
        sort_keys=True,
    )


def signature_hash(block: Sequence[np.ndarray]) -> str:
    return hashlib.sha256(signature_json(block).encode("utf-8")).hexdigest()


def block_hash(block: Sequence[np.ndarray]) -> str:
    digest = hashlib.sha256()
    digest.update(signature_json(block).encode("utf-8"))
    for arr in block:
        digest.update(np.ascontiguousarray(arr).tobytes(order="C"))
    return digest.hexdigest()


def block_total_elements(block: Sequence[np.ndarray]) -> int:
    return int(sum(int(np.asarray(arr).size) for arr in block))


def block_total_bytes(block: Sequence[np.ndarray]) -> int:
    return int(sum(int(np.asarray(arr).nbytes) for arr in block))


def assert_wire_compatible(reference: Sequence[np.ndarray], candidate: Sequence[np.ndarray]) -> None:
    if len(reference) != len(candidate):
        raise ValueError(f"tensor count changed: {len(reference)} -> {len(candidate)}")
    for index, (before, after) in enumerate(zip(reference, candidate)):
        if tuple(before.shape) != tuple(after.shape):
            raise ValueError(
                f"tensor {index} shape changed: {tuple(before.shape)} -> {tuple(after.shape)}"
            )
        if np.dtype(before.dtype) != np.dtype(after.dtype):
            raise ValueError(
                f"tensor {index} dtype changed: {before.dtype} -> {after.dtype}"
            )
        if int(before.nbytes) != int(after.nbytes):
            raise ValueError(
                f"tensor {index} byte length changed: {before.nbytes} -> {after.nbytes}"
            )


def assert_same_structure(left: Sequence[np.ndarray], right: Sequence[np.ndarray]) -> None:
    if tensor_signature(left) != tensor_signature(right):
        raise ValueError("model tensor signatures do not match")


def subtract_blocks(local_model: Sequence[np.ndarray], global_model: Sequence[np.ndarray]) -> Block:
    assert_same_structure(local_model, global_model)
    return [
        (local.astype(np.float64) - global_arr.astype(np.float64)).astype(local.dtype)
        for local, global_arr in zip(local_model, global_model)
    ]


def add_blocks(global_model: Sequence[np.ndarray], update: Sequence[np.ndarray]) -> Block:
    assert_same_structure(global_model, update)
    result = [
        (global_arr.astype(np.float64) + delta.astype(np.float64)).astype(global_arr.dtype)
        for global_arr, delta in zip(global_model, update)
    ]
    assert_wire_compatible(global_model, result)
    return result


def flatten_block(block: Sequence[np.ndarray], dtype=np.float64) -> np.ndarray:
    """Concatenate tensors in C-order.

    ``dtype`` defaults to float64 for backward compatibility. For large-model
    geometry, callers may request float32 to halve the dense-vector memory cost.
    """
    if not block:
        return np.empty((0,), dtype=dtype)
    return np.concatenate([np.asarray(arr, dtype=dtype).ravel(order="C") for arr in block])


def unflatten_block(vector: np.ndarray, template: Sequence[np.ndarray]) -> Block:
    """Reshape a flat vector back into the template's tensor structure.

    Preserves tensor count, order, shapes, and dtypes. The input dtype is not
    forced to float64, which avoids an unnecessary full-vector copy for large
    CNN/transformer models.
    """
    flat = np.asarray(vector).ravel(order="C")
    out: Block = []
    offset = 0
    for tensor in template:
        count = int(np.asarray(tensor).size)
        chunk = flat[offset:offset + count]
        if chunk.size != count:
            raise ValueError(
                f"cannot unflatten: template needs {count} values at offset "
                f"{offset} but only {chunk.size} remain"
            )
        out.append(chunk.reshape(np.asarray(tensor).shape).astype(tensor.dtype, copy=False))
        offset += count
    if offset != flat.size:
        raise ValueError(
            f"cannot unflatten vector of length {flat.size}; template consumes {offset}"
        )
    assert_wire_compatible(list(template), out)
    return out


def _iter_chunks(array: np.ndarray, *, chunk_elements: int = DEFAULT_CHUNK_ELEMENTS) -> Iterator[np.ndarray]:
    flat = np.asarray(array).ravel(order="C")
    step = max(1, int(chunk_elements))
    for start in range(0, flat.size, step):
        yield flat[start:start + step]


def iter_block_chunks(
    block: Sequence[np.ndarray],
    *,
    dtype=np.float64,
    chunk_elements: int = DEFAULT_CHUNK_ELEMENTS,
) -> Iterator[np.ndarray]:
    for arr in block:
        for chunk in _iter_chunks(np.asarray(arr), chunk_elements=chunk_elements):
            yield np.asarray(chunk, dtype=dtype)


def block_l2_norm(block: Sequence[np.ndarray], *, chunk_elements: int = DEFAULT_CHUNK_ELEMENTS) -> float:
    total = 0.0
    for chunk in iter_block_chunks(block, dtype=np.float64, chunk_elements=chunk_elements):
        total += float(np.dot(chunk, chunk))
    return float(np.sqrt(max(total, 0.0)))


def block_l1_norm(block: Sequence[np.ndarray], *, chunk_elements: int = DEFAULT_CHUNK_ELEMENTS) -> float:
    total = 0.0
    for chunk in iter_block_chunks(block, dtype=np.float64, chunk_elements=chunk_elements):
        total += float(np.sum(np.abs(chunk), dtype=np.float64))
    return float(total)


def cosine_similarity(
    left: Sequence[np.ndarray],
    right: Sequence[np.ndarray],
    *,
    chunk_elements: int = DEFAULT_CHUNK_ELEMENTS,
) -> float:
    assert_same_structure(left, right)
    dot = 0.0
    left_sq = 0.0
    right_sq = 0.0
    for l_arr, r_arr in zip(left, right):
        l_flat = np.asarray(l_arr).ravel(order="C")
        r_flat = np.asarray(r_arr).ravel(order="C")
        step = max(1, int(chunk_elements))
        for start in range(0, l_flat.size, step):
            l = np.asarray(l_flat[start:start + step], dtype=np.float64)
            r = np.asarray(r_flat[start:start + step], dtype=np.float64)
            dot += float(np.dot(l, r))
            left_sq += float(np.dot(l, l))
            right_sq += float(np.dot(r, r))
    denom = float(np.sqrt(left_sq) * np.sqrt(right_sq))
    if denom <= 0.0:
        return 0.0
    return float(dot / denom)


def euclidean_distance(
    left: Sequence[np.ndarray],
    right: Sequence[np.ndarray],
    *,
    chunk_elements: int = DEFAULT_CHUNK_ELEMENTS,
) -> float:
    assert_same_structure(left, right)
    total = 0.0
    step = max(1, int(chunk_elements))
    for l_arr, r_arr in zip(left, right):
        l_flat = np.asarray(l_arr).ravel(order="C")
        r_flat = np.asarray(r_arr).ravel(order="C")
        for start in range(0, l_flat.size, step):
            l = np.asarray(l_flat[start:start + step], dtype=np.float64)
            r = np.asarray(r_flat[start:start + step], dtype=np.float64)
            diff = l - r
            total += float(np.dot(diff, diff))
    return float(np.sqrt(max(total, 0.0)))


def deterministic_sketch(
    block: Sequence[np.ndarray],
    *,
    max_dimensions: int = 8192,
    dtype=np.float32,
) -> np.ndarray:
    """Return an architecture-neutral deterministic coordinate sketch.

    The same tensor contract always selects the same evenly spaced global
    coordinates, so candidate and peer updates can be compared without
    materializing an entire CNN/transformer update matrix.
    """
    total = block_total_elements(block)
    if total <= 0:
        return np.empty((0,), dtype=dtype)
    dim = max(1, int(max_dimensions))
    if total <= dim:
        return flatten_block(block, dtype=dtype)

    indices = np.linspace(0, total - 1, num=dim, dtype=np.int64)
    out = np.empty((dim,), dtype=dtype)
    cumulative = 0
    out_pos = 0
    for arr in block:
        flat = np.asarray(arr).ravel(order="C")
        end = cumulative + flat.size
        right = int(np.searchsorted(indices, end, side="left"))
        if right > out_pos:
            local_indices = indices[out_pos:right] - cumulative
            out[out_pos:right] = np.asarray(flat[local_indices], dtype=dtype)
            out_pos = right
        cumulative = end
        if out_pos >= dim:
            break
    if out_pos != dim:
        raise RuntimeError(f"deterministic sketch filled {out_pos}/{dim} coordinates")
    return out
