#!/usr/bin/env python3
"""Per-client update-space benign-envelope learner and poison generator.

V27 runtime guarantees
----------------------
* Engines are keyed by both client identity and model-contract SHA-256.
* Peer observations are supplied by the proxy for every visible client, rather
  than being collected only when the target client's attack engine runs.
* The local defense oracle evaluates only the configured active server defense
  by default and uses deterministic coordinate sketches for large models.
* Full update geometry metrics are computed chunk-by-chunk.
* Envelope state persistence is optional and rate-limited; the default is no
  periodic full-history pickle, avoiding multi-hundred-MB writes each CNN round.
"""
from __future__ import annotations

import json
import logging
import pickle
import shutil
import threading
from collections import deque
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from array_contract import (
    Block,
    assert_same_structure,
    assert_wire_compatible,
    block_l1_norm,
    block_l2_norm,
    block_total_bytes,
    block_total_elements,
    clone_block,
    cosine_similarity,
    deterministic_sketch,
    euclidean_distance,
    iter_block_chunks,
    unflatten_block,
)
from envelope import Envelope
from stealth_projection import project_update_into_envelope
from defense_oracle import DefenseOracle
from selection_attacks import (
    craft_alie,
    craft_ipm,
    craft_min_max,
    craft_min_sum,
    craft_selection_optimal,
)

logger = logging.getLogger("stealth_engine")


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(value))


def _contract_suffix(value: str) -> str:
    raw = _safe_name(str(value or "unknown_contract"))
    return raw[:24] if raw else "unknown_contract"


def update_metrics(block: Sequence[np.ndarray], *, epsilon: float = 1e-8) -> Dict[str, object]:
    dimension = int(sum(int(np.asarray(arr).size) for arr in block))
    if dimension <= 0:
        return {
            "dimension": 0,
            "l1_norm": 0.0,
            "l2_norm": 0.0,
            "max_abs": 0.0,
            "zero_fraction": 0.0,
            "near_zero_fraction": 0.0,
            "mean": 0.0,
            "std": 0.0,
            "minimum": 0.0,
            "maximum": 0.0,
            "tensor_l2_norms_json": "[]",
        }

    total_sum = 0.0
    total_sq = 0.0
    l1 = 0.0
    max_abs = 0.0
    minimum = float("inf")
    maximum = float("-inf")
    zero_count = 0
    near_zero_count = 0
    for chunk in iter_block_chunks(block, dtype=np.float64):
        if chunk.size == 0:
            continue
        total_sum += float(np.sum(chunk, dtype=np.float64))
        total_sq += float(np.dot(chunk, chunk))
        l1 += float(np.sum(np.abs(chunk), dtype=np.float64))
        max_abs = max(max_abs, float(np.max(np.abs(chunk))))
        minimum = min(minimum, float(np.min(chunk)))
        maximum = max(maximum, float(np.max(chunk)))
        zero_count += int(np.count_nonzero(chunk == 0.0))
        near_zero_count += int(np.count_nonzero(np.abs(chunk) < float(epsilon)))

    mean = total_sum / dimension
    variance = max(0.0, total_sq / dimension - mean * mean)
    tensor_l2 = [block_l2_norm([np.asarray(arr)]) for arr in block]
    return {
        "dimension": dimension,
        "l1_norm": l1,
        "l2_norm": float(np.sqrt(max(total_sq, 0.0))),
        "max_abs": max_abs,
        "zero_fraction": zero_count / dimension,
        "near_zero_fraction": near_zero_count / dimension,
        "mean": mean,
        "std": float(np.sqrt(variance)),
        "minimum": minimum,
        "maximum": maximum,
        "tensor_l2_norms_json": json.dumps(tensor_l2, separators=(",", ":")),
    }


def _oracle_defenses(active_defense: str) -> Tuple[str, ...]:
    name = str(active_defense or "flame").strip().lower()
    if name in {"", "none", "fedavg"}:
        return tuple()
    if name == "auto":
        return ("krum", "multi_krum", "median", "trimmed_mean", "bulyan", "flame")
    aliases = {
        "multikrum": "multi_krum",
        "multi-krum": "multi_krum",
        "trimmedmean": "trimmed_mean",
        "trimmed-mean": "trimmed_mean",
    }
    return (aliases.get(name, name),)


class UpdateSpaceStealthEngine:
    def __init__(
        self,
        *,
        client_id: str,
        model_contract_sha256: str = "",
        warmup: int = 20,
        window: int = 5,
        aggressiveness: float = 0.3,
        raw_attack: str = "sign_flip",
        alpha: float = 1.0,
        sigma: float = 0.01,
        k_coord: float = 3.0,
        k_norm: float = 3.0,
        sparsity_epsilon: float = 1e-8,
        random_seed: int = 1234,
        state_path: str = "",
        state_save_every: int = 0,
        cache_dir: str = "",
        disk_history_threshold_mb: float = 256.0,
        ramp_rounds: int = 5,
        adaptive_stealth: bool = True,
        adaptive_backoff_step: float = 0.1,
        derived_f: int = 1,
        multi_krum_m: int = 1,
        trimmed_beta: float = 0.1,
        flame_cosine_threshold: float = 0.1,
        active_defense: str = "flame",
        geometry_sketch_dim: int = 8192,
        large_model_float32_threshold_elements: int = 2_000_000,
        large_model_adaptive_backoff_steps: int = 0,
    ):
        self.client_id = str(client_id)
        self.model_contract_sha256 = str(model_contract_sha256 or "")
        self.warmup = max(0, int(warmup))
        self.window = max(0, int(window))
        self.aggressiveness = float(aggressiveness)
        self.raw_attack = str(raw_attack).lower()
        self.alpha = float(alpha)
        self.sigma = float(sigma)
        self.k_coord = float(k_coord)
        self.k_norm = float(k_norm)
        self.sparsity_epsilon = float(sparsity_epsilon)
        self.random_seed = int(random_seed)
        self.state_save_every = max(0, int(state_save_every))
        self.ramp_rounds = max(0, int(ramp_rounds))
        self.adaptive_stealth = bool(adaptive_stealth)
        self.adaptive_backoff_step = max(0.01, float(adaptive_backoff_step))
        self.derived_f = int(derived_f)
        self.multi_krum_m = int(multi_krum_m)
        self.trimmed_beta = float(trimmed_beta)
        self.flame_cosine_threshold = float(flame_cosine_threshold)
        self.active_defense = str(active_defense or "flame").lower()
        self.oracle_defenses = _oracle_defenses(self.active_defense)
        self.geometry_sketch_dim = max(256, int(geometry_sketch_dim))
        self.large_model_float32_threshold_elements = max(
            1, int(large_model_float32_threshold_elements)
        )
        self.large_model_adaptive_backoff_steps = max(
            0, int(large_model_adaptive_backoff_steps)
        )
        self.peer_registry = None
        self._rng = np.random.default_rng(self.random_seed)
        self._lock = threading.RLock()
        self.observed_updates = 0
        self.poisoned_updates = 0
        self.previous_genuine_update: Optional[Block] = None
        self.previous_genuine_sketch: Optional[np.ndarray] = None
        self.previous_genuine_norm: float = 0.0
        self.disk_history_threshold_mb = max(1.0, float(disk_history_threshold_mb))
        self._history = deque()
        self._history_paths = deque()
        self.cache_dir = self._client_cache_dir(cache_dir)
        self.envelope = Envelope(
            min_observations=max(1, min(3, self.warmup or 3)),
            large_tensor_float32_threshold_elements=self.large_model_float32_threshold_elements,
        )
        self.state_path = self._client_state_path(state_path)
        self._load_state()

    def _client_cache_dir(self, raw: str) -> str:
        raw = str(raw or "").strip()
        if not raw:
            return ""
        base = Path(raw).expanduser()
        return str(base / f"{_safe_name(self.client_id)}_{_contract_suffix(self.model_contract_sha256)}")

    def _large_model(self, block: Sequence[np.ndarray]) -> bool:
        return block_total_elements(block) >= self.large_model_float32_threshold_elements

    def _store_history_block(self, block: Sequence[np.ndarray]) -> Block:
        """Store very large target history on disk; keep medium CNN history in RAM.

        ResNet-18 is ~42.65 MiB in the current protocol. Memory-mapping every
        observation caused repeated disk scans during envelope projection, so V27
        keeps models up to ``disk_history_threshold_mb`` in RAM and only spills
        larger contracts (e.g. large transformers) to mmap-backed storage.
        """
        total_mb = block_total_bytes(block) / float(1024 ** 2)
        if not self.cache_dir or total_mb <= self.disk_history_threshold_mb:
            self._history_paths.append("")
            return [np.asarray(arr) for arr in block]
        root = Path(self.cache_dir)
        root.mkdir(parents=True, exist_ok=True)
        obs_dir = root / f"obs_{self.observed_updates + 1:08d}"
        obs_dir.mkdir(parents=True, exist_ok=True)
        mapped: Block = []
        for idx, arr in enumerate(block):
            path = obs_dir / f"tensor_{idx:04d}.npy"
            np.save(path, np.asarray(arr), allow_pickle=False)
            mapped.append(np.load(path, mmap_mode="r", allow_pickle=False))
        self._history_paths.append(str(obs_dir))
        return mapped

    def _evict_history_if_needed(self) -> None:
        if self.window <= 0:
            return
        while len(self._history) > self.window:
            self._history.popleft()
            path = self._history_paths.popleft() if self._history_paths else ""
            if path:
                shutil.rmtree(path, ignore_errors=True)

    def cleanup_cache(self) -> None:
        if self.cache_dir:
            shutil.rmtree(self.cache_dir, ignore_errors=True)

    def _client_state_path(self, raw: str) -> str:
        raw = str(raw or "").strip()
        if not raw:
            return ""
        path = Path(raw).expanduser()
        suffix = _contract_suffix(self.model_contract_sha256)
        client = _safe_name(self.client_id)
        if path.suffix:
            return str(path.with_name(f"{path.stem}_{client}_{suffix}{path.suffix}"))
        return str(path / f"envelope_{client}_{suffix}.pkl")

    def _rebuild_envelope(self) -> None:
        envelope = Envelope(
            min_observations=max(1, min(3, self.warmup or 3)),
            large_tensor_float32_threshold_elements=self.large_model_float32_threshold_elements,
        )
        for block in self._history:
            # History already owns clones; no second full-model copy is needed.
            envelope.observe(block, copy_block=False)
        self.envelope = envelope

    def _load_state(self) -> None:
        if not self.state_path:
            return
        path = Path(self.state_path)
        if not path.exists():
            return
        try:
            with path.open("rb") as handle:
                state = pickle.load(handle)
            stored_contract = str(state.get("model_contract_sha256", "") or "")
            if stored_contract and self.model_contract_sha256 and stored_contract != self.model_contract_sha256:
                logger.warning(
                    "[UPDATE-SPACE] refusing cross-contract state %s: stored=%s current=%s",
                    self.state_path,
                    stored_contract[:12],
                    self.model_contract_sha256[:12],
                )
                return
            self.observed_updates = int(state.get("observed_updates", 0))
            self.poisoned_updates = int(state.get("poisoned_updates", 0))
            history = state.get("history", [])
            self._history = deque(history)
            self._history_paths = deque([""] * len(self._history))
            self._evict_history_if_needed()
            self.previous_genuine_update = state.get("previous_genuine_update")
            if self.previous_genuine_update is not None:
                self.previous_genuine_norm = block_l2_norm(self.previous_genuine_update)
                if self._large_model(self.previous_genuine_update):
                    self.previous_genuine_sketch = deterministic_sketch(
                        self.previous_genuine_update,
                        max_dimensions=self.geometry_sketch_dim,
                        dtype=np.float32,
                    )
            self._rebuild_envelope()
            logger.info(
                "[UPDATE-SPACE] restored client=%s contract=%s observed=%d poisoned=%d",
                self.client_id,
                self.model_contract_sha256[:12],
                self.observed_updates,
                self.poisoned_updates,
            )
        except Exception as exc:
            logger.warning("[UPDATE-SPACE] could not restore %s: %s", self.state_path, exc)

    def _save_state(self, *, force: bool = False) -> None:
        if not self.state_path:
            return
        if not force:
            if self.state_save_every <= 0:
                return
            if self.observed_updates % self.state_save_every != 0:
                return
        try:
            path = Path(self.state_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".tmp")
            with temporary.open("wb") as handle:
                pickle.dump(
                    {
                        "model_contract_sha256": self.model_contract_sha256,
                        "observed_updates": self.observed_updates,
                        "poisoned_updates": self.poisoned_updates,
                        "history": list(self._history),
                        "previous_genuine_update": self.previous_genuine_update,
                    },
                    handle,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )
            temporary.replace(path)
        except Exception as exc:
            logger.warning("[UPDATE-SPACE] could not save state %s: %s", self.state_path, exc)

    def flush_state(self) -> None:
        with self._lock:
            self._save_state(force=True)

    def _raw_poison(self, update: Sequence[np.ndarray]) -> Block:
        if self.raw_attack == "sign_flip":
            return [(-self.alpha * np.asarray(arr, dtype=np.float64)).astype(arr.dtype) for arr in update]
        if self.raw_attack == "scale":
            return [(self.alpha * np.asarray(arr, dtype=np.float64)).astype(arr.dtype) for arr in update]
        if self.raw_attack == "noise":
            return [
                (
                    np.asarray(arr, dtype=np.float64)
                    + self._rng.normal(0.0, self.sigma, size=arr.shape)
                ).astype(arr.dtype)
                for arr in update
            ]
        raise ValueError(f"unsupported own-update envelope raw attack: {self.raw_attack}")

    def _effective_aggressiveness(self, attack_index: int) -> float:
        target = float(np.clip(self.aggressiveness, 0.0, 1.0))
        if self.ramp_rounds <= 0 or attack_index >= self.ramp_rounds:
            return target
        frac = attack_index / float(self.ramp_rounds)
        start = min(target, 0.05)
        return float(start + (target - start) * frac)

    def _peer_context(self, round_index: Optional[int] = None):
        info = {"peer_mode": "self_only"}
        registry = self.peer_registry
        if registry is None:
            return None, None, info
        try:
            peer_env, pinfo = registry.peer_envelope(
                self.client_id,
                self.model_contract_sha256,
                round_index=round_index,
            )
            info.update(pinfo)
            peer_geometry, ginfo = registry.peer_geometry_matrix(
                self.client_id,
                self.model_contract_sha256,
                latest_only=True,
                max_dimensions=self.geometry_sketch_dim,
                dtype=np.float32,
                round_index=round_index,
            )
            info.update(ginfo)
            if peer_env is not None:
                info["peer_mode"] = "peer"
            return peer_env, peer_geometry, info
        except Exception as exc:
            info["peer_error"] = str(exc)
            return None, None, info

    def _full_peer_matrix(self, round_index: Optional[int] = None):
        if self.peer_registry is None:
            return None, {"peer_full_geometry_rows": 0}
        return self.peer_registry.peer_full_matrix(
            self.client_id,
            self.model_contract_sha256,
            latest_only=True,
            dtype=np.float32,
            round_index=round_index,
        )

    def _selection_raw(
        self,
        genuine: Block,
        peer_full: np.ndarray,
        *,
        strength: float,
    ):
        name = self.raw_attack
        if name == "krum_optimal":
            active = str(self.active_defense or "").strip().lower()
            if active not in {"krum", "multi_krum"}:
                return None, {
                    "feasible": False,
                    "reason": "krum_optimal_requires_krum_or_multi_krum_server",
                    "configured_active_defense": active,
                }
            selection_size = 1 if active == "krum" else max(1, self.multi_krum_m)
            malicious, info = craft_selection_optimal(
                peer_full,
                f=self.derived_f,
                selection_size=selection_size,
                defense=active,
                strength=strength,
            )
        elif name == "alie":
            malicious, info = craft_alie(peer_full, z=abs(self.alpha))
        elif name == "min_max":
            malicious, info = craft_min_max(peer_full)
        elif name == "min_sum":
            malicious, info = craft_min_sum(peer_full, strength=strength)
        elif name == "ipm":
            malicious, info = craft_ipm(peer_full, epsilon=abs(self.alpha))
        else:
            raise ValueError(f"unsupported peer-based raw attack: {name}")
        if not info.get("feasible", False):
            return None, info
        return unflatten_block(malicious, genuine), info

    def process_update(
        self,
        genuine_update: Sequence[np.ndarray],
        *,
        round_index: Optional[int] = None,
        model_contract_sha256: str = "",
        genuine_update_sha256: str = "",
    ) -> Tuple[Optional[Block], Dict[str, object]]:
        with self._lock:
            incoming_contract = str(model_contract_sha256 or "")
            if (
                self.model_contract_sha256
                and incoming_contract
                and incoming_contract != self.model_contract_sha256
            ):
                return None, {
                    "engine_decision": "model_contract_mismatch",
                    "engine_model_contract_sha256": self.model_contract_sha256,
                    "incoming_model_contract_sha256": incoming_contract,
                }

            # The proxy already owns this freshly reconstructed update and the
            # engine never mutates it. Keep array references rather than cloning
            # another full ResNet/transformer update.
            genuine = [np.asarray(arr) for arr in genuine_update]
            previous_genuine = self._history[-1] if self._history else self.previous_genuine_update
            metrics = update_metrics(genuine, epsilon=self.sparsity_epsilon)
            diagnostics: Dict[str, object] = {
                "engine_client_id": self.client_id,
                "engine_model_contract_sha256": self.model_contract_sha256,
                "engine_observed_before": self.observed_updates,
                "engine_poisoned_before": self.poisoned_updates,
                "active_defense": self.active_defense,
                "oracle_evaluated_defenses": ",".join(self.oracle_defenses),
                "geometry_sketch_dim_configured": self.geometry_sketch_dim,
                "state_persistence_enabled": int(bool(self.state_path) and self.state_save_every > 0),
                "genuine_update_dimension": metrics["dimension"],
                "genuine_update_l1_norm": metrics["l1_norm"],
                "genuine_update_l2_norm": metrics["l2_norm"],
                "genuine_update_max_abs": metrics["max_abs"],
                "genuine_update_zero_fraction": metrics["zero_fraction"],
                "genuine_update_near_zero_fraction": metrics["near_zero_fraction"],
                "genuine_update_mean": metrics["mean"],
                "genuine_update_std": metrics["std"],
                "genuine_update_minimum": metrics["minimum"],
                "genuine_update_maximum": metrics["maximum"],
                "genuine_tensor_l2_norms_json": metrics["tensor_l2_norms_json"],
            }
            current_sketch = None
            if previous_genuine is not None:
                try:
                    current_norm = float(metrics["l2_norm"])
                    previous_norm = (
                        float(self.previous_genuine_norm)
                        if self.previous_genuine_norm > 0.0
                        else block_l2_norm(previous_genuine)
                    )
                    if self._large_model(genuine):
                        current_sketch = deterministic_sketch(
                            genuine,
                            max_dimensions=self.geometry_sketch_dim,
                            dtype=np.float32,
                        )
                        previous_sketch = self.previous_genuine_sketch
                        if previous_sketch is None:
                            previous_sketch = deterministic_sketch(
                                previous_genuine,
                                max_dimensions=self.geometry_sketch_dim,
                                dtype=np.float32,
                            )
                        diff = current_sketch.astype(np.float64) - previous_sketch.astype(np.float64)
                        diagnostics["distance_to_previous_genuine_update"] = float(np.linalg.norm(diff))
                        denom = float(np.linalg.norm(current_sketch) * np.linalg.norm(previous_sketch))
                        diagnostics["cosine_to_previous_genuine_update"] = (
                            float(np.dot(current_sketch, previous_sketch) / denom) if denom > 0.0 else 0.0
                        )
                        diagnostics["temporal_geometry_mode"] = "deterministic_coordinate_sketch"
                        diagnostics["temporal_geometry_dimensions"] = int(current_sketch.size)
                    else:
                        diagnostics["distance_to_previous_genuine_update"] = euclidean_distance(
                            genuine, previous_genuine
                        )
                        diagnostics["cosine_to_previous_genuine_update"] = cosine_similarity(
                            genuine, previous_genuine
                        )
                        diagnostics["temporal_geometry_mode"] = "exact_full_update"
                        diagnostics["temporal_geometry_dimensions"] = int(metrics["dimension"])
                    diagnostics["genuine_update_norm_change"] = current_norm - previous_norm
                    diagnostics["genuine_update_norm_change_ratio"] = (
                        current_norm / (previous_norm + 1e-12)
                    )
                except Exception:
                    pass

            if self._history:
                assert_same_structure(self._history[0], genuine)
            history_block = self._store_history_block(genuine)
            self._history.append(history_block)
            self._evict_history_if_needed()
            self.observed_updates += 1
            self._rebuild_envelope()
            self.previous_genuine_update = self._history[-1]
            self.previous_genuine_norm = float(metrics["l2_norm"])
            if self._large_model(genuine):
                if current_sketch is None:
                    current_sketch = deterministic_sketch(
                        genuine,
                        max_dimensions=self.geometry_sketch_dim,
                        dtype=np.float32,
                    )
                self.previous_genuine_sketch = np.asarray(current_sketch, dtype=np.float32)
            else:
                self.previous_genuine_sketch = None

            diagnostics["engine_observed_after"] = self.observed_updates
            diagnostics["engine_poisoned_after"] = self.poisoned_updates
            diagnostics["envelope_observations"] = self.envelope.n_observations
            diagnostics["warmup_configured"] = self.warmup
            diagnostics["warmup_complete"] = int(self.observed_updates > self.warmup)
            diagnostics["engine_round_index"] = int(round_index or self.observed_updates)
            diagnostics["genuine_update_sha256"] = genuine_update_sha256

            if self.observed_updates <= self.warmup:
                diagnostics["engine_decision"] = "warmup_observe_only"
                self._save_state()
                return None, diagnostics

            if not self.envelope.ready:
                diagnostics["engine_decision"] = "envelope_not_ready"
                self._save_state()
                return None, diagnostics

            attack_index = self.observed_updates - self.warmup
            effective_a = self._effective_aggressiveness(attack_index)
            diagnostics["attack_index"] = attack_index
            diagnostics["configured_aggressiveness"] = self.aggressiveness
            diagnostics["effective_aggressiveness"] = effective_a

            peer_env, peer_geometry, peer_info = self._peer_context(round_index)
            diagnostics.update(peer_info)
            proj_env = peer_env if peer_env is not None else self.envelope
            global_env = peer_env if peer_env is not None else self.envelope

            peer_based_attacks = {"krum_optimal", "alie", "min_max", "min_sum", "ipm"}
            if self.raw_attack in peer_based_attacks:
                peer_full, full_info = self._full_peer_matrix(round_index)
                diagnostics.update(full_info)
                if peer_full is None or peer_full.shape[0] < 2:
                    diagnostics["engine_decision"] = f"{self.raw_attack}_needs_peers"
                    diagnostics["selection_attack_feasible"] = 0
                    self._save_state()
                    return None, diagnostics
                raw, sel_info = self._selection_raw(
                    genuine, peer_full, strength=effective_a
                )
                diagnostics.update({f"selection_{k}": v for k, v in sel_info.items()})
                diagnostics["selection_attack_feasible"] = int(bool(sel_info.get("feasible", False)))
                if raw is None:
                    diagnostics["engine_decision"] = "selection_attack_infeasible"
                    self._save_state()
                    return None, diagnostics
                projected = raw
                projection = {
                    "coordinate_containment_fraction": 0.0,
                    "norm_containment_fraction": 0.0,
                    "mean_direction_cosine": sel_info.get("cosine_to_peer_mean", 0.0),
                    "global_norm_contained": 0.0,
                    "global_direction_cosine": sel_info.get("cosine_to_peer_mean", 0.0),
                    "projection_working_dtype": "selection_boundary_no_projection",
                }
            else:
                raw = self._raw_poison(genuine)
                projected, projection = project_update_into_envelope(
                    raw,
                    proj_env,
                    aggressiveness=effective_a,
                    k_coord=self.k_coord,
                    k_norm=self.k_norm,
                    enforce_global=True,
                    global_k_norm=self.k_norm,
                    global_envelope=global_env,
                    large_model_float32_threshold_elements=self.large_model_float32_threshold_elements,
                )

            raw_metrics = update_metrics(raw, epsilon=self.sparsity_epsilon)
            diagnostics.update({
                "raw_poison_update_l1_norm": raw_metrics["l1_norm"],
                "raw_poison_update_l2_norm": raw_metrics["l2_norm"],
                "raw_poison_update_max_abs": raw_metrics["max_abs"],
                "raw_poison_update_near_zero_fraction": raw_metrics["near_zero_fraction"],
                "distance_genuine_to_raw_poison": euclidean_distance(genuine, raw),
                "cosine_genuine_to_raw_poison": cosine_similarity(genuine, raw),
            })

            if (
                self.adaptive_stealth
                and peer_geometry is not None
                and self.raw_attack not in peer_based_attacks
                and self.oracle_defenses
            ):
                oracle = DefenseOracle(
                    f=self.derived_f,
                    multi_krum_m=self.multi_krum_m,
                    trimmed_beta=self.trimmed_beta,
                    flame_cosine_threshold=self.flame_cosine_threshold,
                    coordinate_k=self.k_coord,
                )
                a_try = effective_a
                report = None
                large_model = self._large_model(genuine)
                max_reprojections = (
                    self.large_model_adaptive_backoff_steps if large_model else 5
                )
                reprojections = 0
                while True:
                    candidate_sketch = deterministic_sketch(
                        projected,
                        max_dimensions=self.geometry_sketch_dim,
                        dtype=np.float32,
                    )
                    report = oracle.evaluate(
                        candidate_sketch,
                        peer_geometry,
                        defenses=self.oracle_defenses,
                        geometry_mode="deterministic_coordinate_sketch",
                    )
                    flagged = any(v.candidate_flagged for v in report.verdicts.values())
                    if (
                        not flagged
                        or a_try <= 0.0
                        or reprojections >= max_reprojections
                    ):
                        break
                    a_try = max(0.0, a_try - self.adaptive_backoff_step)
                    projected, projection = project_update_into_envelope(
                        raw,
                        proj_env,
                        aggressiveness=a_try,
                        k_coord=self.k_coord,
                        k_norm=self.k_norm,
                        enforce_global=True,
                        global_k_norm=self.k_norm,
                        global_envelope=global_env,
                        large_model_float32_threshold_elements=self.large_model_float32_threshold_elements,
                    )
                    reprojections += 1
                diagnostics["adaptive_reprojection_count"] = reprojections
                diagnostics["adaptive_backoff_mode"] = (
                    "large_model_audit_only"
                    if large_model and max_reprojections == 0
                    else "bounded_reprojection"
                )
                if report is not None:
                    diagnostics["adaptive_final_aggressiveness"] = a_try
                    diagnostics["oracle_any_flagged"] = int(
                        any(v.candidate_flagged for v in report.verdicts.values())
                    )
                    diagnostics["oracle_geometry_mode"] = report.geometry_mode
                    diagnostics["oracle_geometry_dimensions"] = report.geometry_dimensions
                    diagnostics["oracle_coordinate_containment"] = report.coordinate_containment_fraction
                    diagnostics["oracle_cosine_to_peer_mean"] = report.cosine_to_peer_mean
                    diagnostics["oracle_norm_in_band"] = int(report.norm_in_band)
                    for name, verdict in report.verdicts.items():
                        diagnostics[f"oracle_{name}_flagged"] = int(verdict.candidate_flagged)
                        if verdict.candidate_selected is not None:
                            diagnostics[f"oracle_{name}_selected"] = int(verdict.candidate_selected)

            assert_wire_compatible(genuine, projected)
            projected_metrics = update_metrics(projected, epsilon=self.sparsity_epsilon)
            diagnostics.update({
                "projected_update_l1_norm": projected_metrics["l1_norm"],
                "projected_update_l2_norm": projected_metrics["l2_norm"],
                "projected_update_max_abs": projected_metrics["max_abs"],
                "projected_update_zero_fraction": projected_metrics["zero_fraction"],
                "projected_update_near_zero_fraction": projected_metrics["near_zero_fraction"],
                "projected_tensor_l2_norms_json": projected_metrics["tensor_l2_norms_json"],
                "distance_genuine_to_projected_update": euclidean_distance(genuine, projected),
                "cosine_genuine_to_projected_update": cosine_similarity(genuine, projected),
                "projected_to_genuine_norm_ratio": (
                    block_l2_norm(projected) / (block_l2_norm(genuine) + 1e-12)
                ),
                "envelope_coordinate_containment_fraction": projection["coordinate_containment_fraction"],
                "envelope_norm_containment_fraction": projection["norm_containment_fraction"],
                "envelope_mean_direction_cosine": projection["mean_direction_cosine"],
                "envelope_global_norm_contained": projection.get("global_norm_contained", 0.0),
                "envelope_global_direction_cosine": projection.get("global_direction_cosine", 0.0),
                "projection_working_dtype": projection.get("projection_working_dtype", ""),
            })
            self.poisoned_updates += 1
            diagnostics["engine_poisoned_after"] = self.poisoned_updates
            diagnostics["engine_decision"] = "projected_poison_generated"
            self._save_state()
            return projected, diagnostics

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            return {
                "client_id": self.client_id,
                "model_contract_sha256": self.model_contract_sha256,
                "observed": self.observed_updates,
                "poisoned": self.poisoned_updates,
                "warmup": self.warmup,
                "window": self.window,
                "envelope_ready": self.envelope.ready,
                "envelope_observations": self.envelope.n_observations,
                "aggressiveness": self.aggressiveness,
                "raw_attack": self.raw_attack,
                "active_defense": self.active_defense,
                "oracle_defenses": list(self.oracle_defenses),
                "geometry_sketch_dim": self.geometry_sketch_dim,
                "large_model_adaptive_backoff_steps": self.large_model_adaptive_backoff_steps,
                "state_path": self.state_path,
                "state_save_every": self.state_save_every,
                "cache_dir": self.cache_dir,
                "disk_history_threshold_mb": self.disk_history_threshold_mb,
                "history_storage_mode": (
                    "disk_mmap" if any(bool(path) for path in self._history_paths) else "memory"
                ),
            }


_manager_lock = threading.RLock()


def get_client_engine(
    args,
    client_id: str,
    model_contract_sha256: str = "",
) -> UpdateSpaceStealthEngine:
    with _manager_lock:
        engines = getattr(args, "_update_space_engines", None)
        if engines is None:
            engines = {}
            args._update_space_engines = engines
        contract = str(model_contract_sha256 or "")
        key = f"{str(client_id or 'unknown')}|{contract or 'unknown_contract'}"
        engine = engines.get(key)
        if engine is None:
            engine = UpdateSpaceStealthEngine(
                client_id=str(client_id or "unknown"),
                model_contract_sha256=contract,
                warmup=int(getattr(args, "live_warmup", 20)),
                window=int(getattr(args, "live_window", 5)),
                aggressiveness=float(getattr(args, "live_aggressiveness", 0.3)),
                raw_attack=str(getattr(args, "live_raw_attack", "sign_flip")),
                alpha=float(getattr(args, "live_alpha", 1.0)),
                sigma=float(getattr(args, "live_sigma", 0.01)),
                k_coord=float(getattr(args, "live_k_coord", 3.0)),
                k_norm=float(getattr(args, "live_k_norm", 3.0)),
                sparsity_epsilon=float(getattr(args, "update_sparsity_epsilon", 1e-8)),
                random_seed=int(getattr(args, "live_seed", 1234)),
                state_path=str(getattr(args, "live_envelope_state", "") or ""),
                state_save_every=int(getattr(args, "live_state_save_every", 0) or 0),
                cache_dir=str(getattr(args, "live_engine_cache_dir", "") or ""),
                disk_history_threshold_mb=float(
                    getattr(args, "live_engine_disk_threshold_mb", 256.0) or 256.0
                ),
                ramp_rounds=int(getattr(args, "live_ramp_rounds", 5)),
                adaptive_stealth=bool(getattr(args, "live_adaptive_stealth", True)),
                adaptive_backoff_step=float(getattr(args, "live_backoff_step", 0.1)),
                derived_f=int(getattr(args, "live_derived_f", 1)),
                multi_krum_m=int(getattr(args, "live_multi_krum_m", 1)),
                trimmed_beta=float(getattr(args, "live_trimmed_beta", 0.1)),
                flame_cosine_threshold=float(getattr(args, "live_flame_cosine_threshold", 0.1)),
                active_defense=str(getattr(args, "live_active_defense", "flame")),
                geometry_sketch_dim=int(getattr(args, "live_geometry_sketch_dim", 8192) or 8192),
                large_model_float32_threshold_elements=int(
                    getattr(args, "live_large_model_float32_threshold_elements", 2_000_000)
                    or 2_000_000
                ),
                large_model_adaptive_backoff_steps=int(
                    getattr(args, "live_large_model_adaptive_backoff_steps", 0) or 0
                ),
            )
            try:
                from peer_fingerprint import get_peer_registry
                engine.peer_registry = get_peer_registry(args)
            except Exception as exc:
                logger.warning("[UPDATE-SPACE] peer registry unavailable: %s", exc)
            engines[key] = engine
            logger.info(
                "[UPDATE-SPACE] created engine client=%s contract=%s defense=%s",
                client_id,
                contract[:12],
                engine.active_defense,
            )
        return engine


def manager_snapshot(args) -> Dict[str, object]:
    with _manager_lock:
        engines = getattr(args, "_update_space_engines", {}) or {}
        return {str(key): engine.snapshot() for key, engine in engines.items()}


def flush_manager_state(args) -> None:
    with _manager_lock:
        engines = getattr(args, "_update_space_engines", {}) or {}
        for engine in engines.values():
            try:
                engine.flush_state()
            except Exception as exc:
                logger.warning("[UPDATE-SPACE] could not flush engine state: %s", exc)


def cleanup_manager_cache(args) -> None:
    with _manager_lock:
        engines = getattr(args, "_update_space_engines", {}) or {}
        for engine in engines.values():
            try:
                engine.cleanup_cache()
            except Exception as exc:
                logger.warning("[UPDATE-SPACE] could not clean engine cache: %s", exc)
