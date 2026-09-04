#!/usr/bin/env python3
"""Local defense surrogate for candidate update geometry.

V27 is designed to operate on deterministic geometry sketches for large models.
The caller should pass only the active server defense whenever possible; this
avoids unnecessary Krum/Median/Trimmed-Mean work during a FLAME experiment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Tuple

import numpy as np


def _pairwise_sq(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float64)
    sq = np.einsum("ij,ij->i", matrix, matrix)
    d = sq[:, None] + sq[None, :] - 2.0 * (matrix @ matrix.T)
    np.fill_diagonal(d, 0.0)
    return np.maximum(d, 0.0)


def _krum_scores(matrix: np.ndarray, f: int) -> Tuple[np.ndarray, int]:
    n = matrix.shape[0]
    f = int(f)
    k = n - f - 2
    if k < 1:
        raise ValueError(f"krum undefined: n={n}, f={f} gives k={k}")
    sq = _pairwise_sq(matrix)
    scores = np.empty(n, dtype=np.float64)
    for i in range(n):
        others = np.array([j for j in range(n) if j != i], dtype=np.int64)
        order = others[np.argsort(sq[i, others], kind="stable")]
        scores[i] = float(sq[i, order[:k]].sum())
    return scores, k


def _rank_high_to_low(values: np.ndarray) -> np.ndarray:
    order = np.argsort(-np.asarray(values, dtype=np.float64), kind="stable")
    ranks = np.empty(len(values), dtype=np.int64)
    ranks[order] = np.arange(1, len(values) + 1)
    return ranks


def _robust_high_outlier(values: np.ndarray) -> Tuple[float, np.ndarray]:
    values = np.asarray(values, dtype=np.float64)
    n = len(values)
    flags = np.zeros(n, dtype=np.int64)
    if n < 3 or not np.all(np.isfinite(values)):
        return float("inf"), flags
    center = float(np.median(values))
    mad = float(np.median(np.abs(values - center)))
    eps = max(1e-12, np.finfo(np.float64).eps * max(1.0, abs(center)))
    if mad > eps:
        threshold = center + 3.0 * 1.4826 * mad
    else:
        q1, q3 = np.percentile(values, [25.0, 75.0])
        iqr = float(q3 - q1)
        if iqr > eps:
            threshold = float(q3 + 1.5 * iqr)
        elif float(np.max(values)) > center + eps:
            threshold = center + eps
        else:
            return float("inf"), flags
    flags[values > threshold] = 1
    return float(threshold), flags


@dataclass
class DefenseVerdict:
    defense: str
    candidate_selected: Optional[bool]
    candidate_flagged: bool
    candidate_rank: Optional[int]
    detail: Dict[str, float] = field(default_factory=dict)


@dataclass
class SimilarityReport:
    peer_count: int
    candidate_norm: float
    peer_norm_median: float
    peer_norm_band: Tuple[float, float]
    norm_in_band: bool
    cosine_to_peer_mean: float
    coordinate_containment_fraction: float
    geometry_mode: str = "deterministic_coordinate_sketch"
    geometry_dimensions: int = 0
    verdicts: Dict[str, DefenseVerdict] = field(default_factory=dict)

    @property
    def evades_all(self) -> bool:
        return not any(v.candidate_flagged for v in self.verdicts.values())


class DefenseOracle:
    """Evaluate a candidate update against observed peer geometry.

    FLAME here remains a cosine-threshold surrogate, not an exact reproduction
    of the server's HDBSCAN clustering. That distinction is intentionally kept
    explicit in the returned detail fields.
    """

    def __init__(
        self,
        *,
        f: int = 1,
        multi_krum_m: int = 1,
        trimmed_beta: float = 0.1,
        flame_cosine_threshold: float = 0.1,
        coordinate_k: float = 3.0,
    ):
        self.f = int(f)
        self.multi_krum_m = int(multi_krum_m)
        self.trimmed_beta = float(trimmed_beta)
        self.flame_cosine_threshold = float(flame_cosine_threshold)
        self.coordinate_k = float(coordinate_k)

    def evaluate(
        self,
        candidate_flat: np.ndarray,
        peer_flat: np.ndarray,
        *,
        defenses: Sequence[str] = ("flame",),
        geometry_mode: str = "deterministic_coordinate_sketch",
    ) -> SimilarityReport:
        candidate = np.asarray(candidate_flat, dtype=np.float64).ravel()
        peers = np.atleast_2d(np.asarray(peer_flat, dtype=np.float64))
        if peers.ndim != 2 or peers.shape[1] != candidate.size:
            raise ValueError(
                f"geometry dimension mismatch: candidate={candidate.size}, peers={peers.shape}"
            )
        n_peers = peers.shape[0]
        matrix = np.vstack([peers, candidate[None, :]])
        cand_idx = matrix.shape[0] - 1
        n = matrix.shape[0]

        peer_norms = np.linalg.norm(peers, axis=1)
        cand_norm = float(np.linalg.norm(candidate))
        norm_median = float(np.median(peer_norms))
        norm_mad = float(np.median(np.abs(peer_norms - norm_median)))
        band_lo = max(0.0, norm_median - self.coordinate_k * 1.4826 * norm_mad)
        band_hi = norm_median + self.coordinate_k * 1.4826 * norm_mad
        band_lo = min(band_lo, float(peer_norms.min()))
        band_hi = max(band_hi, float(peer_norms.max()))

        peer_mean = peers.mean(axis=0)
        pm_norm = float(np.linalg.norm(peer_mean))
        cos_peer_mean = (
            float(np.dot(candidate, peer_mean) / (cand_norm * pm_norm))
            if cand_norm > 0 and pm_norm > 0
            else 0.0
        )

        med = np.median(peers, axis=0)
        cmad = np.median(np.abs(peers - med), axis=0)
        scale = 1.4826 * cmad
        lo = np.minimum(med - self.coordinate_k * scale, peers.min(axis=0))
        hi = np.maximum(med + self.coordinate_k * scale, peers.max(axis=0))
        contained = float(np.mean((candidate >= lo) & (candidate <= hi)))

        verdicts: Dict[str, DefenseVerdict] = {}
        for name in defenses:
            normalized = str(name).strip().lower()
            if normalized in {"", "none", "fedavg"}:
                continue
            verdicts[normalized] = self._verdict_for(
                normalized, matrix, cand_idx, n, med
            )

        return SimilarityReport(
            peer_count=n_peers,
            candidate_norm=cand_norm,
            peer_norm_median=norm_median,
            peer_norm_band=(band_lo, band_hi),
            norm_in_band=bool(band_lo <= cand_norm <= band_hi),
            cosine_to_peer_mean=cos_peer_mean,
            coordinate_containment_fraction=contained,
            geometry_mode=str(geometry_mode),
            geometry_dimensions=int(candidate.size),
            verdicts=verdicts,
        )

    def _verdict_for(self, name, matrix, cand_idx, n, med) -> DefenseVerdict:
        if name in {"krum", "multi_krum"}:
            f = self.f
            if n < 2 * f + 3:
                return DefenseVerdict(
                    name, None, False, None,
                    {"undefined": 1.0, "need_n_at_least": float(2 * f + 3)},
                )
            scores, _ = _krum_scores(matrix, f)
            ranks_low = np.argsort(np.argsort(scores, kind="stable"), kind="stable") + 1
            m = 1 if name == "krum" else max(1, self.multi_krum_m)
            selected = bool(ranks_low[cand_idx] <= m)
            _, flags = _robust_high_outlier(scores)
            return DefenseVerdict(
                name,
                selected,
                bool(flags[cand_idx]),
                int(_rank_high_to_low(scores)[cand_idx]),
                {
                    "krum_score": float(scores[cand_idx]),
                    "min_krum_score": float(scores.min()),
                    "selection_rank_low": int(ranks_low[cand_idx]),
                },
            )

        if name == "bulyan":
            f = self.f
            if n < 4 * f + 3:
                return DefenseVerdict(
                    name, None, False, None,
                    {"undefined": 1.0, "need_n_at_least": float(4 * f + 3)},
                )
            scores, _ = _krum_scores(matrix, f)
            selection_size = n - 2 * f
            ranks_low = np.argsort(np.argsort(scores, kind="stable"), kind="stable") + 1
            selected = bool(ranks_low[cand_idx] <= selection_size)
            _, flags = _robust_high_outlier(scores)
            return DefenseVerdict(
                name,
                selected,
                bool(flags[cand_idx]),
                int(_rank_high_to_low(scores)[cand_idx]),
                {"selection_size": float(selection_size)},
            )

        if name == "median":
            dev = np.abs(matrix[cand_idx] - med)
            scores = np.mean(np.abs(matrix - med[None, :]), axis=1)
            _, flags = _robust_high_outlier(scores)
            return DefenseVerdict(
                name,
                None,
                bool(flags[cand_idx]),
                int(_rank_high_to_low(scores)[cand_idx]),
                {"mean_abs_dev_from_median": float(np.mean(dev))},
            )

        if name == "trimmed_mean":
            trim = int(np.floor(self.trimmed_beta * n))
            if trim <= 0:
                return DefenseVerdict(
                    name, None, False, None,
                    {
                        "trimmed_low_fraction": 0.0,
                        "trimmed_high_fraction": 0.0,
                        "trim_count_each_side": 0.0,
                    },
                )
            order = np.argsort(matrix, axis=0, kind="stable")
            positions = np.empty_like(order)
            columns = np.arange(matrix.shape[1])[None, :]
            positions[order, columns] = np.arange(n)[:, None]
            cand_pos = positions[cand_idx]
            low_frac = float(np.mean(cand_pos < trim))
            high_frac = float(np.mean(cand_pos >= n - trim))
            scores_all = np.mean(
                (positions < trim) | (positions >= n - trim),
                axis=1,
            )
            _, flags = _robust_high_outlier(scores_all)
            return DefenseVerdict(
                name,
                None,
                bool(flags[cand_idx]),
                int(_rank_high_to_low(scores_all)[cand_idx]),
                {
                    "trimmed_low_fraction": low_frac,
                    "trimmed_high_fraction": high_frac,
                    "trim_count_each_side": float(trim),
                },
            )

        if name == "flame":
            cand = matrix[cand_idx]
            peer_centroid = matrix[:cand_idx].mean(axis=0)
            cn = float(np.linalg.norm(cand))
            pcn = float(np.linalg.norm(peer_centroid))
            cos = float(np.dot(cand, peer_centroid) / (cn * pcn)) if cn > 0 and pcn > 0 else 0.0
            in_cluster = (1.0 - cos) <= self.flame_cosine_threshold
            return DefenseVerdict(
                name,
                bool(in_cluster),
                not in_cluster,
                None,
                {
                    "cosine_to_peer_centroid": cos,
                    "cosine_distance": 1.0 - cos,
                    "threshold": self.flame_cosine_threshold,
                    "surrogate_not_exact_hdbscan": 1.0,
                },
            )

        return DefenseVerdict(name, None, False, None, {"unsupported": 1.0})
