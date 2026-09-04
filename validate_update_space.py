#!/usr/bin/env python3
"""V27 synthetic validation for the complete model-agnostic runtime stack.

Checks:
* dynamic tensor-contract discovery,
* disk-backed global-model caching,
* exact update-space reconstruction,
* norm-constrained sign-flip geometry,
* phase-gate fail-open behavior,
* peer observation from non-target clients,
* contract-isolated stealth engines,
* envelope warm-up and poisoning,
* active-defense-only oracle configuration,
* length-preserving payload rewrite,
* large-message disk-spool policy.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def load_proxy(path: Path):
    spec = importlib.util.spec_from_file_location("poison_live_v27_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load proxy module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def payload_from_block(block):
    output = bytearray(b"protobuf-prefix")
    for index, array in enumerate(block):
        buffer = io.BytesIO()
        np.save(buffer, np.asarray(array), allow_pickle=False)
        output.extend(buffer.getvalue())
        output.extend(f"separator-{index}".encode("ascii"))
    return bytes(output)


def make_args(tmp: Path):
    return argparse.Namespace(
        phase_gate_enabled=True,
        phase_gate_min_confidence=0.85,
        phase_gate_max_age_s=30.0,
        phase_gate_ignore_age=False,
        phase_gate_require_client=True,
        phase_gate_reject_sources="server_announce",
        require_update_space=True,
        global_model_max_age_s=600.0,
        require_global_round_match=False,
        download_phase_min_confidence=0.70,
        model_cache_entries_per_client=12,
        model_cache_memory_mb=1,
        model_cache_dir=str(tmp / "model_cache"),
        model_cache_disk_gb=2.0,
        model_min_float_arrays=2,
        model_min_elements=10,
        update_sparsity_epsilon=1e-8,
        live_poison=True,
        live_attack="clip",
        live_clip_ratio=0.3,
        live_alpha=1.0,
        live_sigma=0.01,
        live_seed=1234,
        live_include_nonfloat=False,
        live_start_message=0,
        live_end_message=-1,
        live_max_arrays_per_message=0,
        live_log_every=0,
        poison_clients="10.42.0.210",
        poison_target_mode="static",
        experiment_id="synthetic_v27",
        run_id="synthetic_v27",
        condition="validation",
        proxy_run_id="proxy_validation",
        max_message_mb=0,
        hard_max_message_gb=8.0,
        spool_threshold_mb=32,
        spool_dir=str(tmp / "spool"),
        spool_disk_reserve_mb=0,
        adaptive_flow_control=True,
        live_warmup=2,
        live_warmup_rounds=0,
        live_window=3,
        live_aggressiveness=0.5,
        live_raw_attack="sign_flip",
        live_k_coord=3.0,
        live_k_norm=3.0,
        live_envelope_state="",
        live_state_save_every=0,
        live_ramp_rounds=0,
        live_adaptive_stealth=True,
        live_backoff_step=0.1,
        live_min_peers=2,
        live_peer_min_obs=2,
        live_peer_memory_mb=64,
        live_peer_full_block_max_mb=16,
        live_geometry_sketch_dim=1024,
        live_large_model_float32_threshold_elements=100_000,
        live_engine_cache_dir=str(tmp / "engine_cache"),
        live_engine_disk_threshold_mb=256.0,
        live_large_model_adaptive_backoff_steps=0,
        live_derived_f=1,
        live_multi_krum_m=1,
        live_trimmed_beta=0.1,
        live_flame_cosine_threshold=0.1,
        live_active_defense="flame",
    )


def cosine(a, b):
    dot = 0.0
    aa = 0.0
    bb = 0.0
    for x, y in zip(a, b):
        xv = np.asarray(x, dtype=np.float64).ravel()
        yv = np.asarray(y, dtype=np.float64).ravel()
        dot += float(np.dot(xv, yv))
        aa += float(np.dot(xv, xv))
        bb += float(np.dot(yv, yv))
    denom = math.sqrt(aa) * math.sqrt(bb)
    return dot / denom if denom > 0 else 0.0


def norm(block):
    return math.sqrt(
        sum(float(np.dot(np.asarray(a, dtype=np.float64).ravel(), np.asarray(a, dtype=np.float64).ravel())) for a in block)
    )


def subtract(left, right):
    return [
        (np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)).astype(a.dtype)
        for a, b in zip(left, right)
    ]


def set_phase(state, client_ip, phase, round_id):
    state.update_sniffer_metadata(
        {
            "phase": phase,
            "round": round_id,
            "confidence": 0.99,
            "client_ip": client_ip,
            "phase_source": "phase_classifier",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy", type=Path, default=HERE / "poison_live.py")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    proxy_path = args.proxy.expanduser().resolve()
    proxy = load_proxy(proxy_path)

    with tempfile.TemporaryDirectory(prefix="fl_v27_validation_") as tmp_text:
        tmp = Path(tmp_text)
        cfg = make_args(tmp)
        preflight = proxy.validate_runtime_dependencies(cfg)
        if not preflight.get("stealth_engine_available"):
            raise AssertionError(f"stealth engine unavailable: {preflight}")
        state = proxy.AttackerDashboardState(cfg)
        proxy._set_dashboard_state(state)
        rng = np.random.default_rng(7)
        target_ip = "10.42.0.210"

        global_block = [
            np.full((320, 1024), 0.25, dtype=np.float32),
            np.full((257,), -0.5, dtype=np.float32),
            np.full((17, 13, 5), 0.125, dtype=np.float32),
        ]

        # -------- direct update-space path --------
        genuine_delta = [rng.normal(0.0, 0.002, size=a.shape).astype(np.float32) for a in global_block]
        local_block = [(g + d).astype(g.dtype) for g, d in zip(global_block, genuine_delta)]
        set_phase(state, target_ip, "MODEL_DOWNLOAD", 1)
        snapshot = proxy.get_model_cache(cfg).store(target_ip, global_block, 0, 3)
        set_phase(state, target_ip, "MODEL_UPLOAD", 1)
        payload = payload_from_block(local_block)
        new_payload, modified, reason, details, found, written = proxy.process_update_space_upload(
            payload,
            client_ip=target_ip,
            message_index=0,
            stream_id=3,
            args=cfg,
            rng=rng,
        )
        assert modified, (reason, details)
        assert len(new_payload) == len(payload)
        assert found == len(global_block) and written == len(global_block)
        poisoned_local, _, _ = proxy.extract_float_model_block(new_payload, cfg)
        projected_update = subtract(poisoned_local, global_block)
        ratio = norm(projected_update) / (norm(genuine_delta) + 1e-12)
        cos = cosine(genuine_delta, projected_update)
        assert abs(ratio - 0.3) < 5e-4, ratio
        assert cos < -0.999, cos
        assert details.get("projected_update_sha256")
        assert snapshot.storage_mode in {"disk_mmap", "disk", "mmap"}

        # Wrong phase must fail open.
        set_phase(state, target_ip, "LOCAL_TRAINING", 2)
        unchanged, modified2, reason2, details2, _, _ = proxy.process_update_space_upload(
            payload,
            client_ip=target_ip,
            message_index=1,
            stream_id=3,
            args=cfg,
            rng=rng,
        )
        assert not modified2 and unchanged == payload and details2.get("phase_gate_open") == 0

        # -------- envelope + peer observation path --------
        cfg.live_attack = "envelope"
        cfg.live_alpha = 0.5
        peers = ["10.42.0.18", "10.42.0.47", "10.42.0.145"]
        contract_hash = None
        for round_id in range(1, 4):
            # Observe all non-target peers without modifying their bytes.
            for peer_idx, peer_ip in enumerate(peers):
                peer_delta = [
                    rng.normal(0.0, 0.002 + peer_idx * 0.0001, size=a.shape).astype(np.float32)
                    for a in global_block
                ]
                peer_local = [(g + d).astype(g.dtype) for g, d in zip(global_block, peer_delta)]
                set_phase(state, peer_ip, "MODEL_DOWNLOAD", round_id)
                proxy.get_model_cache(cfg).store(peer_ip, global_block, round_id - 1, 3)
                set_phase(state, peer_ip, "MODEL_UPLOAD", round_id)
                peer_payload = payload_from_block(peer_local)
                same, mod, peer_reason, peer_details, _, _ = proxy.process_update_space_upload(
                    peer_payload,
                    client_ip=peer_ip,
                    message_index=round_id - 1,
                    stream_id=3,
                    args=cfg,
                    rng=rng,
                    allow_modify=False,
                )
                assert not mod and same == peer_payload
                assert peer_details.get("peer_observation_recorded") == 1, (peer_reason, peer_details)
                contract_hash = contract_hash or peer_details.get("model_contract_sha256")

            target_delta = [rng.normal(0.0, 0.002, size=a.shape).astype(np.float32) for a in global_block]
            target_local = [(g + d).astype(g.dtype) for g, d in zip(global_block, target_delta)]
            set_phase(state, target_ip, "MODEL_DOWNLOAD", round_id)
            proxy.get_model_cache(cfg).store(target_ip, global_block, round_id - 1, 3)
            set_phase(state, target_ip, "MODEL_UPLOAD", round_id)
            target_payload = payload_from_block(target_local)
            out, mod, target_reason, target_details, _, _ = proxy.process_update_space_upload(
                target_payload,
                client_ip=target_ip,
                message_index=round_id - 1,
                stream_id=3,
                args=cfg,
                rng=rng,
            )
            if round_id <= cfg.live_warmup:
                assert not mod and target_reason == "warmup_observe_only", (round_id, target_reason)
            else:
                assert mod and target_reason == "update_space_poison_applied", target_details
                assert target_details.get("peer_mode") == "peer", target_details
                assert int(target_details.get("peer_client_count", 0)) >= 2
                assert target_details.get("active_defense") == "flame"
                assert target_details.get("oracle_evaluated_defenses") == "flame"
                assert int(target_details.get("oracle_geometry_dimensions", 0)) <= cfg.live_geometry_sketch_dim

        # Contract-isolated engines.
        engine_a = proxy._get_client_stealth_engine(cfg, target_ip, str(contract_hash))
        engine_b = proxy._get_client_stealth_engine(cfg, target_ip, "different_contract_for_test")
        assert engine_a is not engine_b
        assert engine_a.model_contract_sha256 != engine_b.model_contract_sha256

        # Large-message policy.
        policy = proxy.MessageSizePolicy(
            max_message_mb=0,
            hard_max_message_gb=8.0,
            spool_threshold_mb=32,
            spool_dir=tmp / "policy_spool",
            disk_reserve_mb=0,
        )
        decision = policy.decide(128 * 1024 * 1024)
        assert decision.allowed and decision.buffer_mode == "disk_spool"

        registry_snapshot = getattr(cfg, "_peer_fingerprint_registry").snapshot()
        result = {
            "tool_version": "validate_update_space_v27",
            "status": "PASS",
            "proxy": str(proxy_path),
            "direct_clip": {
                "tensor_count": found,
                "global_model_storage_mode": snapshot.storage_mode,
                "projected_to_genuine_norm_ratio": ratio,
                "cosine_genuine_to_projected": cos,
                "payload_length_preserved": len(new_payload) == len(payload),
            },
            "envelope_peer_path": {
                "peer_registry_snapshot": registry_snapshot,
                "model_contract_sha256": contract_hash,
                "target_engine_contract": engine_a.model_contract_sha256,
                "active_defense": engine_a.active_defense,
                "oracle_defenses": list(engine_a.oracle_defenses),
                "geometry_sketch_dim": engine_a.geometry_sketch_dim,
            },
            "phase_gate_fail_open_verified": True,
            "message_policy_128mib": {
                "allowed": decision.allowed,
                "buffer_mode": decision.buffer_mode,
                "hard_limit_bytes": policy.hard_limit_bytes,
            },
            "runtime_preflight": preflight,
        }

        text = json.dumps(result, indent=2, sort_keys=True)
        print(text)
        if args.output_json:
            args.output_json.write_text(text + "\n", encoding="utf-8")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
