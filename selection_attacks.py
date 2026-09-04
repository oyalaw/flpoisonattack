#!/usr/bin/env python3
"""Selection and geometry aware poisoning primitives.

All functions operate on a peer matrix shaped ``(n_peers, D)`` and return a
flattened malicious update plus diagnostics. The proxy normally uses float32
peer matrices for large CNNs to reduce memory pressure.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np


def _as_matrix(peer_flat: np.ndarray) -> np.ndarray:
    peers = np.atleast_2d(np.asarray(peer_flat))
    if peers.ndim != 2 or peers.shape[0] < 1 or peers.shape[1] < 1:
        raise ValueError(f"invalid peer matrix shape: {peers.shape}")
    if not np.all(np.isfinite(peers)):
        raise ValueError("peer matrix contains non-finite values")
    return peers.astype(np.float64, copy=False)


def _pairwise_sq(matrix: np.ndarray) -> np.ndarray:
    sq = np.einsum("ij,ij->i", matrix, matrix)
    distances = sq[:, None] + sq[None, :] - 2.0 * (matrix @ matrix.T)
    np.fill_diagonal(distances, 0.0)
    return np.maximum(distances, 0.0)


def _krum_scores(matrix: np.ndarray, f: int) -> np.ndarray:
    n = matrix.shape[0]
    k = n - int(f) - 2
    if k < 1:
        raise ValueError(f"krum undefined: n={n}, f={f}")
    squared = _pairwise_sq(matrix)
    scores = np.empty(n, dtype=np.float64)
    for index in range(n):
        others = np.array([j for j in range(n) if j != index], dtype=np.int64)
        order = others[np.argsort(squared[index, others], kind="stable")]
        scores[index] = float(squared[index, order[:k]].sum())
    return scores


def _selected_rank_low(scores: np.ndarray, index: int) -> int:
    return int(np.argsort(np.argsort(scores, kind="stable"), kind="stable")[index]) + 1


def _harmful_direction(peer_mean: np.ndarray, direction: Optional[np.ndarray]) -> np.ndarray:
    if direction is None:
        value = -peer_mean
    else:
        value = np.asarray(direction, dtype=np.float64).ravel()
    norm = float(np.linalg.norm(value))
    return value / norm if norm > 0.0 else np.zeros_like(peer_mean)


def _candidate_geometry(candidate: np.ndarray, peer_mean: np.ndarray, gamma: float) -> dict:
    mean_norm = float(np.linalg.norm(peer_mean))
    candidate_norm = float(np.linalg.norm(candidate))
    cosine = float(
        np.dot(candidate, peer_mean)
        / ((candidate_norm * mean_norm) + 1e-12)
    )
    return {
        "peer_mean_norm": mean_norm,
        "gamma_over_peer_mean_norm": float(gamma / (mean_norm + 1e-12)),
        "harmful_direction_crossed": int(cosine < 0.0),
        "cosine_to_peer_mean": cosine,
    }


def craft_selection_optimal(
    peer_flat: np.ndarray,
    *,
    f: int = 1,
    selection_size: int = 1,
    direction: Optional[np.ndarray] = None,
    base: Optional[np.ndarray] = None,
    gamma_max: float = 50.0,
    iterations: int = 30,
    defense: str = "krum",
    strength: float = 1.0,
) -> Tuple[np.ndarray, dict]:
    """Craft a boundary candidate that remains selected by Krum or Multi Krum.

    ``strength`` scales the feasible boundary displacement. A value of one uses
    the full boundary candidate, while zero returns the benign central base.
    """
    peers = _as_matrix(peer_flat)
    n_peers, _dimension = peers.shape
    n = n_peers + 1
    defense = str(defense).strip().lower()
    if defense not in {"krum", "multi_krum"}:
        return peers.mean(axis=0), {
            "feasible": False,
            "reason": f"unsupported_selection_defense:{defense}",
            "configured_active_defense": defense,
        }

    if n < 2 * int(f) + 3:
        return peers.mean(axis=0), {
            "feasible": False,
            "reason": f"krum undefined for n={n}, f={f} (need n>=2f+3)",
            "configured_active_defense": defense,
        }

    peer_mean = peers.mean(axis=0)
    base_vec = (
        peer_mean.copy()
        if base is None
        else np.asarray(base, dtype=np.float64).ravel()
    )
    direction_vec = _harmful_direction(peer_mean, direction)
    peer_scale = float(np.median(np.linalg.norm(peers - peer_mean, axis=1)))
    peer_scale = peer_scale if peer_scale > 0.0 else 1.0
    high = float(gamma_max) * peer_scale
    low = 0.0

    def feasible(gamma: float) -> bool:
        candidate = base_vec + gamma * direction_vec
        matrix = np.vstack([peers, candidate[None, :]])
        scores = _krum_scores(matrix, int(f))
        return _selected_rank_low(scores, n - 1) <= int(selection_size)

    if not feasible(0.0):
        return base_vec, {
            "feasible": False,
            "reason": "base_not_selected",
            "gamma": 0.0,
            "configured_active_defense": defense,
        }

    for _ in range(max(1, int(iterations))):
        middle = 0.5 * (low + high)
        if feasible(middle):
            low = middle
        else:
            high = middle

    boundary_gamma = float(low)
    applied_strength = float(np.clip(strength, 0.0, 1.0))
    gamma = boundary_gamma * applied_strength
    malicious = base_vec + gamma * direction_vec
    matrix = np.vstack([peers, malicious[None, :]])
    scores = _krum_scores(matrix, int(f))
    info = {
        "feasible": True,
        "configured_active_defense": defense,
        "strength": applied_strength,
        "gamma_boundary": boundary_gamma,
        "gamma": gamma,
        "gamma_over_peer_scale": float(gamma / peer_scale),
        "malicious_krum_score": float(scores[-1]),
        "min_peer_krum_score": float(scores[:-1].min()),
        "selection_rank_low": _selected_rank_low(scores, n - 1),
        "selection_size": int(selection_size),
    }
    info.update(_candidate_geometry(malicious, peer_mean, gamma))
    return malicious, info


def craft_alie(peer_flat: np.ndarray, *, z: float = 1.0) -> Tuple[np.ndarray, dict]:
    peers = _as_matrix(peer_flat)
    mean = peers.mean(axis=0)
    std = peers.std(axis=0)
    direction = -np.sign(mean)
    direction[direction == 0] = -1.0
    malicious = mean + abs(float(z)) * std * direction
    return malicious, {
        "feasible": True,
        "z": abs(float(z)),
        "cosine_to_peer_mean": float(
            np.dot(malicious, mean)
            / ((np.linalg.norm(malicious) * np.linalg.norm(mean)) + 1e-12)
        ),
    }


def craft_ipm(peer_flat: np.ndarray, *, epsilon: float = 1.0) -> Tuple[np.ndarray, dict]:
    peers = _as_matrix(peer_flat)
    mean = peers.mean(axis=0)
    malicious = -abs(float(epsilon)) * mean
    return malicious, {
        "feasible": True,
        "epsilon": abs(float(epsilon)),
        "cosine_to_peer_mean": -1.0 if np.linalg.norm(mean) > 0 else 0.0,
    }


def _search_distance_boundary(
    peers: np.ndarray,
    *,
    mode: str,
    gamma_max: float = 50.0,
    iterations: int = 30,
    strength: float = 1.0,
) -> Tuple[np.ndarray, dict]:
    peer_mean = peers.mean(axis=0)
    direction = _harmful_direction(peer_mean, None)
    peer_scale = float(np.median(np.linalg.norm(peers - peer_mean, axis=1))) or 1.0

    if mode == "min_max":
        pairwise = np.sqrt(_pairwise_sq(peers))
        threshold = float(np.max(pairwise))

        def feasible(candidate: np.ndarray) -> bool:
            return (
                float(np.max(np.linalg.norm(peers - candidate, axis=1)))
                <= threshold + 1e-12
            )

        distance_power = 1
    elif mode == "min_sum":
        # Min Sum is defined in the same squared Euclidean geometry used by
        # Krum scores. Summing ordinary Euclidean distances changes the
        # feasible region and can collapse the attack toward the benign mean.
        pairwise_squared = _pairwise_sq(peers)
        threshold = float(np.max(pairwise_squared.sum(axis=1)))

        def feasible(candidate: np.ndarray) -> bool:
            differences = peers - candidate
            candidate_sum = float(np.sum(differences * differences, dtype=np.float64))
            return candidate_sum <= threshold + 1e-12

        distance_power = 2
    else:
        raise ValueError(f"unsupported distance boundary mode: {mode}")

    low = 0.0
    high = float(gamma_max) * peer_scale
    for _ in range(max(1, int(iterations))):
        middle = 0.5 * (low + high)
        candidate = peer_mean + middle * direction
        if feasible(candidate):
            low = middle
        else:
            high = middle

    boundary_gamma = float(low)
    applied_strength = float(np.clip(strength, 0.0, 1.0))
    gamma = boundary_gamma * applied_strength
    malicious = peer_mean + gamma * direction
    info = {
        "feasible": True,
        "strength": applied_strength,
        "gamma_boundary": boundary_gamma,
        "gamma": gamma,
        "gamma_over_peer_scale": float(gamma / peer_scale),
        "boundary_mode": mode,
        "boundary_threshold": threshold,
        "boundary_distance_power": distance_power,
    }
    info.update(_candidate_geometry(malicious, peer_mean, gamma))
    return malicious, info


def craft_min_max(peer_flat: np.ndarray, **kwargs) -> Tuple[np.ndarray, dict]:
    return _search_distance_boundary(_as_matrix(peer_flat), mode="min_max", **kwargs)


def craft_min_sum(peer_flat: np.ndarray, **kwargs) -> Tuple[np.ndarray, dict]:
    return _search_distance_boundary(_as_matrix(peer_flat), mode="min_sum", **kwargs)
