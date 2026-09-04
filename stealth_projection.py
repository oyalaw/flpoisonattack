#!/usr/bin/env python3
"""Projection of a poisoned model update into a learned benign-update envelope.

V27 preserves the existing stealth/effect semantics while reducing large-model
memory pressure. The global flatten-space pass uses float32 for sufficiently
large models instead of always creating several full float64 copies.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from array_contract import (
    Block,
    assert_wire_compatible,
    block_total_elements,
    clone_block,
    flatten_block,
    unflatten_block,
)
from envelope import Envelope

logger = logging.getLogger("stealth_projection")


def project_update_into_envelope(
    poisoned_update: Sequence[np.ndarray],
    envelope: Envelope,
    *,
    aggressiveness: float = 0.5,
    k_coord: float = 3.0,
    k_norm: float = 3.0,
    direction_concentration_floor: float = 0.50,
    enforce_global: bool = True,
    global_k_norm: float = 3.0,
    global_direction_floor: float = 0.0,
    global_envelope: Optional[Envelope] = None,
    large_model_float32_threshold_elements: int = 2_000_000,
) -> Tuple[Block, Dict[str, float]]:
    """Project a poisoned update while preserving all wire properties.

    ``aggressiveness=0`` applies the full benign projection;
    ``aggressiveness=1`` keeps the raw poisoned update.
    """
    # The function never mutates source arrays; avoid cloning another complete
    # CNN/transformer update before projection.
    reference = [np.asarray(arr) for arr in poisoned_update]
    if not envelope.ready:
        return reference, {
            "coordinate_containment_fraction": 0.0,
            "norm_containment_fraction": 0.0,
            "mean_direction_cosine": 0.0,
            "global_norm_contained": 0.0,
            "global_direction_cosine": 0.0,
            "projection_working_dtype": "none",
        }

    a = float(np.clip(aggressiveness, 0.0, 1.0))
    total_elements = block_total_elements(reference)
    large_model = total_elements >= int(large_model_float32_threshold_elements)
    coordinate_bounds = envelope.coordinate_bounds(k_coord)
    norm_bands = envelope.norm_band(k_norm)
    directions = envelope.direction_gate()

    projected: Block = []
    for source, (lower, upper), (norm_low, norm_high), (mean_direction, concentration) in zip(
        reference, coordinate_bounds, norm_bands, directions
    ):
        tensor_dtype = np.float32 if large_model else (
            np.float32
            if int(np.asarray(source).size) >= int(large_model_float32_threshold_elements)
            else np.float64
        )
        raw = np.asarray(source, dtype=tensor_dtype)

        bounded = np.clip(raw, lower, upper)
        value = (1.0 - a) * bounded + a * raw

        norm = float(np.linalg.norm(value.ravel()))
        if norm > 0.0:
            corrected_norm = min(max(norm, norm_low), norm_high)
            blended_norm = (1.0 - a) * corrected_norm + a * norm
            value = value * (blended_norm / norm)

        if mean_direction is not None and concentration >= direction_concentration_floor:
            flat = value.ravel()
            norm = float(np.linalg.norm(flat))
            benign = np.asarray(mean_direction, dtype=tensor_dtype).ravel()
            benign_norm = float(np.linalg.norm(benign))
            if norm > 0.0 and benign_norm > 0.0:
                unit = flat / norm
                benign_unit = benign / benign_norm
                cosine = float(np.dot(unit, benign_unit))
                cosine_floor = min(0.999999, max(0.0, concentration))
                if cosine < cosine_floor:
                    benign_aligned = benign_unit * norm
                    rotated = a * flat + (1.0 - a) * benign_aligned
                    rotated_norm = float(np.linalg.norm(rotated))
                    if rotated_norm > 0.0:
                        rotated *= norm / rotated_norm
                    value = rotated.reshape(value.shape)

        projected.append(value.astype(source.dtype, copy=False))

    genv = global_envelope if (global_envelope is not None and global_envelope.ready) else envelope
    working_dtype = (
        np.float32
        if total_elements >= int(large_model_float32_threshold_elements)
        else np.float64
    )

    if enforce_global and genv.ready:
        flat = flatten_block(projected, dtype=working_dtype)
        gnorm = float(np.linalg.norm(flat))
        if gnorm > 0.0:
            g_low, g_high = genv.global_norm_band(global_k_norm)
            corrected = min(max(gnorm, g_low), g_high)
            blended = (1.0 - a) * corrected + a * gnorm
            flat *= blended / gnorm
            gnorm = float(np.linalg.norm(flat))

        if total_elements < int(large_model_float32_threshold_elements):
            direction, concentration = genv.global_direction(dtype=working_dtype)
            floor = max(float(global_direction_floor), float(concentration) * (1.0 - a))
            if direction is not None and gnorm > 0.0 and floor > 0.0:
                unit = flat / gnorm
                cos = float(np.dot(unit, direction))
                if cos < floor:
                    aligned = direction * gnorm
                    rotated = a * flat + (1.0 - a) * aligned
                    rn = float(np.linalg.norm(rotated))
                    if rn > 0.0:
                        rotated *= gnorm / rn
                    flat = rotated.astype(working_dtype, copy=False)

        projected = unflatten_block(flat, reference)

    assert_wire_compatible(reference, projected)
    if total_elements >= int(large_model_float32_threshold_elements):
        diagnostics = {
            "coordinate_containment_fraction": genv.coordinate_containment_fraction(projected, k_coord),
            "norm_containment_fraction": genv.norm_containment_fraction(projected, k_norm),
            "mean_direction_cosine": genv.mean_direction_cosine(projected),
            "global_norm_contained": genv.global_norm_contained(projected, k_norm),
            "global_direction_cosine": genv.global_direction_cosine_sketch(
                projected, max_dimensions=8192
            ),
            "projection_working_dtype": np.dtype(working_dtype).name,
            "global_direction_projection_mode": "sketch_diagnostic_only_for_large_model",
        }
    else:
        summary = genv.summary(projected, k_coord=k_coord, k_norm=k_norm)
        diagnostics = {
            "coordinate_containment_fraction": summary.coordinate_containment_fraction,
            "norm_containment_fraction": summary.norm_containment_fraction,
            "mean_direction_cosine": summary.mean_direction_cosine,
            "global_norm_contained": summary.global_norm_contained,
            "global_direction_cosine": summary.global_direction_cosine,
            "projection_working_dtype": np.dtype(working_dtype).name,
            "global_direction_projection_mode": "exact_full_vector",
        }
    return projected, diagnostics
