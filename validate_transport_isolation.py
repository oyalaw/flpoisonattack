#!/usr/bin/env python3
"""Focused regression tests for V27.1 target/non-target HTTP/2 isolation."""

from __future__ import annotations

import argparse
import json
import socket
import threading
import time
from pathlib import Path

import poison_live as proxy


def base_args() -> argparse.Namespace:
    return argparse.Namespace(
        live_seed=1234,
        live_poison=True,
        live_attack="envelope",
        live_raw_attack="sign_flip",
        live_alpha=0.5,
        live_sigma=0.01,
        live_clip_ratio=0.3,
        live_start_message=0,
        live_end_message=-1,
        live_max_arrays_per_message=0,
        live_include_nonfloat=False,
        live_log_every=0,
        live_warmup=5,
        live_warmup_rounds=0,
        live_aggressiveness=0.5,
        poison_clients="10.42.0.210",
        poison_target_mode="static",
        adaptive_flow_control=True,
        max_message_mb=0,
        hard_max_message_gb=8.0,
        spool_threshold_mb=32,
        spool_dir=".proxy_spool_test_v27_1",
        spool_disk_reserve_mb=1,
        non_target_observation_queue_frames=128,
        require_update_space=True,
        global_model_max_age_s=600.0,
        require_global_round_match=False,
        download_phase_min_confidence=0.7,
        phase_gate_enabled=True,
        phase_gate_min_confidence=0.85,
        phase_gate_max_age_s=15.0,
        phase_gate_ignore_age=False,
        phase_gate_require_client=True,
        phase_gate_reject_sources="server_announce",
        update_sparsity_epsilon=1e-8,
        model_cache_entries_per_client=12,
        model_cache_memory_mb=128,
        model_cache_dir=".proxy_model_cache_test_v27_1",
        model_cache_disk_gb=1.0,
        live_k_coord=3.0,
        live_k_norm=3.0,
        live_window=5,
        live_ramp_rounds=2,
        live_adaptive_stealth=True,
        live_backoff_step=0.1,
        live_min_peers=2,
        live_peer_min_obs=3,
        live_derived_f=1,
        live_multi_krum_m=1,
        live_trimmed_beta=0.1,
        live_flame_cosine_threshold=0.1,
        live_active_defense="flame",
        live_geometry_sketch_dim=1024,
        live_peer_memory_mb=64,
        live_peer_full_block_max_mb=16,
        live_state_save_every=0,
        live_large_model_float32_threshold_elements=2_000_000,
        live_engine_cache_dir=".stealth_engine_cache_test_v27_1",
        live_engine_disk_threshold_mb=256.0,
        live_large_model_adaptive_backoff_steps=0,
        live_envelope_state="",
        reset_envelope_state=True,
        experiment_id="transport_isolation_test",
        run_id="transport_isolation_test",
        condition="test",
        proxy_run_id="transport_isolation_test",
    )


def recv_all(sock: socket.socket, timeout: float = 2.0) -> bytes:
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            data = sock.recv(65536)
        except socket.timeout:
            break
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks)


def test_non_target_exact_forwarding() -> dict:
    args = base_args()
    assert proxy.client_should_be_poisoned("10.42.0.47", args) is False

    client_app, proxy_src = socket.socketpair()
    proxy_dst, server_app = socket.socketpair()

    thread = threading.Thread(
        target=proxy.relay_http2_transparent_observe_client_to_server,
        args=(proxy_src, proxy_dst, "10.42.0.47", proxy.HTTP2_CLIENT_PREFACE[:4], None, None, None, args),
        daemon=True,
    )
    thread.start()

    payload1 = b"\x00" + (11).to_bytes(4, "big") + b"hello-world"
    payload2 = b"control-frame"
    frame1 = proxy.build_http2_frame_header(len(payload1), 0x0, 0x0, 1) + payload1
    frame2 = proxy.build_http2_frame_header(len(payload2), 0x4, 0x1, 1) + payload2
    expected = proxy.HTTP2_CLIENT_PREFACE + frame1 + frame2

    client_app.sendall(proxy.HTTP2_CLIENT_PREFACE[4:] + frame1 + frame2)
    client_app.shutdown(socket.SHUT_WR)

    received = recv_all(server_app)
    thread.join(timeout=3.0)

    client_app.settimeout(0.1)
    synthetic_credit_seen = False
    try:
        synthetic_credit_seen = bool(client_app.recv(4096))
    except (socket.timeout, BlockingIOError):
        synthetic_credit_seen = False

    for sock in (client_app, proxy_src, proxy_dst, server_app):
        try:
            sock.close()
        except Exception:
            pass

    assert received == expected, (len(received), len(expected))
    assert synthetic_credit_seen is False
    return {
        "client_ip": "10.42.0.47",
        "targeted": False,
        "exact_bytes_preserved": True,
        "expected_bytes": len(expected),
        "received_bytes": len(received),
        "synthetic_credit_seen_by_client": False,
    }



def test_non_target_downstream_exact_forwarding() -> dict:
    args = base_args()
    server_app, proxy_src = socket.socketpair()
    proxy_dst, client_app = socket.socketpair()

    thread = threading.Thread(
        target=proxy.relay_http2_transparent_observe_server_to_client,
        args=(proxy_src, proxy_dst, "10.42.0.47", None, None, None, args),
        daemon=True,
    )
    thread.start()

    settings_payload = b"\x00\x03\x00\x00\x00\x64"
    settings = proxy.build_http2_frame_header(len(settings_payload), 0x4, 0x0, 0) + settings_payload
    grpc_payload = b"\x00" + (12).to_bytes(4, "big") + b"global-model"
    data_frame = proxy.build_http2_frame_header(len(grpc_payload), 0x0, 0x1, 1) + grpc_payload
    expected = settings + data_frame

    server_app.sendall(expected)
    server_app.shutdown(socket.SHUT_WR)
    received = recv_all(client_app)
    thread.join(timeout=3.0)

    for sock in (server_app, proxy_src, proxy_dst, client_app):
        try:
            sock.close()
        except Exception:
            pass

    assert received == expected, (len(received), len(expected))
    return {
        "client_ip": "10.42.0.47",
        "targeted": False,
        "exact_bytes_preserved": True,
        "expected_bytes": len(expected),
        "received_bytes": len(received),
        "server_credit_suppressed_bytes": 0,
    }

def test_target_authorization_and_bridge() -> dict:
    args = base_args()
    assert proxy.client_should_be_poisoned("10.42.0.210", args) is True
    bridge = proxy.FlowControlBridge()
    before = bridge.snapshot()
    assert before["flow_control_synthetic_credit_bytes"] == 0
    return {
        "client_ip": "10.42.0.210",
        "targeted": True,
        "flow_bridge_available": True,
        "initial_synthetic_credit_bytes": before["flow_control_synthetic_credit_bytes"],
    }


def test_source_structure() -> dict:
    source = Path(proxy.__file__).read_text(encoding="utf-8")
    required = [
        "NON-TARGET HTTP/2 connection: transparent bidirectional relay;",
        "relay_http2_transparent_observe_client_to_server",
        "relay_http2_transparent_observe_server_to_client",
        "no rewriter, no synthetic WINDOW_UPDATE, no server-credit suppression",
        "connection_targeted = bool(client_should_be_poisoned(client_ip, args))",
    ]
    missing = [token for token in required if token not in source]
    assert not missing, missing
    return {"required_markers_present": True, "marker_count": len(required)}


def main() -> None:
    report = {
        "tool_version": "validate_transport_isolation_v27_1",
        "non_target_exact_forwarding": test_non_target_exact_forwarding(),
        "non_target_downstream_exact_forwarding": test_non_target_downstream_exact_forwarding(),
        "target_authorization": test_target_authorization_and_bridge(),
        "source_structure": test_source_structure(),
        "status": "PASS",
    }
    path = Path("TRANSPORT_ISOLATION_VALIDATION_V27_1.json")
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
