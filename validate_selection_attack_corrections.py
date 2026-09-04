#!/usr/bin/env python3
"""Focused regression checks for Min Sum, Krum Optimal, and peer round sync."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import numpy as np

from peer_fingerprint import PeerFingerprintRegistry
from selection_attacks import craft_min_sum, craft_selection_optimal, _pairwise_sq


def check_min_sum_squared_geometry() -> None:
    peers = np.asarray(
        [
            [1.0, 0.2, -0.1],
            [0.9, 0.1, -0.2],
            [1.1, 0.3, 0.0],
            [0.95, 0.25, -0.15],
        ],
        dtype=np.float64,
    )
    candidate, info = craft_min_sum(peers, strength=1.0)
    threshold = float(np.max(_pairwise_sq(peers).sum(axis=1)))
    candidate_sum = float(np.sum((peers - candidate) ** 2))
    assert info["boundary_distance_power"] == 2
    assert candidate_sum <= threshold + 1e-8

    half_candidate, half_info = craft_min_sum(peers, strength=0.5)
    assert abs(half_info["gamma"] - 0.5 * half_info["gamma_boundary"]) < 1e-10
    assert np.linalg.norm(half_candidate - peers.mean(axis=0)) <= np.linalg.norm(
        candidate - peers.mean(axis=0)
    ) + 1e-12


def check_krum_strength_and_defense() -> None:
    peers = np.asarray(
        [
            [1.0, 0.0],
            [0.95, 0.05],
            [1.05, -0.05],
            [0.98, 0.02],
        ],
        dtype=np.float64,
    )
    full, full_info = craft_selection_optimal(
        peers, f=1, selection_size=1, defense="krum", strength=1.0
    )
    half, half_info = craft_selection_optimal(
        peers, f=1, selection_size=1, defense="krum", strength=0.5
    )
    assert full_info["feasible"] and half_info["feasible"]
    assert abs(half_info["gamma"] - 0.5 * half_info["gamma_boundary"]) < 1e-10
    assert np.linalg.norm(half - peers.mean(axis=0)) <= np.linalg.norm(
        full - peers.mean(axis=0)
    ) + 1e-12

    _, invalid = craft_selection_optimal(peers, defense="fedavg")
    assert not invalid["feasible"]
    assert "unsupported_selection_defense" in invalid["reason"]


def check_round_synchronization() -> None:
    registry = PeerFingerprintRegistry(
        window=5,
        min_peers=2,
        min_observations=2,
        memory_budget_mb=16,
        geometry_sketch_dim=16,
        full_block_max_mb=16,
    )
    contract = "test-contract"
    clients = ["peer-a", "peer-b", "peer-c"]

    for round_id in (1, 2):
        for index, client in enumerate(clients):
            block = [np.full((4,), round_id + index / 10.0, dtype=np.float32)]
            registry.observe(
                client,
                round_id,
                block,
                model_contract_sha256=contract,
                observation_id=f"{client}:{round_id}",
            )

    # Only one peer has reached round 3. The registry must use round 2 rather
    # than mixing round 3 with round 2 observations from other clients.
    registry.observe(
        clients[0],
        3,
        [np.full((4,), 3.0, dtype=np.float32)],
        model_contract_sha256=contract,
        observation_id=f"{clients[0]}:3",
    )
    matrix, info = registry.peer_full_matrix(
        "target", contract, round_index=3, dtype=np.float32
    )
    assert matrix is not None and matrix.shape[0] == 3
    assert info["peer_full_geometry_selected_round"] == 2
    assert info["peer_full_geometry_round_source"] == "previous_complete_round"

    for index, client in enumerate(clients[1:], start=1):
        registry.observe(
            client,
            3,
            [np.full((4,), 3.0 + index / 10.0, dtype=np.float32)],
            model_contract_sha256=contract,
            observation_id=f"{client}:3",
        )
    matrix, info = registry.peer_full_matrix(
        "target", contract, round_index=3, dtype=np.float32
    )
    assert matrix is not None and matrix.shape[0] == 3
    assert info["peer_full_geometry_selected_round"] == 3
    assert info["peer_full_geometry_round_source"] == "exact_requested_round"


def check_proxy_preflight() -> None:
    import poison_live

    args = argparse.Namespace(
        live_poison=True,
        live_attack="envelope",
        live_raw_attack="krum_optimal",
        live_active_defense="fedavg",
        live_min_peers=2,
        live_geometry_sketch_dim=128,
        live_peer_memory_mb=16,
        live_state_save_every=0,
    )
    try:
        poison_live.validate_runtime_dependencies(args)
    except SystemExit as exc:
        assert "krum_optimal" in str(exc)
    else:
        raise AssertionError("FedAvg plus krum_optimal should fail preflight")


def main() -> None:
    check_min_sum_squared_geometry()
    check_krum_strength_and_defense()
    check_round_synchronization()
    check_proxy_preflight()
    print("PASS: selection attack corrections validated")


if __name__ == "__main__":
    main()
