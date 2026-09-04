import argparse
import csv
import json
import os
import socket
import time
from collections import Counter
from datetime import datetime
from threading import Lock, Thread

RUN_TS = datetime.now().strftime("%Y%m%d_%H%M%S")

from scapy.all import IP, TCP, sniff

INTERFACE = "wlo1"
ANALYZER_HOST = "127.0.0.1"
ANALYZER_PORT = 5005
FL_PORT = 8080
WARMUP_SECONDS = 10
FALLBACK_SERVER_IP = "10.42.0.195"

OBS_LOG_DIR = "logs/attack"
PACKET_LOG_PATH = os.path.join(OBS_LOG_DIR, f"sniffer_packets_{RUN_TS}.csv")
WINDOW_LOG_PATH = os.path.join(OBS_LOG_DIR, f"sniffer_windows_{RUN_TS}.csv")
WINDOW_SECONDS = 0.20
WINDOW_FLUSH_POLL_SECONDS = 0.05

last_packet_time = {}
server_candidate_counter = Counter()
last_debug_print = 0.0
start_time = time.time()
locked_server_ip = None
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
poison_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
POISON_FEED_HOST = os.environ.get("POISONER_HOST", "127.0.0.1")
POISON_FEED_PORT = int(os.environ.get("POISONER_PORT", "7007"))
POISON_FEED_ENABLED = os.environ.get("SNIFFER_POISON_FEED", "1").strip().lower() not in {"0", "false", "no", "off"}

_packet_log_lock = Lock()
_window_log_lock = Lock()
_window_state_lock = Lock()

PACKET_FIELDNAMES = [
    "ts_wall",
    "ts_mono",
    "module",
    "event",
    "client_ip",
    "server_ip",
    "round_id",
    "attack_id",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "direction",
    "payload_bytes",
    "wire_bytes",
    "iat_s",
    "tcp_flags",
    "packet_count",
    "window_id",
    "role_hint",
    "notes",
]

WINDOW_FIELDNAMES = [
    "ts_wall_start",
    "ts_wall_end",
    "ts_mono_start",
    "ts_mono_end",
    "module",
    "event",
    "client_ip",
    "server_ip",
    "round_id",
    "attack_id",
    "window_id",
    "window_seconds",
    "packets_total",
    "packets_uplink",
    "packets_downlink",
    "packets_unknown",
    "payload_bytes_total",
    "payload_bytes_uplink",
    "payload_bytes_downlink",
    "payload_bytes_unknown",
    "wire_bytes_total",
    "iat_mean_s",
    "iat_min_s",
    "iat_max_s",
    "dominant_direction",
    "uplink_fraction",
    "downlink_fraction",
    "unknown_fraction",
    "first_src_ip",
    "first_dst_ip",
    "last_src_ip",
    "last_dst_ip",
    "notes",
]

_packet_seq = 0
_active_windows = {}


def parse_args():
    parser = argparse.ArgumentParser(
        description="FL sniffer with separate packet and short window observation logs."
    )
    parser.add_argument("--interface", default=INTERFACE, help="Network interface to sniff on.")
    parser.add_argument("--analyzer-host", default=ANALYZER_HOST, help="Analyzer UDP host.")
    parser.add_argument("--analyzer-port", type=int, default=ANALYZER_PORT, help="Analyzer UDP port.")
    parser.add_argument("--poison-host", default=POISON_FEED_HOST, help="Poison proxy UDP metadata host.")
    parser.add_argument("--poison-port", type=int, default=POISON_FEED_PORT, help="Poison proxy UDP metadata port.")
    parser.add_argument("--disable-poison-feed", action="store_true", help="Do not forward learned server metadata to the poison proxy.")
    parser.add_argument("--fl-port", type=int, default=FL_PORT, help="Federated learning TCP port.")
    parser.add_argument(
        "--warmup-seconds",
        type=float,
        default=WARMUP_SECONDS,
        help="Seconds to observe before locking the server IP.",
    )
    parser.add_argument(
        "--fallback-server-ip",
        default=FALLBACK_SERVER_IP,
        help="Fallback FL server IP if dynamic learning finds none.",
    )
    parser.add_argument(
        "--log-dir",
        default=OBS_LOG_DIR,
        help="Directory for observation log files.",
    )
    parser.add_argument(
        "--packet-log-path",
        default="",
        help="Optional explicit path for packet observation CSV.",
    )
    parser.add_argument(
        "--window-log-path",
        default="",
        help="Optional explicit path for short window summary CSV.",
    )
    parser.add_argument(
        "--window-seconds",
        type=float,
        default=WINDOW_SECONDS,
        help="Short window length in seconds.",
    )
    parser.add_argument(
        "--window-flush-poll-seconds",
        type=float,
        default=WINDOW_FLUSH_POLL_SECONDS,
        help="Background poll interval for flushing expired windows.",
    )
    parser.add_argument(
        "--debug-print-interval",
        type=float,
        default=0.3,
        help="Minimum seconds between debug prints.",
    )
    return parser.parse_args()


def apply_args(args):
    global INTERFACE, ANALYZER_HOST, ANALYZER_PORT, FL_PORT
    global POISON_FEED_HOST, POISON_FEED_PORT, POISON_FEED_ENABLED
    global WARMUP_SECONDS, FALLBACK_SERVER_IP, OBS_LOG_DIR
    global PACKET_LOG_PATH, WINDOW_LOG_PATH, WINDOW_SECONDS
    global WINDOW_FLUSH_POLL_SECONDS, DEBUG_PRINT_INTERVAL
    global start_time, locked_server_ip, server_candidate_counter

    INTERFACE = args.interface
    ANALYZER_HOST = args.analyzer_host
    ANALYZER_PORT = args.analyzer_port
    POISON_FEED_HOST = args.poison_host
    POISON_FEED_PORT = args.poison_port
    POISON_FEED_ENABLED = not bool(args.disable_poison_feed)
    FL_PORT = args.fl_port
    WARMUP_SECONDS = args.warmup_seconds
    FALLBACK_SERVER_IP = args.fallback_server_ip
    OBS_LOG_DIR = args.log_dir
    PACKET_LOG_PATH = args.packet_log_path or os.path.join(OBS_LOG_DIR, f"sniffer_packets_{RUN_TS}.csv")
    WINDOW_LOG_PATH = args.window_log_path or os.path.join(OBS_LOG_DIR, f"sniffer_windows_{RUN_TS}.csv")
    WINDOW_SECONDS = args.window_seconds
    WINDOW_FLUSH_POLL_SECONDS = args.window_flush_poll_seconds
    DEBUG_PRINT_INTERVAL = args.debug_print_interval

    start_time = time.time()
    locked_server_ip = None
    server_candidate_counter = Counter()


DEBUG_PRINT_INTERVAL = 0.3


def ensure_logs() -> None:
    """
    Always (re)create sniffer log files with fresh headers at session start.
    Previously files were only created when absent, so rows from a prior run
    accumulated silently across sessions.
    """
    packet_dir = os.path.dirname(PACKET_LOG_PATH) or "."
    window_dir = os.path.dirname(WINDOW_LOG_PATH) or "."
    os.makedirs(packet_dir, exist_ok=True)
    os.makedirs(window_dir, exist_ok=True)

    with open(PACKET_LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PACKET_FIELDNAMES)
        writer.writeheader()

    with open(WINDOW_LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=WINDOW_FIELDNAMES)
        writer.writeheader()


def next_packet_window_id() -> str:
    global _packet_seq
    _packet_seq += 1
    return f"P{_packet_seq:08d}"


def wall_ns_to_str(event_wall_ns: int) -> str:
    return datetime.fromtimestamp(event_wall_ns / 1e9).strftime("%Y-%m-%d %H:%M:%S.%f")


def get_tcp_flags_text(pkt) -> str:
    try:
        return str(pkt[TCP].flags)
    except Exception:
        return ""


def dominant_direction_text(window: dict) -> str:
    up = window["payload_bytes_uplink"]
    down = window["payload_bytes_downlink"]
    unknown = window["payload_bytes_unknown"]

    if up >= down and up >= unknown and up > 0:
        return "UPLINK"
    if down >= up and down >= unknown and down > 0:
        return "DOWNLINK"
    if unknown > 0:
        return "UNKNOWN"
    return "NONE"


def make_new_window(
    *,
    client_ip: str,
    server_ip: str,
    event_wall_ns: int,
    event_mono_ns: int,
    src_ip: str,
    dst_ip: str,
) -> dict:
    return {
        "client_ip": client_ip,
        "server_ip": server_ip,
        "window_id": f"W{event_wall_ns}",
        "start_wall_ns": event_wall_ns,
        "end_wall_ns": event_wall_ns,
        "start_mono_ns": event_mono_ns,
        "end_mono_ns": event_mono_ns,
        "packets_total": 0,
        "packets_uplink": 0,
        "packets_downlink": 0,
        "packets_unknown": 0,
        "payload_bytes_total": 0,
        "payload_bytes_uplink": 0,
        "payload_bytes_downlink": 0,
        "payload_bytes_unknown": 0,
        "wire_bytes_total": 0,
        "iat_sum": 0.0,
        "iat_count": 0,
        "iat_min": None,
        "iat_max": None,
        "first_src_ip": src_ip,
        "first_dst_ip": dst_ip,
        "last_src_ip": src_ip,
        "last_dst_ip": dst_ip,
    }


def append_packet_to_window(
    *,
    window: dict,
    direction: int,
    payload_bytes: int,
    wire_bytes: int,
    iat_s: float,
    src_ip: str,
    dst_ip: str,
    event_wall_ns: int,
    event_mono_ns: int,
) -> None:
    window["end_wall_ns"] = event_wall_ns
    window["end_mono_ns"] = event_mono_ns
    window["last_src_ip"] = src_ip
    window["last_dst_ip"] = dst_ip

    window["packets_total"] += 1
    window["payload_bytes_total"] += payload_bytes
    window["wire_bytes_total"] += wire_bytes

    if direction == 1:
        window["packets_uplink"] += 1
        window["payload_bytes_uplink"] += payload_bytes
    elif direction == -1:
        window["packets_downlink"] += 1
        window["payload_bytes_downlink"] += payload_bytes
    else:
        window["packets_unknown"] += 1
        window["payload_bytes_unknown"] += payload_bytes

    if iat_s >= 0:
        window["iat_sum"] += iat_s
        window["iat_count"] += 1
        if window["iat_min"] is None or iat_s < window["iat_min"]:
            window["iat_min"] = iat_s
        if window["iat_max"] is None or iat_s > window["iat_max"]:
            window["iat_max"] = iat_s


def write_packet_row(row: dict) -> None:
    with _packet_log_lock:
        with open(PACKET_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=PACKET_FIELDNAMES)
            writer.writerow(row)


def write_window_row(row: dict) -> None:
    with _window_log_lock:
        with open(WINDOW_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=WINDOW_FIELDNAMES)
            writer.writerow(row)


def log_packet_event(
    *,
    event_wall_ns: int,
    event_mono_ns: int,
    client_ip: str,
    server_ip: str,
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    direction: int,
    payload_bytes: int,
    wire_bytes: int,
    iat_s: float,
    tcp_flags: str,
    role_hint: str,
    notes: str = "",
) -> None:
    row = {
        "ts_wall": wall_ns_to_str(event_wall_ns),
        "ts_mono": f"{event_mono_ns / 1e9:.6f}",
        "module": "sniffer",
        "event": "PKT_OBSERVED",
        "client_ip": client_ip,
        "server_ip": server_ip,
        "round_id": "",
        "attack_id": "",
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "direction": direction,
        "payload_bytes": payload_bytes,
        "wire_bytes": wire_bytes,
        "iat_s": f"{iat_s:.6f}",
        "tcp_flags": tcp_flags,
        "packet_count": 1,
        "window_id": next_packet_window_id(),
        "role_hint": role_hint,
        "notes": notes,
    }
    write_packet_row(row)


def flush_window_locked(client_ip: str, notes: str = "window complete") -> None:
    window = _active_windows.pop(client_ip, None)
    if not window or window["packets_total"] <= 0:
        return

    duration_s = max(0.0, (window["end_wall_ns"] - window["start_wall_ns"]) / 1e9)
    pkt_total = max(1, window["packets_total"])
    iat_mean = window["iat_sum"] / window["iat_count"] if window["iat_count"] > 0 else 0.0
    iat_min = window["iat_min"] if window["iat_min"] is not None else 0.0
    iat_max = window["iat_max"] if window["iat_max"] is not None else 0.0

    row = {
        "ts_wall_start": wall_ns_to_str(window["start_wall_ns"]),
        "ts_wall_end": wall_ns_to_str(window["end_wall_ns"]),
        "ts_mono_start": f"{window['start_mono_ns'] / 1e9:.6f}",
        "ts_mono_end": f"{window['end_mono_ns'] / 1e9:.6f}",
        "module": "sniffer",
        "event": "WINDOW_SUMMARY",
        "client_ip": window["client_ip"],
        "server_ip": window["server_ip"],
        "round_id": "",
        "attack_id": "",
        "window_id": window["window_id"],
        "window_seconds": f"{duration_s:.6f}",
        "packets_total": window["packets_total"],
        "packets_uplink": window["packets_uplink"],
        "packets_downlink": window["packets_downlink"],
        "packets_unknown": window["packets_unknown"],
        "payload_bytes_total": window["payload_bytes_total"],
        "payload_bytes_uplink": window["payload_bytes_uplink"],
        "payload_bytes_downlink": window["payload_bytes_downlink"],
        "payload_bytes_unknown": window["payload_bytes_unknown"],
        "wire_bytes_total": window["wire_bytes_total"],
        "iat_mean_s": f"{iat_mean:.6f}",
        "iat_min_s": f"{iat_min:.6f}",
        "iat_max_s": f"{iat_max:.6f}",
        "dominant_direction": dominant_direction_text(window),
        "uplink_fraction": f"{window['packets_uplink'] / pkt_total:.6f}",
        "downlink_fraction": f"{window['packets_downlink'] / pkt_total:.6f}",
        "unknown_fraction": f"{window['packets_unknown'] / pkt_total:.6f}",
        "first_src_ip": window["first_src_ip"],
        "first_dst_ip": window["first_dst_ip"],
        "last_src_ip": window["last_src_ip"],
        "last_dst_ip": window["last_dst_ip"],
        "notes": notes,
    }
    write_window_row(row)


def flush_all_windows(notes: str = "final flush before shutdown") -> None:
    with _window_state_lock:
        for client_ip in list(_active_windows.keys()):
            flush_window_locked(client_ip, notes=notes)


def maybe_flush_expired_windows(now_wall_ns: int) -> None:
    expiry_ns = int(WINDOW_SECONDS * 1e9)
    expired_clients = []

    with _window_state_lock:
        for client_ip, window in _active_windows.items():
            if now_wall_ns - window["start_wall_ns"] >= expiry_ns:
                expired_clients.append(client_ip)

        for client_ip in expired_clients:
            flush_window_locked(client_ip, notes="window reached configured duration")


def update_window_log(
    *,
    event_wall_ns: int,
    event_mono_ns: int,
    client_ip: str,
    server_ip: str,
    src_ip: str,
    dst_ip: str,
    direction: int,
    payload_bytes: int,
    wire_bytes: int,
    iat_s: float,
) -> None:
    maybe_flush_expired_windows(event_wall_ns)

    with _window_state_lock:
        window = _active_windows.get(client_ip)

        if window is None:
            window = make_new_window(
                client_ip=client_ip,
                server_ip=server_ip,
                event_wall_ns=event_wall_ns,
                event_mono_ns=event_mono_ns,
                src_ip=src_ip,
                dst_ip=dst_ip,
            )
            _active_windows[client_ip] = window
        elif event_wall_ns - window["start_wall_ns"] >= int(WINDOW_SECONDS * 1e9):
            flush_window_locked(client_ip, notes="window rolled over by incoming packet")
            window = make_new_window(
                client_ip=client_ip,
                server_ip=server_ip,
                event_wall_ns=event_wall_ns,
                event_mono_ns=event_mono_ns,
                src_ip=src_ip,
                dst_ip=dst_ip,
            )
            _active_windows[client_ip] = window

        append_packet_to_window(
            window=window,
            direction=direction,
            payload_bytes=payload_bytes,
            wire_bytes=wire_bytes,
            iat_s=iat_s,
            src_ip=src_ip,
            dst_ip=dst_ip,
            event_wall_ns=event_wall_ns,
            event_mono_ns=event_mono_ns,
        )


def background_window_flusher() -> None:
    while True:
        try:
            maybe_flush_expired_windows(time.time_ns())
            time.sleep(WINDOW_FLUSH_POLL_SECONDS)
        except Exception as e:
            print(f"[SNIFFER] Window flusher error: {e}", flush=True)
            time.sleep(WINDOW_FLUSH_POLL_SECONDS)


def is_fl_packet(pkt):
    if not pkt.haslayer(IP) or not pkt.haslayer(TCP):
        return False

    sport = int(pkt[TCP].sport)
    dport = int(pkt[TCP].dport)
    return sport == FL_PORT or dport == FL_PORT


def get_tcp_payload_size(pkt):
    try:
        return len(bytes(pkt[TCP].payload))
    except Exception:
        return 0


def is_ack_only(pkt):
    if not pkt.haslayer(TCP):
        return False

    payload_size = get_tcp_payload_size(pkt)
    tcp_flags = int(pkt[TCP].flags)

    ack_set = bool(tcp_flags & 0x10)
    syn_fin_rst_psh = bool(tcp_flags & (0x02 | 0x01 | 0x04 | 0x08))

    return ack_set and payload_size == 0 and not syn_fin_rst_psh


def maybe_learn_server(pkt):
    global locked_server_ip

    if locked_server_ip is not None:
        return

    if not is_fl_packet(pkt):
        return

    src = pkt[IP].src
    dst = pkt[IP].dst
    sport = int(pkt[TCP].sport)
    dport = int(pkt[TCP].dport)

    if dport == FL_PORT:
        server_candidate_counter[dst] += 1
    elif sport == FL_PORT:
        server_candidate_counter[src] += 1

    if time.time() - start_time >= WARMUP_SECONDS:
        if server_candidate_counter:
            locked_server_ip = server_candidate_counter.most_common(1)[0][0]
            print(f"[SNIFFER] Learned FL server IP dynamically: {locked_server_ip}", flush=True)
        else:
            locked_server_ip = FALLBACK_SERVER_IP
            print(f"[SNIFFER] Using fallback FL server IP: {locked_server_ip}", flush=True)


def get_direction(pkt):
    global locked_server_ip

    try:
        src = pkt[IP].src
        dst = pkt[IP].dst

        if locked_server_ip is None:
            return 0

        if dst == locked_server_ip:
            return 1
        if src == locked_server_ip:
            return -1
        return 0
    except Exception:
        return 0



def get_client_id(pkt):
    try:
        src = pkt[IP].src
        dst = pkt[IP].dst

        if locked_server_ip is None:
            return src

        if src == locked_server_ip:
            return dst
        return src
    except Exception:
        return "unknown"


def maybe_print_debug(
    event_ts,
    event_wall_ns,
    event_mono_ns,
    payload_size,
    wire_size,
    direction,
    client_id,
    iat,
    src,
    dst,
):
    global last_debug_print

    now = time.time()
    if now - last_debug_print < DEBUG_PRINT_INTERVAL:
        return

    human_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event_ts))

    print(
        f"[DEBUG] time={human_time} ts={event_ts:.6f} wall_ns={event_wall_ns} mono_ns={event_mono_ns} "
        f"{src} -> {dst} payload={payload_size} wire={wire_size} "
        f"dir={direction} client={client_id} iat={iat:.6f} server={locked_server_ip}",
        flush=True,
    )
    last_debug_print = now


def send_to_analyzer(data):
    try:
        payload = json.dumps(data).encode("utf-8")
        udp_sock.sendto(payload, (ANALYZER_HOST, ANALYZER_PORT))
    except Exception as e:
        print(f"[SNIFFER] UDP send failed: {e}", flush=True)


def send_to_poison_proxy(data):
    """Forward server metadata to poison proxy so it does not need --server-ip."""
    if not POISON_FEED_ENABLED:
        return

    server_ip = str(data.get("server_ip") or "").strip()
    if not server_ip:
        return

    try:
        payload = dict(data)
        payload["type"] = "server_announce"
        payload["command"] = "server_announce"
        payload["fl_port"] = int(FL_PORT)
        payload["server_port"] = int(FL_PORT)
        poison_sock.sendto(json.dumps(payload).encode("utf-8"), (POISON_FEED_HOST, POISON_FEED_PORT))
    except Exception as e:
        print(f"[SNIFFER] Poison metadata UDP send failed: {e}", flush=True)


def process_packet(pkt):
    if not pkt.haslayer(IP) or not pkt.haslayer(TCP):
        return

    maybe_learn_server(pkt)

    if not is_fl_packet(pkt):
        return

    if is_ack_only(pkt):
        return

    event_wall_ns = time.time_ns()
    event_ts = event_wall_ns / 1e9
    event_mono_ns = time.monotonic_ns()

    wire_size = len(pkt)
    payload_size = get_tcp_payload_size(pkt)
    if payload_size <= 0:
        return

    src = pkt[IP].src
    dst = pkt[IP].dst
    src_port = int(pkt[TCP].sport)
    dst_port = int(pkt[TCP].dport)

    direction = get_direction(pkt)
    client_id = get_client_id(pkt)

    # FIX: use a per-(client_id, direction) clock so upload and download IATs are
    # measured independently.  The original single per-client clock conflated both
    # directions: when a download packet arrived immediately after an upload packet,
    # its IAT was near-zero even though the actual download inter-arrival time was
    # much larger, causing the HMM emission to misread the phase.
    flow_key = (client_id, direction)
    prev_ts = last_packet_time.get(flow_key, event_ts)
    iat = event_ts - prev_ts
    last_packet_time[flow_key] = event_ts

    maybe_print_debug(
        event_ts,
        event_wall_ns,
        event_mono_ns,
        payload_size,
        wire_size,
        direction,
        client_id,
        iat,
        src,
        dst,
    )

    role_hint = "BALANCED"
    if direction == 1:
        role_hint = "UPLINK_DATA"
    elif direction == -1:
        role_hint = "DOWNLINK_DATA"

    log_packet_event(
        event_wall_ns=event_wall_ns,
        event_mono_ns=event_mono_ns,
        client_ip=client_id,
        server_ip=locked_server_ip or "",
        src_ip=src,
        dst_ip=dst,
        src_port=src_port,
        dst_port=dst_port,
        direction=direction,
        payload_bytes=payload_size,
        wire_bytes=wire_size,
        iat_s=iat,
        tcp_flags=get_tcp_flags_text(pkt),
        role_hint=role_hint,
        notes="payload packet forwarded to analyzer",
    )

    update_window_log(
        event_wall_ns=event_wall_ns,
        event_mono_ns=event_mono_ns,
        client_ip=client_id,
        server_ip=locked_server_ip or "",
        src_ip=src,
        dst_ip=dst,
        direction=direction,
        payload_bytes=payload_size,
        wire_bytes=wire_size,
        iat_s=iat,
    )

    data = {
        "timestamp": event_ts,
        "wall_time_ns": event_wall_ns,
        "mono_time_ns": event_mono_ns,
        "src_ip": src,
        "dst_ip": dst,
        "client_id": client_id,
        "server_ip": locked_server_ip or "",   # FIX: was missing; analyzer needs this
        "server_port": FL_PORT,
        "fl_port": FL_PORT,
        "payload_bytes": payload_size,
        "wire_bytes": wire_size,
        "direction": direction,
        "iat": iat,
        "role_hint": role_hint,
        "is_ack_only": False,
    }
    send_to_analyzer(data)
    send_to_poison_proxy(data)


def main():
    args = parse_args()
    apply_args(args)
    ensure_logs()

    flusher = Thread(target=background_window_flusher, daemon=True)
    flusher.start()

    print(f"[SNIFFER] Gateway mode on {INTERFACE}", flush=True)
    print(f"[SNIFFER] FL port for dynamic learning: {FL_PORT}", flush=True)
    print(f"[SNIFFER] Fallback server IP: {FALLBACK_SERVER_IP}", flush=True)
    print(f"[SNIFFER] Direct analyzer UDP target: {ANALYZER_HOST}:{ANALYZER_PORT}", flush=True)
    print(f"[SNIFFER] Poison metadata UDP target: {POISON_FEED_HOST}:{POISON_FEED_PORT} enabled={POISON_FEED_ENABLED}", flush=True)
    print(f"[SNIFFER] Packet log path: {PACKET_LOG_PATH}", flush=True)
    print(f"[SNIFFER] Window log path: {WINDOW_LOG_PATH}", flush=True)
    print(f"[SNIFFER] Window length: {WINDOW_SECONDS:.3f} seconds", flush=True)
    print(f"[SNIFFER] Window flush poll: {WINDOW_FLUSH_POLL_SECONDS:.3f} seconds", flush=True)
    print(f"[SNIFFER] Debug print interval: {DEBUG_PRINT_INTERVAL:.3f} seconds", flush=True)

    # Bootstrap the transparent proxy before the first FL client connects.
    # Without this announcement, the sniffer must observe one real client flow
    # before it can teach the proxy the server address. That first connection
    # is then already established in conntrack and can bypass a later REDIRECT.
    if POISON_FEED_ENABLED and FALLBACK_SERVER_IP:
        bootstrap = {
            "timestamp": time.time(),
            "server_ip": FALLBACK_SERVER_IP,
            "server_port": FL_PORT,
            "fl_port": FL_PORT,
            "type": "server_bootstrap",
            "command": "server_announce",
            "source": "configured_fallback_before_client_traffic",
        }
        send_to_poison_proxy(bootstrap)
        print(
            f"[SNIFFER] Bootstrap server announcement sent to proxy: "
            f"{FALLBACK_SERVER_IP}:{FL_PORT}",
            flush=True,
        )

    try:
        sniff(iface=INTERFACE, prn=process_packet, store=False)
    except KeyboardInterrupt:
        print("\n[SNIFFER] Stopping capture and flushing active windows...", flush=True)
    finally:
        flush_all_windows(notes="final flush before shutdown")


if __name__ == "__main__":
    main()
