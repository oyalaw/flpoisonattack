# WHEN TRAINING IS LATCH, IT KEEPS LOGGING TRAINING DATA IN THE CSV
#the fields are also added to Decisioin Log
#WE ENSURE WE HAVE UNIFIED LOGGING FOR DECISION & DATASHADOW LOGS
import csv
import json
import os
import time
import socket
import threading
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass
from statistics import median
from typing import Dict, Optional, Tuple
import signal
import sys
import atexit

import numpy as np
try:
    import psutil  # type: ignore
except ImportError:
    psutil = None
import resource
import redis

RUN_TS = datetime.now().strftime("%Y%m%d_%H%M%S")

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
ANALYZER_HOST = "0.0.0.0"
ANALYZER_PORT = 5005

ATTACK_CHANNEL = "attack_channel"

_ATTACK_TRUE_VALUES = {"1", "true", "yes", "y", "on", "attack", "enable", "enabled"}
_ATTACK_FALSE_VALUES = {"0", "false", "no", "n", "off", "none", "disable", "disabled", "benign"}

_ATTACK_MODE_ALIASES = {
    "1": "throttle",
    "2": "delay",
    "3": "throttle_delay",
    "4": "poison",
    "5": "delay_poison",
    "tbf": "throttle",
    "bandwidth": "throttle",
    "rate": "throttle",
    "netem": "delay",
    "jitter": "delay",
    "both": "throttle_delay",
    "mixed": "throttle_delay",
    "throttle+delay": "throttle_delay",
    "throttle+jitter": "throttle_delay",
    "delay_throttle": "throttle_delay",
    "poisoning": "poison",
    "update_poison": "poison",
    "update_substitution": "poison",
    "hybrid_poison": "delay_poison",
    "poison_delay": "delay_poison",
    "delay+poison": "delay_poison",
}
_VALID_ATTACK_MODES = {"throttle", "delay", "throttle_delay", "poison", "delay_poison"}


def _parse_bool_choice(value: str, default: bool = False) -> bool:
    value = str(value or "").strip().lower()
    if value in _ATTACK_TRUE_VALUES:
        return True
    if value in _ATTACK_FALSE_VALUES:
        return False
    return bool(default)


def _normalize_analyzer_attack_mode(raw_value: str) -> str:
    mode = str(raw_value or "").strip().lower()
    mode = _ATTACK_MODE_ALIASES.get(mode, mode)
    if mode not in _VALID_ATTACK_MODES:
        raise SystemExit(
            "CRITICAL: Unsupported analyzer attack mode. Use throttle, delay, "
            "throttle_delay, or choose 1, 2, or 3."
        )
    return mode


def choose_attack_enabled() -> bool:
    env_value = os.environ.get("ANALYZER_ATTACK_ENABLED", os.environ.get("ATTACK_ENABLED", "")).strip()
    if env_value:
        return _parse_bool_choice(env_value, default=False)

    if not sys.stdin.isatty():
        print(
            ">>> ANALYZER_ATTACK_ENABLED/ATTACK_ENABLED not set and stdin is not interactive; "
            "defaulting to non-attack mode.",
            flush=True,
        )
        return False

    print("\nChoose analyzer experiment mode:", flush=True)
    print("  1) non_attack   Monitor and log only; do not send attack triggers", flush=True)
    print("  2) attack       Monitor, log, and send attack triggers to intervener", flush=True)
    while True:
        choice = input("Enter choice [1/2] or mode name: ").strip().lower()
        if choice in {"", "1", "non_attack", "non-attack", "benign", "no", "n", "off"}:
            return False
        if choice in {"2", "attack", "yes", "y", "on"}:
            return True
        print("Invalid choice. Enter 1/non_attack or 2/attack.", flush=True)


def choose_analyzer_attack_mode() -> str:
    env_mode = os.environ.get("ANALYZER_ATTACK_MODE", os.environ.get("FL_ATTACK_MODE", "")).strip()
    if env_mode:
        return _normalize_analyzer_attack_mode(env_mode)

    if not sys.stdin.isatty():
        print(
            ">>> ANALYZER_ATTACK_MODE/FL_ATTACK_MODE not set and stdin is not interactive; "
            "defaulting to delay mode for release policy.",
            flush=True,
        )
        return "delay"

    print("\nChoose analyzer release policy mode:", flush=True)
    print("  1) throttle        Analyzer sends release signals on UPLOAD close", flush=True)
    print("  2) delay           Analyzer does not send release; intervener uses elapsed release", flush=True)
    print("  3) throttle_delay  Analyzer does not send release; intervener uses elapsed release", flush=True)
    print("  4) poison          Analyzer sends Upload trigger to poison proxy only", flush=True)
    print("  5) delay_poison    Analyzer sends trigger to both delay intervener and poison proxy", flush=True)
    while True:
        choice = input("Enter choice [1/2/3/4/5] or mode name: ").strip()
        try:
            return _normalize_analyzer_attack_mode(choice)
        except SystemExit:
            print("Invalid choice. Enter throttle, delay, throttle_delay, poison, delay_poison, or 1, 2, 3, 4, 5.", flush=True)


ATTACK_ENABLED = choose_attack_enabled()
ANALYZER_ATTACK_MODE = choose_analyzer_attack_mode() if ATTACK_ENABLED else "none"
ANALYZER_SEND_RELEASE = ATTACK_ENABLED and ANALYZER_ATTACK_MODE == "throttle"

INTERVENER_HOST = "127.0.0.1" # Communication From Analyzer to Intervener
INTERVENER_PORT = 6006 # Communication From Analyzer to Intervener
POISONER_HOST = os.environ.get("POISONER_HOST", "127.0.0.1")
POISONER_PORT = int(os.environ.get("POISONER_PORT", "7007"))
DEFAULT_FL_SERVER_PORT = int(os.environ.get("FL_SERVER_PORT", "8080"))
attack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Communication From Analyzer to Intervener
outcome_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Wire-upload outcome feedback to Intervener
poison_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Analyzer to poison proxy control channel
sock = None  # Analyzer UDP receive socket; kept global so cleanup can close it.


STATE_KEY = "current_fl_state"
TARGET_CLIENT_KEY = "current_target_client"
CLIENT_RANKING_KEY = "current_client_ranking"

CLIENT_STATE_PREFIX = "current_fl_state:"
CLIENT_PHASE_PREFIX = "current_phase_label:"
CLIENT_DIRECTION_PREFIX = "current_live_direction:"
CLIENT_CONFIDENCE_PREFIX = "current_state_confidence:"
CLIENT_PHASE_TS_PREFIX = "current_phase_ts:"
CLIENT_MEAN_UPLOAD_TIME_PREFIX = "mean_upload_time:"
PENDING_ATTACK_CONTEXT_PREFIX = "pending_attack_context:"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
DATASET_FILE = os.path.join(DATA_DIR, f"shadow_dataset_{RUN_TS}.csv")
EVENT_LOG_FILE = os.path.join(DATA_DIR, f"analyzer_events_{RUN_TS}.jsonl")
LATEST_DATASET_FILE = os.path.join(DATA_DIR, "shadow_dataset.csv")
LATEST_EVENT_LOG_FILE = os.path.join(DATA_DIR, "analyzer_events.jsonl")
PHASE_LOG_FILE = os.path.join(DATA_DIR, f"analyzer_phase_log_{RUN_TS}.csv")
ROUND_LOG_FILE = os.path.join(DATA_DIR, f"analyzer_round_log_{RUN_TS}.csv")
DECISION_LOG_FILE = os.path.join(DATA_DIR, f"analyzer_decision_log_{RUN_TS}.csv")
WIRE_UPLOAD_LOG_FILE = os.path.join(DATA_DIR, f"analyzer_wire_upload_log_{RUN_TS}.csv")
LATEST_WIRE_UPLOAD_LOG_FILE = os.path.join(DATA_DIR, "analyzer_wire_upload_log.csv")

EXPERIMENT_ID = os.environ.get("EXPERIMENT_ID", f"exp_{int(time.time())}")

A = np.array([
    [0.88, 0.12, 0.00, 0.00],  # IDLE     → IDLE/DOWNLOAD
    [0.00, 0.58, 0.42, 0.00],  # DOWNLOAD → DOWNLOAD/TRAINING
    [0.00, 0.00, 0.78, 0.22],  # TRAINING → TRAINING/UPLOAD
    [0.20, 0.20, 0.00, 0.60],  # UPLOAD   → IDLE/DOWNLOAD/UPLOAD
], dtype=float)
# Row 3 change: UPLOAD→DOWNLOAD 0.00→0.20 (direct next-round path),
# UPLOAD→TRAINING 0.10→0.00 (removed, not valid in fixed protocol),
# UPLOAD→UPLOAD   0.70→0.60 (reduced to accommodate new DOWNLOAD path).

INITIAL_BELIEF = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)

DENSITY_WINDOW = 200
IAT_WINDOW = 200
PACKET_SIZE_WINDOW = 200
STATE_HISTORY_WINDOW = 16
DIRECTION_HISTORY_WINDOW = 16
UPLINK_SIZE_WINDOW = 16
ATTACK_COOLDOWN_SECONDS = 5.0
STARTUP_GRACE_PERIOD_SECONDS = 20.0
system_start_time = time.time()

SOFTMAX_TEMPERATURE = 2.2
EPS = 1e-6
MIN_FAST_UPLOAD_PACKET_SIZE = 256
MIN_VALID_PAYLOAD_BYTES = 32
WIRE_UPLOAD_MIN_PAYLOAD_BYTES = 256
# Minimum real upload packets required before an UPLOAD -> DOWNLOAD boundary can complete a round.
# This blocks one-packet upload fragments from creating extra inferred rounds under attack.
MIN_UPLOAD_COMPLETION_PACKETS = 3
# Timing-free round-count guard.  This is deliberately small and model agnostic:
# it blocks ACK/control-only or one-packet micro upload fragments from creating
# extra rounds, while still allowing compact RNN uploads.  It is used only for
# online round counting; upload validity remains a diagnostic label.
# Packets at or below this size are keepalive / ACK / control frames that
# carry no meaningful transfer direction. Their direction is neutralised to 0
# in normalize_packet_fields so they cannot skew HMM emission scores, feature
# direction ratios, or transfer-evidence tests toward DOWNLOAD or UPLOAD.
# Value intentionally matches TRAINING_LATCH_MAX_CONTROL_PAYLOAD (128 bytes).
KEEPALIVE_MAX_PAYLOAD_BYTES = 128

CLIENT_ACTIVITY_WINDOW_SECONDS = 40.0
CLIENT_IDLE_TIMEOUT_SECONDS = 60.0
RANK_REFRESH_SECONDS = 1.0
TARGET_SELECTION_TIE_MARGIN = 0.75
TARGET_SELECTION_DEFER_SECONDS = 0 #0.35
TARGET_SELECTION_PROGRESS_READY = 0.65
TARGET_SELECTION_RECENT_ATTACK_WINDOW_ROUNDS = 3
UPLOAD_CANDIDATE_THRESHOLD = 0.55
UPLOAD_CONFIRMED_THRESHOLD = 0.75
UPLOAD_ATTACKABLE_HOLD_SECONDS = 0
UPLOAD_SCORE_WINDOW_SECONDS = 0.35
UPLOAD_CONTEXT_RECENCY_SECONDS = 2.0
UPLOAD_INVALIDATE_INBOUND_SHARE = 0.75
UPLOAD_INVALIDATE_IDLE_SECONDS = 0.25
# In synchronous FL, all clients start the next round within a few seconds of
# each other (server waits for all clients before aggregating). Peers active
# within this window are considered to be in the same FL round and will have
# their round counters aligned when any peer completes a cycle.

MIN_STATE_HOLD_PACKETS = 5
MIN_STATE_HOLD_SECONDS = 0.0  # timing-free transition authority
MIN_STATE_DWELL_SECONDS = {
    0: 0.0,
    1: 0.0,
    2: 0.0,
    3: 0.0,   # timing-free transition authority
}

MIN_ROUND_GAP_SECONDS = 0.0  # timing-free round authority; duplicate guard is cycle_stage

KALMAN_Q = 1e-4
KALMAN_R = 5e-3
KALMAN_P0 = 1.0

ADAPTIVE_UPLOAD_MIN_HISTORY = 3
BASELINE_WARMUP_UPLOADS = int(os.environ.get("BASELINE_WARMUP_UPLOADS", "3"))
ADAPTIVE_DURATION_ALPHA = 0.50
ADAPTIVE_BYTES_ALPHA = 0.50

# Bootstrap thresholds used ONLY for the first ADAPTIVE_UPLOAD_MIN_HISTORY
# episodes, before per-client history is available.  These are intentionally
# very permissive so any real upload burst passes regardless of model size.
# Once history accumulates these values play no further role — thresholds
# are derived entirely from observed episodes and carry no hardcoded byte floor.
UPLOAD_DURATION_FLOOR_SECONDS = 0.10   # was 0.30
UPLOAD_BYTES_FLOOR = 1000              # was 250000 — now just a sanity guard
                                       # against counting ACK-only episodes

# How far below the observed median the threshold is allowed to sit.
# 0.25 means the threshold is at most 25 percent of the observed median,
# preventing a single anomalously large episode from raising the bar so
# high that subsequent normal episodes are rejected.
ADAPTIVE_BYTES_MIN_FRACTION = 0.25
ADAPTIVE_DURATION_MIN_FRACTION = 0.25

DEFAULT_MEAN_UPLOAD_TIME_SECONDS = 2.0
MIN_MEAN_UPLOAD_TIME_SECONDS = 0.25
MAX_MEAN_UPLOAD_TIME_SECONDS = 60.0

IDLE = 0
DOWNLOAD = 1
TRAINING = 2
UPLOAD = 3

PHASE_IDLE = "IDLE"
PHASE_DOWNLOAD = "DOWNLOAD"
PHASE_TRAINING = "TRAINING"
PHASE_UPLOAD = "UPLOAD"

ADAPTIVE_RULE_WINDOW_SHORT = 20
ADAPTIVE_RULE_WINDOW_LONG = 80
ADAPTIVE_RULE_WARMUP_MIN = 12

last_rank_refresh_time = 0.0
selected_target_client = None

packet_clock_by_flow: Dict[Tuple[str, int], float] = {}

PHASE_CONFIDENCE_THRESHOLD = 0.50

# Fast-exit from TRAINING when raw HMM + live phase agree consecutively.
# Three packets is enough because by this point HMM confidence is already
# ~0.98 and all three signal sources (raw, live, adaptive) agree — holding
# longer only adds latency without improving accuracy.
TRAINING_FAST_EXIT_MIN_PACKETS = 1  # timing-free: one meaningful boundary packet is enough
TRAINING_FAST_EXIT_MIN_CONFIDENCE = 0.80
PHASE_GAP_THRESHOLD = 0.01
PHASE_MIN_PAYLOAD = 200
PHASE_MIN_STREAK = 3

# Timing-free round-completion evidence guard. These are deliberately
# very small and model-agnostic: they block ACK/control micro-cycles
# without requiring CNN-sized uploads.
MIN_ROUND_UPLOAD_EVIDENCE_PACKETS = 2
MIN_ROUND_UPLOAD_EVIDENCE_BYTES = 2 * PHASE_MIN_PAYLOAD

LIVE_IDLE_PAYLOAD_MAX = 128
LIVE_IDLE_IAT_MIN = 0.050
LIVE_TRANSFER_FAST_IAT = 0.010
LIVE_TRANSFER_MODERATE_IAT = 0.020
LIVE_MIN_TRANSFER_PAYLOAD = 200

PHASE_DRIVING_MIN_PAYLOAD = 128
UPLOAD_TO_DOWNLOAD_MIN_INBOUND_FRAC = 0.60
UPLOAD_TO_DOWNLOAD_MIN_LARGE_FRAC = 0.55
UPLOAD_TO_DOWNLOAD_MIN_DENSE = 0.55
UPLOAD_TO_DOWNLOAD_MIN_INBOUND_RUN = 2
UPLOAD_TO_DOWNLOAD_STATE_HOLD_PACKETS = 1
UPLOAD_TO_DOWNLOAD_STATE_HOLD_SECONDS = 0.0
UPLOAD_TO_DOWNLOAD_MIN_CONFIDENCE = 0.40
# How long after the last large inbound packet a download burst is still
# considered valid evidence for the UPLOAD->DOWNLOAD transition guard.
# Fast FL model downloads can complete in <<300 ms, so this window must be
# long enough to bridge the gap between burst end and the post-burst control
# packet that finally triggers state promotion.
UPLOAD_TO_DOWNLOAD_BURST_EVIDENCE_WINDOW_SECONDS = 0.0  # timing-free: no recent-time evidence window

# Model agnostic boundary evidence settings.
# The full 1 second feature window can be polluted by the previous phase,
# especially for small or fast models.  Boundary decisions therefore use
# the current packet first, a short recent window second, and the long
# window only as supporting evidence.
SHORT_FEATURE_WINDOW_SECONDS = float(os.environ.get("SHORT_FEATURE_WINDOW_SECONDS", "0.20"))
BOUNDARY_MIN_WINDOW_SHARE = float(os.environ.get("BOUNDARY_MIN_WINDOW_SHARE", "0.35"))
BOUNDARY_STRONG_WINDOW_SHARE = float(os.environ.get("BOUNDARY_STRONG_WINDOW_SHARE", "0.60"))
BOUNDARY_MIN_CONFIDENCE = float(os.environ.get("BOUNDARY_MIN_CONFIDENCE", "0.40"))

LIVE_MAX_LAG_SECONDS = 2.0

TRAINING_LATCH_MIN_GAP_SECONDS = 0.0  # timing-free latch authority
TRAINING_LATCH_MAX_CONTROL_PAYLOAD = 128
DOWNLOAD_GAP_HISTORY_WINDOW = 64
DOWNLOAD_GAP_CLUSTER_ITERS = 12
TRAINING_LATCH_MIN_UPLOAD_PACKETS = 5
TRAINING_LATCH_MIN_DOWNLOAD_PACKETS = 1

UDP_RECV_TIMEOUT_SECONDS = 0.05
TRAINING_SILENCE_TIMEOUT_SECONDS = 0.0
TRAINING_LATCH_LOG_INTERVAL_SECONDS = 0.50

# Adaptive TRAINING -> UPLOAD sanity gate.  This blocks false micro fit phases
# without making UPLOAD completion depend on fixed elapsed time.
TRAINING_TO_UPLOAD_MEDIAN_IAT_MULTIPLIER = 3.0
TRAINING_TO_UPLOAD_MIN_FLOOR_SECONDS = 0.0
TRAINING_TO_UPLOAD_MAX_GATE_SECONDS = 0.0
TRAINING_TO_UPLOAD_IAT_FILTER_MAX_SECONDS = 0.50

client_stats = defaultdict(
    lambda: {
        "uplink_bytes": 0.0,
        "uplink_packets": 0,
        "downlink_bytes": 0.0,
        "downlink_packets": 0,
        "recent_iats": deque(maxlen=30),
        "last_seen": 0.0,
        "last_state_seen": 0,
    }
)

client_runtime = defaultdict(
    lambda: {
        "belief": INITIAL_BELIEF.copy(),
        "recent_densities": deque(maxlen=DENSITY_WINDOW),
        "recent_iats": deque(maxlen=IAT_WINDOW),
        "recent_packet_sizes": deque(maxlen=PACKET_SIZE_WINDOW),
        "recent_states": deque(maxlen=STATE_HISTORY_WINDOW),
        "recent_directions": deque(maxlen=DIRECTION_HISTORY_WINDOW),
        "recent_uplink_sizes": deque(maxlen=UPLINK_SIZE_WINDOW),
        "last_attack_time": 0.0,
        "last_attack_round_id": 0,
        "recent_attack_rounds": deque(maxlen=8),
        "recent_attack_timestamps": deque(maxlen=8),
        "attack_active_until": 0.0,
        "active_attack_id": "",
        "raw_state": 0,
        "stable_state": 0,
        "candidate_state": 0,
        "candidate_count": 0,
        "candidate_first_ts": 0.0,
        "stable_state_since": 0.0,
        "kalman_x": None,
        "kalman_p": KALMAN_P0,
        "phase_history": deque(maxlen=10),
        "last_phase": 0,
        "cycle_stage": 0,
        "inferred_round_id": 1,
        "completed_cycle_id": 0,
        "upload_episode_active": False,
        "upload_episode_start_ts": 0.0,
        "upload_episode_last_ts": 0.0,
        "upload_episode_bytes": 0,
        "upload_episode_packets": 0,
        "current_upload_bytes": 0,
        "previous_upload_bytes": 0,
        "normal_upload_samples": deque(maxlen=max(BASELINE_WARMUP_UPLOADS, 1)),
        "normal_upload_bandwidth_samples": deque(maxlen=max(BASELINE_WARMUP_UPLOADS, 1)),
        "normal_upload_duration_s": 0.0,
        "normal_upload_bytes": 0,
        "normal_upload_packets": 0,
        "mean_effective_bandwidth_mbps": 0.0,
        "baseline_ready": False,
        "last_round_increment_ts": 0.0,
        "upload_duration_history": deque(maxlen=20),
        "upload_bytes_history": deque(maxlen=20),
        "upload_packet_history": deque(maxlen=20),
        "live_phase": PHASE_IDLE,
        "live_phase_confidence": 0.0,
        "live_direction_label": "unknown",
        "training_latched": False,
        "training_start_ts": 0.0,
        "last_training_latch_log_ts": 0.0,
        "last_download_like_ts": 0.0,
        "last_upload_like_ts": 0.0,
        "recent_download_gaps": deque(maxlen=DOWNLOAD_GAP_HISTORY_WINDOW),
        "recent_feature_packets": deque(maxlen=200),
        "recent_feature_payloads": deque(maxlen=200),
        "recent_feature_timestamps": deque(maxlen=200),
        "recent_inbound_bytes": deque(maxlen=200),
        "recent_outbound_bytes": deque(maxlen=200),
        "recent_inbound_counts": deque(maxlen=200),
        "recent_outbound_counts": deque(maxlen=200),
        "recent_dir_balance": deque(maxlen=200),
        "recent_dir_ratios": deque(maxlen=200),
        "recent_inbound_density": deque(maxlen=200),
        "recent_outbound_density": deque(maxlen=200),
        "phase_record_label": None,
        "phase_record_start_ts": 0.0,
        "phase_record_start_wall_ns": 0,
        "phase_record_start_mono_ns": 0,
        "phase_record_round_id": 0,
        "phase_record_src_ip": "",
        "phase_record_dst_ip": "",
        "phase_record_server_host": "",
        "phase_record_last_ts": 0.0,
        "round_record_active": False,
        "round_record_start_ts": 0.0,
        "round_record_last_ts": 0.0,
        "round_record_round_id": 1,
        "last_processed_attack_id": "",
        "last_large_inbound_ts": 0.0,
        # Consecutive-packet streaks used by maybe_apply_training_fast_exit.
        # Kept separate from candidate_count so the training latch cannot
        # reset them by writing candidate_count=1 on every latched packet.
        "training_exit_download_streak": 0,
        "training_exit_upload_streak": 0,
        # Streak counter for UPLOAD->DOWNLOAD fast-exit.
        "upload_exit_download_streak": 0,
        "upload_candidate": False,
        "upload_confirmed": False,
        "attackable_upload": False,
        "upload_confirmed_since": 0.0,
        "recent_validated_upload_ts": 0.0,
        "upload_score": 0.0,
        "packet_support_score": 0.0,
        "phase_agreement_score": 0.0,
        "direction_persistence_score": 0.0,
        "round_context_score": 0.0,
    }
)

wire_upload_state = defaultdict(lambda: {
    "active": False,
    "client_id": "",
    "round_id": 0,
    "start_ts": 0.0,
    "last_ts": 0.0,
    "bytes": 0,
    "packets": 0,
    "iat_values": [],
    "first_wall_time_ns": 0,
    "last_wall_time_ns": 0,
    "first_mono_time_ns": 0,
    "last_mono_time_ns": 0,
})

WIRE_UPLOAD_LOG_HEADERS = [
    "timestamp",
    "experiment_id",
    "client_id",
    "round",
    "wire_upload_start_ts",
    "wire_upload_end_ts",
    "wire_upload_duration_s",
    "wire_upload_bytes",
    "wire_upload_packets",
    "mean_iat_s",
    "max_iat_s",
    "close_reason",
    "attack_id",
    "first_wall_time_ns",
    "last_wall_time_ns",
    "first_mono_time_ns",
    "last_mono_time_ns",
]

CSV_HEADERS = [
    "timestamp", "wall_time_ns", "mono_time_ns", "experiment_id", "src_ip", "client_id",
    "payload_bytes", "direction", "iat", "dir_ratio", "burst_density",
    "inbound_bytes", "outbound_bytes", "inbound_count", "outbound_count", "inbound_share", "outbound_share", "raw_state_est",
    "state_est", "state_confidence", "cycle_stage", "inferred_round_id", "completed_cycle_id",
    "live_direction_label", "live_phase_label", "live_phase_confidence", "adaptive_phase_label",
    "adaptive_phase_score_idle", "adaptive_phase_score_download", "adaptive_phase_score_training",
    "adaptive_phase_score_upload",
]

PHASE_LOG_HEADERS = [
    "timestamp",
    "client_id",
    "round",
    "phase",
    "src_ip",
    "dst_ip",
    "server_host",
    "upload_success",
    "phase_start",
    "phase_end",
    "phase_duration_s",
]

ROUND_LOG_HEADERS = [
    "timestamp",
    "client_id",
    "round",
    "round_start",
    "round_end",
    "round_duration_s",
]

DECISION_LOG_HEADERS = [
    "timestamp",
    "client_id",
    "selected_target_client",
    "round",
    "stable_state",
    "stable_phase",
    "hmm_confidence",
    "decision_phase",
    "decision_confidence",
    "direction",
    "payload_bytes",
    "dir_ratio",
    "burst_density",
    "inbound_bytes",
    "outbound_bytes",
    "inbound_count",
    "outbound_count",
    "inbound_share",
    "outbound_share",
    "iat_s",
    "is_selected_target",
    "startup_grace_active",
    "cooldown_active",
    "phase_upload_confirmed",
    "packet_upload_support",
    "upload_candidate",
    "upload_confirmed",
    "attackable_upload",
    "upload_score",
    "packet_support_score",
    "phase_agreement_score",
    "direction_persistence_score",
    "round_context_score",
    "action",
    "reason",
    "packet_ts",
    "packet_wall_time_ns",
    "packet_mono_time_ns",
    "analyzer_cpu_percent",
    "analyzer_rss_mb",
    "decision_lag_ms",
    "trigger_publish_wall_time_ns",
    "trigger_publish_mono_time_ns",
]


_SHUTTING_DOWN = False

def cleanup_analyzer(reason="shutdown"):
    global _SHUTTING_DOWN

    if _SHUTTING_DOWN:
        return

    _SHUTTING_DOWN = True

    print(f"\n[CLEANUP] Analyzer cleanup started. reason={reason}")

    # Finalize logs before clearing runtime/socket state.  This is important
    # because SIGINT/SIGTERM are handled by handle_analyzer_shutdown(), which
    # calls cleanup_analyzer() directly and therefore may bypass the
    # KeyboardInterrupt block at the bottom of the file.
    for finalizer_name, finalizer_args in (
        ("finalize_terminal_upload_rounds", {"reason": reason}),
        ("finalize_open_wire_upload_logs", {}),
        ("finalize_open_phase_logs", {}),
        ("finalize_open_round_logs", {}),
    ):
        finalizer = globals().get(finalizer_name)
        if callable(finalizer):
            try:
                finalizer(**finalizer_args)
            except Exception as e:
                print(f"[CLEANUP] {finalizer_name} failed: {e}", flush=True)

    try:
        # Clear local attack related dictionaries if they exist
        for name in [
            "pending_attacks",
            "active_attacks",
            "attack_context",
            "last_attack_by_client",
            "client_attack_state",
        ]:
            obj = globals().get(name)
            if isinstance(obj, dict):
                obj.clear()
                print(f"[CLEANUP] Cleared analyzer state: {name}")
    except Exception as e:
        print(f"[CLEANUP] Analyzer local state cleanup error: {e}")

    try:
        # Clear Redis attack related keys only, not the whole Redis database
        r = globals().get("redis_client") or globals().get("r")
        if r is not None:
            patterns = [
                "attack:*",
                "pending_attack:*",
                "active_attack:*",
                "client_attack:*",
                "fl_attack:*",
            ]

            deleted = 0
            for pattern in patterns:
                try:
                    keys = list(r.scan_iter(pattern))
                    if keys:
                        deleted += r.delete(*keys)
                except Exception as e:
                    print(f"[CLEANUP] Redis pattern cleanup failed for {pattern}: {e}")

            print(f"[CLEANUP] Redis attack keys deleted: {deleted}")
    except Exception as e:
        print(f"[CLEANUP] Redis cleanup error: {e}")

    try:
        # Close UDP sockets so ports are released cleanly on Ctrl+C/restart.
        recv_sock = globals().get("sock")
        if recv_sock is not None:
            try:
                recv_sock.close()
                print("[CLEANUP] Analyzer receive socket closed")
            finally:
                globals()["sock"] = None

        for sock_name in ("attack_sock", "outcome_sock", "poison_sock"):
            udp_sock = globals().get(sock_name)
            if udp_sock is not None:
                try:
                    udp_sock.close()
                    print(f"[CLEANUP] Analyzer {sock_name} closed")
                except Exception:
                    pass
    except Exception as e:
        print(f"[CLEANUP] Socket cleanup error: {e}")

    print("[CLEANUP] Analyzer cleanup completed")
    
def handle_analyzer_shutdown(signum, frame):
    cleanup_analyzer(reason=f"signal_{signum}")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_analyzer_shutdown)
signal.signal(signal.SIGTERM, handle_analyzer_shutdown)
atexit.register(cleanup_analyzer)


@dataclass
class PacketRecord:
    ts: float
    src_ip: str
    dst_ip: str
    payload: int
    wire: int = 0
    iat: float = 0.0
    client_id: str = ""
    direction: int = 0


@dataclass
class TransitionDecision:
    allowed: bool
    from_state: int
    to_state: int
    source: str
    reason: str


class DirectionInferer:
    def __init__(self, window_seconds: float = 1.0, min_packets: int = 8, dominance_ratio: float = 2.0,
                 low_iat_threshold: float = 0.002, role_hold_seconds: float = 2.0, min_payload: int = 200):
        self.window_seconds = window_seconds
        self.min_packets = min_packets
        self.dominance_ratio = dominance_ratio
        self.low_iat_threshold = low_iat_threshold
        self.role_hold_seconds = role_hold_seconds
        self.min_payload = min_payload
        self.window = deque()
        self.current_sender = None
        self.current_receiver = None
        self.last_role_update_ts = None

    def _evict_old(self, now: float) -> None:
        while self.window and (now - self.window[0].ts) > self.window_seconds:
            self.window.popleft()

    def _compute_stats(self):
        pair_dir_bytes = defaultdict(int)
        pair_dir_pkts = defaultdict(int)
        pair_iats = defaultdict(list)
        prev_ts_by_dir = {}
        for pkt in self.window:
            if pkt.payload < self.min_payload:
                continue
            key = (pkt.src_ip, pkt.dst_ip)
            pair_dir_bytes[key] += pkt.payload
            pair_dir_pkts[key] += 1
            if key in prev_ts_by_dir:
                local_iat = pkt.ts - prev_ts_by_dir[key]
                if local_iat >= 0:
                    pair_iats[key].append(local_iat)
            prev_ts_by_dir[key] = pkt.ts
        return pair_dir_bytes, pair_dir_pkts, pair_iats

    def _infer_roles(self, now: float):
        pair_dir_bytes, pair_dir_pkts, pair_iats = self._compute_stats()
        if not pair_dir_bytes:
            if self.last_role_update_ts is not None and (now - self.last_role_update_ts) <= self.role_hold_seconds:
                return {
                    "sender": self.current_sender,
                    "receiver": self.current_receiver,
                    "byte_ratio": 0.0,
                    "median_iat": 999.0,
                    "confidence": 0.0,
                }
            self.current_sender = None
            self.current_receiver = None
            return {
                "sender": None,
                "receiver": None,
                "byte_ratio": 0.0,
                "median_iat": 999.0,
                "confidence": 0.0,
            }

        total_bytes_by_ip = defaultdict(int)
        total_pkts_by_ip = defaultdict(int)
        iats_by_ip = defaultdict(list)
        for (src, dst), byte_count in pair_dir_bytes.items():
            pkt_count = pair_dir_pkts[(src, dst)]
            total_bytes_by_ip[src] += byte_count
            total_pkts_by_ip[src] += pkt_count
            iats_by_ip[src].extend(pair_iats.get((src, dst), []))

        ranked = sorted(total_bytes_by_ip.items(), key=lambda x: x[1], reverse=True)
        if len(ranked) < 2:
            return {
                "sender": self.current_sender,
                "receiver": self.current_receiver,
                "byte_ratio": 0.0,
                "median_iat": 999.0,
                "confidence": 0.0,
            }

        sender, sender_bytes = ranked[0]
        receiver, receiver_bytes = ranked[1]
        sender_pkts = total_pkts_by_ip[sender]
        sender_iats = iats_by_ip.get(sender, [])
        sender_med_iat = median(sender_iats) if sender_iats else 999.0
        ratio = (sender_bytes + 1) / (receiver_bytes + 1)

        if sender_pkts >= self.min_packets and ratio >= self.dominance_ratio:
            self.current_sender = sender
            self.current_receiver = receiver
            self.last_role_update_ts = now
            continuity = 1.0 if sender_med_iat <= self.low_iat_threshold else 0.5
            confidence = min(1.0, (ratio / self.dominance_ratio) * continuity)
            return {
                "sender": sender,
                "receiver": receiver,
                "byte_ratio": ratio,
                "median_iat": sender_med_iat,
                "confidence": confidence,
            }

        return {
            "sender": self.current_sender,
            "receiver": self.current_receiver,
            "byte_ratio": ratio,
            "median_iat": sender_med_iat,
            "confidence": 0.25 if self.current_sender else 0.0,
        }

    def update_and_classify(self, pkt: PacketRecord):
        self.window.append(pkt)
        self._evict_old(pkt.ts)
        info = self._infer_roles(pkt.ts)
        if pkt.payload < self.min_payload:
            return "other", info
        if self.current_sender is None or self.current_receiver is None:
            return "unknown", info
        if pkt.src_ip == self.current_sender and pkt.dst_ip == self.current_receiver:
            return "inbound", info
        if pkt.src_ip == self.current_receiver and pkt.dst_ip == self.current_sender:
            return "outbound", info
        return "other", info


def map_direction_to_live_label(direction: int) -> str:
    if direction == -1:
        return "inbound"
    if direction == 1:
        return "outbound"
    return "unknown"


def infer_phase_from_direction(direction_value: int, payload: int, iat: float,
                               confidence_threshold: float = PHASE_CONFIDENCE_THRESHOLD,
                               gap_threshold: float = PHASE_GAP_THRESHOLD,
                               min_payload: int = PHASE_MIN_PAYLOAD) -> Tuple[str, float]:
    if payload < min_payload:
        if payload <= LIVE_IDLE_PAYLOAD_MAX and iat >= LIVE_IDLE_IAT_MIN:
            return PHASE_IDLE, 0.80
        return PHASE_IDLE, 0.20
    if direction_value == -1:
        if iat <= LIVE_TRANSFER_FAST_IAT:
            return PHASE_DOWNLOAD, 0.95
        if iat <= LIVE_TRANSFER_MODERATE_IAT:
            return PHASE_DOWNLOAD, 0.80
        return PHASE_DOWNLOAD, 0.55
    if direction_value == 1:
        if iat <= LIVE_TRANSFER_FAST_IAT:
            return PHASE_UPLOAD, 0.95
        if iat <= LIVE_TRANSFER_MODERATE_IAT:
            return PHASE_UPLOAD, 0.80
        return PHASE_UPLOAD, 0.55
    if iat >= gap_threshold:
        return PHASE_IDLE, 0.60
    return PHASE_IDLE, 0.20


class LivePhaseTracker:
    def __init__(self, confidence_threshold: float = PHASE_CONFIDENCE_THRESHOLD,
                 gap_threshold: float = PHASE_GAP_THRESHOLD, min_payload: int = PHASE_MIN_PAYLOAD,
                 min_phase_duration_packets: int = PHASE_MIN_STREAK):
        self.inferers: Dict[Tuple[str, str], DirectionInferer] = {}
        self.confidence_threshold = confidence_threshold
        self.gap_threshold = gap_threshold
        self.min_payload = min_payload
        self.min_phase_duration_packets = min_phase_duration_packets
        self.last_phase_by_client: Dict[str, str] = {}
        self.phase_count_by_client: Dict[str, int] = defaultdict(int)

    def _pair_key(self, src_ip: str, dst_ip: str) -> Tuple[str, str]:
        return tuple(sorted((src_ip, dst_ip)))

    def process_packet(self, pkt: PacketRecord) -> Optional[dict]:
        key = self._pair_key(pkt.src_ip, pkt.dst_ip)
        if key not in self.inferers:
            self.inferers[key] = DirectionInferer(min_payload=self.min_payload)
        inferer = self.inferers[key]
        _, role_info = inferer.update_and_classify(pkt)
        direction_label = map_direction_to_live_label(pkt.direction)
        phase, confidence = infer_phase_from_direction(
            pkt.direction, pkt.payload, pkt.iat,
            self.confidence_threshold, self.gap_threshold, self.min_payload
        )
        client_id = pkt.client_id or pkt.src_ip
        last_phase = self.last_phase_by_client.get(client_id)
        if phase == last_phase:
            self.phase_count_by_client[client_id] += 1
        else:
            self.last_phase_by_client[client_id] = phase
            self.phase_count_by_client[client_id] = 1
        confirmed = self.phase_count_by_client[client_id] >= self.min_phase_duration_packets
        return {
            "client_id": client_id,
            "direction_label": direction_label,
            "phase": phase,
            "confidence": float(confidence),
            "confirmed": bool(confirmed),
            "sender": None if role_info is None else role_info.get("sender"),
            "receiver": None if role_info is None else role_info.get("receiver"),
            "byte_ratio": 0.0 if role_info is None else float(role_info.get("byte_ratio", 0.0)),
            "median_iat": 999.0 if role_info is None else float(role_info.get("median_iat", 999.0)),
        }


class AdaptiveTrafficClassifier:
    def __init__(self):
        self.runtime = defaultdict(lambda: {
            "recent_dirs": deque(maxlen=ADAPTIVE_RULE_WINDOW_LONG),
            "recent_sizes": deque(maxlen=ADAPTIVE_RULE_WINDOW_LONG),
            "recent_iats": deque(maxlen=ADAPTIVE_RULE_WINDOW_LONG),
            "recent_density": deque(maxlen=ADAPTIVE_RULE_WINDOW_LONG),
            "recent_labels": deque(maxlen=10),
        })

    def update(self, client_id: str, direction: int, payload_bytes: int, iat: float, burst_density: int):
        rt = self.runtime[client_id]
        prev_state = client_runtime[client_id]["stable_state"]
        phase_driving_direction = int(direction)
        phase_driving_payload = float(payload_bytes)
        phase_driving_iat = float(max(iat, 0.0))
        phase_driving_density = float(max(burst_density, 0.0))
        if payload_bytes < PHASE_DRIVING_MIN_PAYLOAD and prev_state in (UPLOAD, DOWNLOAD):
            phase_driving_direction = 0
            phase_driving_density = 0.0
        rt["recent_dirs"].append(phase_driving_direction)
        rt["recent_sizes"].append(phase_driving_payload)
        rt["recent_iats"].append(phase_driving_iat)
        rt["recent_density"].append(phase_driving_density)
        features = self._extract_features(client_id)
        phase, scores = self._classify(features)
        rt["recent_labels"].append(phase)
        return phase, features, scores

    def _extract_features(self, client_id: str):
        rt = self.runtime[client_id]
        dirs = list(rt["recent_dirs"])[-ADAPTIVE_RULE_WINDOW_SHORT:]
        sizes = list(rt["recent_sizes"])[-ADAPTIVE_RULE_WINDOW_SHORT:]
        iats = list(rt["recent_iats"])[-ADAPTIVE_RULE_WINDOW_SHORT:]
        dens = list(rt["recent_density"])[-ADAPTIVE_RULE_WINDOW_SHORT:]
        all_sizes = list(rt["recent_sizes"])
        all_iats = list(rt["recent_iats"])
        all_dens = list(rt["recent_density"])
        inbound_frac = sum(1 for d in dirs if d == -1) / max(len(dirs), 1)
        outbound_frac = sum(1 for d in dirs if d == 1) / max(len(dirs), 1)
        neutral_frac = sum(1 for d in dirs if d not in (-1, 1)) / max(len(dirs), 1)
        direction_balance = inbound_frac - outbound_frac
        large_pkt_thr = percentile_or_fallback(all_sizes, 75, 1000.0)
        very_large_pkt_thr = percentile_or_fallback(all_sizes, 90, 1200.0)
        fast_iat_thr = percentile_or_fallback(all_iats, 25, 0.003)
        slow_iat_thr = percentile_or_fallback(all_iats, 75, 0.010)
        dense_thr = percentile_or_fallback(all_dens, 75, 20.0)
        very_dense_thr = percentile_or_fallback(all_dens, 90, 40.0)
        mean_pkt = safe_mean(sizes, 0.0)
        mean_iat = safe_mean(iats, 0.0)
        mean_density = safe_mean(dens, 0.0)
        large_pkt_frac = sum(1 for s in sizes if s >= large_pkt_thr) / max(len(sizes), 1)
        very_large_pkt_frac = sum(1 for s in sizes if s >= very_large_pkt_thr) / max(len(sizes), 1)
        inbound_run = 0
        for d in reversed(dirs):
            if d == -1:
                inbound_run += 1
            else:
                break
        outbound_run = 0
        for d in reversed(dirs):
            if d == 1:
                outbound_run += 1
            else:
                break
        pkt_med, pkt_scale = robust_stats(all_sizes)
        iat_med, iat_scale = robust_stats(all_iats)
        den_med, den_scale = robust_stats(all_dens)
        pkt_z = (mean_pkt - pkt_med) / pkt_scale
        iat_z = (mean_iat - iat_med) / iat_scale
        den_z = (mean_density - den_med) / den_scale
        fast_score = 1.0 if mean_iat <= fast_iat_thr else max(0.0, 1.0 - (mean_iat - fast_iat_thr) / max(fast_iat_thr, EPS))
        slow_score = 1.0 if mean_iat >= slow_iat_thr else max(0.0, mean_iat / max(slow_iat_thr, EPS))
        dense_score = 1.0 if mean_density >= dense_thr else max(0.0, mean_density / max(dense_thr, EPS))
        return {
            "client_id": client_id,
            "inbound_frac": inbound_frac,
            "outbound_frac": outbound_frac,
            "neutral_frac": neutral_frac,
            "direction_balance": direction_balance,
            "large_pkt_frac": large_pkt_frac,
            "very_large_pkt_frac": very_large_pkt_frac,
            "mean_pkt": mean_pkt,
            "mean_iat": mean_iat,
            "mean_density": mean_density,
            "inbound_run": inbound_run,
            "outbound_run": outbound_run,
            "pkt_z": pkt_z,
            "iat_z": iat_z,
            "den_z": den_z,
            "fast_score": fast_score,
            "slow_score": slow_score,
            "dense_score": dense_score,
            "large_pkt_thr": large_pkt_thr,
            "very_large_pkt_thr": very_large_pkt_thr,
            "fast_iat_thr": fast_iat_thr,
            "slow_iat_thr": slow_iat_thr,
            "dense_thr": dense_thr,
            "very_dense_thr": very_dense_thr,
            "warm": len(all_sizes) >= ADAPTIVE_RULE_WARMUP_MIN,
        }

    def _classify(self, f: dict):
        prev_state = client_runtime[f["client_id"]]["stable_state"]
        inbound_frac = f["inbound_frac"]
        outbound_frac = f["outbound_frac"]
        direction_balance = f["direction_balance"]
        large_pkt_frac = f["large_pkt_frac"]
        mean_pkt = f["mean_pkt"]
        mean_iat = f["mean_iat"]
        dense_score = f["dense_score"]
        slow_score = f["slow_score"]
        inbound_run = f["inbound_run"]
        outbound_run = f["outbound_run"]
        tiny_pkt_score = 1.0 if mean_pkt <= 128 else max(0.0, 1.0 - ((mean_pkt - 128.0) / 512.0))
        sparse_score = 1.0 - dense_score
        huge_gap_score = 1.0 if mean_iat >= max(5.0 * f["slow_iat_thr"], 0.05) else 0.0
        scores = {
            PHASE_IDLE: 0.0,
            PHASE_DOWNLOAD: 0.0,
            PHASE_TRAINING: 0.0,
            PHASE_UPLOAD: 0.0,
        }

        if prev_state == UPLOAD and inbound_frac >= UPLOAD_TO_DOWNLOAD_MIN_INBOUND_FRAC and \
           large_pkt_frac >= UPLOAD_TO_DOWNLOAD_MIN_LARGE_FRAC and dense_score >= UPLOAD_TO_DOWNLOAD_MIN_DENSE and \
           inbound_run >= UPLOAD_TO_DOWNLOAD_MIN_INBOUND_RUN and mean_pkt >= PHASE_DRIVING_MIN_PAYLOAD:
            scores[PHASE_DOWNLOAD] = 1.25
            return PHASE_DOWNLOAD, scores
        if inbound_frac >= 0.75 and large_pkt_frac >= 0.60 and dense_score >= 0.70 and inbound_run >= 4:
            scores[PHASE_DOWNLOAD] = 1.0
            return PHASE_DOWNLOAD, scores
        if outbound_frac >= 0.75 and large_pkt_frac >= 0.60 and dense_score >= 0.70 and outbound_run >= 4:
            scores[PHASE_UPLOAD] = 1.0
            return PHASE_UPLOAD, scores
        if tiny_pkt_score >= 0.70 and sparse_score >= 0.70 and huge_gap_score >= 1.0:
            scores[PHASE_IDLE] = 1.0
            return PHASE_IDLE, scores

        s_download = 2.5 * inbound_frac + 2.5 * max(direction_balance, 0.0) + 1.2 * large_pkt_frac + 1.0 * dense_score + 0.8 * min(inbound_run / 8.0, 1.0) - 1.8 * max(-direction_balance, 0.0) - 1.2 * sparse_score - 1.2 * huge_gap_score
        s_upload = 2.5 * outbound_frac + 2.5 * max(-direction_balance, 0.0) + 1.2 * large_pkt_frac + 1.0 * dense_score + 0.8 * min(outbound_run / 8.0, 1.0) - 1.8 * max(direction_balance, 0.0) - 1.2 * sparse_score - 1.2 * huge_gap_score
        s_training = 1.8 * slow_score + 1.4 * sparse_score + 1.2 * (1.0 - max(inbound_frac, outbound_frac)) + 0.8 * (1.0 - large_pkt_frac) - 0.8 * tiny_pkt_score - 0.8 * huge_gap_score
        s_idle = 1.8 * sparse_score + 1.6 * huge_gap_score + 1.3 * tiny_pkt_score + 0.8 * slow_score - 0.8 * large_pkt_frac - 0.6 * max(inbound_frac, outbound_frac)
        scores = {
            PHASE_IDLE: float(s_idle),
            PHASE_DOWNLOAD: float(s_download),
            PHASE_TRAINING: float(s_training),
            PHASE_UPLOAD: float(s_upload),
        }
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        best_label, best_score = ranked[0]
        second_score = ranked[1][1]
        margin = best_score - second_score
        if best_label == PHASE_TRAINING or margin < 0.20:
            return PHASE_IDLE, scores
        return best_label, scores


live_phase_tracker = LivePhaseTracker()
adaptive_phase_classifier = AdaptiveTrafficClassifier()


ANALYZER_PROC = psutil.Process(os.getpid()) if psutil is not None else None
if ANALYZER_PROC is not None:
    ANALYZER_PROC.cpu_percent(interval=None)
_ANALYZER_USAGE_LAST_NS = 0
_ANALYZER_USAGE_LAST_CPU = 0.0
_ANALYZER_USAGE_LAST_RSS_MB = 0.0
_ANALYZER_PROC_LAST_CPU_TOTAL_S = None
_ANALYZER_PROC_LAST_WALL_NS = None


def _rss_mb_fallback() -> float:
    try:
        return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
    except Exception:
        return 0.0


def _cpu_percent_fallback(now_ns: int) -> float:
    global _ANALYZER_PROC_LAST_CPU_TOTAL_S, _ANALYZER_PROC_LAST_WALL_NS
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cpu_total_s = float(usage.ru_utime + usage.ru_stime)
        if _ANALYZER_PROC_LAST_CPU_TOTAL_S is None or _ANALYZER_PROC_LAST_WALL_NS is None:
            _ANALYZER_PROC_LAST_CPU_TOTAL_S = cpu_total_s
            _ANALYZER_PROC_LAST_WALL_NS = now_ns
            return 0.0
        wall_delta_s = max((now_ns - _ANALYZER_PROC_LAST_WALL_NS) / 1e9, 1e-9)
        cpu_delta_s = max(cpu_total_s - _ANALYZER_PROC_LAST_CPU_TOTAL_S, 0.0)
        _ANALYZER_PROC_LAST_CPU_TOTAL_S = cpu_total_s
        _ANALYZER_PROC_LAST_WALL_NS = now_ns
        return max(0.0, min(100.0, (cpu_delta_s / wall_delta_s) * 100.0))
    except Exception:
        return 0.0


def sample_analyzer_usage(min_interval_s: float = 0.5) -> Tuple[float, float]:
    global _ANALYZER_USAGE_LAST_NS, _ANALYZER_USAGE_LAST_CPU, _ANALYZER_USAGE_LAST_RSS_MB
    now_ns = time.monotonic_ns()
    if _ANALYZER_USAGE_LAST_NS and (now_ns - _ANALYZER_USAGE_LAST_NS) < int(min_interval_s * 1e9):
        return _ANALYZER_USAGE_LAST_CPU, _ANALYZER_USAGE_LAST_RSS_MB
    try:
        if ANALYZER_PROC is not None:
            _ANALYZER_USAGE_LAST_CPU = float(ANALYZER_PROC.cpu_percent(interval=None))
            _ANALYZER_USAGE_LAST_RSS_MB = float(ANALYZER_PROC.memory_info().rss) / (1024.0 * 1024.0)
        else:
            _ANALYZER_USAGE_LAST_CPU = _cpu_percent_fallback(now_ns)
            _ANALYZER_USAGE_LAST_RSS_MB = _rss_mb_fallback()
    except Exception:
        pass
    _ANALYZER_USAGE_LAST_NS = now_ns
    return _ANALYZER_USAGE_LAST_CPU, _ANALYZER_USAGE_LAST_RSS_MB


def now_wall_ns() -> int:
    return time.time_ns()


def now_mono_ns() -> int:
    return time.monotonic_ns()


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _norm(value: float, max_value: float) -> float:
    """Normalize a nonnegative value to [0, 1] with zero safe denominator handling."""
    try:
        denom = float(max_value)
        if denom <= 0.0:
            return 0.0
        return max(0.0, min(1.0, float(value) / denom))
    except Exception:
        return 0.0


def write_csv_header(path: str, headers: list) -> None:
    with open(path, "w", newline="") as f:
        csv.writer(f).writerow(headers)
        f.flush()

def ensure_output_files() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    write_csv_header(DECISION_LOG_FILE, DECISION_LOG_HEADERS)
    write_csv_header(DATASET_FILE, CSV_HEADERS)
    write_csv_header(LATEST_DATASET_FILE, CSV_HEADERS)
    write_csv_header(PHASE_LOG_FILE, PHASE_LOG_HEADERS)
    write_csv_header(ROUND_LOG_FILE, ROUND_LOG_HEADERS)
    write_csv_header(WIRE_UPLOAD_LOG_FILE, WIRE_UPLOAD_LOG_HEADERS)
    write_csv_header(LATEST_WIRE_UPLOAD_LOG_FILE, WIRE_UPLOAD_LOG_HEADERS)

    with open(EVENT_LOG_FILE, "w", encoding="utf-8"):
        pass

    with open(LATEST_EVENT_LOG_FILE, "w", encoding="utf-8"):
        pass

def write_event(event_type: str, payload: dict) -> None:
    _wns = now_wall_ns()
    record = {
        "event_type": event_type,
        "experiment_id": EXPERIMENT_ID,
        "timestamp": _wns / 1e9,
        "wall_time_ns": _wns,
        "mono_time_ns": now_mono_ns(),
        **payload,
    }
    for path in (EVENT_LOG_FILE, LATEST_EVENT_LOG_FILE):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            f.flush()




def connect_redis() -> redis.Redis:
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    client.ping()
    return client


def is_informative_packet(data: dict) -> bool:
    if bool(data.get("is_ack_only", False)):
        return False
    payload_bytes = int(data.get("payload_bytes", data.get("frame_bytes", data.get("packet_size", 0))))
    if payload_bytes < MIN_VALID_PAYLOAD_BYTES:
        return False
    direction = int(data.get("direction", 0))
    return direction in (-1, 1)


def normalize_packet_fields(data: dict) -> dict:
    ts = float(data.get("timestamp", time.time()))
    src_ip = str(data.get("src_ip", "unknown"))

    client_id_raw = data.get("client_id")
    if client_id_raw is None or str(client_id_raw).strip() == "":
        raise ValueError("Missing client_id from sniffer")
    client_id = str(client_id_raw).strip()

    server_ip_raw = data.get("server_ip")
    server_ip = ""
    if server_ip_raw is not None:
        server_ip = str(server_ip_raw).strip()
        if server_ip and client_id == server_ip:
            raise ValueError(f"Invalid client_id equals server_ip: {client_id}")

    payload_bytes = int(data.get("payload_bytes", data.get("frame_bytes", data.get("packet_size", 0))))
    raw_direction = int(data.get("direction", 0))
    # Keepalive / ACK / control packets carry no meaningful transfer direction.
    # Assigning them inbound (-1) or outbound (1) skews HMM emission scores and
    # direction-ratio features, causing the classifier to see spurious DOWNLOAD
    # or UPLOAD evidence during local training (where all real traffic is control
    # frames). Force direction=0 so these packets contribute to IAT and density
    # statistics but never tip the direction balance.
    direction = 0 if payload_bytes <= KEEPALIVE_MAX_PAYLOAD_BYTES else raw_direction
    flow_key = (client_id, direction)
    prev_ts = packet_clock_by_flow.get(flow_key, ts)
    computed_iat = ts - prev_ts
    packet_clock_by_flow[flow_key] = ts
    iat = float(data.get("iat", computed_iat))
    if iat < 0:
        iat = computed_iat if computed_iat >= 0 else 0.0
    has_source_wall = "wall_time_ns" in data
    has_source_mono = "mono_time_ns" in data
    wall_time_ns = int(data["wall_time_ns"]) if has_source_wall else int(ts * 1e9)
    mono_time_ns = int(data["mono_time_ns"]) if has_source_mono else -1
    timing_source = "sniffer" if has_source_wall and has_source_mono else "fallback"
    dst_ip = str(data.get("dst_ip", "unknown"))
    src_port = int(data.get("src_port", data.get("sport", 0)) or 0)
    dst_port = int(data.get("dst_port", data.get("dport", data.get("server_port", data.get("fl_port", 0))) or 0) or 0)

    if not server_ip:
        if src_ip == client_id and dst_ip and dst_ip != "unknown":
            server_ip = dst_ip
        elif dst_ip == client_id and src_ip and src_ip != "unknown":
            server_ip = src_ip

    server_port = int(data.get("server_port", data.get("fl_port", 0)) or 0)
    if server_port <= 0:
        if direction == 1 and dst_port > 0:
            server_port = dst_port
        elif direction == -1 and src_port > 0:
            server_port = src_port
    if server_port <= 0:
        server_port = DEFAULT_FL_SERVER_PORT

    return {
        "timestamp": ts,
        "wall_time_ns": wall_time_ns,
        "mono_time_ns": mono_time_ns,
        "timing_source": timing_source,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "server_ip": server_ip,
        "server_port": server_port,
        "client_id": client_id,
        "payload_bytes": payload_bytes,
        "wire_bytes": int(data.get("wire_bytes", 0)),
        "direction": direction,
        "iat": iat,
    }


def kalman_filter_iat(client_id: str, measured_iat: float) -> float:
    runtime = client_runtime[client_id]
    z = max(float(measured_iat), 0.0)
    if runtime["kalman_x"] is None:
        runtime["kalman_x"] = z
        runtime["kalman_p"] = KALMAN_P0
        return z
    x_prior = runtime["kalman_x"]
    p_prior = runtime["kalman_p"] + KALMAN_Q
    k_gain = p_prior / (p_prior + KALMAN_R)
    x_post = x_prior + k_gain * (z - x_prior)
    p_post = (1.0 - k_gain) * p_prior
    runtime["kalman_x"] = float(x_post)
    runtime["kalman_p"] = float(max(p_post, EPS))
    return float(x_post)


def compute_features(client_id: str, ts: float, payload_bytes: int, direction: int):
    runtime = client_runtime[client_id]
    runtime["recent_feature_packets"].append((ts, int(direction), int(payload_bytes)))
    runtime["recent_feature_payloads"].append(int(payload_bytes))
    runtime["recent_feature_timestamps"].append(float(ts))

    # Long window used for stable phase scoring.
    while runtime["recent_feature_packets"] and (ts - runtime["recent_feature_packets"][0][0]) > 1.0:
        runtime["recent_feature_packets"].popleft()

    window_packets = list(runtime["recent_feature_packets"])

    # Short window used for model agnostic boundary detection.  This reduces
    # phase residue when small models such as RNNs finish a burst quickly and
    # the 1 second window still contains packets from the previous phase.
    short_window_packets = [
        (t, d, p)
        for (t, d, p) in window_packets
        if (float(ts) - float(t)) <= SHORT_FEATURE_WINDOW_SECONDS
    ]

    inbound_bytes = sum(p for t, d, p in window_packets if d == -1)
    outbound_bytes = sum(p for t, d, p in window_packets if d == 1)
    inbound_count = sum(1 for t, d, p in window_packets if d == -1)
    outbound_count = sum(1 for t, d, p in window_packets if d == 1)

    short_inbound_bytes = sum(p for t, d, p in short_window_packets if d == -1)
    short_outbound_bytes = sum(p for t, d, p in short_window_packets if d == 1)
    short_inbound_count = sum(1 for t, d, p in short_window_packets if d == -1)
    short_outbound_count = sum(1 for t, d, p in short_window_packets if d == 1)

    total_bytes = inbound_bytes + outbound_bytes
    total_count = inbound_count + outbound_count
    total_bytes_safe = max(total_bytes, EPS)
    inbound_share = inbound_bytes / total_bytes_safe
    outbound_share = outbound_bytes / total_bytes_safe

    short_total_bytes = short_inbound_bytes + short_outbound_bytes
    short_total_count = short_inbound_count + short_outbound_count
    short_total_bytes_safe = max(short_total_bytes, EPS)
    short_inbound_share = short_inbound_bytes / short_total_bytes_safe
    short_outbound_share = short_outbound_bytes / short_total_bytes_safe

    raw_dir_ratio = (outbound_bytes + EPS) / (inbound_bytes + EPS)
    dir_ratio = min(max(raw_dir_ratio, 0.0), 100.0)
    short_raw_dir_ratio = (short_outbound_bytes + EPS) / (short_inbound_bytes + EPS)
    short_dir_ratio = min(max(short_raw_dir_ratio, 0.0), 100.0)

    dir_balance = (outbound_bytes - inbound_bytes) / total_bytes_safe
    short_dir_balance = (short_outbound_bytes - short_inbound_bytes) / short_total_bytes_safe
    inbound_density = inbound_count
    outbound_density = outbound_count
    burst_density = total_count
    runtime["recent_inbound_bytes"].append(float(inbound_bytes))
    runtime["recent_outbound_bytes"].append(float(outbound_bytes))
    runtime["recent_inbound_counts"].append(float(inbound_count))
    runtime["recent_outbound_counts"].append(float(outbound_count))
    runtime["recent_dir_balance"].append(float(dir_balance))
    runtime["recent_dir_ratios"].append(float(dir_ratio))
    runtime["recent_inbound_density"].append(float(inbound_density))
    runtime["recent_outbound_density"].append(float(outbound_density))
    return {
        "dir_ratio": float(dir_ratio),
        "dir_balance": float(dir_balance),
        "burst_density": int(burst_density),
        "inbound_density": int(inbound_density),
        "outbound_density": int(outbound_density),
        "inbound_bytes": float(inbound_bytes),
        "outbound_bytes": float(outbound_bytes),
        "inbound_count": int(inbound_count),
        "outbound_count": int(outbound_count),
        "inbound_share": float(inbound_share),
        "outbound_share": float(outbound_share),
        "short_window_s": float(SHORT_FEATURE_WINDOW_SECONDS),
        "short_dir_ratio": float(short_dir_ratio),
        "short_dir_balance": float(short_dir_balance),
        "short_burst_density": int(short_total_count),
        "short_inbound_bytes": float(short_inbound_bytes),
        "short_outbound_bytes": float(short_outbound_bytes),
        "short_inbound_count": int(short_inbound_count),
        "short_outbound_count": int(short_outbound_count),
        "short_inbound_share": float(short_inbound_share),
        "short_outbound_share": float(short_outbound_share),
    }

def robust_center_scale(values):
    arr = np.array(values, dtype=float)
    if len(arr) < 10:
        return 0.0, 1.0
    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med)))
    scale = 1.4826 * mad + EPS
    return med, scale


def robust_z(x, values):
    med, scale = robust_center_scale(values)
    return (float(x) - med) / scale


def robust_stats(values):
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return 0.0, 1.0
    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med)))
    scale = max(1.4826 * mad, EPS)
    return med, scale


def percentile_or_fallback(values, q, fallback):
    arr = np.asarray(list(values), dtype=float)
    if arr.size < ADAPTIVE_RULE_WARMUP_MIN:
        return float(fallback)
    return float(np.percentile(arr, q))


def safe_mean(values, default=0.0):
    arr = list(values)
    return float(default) if not arr else float(np.mean(arr))


def record_download_gap(runtime: dict, ts: float) -> None:
    last_download_like_ts = float(runtime.get("last_download_like_ts", 0.0))
    if last_download_like_ts <= 0.0:
        return

    gap = float(ts) - last_download_like_ts
    if gap > 0.0 and np.isfinite(gap):
        runtime["recent_download_gaps"].append(gap)


def fit_two_log_gap_regimes(gaps) -> Tuple[Optional[float], Optional[float]]:
    arr = np.asarray([float(g) for g in gaps if float(g) > 0.0 and np.isfinite(float(g))], dtype=float)
    if arr.size == 0:
        return None, None

    log_arr = np.log(arr + EPS)
    if log_arr.size == 1:
        only = float(log_arr[0])
        return only, only

    c1 = float(np.percentile(log_arr, 25))
    c2 = float(np.percentile(log_arr, 75))
    if c1 == c2:
        c1 = float(np.min(log_arr))
        c2 = float(np.max(log_arr))

    for _ in range(DOWNLOAD_GAP_CLUSTER_ITERS):
        d1 = np.abs(log_arr - c1)
        d2 = np.abs(log_arr - c2)
        mask = d1 <= d2

        if np.any(mask):
            c1 = float(np.mean(log_arr[mask]))
        if np.any(~mask):
            c2 = float(np.mean(log_arr[~mask]))

    small = min(c1, c2)
    large = max(c1, c2)
    return small, large


def is_download_gap_sufficient(runtime: dict, current_gap: float) -> Tuple[bool, dict]:
    samples = [
        float(g)
        for g in runtime.get("recent_download_gaps", [])
        if float(g) > 0.0 and np.isfinite(float(g))
    ]

    if current_gap <= 0.0 or not np.isfinite(current_gap):
        return False, {
            "gap_mode": "invalid",
            "sample_count": len(samples),
            "current_gap": float(current_gap),
        }

    if not samples:
        return False, {
            "gap_mode": "no_history",
            "sample_count": 0,
            "current_gap": float(current_gap),
        }

    if len(samples) < 4:
        decision = float(current_gap) > float(max(samples))
        return decision, {
            "gap_mode": "max_compare",
            "sample_count": len(samples),
            "current_gap": float(current_gap),
            "reference_gap": float(max(samples)),
        }

    small_center, large_center = fit_two_log_gap_regimes(samples)
    if small_center is None or large_center is None:
        return False, {
            "gap_mode": "fit_failed",
            "sample_count": len(samples),
            "current_gap": float(current_gap),
        }

    current_log_gap = float(np.log(float(current_gap) + EPS))

    if abs(large_center - small_center) < EPS:
        decision = float(current_gap) > float(max(samples))
        return decision, {
            "gap_mode": "collapsed_fit",
            "sample_count": len(samples),
            "current_gap": float(current_gap),
            "reference_gap": float(max(samples)),
            "small_center_log": float(small_center),
            "large_center_log": float(large_center),
        }

    midpoint = 0.5 * (small_center + large_center)
    dist_small = abs(current_log_gap - small_center)
    dist_large = abs(current_log_gap - large_center)
    decision = bool(dist_large < dist_small or current_log_gap >= midpoint)

    return decision, {
        "gap_mode": "clustered",
        "sample_count": len(samples),
        "current_gap": float(current_gap),
        "current_log_gap": float(current_log_gap),
        "small_center_log": float(small_center),
        "large_center_log": float(large_center),
        "midpoint_log": float(midpoint),
        "dist_small": float(dist_small),
        "dist_large": float(dist_large),
    }


def softmax(scores, temperature=1.0):
    x = np.array(scores, dtype=float) / max(float(temperature), EPS)
    x = x - np.max(x)
    ex = np.exp(x)
    return ex / np.sum(ex)


def adaptive_emission(client_id: str, direction: int, feature_bundle: dict, iat: float, packet_size: int):
    runtime = client_runtime[client_id]
    prev_state = runtime["stable_state"]
    dir_ratio = float(feature_bundle["dir_ratio"])
    dir_balance = float(feature_bundle["dir_balance"])
    burst_density = int(feature_bundle["burst_density"])
    inbound_density = int(feature_bundle["inbound_density"])
    outbound_density = int(feature_bundle["outbound_density"])
    runtime["recent_dir_ratios"].append(dir_ratio)
    runtime["recent_densities"].append(float(burst_density))
    runtime["recent_iats"].append(float(iat))
    runtime["recent_packet_sizes"].append(float(packet_size))
    zr = robust_z(dir_ratio, runtime["recent_dir_ratios"])
    zb = robust_z(dir_balance, runtime["recent_dir_balance"])
    zd = robust_z(burst_density, runtime["recent_densities"])
    zi = robust_z(iat, runtime["recent_iats"])
    zq = robust_z(packet_size, runtime["recent_packet_sizes"])
    zin = robust_z(inbound_density, runtime["recent_inbound_density"])
    zout = robust_z(outbound_density, runtime["recent_outbound_density"])
    # uplink_frac/downlink_frac previously counted the last 12 *packets*
    # (recent_directions has no byte size), so a client whose upload arrives
    # as fewer, larger packets showed an artificially low uplink_frac even
    # while transferring the same or more data -- the same packet-count bias
    # already fixed in the upload-confirmation scoring (see
    # _compute_packet_support_score / _compute_direction_persistence_score).
    # feature_bundle["outbound_share"]/["inbound_share"] are already computed
    # from bytes over the same window (compute_features) and were sitting
    # unused right here; use them instead of recent_directions.
    uplink_frac = float(feature_bundle.get("outbound_share", 0.0))
    downlink_frac = float(feature_bundle.get("inbound_share", 0.0))
    recent_iat_window = list(runtime["recent_iats"])[-12:]
    recent_size_window = list(runtime["recent_packet_sizes"])[-12:]
    mean_iat = float(np.mean(recent_iat_window)) if recent_iat_window else 0.0
    mean_size = float(np.mean(recent_size_window)) if recent_size_window else 0.0
    zi_mean = robust_z(mean_iat, runtime["recent_iats"])
    zq_mean = robust_z(mean_size, runtime["recent_packet_sizes"])
    down_balance = max(-dir_balance, 0.0)
    up_balance = max(dir_balance, 0.0)
    dense_inbound_bonus = max(zin, 0.0) + max(-zout, 0.0)
    dense_outbound_bonus = max(zout, 0.0) + max(-zin, 0.0)
    s_idle = -0.45 * abs(zr) - 0.60 * abs(zb) - 0.45 * abs(zd) - 0.25 * abs(zq) - 0.20 * abs(zi) + 0.10 * (1.0 if burst_density <= 2 else 0.0)
    s_download = 1.70 * downlink_frac + 1.80 * down_balance + 0.90 * max(-zb, 0.0) + 0.60 * dense_inbound_bonus + 0.35 * max(zq_mean, 0.0) - 0.20 * max(zi_mean, 0.0) - 0.25 * up_balance
    s_train = 0.50 * max(zi_mean, 0.0) + 0.60 * (1.0 - min(abs(dir_balance), 1.0)) + 0.40 * (1.0 - max(uplink_frac, downlink_frac)) - 0.55 * max(zq_mean, 0.0) - 0.60 * max(zd, 0.0) - 0.35 * max(abs(zb), 0.0)
    s_upload = 1.90 * uplink_frac + 2.00 * up_balance + 1.00 * max(zb, 0.0) + 0.75 * dense_outbound_bonus + 0.45 * max(zq_mean, 0.0) - 0.15 * max(zi_mean, 0.0) - 0.30 * down_balance + 0.15 * (1.0 if packet_size >= 1200 else 0.0)

    inbound_bytes = float(feature_bundle["inbound_bytes"])
    outbound_bytes = float(feature_bundle["outbound_bytes"])
    inbound_byte_share = inbound_bytes / max(inbound_bytes + outbound_bytes, EPS)
    inbound_dominant = (
        downlink_frac >= 0.75
        and down_balance >= 0.50
        and inbound_byte_share >= 0.85
    )

    if inbound_dominant:
        s_download += 1.00
        s_train -= 1.00

    if prev_state == UPLOAD and downlink_frac >= 0.50 and mean_size >= PHASE_DRIVING_MIN_PAYLOAD and burst_density >= 2:
        s_download += 1.50
        s_upload -= 0.60
    emissions = softmax([s_idle, s_download, s_train, s_upload], temperature=SOFTMAX_TEMPERATURE)
    emissions = np.clip(emissions, 0.02, 0.94)
    emissions = emissions / np.sum(emissions)
    return emissions


def update_hmm_adaptive(client_id: str, direction: int, feature_bundle: dict, iat: float, packet_size: int):
    runtime = client_runtime[client_id]
    belief = runtime["belief"]
    runtime["recent_directions"].append(int(direction))
    emissions = adaptive_emission(client_id, direction, feature_bundle, iat, packet_size)
    belief[:] = np.dot(belief, A) * emissions
    total = np.sum(belief)
    belief[:] = belief / total if total > 0 else INITIAL_BELIEF.copy()
    state = int(np.argmax(belief))
    confidence = float(np.max(belief))
    runtime["recent_states"].append(state)
    if direction == 1:
        runtime["recent_uplink_sizes"].append(packet_size)
    return state, confidence, emissions


def get_adaptive_upload_thresholds(client_id: str):
    """Return (duration_threshold_s, bytes_threshold) for this client.

    Bootstrap phase (fewer than ADAPTIVE_UPLOAD_MIN_HISTORY episodes):
        Use the permissive floor constants so the first few real upload
        episodes always pass and seed the history regardless of model size.

    Steady state (history available):
        Derive thresholds entirely from observed history using a fraction of
        the median.  No hardcoded byte floor is applied — the threshold is
        model-agnostic and adapts automatically to whatever byte volume this
        client actually produces (LSTM at ~50 KB, ResNet at ~100 MB, etc.).
        ADAPTIVE_BYTES_MIN_FRACTION and ADAPTIVE_DURATION_MIN_FRACTION act
        as relative floors, preventing a single large episode from raising
        the bar so high that subsequent normal episodes are rejected.
    """
    runtime = client_runtime[client_id]
    duration_hist = list(runtime["upload_duration_history"])
    bytes_hist = list(runtime["upload_bytes_history"])

    if len(duration_hist) < ADAPTIVE_UPLOAD_MIN_HISTORY:
        # Bootstrap: permissive floors only, no history yet.
        return UPLOAD_DURATION_FLOOR_SECONDS, UPLOAD_BYTES_FLOOR

    median_duration = float(np.median(duration_hist))
    median_bytes    = float(np.median(bytes_hist))

    # Target: ALPHA fraction of the median, so the threshold tracks the
    # observed volume rather than being anchored to any absolute value.
    target_duration = ADAPTIVE_DURATION_ALPHA * median_duration
    target_bytes    = ADAPTIVE_BYTES_ALPHA    * median_bytes

    # Relative floor: never drop below MIN_FRACTION of the median, so a
    # brief burst of very short episodes cannot collapse the threshold to zero.
    floor_duration = ADAPTIVE_DURATION_MIN_FRACTION * median_duration
    floor_bytes    = ADAPTIVE_BYTES_MIN_FRACTION    * median_bytes

    duration_thr = max(floor_duration, target_duration, UPLOAD_DURATION_FLOOR_SECONDS)
    bytes_thr    = int(max(floor_bytes, target_bytes, float(UPLOAD_BYTES_FLOOR)))

    return duration_thr, bytes_thr



def _finite_positive_values(values) -> list:
    clean = []
    for value in values:
        try:
            x = float(value)
        except Exception:
            continue
        if x > 0.0 and np.isfinite(x):
            clean.append(x)
    return clean


def get_dynamic_upload_history_profile(client_id: str) -> dict:
    """Return per-client upload medians used by the dynamic completion gate."""
    runtime = client_runtime[client_id]
    duration_hist = _finite_positive_values(runtime.get("upload_duration_history", []))
    bytes_hist = _finite_positive_values(runtime.get("upload_bytes_history", []))
    packet_hist = _finite_positive_values(runtime.get("upload_packet_history", []))

    history_count = min(len(bytes_hist), len(packet_hist)) if packet_hist else len(bytes_hist)

    return {
        "history_count": int(history_count),
        "median_duration_s": float(np.median(duration_hist)) if duration_hist else 0.0,
        "median_bytes": float(np.median(bytes_hist)) if bytes_hist else 0.0,
        "median_packets": float(np.median(packet_hist)) if packet_hist else 0.0,
    }


def evaluate_upload_completion_evidence(client_id: str, upload_duration_s: float,
                                        upload_bytes: int, upload_packets: int) -> dict:
    """Dynamic upload validity gate for round completion.

    The gate is intentionally based mainly on per-client byte and packet ratios.
    Duration is logged for diagnostics but is not a mandatory condition because
    attack changes upload time: attacked uploads can be slow and fragmented,
    while clean uploads can be short and compact.
    """
    profile = get_dynamic_upload_history_profile(client_id)
    history_count = int(profile.get("history_count", 0))
    median_bytes = float(profile.get("median_bytes", 0.0) or 0.0)
    median_packets = float(profile.get("median_packets", 0.0) or 0.0)
    median_duration_s = float(profile.get("median_duration_s", 0.0) or 0.0)

    upload_duration_s = max(float(upload_duration_s), 0.0)
    upload_bytes = max(int(upload_bytes), 0)
    upload_packets = max(int(upload_packets), 0)

    if history_count < ADAPTIVE_UPLOAD_MIN_HISTORY or median_bytes <= 0.0 or median_packets <= 0.0:
        bootstrap_valid = (
            upload_packets >= MIN_UPLOAD_COMPLETION_PACKETS
            and upload_bytes >= UPLOAD_BYTES_FLOOR
        )
        return {
            "valid": bool(bootstrap_valid),
            "gate_mode": "bootstrap_dynamic_upload_gate",
            "history_count": int(history_count),
            "upload_duration_s": float(upload_duration_s),
            "upload_bytes": int(upload_bytes),
            "upload_packets": int(upload_packets),
            "median_duration_s": float(median_duration_s),
            "median_bytes": float(median_bytes),
            "median_packets": float(median_packets),
            "byte_ratio": 0.0,
            "packet_ratio": 0.0,
            "duration_ratio": 0.0,
            "byte_ratio_threshold": 0.0,
            "packet_ratio_threshold": 0.0,
            "bootstrap_packet_threshold": int(MIN_UPLOAD_COMPLETION_PACKETS),
            "bootstrap_bytes_floor": int(UPLOAD_BYTES_FLOOR),
            "enough_packets_met": bool(upload_packets >= MIN_UPLOAD_COMPLETION_PACKETS),
            "enough_bytes_met": bool(upload_bytes >= UPLOAD_BYTES_FLOOR),
        }

    byte_ratio = float(upload_bytes) / max(float(median_bytes), 1.0)
    packet_ratio = float(upload_packets) / max(float(median_packets), 1.0)
    duration_ratio = float(upload_duration_s) / max(float(median_duration_s), EPS)

    attack_context = bool(client_runtime[client_id].get("active_attack_id", ""))

    # Dynamic acceptance thresholds are ratios against the client's own history.
    # Duration is deliberately diagnostic only.  In attacked runs, duration can
    # expand sharply, while in clean runs the same upload can be compact.  The
    # completion decision therefore uses byte and packet evidence, with an
    # additional high-packet-volume path for substantial fragmented uploads.
    byte_ratio_threshold = 0.45 if attack_context else 0.50
    packet_ratio_threshold = 0.30

    enough_packet_ratio = packet_ratio >= packet_ratio_threshold
    enough_byte_ratio = byte_ratio >= byte_ratio_threshold

    # Normal dynamic path: the upload has enough packet volume and enough bytes
    # relative to the client's own median history.
    normal_ratio_gate = enough_packet_ratio and enough_byte_ratio

    # Strong-history path: useful when both byte and packet ratios are clearly
    # substantial, even if one of the basic thresholds is marginal.
    strong_packet_and_substantial_bytes = (
        packet_ratio >= 0.50
        and byte_ratio >= 0.40
    )

    # High-packet-volume fragmented path: this is the important correction for
    # attacked uploads such as 43-63 packets and 60-90 KB.  Those episodes are
    # too large to be treated like tiny fragments, even when byte_ratio is below
    # the normal byte threshold.  The absolute packet floor prevents 3-5 packet
    # fragments from passing merely because a client's historical packet median
    # is small.
    high_packet_volume_substantial_bytes = (
        upload_packets >= 40
        and packet_ratio >= 0.25
        and byte_ratio >= 0.25
    )

    # Compact but byte-heavy path: protects cases such as 34 packets with more
    # than half of the expected byte volume.  This keeps the gate dynamic while
    # accepting real uploads that are short in time but substantial in volume.
    compact_byte_heavy_upload = (
        upload_packets >= 30
        and packet_ratio >= 0.25
        and byte_ratio >= 0.50
    )

    valid = bool(
        upload_packets >= MIN_UPLOAD_COMPLETION_PACKETS
        and (
            normal_ratio_gate
            or strong_packet_and_substantial_bytes
            or high_packet_volume_substantial_bytes
            or compact_byte_heavy_upload
        )
    )

    return {
        "valid": bool(valid),
        "gate_mode": "dynamic_ratio_upload_gate",
        "attack_context": bool(attack_context),
        "history_count": int(history_count),
        "upload_duration_s": float(upload_duration_s),
        "upload_bytes": int(upload_bytes),
        "upload_packets": int(upload_packets),
        "median_duration_s": float(median_duration_s),
        "median_bytes": float(median_bytes),
        "median_packets": float(median_packets),
        "byte_ratio": float(byte_ratio),
        "packet_ratio": float(packet_ratio),
        "duration_ratio": float(duration_ratio),
        "byte_ratio_threshold": float(byte_ratio_threshold),
        "packet_ratio_threshold": float(packet_ratio_threshold),
        "minimum_packet_floor": int(MIN_UPLOAD_COMPLETION_PACKETS),
        "enough_packet_ratio_met": bool(enough_packet_ratio),
        "enough_byte_ratio_met": bool(enough_byte_ratio),
        "normal_ratio_gate_met": bool(normal_ratio_gate),
        "strong_packet_and_substantial_bytes_met": bool(strong_packet_and_substantial_bytes),
        "high_packet_volume_substantial_bytes_met": bool(high_packet_volume_substantial_bytes),
        "compact_byte_heavy_upload_met": bool(compact_byte_heavy_upload),
    }


def get_open_upload_completion_evidence(client_id: str, ts: float) -> dict:
    """Return whether the currently open upload is strong enough to complete a round."""
    runtime = client_runtime[client_id]
    wire_state = wire_upload_state.get(client_id, {})

    start_candidates = [
        float(runtime.get("upload_episode_start_ts", 0.0) or 0.0),
        float(wire_state.get("start_ts", 0.0) or 0.0),
    ]
    start_ts = max(start_candidates)
    duration_s = max(float(ts) - start_ts, 0.0) if start_ts > 0.0 else 0.0

    upload_bytes = max(
        int(runtime.get("current_upload_bytes", 0) or 0),
        int(runtime.get("upload_episode_bytes", 0) or 0),
        int(wire_state.get("bytes", 0) or 0),
    )
    upload_packets = max(
        int(runtime.get("upload_episode_packets", 0) or 0),
        int(wire_state.get("packets", 0) or 0),
    )

    return evaluate_upload_completion_evidence(
        client_id=client_id,
        upload_duration_s=duration_s,
        upload_bytes=upload_bytes,
        upload_packets=upload_packets,
    )

def state_to_phase_label(state: int) -> str:
    if state == DOWNLOAD:
        return PHASE_DOWNLOAD
    if state == TRAINING:
        return PHASE_TRAINING
    if state == UPLOAD:
        return PHASE_UPLOAD
    return PHASE_IDLE


def get_filtered_recent_median_iat(client_id: str, fallback: float = 0.01) -> float:
    """Return a robust recent per client IAT estimate for transition gating.

    Long gaps are excluded so attack delay, idle silence, and shutdown gaps do
    not inflate the gate.  The value is used only as a sanity check for
    TRAINING -> UPLOAD, not as upload completion evidence.
    """
    runtime = client_runtime[client_id]
    values = []
    for value in runtime.get("recent_iats", []):
        try:
            x = float(value)
        except Exception:
            continue
        if x > 0.0 and np.isfinite(x) and x <= TRAINING_TO_UPLOAD_IAT_FILTER_MAX_SECONDS:
            values.append(x)

    if not values:
        return float(fallback)

    return float(np.median(values))


def get_training_elapsed_s(runtime: dict, ts: float) -> float:
    training_start_ts = float(runtime.get("training_start_ts", 0.0) or 0.0)
    if training_start_ts <= 0.0:
        training_start_ts = float(runtime.get("stable_state_since", 0.0) or 0.0)
    if training_start_ts <= 0.0:
        return 0.0
    return max(0.0, float(ts) - training_start_ts)


def get_adaptive_training_to_upload_gate_s(client_id: str) -> Tuple[float, float]:
    median_iat = get_filtered_recent_median_iat(client_id)
    gate_s = max(
        TRAINING_TO_UPLOAD_MIN_FLOOR_SECONDS,
        TRAINING_TO_UPLOAD_MEDIAN_IAT_MULTIPLIER * median_iat,
    )
    gate_s = min(gate_s, TRAINING_TO_UPLOAD_MAX_GATE_SECONDS)
    return float(gate_s), float(median_iat)

def write_protocol_transition_block(client_id: str, from_state: int, to_state: int, reason: str,
                                    confidence: float = 0.0, direction: int = 0,
                                    payload_bytes: int = 0, ts: float = 0.0,
                                    wall_time_ns: int = 0, mono_time_ns: int = 0,
                                    extra: Optional[dict] = None) -> None:
    payload = {
        "client_id": client_id,
        "from_state": int(from_state),
        "to_state": int(to_state),
        "from_phase": state_to_phase_label(int(from_state)),
        "to_phase": state_to_phase_label(int(to_state)),
        "reason": str(reason),
        "confidence": float(confidence),
        "direction": int(direction),
        "payload_bytes": int(payload_bytes),
        "packet_timestamp": float(ts),
        "packet_wall_time_ns": int(wall_time_ns),
        "packet_mono_time_ns": int(mono_time_ns),
    }
    if isinstance(extra, dict):
        payload.update(extra)
    write_event("protocol_transition_guard_block", payload)



def has_upload_start_evidence(direction: int, payload_bytes: int, feature_bundle: Optional[dict]) -> bool:
    """Model agnostic evidence gate for TRAINING -> UPLOAD.

    The current meaningful outbound packet is the primary signal.  Short and
    long window statistics are supporting evidence only, because the 1 second
    window can still contain download residue for smaller models.
    """
    feature_bundle = feature_bundle or {}
    if int(direction) != 1 or int(payload_bytes) < PHASE_MIN_PAYLOAD:
        return False

    short_outbound_share = float(feature_bundle.get("short_outbound_share", 0.0))
    short_outbound_count = int(feature_bundle.get("short_outbound_count", 0))
    outbound_share = float(feature_bundle.get("outbound_share", 0.0))
    outbound_count = int(feature_bundle.get("outbound_count", 0))
    dir_ratio = float(feature_bundle.get("dir_ratio", 0.0))

    current_packet_evidence = True
    short_window_support = short_outbound_count >= 1 and short_outbound_share >= BOUNDARY_MIN_WINDOW_SHARE
    long_window_support = outbound_count >= 1 and (outbound_share >= BOUNDARY_MIN_WINDOW_SHARE or dir_ratio >= 1.0)

    return bool(current_packet_evidence or short_window_support or long_window_support)

def has_upload_to_download_evidence(prev_state: int, direction: int, payload_bytes: int,
                                    feature_bundle: Optional[dict]) -> bool:
    """Model agnostic evidence gate for UPLOAD -> DOWNLOAD.

    Once the protocol state is already UPLOAD, the first meaningful inbound
    server to client packet is valid next round download evidence.  Short and
    long window statistics support the decision but do not veto the current
    packet, because small model traffic can leave the 1 second window mixed.
    """
    feature_bundle = feature_bundle or {}

    if int(prev_state) != UPLOAD:
        return False
    if int(direction) != -1:
        return False
    if int(payload_bytes) < PHASE_MIN_PAYLOAD:
        return False

    short_inbound_share = float(feature_bundle.get("short_inbound_share", 0.0))
    short_inbound_count = int(feature_bundle.get("short_inbound_count", 0))
    inbound_share = float(feature_bundle.get("inbound_share", 0.0))
    inbound_count = int(feature_bundle.get("inbound_count", 0))
    dir_ratio = float(feature_bundle.get("dir_ratio", 100.0))

    current_packet_evidence = True
    short_window_support = short_inbound_count >= 1 and short_inbound_share >= BOUNDARY_MIN_WINDOW_SHARE
    long_window_support = inbound_count >= 1 and (inbound_share >= BOUNDARY_MIN_WINDOW_SHARE or dir_ratio <= 1.0)

    return bool(current_packet_evidence or short_window_support or long_window_support)

def has_download_still_active_evidence(direction: int, payload_bytes: int,
                                       feature_bundle: Optional[dict],
                                       runtime: Optional[dict] = None,
                                       ts: float = 0.0) -> bool:
    """Evidence that the current DOWNLOAD burst is still active.

    Timing-free version: only the current packet and current feature window can
    hold DOWNLOAD open.  A previous large inbound timestamp is not allowed to
    veto a transition, because that makes short RNN rounds depend on elapsed
    time while CNN continues to pass.
    """
    feature_bundle = feature_bundle or {}

    inbound_bytes = float(feature_bundle.get("inbound_bytes", 0.0))
    inbound_count = int(feature_bundle.get("inbound_count", 0))
    burst_density = int(feature_bundle.get("burst_density", 0))
    inbound_share = float(feature_bundle.get("inbound_share", 0.0))
    short_inbound_count = int(feature_bundle.get("short_inbound_count", 0))
    short_inbound_share = float(feature_bundle.get("short_inbound_share", 0.0))

    current_large_inbound = (
        int(direction) == -1
        and int(payload_bytes) >= PHASE_MIN_PAYLOAD
    )

    short_window_download = (
        short_inbound_count >= 1
        and short_inbound_share >= BOUNDARY_MIN_WINDOW_SHARE
    )

    long_window_download = (
        inbound_count >= max(TRAINING_LATCH_MIN_DOWNLOAD_PACKETS, 1)
        and burst_density >= 1
        and inbound_share >= BOUNDARY_STRONG_WINDOW_SHARE
        and inbound_bytes >= PHASE_MIN_PAYLOAD
    )

    return bool(current_large_inbound or short_window_download or long_window_download)


def log_transition_block(client_id: str, decision: TransitionDecision, confidence: float,
                         direction: int, payload_bytes: int, ts: float,
                         wall_time_ns: int, mono_time_ns: int,
                         feature_bundle: Optional[dict]) -> None:
    feature_bundle = feature_bundle or {}
    write_event("transition_guard_block", {
        "client_id": client_id,
        "from_state": int(decision.from_state),
        "to_state": int(decision.to_state),
        "from_phase": state_to_phase_label(int(decision.from_state)),
        "to_phase": state_to_phase_label(int(decision.to_state)),
        "source": str(decision.source),
        "reason": str(decision.reason),
        "confidence": float(confidence),
        "direction": int(direction),
        "payload_bytes": int(payload_bytes),
        "burst_density": int(feature_bundle.get("burst_density", 0)),
        "inbound_count": int(feature_bundle.get("inbound_count", 0)),
        "outbound_count": int(feature_bundle.get("outbound_count", 0)),
        "inbound_share": float(feature_bundle.get("inbound_share", 0.0)),
        "outbound_share": float(feature_bundle.get("outbound_share", 0.0)),
        "dir_ratio": float(feature_bundle.get("dir_ratio", 0.0)),
        "packet_timestamp": float(ts),
        "packet_wall_time_ns": int(wall_time_ns),
        "packet_mono_time_ns": int(mono_time_ns),
    })


def decide_phase_transition(client_id: str, from_state: int, to_state: int,
                            source: str, confidence: float, direction: int,
                            payload_bytes: int, feature_bundle: Optional[dict],
                            ts: float, force: bool = False) -> TransitionDecision:
    """Single authority for FL phase transitions.

    All callers may propose a state, but this function owns the protocol order
    and evidence checks. Valid FL order is:
    IDLE -> DOWNLOAD -> TRAINING -> UPLOAD -> DOWNLOAD.
    """
    runtime = client_runtime[client_id]
    from_state = int(from_state)
    to_state = int(to_state)

    if from_state == to_state:
        return TransitionDecision(True, from_state, to_state, str(source), "self_transition")

    upload_start = has_upload_start_evidence(direction, payload_bytes, feature_bundle)
    upload_to_download = has_upload_to_download_evidence(from_state, direction, payload_bytes, feature_bundle)
    download_still_active = has_download_still_active_evidence(
        direction, payload_bytes, feature_bundle, runtime=runtime, ts=ts
    )

    if from_state == IDLE and to_state == DOWNLOAD:
        return TransitionDecision(True, from_state, to_state, str(source), "idle_to_download")

    if from_state == DOWNLOAD and to_state == TRAINING:
        if download_still_active and not force:
            return TransitionDecision(False, from_state, to_state, str(source), "download_evidence_still_present")
        return TransitionDecision(True, from_state, to_state, str(source), "download_to_training")

    if from_state == TRAINING and to_state == UPLOAD:
        if not (upload_start or force):
            return TransitionDecision(False, from_state, to_state, str(source), "training_to_upload_without_upload_evidence")

        # Timing-free transition authority: a meaningful outbound packet is
        # sufficient TRAINING -> UPLOAD evidence.  Training duration and IAT
        # gates are kept only for logging/evaluation elsewhere, not as vetoes.
        return TransitionDecision(True, from_state, to_state, str(source), "training_to_upload_confirmed")

    if from_state == UPLOAD and to_state == DOWNLOAD:
        if upload_to_download or force:
            return TransitionDecision(True, from_state, to_state, str(source), "upload_to_download_confirmed")
        return TransitionDecision(False, from_state, to_state, str(source), "upload_to_download_without_download_evidence")

    if from_state == UPLOAD and to_state == IDLE:
        if int(runtime.get("cycle_stage", 0)) == 2 and not force:
            return TransitionDecision(False, from_state, to_state, str(source), "upload_to_idle_deferred_until_download")
        return TransitionDecision(True, from_state, to_state, str(source), "upload_to_idle")

    return TransitionDecision(False, from_state, to_state, str(source), "protocol_order_forbidden")


def commit_phase_transition(client_id: str, decision: TransitionDecision,
                            confidence: float, ts: float, wall_time_ns: int,
                            mono_time_ns: int, direction: int = 0,
                            payload_bytes: int = 0,
                            feature_bundle: Optional[dict] = None) -> Tuple[int, bool]:
    """Commit the transition decision and update state bookkeeping.

    No other function should directly finalize runtime["stable_state"].
    """
    runtime = client_runtime[client_id]

    if not decision.allowed:
        log_transition_block(
            client_id=client_id,
            decision=decision,
            confidence=confidence,
            direction=direction,
            payload_bytes=payload_bytes,
            ts=ts,
            wall_time_ns=wall_time_ns,
            mono_time_ns=mono_time_ns,
            feature_bundle=feature_bundle,
        )
        runtime["stable_state"] = int(decision.from_state)
        runtime["candidate_state"] = int(decision.from_state)
        runtime["candidate_count"] = 1
        runtime["candidate_first_ts"] = float(ts)
        return int(decision.from_state), False

    changed = int(decision.from_state) != int(decision.to_state)
    runtime["stable_state"] = int(decision.to_state)
    runtime["stable_state_since"] = float(ts)
    runtime["candidate_state"] = int(decision.to_state)
    runtime["candidate_count"] = 1
    runtime["candidate_first_ts"] = float(ts)
    runtime["raw_state"] = int(decision.to_state)

    if int(decision.to_state) == IDLE:
        runtime["belief"][:] = np.array([0.94, 0.02, 0.02, 0.02], dtype=float)
    elif int(decision.to_state) == DOWNLOAD:
        runtime["belief"][:] = np.array([0.02, 0.94, 0.02, 0.02], dtype=float)
    elif int(decision.to_state) == TRAINING:
        runtime["belief"][:] = np.array([0.02, 0.02, 0.94, 0.02], dtype=float)
    elif int(decision.to_state) == UPLOAD:
        runtime["belief"][:] = np.array([0.02, 0.02, 0.02, 0.94], dtype=float)

    if int(decision.to_state) == TRAINING:
        if changed or float(runtime.get("training_start_ts", 0.0) or 0.0) <= 0.0:
            runtime["training_start_ts"] = float(ts)
    else:
        runtime["training_latched"] = False
        runtime["training_start_ts"] = 0.0

    if changed:
        write_event("state_transition", {
            "client_id": client_id,
            "from_state": int(decision.from_state),
            "to_state": int(decision.to_state),
            "from_phase": state_to_phase_label(int(decision.from_state)),
            "to_phase": state_to_phase_label(int(decision.to_state)),
            "source": str(decision.source),
            "reason": str(decision.reason),
            "inferred_round_id": int(runtime["inferred_round_id"]),
            "completed_cycle_id": int(runtime["completed_cycle_id"]),
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(wall_time_ns),
            "packet_mono_time_ns": int(mono_time_ns),
        })

    return int(decision.to_state), changed


def update_stable_state(client_id: str, raw_state: int, confidence: float, ts: float,
                        wall_time_ns: int, mono_time_ns: int, payload_bytes: int,
                        direction: int, feature_bundle: dict):
    """Update candidate state, then delegate all promotion decisions to the
    unified transition engine.
    """
    runtime = client_runtime[client_id]
    prev_stable_state = int(runtime["stable_state"])
    runtime["raw_state"] = int(raw_state)

    if int(raw_state) == int(runtime["candidate_state"]):
        runtime["candidate_count"] += 1
    else:
        runtime["candidate_state"] = int(raw_state)
        runtime["candidate_count"] = 1
        runtime["candidate_first_ts"] = float(ts)

    proposed_state = int(runtime["candidate_state"])

    # Timing-free transition authority.  We use packet/streak evidence and
    # confidence only.  Elapsed candidate duration and stable dwell are not
    # allowed to veto phase transitions.
    required_packets = MIN_STATE_HOLD_PACKETS
    required_confidence = 0.45

    if prev_stable_state == IDLE and proposed_state == DOWNLOAD:
        required_packets = 1
        required_confidence = 0.40

    if prev_stable_state == UPLOAD and proposed_state == DOWNLOAD:
        required_packets = UPLOAD_TO_DOWNLOAD_STATE_HOLD_PACKETS
        required_confidence = UPLOAD_TO_DOWNLOAD_MIN_CONFIDENCE

    if prev_stable_state == TRAINING and proposed_state in (DOWNLOAD, UPLOAD):
        required_packets = 1 if proposed_state == UPLOAD else TRAINING_FAST_EXIT_MIN_PACKETS
        required_confidence = BOUNDARY_MIN_CONFIDENCE

    if prev_stable_state == IDLE and proposed_state == DOWNLOAD:
        write_event("idle_download_gate_debug", {
            "client_id": client_id,
            "candidate_count": int(runtime["candidate_count"]),
            "confidence": float(confidence),
            "required_packets": int(required_packets),
            "required_confidence": float(required_confidence),
            "timing_free_transition": True,
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(wall_time_ns),
            "packet_mono_time_ns": int(mono_time_ns),
        })

    upload_to_download_candidate = (
        prev_stable_state == UPLOAD
        and proposed_state == DOWNLOAD
        and has_upload_to_download_evidence(
            prev_stable_state, direction, payload_bytes, feature_bundle
        )
    )

    training_to_upload_candidate = (
        prev_stable_state == TRAINING
        and proposed_state == UPLOAD
        and has_upload_start_evidence(direction, payload_bytes, feature_bundle)
    )

    if upload_to_download_candidate or training_to_upload_candidate:
        promote_candidate = (
            proposed_state != prev_stable_state
            and int(runtime["candidate_count"]) >= int(required_packets)
            and float(confidence) >= float(required_confidence)
        )
    else:
        promote_candidate = (
            proposed_state != prev_stable_state
            and int(runtime["candidate_count"]) >= int(required_packets)
            and float(confidence) >= float(required_confidence)
        )

    if not promote_candidate:
        return int(runtime["stable_state"]), False

    decision = decide_phase_transition(
        client_id=client_id,
        from_state=prev_stable_state,
        to_state=proposed_state,
        source="stable_candidate_promotion",
        confidence=confidence,
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
        ts=ts,
    )

    return commit_phase_transition(
        client_id=client_id,
        decision=decision,
        confidence=confidence,
        ts=ts,
        wall_time_ns=wall_time_ns,
        mono_time_ns=mono_time_ns,
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
    )


def update_cycle_round(client_id: str, stable_state: int, prev_stable_state: int, confidence: float,
                       ts: float, wall_time_ns: int, mono_time_ns: int):
    runtime = client_runtime[client_id]
    stage = runtime["cycle_stage"]

    # Stage 0→1: DOWNLOAD (or IDLE) → TRAINING
    # No confidence gate here.  The training latch and stable state gates
    # already filter this transition.  Gating on confidence caused a silent
    # failure: a low-confidence control packet (keepalive/ACK, direction=0)
    # would bail out of this function before the stage advanced, but
    # apply_training_latch (which has no confidence check) then set
    # stable_state=TRAINING in the runtime.  Every subsequent packet saw
    # prev_stable_state=TRAINING, so the DOWNLOAD->TRAINING transition was
    # never recorded and cycle_stage stayed at 0 indefinitely.
    if stage == 0 and stable_state == TRAINING and prev_stable_state in (DOWNLOAD, IDLE):
        runtime["cycle_stage"] = 1

    # Stage 1→2: TRAINING → UPLOAD
    # Same reasoning — no confidence gate.  The latch release and
    # training_fast_exit (guarded to stage==1) already confirm this.
    elif stage == 1 and prev_stable_state == TRAINING and stable_state == UPLOAD:
        runtime["cycle_stage"] = 2

    # Stage 2→0: UPLOAD (or IDLE) → DOWNLOAD  — round increment.
    # Confidence gate kept here only.  This is the one transition that
    # changes an observable counter (inferred_round_id), so a low-confidence
    # jitter packet should not trigger it.  Stage advancements (0→1, 1→2)
    # are rule-driven and do not need this protection.
    #elif stage == 2 and stable_state == DOWNLOAD and prev_stable_state in (UPLOAD, IDLE):
    elif stage == 2 and stable_state == DOWNLOAD and prev_stable_state == UPLOAD:
        if confidence < 0.45:
            return runtime["inferred_round_id"], runtime["completed_cycle_id"], stage

        upload_evidence = get_open_upload_completion_evidence(client_id, ts)
        upload_packets = int(upload_evidence.get("upload_packets", 0) or 0)
        upload_bytes = int(upload_evidence.get("upload_bytes", 0) or 0)

        round_upload_evidence_ok = (
            upload_packets >= MIN_ROUND_UPLOAD_EVIDENCE_PACKETS
            and upload_bytes >= MIN_ROUND_UPLOAD_EVIDENCE_BYTES
        )

        if bool(upload_evidence.get("valid", False)):
            upload_quality = "full_upload"
        elif round_upload_evidence_ok:
            upload_quality = "short_or_fragmented_upload"
        elif upload_packets > 0 or upload_bytes > 0:
            upload_quality = "micro_upload_fragment"
        else:
            upload_quality = "missing_upload_evidence"

        # Timing-free round counting still needs concrete upload evidence.
        # Without this guard, a compressed false cycle such as
        # DOWNLOAD -> FIT -> tiny UPLOAD -> DOWNLOAD can create an extra round.
        # This is not a duration check and it is not model-specific; it only
        # requires at least two meaningful upload packets and non-control bytes.
        if not round_upload_evidence_ok:
            runtime["cycle_stage"] = 0
            write_event("round_completion_blocked", {
                "client_id": client_id,
                "reason": "insufficient_packet_upload_evidence",
                "stable_state": int(stable_state),
                "prev_stable_state": int(prev_stable_state),
                "cycle_stage_before_reset": int(stage),
                "inferred_round_id": int(runtime.get("inferred_round_id", 0)),
                "completed_cycle_id": int(runtime.get("completed_cycle_id", 0)),
                "packet_timestamp": float(ts),
                "packet_wall_time_ns": int(wall_time_ns),
                "packet_mono_time_ns": int(mono_time_ns),
                "upload_quality": str(upload_quality),
                "min_round_upload_packets": int(MIN_ROUND_UPLOAD_EVIDENCE_PACKETS),
                "min_round_upload_bytes": int(MIN_ROUND_UPLOAD_EVIDENCE_BYTES),
                **upload_evidence,
            })
            return runtime["inferred_round_id"], runtime["completed_cycle_id"], runtime["cycle_stage"]

        # Each client counts its own rounds independently — no cross-client sync.
        runtime["inferred_round_id"] += 1
        runtime["completed_cycle_id"] += 1
        runtime["cycle_stage"] = 0
        write_event("cycle_completed", {
            "client_id": client_id,
            "inferred_round_id": int(runtime["inferred_round_id"]),
            "completed_cycle_id": int(runtime["completed_cycle_id"]),
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(wall_time_ns),
            "packet_mono_time_ns": int(mono_time_ns),
            "upload_quality": str(upload_quality),
            "min_round_upload_packets": int(MIN_ROUND_UPLOAD_EVIDENCE_PACKETS),
            "min_round_upload_bytes": int(MIN_ROUND_UPLOAD_EVIDENCE_BYTES),
            **upload_evidence,
        })

    return runtime["inferred_round_id"], runtime["completed_cycle_id"], runtime["cycle_stage"]


def get_pending_attack_context_key(client_id: str) -> str:
    return f"{PENDING_ATTACK_CONTEXT_PREFIX}{client_id}"


def get_recent_upload_duration_s(client_id: str) -> float:
    """Return a local upload duration estimate for timing gates only.

    This is not an adaptation profile, is not written to Redis, and is not
    used to compute bandwidth. It only helps the analyzer avoid repeated
    trigger attempts while clients are still in the same upload opportunity.
    """
    runtime = client_runtime[client_id]
    duration_hist = list(runtime.get("upload_duration_history", []))
    if duration_hist:
        value = float(np.median(duration_hist))
    else:
        value = DEFAULT_MEAN_UPLOAD_TIME_SECONDS
    return clamp(value, MIN_MEAN_UPLOAD_TIME_SECONDS, MAX_MEAN_UPLOAD_TIME_SECONDS)


def log_upload_observation(client_id: str, upload_duration_s: float, upload_bytes: int,
                           upload_start_ts: float, upload_end_ts: float,
                           inferred_round_id: int, wall_time_ns: int, mono_time_ns: int) -> None:
    """Log upload observation only.

    The analyzer must not compute available bandwidth, must not update any
    bandwidth key in Redis, and must not maintain any attack adaptation value.
    """
    write_event("upload_observation_logged", {
        "client_id": client_id,
        "round_id": int(inferred_round_id),
        "upload_duration_s": float(upload_duration_s),
        "upload_bytes": int(upload_bytes),
        "upload_start_ts": float(upload_start_ts),
        "upload_end_ts": float(upload_end_ts),
        "packet_timestamp": float(upload_end_ts),
        "packet_wall_time_ns": int(wall_time_ns),
        "packet_mono_time_ns": int(mono_time_ns),
    })


def send_attack_outcome_to_intervener(
    attack_id: str,
    client_id: str,
    round_id: int,
    wire_upload_duration_s: float,
    wire_upload_bytes: int,
    wire_upload_packets: int,
    close_reason: str,
) -> None:
    """Send completed wire upload outcome to the intervener for local adaptation.

    This is not Redis feedback and does not reintroduce analyzer side adaptation.
    The analyzer only reports measured wire-level outcome for a known attack_id.
    """
    if not attack_id:
        return
    payload = {
        "type": "attack_outcome",
        "attack_id": str(attack_id),
        "client_id": str(client_id),
        "round_id": int(round_id),
        "wire_upload_duration_s": float(wire_upload_duration_s),
        "wire_upload_bytes": int(wire_upload_bytes),
        "wire_upload_packets": int(wire_upload_packets),
        "close_reason": str(close_reason),
        "timestamp": time.time(),
    }
    try:
        outcome_sock.sendto(
            json.dumps(payload).encode("utf-8"),
            (INTERVENER_HOST, INTERVENER_PORT),
        )
    except Exception as exc:
        print(f"[WARN] attack outcome UDP send failed: {exc}", flush=True)


def send_attack_release_to_intervener(
    attack_id: str,
    client_id: str,
    round_id: int,
    close_reason: str,
) -> None:
    """Release the active intervener rule when the analyzer closes upload."""
    if not attack_id:
        return
    payload = {
        "type": "release_attack",
        "command": "release_attack",
        "attack_id": str(attack_id),
        "client_id": str(client_id),
        "target_client": str(client_id),
        "round_id": int(round_id),
        "close_reason": str(close_reason),
        "timestamp": time.time(),
    }
    try:
        outcome_sock.sendto(
            json.dumps(payload).encode("utf-8"),
            (INTERVENER_HOST, INTERVENER_PORT),
        )
        print(
            f"[RELEASE-SEND] client={client_id} attack_id={attack_id} reason={close_reason}",
            flush=True,
        )
    except Exception as exc:
        print(f"[WARN] attack release UDP send failed: {exc}", flush=True)


def reset_wire_upload_state(client_id: str) -> None:
    wire_upload_state[client_id] = {
        "active": False,
        "client_id": "",
        "round_id": 0,
        "attack_id": "",
        "start_ts": 0.0,
        "last_ts": 0.0,
        "bytes": 0,
        "packets": 0,
        "iat_values": [],
        "first_wall_time_ns": 0,
        "last_wall_time_ns": 0,
        "first_mono_time_ns": 0,
        "last_mono_time_ns": 0,
        "last_upload_packet_ts": 0.0,
    }


def write_wire_upload_episode(client_id: str, close_reason: str) -> None:
    state = wire_upload_state[client_id]
    if not state.get("active"):
        return

    start_ts = float(state.get("start_ts", 0.0))
    end_ts = float(state.get("last_ts", start_ts))
    duration_s = max(end_ts - start_ts, 0.0)
    iats = list(state.get("iat_values", []))
    mean_iat_s = sum(iats) / len(iats) if iats else 0.0
    max_iat_s = max(iats) if iats else 0.0

    row = [
        f"{time.time():.6f}",
        EXPERIMENT_ID,
        client_id,
        int(state.get("round_id", 0)),
        round(start_ts, 6),
        round(end_ts, 6),
        round(duration_s, 6),
        int(state.get("bytes", 0)),
        int(state.get("packets", 0)),
        round(mean_iat_s, 6),
        round(max_iat_s, 6),
        close_reason,
        str(state.get("attack_id", "")),
        int(state.get("first_wall_time_ns", 0)),
        int(state.get("last_wall_time_ns", 0)),
        int(state.get("first_mono_time_ns", 0)),
        int(state.get("last_mono_time_ns", 0)),
    ]

    for path in (WIRE_UPLOAD_LOG_FILE, LATEST_WIRE_UPLOAD_LOG_FILE):
        with open(path, "a", newline="") as f:
            csv.writer(f).writerow(row)
            f.flush()

    write_event("wire_upload_episode", {
        "client_id": client_id,
        "round_id": int(state.get("round_id", 0)),
        "wire_upload_start_ts": round(start_ts, 6),
        "wire_upload_end_ts": round(end_ts, 6),
        "wire_upload_duration_s": round(duration_s, 6),
        "wire_upload_bytes": int(state.get("bytes", 0)),
        "wire_upload_packets": int(state.get("packets", 0)),
        "attack_id": str(state.get("attack_id", "")),
        "mean_iat_s": round(mean_iat_s, 6),
        "max_iat_s": round(max_iat_s, 6),
        "close_reason": close_reason,
    })
    attack_id = str(state.get("attack_id", ""))
    round_id = int(state.get("round_id", 0))

    if ANALYZER_SEND_RELEASE:
        send_attack_release_to_intervener(
            attack_id=attack_id,
            client_id=client_id,
            round_id=round_id,
            close_reason=close_reason,
        )
    elif attack_id:
        write_event("analyzer_release_suppressed", {
            "attack_id": attack_id,
            "client_id": client_id,
            "round_id": int(round_id),
            "close_reason": close_reason,
            "analyzer_attack_mode": str(ANALYZER_ATTACK_MODE),
            "reason": "release_only_sent_for_throttle_mode",
        })

    send_attack_outcome_to_intervener(
        attack_id=attack_id,
        client_id=client_id,
        round_id=round_id,
        wire_upload_duration_s=duration_s,
        wire_upload_bytes=int(state.get("bytes", 0)),
        wire_upload_packets=int(state.get("packets", 0)),
        close_reason=close_reason,
    )

    runtime = client_runtime[client_id]
    runtime["active_attack_id"] = ""
    runtime["attack_active_until"] = 0.0

    reset_wire_upload_state(client_id)


def update_wire_upload_episode(client_id: str, inferred_round_id: int, previous_decision_phase: str,
                               decision_phase_label: str, direction: int, payload_bytes: int,
                               packet_ts: float, wall_time_ns: int, mono_time_ns: int) -> None:
    """Measure active wire upload duration inside the decision UPLOAD phase.

    Upload starts when decision_phase changes from TRAINING to UPLOAD.
    The recorded duration ends at the last large outbound upload packet, not at
    the later UPLOAD to DOWNLOAD transition. This prevents synchronous server
    waiting time from polluting the bandwidth baseline.
    """
    runtime = client_runtime[client_id]
    state = wire_upload_state[client_id]
    prev_phase = str(previous_decision_phase or "").upper()
    curr_phase = str(decision_phase_label or "").upper()

    upload_started = prev_phase == PHASE_TRAINING and curr_phase == PHASE_UPLOAD
    upload_ended = prev_phase == PHASE_UPLOAD and curr_phase == PHASE_DOWNLOAD

    if upload_started:
        if state.get("active"):
            write_wire_upload_episode(client_id, "new_decision_training_to_upload")
            state = wire_upload_state[client_id]

        state["active"] = True
        state["client_id"] = client_id
        state["round_id"] = int(inferred_round_id)
        state["attack_id"] = str(runtime.get("active_attack_id", "") or "")
        state["start_ts"] = float(packet_ts)
        state["last_ts"] = float(packet_ts)
        state["bytes"] = 0
        state["packets"] = 0
        state["iat_values"] = []
        state["first_wall_time_ns"] = int(wall_time_ns)
        state["last_wall_time_ns"] = int(wall_time_ns)
        state["first_mono_time_ns"] = int(mono_time_ns)
        state["last_mono_time_ns"] = int(mono_time_ns)
        state["last_upload_packet_ts"] = 0.0

    state = wire_upload_state[client_id]
    if state.get("active"):
        if not state.get("attack_id"):
            state["attack_id"] = str(runtime.get("active_attack_id", "") or "")

        if int(direction) == 1 and int(payload_bytes) >= WIRE_UPLOAD_MIN_PAYLOAD_BYTES:
            last_upload_ts = float(state.get("last_upload_packet_ts", 0.0) or 0.0)
            if int(state.get("packets", 0) or 0) == 0:
                state["start_ts"] = float(packet_ts)
                state["first_wall_time_ns"] = int(wall_time_ns)
                state["first_mono_time_ns"] = int(mono_time_ns)
            elif last_upload_ts > 0.0:
                state["iat_values"].append(max(float(packet_ts) - last_upload_ts, 0.0))
            state["last_upload_packet_ts"] = float(packet_ts)
            state["last_ts"] = float(packet_ts)
            state["last_wall_time_ns"] = int(wall_time_ns)
            state["last_mono_time_ns"] = int(mono_time_ns)
            state["bytes"] = int(state.get("bytes", 0)) + int(payload_bytes)
            state["packets"] = int(state.get("packets", 0)) + 1

    if upload_ended and state.get("active"):
        # Keep last_ts as the last large outbound upload packet timestamp.
        # Do not overwrite it with the later DOWNLOAD transition packet,
        # otherwise synchronous server waiting time pollutes upload duration.
        write_wire_upload_episode(client_id, "decision_upload_to_download")


def finalize_open_wire_upload_logs() -> None:
    for client_id, state in list(wire_upload_state.items()):
        if state.get("active"):
            write_wire_upload_episode(client_id, "program_shutdown")

def update_normal_upload_baseline_if_clean(
    client_id: str,
    upload_duration_s: float,
    upload_bytes: int,
    upload_packets: int,
    round_id: int,
    ts: float,
    wall_time_ns: int,
    mono_time_ns: int,
) -> None:
    """Collect the first clean active wire upload durations for the per client normal baseline.

    Only uploads from rounds without an analyzer triggered attack are accepted.
    Once BASELINE_WARMUP_UPLOADS samples are collected, the baseline is frozen so
    attacked upload durations cannot make the next expected upload time grow.
    """
    runtime = client_runtime[client_id]

    if bool(runtime.get("baseline_ready", False)):
        return

    attacked_round = int(runtime.get("last_attack_round_id", 0) or 0) == int(round_id)
    active_attack = bool(runtime.get("active_attack_id", ""))

    if attacked_round or active_attack:
        write_event("normal_upload_baseline_skipped", {
            "client_id": client_id,
            "round_id": int(round_id),
            "reason": "upload_episode_had_attack",
            "attacked_round": bool(attacked_round),
            "active_attack": bool(active_attack),
            "upload_duration_s": float(upload_duration_s),
            "upload_bytes": int(upload_bytes),
            "upload_packets": int(upload_packets),
            "baseline_sample_count": int(len(runtime.get("normal_upload_samples", []))),
            "baseline_required_samples": int(BASELINE_WARMUP_UPLOADS),
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(wall_time_ns),
            "packet_mono_time_ns": int(mono_time_ns),
        })
        return

    duration_samples = runtime["normal_upload_samples"]
    bandwidth_samples = runtime["normal_upload_bandwidth_samples"]

    if len(duration_samples) < BASELINE_WARMUP_UPLOADS:
        duration_samples.append(float(upload_duration_s))
        if float(upload_duration_s) > 0.0 and int(upload_bytes) > 0:
            effective_bw_mbps = (float(upload_bytes) * 8.0) / (float(upload_duration_s) * 1_000_000.0)
            bandwidth_samples.append(float(effective_bw_mbps))

    if duration_samples:
        runtime["normal_upload_duration_s"] = float(np.mean(list(duration_samples)))
        runtime["normal_upload_bytes"] = int(upload_bytes)
        runtime["normal_upload_packets"] = int(upload_packets)

    if bandwidth_samples:
        runtime["mean_effective_bandwidth_mbps"] = float(np.mean(list(bandwidth_samples)))

    if len(duration_samples) >= BASELINE_WARMUP_UPLOADS:
        runtime["baseline_ready"] = True

    write_event("normal_upload_baseline_update", {
        "client_id": client_id,
        "round_id": int(round_id),
        "upload_duration_s": float(upload_duration_s),
        "upload_bytes": int(upload_bytes),
        "upload_packets": int(upload_packets),
        "baseline_sample_count": int(len(duration_samples)),
        "baseline_required_samples": int(BASELINE_WARMUP_UPLOADS),
        "normal_upload_duration_s": float(runtime.get("normal_upload_duration_s", 0.0) or 0.0),
        "normal_upload_bytes": int(runtime.get("normal_upload_bytes", 0) or 0),
        "normal_upload_packets": int(runtime.get("normal_upload_packets", 0) or 0),
        "mean_effective_bandwidth_mbps": float(runtime.get("mean_effective_bandwidth_mbps", 0.0) or 0.0),
        "baseline_ready": bool(runtime.get("baseline_ready", False)),
        "packet_timestamp": float(ts),
        "packet_wall_time_ns": int(wall_time_ns),
        "packet_mono_time_ns": int(mono_time_ns),
    })


def update_upload_episode(r: Optional[redis.Redis], client_id: str, stable_state: int, direction: int, packet_size: int,
                          ts: float, wall_time_ns: int, mono_time_ns: int):
    runtime = client_runtime[client_id]

    if stable_state == UPLOAD and direction == 1 and int(packet_size) >= WIRE_UPLOAD_MIN_PAYLOAD_BYTES:
        if not runtime["upload_episode_active"]:
            runtime["upload_episode_active"] = True
            runtime["upload_episode_start_ts"] = ts
            runtime["upload_episode_last_ts"] = ts
            runtime["upload_episode_bytes"] = 0
            runtime["upload_episode_packets"] = 0
            runtime["current_upload_bytes"] = 0

        runtime["upload_episode_last_ts"] = float(ts)
        runtime["upload_episode_bytes"] += int(packet_size)
        runtime["upload_episode_packets"] = int(runtime.get("upload_episode_packets", 0) or 0) + 1
        runtime["current_upload_bytes"] += int(packet_size)
        return

    if runtime["upload_episode_active"] and stable_state != UPLOAD:
        upload_start_ts = float(runtime["upload_episode_start_ts"])
        upload_last_ts = float(runtime.get("upload_episode_last_ts", upload_start_ts) or upload_start_ts)
        upload_duration = max(upload_last_ts - upload_start_ts, 0.0)
        upload_bytes = int(runtime["upload_episode_bytes"])
        round_gap = float(ts) - float(runtime["last_round_increment_ts"])
        upload_packets = int(runtime.get("upload_episode_packets", 0) or 0)
        upload_evidence = evaluate_upload_completion_evidence(
            client_id=client_id,
            upload_duration_s=upload_duration,
            upload_bytes=upload_bytes,
            upload_packets=upload_packets,
        )

        valid_upload_episode = (
            bool(upload_evidence.get("valid", False))
            and round_gap >= MIN_ROUND_GAP_SECONDS
        )

        if valid_upload_episode:
            update_normal_upload_baseline_if_clean(
                client_id=client_id,
                upload_duration_s=float(upload_duration),
                upload_bytes=int(upload_bytes),
                upload_packets=int(upload_packets),
                round_id=int(runtime.get("inferred_round_id", 0)),
                ts=float(ts),
                wall_time_ns=int(wall_time_ns),
                mono_time_ns=int(mono_time_ns),
            )
            runtime["upload_duration_history"].append(float(upload_duration))
            runtime["upload_bytes_history"].append(int(upload_bytes))
            runtime["upload_packet_history"].append(int(upload_packets))
            runtime["last_round_increment_ts"] = ts
            write_event("validated_upload_episode", {
                "client_id": client_id,
                "upload_episode_seconds": float(upload_duration),
                "upload_episode_bytes": int(upload_bytes),
                "upload_episode_packets": int(upload_packets),
                "packet_timestamp": float(ts),
                "packet_wall_time_ns": int(wall_time_ns),
                "packet_mono_time_ns": int(mono_time_ns),
                **upload_evidence,
            })
            log_upload_observation(
                client_id=client_id,
                upload_duration_s=float(upload_duration),
                upload_bytes=int(upload_bytes),
                upload_start_ts=float(upload_start_ts),
                upload_end_ts=float(upload_last_ts),
                inferred_round_id=int(runtime.get("inferred_round_id", 0)),
                wall_time_ns=int(wall_time_ns),
                mono_time_ns=int(mono_time_ns),
            )

        completed_upload_bytes = int(runtime.get("current_upload_bytes", 0) or 0)
        if completed_upload_bytes > 0:
            runtime["previous_upload_bytes"] = completed_upload_bytes

        runtime["current_upload_bytes"] = 0
        runtime["upload_episode_active"] = False
        runtime["upload_episode_start_ts"] = 0.0
        runtime["upload_episode_last_ts"] = 0.0
        runtime["upload_episode_bytes"] = 0
        runtime["upload_episode_packets"] = 0


def client_attacked_this_round(client_id: str, round_id: int) -> bool:
    runtime = client_runtime[client_id]
    return int(runtime.get("last_attack_round_id", 0)) == int(round_id)


def get_recent_attack_count(client_id: str, current_round: int,
                            window_rounds: int = TARGET_SELECTION_RECENT_ATTACK_WINDOW_ROUNDS) -> int:
    runtime = client_runtime[client_id]
    rounds = [int(r) for r in runtime.get("recent_attack_rounds", [])]
    lower = int(current_round) - int(window_rounds) + 1
    return sum(1 for r in rounds if r >= lower)


def get_client_phase_start_ts(r: redis.Redis, client_id: str, fallback_ts: float) -> float:
    raw = r.get(get_client_phase_ts_key(client_id))
    if raw is None:
        return float(fallback_ts)
    try:
        return float(raw)
    except Exception:
        return float(fallback_ts)


def get_upload_progress_score(r: redis.Redis, client_id: str, now_ts: float) -> float:
    runtime = client_runtime[client_id]
    phase_start_ts = get_client_phase_start_ts(r, client_id, now_ts)
    recent_upload_duration_s = max(get_recent_upload_duration_s(client_id), MIN_MEAN_UPLOAD_TIME_SECONDS)
    progress = (float(now_ts) - float(phase_start_ts)) / max(recent_upload_duration_s, EPS)
    return clamp(progress, 0.0, 1.5)


def is_client_upload_confirmed(client_id: str) -> bool:
    runtime = client_runtime[client_id]
    decision_phase = str(runtime.get("decision_phase", state_to_phase_label(int(runtime.get("stable_state", IDLE)))))
    decision_conf = float(runtime.get("decision_phase_confidence", runtime.get("live_phase_confidence", 0.0)))
    return decision_phase == PHASE_UPLOAD and decision_conf >= PHASE_CONFIDENCE_THRESHOLD


def is_attack_presently_active(r: Optional[redis.Redis], client_id: str, now_ts: float) -> bool:
    """Return True only during the analyzer local guard interval.

    Release control belongs fully to the intervener. The analyzer does
    not receive or process release records, and it does not maintain attack adaptation state. This guard only prevents repeated
    trigger attempts during a short local interval after an attack command is sent.
    """
    runtime = client_runtime[client_id]
    active_until = float(runtime.get("attack_active_until", 0.0) or 0.0)
    if active_until > float(now_ts):
        return True
    runtime["active_attack_id"] = ""
    runtime["attack_active_until"] = 0.0
    return False


def get_multi_attack_targets(r: redis.Redis, ranking: list, now_ts: float):
    active = {
        client_id: stats
        for client_id, stats in client_stats.items()
        if now_ts - stats["last_seen"] <= CLIENT_ACTIVITY_WINDOW_SECONDS
    }
    if not active:
        return [], ranking, "no_active_clients"

    active_round = max(int(client_runtime[c]["inferred_round_id"]) for c in active)
    same_round_clients = [
        client_id for client_id in active
        if int(client_runtime[client_id]["inferred_round_id"]) == active_round
    ]

    confirmed_upload_clients = [
        client_id for client_id in same_round_clients
        if is_client_upload_confirmed(client_id)
    ]

    ranking_map = {row["client_id"]: row for row in ranking}
    ordered = []
    for client_id in confirmed_upload_clients:
        runtime = client_runtime[client_id]
        row = dict(ranking_map.get(client_id, {"client_id": client_id, "score": 0.0}))
        row.update({
            "eligible": True,
            "active_round": int(active_round),
            "attack_active": bool(is_attack_presently_active(r, client_id, now_ts)),
            "upload_confirmed": True,
            "recent_attack_count": int(get_recent_attack_count(client_id, active_round)),
            "round_id": int(runtime.get("inferred_round_id", active_round)),
        })
        ordered.append(row)

    if len(confirmed_upload_clients) > 1:
        ordered.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)
    else:
        ordered.sort(key=lambda row: row["client_id"])

    selected = [row["client_id"] for row in ordered if not row["attack_active"]]
    reason = "multi_upload_ranked" if len(confirmed_upload_clients) > 1 else ("single_upload_confirmed" if len(confirmed_upload_clients) == 1 else "no_upload_confirmed")

    remaining_ids = {row["client_id"] for row in ordered}
    for row in ranking:
        if row["client_id"] not in remaining_ids:
            row_copy = dict(row)
            row_copy.setdefault("eligible", False)
            row_copy.setdefault("active_round", int(active_round))
            row_copy.setdefault("attack_active", False)
            row_copy.setdefault("upload_confirmed", False)
            ordered.append(row_copy)
    return selected, ordered, reason


def compute_client_ranking(now_ts: float):
    active = {
        client_id: stats
        for client_id, stats in client_stats.items()
        if now_ts - stats["last_seen"] <= CLIENT_ACTIVITY_WINDOW_SECONDS
    }
    if not active:
        return []

    max_uplink_bytes = max(stats["uplink_bytes"] for stats in active.values())
    max_uplink_packets = max(stats["uplink_packets"] for stats in active.values())
    max_downlink_bytes = max(stats["downlink_bytes"] for stats in active.values())

    ranking = []
    for client_id, stats in active.items():
        runtime = client_runtime[client_id]
        avg_iat = (sum(stats["recent_iats"]) / len(stats["recent_iats"])) if len(stats["recent_iats"]) > 0 else 1.0
        recency_score = max(0.0, 1.0 - ((now_ts - stats["last_seen"]) / CLIENT_ACTIVITY_WINDOW_SECONDS))
        iat_score = 1.0 / max(avg_iat, 1e-6)

        decision_phase = runtime.get("decision_phase", state_to_phase_label(int(runtime["stable_state"])))
        decision_phase_confidence = float(runtime.get("decision_phase_confidence", runtime["live_phase_confidence"]))

        ranking.append({
            "client_id": client_id,
            "score": round(
                0.55 * _norm(stats["uplink_bytes"], max_uplink_bytes) +
                0.20 * _norm(stats["uplink_packets"], max_uplink_packets) +
                0.10 * _norm(stats["downlink_bytes"], max_downlink_bytes) +
                0.10 * recency_score +
                0.05 * min(iat_score / 1000.0, 1.0),
                6
            ),
            "uplink_bytes": int(stats["uplink_bytes"]),
            "uplink_packets": int(stats["uplink_packets"]),
            "downlink_bytes": int(stats["downlink_bytes"]),
            "avg_iat": round(avg_iat, 6),
            "last_seen_age_s": round(now_ts - stats["last_seen"], 3),
            "inferred_round_id": int(runtime["inferred_round_id"]),
            "completed_cycle_id": int(runtime["completed_cycle_id"]),
            "last_state": int(runtime["stable_state"]),
            "cycle_stage": int(runtime["cycle_stage"]),
            "decision_phase": str(decision_phase),
            "decision_phase_confidence": round(decision_phase_confidence, 4),
            "live_phase": str(runtime["live_phase"]),
            "live_phase_confidence": round(float(runtime["live_phase_confidence"]), 4),
        })

    ranking.sort(key=lambda x: x["score"], reverse=True)
    return ranking


def refresh_target_client_if_needed(r: redis.Redis, state: int, now_ts: float) -> None:
    global last_rank_refresh_time, selected_target_client

    if now_ts - last_rank_refresh_time < RANK_REFRESH_SECONDS:
        return

    ranking = compute_client_ranking(now_ts)
    if not ranking:
        selected_target_client = None
        r.delete(TARGET_CLIENT_KEY)
        r.set(CLIENT_RANKING_KEY, json.dumps([]))
        return

    selected_targets, ordered_ranking, selection_reason = get_multi_attack_targets(r, ranking, now_ts)
    last_rank_refresh_time = now_ts

    selected_target_client = selected_targets[0] if selected_targets else None
    if selected_target_client is None:
        r.delete(TARGET_CLIENT_KEY)
    else:
        r.set(TARGET_CLIENT_KEY, selected_target_client)
    r.set(CLIENT_RANKING_KEY, json.dumps(ordered_ranking))

    top_row = ordered_ranking[0] if ordered_ranking else None
    if top_row is not None:
        top_score = float(top_row.get("round_aware_score", top_row.get("score", 0.0)))
        print(
            f"[RANK] Selected targets: {selected_targets} "
            f"reason={selection_reason} score={top_score:.4f} state={state} "
            f"inferred_round={int(top_row.get('inferred_round_id', top_row.get('round_id', 0)))} "
            f"completed={int(top_row.get('completed_cycle_id', 0))} "
            f"phase={top_row.get('decision_phase', '')} "
            f"phase_conf={float(top_row.get('decision_phase_confidence', 0.0)):.3f}",
            flush=True,
        )

    write_event("target_client_refresh", {
        "selected_target_client": selected_target_client,
        "selected_target_clients": selected_targets,
        "selection_reason": selection_reason,
        "state": state,
        "ranking_top5": ordered_ranking[:5],
    })


def get_client_state_key(client_id: str) -> str:
    return f"{CLIENT_STATE_PREFIX}{client_id}"


def get_client_phase_key(client_id: str) -> str:
    return f"{CLIENT_PHASE_PREFIX}{client_id}"


def get_client_direction_key(client_id: str) -> str:
    return f"{CLIENT_DIRECTION_PREFIX}{client_id}"


def get_client_confidence_key(client_id: str) -> str:
    return f"{CLIENT_CONFIDENCE_PREFIX}{client_id}"


def get_client_phase_ts_key(client_id: str) -> str:
    return f"{CLIENT_PHASE_TS_PREFIX}{client_id}"


def publish_client_snapshot(
    r: redis.Redis,
    client_id: str,
    stable_state: int,
    stable_confidence: float,
    live_direction_label: str,
    phase_label: str,
    packet_ts: float,
) -> None:
    r.set(get_client_state_key(client_id), int(stable_state))
    r.set(get_client_phase_key(client_id), str(phase_label))
    r.set(get_client_direction_key(client_id), str(live_direction_label))
    r.set(get_client_confidence_key(client_id), round(float(stable_confidence), 6))
    r.set(get_client_phase_ts_key(client_id), round(float(packet_ts), 6))


def _recent_upload_window_stats(runtime: dict, now_ts: float, window_s: float = UPLOAD_SCORE_WINDOW_SECONDS) -> dict:
    packets = [p for p in runtime.get("recent_feature_packets", []) if (float(now_ts) - float(p[0])) <= float(window_s)]
    if not packets:
        return {
            "outbound_pkts": 0, "inbound_pkts": 0, "outbound_bytes": 0.0, "inbound_bytes": 0.0,
            "large_outbound_pkts": 0, "large_inbound_pkts": 0, "outbound_share": 0.0, "inbound_share": 0.0,
            "tiny_control_only": True,
        }
    outbound_pkts = sum(1 for _, d, _ in packets if int(d) == 1)
    inbound_pkts = sum(1 for _, d, _ in packets if int(d) == -1)
    outbound_bytes = float(sum(p for _, d, p in packets if int(d) == 1))
    inbound_bytes = float(sum(p for _, d, p in packets if int(d) == -1))
    large_outbound_pkts = sum(1 for _, d, p in packets if int(d) == 1 and int(p) >= MIN_FAST_UPLOAD_PACKET_SIZE)
    large_inbound_pkts = sum(1 for _, d, p in packets if int(d) == -1 and int(p) >= MIN_FAST_UPLOAD_PACKET_SIZE)
    total_bytes = max(outbound_bytes + inbound_bytes, EPS)
    outbound_share = outbound_bytes / total_bytes
    inbound_share = inbound_bytes / total_bytes
    tiny_control_only = all(int(p) <= KEEPALIVE_MAX_PAYLOAD_BYTES for _, _, p in packets)
    return {
        "outbound_pkts": outbound_pkts,
        "inbound_pkts": inbound_pkts,
        "outbound_bytes": outbound_bytes,
        "inbound_bytes": inbound_bytes,
        "large_outbound_pkts": large_outbound_pkts,
        "large_inbound_pkts": large_inbound_pkts,
        "outbound_share": outbound_share,
        "inbound_share": inbound_share,
        "tiny_control_only": tiny_control_only,
    }


def _compute_packet_support_score(runtime: dict, direction: int, packet_size: int, dir_ratio: float, now_ts: float) -> float:
    # Packet-count thresholds below assume upload data arrives split across
    # several packets. Clients whose uploads arrive as fewer, larger packets
    # (different MTU/path/TCP buffering) carry the same or more data but never
    # clear a raw packet count -- each count check also accepts an equivalent
    # byte-volume path so those clients aren't structurally penalized for how
    # their traffic happens to be chunked.
    stats = _recent_upload_window_stats(runtime, now_ts)
    score = 0.0
    if int(direction) == 1 and int(packet_size) >= MIN_FAST_UPLOAD_PACKET_SIZE:
        score += 0.25
    if stats["outbound_pkts"] >= 3 or stats["outbound_bytes"] >= 3.0 * MIN_FAST_UPLOAD_PACKET_SIZE:
        score += 0.25
    if stats["outbound_pkts"] >= 5 or stats["outbound_bytes"] >= 6.0 * MIN_FAST_UPLOAD_PACKET_SIZE:
        score += 0.15
    if stats["outbound_bytes"] >= 2.0 * PHASE_MIN_PAYLOAD:
        score += 0.20
    if stats["large_outbound_pkts"] >= 2 or stats["outbound_bytes"] >= 2.0 * MIN_FAST_UPLOAD_PACKET_SIZE:
        score += 0.15
    if float(dir_ratio) >= 1.20:
        score += 0.10
    elif float(dir_ratio) >= 0.80:
        score += 0.05
    return clamp(score, 0.0, 1.0)


def _compute_phase_agreement_score(runtime: dict, stable_phase_label: str, stable_confidence: float,
                                   decision_phase_label: str, decision_phase_confidence: float) -> float:
    live_phase = str(runtime.get("live_phase", PHASE_IDLE))
    live_conf = float(runtime.get("live_phase_confidence", 0.0))
    stable_upload = stable_phase_label == PHASE_UPLOAD
    decision_upload = decision_phase_label == PHASE_UPLOAD
    live_upload = live_phase == PHASE_UPLOAD
    if stable_upload and decision_upload:
        return 1.0
    if stable_upload and float(stable_confidence) >= 0.75:
        return 0.85
    if decision_upload and float(decision_phase_confidence) >= PHASE_CONFIDENCE_THRESHOLD:
        return 0.80
    if decision_upload and float(decision_phase_confidence) >= PHASE_CONFIDENCE_THRESHOLD * 0.60:
        return 0.60
    if live_upload and live_conf >= 0.85:
        return 0.50
    return 0.0


def _compute_direction_persistence_score(runtime: dict, now_ts: float) -> float:
    # The previous version measured persistence over the last 8 *packets*
    # (recent_directions has no timestamp or size). For a client whose
    # uploads are chunked into fewer, larger packets, that fixed-count window
    # spans more wall-clock time and picks up proportionally more interleaved
    # inbound/ACK packets, breaking the "outbound streak" this score depends
    # on -- even when the client is genuinely mid-upload. Measuring over the
    # same time-boxed, byte-aware window as packet_support_score removes that
    # bias: persistence is judged by how much of the recent traffic (by
    # bytes) was outbound, not by how many discrete packets it arrived in.
    stats = _recent_upload_window_stats(runtime, now_ts)
    packets = [
        p for p in runtime.get("recent_feature_packets", [])
        if (float(now_ts) - float(p[0])) <= float(UPLOAD_SCORE_WINDOW_SECONDS)
    ]
    if not packets:
        return 0.0
    outbound_frac = stats["outbound_share"]
    trailing_outbound_bytes = 0.0
    for _, d, size in reversed(packets):
        if int(d) == 1:
            trailing_outbound_bytes += float(size)
        else:
            break
    score = 0.0
    if outbound_frac >= 0.60:
        score += 0.40
    if outbound_frac >= 0.75:
        score += 0.20
    if trailing_outbound_bytes >= 3.0 * MIN_FAST_UPLOAD_PACKET_SIZE:
        score += 0.20
    if trailing_outbound_bytes >= 5.0 * MIN_FAST_UPLOAD_PACKET_SIZE:
        score += 0.20
    return clamp(score, 0.0, 1.0)


def _compute_round_context_score(runtime: dict, inferred_round_id: int, packet_ts: float, state: int) -> float:
    score = 0.0
    if int(runtime.get("cycle_stage", 0)) == 2:
        score += 0.45
    if int(runtime.get("stable_state", IDLE)) == UPLOAD or int(state) == UPLOAD:
        score += 0.20
    if int(runtime.get("inferred_round_id", 0)) == int(inferred_round_id):
        score += 0.15
    last_validated = float(runtime.get("recent_validated_upload_ts", 0.0))
    if last_validated > 0.0 and (float(packet_ts) - last_validated) <= UPLOAD_CONTEXT_RECENCY_SECONDS:
        score += 0.20
    return clamp(score, 0.0, 1.0)


def _invalidate_upload_candidate(runtime: dict, state: int, decision_phase_label: str, packet_ts: float) -> bool:
    stats = _recent_upload_window_stats(runtime, packet_ts)
    inbound_dominant = stats["inbound_share"] >= UPLOAD_INVALIDATE_INBOUND_SHARE and stats["inbound_pkts"] >= 2
    tiny_control_only = stats["tiny_control_only"] and stats["outbound_pkts"] <= 1
    lost_phase_support = int(state) == DOWNLOAD or decision_phase_label == PHASE_DOWNLOAD
    confirmed_since = float(runtime.get("upload_confirmed_since", 0.0) or 0.0)
    stale_candidate = confirmed_since > 0.0 and (float(packet_ts) - confirmed_since) >= UPLOAD_INVALIDATE_IDLE_SECONDS and stats["outbound_pkts"] == 0
    return bool(inbound_dominant or tiny_control_only or lost_phase_support or stale_candidate)


def update_upload_trigger_state(client_id: str, state: int, stable_confidence: float, direction: int, packet_size: int,
                                dir_ratio: float, packet_ts: float, inferred_round_id: int,
                                decision_phase_label: str, decision_phase_confidence: float) -> dict:
    runtime = client_runtime[client_id]
    stable_phase_label = state_to_phase_label(int(state))
    packet_support_score = _compute_packet_support_score(runtime, direction, packet_size, dir_ratio, packet_ts)
    phase_agreement_score = _compute_phase_agreement_score(runtime, stable_phase_label, stable_confidence, decision_phase_label, decision_phase_confidence)
    direction_persistence_score = _compute_direction_persistence_score(runtime, packet_ts)
    round_context_score = _compute_round_context_score(runtime, inferred_round_id, packet_ts, state)
    upload_score = (
        0.35 * packet_support_score +
        0.30 * phase_agreement_score +
        0.20 * direction_persistence_score +
        0.15 * round_context_score
    )
    upload_candidate = upload_score >= UPLOAD_CANDIDATE_THRESHOLD
    hard_packet_evidence = packet_support_score >= 0.60
    hard_phase_evidence = phase_agreement_score >= 0.80
    upload_confirmed = bool(upload_score >= UPLOAD_CONFIRMED_THRESHOLD and (hard_packet_evidence or hard_phase_evidence))

    if _invalidate_upload_candidate(runtime, state, decision_phase_label, packet_ts):
        upload_candidate = False
        upload_confirmed = False
        runtime["upload_confirmed_since"] = 0.0
    elif upload_confirmed:
        if float(runtime.get("upload_confirmed_since", 0.0) or 0.0) <= 0.0:
            runtime["upload_confirmed_since"] = float(packet_ts)
    else:
        runtime["upload_confirmed_since"] = 0.0

    confirmed_since = float(runtime.get("upload_confirmed_since", 0.0) or 0.0)
    attackable_upload = bool(confirmed_since > 0.0 and (float(packet_ts) - confirmed_since) >= UPLOAD_ATTACKABLE_HOLD_SECONDS)

    runtime["upload_candidate"] = bool(upload_candidate)
    runtime["upload_confirmed"] = bool(upload_confirmed)
    runtime["attackable_upload"] = bool(attackable_upload)
    runtime["upload_score"] = float(upload_score)
    runtime["packet_support_score"] = float(packet_support_score)
    runtime["phase_agreement_score"] = float(phase_agreement_score)
    runtime["direction_persistence_score"] = float(direction_persistence_score)
    runtime["round_context_score"] = float(round_context_score)

    return {
        "upload_candidate": bool(upload_candidate),
        "upload_confirmed": bool(upload_confirmed),
        "attackable_upload": bool(attackable_upload),
        "upload_score": float(upload_score),
        "packet_support_score": float(packet_support_score),
        "phase_agreement_score": float(phase_agreement_score),
        "direction_persistence_score": float(direction_persistence_score),
        "round_context_score": float(round_context_score),
        "hard_packet_evidence": bool(hard_packet_evidence),
        "hard_phase_evidence": bool(hard_phase_evidence),
    }




def dispatch_attack_command(pending_context: dict) -> dict:
    """Dispatch analyzer trigger to the configured attack executor.

    Normal delay/throttle modes keep the existing intervener path.
    Poison modes send the same Upload-confirmed context to the controlled
    poison proxy, which decides whether to substitute a payload on the
    corresponding client upload stream.
    """
    mode = str(ANALYZER_ATTACK_MODE or "none").lower()
    sent = {"intervener": False, "poisoner": False}

    if mode in {"throttle", "delay", "throttle_delay", "delay_poison"}:
        delay_context = dict(pending_context)
        delay_context.setdefault("type", "attack_trigger")
        delay_context.setdefault("command", "apply_delay")
        attack_sock.sendto(
            json.dumps(delay_context).encode("utf-8"),
            (INTERVENER_HOST, INTERVENER_PORT),
        )
        sent["intervener"] = True

    if mode in {"poison", "delay_poison"}:
        poison_context = dict(pending_context)
        poison_context["type"] = "poison_trigger"
        poison_context["command"] = "apply_poison"
        poison_context["target_client"] = str(
            poison_context.get("target_client") or poison_context.get("client_id") or ""
        )
        poison_context["client_ip"] = str(
            poison_context.get("client_ip") or poison_context.get("client_id") or ""
        )
        # 8.0s was too tight for clients that only trigger sporadically (observed
        # inter-trigger gaps up to ~68s for low-confirmation-rate peers) -- see
        # matching phase_gate_max_age_s change in poison_live.py.
        poison_context["ttl_s"] = float(os.environ.get("POISON_TRIGGER_TTL_S", "90.0"))
        poison_sock.sendto(
            json.dumps(poison_context).encode("utf-8"),
            (POISONER_HOST, POISONER_PORT),
        )
        sent["poisoner"] = True

    return sent


def maybe_trigger_attack(r: redis.Redis, client_id: str, state: int, confidence: float, packet_size: int,
                         dir_ratio: float, burst_density: int, direction: int, iat: float,
                         packet_ts: float, packet_wall_time_ns: int, packet_mono_time_ns: int,
                         inferred_round_id: int, decision_phase_label: str,
                         decision_phase_confidence: float, feature_bundle: Optional[dict] = None,
                         server_ip: str = "", server_port: int = 0):
    global selected_target_client

    now = time.time()
    runtime = client_runtime[client_id]

    if not ATTACK_ENABLED:
        return {
            "action": "skip",
            "reason": "attack_disabled",
            "attack_triggered": False,
            "attack_id": "",
            "selected_target_client": "",
        }

    feature_bundle = feature_bundle or {}
    stable_phase_label = state_to_phase_label(state)

    startup_grace_active = (now - system_start_time) < STARTUP_GRACE_PERIOD_SECONDS
    cooldown_active = (now - runtime["last_attack_time"]) < ATTACK_COOLDOWN_SECONDS
    attacked_this_round = client_attacked_this_round(client_id, inferred_round_id)
    attack_active = is_attack_presently_active(r, client_id, packet_ts)

    active = {
        cid: stats for cid, stats in client_stats.items()
        if packet_ts - stats["last_seen"] <= CLIENT_ACTIVITY_WINDOW_SECONDS
    }
    active_round = max([int(client_runtime[cid]["inferred_round_id"]) for cid in active], default=int(inferred_round_id))
    confirmed_upload_clients = [
        cid for cid in active
        if int(client_runtime[cid]["inferred_round_id"]) == active_round and is_client_upload_confirmed(cid)
    ]

    ranked_upload_clients = []
    if len(confirmed_upload_clients) > 1:
        ranking_now = compute_client_ranking(packet_ts)
        ranking_map = {row["client_id"]: row for row in ranking_now}
        ranked_upload_clients = sorted(
            confirmed_upload_clients,
            key=lambda cid: float(ranking_map.get(cid, {}).get("score", 0.0)),
            reverse=True,
        )
    elif len(confirmed_upload_clients) == 1:
        ranked_upload_clients = list(confirmed_upload_clients)

    multi_upload_mode = len(confirmed_upload_clients) > 1
    is_multi_upload_eligible = client_id in ranked_upload_clients

    trigger_state = update_upload_trigger_state(
        client_id=client_id,
        state=state,
        stable_confidence=confidence,
        direction=direction,
        packet_size=packet_size,
        dir_ratio=dir_ratio,
        packet_ts=packet_ts,
        inferred_round_id=inferred_round_id,
        decision_phase_label=decision_phase_label,
        decision_phase_confidence=decision_phase_confidence,
    )

    confirmed_phase_upload = bool(trigger_state["upload_confirmed"])
    packet_upload_support = bool(trigger_state["packet_support_score"] >= 0.60)
    upload_candidate = bool(trigger_state["upload_candidate"])
    attackable_upload = bool(trigger_state["attackable_upload"])

    outbound_share = float(feature_bundle.get("outbound_share", 0.0))
    
    training_latched = bool(runtime.get("training_latched", False))
    training_start_ts = float(runtime.get("training_start_ts", 0.0) or 0.0)
    training_elapsed_s = max(0.0, float(packet_ts) - training_start_ts) if training_start_ts > 0 else 0.0

    # FIX: apply_training_latch → commit_phase_transition(UPLOAD) clears
    # training_latched on the SAME packet that releases the latch.
    # By the time we reach this point training_latched is already False.
    # Consume the one-shot flag set just before commit_latch_state() so we
    # still recognise this packet as "right after training" and allow
    # strong_outbound_upload_start to fire immediately.
    training_just_released = bool(runtime.get("training_just_released", False))
    if training_just_released:
        runtime["training_just_released"] = False  # one-shot: consume now

    recent_training_context = (
        stable_phase_label in {PHASE_TRAINING, "FIT", "TRAINING"}
        or training_latched
        or training_just_released   # true on the exact latch-release packet
    )

    first_upload_after_training = (
        recent_training_context
        and training_elapsed_s >= 0.50
        and direction == 1
        and packet_size >= PHASE_MIN_PAYLOAD
    )

    strong_outbound_upload_start = (
        first_upload_after_training
        and (
            outbound_share >= 0.50
            or dir_ratio >= 1.0
            or packet_size >= 1024
        )
    )

    confirmed_upload_phase = (
        decision_phase_label == PHASE_UPLOAD
        and direction == 1
        and packet_size >= PHASE_MIN_PAYLOAD
        # COMMENTED OUT 2026-07-20: outbound_share >= 0.70 was confirmed (via
        # analyzer_decision_log data) to be a hard ceiling real, non-rewritten
        # client traffic never crosses (observed max 0.69-0.697 across 3
        # clients, 100% of otherwise-qualifying packets rejected on this
        # clause alone) -- only the target's proxy-rewritten traffic (which
        # gets synthetic WINDOW_UPDATE credit + real server-credit suppression,
        # producing dir_ratio=100.00) can ever clear it. decision_phase,
        # direction, and packet_size above already establish this is a genuine
        # substantial outbound upload packet; this clause added nothing but
        # that structural blind spot.
        # and outbound_share >= 0.70
        # FIX: removed "and dir_ratio >= 70.0" — this gate was the fallback
        # path that finally triggered when the sliding-window dir_ratio
        # accumulated enough pure-outbound bytes to reach 70×.  That only
        # happened deep into the upload burst (the window has to shed the
        # residual inbound bytes from the preceding download phase).
        # outbound_share >= 0.70 + decision_phase_label == UPLOAD already
        # provides equivalent directional certainty without the multi-second
        # accumulation delay.  Fix A (training_just_released) is the primary
        # early-trigger path; this fix makes the confirmed_upload_phase
        # fallback also fire promptly when Fix A does not apply (e.g. when
        # the trigger arrives after the latch has already been released by a
        # prior attempt that was blocked by cooldown or baseline-not-ready).
    )

    should_trigger_attack = (
        strong_outbound_upload_start
        or confirmed_upload_phase
    )
    


    action = "skip"
    reason = "no_decision"

    if startup_grace_active:
        reason = "startup_grace_active"
    elif attack_active:
        reason = "attack_already_active"
    elif attacked_this_round:
        reason = "already_attacked_this_round"
    elif cooldown_active:
        reason = "cooldown_active"
    elif not should_trigger_attack:
        reason = "training_upload_trigger_not_confirmed"
    else:
        # Removed: baseline_ready gate (required BASELINE_WARMUP_UPLOADS=3 clean
        # completed upload episodes per client before any trigger was ever
        # allowed) and the dependent previous_upload_bytes/normal_upload_duration_s
        # skip checks. Per-client calibration isn't part of the intended design --
        # any client confirmed in UPLOAD state should be reported, full stop.
        # previous_upload_bytes/normal_upload_duration_s are kept as informational
        # fields in the dispatched context (0 if no baseline has formed yet);
        # nothing downstream requires them to be nonzero.
        previous_upload_bytes = int(runtime.get("normal_upload_bytes", 0) or 0)
        if previous_upload_bytes <= 0:
            previous_upload_bytes = int(runtime.get("previous_upload_bytes", 0) or 0)

        normal_upload_duration_s = float(runtime.get("normal_upload_duration_s", 0.0) or 0.0)

        if True:
            server_ip = str(server_ip or "").strip()
            server_port = int(server_port or 0)

            if not server_ip:
                action = "skip"
                reason = "missing_server_ip"
                analyzer_cpu_percent, analyzer_rss_mb = sample_analyzer_usage()
                return {
                    "selected_target": selected_target_client or "",
                    "stable_phase": stable_phase_label,
                    "decision_phase": decision_phase_label,
                    "decision_confidence": float(decision_phase_confidence),
                    "is_selected_target": bool(is_multi_upload_eligible),
                    "startup_grace_active": bool(startup_grace_active),
                    "cooldown_active": bool(cooldown_active),
                    "phase_upload_confirmed": bool(confirmed_phase_upload),
                    "packet_upload_support": bool(packet_upload_support),
                    "upload_candidate": bool(trigger_state["upload_candidate"]),
                    "upload_confirmed": bool(trigger_state["upload_confirmed"]),
                    "attackable_upload": bool(trigger_state["attackable_upload"]),
                    "upload_score": float(trigger_state["upload_score"]),
                    "packet_support_score": float(trigger_state["packet_support_score"]),
                    "phase_agreement_score": float(trigger_state["phase_agreement_score"]),
                    "direction_persistence_score": float(trigger_state["direction_persistence_score"]),
                    "round_context_score": float(trigger_state["round_context_score"]),
                    "action": action,
                    "reason": reason,
                    "packet_ts": float(packet_ts),
                    "packet_wall_time_ns": int(packet_wall_time_ns),
                    "packet_mono_time_ns": int(packet_mono_time_ns),
                    "analyzer_cpu_percent": float(analyzer_cpu_percent),
                    "analyzer_rss_mb": float(analyzer_rss_mb),
                    "decision_lag_ms": -1.0,
                    "trigger_publish_wall_time_ns": 0,
                    "trigger_publish_mono_time_ns": 0,
                }

            if server_port <= 0:
                action = "skip"
                reason = "missing_server_port"
                analyzer_cpu_percent, analyzer_rss_mb = sample_analyzer_usage()
                return {
                    "selected_target": selected_target_client or "",
                    "stable_phase": stable_phase_label,
                    "decision_phase": decision_phase_label,
                    "decision_confidence": float(decision_phase_confidence),
                    "is_selected_target": bool(is_multi_upload_eligible),
                    "startup_grace_active": bool(startup_grace_active),
                    "cooldown_active": bool(cooldown_active),
                    "phase_upload_confirmed": bool(confirmed_phase_upload),
                    "packet_upload_support": bool(packet_upload_support),
                    "upload_candidate": bool(trigger_state["upload_candidate"]),
                    "upload_confirmed": bool(trigger_state["upload_confirmed"]),
                    "attackable_upload": bool(trigger_state["attackable_upload"]),
                    "upload_score": float(trigger_state["upload_score"]),
                    "packet_support_score": float(trigger_state["packet_support_score"]),
                    "phase_agreement_score": float(trigger_state["phase_agreement_score"]),
                    "direction_persistence_score": float(trigger_state["direction_persistence_score"]),
                    "round_context_score": float(trigger_state["round_context_score"]),
                    "action": action,
                    "reason": reason,
                    "packet_ts": float(packet_ts),
                    "packet_wall_time_ns": int(packet_wall_time_ns),
                    "packet_mono_time_ns": int(packet_mono_time_ns),
                    "analyzer_cpu_percent": float(analyzer_cpu_percent),
                    "analyzer_rss_mb": float(analyzer_rss_mb),
                    "decision_lag_ms": -1.0,
                    "trigger_publish_wall_time_ns": 0,
                    "trigger_publish_mono_time_ns": 0,
                }

            attack_id = f"atk_{client_id}_{int(packet_ts * 1_000_000)}"

            analyzer_cpu_percent, analyzer_rss_mb = sample_analyzer_usage()
            trigger_publish_wall_time_ns = time.time_ns()
            trigger_publish_mono_time_ns = time.monotonic_ns()
            decision_lag_ms = (trigger_publish_mono_time_ns - int(packet_mono_time_ns)) / 1e6

            pending_context = {
                "attack_id": attack_id,
                "client_id": client_id,
                "client_ip": client_id,
                "server_ip": server_ip,
                "server_port": int(server_port),
                "round_id": int(inferred_round_id),
                "phase_ts": round(float(packet_ts), 6),
                "created_at": now,
                "previous_upload_bytes": int(previous_upload_bytes),
                "previous_upload_duration_s": float(normal_upload_duration_s),
                "previous_wire_upload_duration_s": float(normal_upload_duration_s),
                "previous_completed_wire_upload_duration_s": float(normal_upload_duration_s),
                "normal_upload_duration_s": float(normal_upload_duration_s),
                "baseline_upload_duration_s": float(normal_upload_duration_s),
                "baseline_upload_bytes": int(runtime.get("normal_upload_bytes", 0) or 0),
                "baseline_upload_packets": int(runtime.get("normal_upload_packets", 0) or 0),
                "mean_effective_bandwidth_mbps": float(runtime.get("mean_effective_bandwidth_mbps", 0.0) or 0.0),
                "mean_effective_upload_bandwidth_mbps": float(runtime.get("mean_effective_bandwidth_mbps", 0.0) or 0.0),
                "baseline_sample_count": int(len(runtime.get("normal_upload_samples", []))),
                "baseline_required_samples": int(BASELINE_WARMUP_UPLOADS),
                "decision_phase": decision_phase_label,
                "decision_confidence": round(float(decision_phase_confidence), 6),
                "trigger_publish_wall_time_ns": int(trigger_publish_wall_time_ns),
                "trigger_publish_mono_time_ns": int(trigger_publish_mono_time_ns),
                "decision_lag_ms": round(float(decision_lag_ms), 6),
                "analyzer_cpu_percent": round(float(analyzer_cpu_percent), 6),
                "analyzer_rss_mb": round(float(analyzer_rss_mb), 6),
                "state": int(state),
                "phase": stable_phase_label,
                "direction": int(direction),
                "payload_bytes": int(packet_size),
                "dir_ratio": round(float(dir_ratio), 6),
                "upload_score": round(float(trigger_state["upload_score"]), 6),
                "direction_persistence_score": round(float(trigger_state["direction_persistence_score"]), 6),
                "packet_support_score": round(float(trigger_state["packet_support_score"]), 6),
                "inbound_share": round(float(feature_bundle.get("inbound_share", 0.0)), 6),
                "outbound_share": round(float(feature_bundle.get("outbound_share", 0.0)), 6),
                "inbound_bytes": round(float(feature_bundle.get("inbound_bytes", 0.0)), 6),
                "outbound_bytes": round(float(feature_bundle.get("outbound_bytes", 0.0)), 6),
                "inbound_count": int(feature_bundle.get("inbound_count", 0)),
                "outbound_count": int(feature_bundle.get("outbound_count", 0)),
                "feature_bundle": feature_bundle,
                "command": "apply_delay",
                "target_client": client_id,
            }

            if ATTACK_ENABLED:
                dispatch_result = dispatch_attack_command(pending_context)
                pending_context["dispatch_intervener"] = bool(dispatch_result.get("intervener", False))
                pending_context["dispatch_poisoner"] = bool(dispatch_result.get("poisoner", False))

                r.set(TARGET_CLIENT_KEY, client_id)
                r.set(get_pending_attack_context_key(client_id), json.dumps(pending_context))

                runtime["last_attack_time"] = now
                runtime["last_attack_round_id"] = int(inferred_round_id)
                runtime["recent_attack_rounds"].append(int(inferred_round_id))
                runtime["recent_attack_timestamps"].append(float(packet_ts))
                runtime["active_attack_id"] = attack_id
                runtime["attack_active_until"] = float(packet_ts) + max(ATTACK_COOLDOWN_SECONDS, 0.25)

                if wire_upload_state[client_id].get("active") and not wire_upload_state[client_id].get("attack_id"):
                    wire_upload_state[client_id]["attack_id"] = attack_id

                action = "trigger"
                reason = "training_upload_trigger_confirmed"

                write_event("attack_trigger", {
                    "attack_id": attack_id,
                    "target_client": client_id,
                    "client_id": client_id,
                    "client_ip": client_id,
                    "server_ip": server_ip,
                    "server_port": int(server_port),
                    "inferred_round_id": int(inferred_round_id),
                    "state": state,
                    "confidence": round(confidence, 6),
                    "decision_phase_label": decision_phase_label,
                    "decision_phase_confidence": round(decision_phase_confidence, 6),
                    "payload_bytes": int(packet_size),
                    "dir_ratio": round(dir_ratio, 6),
                    "burst_density": int(burst_density),
                    "direction": int(direction),
                    "iat": float(iat),
                                    "packet_timestamp": float(packet_ts),
                    "packet_wall_time_ns": int(packet_wall_time_ns),
                    "packet_mono_time_ns": int(packet_mono_time_ns),
                    "trigger_publish_wall_time_ns": int(trigger_publish_wall_time_ns),
                    "trigger_publish_mono_time_ns": int(trigger_publish_mono_time_ns),
                    "decision_lag_ms": round(float(decision_lag_ms), 6),
                    "analyzer_cpu_percent": round(float(analyzer_cpu_percent), 6),
                    "analyzer_rss_mb": round(float(analyzer_rss_mb), 6),
                        "upload_score": round(float(trigger_state["upload_score"]), 6),
                    "packet_support_score": round(float(trigger_state["packet_support_score"]), 6),
                    "phase_agreement_score": round(float(trigger_state["phase_agreement_score"]), 6),
                    "direction_persistence_score": round(float(trigger_state["direction_persistence_score"]), 6),
                    "round_context_score": round(float(trigger_state["round_context_score"]), 6),
                })
    analyzer_cpu_percent, analyzer_rss_mb = sample_analyzer_usage()
    return {
        "selected_target": ("|".join(ranked_upload_clients) if ranked_upload_clients else (selected_target_client or "")),
        "stable_phase": stable_phase_label,
        "decision_phase": decision_phase_label,
        "decision_confidence": float(decision_phase_confidence),
        "is_selected_target": bool(is_multi_upload_eligible),
        "startup_grace_active": bool(startup_grace_active),
        "cooldown_active": bool(cooldown_active),
        "phase_upload_confirmed": bool(confirmed_phase_upload),
        "packet_upload_support": bool(packet_upload_support),
        "upload_candidate": bool(trigger_state["upload_candidate"]),
        "upload_confirmed": bool(trigger_state["upload_confirmed"]),
        "attackable_upload": bool(trigger_state["attackable_upload"]),
        "upload_score": float(trigger_state["upload_score"]),
        "packet_support_score": float(trigger_state["packet_support_score"]),
        "phase_agreement_score": float(trigger_state["phase_agreement_score"]),
        "direction_persistence_score": float(trigger_state["direction_persistence_score"]),
        "round_context_score": float(trigger_state["round_context_score"]),
        "action": action,
        "reason": reason,
        "packet_ts": float(packet_ts),
        "packet_wall_time_ns": int(packet_wall_time_ns),
        "packet_mono_time_ns": int(packet_mono_time_ns),
        "analyzer_cpu_percent": float(analyzer_cpu_percent),
        "analyzer_rss_mb": float(analyzer_rss_mb),
        "decision_lag_ms": float(locals().get("decision_lag_ms", -1.0)),
        "trigger_publish_wall_time_ns": int(locals().get("trigger_publish_wall_time_ns", 0)),
        "trigger_publish_mono_time_ns": int(locals().get("trigger_publish_mono_time_ns", 0)),
    }


def classify_transfer_evidence(direction: int, payload_bytes: int, density: int):
    download_like = direction == -1 and payload_bytes >= PHASE_MIN_PAYLOAD and density >= TRAINING_LATCH_MIN_DOWNLOAD_PACKETS
    upload_like = direction == 1 and payload_bytes >= PHASE_MIN_PAYLOAD and density >= TRAINING_LATCH_MIN_UPLOAD_PACKETS
    control_like = payload_bytes <= TRAINING_LATCH_MAX_CONTROL_PAYLOAD
    return download_like, upload_like, control_like


def apply_training_latch(client_id: str, ts: float, payload_bytes: int, direction: int, density: int,
                         filtered_iat: float, prev_stable_state: int, stable_state: int,
                         live_phase_label: str, live_phase_confidence: float,
                         adaptive_phase_label: str, adaptive_phase_scores: dict,
                         raw_state: int, raw_confidence: float,
                         wall_time_ns: int, mono_time_ns: int,
                         feature_bundle: dict = None):
    """Latch TRAINING during local-compute silence without directly owning
    final phase authority.

    This function now proposes TRAINING or UPLOAD transitions and commits them
    through the unified transition engine. It no longer writes stable_state,
    candidate_state, or belief directly.
    """
    runtime = client_runtime[client_id]
    feature_bundle = feature_bundle or {}

    download_like, upload_like, control_like = classify_transfer_evidence(direction, payload_bytes, density)
    dir_ratio = float(feature_bundle.get("dir_ratio", 0.0))
    inbound_share = float(feature_bundle.get("inbound_share", 0.0))
    outbound_share = float(feature_bundle.get("outbound_share", 0.0))

    upload_start_evidence = has_upload_start_evidence(direction, payload_bytes, feature_bundle)

    if download_like:
        record_download_gap(runtime, ts)
        runtime["last_download_like_ts"] = ts
    if upload_like:
        runtime["last_upload_like_ts"] = ts

    last_download_like_ts = float(runtime.get("last_download_like_ts", 0.0))
    last_upload_like_ts = float(runtime.get("last_upload_like_ts", 0.0))
    download_gap_s = (ts - last_download_like_ts) if last_download_like_ts > 0.0 else float("inf")
    upload_gap_s = (ts - last_upload_like_ts) if last_upload_like_ts > 0.0 else float("inf")

    direction_unknown = (direction not in (-1, 1)) or (live_phase_label == PHASE_IDLE)
    # TRAINING may be inferred from silence/neutral traffic only.
    # A real inbound packet (direction=-1 with transfer-size payload) must not
    # create or hold TRAINING even if a silence/gap gate was previously met.
    last_direction_label = str(live_phase_label or "unknown").lower()
    direction_is_silent_or_unknown = (
        int(direction) == 0
        or last_direction_label == "unknown"
    )
    inbound_transfer_packet = (
        int(direction) == -1
        and int(payload_bytes) >= PHASE_MIN_PAYLOAD
    )
    gap_is_sufficient, gap_meta = is_download_gap_sufficient(runtime, download_gap_s)

    download_gap_samples = [
        float(g)
        for g in runtime.get("recent_download_gaps", [])
        if float(g) > 0.0 and np.isfinite(float(g))
    ]
    if len(download_gap_samples) >= 4:
        small_center, _large_center = fit_two_log_gap_regimes(download_gap_samples)
        if small_center is not None:
            small_gap_regime_s = float(np.exp(small_center))
            dynamic_training_gap_s = max(float(np.percentile(download_gap_samples, 75)), 3.0 * small_gap_regime_s)
        else:
            dynamic_training_gap_s = float(np.percentile(download_gap_samples, 75))
    elif download_gap_samples:
        dynamic_training_gap_s = float(np.percentile(download_gap_samples, 75))
    else:
        dynamic_training_gap_s = float(max(filtered_iat, 0.0))

    def commit_latch_state(to_state: int, source: str, confidence_value: float, force: bool = False):
        decision = decide_phase_transition(
            client_id=client_id,
            from_state=int(runtime.get("stable_state", stable_state)),
            to_state=int(to_state),
            source=source,
            confidence=confidence_value,
            direction=direction,
            payload_bytes=payload_bytes,
            feature_bundle=feature_bundle,
            ts=ts,
            force=force,
        )
        return commit_phase_transition(
            client_id=client_id,
            decision=decision,
            confidence=confidence_value,
            ts=ts,
            wall_time_ns=wall_time_ns,
            mono_time_ns=mono_time_ns,
            direction=direction,
            payload_bytes=payload_bytes,
            feature_bundle=feature_bundle,
        )[0]

    # Model agnostic compressed-boundary recovery.
    #
    # Some small/fast clients can begin a short upload before the analyzer has
    # emitted the intervening TRAINING segment.  The raw packet direction then
    # proposes DOWNLOAD->UPLOAD, which the protocol guard correctly forbids.
    # If we simply ignore that outbound evidence, the next inbound model
    # download can arrive while the client is still classified as TRAINING,
    # causing TRAINING->DOWNLOAD to be blocked and one client round to be
    # merged.
    #
    # Recovery rule: when a meaningful outbound packet appears while the client
    # is still in DOWNLOAD, and this DOWNLOAD phase has already seen at least
    # one real inbound model packet, first commit a short TRAINING boundary.
    # The next outbound packet can then release TRAINING->UPLOAD through the
    # existing latch path.  This preserves the protocol order
    # DOWNLOAD->TRAINING->UPLOAD without adding model-specific thresholds.
    download_phase_start_ts = float(runtime.get("stable_state_since", 0.0) or 0.0)
    last_phase_download_ts = (
        last_download_like_ts
        if (last_download_like_ts > 0.0
            and download_phase_start_ts > 0.0
            and last_download_like_ts >= download_phase_start_ts)
        else 0.0
    )

    early_upload_while_download = (
        int(runtime.get("stable_state", stable_state)) == DOWNLOAD
        and int(prev_stable_state) == DOWNLOAD
        and int(runtime.get("cycle_stage", 0)) == 0
        and bool(upload_start_evidence)
        and last_phase_download_ts > 0.0
    )

    if early_upload_while_download:
        runtime["training_latched"] = True
        runtime["training_start_ts"] = float(ts)
        runtime["early_upload_seen_while_download"] = True
        runtime["early_upload_seen_ts"] = float(ts)
        raw_confidence = max(float(raw_confidence), 0.90)
        stable_state = commit_latch_state(
            TRAINING,
            source="download_to_training_compressed_before_upload",
            confidence_value=raw_confidence,
            force=True,
        )
        raw_state = stable_state
        adaptive_phase_label = PHASE_TRAINING
        adaptive_phase_scores[PHASE_TRAINING] = max(float(adaptive_phase_scores.get(PHASE_TRAINING, 0.0)), 1.0)
        live_phase_label = PHASE_TRAINING
        live_phase_confidence = max(float(live_phase_confidence), 0.85)

        write_event("compressed_download_to_training_before_upload", {
            "client_id": client_id,
            "reason": "outbound_upload_evidence_seen_before_training_boundary",
            "from_state": int(DOWNLOAD),
            "to_state": int(TRAINING),
            "cycle_stage": int(runtime.get("cycle_stage", 0)),
            "payload_bytes": int(payload_bytes),
            "direction": int(direction),
            "dir_ratio": float(dir_ratio),
            "inbound_share": float(inbound_share),
            "outbound_share": float(outbound_share),
            "short_outbound_share": float(feature_bundle.get("short_outbound_share", 0.0)),
            "short_outbound_count": int(feature_bundle.get("short_outbound_count", 0)),
            "last_phase_download_ts": float(last_phase_download_ts),
            "download_phase_start_ts": float(download_phase_start_ts),
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(wall_time_ns),
            "packet_mono_time_ns": int(mono_time_ns),
        })
        return raw_state, raw_confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores

    if runtime["training_latched"]:
        strong_upload_like = (
            upload_start_evidence
            or (upload_like and not control_like)
        )

        if strong_upload_like:
            # FIX: stamp the flag BEFORE commit_latch_state(), which internally
            # calls commit_phase_transition(to_state=UPLOAD) and unconditionally
            # sets runtime["training_latched"] = False there.  By the time
            # maybe_trigger_attack() runs on this same packet, training_latched
            # is already False and recent_training_context would be False —
            # blocking strong_outbound_upload_start from firing.
            # training_just_released survives across the commit and lets
            # maybe_trigger_attack() fire the trigger on this first upload
            # packet rather than waiting for confirmed_upload_phase which
            # requires dir_ratio >= 70 and only fires late in the burst.
            runtime["training_just_released"] = True
            runtime["early_upload_seen_while_download"] = False
            runtime["early_upload_seen_ts"] = 0.0
            raw_confidence = max(float(raw_confidence), 0.95)
            stable_state = commit_latch_state(
                UPLOAD,
                source="training_latch_release_upload",
                confidence_value=raw_confidence,
                force=False,
            )
            raw_state = stable_state
            adaptive_phase_label = state_to_phase_label(stable_state)
            adaptive_phase_scores[adaptive_phase_label] = max(float(adaptive_phase_scores.get(adaptive_phase_label, 0.0)), 1.0)
            live_phase_label = adaptive_phase_label
            live_phase_confidence = max(float(live_phase_confidence), 0.95)

            write_event("training_latch_release", {
                "client_id": client_id,
                "reason": "upload_detected" if not upload_start_evidence else "upload_detected_early_override",
                "packet_timestamp": float(ts),
                "packet_wall_time_ns": int(wall_time_ns),
                "packet_mono_time_ns": int(mono_time_ns),
                "upload_gap_s": float(upload_gap_s),
                "dir_ratio": float(dir_ratio),
                "outbound_share": float(outbound_share),
                "payload_bytes": int(payload_bytes),
                "direction": int(direction),
                "upload_start_evidence": bool(upload_start_evidence),
            })
            return raw_state, raw_confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores

        if int(runtime.get("cycle_stage", 0)) >= 2:
            runtime["training_latched"] = False
            runtime["training_start_ts"] = 0.0
            write_event("training_latch_release", {
                "client_id": client_id,
                "reason": "cycle_stage_advanced",
                "cycle_stage": int(runtime.get("cycle_stage", 0)),
                "packet_timestamp": float(ts),
                "packet_wall_time_ns": int(wall_time_ns),
                "packet_mono_time_ns": int(mono_time_ns),
            })
        else:
            if inbound_transfer_packet or download_like:
                # Do not force TRAINING across real inbound DOWNLOAD evidence.
                # This prevents rows such as direction=-1 with stable/decision
                # phase TRAINING.  The packet-driven transition path and
                # training fast-exit can then evaluate the inbound evidence
                # without the latch overwriting it back to TRAINING.
                runtime["training_latched"] = False
                runtime["training_start_ts"] = 0.0
                runtime["last_training_latch_log_ts"] = 0.0
                write_event("training_latch_hold_blocked_by_inbound", {
                    "client_id": client_id,
                    "reason": "inbound_transfer_packet_seen_while_latched",
                    "direction": int(direction),
                    "payload_bytes": int(payload_bytes),
                    "download_like": bool(download_like),
                    "inbound_share": float(inbound_share),
                    "outbound_share": float(outbound_share),
                    "dir_ratio": float(dir_ratio),
                    "packet_timestamp": float(ts),
                    "packet_wall_time_ns": int(wall_time_ns),
                    "packet_mono_time_ns": int(mono_time_ns),
                })
                return raw_state, raw_confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores

            training_hold_allowed = (
                direction_is_silent_or_unknown
                and not download_like
                and not upload_like
                and (control_like or int(payload_bytes) <= TRAINING_LATCH_MAX_CONTROL_PAYLOAD)
            )

            if not training_hold_allowed:
                runtime["training_latched"] = False
                runtime["training_start_ts"] = 0.0
                runtime["last_training_latch_log_ts"] = 0.0
                write_event("training_latch_hold_blocked_by_direction", {
                    "client_id": client_id,
                    "reason": "non_silent_direction_seen_while_latched",
                    "direction": int(direction),
                    "payload_bytes": int(payload_bytes),
                    "download_like": bool(download_like),
                    "upload_like": bool(upload_like),
                    "control_like": bool(control_like),
                    "direction_is_silent_or_unknown": bool(direction_is_silent_or_unknown),
                    "packet_timestamp": float(ts),
                    "packet_wall_time_ns": int(wall_time_ns),
                    "packet_mono_time_ns": int(mono_time_ns),
                })
                return raw_state, raw_confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores

            raw_confidence = max(float(raw_confidence), 0.90)
            stable_state = commit_latch_state(
                TRAINING,
                source="training_latch_hold",
                confidence_value=raw_confidence,
                force=True,
            )
            raw_state = stable_state
            adaptive_phase_label = PHASE_TRAINING
            adaptive_phase_scores[PHASE_TRAINING] = max(float(adaptive_phase_scores.get(PHASE_TRAINING, 0.0)), 1.0)
            live_phase_label = PHASE_TRAINING
            live_phase_confidence = max(float(live_phase_confidence), 0.85)
            return raw_state, raw_confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores

    download_window_still_active = (
        inbound_share >= 0.55
        and outbound_share <= 0.35
        and dir_ratio <= 30.0
        and density >= TRAINING_LATCH_MIN_DOWNLOAD_PACKETS
    )

    # Phase-scoped download recency check.
    #
    # last_download_like_ts is never reset when a new DOWNLOAD phase starts,
    # so it can carry a stale timestamp from a previous round's model download
    # or from a server upload-ACK that happened before the stable state
    # committed to DOWNLOAD.  Using that stale timestamp gives a false sense
    # of recency:  recent_download_packet becomes False immediately (because
    # the stale ts is already > 0.25 s old), and the very first direction=0
    # keepalive that arrives fires the training latch even though no real
    # model download has taken place in the current phase.
    #
    # The fix: only count download-like timestamps that are at or after the
    # moment stable_state transitioned into DOWNLOAD.  If no large inbound
    # packet has arrived since we entered DOWNLOAD, there is no model to
    # train on and the latch must not fire.
    download_phase_start_ts = float(runtime.get("stable_state_since", 0.0))
    last_phase_download_ts = (
        last_download_like_ts
        if (last_download_like_ts > 0.0
            and download_phase_start_ts > 0.0
            and last_download_like_ts >= download_phase_start_ts)
        else 0.0
    )

    if prev_stable_state == DOWNLOAD and last_phase_download_ts <= 0.0:
        # No large inbound packet has arrived in this DOWNLOAD phase at all.
        # A real model broadcast must be received before training can start.
        # Return without firing the latch regardless of any other condition.
        return (raw_state, raw_confidence, stable_state,
                live_phase_label, live_phase_confidence,
                adaptive_phase_label, adaptive_phase_scores)

    # Timing-free training latch: once the current DOWNLOAD phase has seen a
    # real inbound model packet, TRAINING begins on the first neutral/control
    # packet that is not itself download or upload evidence.
    should_enter_training = (
        prev_stable_state == DOWNLOAD
        and not download_like
        and not upload_like
        and control_like
        and direction_is_silent_or_unknown
        and not inbound_transfer_packet
        and not download_window_still_active
    )

    if should_enter_training:
        runtime["training_latched"] = True
        runtime["training_start_ts"] = ts
        raw_confidence = max(float(raw_confidence), 0.90)
        stable_state = commit_latch_state(
            TRAINING,
            source="training_latch_start",
            confidence_value=raw_confidence,
            force=False,
        )
        raw_state = stable_state
        adaptive_phase_label = PHASE_TRAINING
        adaptive_phase_scores[PHASE_TRAINING] = max(float(adaptive_phase_scores.get(PHASE_TRAINING, 0.0)), 1.0)
        live_phase_label = PHASE_TRAINING
        live_phase_confidence = max(float(live_phase_confidence), 0.85)

        write_event("training_latch_start", {
            "client_id": client_id,
            "from_state": int(prev_stable_state),
            "to_state": int(TRAINING),
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(wall_time_ns),
            "packet_mono_time_ns": int(mono_time_ns),
            "payload_bytes": int(payload_bytes),
            "direction": int(direction),
            "iat": float(filtered_iat),
            "download_gap_s": float(download_gap_s),
            "dynamic_training_gap_s": float(dynamic_training_gap_s),
            **gap_meta,
        })

    return raw_state, raw_confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores


def maybe_apply_upload_fast_exit(
    client_id: str, stable_state: int, raw_state: int, confidence: float,
    live_phase_label: str, adaptive_phase_label: str,
    ts: float, wall_time_ns: int, mono_time_ns: int,
    direction: int = 0, payload_bytes: int = 0, feature_bundle: Optional[dict] = None,
) -> int:
    """Consensus fast-exit from UPLOAD to DOWNLOAD.

    The normal UPLOAD->DOWNLOAD promotion path in update_stable_state requires:
      - stable_dwell >= MIN_STATE_DWELL_SECONDS[UPLOAD] (0.10 s after Fix 3)
      - candidate_count >= 2 with current inbound DOWNLOAD evidence
      - strong_download_evidence confirmed

    In practice, when the upload burst is short and the server aggregates
    quickly, the download burst begins before some of these gates open.
    The result is that stable=UPLOAD persists for 40-70 packets while raw,
    live, and adaptive all already indicate DOWNLOAD.

    This function fires when all three independent signals agree on DOWNLOAD
    for TRAINING_FAST_EXIT_MIN_PACKETS consecutive packets, bypassing the
    dwell and duration requirements for the boundary case.

    Returns the (possibly updated) stable_state value.
    """
    runtime = client_runtime[client_id]

    # Only allow fast-exit when the client has completed the full
    # DOWNLOAD->TRAINING->UPLOAD sequence (cycle_stage == 2).
    # If stage is 0 or 1, a UPLOAD->DOWNLOAD transition here would be
    # premature — the client has not yet earned a round boundary.
    if stable_state != UPLOAD or int(runtime.get("cycle_stage", 0)) != 2:
        runtime["upload_exit_download_streak"] = 0
        return stable_state

    evidence_confirmed = has_upload_to_download_evidence(
        UPLOAD, direction, payload_bytes, feature_bundle
    )
    download_consensus = (
        evidence_confirmed
        and (raw_state == DOWNLOAD or live_phase_label == PHASE_DOWNLOAD or adaptive_phase_label == PHASE_DOWNLOAD)
        and confidence >= BOUNDARY_MIN_CONFIDENCE
    )

    if not evidence_confirmed and raw_state == DOWNLOAD:
        write_protocol_transition_block(
            client_id=client_id,
            from_state=UPLOAD,
            to_state=DOWNLOAD,
            reason="upload_fast_exit_download_evidence_missing",
            confidence=confidence,
            direction=direction,
            payload_bytes=payload_bytes,
            ts=ts,
            wall_time_ns=wall_time_ns,
            mono_time_ns=mono_time_ns,
            extra={
                "live_phase_label": live_phase_label,
                "adaptive_phase_label": adaptive_phase_label,
                "inbound_share": float((feature_bundle or {}).get("inbound_share", 0.0)),
                "outbound_share": float((feature_bundle or {}).get("outbound_share", 0.0)),
                "dir_ratio": float((feature_bundle or {}).get("dir_ratio", 0.0)),
                "burst_density": int((feature_bundle or {}).get("burst_density", 0)),
            },
        )

    if download_consensus:
        runtime["upload_exit_download_streak"] = (
            int(runtime.get("upload_exit_download_streak", 0)) + 1
        )
    else:
        runtime["upload_exit_download_streak"] = 0
        return stable_state

    streak = int(runtime.get("upload_exit_download_streak", 0))
    if streak < UPLOAD_TO_DOWNLOAD_STATE_HOLD_PACKETS:
        return stable_state

    prev_stable = int(runtime["stable_state"])
    decision = decide_phase_transition(
        client_id=client_id,
        from_state=prev_stable,
        to_state=DOWNLOAD,
        source="upload_fast_exit",
        confidence=confidence,
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
        ts=ts,
    )
    committed_state, _changed = commit_phase_transition(
        client_id=client_id,
        decision=decision,
        confidence=confidence,
        ts=ts,
        wall_time_ns=wall_time_ns,
        mono_time_ns=mono_time_ns,
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
    )
    runtime["upload_exit_download_streak"] = 0

    write_event("upload_fast_exit", {
        "client_id": client_id,
        "from_state": prev_stable,
        "to_state": int(DOWNLOAD),
        "download_streak": int(streak),
        "confidence": round(float(confidence), 6),
        "live_phase_label": live_phase_label,
        "adaptive_phase_label": adaptive_phase_label,
        "packet_timestamp": float(ts),
        "packet_wall_time_ns": int(wall_time_ns),
        "packet_mono_time_ns": int(mono_time_ns),
    })
    print(
        f"[FAST-EXIT-UL] pkt_ts={ts:.6f} client={client_id} "
        f"from=UPLOAD to=DOWNLOAD streak={streak} conf={confidence:.3f} "
        f"live={live_phase_label} adaptive={adaptive_phase_label}",
        flush=True,
    )
    return committed_state


def maybe_apply_training_fast_exit(
    client_id: str, stable_state: int, raw_state: int, confidence: float,
    live_phase_label: str, adaptive_phase_label: str,
    ts: float, wall_time_ns: int, mono_time_ns: int,
    direction: int = 0, payload_bytes: int = 0, feature_bundle: Optional[dict] = None,
) -> int:
    """Consensus fast-exit from TRAINING.

    Fires when raw HMM state, live phase, and HMM confidence all agree on
    the same non-TRAINING state for TRAINING_FAST_EXIT_MIN_PACKETS
    consecutive packets.  This bypasses:

      - the training_to_download_forbidden hard block in update_stable_state
      - the candidate duration / dwell requirements
      - the training latch (which resets candidate_count on every latched
        packet, preventing normal promotion from ever accumulating enough
        evidence while the latch is active)

    The streaks are maintained on fields that the training latch never
    touches, so they accumulate correctly even while the latch is forcing
    stable=TRAINING on every packet.

    Returns the (possibly updated) stable_state value.
    """
    runtime = client_runtime[client_id]

    # Only allow fast-exit when the client is genuinely mid-training,
    # i.e. cycle_stage == 1 (DOWNLOAD->TRAINING transition was recorded
    # but TRAINING->UPLOAD has not yet fired).  If stage == 0 or 2, a
    # training fast-exit would produce an out-of-order transition:
    #   stage 0: TRAINING->DOWNLOAD would skip the UPLOAD phase entirely
    #   stage 2: client is already in UPLOAD — fast-exit into TRAINING or
    #            UPLOAD here creates the spurious upload->fit boundary
    #            observed in the phase log.
    if stable_state != TRAINING or int(runtime.get("cycle_stage", 0)) != 1:
        runtime["training_exit_download_streak"] = 0
        runtime["training_exit_upload_streak"] = 0
        return stable_state

    download_consensus = (
        raw_state == DOWNLOAD
        and live_phase_label == PHASE_DOWNLOAD
        and confidence >= TRAINING_FAST_EXIT_MIN_CONFIDENCE
    )
    upload_evidence = has_upload_start_evidence(direction, payload_bytes, feature_bundle)
    upload_consensus = (
        upload_evidence
        and (raw_state == UPLOAD or live_phase_label == PHASE_UPLOAD or adaptive_phase_label == PHASE_UPLOAD)
        and confidence >= BOUNDARY_MIN_CONFIDENCE
    )

    if download_consensus:
        runtime["training_exit_download_streak"] = (
            int(runtime.get("training_exit_download_streak", 0)) + 1
        )
        runtime["training_exit_upload_streak"] = 0
    elif upload_consensus:
        runtime["training_exit_upload_streak"] = (
            int(runtime.get("training_exit_upload_streak", 0)) + 1
        )
        runtime["training_exit_download_streak"] = 0
    else:
        runtime["training_exit_download_streak"] = 0
        runtime["training_exit_upload_streak"] = 0
        return stable_state

    dl_streak = int(runtime.get("training_exit_download_streak", 0))
    ul_streak = int(runtime.get("training_exit_upload_streak", 0))

    if dl_streak >= TRAINING_FAST_EXIT_MIN_PACKETS:
        exit_state = DOWNLOAD
    elif ul_streak >= 1:
        exit_state = UPLOAD
    else:
        return stable_state

    prev_stable = int(runtime["stable_state"])
    decision = decide_phase_transition(
        client_id=client_id,
        from_state=prev_stable,
        to_state=exit_state,
        source="training_fast_exit",
        confidence=confidence,
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
        ts=ts,
    )
    committed_state, changed = commit_phase_transition(
        client_id=client_id,
        decision=decision,
        confidence=confidence,
        ts=ts,
        wall_time_ns=wall_time_ns,
        mono_time_ns=mono_time_ns,
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
    )
    if not changed:
        runtime["training_exit_download_streak"] = 0
        runtime["training_exit_upload_streak"] = 0
        return stable_state

    runtime["training_exit_download_streak"] = 0
    runtime["training_exit_upload_streak"] = 0

    write_event("training_fast_exit", {
        "client_id": client_id,
        "from_state": prev_stable,
        "to_state": int(exit_state),
        "download_streak": int(dl_streak),
        "upload_streak": int(ul_streak),
        "confidence": round(float(confidence), 6),
        "live_phase_label": live_phase_label,
        "packet_timestamp": float(ts),
        "packet_wall_time_ns": int(wall_time_ns),
        "packet_mono_time_ns": int(mono_time_ns),
    })
    print(
        f"[FAST-EXIT] pkt_ts={ts:.6f} client={client_id} "
        f"from={prev_stable} to={exit_state} "
        f"dl_streak={dl_streak} ul_streak={ul_streak} conf={confidence:.3f} "
        f"live={live_phase_label}",
        flush=True,
    )
    return committed_state



def update_client_stats(client_id: str, direction: int, payload_bytes: int, iat: float, stable_state: int, ts: float) -> None:
    """Update lightweight per client traffic counters used by ranking, pruning, and dashboard views.

    This function does not modify phase, round, HMM, or attack state. It only
    maintains recent activity statistics so the analyzer can keep existing
    decision logic working after removing analyzer side attack adaptation.
    """
    stats = client_stats[client_id]
    payload = max(int(payload_bytes or 0), 0)
    direction = int(direction or 0)
    ts = float(ts or time.time())

    stats["last_seen"] = ts
    stats["last_state_seen"] = int(stable_state)

    try:
        if iat is not None:
            stats["recent_iats"].append(float(max(iat, 0.0)))
    except Exception:
        pass

    if direction == 1:
        stats["uplink_bytes"] = float(stats.get("uplink_bytes", 0.0)) + float(payload)
        stats["uplink_packets"] = int(stats.get("uplink_packets", 0)) + 1
    elif direction == -1:
        stats["downlink_bytes"] = float(stats.get("downlink_bytes", 0.0)) + float(payload)
        stats["downlink_packets"] = int(stats.get("downlink_packets", 0)) + 1

def write_training_latch_interval_row(client_id: str, now_ts: float, reason: str = "training_latch_interval") -> None:
    """Write a synthetic TRAINING row during silent local computation.

    This interval is logged only as an event. It is deliberately not written
    to shadow_dataset_<RUN_TS>.csv or analyzer_decision_log_<RUN_TS>.csv, because
    synthetic TRAINING rows can create false transition-quality artifacts.
    """
    runtime = client_runtime[client_id]

    # Guard against stale synthetic TRAINING rows after the client has already
    # moved out of TRAINING. Without this guard, a delayed latch interval row
    # can appear after a real TRAINING -> UPLOAD transition and create a false
    # UPLOAD -> TRAINING transition in the decision log.
    if int(runtime.get("stable_state", IDLE)) != TRAINING or not bool(runtime.get("training_latched", False)):
        return

    stats = client_stats[client_id]
    last_seen = float(stats.get("last_seen", now_ts) or now_ts)
    silence_iat = max(0.0, float(now_ts) - last_seen)

    wall_ns = int(time.time_ns())
    mono_ns = int(time.monotonic_ns())
    usage_cpu, usage_rss = sample_analyzer_usage()
    round_id = int(runtime.get("inferred_round_id", 1))
    cycle_stage = int(runtime.get("cycle_stage", 1))
    completed_cycle_id = int(runtime.get("completed_cycle_id", 0))

    normalized = {
        "timestamp": float(now_ts),
        "wall_time_ns": wall_ns,
        "mono_time_ns": mono_ns,
        "src_ip": str(runtime.get("phase_record_src_ip", "") or client_id),
        "dst_ip": str(runtime.get("phase_record_dst_ip", "") or "unknown"),
        "client_id": client_id,
        "payload_bytes": 0,
        "wire_bytes": 0,
        "direction": 0,
        "iat": float(silence_iat),
    }

    feature_bundle = {
        "dir_ratio": 0.0,
        "dir_balance": 0.0,
        "burst_density": 0,
        "inbound_density": 0,
        "outbound_density": 0,
        "inbound_bytes": 0.0,
        "outbound_bytes": 0.0,
        "inbound_count": 0,
        "outbound_count": 0,
        "inbound_share": 0.0,
        "outbound_share": 0.0,
    }

    scores = {
        PHASE_IDLE: 0.0,
        PHASE_DOWNLOAD: 0.0,
        PHASE_TRAINING: 1.0,
        PHASE_UPLOAD: 0.0,
    }

    # Synthetic TRAINING intervals are intentionally event-only.
    # They are not written through write_row() because that would insert
    # payload_bytes=0 / direction=0 TRAINING rows into the decision log and
    # can create false UPLOAD -> TRAINING artifacts in transition-quality analysis.


    write_event("training_latch_interval_row", {
        "client_id": client_id,
        "reason": reason,
        "packet_timestamp": float(now_ts),
        "packet_wall_time_ns": wall_ns,
        "packet_mono_time_ns": mono_ns,
        "silence_iat": float(silence_iat),
        "dir_ratio": 0.0,
        "inferred_round_id": round_id,
        "cycle_stage": cycle_stage,
    })


def prune_stale_clients(now_ts: float) -> None:
    """Prune only volatile target state for clients that have not produced traffic recently.

    This function intentionally does not delete client_runtime or client_stats entries,
    because phase and round finalization still need that history. It only clears
    selection and attack flags for stale clients so timeout processing remains safe.
    """
    global selected_target_client

    stale_clients = []
    for client_id, stats in list(client_stats.items()):
        last_seen = float(stats.get("last_seen", 0.0) or 0.0)
        if last_seen <= 0.0:
            continue
        if float(now_ts) - last_seen >= CLIENT_IDLE_TIMEOUT_SECONDS:
            stale_clients.append(client_id)

    for client_id in stale_clients:
        runtime = client_runtime[client_id]
        runtime["upload_candidate"] = False
        runtime["upload_confirmed"] = False
        runtime["attackable_upload"] = False
        runtime["active_attack_id"] = ""
        runtime["attack_active_until"] = 0.0

        if selected_target_client == client_id:
            selected_target_client = None

def check_for_training_silence(r: redis.Redis, now_ts: float) -> None:
    for client_id, stats in list(client_stats.items()):
        runtime = client_runtime[client_id]

        last_seen = float(stats.get("last_seen", 0.0))
        if last_seen <= 0.0:
            continue

        if runtime["training_latched"]:
            last_log_ts = float(runtime.get("last_training_latch_log_ts", 0.0))

            recent_iats = [
                float(x)
                for x in runtime.get("recent_iats", [])
                if float(x) > 0.0 and np.isfinite(float(x))
            ]

            mean_iat = (
                float(np.mean(recent_iats))
                if recent_iats
                else TRAINING_LATCH_LOG_INTERVAL_SECONDS
            )

            adaptive_log_interval_s = min(
                1.0,
                max(0.05, mean_iat)
            )

            if now_ts - last_log_ts >= adaptive_log_interval_s:
                runtime["last_training_latch_log_ts"] = now_ts
                write_training_latch_interval_row(
                    client_id=client_id,
                    now_ts=now_ts,
                    reason="training_latch_interval",
                )
            continue

        silence_age = now_ts - last_seen

        last_download_like_ts = float(runtime.get("last_download_like_ts", 0.0))
        download_gap_s = (now_ts - last_download_like_ts) if last_download_like_ts > 0.0 else float("inf")

        gap_is_sufficient, gap_meta = is_download_gap_sufficient(runtime, download_gap_s)

        # This timeout path has no current packet, so the immediate direction is
        # silence/neutral (0).  Keep the explicit direction guard so DOWNLOAD
        # -> TRAINING cannot be forced from an active non-neutral packet path.
        last_direction_label = str(runtime.get("live_direction_label", "unknown") or "unknown").lower()
        direction = 0
        direction_is_silent_or_unknown = (
            direction == 0
            or last_direction_label == "unknown"
        )

        should_force_training = (
            runtime["stable_state"] == DOWNLOAD
            and direction_is_silent_or_unknown
            and silence_age >= TRAINING_SILENCE_TIMEOUT_SECONDS
            and gap_is_sufficient
        )

        if should_force_training:
            runtime["training_latched"] = True
            runtime["training_start_ts"] = now_ts
            decision = decide_phase_transition(
                client_id=client_id,
                from_state=int(runtime.get("stable_state", DOWNLOAD)),
                to_state=TRAINING,
                source="training_silence_timeout",
                confidence=0.90,
                direction=0,
                payload_bytes=0,
                feature_bundle={},
                ts=now_ts,
                force=True,
            )
            commit_phase_transition(
                client_id=client_id,
                decision=decision,
                confidence=0.90,
                ts=now_ts,
                wall_time_ns=int(time.time_ns()),
                mono_time_ns=int(time.monotonic_ns()),
                direction=0,
                payload_bytes=0,
                feature_bundle={},
            )
            runtime["live_phase"] = PHASE_TRAINING
            runtime["live_phase_confidence"] = 0.90
            runtime["live_direction_label"] = "unknown"
            runtime["last_training_latch_log_ts"] = now_ts
            write_training_latch_interval_row(
                client_id=client_id,
                now_ts=now_ts,
                reason="training_latch_start_silence",
            )

            phase_log_normalized = {
                "timestamp": float(now_ts),
                "wall_time_ns": int(time.time_ns()),
                "mono_time_ns": int(time.monotonic_ns()),
                "src_ip": str(client_id),
                "dst_ip": "",
            }

            update_phase_log(
                client_id=client_id,
                phase_label=PHASE_TRAINING,
                inferred_round_id=int(runtime.get("inferred_round_id", 0)),
                normalized=phase_log_normalized,
            )
            runtime["decision_phase"] = PHASE_TRAINING
            runtime["decision_phase_confidence"] = 0.90

            if runtime["cycle_stage"] == 0:
                runtime["cycle_stage"] = 1

            r.set(STATE_KEY, int(TRAINING))
            publish_client_snapshot(
                r=r,
                client_id=client_id,
                stable_state=TRAINING,
                stable_confidence=0.90,
                live_direction_label="unknown",
                phase_label=PHASE_TRAINING,
                packet_ts=now_ts,
            )

            write_event("training_latch_start", {
                "client_id": client_id,
                "from_state": int(DOWNLOAD),
                "to_state": int(TRAINING),
                "reason": "silence_regime",
                "silence_age_s": float(silence_age),
                "download_gap_s": float(download_gap_s),
                "last_direction_label": str(last_direction_label),
                "direction_is_silent_or_unknown": bool(direction_is_silent_or_unknown),
                "packet_timestamp": float(now_ts),
                "packet_wall_time_ns": int(time.time_ns()),
                "packet_mono_time_ns": int(time.monotonic_ns()),
                "adaptive_log_interval_s": float(adaptive_log_interval_s)
                if "adaptive_log_interval_s" in locals()
                else float(TRAINING_LATCH_LOG_INTERVAL_SECONDS),
                **gap_meta,
            })

def maybe_print_phase_transition(client_id: str, ts: float, wall_time_ns: int, mono_time_ns: int,
                                 prev_stable_state: int, stable_state: int, inferred_round_id: int,
                                 completed_cycle_id: int, cycle_stage: int, direction: int,
                                 payload_bytes: int, filtered_iat: float):
    if stable_state == prev_stable_state:
        return
    state_name_map = {
        0: PHASE_IDLE,
        DOWNLOAD: PHASE_DOWNLOAD,
        TRAINING: PHASE_TRAINING,
        UPLOAD: PHASE_UPLOAD,
    }
    prev_name = state_name_map.get(prev_stable_state, str(prev_stable_state))
    curr_name = state_name_map.get(stable_state, str(stable_state))
    tag = "[TRAINING]" if stable_state == TRAINING else "[DOWNLOAD]" if stable_state == DOWNLOAD else "[UPLOAD]" if stable_state == UPLOAD else "[PHASE]"
    print(
        f"{tag} pkt_ts={ts:.6f} pkt_wall_ns={wall_time_ns} pkt_mono_ns={mono_time_ns} "
        f"client={client_id} from={prev_name} to={curr_name} inf_round={inferred_round_id} "
        f"done={completed_cycle_id} stage={cycle_stage} bytes={payload_bytes} dir={direction} "
        f"iat_kf={filtered_iat:.6f}",
        flush=True,
    )


def write_row(normalized: dict, dir_ratio: float, density: int, feature_bundle: dict,
              raw_state: int, stable_state: int, confidence: float,
              cycle_stage: int, inferred_round_id: int, completed_cycle_id: int,
              live_direction_label: str, live_phase_label: str, live_phase_confidence: float,
              adaptive_phase_label: str, adaptive_phase_scores: dict,
              decision_info: Optional[dict] = None) -> None:
    row = [
        normalized["timestamp"],
        normalized["wall_time_ns"],
        normalized["mono_time_ns"],
        EXPERIMENT_ID,
        normalized["src_ip"],
        normalized["client_id"],
        normalized["payload_bytes"],
        normalized["direction"],
        normalized["iat"],
        round(dir_ratio, 2),
        density,
        float(feature_bundle.get("inbound_bytes", 0.0)),
        float(feature_bundle.get("outbound_bytes", 0.0)),
        int(feature_bundle.get("inbound_count", 0)),
        int(feature_bundle.get("outbound_count", 0)),
        round(float(feature_bundle.get("inbound_share", 0.0)), 6),
        round(float(feature_bundle.get("outbound_share", 0.0)), 6),
        raw_state,
        stable_state,
        round(confidence, 6),
        cycle_stage,
        inferred_round_id,
        completed_cycle_id,
        live_direction_label,
        live_phase_label,
        round(live_phase_confidence, 6),
        adaptive_phase_label,
        round(float(adaptive_phase_scores.get(PHASE_IDLE, 0.0)), 6),
        round(float(adaptive_phase_scores.get(PHASE_DOWNLOAD, 0.0)), 6),
        round(float(adaptive_phase_scores.get(PHASE_TRAINING, 0.0)), 6),
        round(float(adaptive_phase_scores.get(PHASE_UPLOAD, 0.0)), 6),
    ]
    for path in (DATASET_FILE, LATEST_DATASET_FILE):
        with open(path, "a", newline="") as f:
            csv.writer(f).writerow(row)
            f.flush()

    info = decision_info or {}
    analyzer_cpu_percent, analyzer_rss_mb = sample_analyzer_usage()
    packet_ts = float(info.get("packet_ts", normalized["timestamp"]))
    decision_row = [
        time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(packet_ts)) + f".{int((packet_ts % 1) * 1000):03d}",
        normalized["client_id"],
        info.get("selected_target", ""),
        int(inferred_round_id) if inferred_round_id is not None else "",
        int(stable_state),
        info.get("stable_phase", state_to_phase_label(stable_state)),
        float(confidence),
        info.get("decision_phase", state_to_phase_label(stable_state)),
        float(info.get("decision_confidence", confidence)),
        int(normalized["direction"]),
        int(normalized["payload_bytes"]),
        float(dir_ratio),
        int(density),
        float(feature_bundle.get("inbound_bytes", 0.0)),
        float(feature_bundle.get("outbound_bytes", 0.0)),
        int(feature_bundle.get("inbound_count", 0)),
        int(feature_bundle.get("outbound_count", 0)),
        float(feature_bundle.get("inbound_share", 0.0)),
        float(feature_bundle.get("outbound_share", 0.0)),
        float(normalized["iat"]),
        int(bool(info.get("is_selected_target", False))),
        int(bool(info.get("startup_grace_active", False))),
        int(bool(info.get("cooldown_active", False))),
        int(bool(info.get("phase_upload_confirmed", False))),
        int(bool(info.get("packet_upload_support", False))),
        int(bool(info.get("upload_candidate", False))),
        int(bool(info.get("upload_confirmed", False))),
        int(bool(info.get("attackable_upload", False))),
        float(info.get("upload_score", 0.0)),
        float(info.get("packet_support_score", 0.0)),
        float(info.get("phase_agreement_score", 0.0)),
        float(info.get("direction_persistence_score", 0.0)),
        float(info.get("round_context_score", 0.0)),
        info.get("action", "skip"),
        info.get("reason", "packet_processed"),
        packet_ts,
        int(info.get("packet_wall_time_ns", normalized["wall_time_ns"])),
        int(info.get("packet_mono_time_ns", normalized["mono_time_ns"])),
        float(info.get("analyzer_cpu_percent", analyzer_cpu_percent)),
        float(info.get("analyzer_rss_mb", analyzer_rss_mb)),
        float(info.get("decision_lag_ms", -1.0)),
        int(info.get("trigger_publish_wall_time_ns", 0)),
        int(info.get("trigger_publish_mono_time_ns", 0)),
    ]
    with open(DECISION_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(decision_row)
        f.flush()



def process_packet_message(r: redis.Redis, data: dict) -> None:
    if not is_informative_packet(data):
        return

    normalized = normalize_packet_fields(data)
    ts = normalized["timestamp"]
    payload_bytes = normalized["payload_bytes"]
    direction = normalized["direction"]
    raw_iat = normalized["iat"]
    client_id = normalized["client_id"]

    lag_s = max(0.0, time.time() - ts)

    filtered_iat = kalman_filter_iat(client_id, raw_iat)
    normalized["iat"] = filtered_iat

    live_pkt = PacketRecord(
        ts=ts,
        src_ip=normalized["src_ip"],
        dst_ip=normalized["dst_ip"],
        payload=payload_bytes,
        wire=normalized["wire_bytes"],
        iat=filtered_iat,
        client_id=client_id,
        direction=direction,
    )
    live_phase_event = live_phase_tracker.process_packet(live_pkt)

    if live_phase_event is None:
        live_direction_label = "unknown"
        live_phase_label = PHASE_IDLE
        live_phase_confidence = 0.0
    else:
        live_direction_label = str(live_phase_event["direction_label"])
        live_phase_label = str(live_phase_event["phase"])
        live_phase_confidence = float(live_phase_event["confidence"])
        client_runtime[client_id]["live_direction_label"] = live_direction_label
        client_runtime[client_id]["live_phase"] = live_phase_label
        client_runtime[client_id]["live_phase_confidence"] = live_phase_confidence
        if live_phase_event["confirmed"] and live_phase_label in {PHASE_DOWNLOAD, PHASE_UPLOAD}:
            write_event("live_phase_event", {
                "client_id": client_id,
                "live_direction_label": live_direction_label,
                "live_phase_label": live_phase_label,
                "live_phase_confidence": round(live_phase_confidence, 6),
                "packet_timestamp": float(ts),
                "src_ip": normalized["src_ip"],
                "dst_ip": normalized["dst_ip"],
                "payload_bytes": int(payload_bytes),
                "iat": float(filtered_iat),
            })

    feature_bundle = compute_features(client_id, ts, payload_bytes, direction)
    dir_ratio = feature_bundle["dir_ratio"]
    density = feature_bundle["burst_density"]

    adaptive_phase_label, adaptive_phase_features, adaptive_phase_scores = adaptive_phase_classifier.update(
        client_id, direction, payload_bytes, filtered_iat, density
    )
    
    if not isinstance(adaptive_phase_scores, dict):
        adaptive_phase_scores = {
        PHASE_IDLE: 0.0,
        PHASE_DOWNLOAD: 0.0,
        PHASE_TRAINING: 0.0,
        PHASE_UPLOAD: 0.0,
    }

    if payload_bytes <= LIVE_IDLE_PAYLOAD_MAX and filtered_iat >= LIVE_IDLE_IAT_MIN:
        adaptive_phase_label = PHASE_IDLE
        adaptive_phase_scores = {
            PHASE_IDLE: 1.0,
            PHASE_DOWNLOAD: 0.0,
            PHASE_TRAINING: 0.0,
            PHASE_UPLOAD: 0.0,
        }

    raw_state, confidence, emissions = update_hmm_adaptive(
        client_id, direction, feature_bundle, filtered_iat, payload_bytes
    )

    
    # === HARD DIRECTION CONSISTENCY FIX ===
    if direction == -1:
        raw_state = DOWNLOAD
        confidence = max(confidence, 0.95)
    elif direction == 1:
        raw_state = UPLOAD
        confidence = max(confidence, 0.95)
    
    inbound_count = int(feature_bundle["inbound_count"])
    outbound_count = int(feature_bundle["outbound_count"])
    inbound_bytes = float(feature_bundle["inbound_bytes"])
    outbound_bytes = float(feature_bundle["outbound_bytes"])
    total_bytes = max(inbound_bytes + outbound_bytes, EPS)
    inbound_share = inbound_bytes / total_bytes

    if (
        client_runtime[client_id]["stable_state"] == IDLE
        and raw_state == UPLOAD
        and direction == -1
        and payload_bytes >= PHASE_MIN_PAYLOAD
        and inbound_count >= 1
        and outbound_count == 0
        and inbound_share >= 0.70
    ):
        raw_state = DOWNLOAD
        confidence = max(float(confidence), 0.95)
        client_runtime[client_id]["raw_state"] = DOWNLOAD
        client_runtime[client_id]["belief"][:] = np.array([0.02, 0.94, 0.02, 0.02], dtype=float)

        write_event("startup_rawstate_corrected", {
            "client_id": client_id,
            "old_raw_state": int(UPLOAD),
            "new_raw_state": int(DOWNLOAD),
            "direction": int(direction),
            "payload_bytes": int(payload_bytes),
            "inbound_count": int(inbound_count),
            "outbound_count": int(outbound_count),
            "inbound_share": float(inbound_share),
            "packet_timestamp": float(ts),
            "packet_wall_time_ns": int(normalized["wall_time_ns"]),
            "packet_mono_time_ns": int(normalized["mono_time_ns"]),
        })

    # Track the most recent large inbound packet timestamp.
    # This is used by strong_download_evidence in update_stable_state so that a
    # fast download burst that completes before the time-hold gate opens can
    # still satisfy the UPLOAD->DOWNLOAD transition guard on the post-burst
    # control packet that eventually triggers promotion.
    if direction == -1 and payload_bytes >= PHASE_MIN_PAYLOAD:
        client_runtime[client_id]["last_large_inbound_ts"] = ts

    prev_stable_state = client_runtime[client_id]["stable_state"]
    stable_state, _ = update_stable_state(
        client_id=client_id,
        raw_state=raw_state,
        confidence=confidence,
        ts=ts,
        wall_time_ns=normalized["wall_time_ns"],
        mono_time_ns=normalized["mono_time_ns"],
        payload_bytes=payload_bytes,
        direction=direction,
        feature_bundle=feature_bundle,
    )

    raw_state, confidence, stable_state, live_phase_label, live_phase_confidence, adaptive_phase_label, adaptive_phase_scores = apply_training_latch(
        client_id=client_id,
        ts=ts,
        payload_bytes=payload_bytes,
        direction=direction,
        density=density,
        filtered_iat=filtered_iat,
        prev_stable_state=prev_stable_state,
        stable_state=stable_state,
        live_phase_label=live_phase_label,
        live_phase_confidence=live_phase_confidence,
        adaptive_phase_label=adaptive_phase_label,
        adaptive_phase_scores=adaptive_phase_scores,
        raw_state=raw_state,
        raw_confidence=confidence,
        wall_time_ns=normalized["wall_time_ns"],
        mono_time_ns=normalized["mono_time_ns"],
        feature_bundle=feature_bundle,
    )

    # Consensus fast-exit: fires when raw HMM + live phase agree on the
    # same non-TRAINING state for TRAINING_FAST_EXIT_MIN_PACKETS consecutive
    # packets.  Runs after apply_training_latch so the latch cannot suppress
    # it, and before decision_phase_label is derived so the dashboard and
    # attack trigger see the corrected state immediately.
    stable_state = maybe_apply_training_fast_exit(
        client_id, stable_state, raw_state, confidence,
        live_phase_label, adaptive_phase_label, ts,
        normalized["wall_time_ns"], normalized["mono_time_ns"],
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
    )

    # Consensus fast-exit from UPLOAD: fires when raw HMM, live phase,
    # and adaptive phase all agree on DOWNLOAD for
    # TRAINING_FAST_EXIT_MIN_PACKETS consecutive packets, bypassing the
    # stable dwell and candidate duration requirements that cause 40-70
    # packet lag when the upload burst is short.
    stable_state = maybe_apply_upload_fast_exit(
        client_id, stable_state, raw_state, confidence,
        live_phase_label, adaptive_phase_label, ts,
        normalized["wall_time_ns"], normalized["mono_time_ns"],
        direction=direction,
        payload_bytes=payload_bytes,
        feature_bundle=feature_bundle,
    )

    
    decision_phase_label = state_to_phase_label(stable_state)
    decision_phase_confidence = float(confidence)

    previous_decision_phase = str(
        client_runtime[client_id].get("decision_phase", state_to_phase_label(prev_stable_state))
        or state_to_phase_label(prev_stable_state)
    )

    packet_phase_label = None
    if packet_phase_label == PHASE_UPLOAD and stable_state == DOWNLOAD and previous_decision_phase == PHASE_DOWNLOAD:
        decision_phase_label = PHASE_TRAINING
        decision_phase_confidence = max(float(decision_phase_confidence), 0.90)
    elif packet_phase_label == PHASE_DOWNLOAD and stable_state == UPLOAD:
        decision_phase_label = PHASE_DOWNLOAD
        decision_phase_confidence = max(float(decision_phase_confidence), 0.95)
    elif packet_phase_label == PHASE_UPLOAD and stable_state in (TRAINING, DOWNLOAD):
        decision_phase_label = PHASE_UPLOAD
        decision_phase_confidence = max(float(decision_phase_confidence), 0.95)

    upload_start_evidence = has_upload_start_evidence(
        direction, payload_bytes, feature_bundle
    )

    if (
        previous_decision_phase == PHASE_TRAINING
        and decision_phase_label == PHASE_DOWNLOAD
    ):
        if upload_start_evidence:
            decision_phase_label = PHASE_UPLOAD
            decision_phase_confidence = max(float(decision_phase_confidence), 0.95)
        else:
            decision_phase_label = PHASE_TRAINING
            decision_phase_confidence = max(float(decision_phase_confidence), 0.90)

    # Reset attack cooldown when the client enters a new DOWNLOAD phase.
    # The fixed-timer cooldown (ATTACK_COOLDOWN_SECONDS) can otherwise spill
    # into the next round's upload window if a trigger fires late in an upload.
    # Tying expiry to the download transition guarantees the controller is
    # always ready by the time the next upload begins.
    if stable_state == DOWNLOAD and prev_stable_state != DOWNLOAD:
        client_runtime[client_id]["last_attack_time"] = 0.0

    # During local training, individual packet direction (inbound/outbound) is
    # not meaningful — training produces sparse keepalive/control traffic that
    # can be either direction unpredictably. Showing the raw per-packet
    # direction on the dashboard is misleading: two clients in TRAINING will
    # randomly display different directions depending on which direction their
    # last control packet happened to be, giving a false impression of
    # asymmetry. Override to "unknown" so the dashboard reflects the phase
    # correctly.
    if stable_state == TRAINING:
        live_direction_label = "unknown"
        client_runtime[client_id]["live_direction_label"] = live_direction_label

    ensure_round_record(client_id, client_runtime[client_id]["inferred_round_id"], ts)
    prev_completed_cycle_id = int(client_runtime[client_id]["completed_cycle_id"])

    client_runtime[client_id]["live_phase"] = live_phase_label
    client_runtime[client_id]["live_phase_confidence"] = live_phase_confidence
    client_runtime[client_id]["decision_phase"] = decision_phase_label
    client_runtime[client_id]["decision_phase_confidence"] = decision_phase_confidence
    inferred_round_id, completed_cycle_id, cycle_stage = update_cycle_round(
        client_id, stable_state, prev_stable_state, confidence, ts,
        normalized["wall_time_ns"], normalized["mono_time_ns"]
    )

    if completed_cycle_id > prev_completed_cycle_id:
        maybe_finalize_round_log(client_id, completed_cycle_id, ts)

    maybe_print_phase_transition(
        client_id, ts, normalized["wall_time_ns"], normalized["mono_time_ns"],
        prev_stable_state, stable_state, inferred_round_id, completed_cycle_id,
        cycle_stage, direction, payload_bytes, filtered_iat
    )

    update_wire_upload_episode(
        client_id=client_id,
        inferred_round_id=inferred_round_id,
        previous_decision_phase=previous_decision_phase,
        decision_phase_label=decision_phase_label,
        direction=direction,
        payload_bytes=payload_bytes,
        packet_ts=ts,
        wall_time_ns=normalized["wall_time_ns"],
        mono_time_ns=normalized["mono_time_ns"],
    )

    update_upload_episode(
        r, client_id, stable_state, direction, payload_bytes, ts,
        normalized["wall_time_ns"], normalized["mono_time_ns"]
    )

    update_phase_log(client_id, decision_phase_label, inferred_round_id, normalized)

    update_client_stats(client_id, direction, payload_bytes, filtered_iat, stable_state, ts)
    prune_stale_clients(ts)

    decision_info = {
        "selected_target": selected_target_client or "",
        "stable_phase": decision_phase_label,
        "decision_phase": decision_phase_label,
        "decision_confidence": decision_phase_confidence,
        "action": "skip",
        "reason": "live_lag_too_high" if lag_s > LIVE_MAX_LAG_SECONDS else "packet_processed",
        "packet_ts": float(ts),
        "packet_wall_time_ns": int(normalized["wall_time_ns"]),
        "packet_mono_time_ns": int(normalized["mono_time_ns"]),
    }

    if lag_s <= LIVE_MAX_LAG_SECONDS:
        r.set(STATE_KEY, int(stable_state))
        publish_client_snapshot(
            r=r,
            client_id=client_id,
            stable_state=stable_state,
            stable_confidence=decision_phase_confidence,
            live_direction_label=live_direction_label,
            phase_label=decision_phase_label,
            packet_ts=ts,
        )

        refresh_target_client_if_needed(r, stable_state, ts)

        decision_info = maybe_trigger_attack(
            r,
            client_id,
            stable_state,
            confidence,
            payload_bytes,
            dir_ratio,
            density,
            direction,
            filtered_iat,
            ts,
            normalized["wall_time_ns"],
            normalized["mono_time_ns"],
            inferred_round_id,
            decision_phase_label,
            decision_phase_confidence,
            feature_bundle=feature_bundle,
            server_ip=str(normalized.get("server_ip", "")),
            server_port=int(normalized.get("server_port", 0) or 0),
        ) or decision_info

    write_row(
        normalized, dir_ratio, density, feature_bundle, raw_state, stable_state, confidence,
        cycle_stage, inferred_round_id, completed_cycle_id,
        live_direction_label, live_phase_label, live_phase_confidence,
        adaptive_phase_label, adaptive_phase_scores,
        decision_info=decision_info,
    )

    print(
        f"[HMM] pkt_ts={ts:.6f} pkt_wall_ns={normalized['wall_time_ns']} "
        f"pkt_mono_ns={normalized['mono_time_ns']} timing_source={normalized['timing_source']} "
        f"lag_s={lag_s:.6f} client={client_id} inf_round={inferred_round_id} "
        f"done={completed_cycle_id} stage={cycle_stage} raw={raw_state} stable={stable_state} "
        f"conf={confidence:.3f} decision_phase={decision_phase_label} "
        f"decision_conf={decision_phase_confidence:.3f} dir_ratio={dir_ratio:.2f} "
        f"density={density} iat_raw={raw_iat:.6f} iat_kf={filtered_iat:.6f} "
        f"bytes={payload_bytes} dir={direction} live_dir={live_direction_label} "
        f"live_phase={live_phase_label} live_conf={live_phase_confidence:.3f} "
        f"adaptive_phase={adaptive_phase_label} "
        f"adaptive_scores={{idle:{adaptive_phase_scores.get(PHASE_IDLE, 0.0):.3f}, "
        f"down:{adaptive_phase_scores.get(PHASE_DOWNLOAD, 0.0):.3f}, "
        f"train:{adaptive_phase_scores.get(PHASE_TRAINING, 0.0):.3f}, "
        f"up:{adaptive_phase_scores.get(PHASE_UPLOAD, 0.0):.3f}}} "
        f"ems={np.round(emissions, 3)}",
        flush=True,
    )


def phase_label_for_log(phase_label: str) -> str:
    if phase_label == PHASE_TRAINING:
        return "fit"
    if phase_label == PHASE_DOWNLOAD:
        return "download"
    if phase_label == PHASE_UPLOAD:
        return "upload"
    return "idle"


def infer_server_host(normalized: dict, client_id: str) -> str:
    src_ip = str(normalized.get("src_ip", ""))
    dst_ip = str(normalized.get("dst_ip", ""))
    if src_ip == client_id and dst_ip:
        return dst_ip
    if dst_ip == client_id and src_ip:
        return src_ip
    return dst_ip or src_ip


def write_phase_log_row(client_id: str, round_id: int, phase_label: str, src_ip: str, dst_ip: str,
                        server_host: str, phase_start: float, phase_end: float, upload_success):
    if not phase_label:
        return
    row = [
        time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(phase_end)) + f".{int((phase_end % 1) * 1000):03d}",
        client_id,
        int(round_id) if round_id is not None else "",
        phase_label_for_log(phase_label),
        src_ip,
        dst_ip,
        server_host,
        upload_success,
        float(phase_start),
        float(phase_end),
        float(max(0.0, phase_end - phase_start)),
    ]
    with open(PHASE_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)
        f.flush()


def update_phase_log(client_id: str, phase_label: str, inferred_round_id: int, normalized: dict) -> None:
    runtime = client_runtime[client_id]
    current_label = runtime.get("phase_record_label")
    packet_ts = float(normalized["timestamp"])
    server_host = infer_server_host(normalized, client_id)

    if current_label is None:
        runtime["phase_record_label"] = phase_label
        runtime["phase_record_start_ts"] = packet_ts
        runtime["phase_record_start_wall_ns"] = int(normalized["wall_time_ns"])
        runtime["phase_record_start_mono_ns"] = int(normalized["mono_time_ns"])
        runtime["phase_record_round_id"] = int(inferred_round_id)
        runtime["phase_record_src_ip"] = str(normalized["src_ip"])
        runtime["phase_record_dst_ip"] = str(normalized["dst_ip"])
        runtime["phase_record_server_host"] = server_host
        runtime["phase_record_last_ts"] = packet_ts
        return

    if phase_label == current_label:
        runtime["phase_record_last_ts"] = packet_ts
        return

    upload_success = 1.0 if current_label == PHASE_UPLOAD else ""
    write_phase_log_row(
            client_id=client_id,
            round_id=int(runtime.get("phase_record_round_id", inferred_round_id)),
            phase_label=str(current_label),
            src_ip=str(runtime.get("phase_record_src_ip", "")),
            dst_ip=str(runtime.get("phase_record_dst_ip", "")),
            server_host=str(runtime.get("phase_record_server_host", "")),
            phase_start=float(runtime.get("phase_record_start_ts", packet_ts)),
            phase_end=packet_ts,
            upload_success=upload_success,
        )

    runtime["phase_record_label"] = phase_label
    runtime["phase_record_start_ts"] = packet_ts
    runtime["phase_record_start_wall_ns"] = int(normalized["wall_time_ns"])
    runtime["phase_record_start_mono_ns"] = int(normalized["mono_time_ns"])
    runtime["phase_record_round_id"] = int(inferred_round_id)
    runtime["phase_record_src_ip"] = str(normalized["src_ip"])
    runtime["phase_record_dst_ip"] = str(normalized["dst_ip"])
    runtime["phase_record_server_host"] = server_host
    runtime["phase_record_last_ts"] = packet_ts




def finalize_open_phase_logs() -> None:
    """Flush any open phase records on shutdown."""
    now_ts = time.time()
    for client_id, runtime in list(client_runtime.items()):
        phase_label = runtime.get("phase_record_label")
        if phase_label is None:
            continue
        phase_start = float(runtime.get("phase_record_start_ts", now_ts))
        phase_end = max(float(runtime.get("phase_record_last_ts", now_ts)), phase_start)
        upload_success = 1.0 if phase_label == PHASE_UPLOAD else ""
        try:
            write_phase_log_row(
                client_id=client_id,
                round_id=int(runtime.get("phase_record_round_id", runtime.get("inferred_round_id", 0))),
                phase_label=str(phase_label),
                src_ip=str(runtime.get("phase_record_src_ip", "")),
                dst_ip=str(runtime.get("phase_record_dst_ip", "")),
                server_host=str(runtime.get("phase_record_server_host", "")),
                phase_start=phase_start,
                phase_end=phase_end,
                upload_success=upload_success,
            )
        except Exception as exc:
            print(f"[CLEANUP] Failed to flush phase log for client={client_id}: {exc}", flush=True)
        runtime["phase_record_label"] = None

def ensure_round_record(client_id: str, inferred_round_id: int, packet_ts: float) -> None:
    runtime = client_runtime[client_id]
    if not runtime.get("round_record_active", False):
        runtime["round_record_active"] = True
        runtime["round_record_start_ts"] = float(packet_ts)
        runtime["round_record_last_ts"] = float(packet_ts)
        runtime["round_record_round_id"] = int(inferred_round_id)
    else:
        runtime["round_record_last_ts"] = float(packet_ts)


def write_round_log_row(client_id: str, round_id: int, round_start: float, round_end: float) -> None:
    row = [
        time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(round_end)) + f".{int((round_end % 1) * 1000):03d}",
        client_id,
        int(round_id) if round_id is not None else "",
        float(round_start),
        float(round_end),
        float(max(0.0, round_end - round_start)),
    ]
    with open(ROUND_LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)
        f.flush()


def maybe_finalize_round_log(client_id: str, completed_round_id: int, packet_ts: float) -> None:
    runtime = client_runtime[client_id]
    if not runtime.get("round_record_active", False):
        runtime["round_record_active"] = True
        runtime["round_record_start_ts"] = float(packet_ts)
        runtime["round_record_last_ts"] = float(packet_ts)
        runtime["round_record_round_id"] = int(completed_round_id) + 1
        return

    round_start = float(runtime.get("round_record_start_ts", packet_ts))
    round_end = max(float(packet_ts), round_start)
    round_id = int(completed_round_id)
    write_round_log_row(
        client_id=client_id,
        round_id=round_id,
        round_start=round_start,
        round_end=round_end,
    )
    runtime["round_record_active"] = True
    runtime["round_record_start_ts"] = float(packet_ts)
    runtime["round_record_last_ts"] = float(packet_ts)
    runtime["round_record_round_id"] = int(completed_round_id) + 1



def finalize_terminal_upload_rounds(reason: str = "shutdown") -> None:
    """Close the final FL round when the run ends during UPLOAD.

    Normal online round completion is counted only on UPLOAD -> DOWNLOAD,
    because that boundary proves the server has accepted the client's upload
    and started the next round.  The last FL round is different: there may be
    no next DOWNLOAD after the final client upload, so waiting for
    UPLOAD -> DOWNLOAD leaves the final completed round unlogged.

    This function is used only during analyzer shutdown/finalization.  It does
    not alter live transition behavior and it does not invent an extra inferred
    round.  It only marks the currently inferred round as completed when the
    client is already in stage 2 (DOWNLOAD -> TRAINING -> UPLOAD observed) and
    there is concrete upload-byte evidence for that open round.
    """
    now_ts = time.time()

    for client_id, runtime in list(client_runtime.items()):
        try:
            stable_state = int(runtime.get("stable_state", IDLE))
            cycle_stage = int(runtime.get("cycle_stage", 0))
            inferred_round_id = int(runtime.get("inferred_round_id", 0))
            completed_cycle_id = int(runtime.get("completed_cycle_id", 0))
        except Exception:
            continue

        if stable_state != UPLOAD:
            continue
        if cycle_stage != 2:
            continue
        if inferred_round_id <= 0:
            continue
        if completed_cycle_id >= inferred_round_id:
            continue

        wire_state = wire_upload_state.get(client_id, {})
        upload_evidence = get_open_upload_completion_evidence(client_id, now_ts)
        observed_upload_bytes = int(upload_evidence.get("upload_bytes", 0))
        observed_upload_packets = int(upload_evidence.get("upload_packets", 0))
        bytes_thr = int(upload_evidence.get("median_bytes", UPLOAD_BYTES_FLOOR))

        if not bool(upload_evidence.get("valid", False)):
            write_event("terminal_upload_round_not_completed", {
                "client_id": client_id,
                "reason": "insufficient_upload_completion_evidence",
                "shutdown_reason": str(reason),
                "stable_state": int(stable_state),
                "cycle_stage": int(cycle_stage),
                "inferred_round_id": int(inferred_round_id),
                "completed_cycle_id": int(completed_cycle_id),
                "packet_timestamp": float(now_ts),
                **upload_evidence,
            })
            continue

        round_start = float(runtime.get("round_record_start_ts", now_ts) or now_ts)
        round_end = max(
            float(runtime.get("round_record_last_ts", now_ts) or now_ts),
            float(wire_state.get("last_ts", 0.0) or 0.0),
            float(runtime.get("phase_record_last_ts", 0.0) or 0.0),
            round_start,
        )

        write_round_log_row(
            client_id=client_id,
            round_id=int(inferred_round_id),
            round_start=float(round_start),
            round_end=float(round_end),
        )

        runtime["completed_cycle_id"] = int(inferred_round_id)
        if observed_upload_bytes > 0:
            runtime["upload_bytes_history"].append(int(observed_upload_bytes))
        if observed_upload_packets > 0:
            runtime["upload_packet_history"].append(int(observed_upload_packets))
        runtime["round_record_active"] = False
        runtime["round_record_round_id"] = int(inferred_round_id) + 1
        runtime["round_record_start_ts"] = float(round_end)
        runtime["round_record_last_ts"] = float(round_end)

        write_event("terminal_upload_round_completed", {
            "client_id": client_id,
            "reason": str(reason),
            "round_id": int(inferred_round_id),
            "inferred_round_id": int(inferred_round_id),
            "completed_cycle_id": int(runtime.get("completed_cycle_id", 0)),
            "observed_upload_bytes": int(observed_upload_bytes),
            "observed_upload_packets": int(observed_upload_packets),
            "bytes_threshold": int(bytes_thr),
            **upload_evidence,
            "round_start": float(round_start),
            "round_end": float(round_end),
            "round_duration_s": float(max(0.0, round_end - round_start)),
            "packet_timestamp": float(now_ts),
        })

        print(
            f"[SHUTDOWN] Completed terminal upload round: client={client_id} "
            f"round={inferred_round_id} bytes={observed_upload_bytes}",
            flush=True,
        )

def finalize_open_round_logs() -> None:
    """Flush any round record that was opened but never closed.

    This fires on shutdown.  The final round completes its phase transitions
    but never receives the upload->download boundary that would normally
    trigger maybe_finalize_round_log, so the round counter in the log is
    one short.  Using the last observed packet timestamp as round_end is
    accurate enough for analysis purposes.
    """
    now_ts = time.time()
    for client_id, runtime in list(client_runtime.items()):
        if not runtime.get("round_record_active", False):
            continue
        round_start = float(runtime.get("round_record_start_ts", now_ts))
        round_end = max(float(runtime.get("round_record_last_ts", now_ts)), round_start)
        round_id = int(runtime.get("round_record_round_id", 0))
        if round_id <= 0:
            continue
        write_round_log_row(
            client_id=client_id,
            round_id=round_id,
            round_start=round_start,
            round_end=round_end,
        )
        runtime["round_record_active"] = False
        print(
            f"[SHUTDOWN] Flushed open round log: client={client_id} "
            f"round={round_id} duration={round_end - round_start:.3f}s",
            flush=True,
        )


def main() -> None:
    global sock
    ensure_output_files()
    try:
        r = connect_redis()
    except Exception as e:
        print(f"CRITICAL: Redis connection failed: {e}", flush=True)
        return

    r.set(STATE_KEY, 0)
    r.delete(TARGET_CLIENT_KEY)
    r.delete(CLIENT_RANKING_KEY)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((ANALYZER_HOST, ANALYZER_PORT))
    except OSError as exc:
        raise SystemExit(
            f"CRITICAL: Analyzer cannot bind UDP {ANALYZER_HOST}:{ANALYZER_PORT}. "
            f"Another analyzer/sniffer receiver is probably still using port {ANALYZER_PORT}. "
            f"Run: sudo lsof -iUDP:{ANALYZER_PORT} && sudo fuser -k {ANALYZER_PORT}/udp"
        ) from exc
    sock.settimeout(UDP_RECV_TIMEOUT_SECONDS)

    print(">>> Direct sniffer to analyzer mode ARMED.", flush=True)
    print(f">>> Experiment ID: {EXPERIMENT_ID}", flush=True)
    print(f">>> Listening on UDP {ANALYZER_HOST}:{ANALYZER_PORT}", flush=True)
    print(f">>> Writing dataset to: {DATASET_FILE}", flush=True)
    print(f">>> Writing latest dataset replica to: {LATEST_DATASET_FILE}", flush=True)
    print(f">>> Writing event log to: {EVENT_LOG_FILE}", flush=True)
    print(f">>> Writing latest event log replica to: {LATEST_EVENT_LOG_FILE}", flush=True)
    print(f">>> Writing phase log to: {PHASE_LOG_FILE}", flush=True)
    print(f">>> Writing round log to: {ROUND_LOG_FILE}", flush=True)
    print(f">>> Writing decision log to: {DECISION_LOG_FILE}", flush=True)
    print(f">>> Live freshness threshold: {LIVE_MAX_LAG_SECONDS:.2f}s", flush=True)
    print(f">>> Analyzer attack enabled: {ATTACK_ENABLED}", flush=True)
    print(f">>> Analyzer attack mode: {ANALYZER_ATTACK_MODE}", flush=True)
    print(f">>> Analyzer sends release signals: {ANALYZER_SEND_RELEASE}", flush=True)
    print(f">>> Poisoner UDP target: {POISONER_HOST}:{POISONER_PORT}", flush=True)

    write_event("analyzer_started", {
        "transport": "udp_direct",
        "udp_host": ANALYZER_HOST,
        "udp_port": ANALYZER_PORT,
        "dataset_file": DATASET_FILE,
        "latest_dataset_file": LATEST_DATASET_FILE,
        "event_log_file": EVENT_LOG_FILE,
        "latest_event_log_file": LATEST_EVENT_LOG_FILE,
        "phase_log_file": PHASE_LOG_FILE,
        "round_log_file": ROUND_LOG_FILE,
        "decision_log_file": DECISION_LOG_FILE,
    })

    while True:
        raw = None
        try:
            packet_bytes, _addr = sock.recvfrom(65535)
            raw = packet_bytes.decode("utf-8", errors="ignore")
            data = json.loads(raw)
            process_packet_message(r, data)

        except socket.timeout:
            now_ts = time.time()
            check_for_training_silence(r, now_ts)
            prune_stale_clients(now_ts)

        except KeyboardInterrupt:
            raise

        except KeyError as e:
            print(f"HMM Error: missing field {e}", flush=True)
            write_event("analyzer_error", {
                "error_type": "KeyError",
                "detail": str(e),
                "raw": raw,
            })

        except json.JSONDecodeError as e:
            print(f"HMM Error: invalid JSON payload: {raw!r} | {e}", flush=True)
            write_event("analyzer_error", {
                "error_type": "JSONDecodeError",
                "detail": str(e),
                "raw": raw,
            })

        except ValueError as e:
            print(f"HMM Error: invalid numeric value: {e}", flush=True)
            write_event("analyzer_error", {
                "error_type": "ValueError",
                "detail": str(e),
                "raw": raw,
            })

        except Exception as e:
            print(f"HMM Error: {e}", flush=True)
            write_event("analyzer_error", {
                "error_type": type(e).__name__,
                "detail": str(e),
                "raw": raw,
            })

    finalize_open_phase_logs()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n>>> Analyzer stopping. Finalizing open logs...", flush=True)

        try:
            finalize_terminal_upload_rounds(reason="keyboard_interrupt")
        except Exception as e:
            print(f"[CLEANUP] finalize_terminal_upload_rounds failed: {e}", flush=True)

        try:
            finalize_open_wire_upload_logs()
        except Exception as e:
            print(f"[CLEANUP] finalize_open_wire_upload_logs failed: {e}", flush=True)

        try:
            finalize_open_phase_logs()
        except Exception as e:
            print(f"[CLEANUP] finalize_open_phase_logs failed: {e}", flush=True)

        try:
            finalize_open_round_logs()
        except Exception as e:
            print(f"[CLEANUP] finalize_open_round_logs failed: {e}", flush=True)

        try:
            cleanup_analyzer(reason="keyboard_interrupt")
        except Exception as e:
            print(f"[CLEANUP] cleanup_analyzer failed: {e}", flush=True)

        print(">>> Analyzer finalization complete.", flush=True)

    finally:
        try:
            cleanup_analyzer(reason="finally")
        except Exception as e:
            print(f"[CLEANUP] final cleanup_analyzer failed: {e}", flush=True)
