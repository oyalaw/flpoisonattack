#!/usr/bin/env python3
"""Cross-sectional peer fingerprinting for the live FL poisoning proxy.

V27 large-model policy
----------------------
Every observation stores a deterministic geometry sketch. A full update block is
stored only when it is below ``live_peer_full_block_max_mb`` and the global peer
memory budget permits it. Thus RNNs can use a full peer envelope, while
ResNet/transformer experiments remain scalable by using self-envelope projection
plus true cross-client sketch geometry for the active-defense oracle.
"""
from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Sequence, Tuple

import numpy as np

from array_contract import (
    Block,
    block_l2_norm,
    block_total_bytes,
    clone_block,
    deterministic_sketch,
    flatten_block,
    signature_hash,
)
from envelope import Envelope

logger = logging.getLogger("peer_fingerprint")


@dataclass
class _Observation:
    round_index: int
    observation_id: str
    norm: float
    sketch: np.ndarray
    block: Optional[Block]
    block_bytes: int


class _ClientTrace:
    __slots__ = ("client_id", "contract_sha256", "observations", "last_round")

    def __init__(self, client_id: str, contract_sha256: str):
        self.client_id = client_id
        self.contract_sha256 = contract_sha256
        self.observations: Deque[_Observation] = deque()
        self.last_round = -1


class PeerFingerprintRegistry:
    def __init__(
        self,
        *,
        window: int = 5,
        min_peers: int = 2,
        min_observations: int = 3,
        memory_budget_mb: int = 512,
        geometry_sketch_dim: int = 8192,
        full_block_max_mb: int = 16,
    ):
        self.window = max(0, int(window))
        self.min_peers = max(1, int(min_peers))
        self.min_observations = max(1, int(min_observations))
        self.memory_budget_bytes = max(0, int(memory_budget_mb)) * 1024 * 1024
        self.geometry_sketch_dim = max(256, int(geometry_sketch_dim))
        self.full_block_max_bytes = max(0, int(full_block_max_mb)) * 1024 * 1024
        self._lock = threading.RLock()
        self._traces: Dict[Tuple[str, str], _ClientTrace] = {}
        self._total_full_block_bytes = 0

    @staticmethod
    def _contract_key(block: Sequence[np.ndarray], model_contract_sha256: str) -> str:
        value = str(model_contract_sha256 or "").strip()
        return value or signature_hash(block)

    def _trace_key(self, client_id: str, contract_sha256: str) -> Tuple[str, str]:
        return str(contract_sha256), str(client_id or "unknown")

    def _drop_observation(self, trace: _ClientTrace) -> None:
        if not trace.observations:
            return
        obs = trace.observations.popleft()
        if obs.block is not None:
            self._total_full_block_bytes = max(
                0, self._total_full_block_bytes - int(obs.block_bytes)
            )

    def _enforce_limits(self) -> None:
        if self.window > 0:
            for trace in self._traces.values():
                while len(trace.observations) > self.window:
                    self._drop_observation(trace)

        if self.memory_budget_bytes <= 0:
            return
        while self._total_full_block_bytes > self.memory_budget_bytes:
            candidates = []
            for trace in self._traces.values():
                for obs in trace.observations:
                    if obs.block is not None:
                        candidates.append((obs.round_index, obs))
                        break
            if not candidates:
                break
            _round, oldest = min(candidates, key=lambda item: item[0])
            self._total_full_block_bytes = max(
                0, self._total_full_block_bytes - int(oldest.block_bytes)
            )
            oldest.block = None
            oldest.block_bytes = 0

    def observe(
        self,
        client_id: str,
        round_index: int,
        genuine_update: Sequence[np.ndarray],
        *,
        model_contract_sha256: str = "",
        observation_id: str = "",
    ) -> Dict[str, object]:
        client = str(client_id or "unknown")
        contract = self._contract_key(genuine_update, model_contract_sha256)
        obs_id = str(observation_id or f"round:{int(round_index)}")
        key = self._trace_key(client, contract)
        nbytes = block_total_bytes(genuine_update)
        sketch = deterministic_sketch(
            genuine_update,
            max_dimensions=self.geometry_sketch_dim,
            dtype=np.float32,
        )

        with self._lock:
            trace = self._traces.get(key)
            if trace is None:
                trace = _ClientTrace(client, contract)
                self._traces[key] = trace
            if any(obs.observation_id == obs_id for obs in trace.observations):
                return {
                    "peer_observation_recorded": 0,
                    "peer_observation_reason": "duplicate_observation_id",
                    "peer_contract_sha256": contract,
                    "peer_registry_total_bytes": self._total_full_block_bytes,
                }

            keep_full = (
                self.full_block_max_bytes > 0
                and nbytes <= self.full_block_max_bytes
            )
            block = clone_block(genuine_update) if keep_full else None
            stored_bytes = nbytes if block is not None else 0
            trace.observations.append(
                _Observation(
                    round_index=int(round_index),
                    observation_id=obs_id,
                    norm=block_l2_norm(genuine_update),
                    sketch=sketch,
                    block=block,
                    block_bytes=stored_bytes,
                )
            )
            trace.last_round = int(round_index)
            self._total_full_block_bytes += stored_bytes
            self._enforce_limits()

            return {
                "peer_observation_recorded": 1,
                "peer_observation_reason": "recorded_full_block" if block is not None else "recorded_sketch_only",
                "peer_contract_sha256": contract,
                "peer_registry_total_bytes": self._total_full_block_bytes,
                "peer_registry_total_mb": self._total_full_block_bytes / (1024.0 * 1024.0),
                "peer_observation_storage_mode": "full_block_plus_sketch" if block is not None else "sketch_only",
                "peer_observation_sketch_dimensions": int(sketch.size),
            }

    def _traces_for_contract(self, contract_sha256: str) -> List[_ClientTrace]:
        contract = str(contract_sha256 or "")
        return [
            trace
            for (stored_contract, _cid), trace in self._traces.items()
            if stored_contract == contract and trace.observations
        ]

    def _round_synchronized_observations(
        self,
        traces: Sequence[_ClientTrace],
        *,
        round_index: Optional[int],
        require_full_block: bool,
    ) -> Tuple[List[_Observation], Dict[str, object]]:
        """Select one peer observation per client from a single FL round.

        A round qualifies once at least ``self.min_peers`` distinct clients
        have an observation for it (a quorum) -- it no longer requires every
        eligible peer to have uploaded. The requested (current) round is
        preferred; among qualifying rounds, the most complete round wins,
        ties broken by recency. The method never mixes observations from
        different rounds within a single selection.
        """
        eligible_traces = []
        for trace in traces:
            if require_full_block:
                if not any(obs.block is not None for obs in trace.observations):
                    continue
            eligible_traces.append(trace)

        requested_round = int(round_index) if round_index is not None else None
        by_round: Dict[int, Dict[str, _Observation]] = {}
        for trace in eligible_traces:
            for obs in trace.observations:
                if require_full_block and obs.block is None:
                    continue
                by_round.setdefault(int(obs.round_index), {})[trace.client_id] = obs

        required_clients = len(eligible_traces)
        quorum = min(required_clients, max(1, self.min_peers)) if required_clients else 0
        selected_round: Optional[int] = None
        source = "no_quorum_round"
        if required_clients > 0:
            requested_count = len(by_round.get(requested_round, {})) if requested_round is not None else 0
            if requested_round is not None and requested_count >= quorum:
                selected_round = requested_round
                source = (
                    "exact_requested_round"
                    if requested_count == required_clients
                    else "quorum_requested_round"
                )
            else:
                candidates = [
                    value
                    for value, observations in by_round.items()
                    if len(observations) >= quorum
                    and (requested_round is None or value < requested_round)
                ]
                if candidates:
                    # Prefer the most complete qualifying round, then the most recent.
                    selected_round = max(
                        candidates, key=lambda value: (len(by_round[value]), value)
                    )
                    complete = len(by_round[selected_round]) == required_clients
                    if requested_round is None:
                        source = "latest_complete_round" if complete else "latest_quorum_round"
                    else:
                        source = "previous_complete_round" if complete else "previous_quorum_round"

        selected: List[_Observation] = []
        if selected_round is not None:
            selected_map = by_round[selected_round]
            for trace in eligible_traces:
                observation = selected_map.get(trace.client_id)
                if observation is not None:
                    selected.append(observation)

        return selected, {
            "requested_round": requested_round if requested_round is not None else "",
            "selected_round": selected_round if selected_round is not None else "",
            "round_source": source,
            "required_client_count": required_clients,
            "selected_client_count": len(selected),
            "round_quorum_threshold": quorum,
        }

    def peer_envelope(
        self,
        exclude_client_id: str,
        model_contract_sha256: str,
        *,
        latest_only: bool = True,
        round_index: Optional[int] = None,
    ) -> Tuple[Optional[Envelope], Dict[str, object]]:
        exclude = str(exclude_client_id or "unknown")
        contract = str(model_contract_sha256 or "")
        with self._lock:
            traces = [
                trace for trace in self._traces_for_contract(contract)
                if trace.client_id != exclude
            ]
            observations, round_info = self._round_synchronized_observations(
                traces,
                round_index=round_index,
                require_full_block=True,
            )
            envelope = Envelope(min_observations=self.min_observations)
            for observation in observations:
                if observation.block is None:
                    continue
                envelope.observe(observation.block, copy_block=False)

            full_capable = sum(
                1 for trace in traces
                if any(obs.block is not None for obs in trace.observations)
            )
            info: Dict[str, object] = {
                "peer_client_count": len(traces),
                "peer_full_block_client_count": full_capable,
                "peer_sketch_only_client_count": len(traces) - full_capable,
                "peer_envelope_observations": len(observations),
                "peer_contract_sha256": contract,
                "peer_registry_total_bytes": self._total_full_block_bytes,
                "peer_registry_total_mb": self._total_full_block_bytes / (1024.0 * 1024.0),
                "peer_envelope_requested_round": round_info["requested_round"],
                "peer_envelope_selected_round": round_info["selected_round"],
                "peer_envelope_round_source": round_info["round_source"],
                "peer_envelope_required_client_count": round_info["required_client_count"],
                "peer_envelope_selected_client_count": round_info["selected_client_count"],
            }
            if len(observations) >= self.min_peers and envelope.ready:
                info["peer_mode"] = "peer_full_envelope"
                return envelope, info
            if len(traces) >= self.min_peers:
                info["peer_mode"] = "peer_sketch_oracle_self_projection"
            else:
                info["peer_mode"] = "no_peers"
            return None, info

    def peer_geometry_matrix(
        self,
        exclude_client_id: str,
        model_contract_sha256: str,
        *,
        latest_only: bool = True,
        max_dimensions: Optional[int] = None,
        dtype=np.float32,
        round_index: Optional[int] = None,
    ) -> Tuple[Optional[np.ndarray], Dict[str, object]]:
        exclude = str(exclude_client_id or "unknown")
        contract = str(model_contract_sha256 or "")
        requested_dim = int(max_dimensions or self.geometry_sketch_dim)
        with self._lock:
            traces = [
                trace for trace in self._traces_for_contract(contract)
                if trace.client_id != exclude
            ]
            observations, round_info = self._round_synchronized_observations(
                traces,
                round_index=round_index,
                require_full_block=False,
            )
            rows = []
            peer_ids = []
            for trace in traces:
                chosen = None
                for observation in observations:
                    if any(observation is item for item in trace.observations):
                        chosen = observation
                        break
                if chosen is None:
                    continue
                sketch = chosen.sketch
                if requested_dim < sketch.size:
                    positions = np.linspace(0, sketch.size - 1, requested_dim, dtype=np.int64)
                    sketch = sketch[positions]
                rows.append(np.asarray(sketch, dtype=dtype))
                peer_ids.append(trace.client_id)
            info = {
                "peer_geometry_mode": "deterministic_coordinate_sketch",
                "peer_geometry_dimensions": int(rows[0].size) if rows else 0,
                "peer_geometry_rows": len(rows),
                "peer_geometry_peer_ids": ",".join(peer_ids),
                "peer_geometry_requested_round": round_info["requested_round"],
                "peer_geometry_selected_round": round_info["selected_round"],
                "peer_geometry_round_source": round_info["round_source"],
                "peer_geometry_required_client_count": round_info["required_client_count"],
                "peer_geometry_selected_client_count": round_info["selected_client_count"],
            }
            if not rows:
                return None, info
            return np.stack(rows, axis=0), info

    def peer_full_matrix(
        self,
        exclude_client_id: str,
        model_contract_sha256: str,
        *,
        latest_only: bool = True,
        dtype=np.float32,
        round_index: Optional[int] = None,
    ) -> Tuple[Optional[np.ndarray], Dict[str, object]]:
        exclude = str(exclude_client_id or "unknown")
        contract = str(model_contract_sha256 or "")
        with self._lock:
            traces = [
                trace for trace in self._traces_for_contract(contract)
                if trace.client_id != exclude
            ]
            observations, round_info = self._round_synchronized_observations(
                traces,
                round_index=round_index,
                require_full_block=True,
            )
            rows = []
            peer_ids = []
            for trace in traces:
                chosen = None
                for observation in observations:
                    if any(observation is item for item in trace.observations):
                        chosen = observation
                        break
                if chosen is None or chosen.block is None:
                    continue
                rows.append(flatten_block(chosen.block, dtype=dtype))
                peer_ids.append(trace.client_id)
            missing_full = [
                trace.client_id for trace in traces
                if not any(obs.block is not None for obs in trace.observations)
            ]
            info = {
                "peer_full_geometry_rows": len(rows),
                "peer_full_geometry_peer_ids": ",".join(peer_ids),
                "peer_full_geometry_missing_clients": ",".join(sorted(set(missing_full))),
                "peer_full_geometry_requested_round": round_info["requested_round"],
                "peer_full_geometry_selected_round": round_info["selected_round"],
                "peer_full_geometry_round_source": round_info["round_source"],
                "peer_full_geometry_required_client_count": round_info["required_client_count"],
                "peer_full_geometry_selected_client_count": round_info["selected_client_count"],
            }
            if not rows:
                return None, info
            return np.stack(rows, axis=0), info

    def fingerprint_table(self, model_contract_sha256: str = "") -> List[Dict[str, object]]:
        contract = str(model_contract_sha256 or "")
        with self._lock:
            traces = self._traces_for_contract(contract) if contract else list(self._traces.values())
            rows = []
            for trace in traces:
                if not trace.observations:
                    continue
                norms = np.asarray([obs.norm for obs in trace.observations], dtype=np.float64)
                rows.append({
                    "client_id": trace.client_id,
                    "model_contract_sha256": trace.contract_sha256,
                    "observations": len(trace.observations),
                    "last_round": trace.last_round,
                    "mean_update_norm": float(np.mean(norms)),
                    "median_update_norm": float(np.median(norms)),
                    "last_update_norm": float(norms[-1]),
                    "latest_has_full_block": int(trace.observations[-1].block is not None),
                    "sketch_dimensions": int(trace.observations[-1].sketch.size),
                })
            return rows

    def all_client_ids(self, model_contract_sha256: str = "") -> List[str]:
        contract = str(model_contract_sha256 or "")
        with self._lock:
            if contract:
                return sorted({t.client_id for t in self._traces_for_contract(contract)})
            return sorted({trace.client_id for trace in self._traces.values()})

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            contracts = sorted({contract for contract, _cid in self._traces})
            return {
                "contracts": contracts,
                "trace_count": len(self._traces),
                "total_bytes": self._total_full_block_bytes,
                "total_mb": self._total_full_block_bytes / (1024.0 * 1024.0),
                "memory_budget_mb": self.memory_budget_bytes / (1024.0 * 1024.0),
                "geometry_sketch_dim": self.geometry_sketch_dim,
                "full_block_max_mb": self.full_block_max_bytes / (1024.0 * 1024.0),
            }


_registry_lock = threading.RLock()


def get_peer_registry(args) -> PeerFingerprintRegistry:
    with _registry_lock:
        registry = getattr(args, "_peer_fingerprint_registry", None)
        if registry is None:
            registry = PeerFingerprintRegistry(
                window=int(getattr(args, "live_window", 5) or 0),
                min_peers=int(getattr(args, "live_min_peers", 2) or 2),
                min_observations=int(getattr(args, "live_peer_min_obs", 3) or 3),
                memory_budget_mb=int(getattr(args, "live_peer_memory_mb", 512) or 512),
                geometry_sketch_dim=int(getattr(args, "live_geometry_sketch_dim", 8192) or 8192),
                full_block_max_mb=int(getattr(args, "live_peer_full_block_max_mb", 16) or 16),
            )
            args._peer_fingerprint_registry = registry
            logger.info(
                "[PEER-FP] created registry window=%d budget_mb=%d sketch_dim=%d full_block_max_mb=%d",
                registry.window,
                int(registry.memory_budget_bytes / (1024 * 1024)),
                registry.geometry_sketch_dim,
                int(registry.full_block_max_bytes / (1024 * 1024)),
            )
        return registry


def observe_peer_update(
    args,
    *,
    client_id: str,
    round_index: int,
    genuine_update: Sequence[np.ndarray],
    model_contract_sha256: str = "",
    observation_id: str = "",
) -> Dict[str, object]:
    return get_peer_registry(args).observe(
        client_id,
        round_index,
        genuine_update,
        model_contract_sha256=model_contract_sha256,
        observation_id=observation_id,
    )
