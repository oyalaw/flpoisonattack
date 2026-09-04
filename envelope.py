#!/usr/bin/env python3
"""Robust benign-update envelope used by the update-space poisoner.

V27 keeps the original public API while making the implementation safer for
large CNN/transformer updates. Large tensors use float32 working buffers where
appropriate, full-block norms are computed streaming, and callers may request a
deterministic low-dimensional geometry matrix instead of a dense full update
matrix.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

from array_contract import (
    Block,
    assert_same_structure,
    block_l2_norm,
    block_total_elements,
    clone_block,
    deterministic_sketch,
    flatten_block,
)


@dataclass
class EnvelopeSummary:
    observations: int
    tensor_count: int
    coordinate_containment_fraction: float
    norm_containment_fraction: float
    mean_direction_cosine: float
    global_norm_contained: float = 0.0
    global_direction_cosine: float = 0.0


class Envelope:
    def __init__(
        self,
        min_observations: int = 3,
        max_observations: int = 0,
        *,
        large_tensor_float32_threshold_elements: int = 2_000_000,
    ):
        self.min_observations = max(1, int(min_observations))
        self.max_observations = max(0, int(max_observations))
        self.large_tensor_float32_threshold_elements = max(
            1, int(large_tensor_float32_threshold_elements)
        )
        self._blocks: List[Block] = []
        self._cache = {}

    @property
    def n_observations(self) -> int:
        return len(self._blocks)

    @property
    def ready(self) -> bool:
        return self.n_observations >= self.min_observations

    @property
    def tensor_count(self) -> int:
        return len(self._blocks[0]) if self._blocks else 0

    @property
    def total_elements(self) -> int:
        return block_total_elements(self._blocks[0]) if self._blocks else 0

    def clear(self) -> None:
        self._blocks.clear()
        self._cache.clear()

    def blocks_snapshot(self, *, copy_blocks: bool = True) -> List[Block]:
        if copy_blocks:
            return [clone_block(block) for block in self._blocks]
        return list(self._blocks)

    def observe(self, block: Sequence[np.ndarray], *, copy_block: bool = True) -> None:
        if not block:
            raise ValueError("empty update block")
        if self._blocks:
            assert_same_structure(self._blocks[0], block)
        stored = clone_block(block) if copy_block else [np.asarray(arr) for arr in block]
        self._blocks.append(stored)
        if self.max_observations > 0 and len(self._blocks) > self.max_observations:
            del self._blocks[: len(self._blocks) - self.max_observations]
        self._cache.clear()

    def _working_dtype_for_tensor(self, tensor_index: int):
        if not self._blocks:
            return np.float64
        if self.total_elements >= self.large_tensor_float32_threshold_elements:
            return np.float32
        size = int(np.asarray(self._blocks[0][tensor_index]).size)
        return np.float32 if size >= self.large_tensor_float32_threshold_elements else np.float64

    def _global_working_dtype(self):
        return (
            np.float32
            if self.total_elements >= self.large_tensor_float32_threshold_elements
            else np.float64
        )

    def coordinate_bounds(self, k: float = 3.0) -> List[Tuple[np.ndarray, np.ndarray]]:
        if not self.ready:
            raise ValueError("envelope is not ready")
        multiplier = max(0.0, float(k))
        cache_key = ("coordinate_bounds", multiplier)
        if cache_key in self._cache:
            return self._cache[cache_key]
        bounds: List[Tuple[np.ndarray, np.ndarray]] = []
        for tensor_index in range(self.tensor_count):
            dtype = self._working_dtype_for_tensor(tensor_index)
            n_obs = len(self._blocks)
            if n_obs == 1:
                only = np.asarray(self._blocks[0][tensor_index], dtype=dtype)
                lower = np.array(only, copy=True)
                upper = np.array(only, copy=True)
            elif n_obs == 2:
                # For two observations the robust envelope collapses to their
                # observed min/max. Avoid np.stack/median temporaries on a
                # multi-million-coordinate CNN tensor.
                first = np.asarray(self._blocks[0][tensor_index], dtype=dtype)
                second = np.asarray(self._blocks[1][tensor_index], dtype=dtype)
                lower = np.minimum(first, second)
                upper = np.maximum(first, second)
            else:
                stack = np.stack(
                    [np.asarray(block[tensor_index], dtype=dtype) for block in self._blocks],
                    axis=0,
                )
                median = np.median(stack, axis=0)
                mad = np.median(np.abs(stack - median), axis=0)
                robust_scale = 1.4826 * mad
                lower = median - multiplier * robust_scale
                upper = median + multiplier * robust_scale
                observed_min = np.min(stack, axis=0)
                observed_max = np.max(stack, axis=0)
                lower = np.minimum(lower, observed_min)
                upper = np.maximum(upper, observed_max)
            bounds.append((lower, upper))
        self._cache[cache_key] = bounds
        return bounds

    def norm_band(self, k: float = 3.0) -> List[Tuple[float, float]]:
        if not self.ready:
            raise ValueError("envelope is not ready")
        multiplier = max(0.0, float(k))
        cache_key = ("norm_band", multiplier)
        if cache_key in self._cache:
            return self._cache[cache_key]
        bands: List[Tuple[float, float]] = []
        for tensor_index in range(self.tensor_count):
            norms = np.asarray(
                [
                    float(np.linalg.norm(np.asarray(block[tensor_index]).ravel()))
                    for block in self._blocks
                ],
                dtype=np.float64,
            )
            median = float(np.median(norms))
            mad = float(np.median(np.abs(norms - median)))
            scale = 1.4826 * mad
            low = max(0.0, median - multiplier * scale)
            high = max(low, median + multiplier * scale)
            low = min(low, float(np.min(norms)))
            high = max(high, float(np.max(norms)))
            bands.append((low, high))
        self._cache[cache_key] = bands
        return bands

    def direction_gate(self) -> List[Tuple[Optional[np.ndarray], float]]:
        if not self.ready:
            raise ValueError("envelope is not ready")
        cache_key = ("direction_gate",)
        if cache_key in self._cache:
            return self._cache[cache_key]
        output: List[Tuple[Optional[np.ndarray], float]] = []
        for tensor_index in range(self.tensor_count):
            dtype = self._working_dtype_for_tensor(tensor_index)
            units = []
            shape = self._blocks[0][tensor_index].shape
            for block in self._blocks:
                flat = np.asarray(block[tensor_index], dtype=dtype).ravel()
                norm = float(np.linalg.norm(flat))
                if norm > 0.0:
                    units.append(flat / norm)
            if not units:
                output.append((None, 0.0))
                continue
            mean_vector = np.zeros_like(units[0], dtype=dtype)
            for unit in units:
                mean_vector += unit.astype(dtype, copy=False)
            mean_vector /= float(len(units))
            concentration = float(np.linalg.norm(mean_vector))
            if concentration <= 0.0:
                output.append((None, 0.0))
                continue
            mean_direction = (mean_vector / concentration).reshape(shape)
            output.append((mean_direction, min(1.0, concentration)))
        self._cache[cache_key] = output
        return output

    def _flat(self, block: Sequence[np.ndarray], *, dtype=None) -> np.ndarray:
        return flatten_block(block, dtype=dtype or self._global_working_dtype())

    def global_norm_band(self, k: float = 3.0) -> Tuple[float, float]:
        """Robust band on the L2 norm of the fully concatenated update."""
        if not self.ready:
            raise ValueError("envelope is not ready")
        multiplier = max(0.0, float(k))
        cache_key = ("global_norm_band", multiplier)
        if cache_key in self._cache:
            return self._cache[cache_key]
        norms = np.asarray([block_l2_norm(block) for block in self._blocks], dtype=np.float64)
        median = float(np.median(norms))
        mad = float(np.median(np.abs(norms - median)))
        scale = 1.4826 * mad
        low = max(0.0, median - multiplier * scale)
        high = max(low, median + multiplier * scale)
        low = min(low, float(np.min(norms)))
        high = max(high, float(np.max(norms)))
        result = (low, high)
        self._cache[cache_key] = result
        return result

    def global_direction(self, *, dtype=None) -> Tuple[Optional[np.ndarray], float]:
        """Mean unit direction of the concatenated update, with concentration."""
        if not self.ready:
            raise ValueError("envelope is not ready")
        working_dtype = dtype or self._global_working_dtype()
        cache_key = ("global_direction", np.dtype(working_dtype).str)
        if cache_key in self._cache:
            return self._cache[cache_key]
        units = []
        for block in self._blocks:
            flat = self._flat(block, dtype=working_dtype)
            norm = float(np.linalg.norm(flat))
            if norm > 0.0:
                units.append(flat / norm)
        if not units:
            return None, 0.0
        mean_vector = np.mean(np.stack(units, axis=0), axis=0, dtype=working_dtype)
        concentration = float(np.linalg.norm(mean_vector))
        if concentration <= 0.0:
            return None, 0.0
        result = (mean_vector / concentration, min(1.0, concentration))
        self._cache[cache_key] = result
        return result


    def global_direction_sketch(
        self,
        *,
        max_dimensions: int = 8192,
        dtype=np.float32,
    ) -> Tuple[Optional[np.ndarray], float]:
        """Mean unit direction in deterministic sketch space for large models."""
        if not self.ready:
            raise ValueError("envelope is not ready")
        key = ("global_direction_sketch", int(max_dimensions), np.dtype(dtype).str)
        if key in self._cache:
            return self._cache[key]
        mean = None
        count = 0
        for block in self._blocks:
            vec = deterministic_sketch(block, max_dimensions=max_dimensions, dtype=dtype)
            norm = float(np.linalg.norm(vec))
            if norm <= 0.0:
                continue
            unit = vec / norm
            if mean is None:
                mean = np.zeros_like(unit, dtype=dtype)
            mean += unit.astype(dtype, copy=False)
            count += 1
        if mean is None or count == 0:
            result = (None, 0.0)
        else:
            mean /= float(count)
            concentration = float(np.linalg.norm(mean))
            result = (
                (mean / concentration).astype(dtype, copy=False) if concentration > 0 else None,
                min(1.0, concentration),
            )
        self._cache[key] = result
        return result

    def global_direction_cosine_sketch(
        self,
        block: Sequence[np.ndarray],
        *,
        max_dimensions: int = 8192,
    ) -> float:
        if not self.ready:
            return 0.0
        direction, _ = self.global_direction_sketch(max_dimensions=max_dimensions, dtype=np.float32)
        if direction is None:
            return 0.0
        vec = deterministic_sketch(block, max_dimensions=max_dimensions, dtype=np.float32)
        denom = float(np.linalg.norm(vec) * np.linalg.norm(direction))
        return float(np.dot(vec, direction) / denom) if denom > 0 else 0.0

    def global_median_flat(self, *, dtype=None) -> Optional[np.ndarray]:
        if not self.ready:
            return None
        working_dtype = dtype or self._global_working_dtype()
        stack = np.stack([self._flat(block, dtype=working_dtype) for block in self._blocks], axis=0)
        return np.median(stack, axis=0)

    def peer_flat_matrix(
        self,
        *,
        dtype=np.float32,
        max_dimensions: int = 0,
    ) -> Optional[np.ndarray]:
        """Return observed updates as a matrix.

        For large-model diagnostics/oracles, set ``max_dimensions`` to a positive
        value to obtain the same deterministic coordinate sketch for every row.
        """
        if not self._blocks:
            return None
        if int(max_dimensions) > 0:
            return np.stack(
                [
                    deterministic_sketch(
                        block,
                        max_dimensions=int(max_dimensions),
                        dtype=dtype,
                    )
                    for block in self._blocks
                ],
                axis=0,
            )
        return np.stack([self._flat(block, dtype=dtype) for block in self._blocks], axis=0)

    def coordinate_containment_fraction(self, block: Sequence[np.ndarray], k: float = 3.0) -> float:
        if not self.ready:
            return 0.0
        assert_same_structure(self._blocks[0], block)
        total = 0
        contained = 0
        for arr, (low, high) in zip(block, self.coordinate_bounds(k)):
            values = np.asarray(arr)
            mask = (values >= low) & (values <= high)
            total += int(values.size)
            contained += int(np.count_nonzero(mask))
        return float(contained / total) if total else 0.0

    def norm_containment_fraction(self, block: Sequence[np.ndarray], k: float = 3.0) -> float:
        if not self.ready:
            return 0.0
        assert_same_structure(self._blocks[0], block)
        within = 0
        bands = self.norm_band(k)
        for arr, (low, high) in zip(block, bands):
            norm = float(np.linalg.norm(np.asarray(arr).ravel()))
            within += int(low <= norm <= high)
        return float(within / len(block)) if block else 0.0

    def mean_direction_cosine(self, block: Sequence[np.ndarray]) -> float:
        if not self.ready:
            return 0.0
        assert_same_structure(self._blocks[0], block)
        values = []
        for arr, (mean_direction, _concentration) in zip(block, self.direction_gate()):
            if mean_direction is None:
                continue
            a = np.asarray(arr).ravel()
            b = np.asarray(mean_direction).ravel()
            denom = float(np.linalg.norm(a) * np.linalg.norm(b))
            if denom > 0.0:
                values.append(float(np.dot(a, b) / denom))
        return float(np.mean(values)) if values else 0.0

    def global_norm_contained(self, block: Sequence[np.ndarray], k: float = 3.0) -> float:
        if not self.ready:
            return 0.0
        low, high = self.global_norm_band(k)
        norm = block_l2_norm(block)
        return float(low <= norm <= high)

    def global_direction_cosine(self, block: Sequence[np.ndarray]) -> float:
        if not self.ready:
            return 0.0
        dtype = self._global_working_dtype()
        direction, _concentration = self.global_direction(dtype=dtype)
        if direction is None:
            return 0.0
        flat = self._flat(block, dtype=dtype)
        denom = float(np.linalg.norm(flat) * np.linalg.norm(direction))
        if denom <= 0.0:
            return 0.0
        return float(np.dot(flat, direction) / denom)

    def summary(self, block: Sequence[np.ndarray], k_coord: float = 3.0, k_norm: float = 3.0) -> EnvelopeSummary:
        return EnvelopeSummary(
            observations=self.n_observations,
            tensor_count=self.tensor_count,
            coordinate_containment_fraction=self.coordinate_containment_fraction(block, k_coord),
            norm_containment_fraction=self.norm_containment_fraction(block, k_norm),
            mean_direction_cosine=self.mean_direction_cosine(block),
            global_norm_contained=self.global_norm_contained(block, k_norm),
            global_direction_cosine=self.global_direction_cosine(block),
        )
