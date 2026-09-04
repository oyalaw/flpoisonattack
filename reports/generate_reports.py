#!/usr/bin/env python3
"""
Regenerates the Run-Validation Ledger, Attack Execution Funnel, and Model-Impact
reports directly from the experiment's own log files (no numbers are hand-entered).

Scans, by default:
  - <repo_root>/                       (in-progress/live runs dumped at top level)
  - <repo_root>/Result/RNN/            (proxy AND server-side logs, post-restructure --
    the old separate <repo_root>/poison_experiment_from_dgx/ tree no longer exists;
    server_metrics_log/server_client_defense_log/etc. now live alongside the proxy
    files under Result/RNN/proxy/<condition>/<defense>/<attack>/exp*/)

Result/ also now holds Result/CNN, Result/Autoencoder, Result/Transformer from other
model tracks -- deliberately NOT scanned by default (see --model) to avoid mixing
different model architectures' baselines into the same pool. CNN's server logs use
a different phase-label convention (lowercase "download"/"fit"/"upload" vs RNN's
"server_download"/"server_upload") that parse_server_metrics does not currently
handle -- passing --model CNN would silently return empty trajectories, not an error.

Data sources read per run:
  - proxy_attack_events_*.csv   -> delivery funnel (targeted==1 rows only)
  - server_metrics_log_*.csv    -> accuracy trajectory (phase == server_download)
  - proxy_run_manifest_*.json / server_run_manifest_*.json -> sha256 fingerprints,
    experiment_id/run_id, requested vs effective defense, attack params

Runs are joined on `experiment_id`, the one identifier both proxy and server sides
write independently (confirmed by inspection, not assumed) into every CSV row and
manifest for a given launch. A known duplication (Result/RNN/proxy/RNN/... mirrors
Result/RNN/proxy/... byte-for-byte) is harmless -- both copies share the same
experiment_id and collapse into one record automatically.

Usage:
    python3 reports/generate_reports.py
    python3 reports/generate_reports.py --root /path/to/FL_poison --out reports/out --html
    python3 reports/generate_reports.py --model CNN   # different model track, see caveat above
"""

import argparse
import csv
import glob
import hashlib
import html
import json
import os
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Config: folder/defense-name normalization. The same defense is spelled
# differently across baseline vs attack folders and across the two source
# trees (fedAvg / fedavg, multi_krum / multi-krum, trim / trimmed_mean).
# ---------------------------------------------------------------------------
DEFENSE_ALIASES = {
    "fedavg": "fedavg", "fedavg_blind": "fedavg",
    "krum": "krum",
    "multi_krum": "multi-krum", "multi-krum": "multi-krum", "multikrum": "multi-krum",
    "median": "median",
    "trim": "trimmed-mean", "trimmed_mean": "trimmed-mean", "trimmed-mean": "trimmed-mean",
    "flame": "flame",
}

# Delivery-rate buckets used by the validity heuristic below.
LOW_DELIVERY_MAX = 0.15
MID_DELIVERY_MAX = 0.60

# Attacks dropped from every report entirely, by user decision -- e.g.
# krum_optimal, which is structurally infeasible against half this project's
# defenses (n>=2f+3 peer requirement the 5-client testbed can't satisfy) and
# was excluded from analysis rather than reported as a partial/inconsistent
# picture.
EXCLUDED_ATTACKS = {"krum_optimal"}


def normalize_defense(name):
    if not name:
        return None
    return DEFENSE_ALIASES.get(name.strip().lower(), name.strip().lower())


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def find_files(roots, filename_glob, exclude_prefixes=None):
    # exclude_prefixes matters because one of `roots` is typically the bare
    # repo root (to catch in-progress files dumped there), and that root's
    # recursive glob will also walk into Result/<other-model> subtrees no
    # matter what Result/<model> was explicitly requested -- scoping the
    # Result/ root alone does not stop that. Excluded here, not by trusting
    # callers to only pass a narrow root.
    exclude_prefixes = [os.path.realpath(p) for p in (exclude_prefixes or [])]
    seen = set()
    out = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in glob.glob(os.path.join(root, "**", filename_glob), recursive=True):
            real = os.path.realpath(path)
            if real in seen:
                continue
            if any(real == p or real.startswith(p + os.sep) for p in exclude_prefixes):
                continue
            seen.add(real)
            out.append(path)
    return out


def path_condition(path):
    """baseline vs attack/poisoned, inferred from the path itself, not filename."""
    parts = [p.lower() for p in path.split(os.sep)]
    if "baseline" in parts:
        return "baseline"
    if "attack" in parts or "poisoned" in parts:
        return "attack"
    return "unknown"


def path_defense_and_attack(path):
    parts = path.split(os.sep)
    lparts = [p.lower() for p in parts]
    defense = None
    attack = None
    for anchor in ("baseline", "attack", "poisoned"):
        if anchor in lparts:
            idx = lparts.index(anchor)
            if idx + 1 < len(parts):
                defense = normalize_defense(parts[idx + 1])
            if anchor in ("attack", "poisoned") and idx + 2 < len(parts):
                candidate = parts[idx + 2]
                if not candidate.lower().startswith("exp"):
                    attack = candidate.lower()
            break
    return defense, attack


# ---------------------------------------------------------------------------
# Proxy-side parsing: attack execution funnel
# ---------------------------------------------------------------------------

def parse_proxy_events(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None

    experiment_id = rows[0].get("experiment_id") or None
    raw_attack = next((r["raw_attack"] for r in rows if r.get("raw_attack")), "")
    active_defense = next((r["active_defense"] for r in rows if r.get("active_defense")), "")

    targeted_rows = [r for r in rows if r.get("targeted") == "1"]
    all_client_ips = sorted({r["client_ip"] for r in rows if r.get("client_ip")})
    target_ip = sorted({r["client_ip"] for r in targeted_rows}) or None

    gate_open = sum(1 for r in targeted_rows if r.get("phase_gate_open") == "1")
    delivered = sum(1 for r in targeted_rows if r.get("modified") == "1")
    fl_rounds = sorted({int(r["fl_round"]) for r in targeted_rows if r.get("fl_round", "").isdigit()})

    # attack_phase distinguishes rows still inside the configured warmup window
    # ("warmup") from rows the engine considered live candidates ("active") --
    # this is the "post-warmup eligible" stage of the execution funnel.
    active_rows = sum(1 for r in targeted_rows if r.get("attack_phase") == "active")
    warmup_rows = sum(1 for r in targeted_rows if r.get("attack_phase") == "warmup")
    delivered_of_active = sum(1 for r in targeted_rows if r.get("attack_phase") == "active" and r.get("modified") == "1")

    # "need n>=2f+3" is krum_optimal's own feasibility check reporting that the
    # peer pool is structurally too small for the configured f -- e.g. 4 client
    # peers can never satisfy n>=2*1+3=5. This is not a run that failed and
    # could be retried; it cannot succeed under the current client count, full
    # stop. Flagged separately so it isn't reported as an open experimental gap.
    infeasible_rows = sum(
        1 for r in targeted_rows
        if "need n>=2f+3" in (r.get("selection_reason") or "")
    )
    structurally_infeasible = (
        delivered == 0 and targeted_rows and infeasible_rows >= 0.5 * len(targeted_rows)
    )

    # "<attack>_needs_peers" in modification_reason means the attack's own
    # crafting logic (e.g. min_sum) couldn't compute a poison because this
    # proxy session never accumulated enough peer observations -- unlike
    # structurally_infeasible above, this is a per-run peer-registry gap, not
    # a hard mathematical wall; a rerun with better peer visibility could
    # still succeed. Kept as a distinct category so it isn't reported as
    # either an open "the defense stopped it" gap or folded into the
    # never-fixable infeasible bucket.
    peer_limited_rows = sum(
        1 for r in targeted_rows
        if (r.get("modification_reason") or "").endswith("_needs_peers")
    )
    peer_limited = (
        delivered == 0 and targeted_rows and peer_limited_rows >= 0.5 * len(targeted_rows)
    )

    return {
        "path": path,
        "experiment_id": experiment_id,
        "raw_attack": raw_attack or None,
        "active_defense": normalize_defense(active_defense) if active_defense else None,
        "target_client_ips": target_ip,
        "all_client_ips": all_client_ips,
        "n_rows_total": len(rows),
        "n_targeted_rows": len(targeted_rows),
        "n_target_rounds": len(fl_rounds),
        "round_min": fl_rounds[0] if fl_rounds else None,
        "round_max": fl_rounds[-1] if fl_rounds else None,
        "gate_open_count": gate_open,
        "active_count": active_rows,
        "warmup_count": warmup_rows,
        "delivered_count": delivered,
        "delivered_of_active_count": delivered_of_active,
        "delivery_rate": (delivered / len(targeted_rows)) if targeted_rows else None,
        "structurally_infeasible": structurally_infeasible,
        "peer_limited": peer_limited,
        "peer_limited_rows": peer_limited_rows,
        "mtime": os.path.getmtime(path),
    }


# ---------------------------------------------------------------------------
# Server-side parsing: accuracy trajectory / model impact
# ---------------------------------------------------------------------------

def parse_server_metrics(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None

    experiment_id = rows[0].get("experiment_id") or None
    requested_defense = next((r["requested_defense"] for r in rows if r.get("requested_defense")), "")

    # RNN logs use "server_download"; CNN's logs (added in the 2026-07-22
    # filesystem restructure) use plain "download" for the same role -- the
    # row where that round's post-aggregation accuracy is recorded. Accepting
    # both rather than assuming one convention project-wide.
    trajectory = []
    for r in rows:
        if r.get("phase") in ("server_download", "download") and r.get("accuracy"):
            try:
                trajectory.append((int(r["round"]), float(r["accuracy"])))
            except ValueError:
                continue
    trajectory.sort(key=lambda t: t[0])

    return {
        "path": path,
        "experiment_id": experiment_id,
        "requested_defense": normalize_defense(requested_defense) if requested_defense else None,
        "n_rounds": len(trajectory),
        "final_accuracy": trajectory[-1][1] if trajectory else None,
        "final_round": trajectory[-1][0] if trajectory else None,
        "trajectory": trajectory,
        "mtime": os.path.getmtime(path),
        "content_sha256": sha256_of_file(path),
    }


# ---------------------------------------------------------------------------
# Manifest parsing: code fingerprints + declared config
# ---------------------------------------------------------------------------

def parse_manifest(path):
    try:
        with open(path) as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    is_proxy = "proxy_run_id" in d or "proxy" in os.path.basename(path)
    sha = d.get("script_sha256")
    if not sha:
        # proxy manifests may nest it differently; fall back to a shallow search
        for v in d.values():
            if isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v):
                sha = v
                break
    return {
        "path": path,
        "kind": "proxy" if is_proxy else "server",
        "experiment_id": d.get("experiment_id"),
        "run_id": d.get("run_id"),
        "script_sha256": sha,
        "raw": d,
    }


# ---------------------------------------------------------------------------
# Grouping + classification
# ---------------------------------------------------------------------------

def build_run_records(roots, exclude_prefixes=None):
    proxy_files = find_files(roots, "proxy_attack_events_*.csv", exclude_prefixes)
    server_files = find_files(roots, "server_metrics_log_*.csv", exclude_prefixes)
    manifest_files = find_files(roots, "*_run_manifest_*.json", exclude_prefixes)

    records = defaultdict(lambda: {
        "experiment_id": None, "proxy": None, "server": None,
        "proxy_manifest": None, "server_manifest": None,
        "defense": None, "attack": None, "condition": None,
        "source_paths": [],
    })

    for path in proxy_files:
        _, path_attack = path_defense_and_attack(path)
        if path_attack in EXCLUDED_ATTACKS:
            continue
        parsed = parse_proxy_events(path)
        if not parsed or not parsed["experiment_id"]:
            continue
        if parsed.get("raw_attack") in EXCLUDED_ATTACKS:
            continue
        key = parsed["experiment_id"]
        rec = records[key]
        # Prefer the most recently modified file if the same experiment_id
        # somehow shows up under two source trees.
        if rec["proxy"] is None or parsed["mtime"] > rec["proxy"]["mtime"]:
            rec["proxy"] = parsed
        rec["source_paths"].append(path)
        defense, attack = path_defense_and_attack(path)
        rec["defense"] = rec["defense"] or defense
        rec["attack"] = rec["attack"] or attack
        if not rec["condition"] or rec["condition"] == "unknown":
            rec["condition"] = path_condition(path)

    for path in server_files:
        _, path_attack = path_defense_and_attack(path)
        if path_attack in EXCLUDED_ATTACKS:
            continue
        parsed = parse_server_metrics(path)
        if not parsed or not parsed["experiment_id"]:
            continue
        key = parsed["experiment_id"]
        rec = records[key]
        if rec["server"] is None or parsed["mtime"] > rec["server"]["mtime"]:
            rec["server"] = parsed
        rec["source_paths"].append(path)
        defense, attack = path_defense_and_attack(path)
        rec["defense"] = rec["defense"] or defense
        rec["attack"] = rec["attack"] or attack
        if not rec["condition"] or rec["condition"] == "unknown":
            rec["condition"] = path_condition(path)

    for path in manifest_files:
        _, path_attack = path_defense_and_attack(path)
        if path_attack in EXCLUDED_ATTACKS:
            continue
        parsed = parse_manifest(path)
        if not parsed or not parsed["experiment_id"]:
            continue
        key = parsed["experiment_id"]
        if key not in records:
            continue  # no proxy/server data survived exclusion for this run
        rec = records[key]
        slot = "proxy_manifest" if parsed["kind"] == "proxy" else "server_manifest"
        if rec[slot] is None or os.path.getmtime(path) > os.path.getmtime(rec[slot]["path"]):
            rec[slot] = parsed

    return records


def compute_baseline_stats(records):
    """Per-defense clean-baseline mean/min/max final accuracy, with byte-identical
    duplicate files (same content sha256) collapsed to a single data point and
    flagged, since a copied file is not an independent repetition."""
    by_defense = defaultdict(list)
    for exp_id, rec in records.items():
        if rec["condition"] != "baseline" or not rec["server"]:
            continue
        defense = rec["defense"] or rec["server"].get("requested_defense")
        if not defense or rec["server"]["final_accuracy"] is None:
            continue
        by_defense[defense].append((exp_id, rec["server"]))

    stats = {}
    for defense, items in by_defense.items():
        seen_hashes = set()
        deduped = []
        n_duplicate_files = 0
        for exp_id, server in items:
            h = server["content_sha256"]
            if h in seen_hashes:
                n_duplicate_files += 1
                continue
            seen_hashes.add(h)
            deduped.append((exp_id, server["final_accuracy"]))
        accs = [a for _, a in deduped]
        if not accs:
            continue
        stats[defense] = {
            "n": len(accs),
            "mean": statistics.mean(accs),
            "min": min(accs),
            "max": max(accs),
            "runs": deduped,
            "n_duplicate_files_collapsed": n_duplicate_files,
        }
    return stats


def classify_validity(rec, baseline_stats):
    """Documented heuristic, not a black box:
      1. No proxy log at all -> can't verify delivery -> 'pending' for attack
         conditions; baseline conditions need no delivery check.
      2. delivery_rate == 0 -> Invalid: no poisoned update delivered.
      3. delivery_rate in (0, 0.15] -> Partial: delivered, incomplete coverage.
      4. delivery_rate > 0.15 -> looks at whether final accuracy falls outside
         the defense's own baseline [min, max] band:
           - outside band -> Valid attack
           - inside band  -> Diagnostic-only: delivered, no measurable damage
    This mirrors, but does not silently replicate, this project's own manual
    calls earlier in the investigation -- inspect borderline cases yourself
    before citing them.
    """
    condition = rec["condition"]
    defense = rec["defense"]

    if condition == "baseline":
        n = baseline_stats.get(defense, {}).get("n", 0)
        if n >= 5:
            return "valid_baseline", f"n={n} independent runs"
        elif n > 0:
            return "partial_baseline", f"n={n} independent runs (want >=5)"
        else:
            return "unknown", "no server accuracy data found"

    if not rec["proxy"]:
        return "pending", "no proxy_attack_events log found for this experiment_id -- delivery unverified"

    rate = rec["proxy"]["delivery_rate"]
    if rate is None or rec["proxy"]["n_targeted_rows"] == 0:
        return "pending", "proxy log exists but has zero rows for the target client"

    if rec["proxy"].get("structurally_infeasible"):
        return "infeasible", (
            "attack's own feasibility check reports the peer pool is too small "
            "for the configured f (needs n>=2f+3) -- cannot deliver under the "
            "current client count regardless of reruns, not an open gap"
        )

    if rec["proxy"].get("peer_limited"):
        n = rec["proxy"]["peer_limited_rows"]
        total = rec["proxy"]["n_targeted_rows"]
        return "peer_limited", (
            f"{n}/{total} targeted rounds blocked by the attack's own "
            "'_needs_peers' crafting check (insufficient peer observations "
            "in this proxy session) -- a per-run peer-visibility gap, not a "
            "defense outcome; may succeed on a rerun with better peer "
            "registry population"
        )

    if rate == 0:
        return "invalid", "0% of targeted rounds had a poisoned update delivered"

    base = baseline_stats.get(defense)
    accuracy_known = bool(rec["server"] and rec["server"]["final_accuracy"] is not None)
    direction = None  # 'below' (degraded), 'above' (improved/anomalous), or None (inside band)
    if base and accuracy_known:
        acc = rec["server"]["final_accuracy"]
        if acc < base["min"]:
            direction = "below"
        elif acc > base["max"]:
            direction = "above"

    if rate <= LOW_DELIVERY_MAX:
        return "partial", f"only {rate:.0%} delivery -- incomplete coverage"

    if not accuracy_known:
        return "pending", f"{rate:.0%} delivery confirmed, but no server_metrics_log accuracy found for this experiment_id -- impact unknown, not yet 'no measurable damage'"
    if direction is None and base is None:
        return "pending", f"{rate:.0%} delivery confirmed, but no baseline band available to judge impact"
    if direction == "below":
        return "valid_attack", f"{rate:.0%} delivery, final accuracy BELOW baseline floor [{base['min']:.4f}, {base['max']:.4f}] -- degradation"
    if direction == "above":
        return "anomalous", f"{rate:.0%} delivery, final accuracy ABOVE baseline ceiling [{base['min']:.4f}, {base['max']:.4f}] -- attack delivered but accuracy improved, inspect before citing"
    return "diagnostic_only", f"{rate:.0%} delivery, final accuracy within baseline noise band"


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

VALIDITY_LABELS = {
    "valid_baseline": "Valid baseline",
    "partial_baseline": "Partial baseline (n<5)",
    "valid_attack": "Valid attack (degraded)",
    "anomalous": "Anomalous (delivered, accuracy improved -- inspect)",
    "diagnostic_only": "Diagnostic-only (delivered, no measurable damage)",
    "partial": "Partial (delivered, incomplete coverage)",
    "invalid": "Invalid (no poisoned update delivered)",
    "infeasible": "Structurally infeasible (not an open gap -- see rationale)",
    "peer_limited": "Peer-visibility-limited (per-run gap, not infeasible)",
    "pending": "Classification pending (missing data)",
    "unknown": "Unknown",
}


def write_ledger(records, baseline_stats, out_dir):
    path = os.path.join(out_dir, "validation_ledger.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["experiment_id", "defense", "attack", "condition", "rounds",
                    "delivered", "delivery_rate", "final_accuracy", "validity",
                    "rationale", "server_script_sha256", "analyzer_or_proxy_sha256"])
        for exp_id, rec in sorted(records.items(), key=lambda kv: (kv[1]["defense"] or "", kv[1]["attack"] or "", kv[0])):
            tag, rationale = classify_validity(rec, baseline_stats)
            proxy = rec["proxy"]
            server = rec["server"]
            w.writerow([
                exp_id,
                rec["defense"] or "",
                rec["attack"] or ("baseline" if rec["condition"] == "baseline" else ""),
                rec["condition"] or "",
                server["n_rounds"] if server else (proxy["n_target_rounds"] if proxy else ""),
                f"{proxy['delivered_count']}/{proxy['n_targeted_rows']}" if proxy and proxy["n_targeted_rows"] else "",
                f"{proxy['delivery_rate']:.2%}" if proxy and proxy["delivery_rate"] is not None else "",
                f"{server['final_accuracy']:.4f}" if server and server["final_accuracy"] is not None else "",
                VALIDITY_LABELS.get(tag, tag),
                rationale,
                (rec["server_manifest"] or {}).get("script_sha256", "") or "",
                (rec["proxy_manifest"] or {}).get("script_sha256", "") or "",
            ])
    return path


def write_funnel(records, out_dir):
    path = os.path.join(out_dir, "attack_funnel.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["experiment_id", "defense", "attack", "target_rounds_observed",
                    "phase_gate_open", "gate_open_rate", "delivered", "delivery_rate_of_gated",
                    "delivery_rate_of_all"])
        for exp_id, rec in sorted(records.items(), key=lambda kv: (kv[1]["defense"] or "", kv[1]["attack"] or "")):
            proxy = rec["proxy"]
            if not proxy or rec["condition"] != "attack" or not proxy["n_targeted_rows"]:
                continue
            n = proxy["n_targeted_rows"]
            gate = proxy["gate_open_count"]
            delivered = proxy["delivered_count"]
            w.writerow([
                exp_id, rec["defense"] or "", rec["attack"] or "",
                n, gate, f"{gate/n:.2%}" if n else "",
                delivered,
                f"{delivered/gate:.2%}" if gate else "",
                f"{delivered/n:.2%}" if n else "",
            ])
    return path


def write_model_impact(records, baseline_stats, out_dir):
    path = os.path.join(out_dir, "model_impact.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["experiment_id", "defense", "attack", "baseline_mean", "baseline_min",
                    "baseline_max", "baseline_n", "final_accuracy", "delta_pp",
                    "relative_degradation_pct", "band_position"])
        for exp_id, rec in sorted(records.items(), key=lambda kv: (kv[1]["defense"] or "", kv[1]["attack"] or "")):
            if rec["condition"] != "attack" or not rec["server"] or rec["server"]["final_accuracy"] is None:
                continue
            defense = rec["defense"]
            base = baseline_stats.get(defense)
            acc = rec["server"]["final_accuracy"]
            if not base:
                w.writerow([exp_id, defense or "", rec["attack"] or "", "", "", "", 0,
                            f"{acc:.4f}", "", "", ""])
                continue
            delta_pp = (acc - base["mean"]) * 100
            rel = (base["mean"] - acc) / base["mean"] * 100 if base["mean"] else ""
            if acc < base["min"]:
                band = "below_floor"
            elif acc > base["max"]:
                band = "above_ceiling"
            else:
                band = "inside_range"
            w.writerow([
                exp_id, defense or "", rec["attack"] or "",
                f"{base['mean']:.4f}", f"{base['min']:.4f}", f"{base['max']:.4f}", base["n"],
                f"{acc:.4f}", f"{delta_pp:+.2f}", f"{rel:.1f}" if rel != "" else "",
                band,
            ])
    return path


def write_json_dump(records, baseline_stats, out_dir):
    path = os.path.join(out_dir, "report_data.json")
    serializable = {}
    for exp_id, rec in records.items():
        serializable[exp_id] = {
            "defense": rec["defense"], "attack": rec["attack"], "condition": rec["condition"],
            "proxy": rec["proxy"], "server": rec["server"],
            "server_script_sha256": (rec["server_manifest"] or {}).get("script_sha256"),
            "proxy_script_sha256": (rec["proxy_manifest"] or {}).get("script_sha256"),
        }
    with open(path, "w") as f:
        json.dump({"runs": serializable, "baseline_stats": baseline_stats}, f, indent=2, default=str)
    return path


HTML_CSS = """
:root {
  color-scheme: light;
  --paper: #F3F5F6; --surface: #FCFCFC; --surface-2: #EFF2F4;
  --ink: #10161C; --ink-2: #47525C; --ink-muted: #7C8791;
  --hairline: #DCE1E5;
  --accent: #2A78D6; --accent-soft: #CDE2FB; --accent-ink: #184F95;
  --good: #0CA30C; --warning-mark: #C98500; --critical: #D03B3B; --muted-mark: #8993A0;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --paper: #0C1014; --surface: #151A20; --surface-2: #1B2128;
    --ink: #EEF1F3; --ink-2: #B8C1C9; --ink-muted: #808A93;
    --hairline: #262D34;
    --accent: #5C9EEA; --accent-soft: #1C3A5E; --accent-ink: #BBD8F8;
    --good: #3FC23F; --warning-mark: #E0A63A; --critical: #E5665F; --muted-mark: #9AA4AD;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #0C1014; --surface: #151A20; --surface-2: #1B2128;
  --ink: #EEF1F3; --ink-2: #B8C1C9; --ink-muted: #808A93;
  --hairline: #262D34;
  --accent: #5C9EEA; --accent-soft: #1C3A5E; --accent-ink: #BBD8F8;
  --good: #3FC23F; --warning-mark: #E0A63A; --critical: #E5665F; --muted-mark: #9AA4AD;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink);
  font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.6; }
.page { max-width: 1040px; margin: 0 auto; padding: 48px 24px 96px; }
h1, h2, h3 { font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; font-weight: 600; }
code, .mono { font-family: ui-monospace, "SF Mono", Consolas, monospace; }
header { border-bottom: 1px solid var(--hairline); padding-bottom: 24px; margin-bottom: 32px; }
.eyebrow { font-family: ui-monospace, monospace; font-size: 12px; letter-spacing: .06em; text-transform: uppercase;
  color: var(--accent-ink); background: var(--accent-soft); display: inline-block; padding: 3px 8px; border-radius: 3px; margin-bottom: 12px; }
h1 { font-size: 26px; margin: 0 0 8px; }
.subtitle { color: var(--ink-2); font-size: 14.5px; max-width: 70ch; margin: 0 0 14px; }
.provenance { font-size: 12px; color: var(--ink-muted); display: flex; flex-wrap: wrap; gap: 4px 16px; }
.stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1px; background: var(--hairline);
  border: 1px solid var(--hairline); border-radius: 6px; overflow: hidden; margin-bottom: 36px; }
.stat-tile { background: var(--surface); padding: 14px 16px; }
.stat-value { font-size: 20px; font-weight: 600; font-family: ui-monospace, monospace; }
.stat-label { font-size: 11px; color: var(--ink-muted); margin-top: 2px; }
section { margin-bottom: 48px; }
h2 { font-size: 19px; margin: 0 0 4px; }
.section-dek { color: var(--ink-2); font-size: 13.5px; margin: 4px 0 16px; max-width: 76ch; }
.table-scroll { overflow-x: auto; border: 1px solid var(--hairline); border-radius: 6px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; min-width: 720px; }
th, td { padding: 8px 11px; text-align: left; font-size: 12.5px; border-bottom: 1px solid var(--hairline); white-space: nowrap; }
th { color: var(--ink-muted); font-weight: 600; text-transform: uppercase; letter-spacing: .02em; font-size: 10px; background: var(--surface-2); }
tr:last-child td { border-bottom: none; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
.pill { display: inline-flex; align-items: center; gap: 5px; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.pill.valid { background: rgba(12,163,12,.14); color: var(--good); }
.pill.invalid { background: rgba(208,59,59,.12); color: var(--critical); }
.pill.partial { background: rgba(201,133,0,.15); color: var(--warning-mark); }
.pill.anomalous { background: rgba(201,133,0,.15); color: var(--warning-mark); }
.pill.pending { background: var(--surface-2); color: var(--ink-muted); }
.funnel { display: flex; flex-direction: column; border: 1px solid var(--hairline); border-radius: 8px; overflow: hidden; background: var(--surface); margin-bottom: 18px; }
.funnel-head { padding: 10px 16px; border-bottom: 1px solid var(--hairline); font-size: 13px; font-weight: 600; display: flex; justify-content: space-between; gap: 10px; }
.funnel-row { display: grid; grid-template-columns: 190px 1fr 70px; align-items: center; gap: 12px; padding: 7px 16px; border-bottom: 1px solid var(--hairline); }
.funnel-row:last-child { border-bottom: none; }
.funnel-label { font-size: 12px; color: var(--ink-2); }
.funnel-bar-track { background: var(--surface-2); border-radius: 4px; height: 16px; overflow: hidden; }
.funnel-bar-fill { height: 100%; background: var(--accent); border-radius: 4px; }
.funnel-count { font-family: ui-monospace, monospace; font-size: 12px; text-align: right; }
footer { margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--hairline); font-size: 11.5px; color: var(--ink-muted); }
"""

VALIDITY_PILL_CLASS = {
    "valid_baseline": "valid", "valid_attack": "valid",
    "invalid": "invalid",
    "partial": "partial", "partial_baseline": "partial", "anomalous": "anomalous",
    "diagnostic_only": "pending", "pending": "pending", "unknown": "pending",
    "infeasible": "pending", "peer_limited": "pending",
}


def render_html(records, baseline_stats, out_dir, generated_at):
    sorted_recs = sorted(records.items(), key=lambda kv: (kv[1]["defense"] or "", kv[1]["attack"] or "", kv[0]))

    tag_counts = defaultdict(int)
    ledger_rows_html = []
    for exp_id, rec in sorted_recs:
        tag, rationale = classify_validity(rec, baseline_stats)
        tag_counts[tag] += 1
        proxy, server = rec["proxy"], rec["server"]
        delivered_str = f"{proxy['delivered_count']}/{proxy['n_targeted_rows']}" if proxy and proxy["n_targeted_rows"] else "—"
        rate_str = f"{proxy['delivery_rate']:.0%}" if proxy and proxy["delivery_rate"] is not None else "—"
        acc_str = f"{server['final_accuracy']:.2%}" if server and server["final_accuracy"] is not None else "—"
        pill_class = VALIDITY_PILL_CLASS.get(tag, "pending")
        ledger_rows_html.append(f"""<tr>
          <td class="mono">{html.escape(exp_id)}</td>
          <td>{html.escape(rec['defense'] or '—')}</td>
          <td>{html.escape(rec['attack'] or ('baseline' if rec['condition']=='baseline' else '—'))}</td>
          <td class="num">{delivered_str}</td>
          <td class="num">{rate_str}</td>
          <td class="num">{acc_str}</td>
          <td><span class="pill {pill_class}">{html.escape(VALIDITY_LABELS.get(tag, tag))}</span></td>
          <td style="white-space:normal; color:var(--ink-muted); font-size:11.5px;">{html.escape(rationale)}</td>
        </tr>""")

    funnel_html = []
    for exp_id, rec in sorted_recs:
        proxy = rec["proxy"]
        if rec["condition"] != "attack" or not proxy or not proxy["n_targeted_rows"]:
            continue
        n = proxy["n_targeted_rows"]

        def bar(label, count):
            pct = (count / n * 100) if n else 0
            return f"""<div class="funnel-row">
              <div class="funnel-label">{label}</div>
              <div class="funnel-bar-track"><div class="funnel-bar-fill" style="width:{pct:.1f}%"></div></div>
              <div class="funnel-count">{count}</div>
            </div>"""

        funnel_html.append(f"""<div class="funnel">
          <div class="funnel-head"><span>{html.escape(rec['defense'] or '?')} &middot; {html.escape(rec['attack'] or '?')}</span>
          <span class="mono" style="color:var(--ink-muted); font-weight:400;">{html.escape(exp_id)}</span></div>
          {bar('Target uploads observed', n)}
          {bar('Eligible after phase gate', proxy['gate_open_count'])}
          {bar('Post-warmup candidates', proxy['active_count'])}
          {bar('Poisoned payloads delivered', proxy['delivered_count'])}
        </div>""")

    impact_rows_html = []
    for exp_id, rec in sorted_recs:
        if rec["condition"] != "attack" or not rec["server"] or rec["server"]["final_accuracy"] is None:
            continue
        base = baseline_stats.get(rec["defense"])
        acc = rec["server"]["final_accuracy"]
        if not base:
            continue
        delta_pp = (acc - base["mean"]) * 100
        color = "var(--critical)" if acc < base["min"] else ("var(--warning-mark)" if acc > base["max"] else "var(--ink-muted)")
        band = "below floor" if acc < base["min"] else ("above ceiling" if acc > base["max"] else "inside range")
        impact_rows_html.append(f"""<tr>
          <td>{html.escape(rec['defense'])} &middot; {html.escape(rec['attack'] or '?')}</td>
          <td class="num">{base['mean']:.2%}</td>
          <td class="num">{acc:.2%}</td>
          <td class="num" style="color:{color}; font-weight:600;">{delta_pp:+.2f}pp</td>
          <td style="color:{color};">{band}</td>
        </tr>""")

    n_total = len(sorted_recs)
    n_attack = sum(1 for _, r in sorted_recs if r["condition"] == "attack")
    n_valid_attack = tag_counts.get("valid_attack", 0)
    n_invalid = tag_counts.get("invalid", 0)
    n_pending = tag_counts.get("pending", 0)

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>FL Poisoning -- Run-Validation Report</title>
<style>{HTML_CSS}</style></head>
<body><div class="page">

<header>
  <div class="eyebrow">Auto-generated by reports/generate_reports.py -- not hand-edited</div>
  <h1>Run-Validation, Attack-Funnel &amp; Model-Impact Report</h1>
  <p class="subtitle">Computed directly from proxy_attack_events / server_metrics_log / run-manifest files discovered on disk. Nothing below is estimated or carried over from a prior conversation.</p>
  <div class="provenance">
    <span>Generated {html.escape(generated_at)}</span>
    <span>{n_total} experiment_id runs discovered</span>
    <span>{n_attack} attack-condition runs</span>
  </div>
</header>

<div class="stat-strip">
  <div class="stat-tile"><div class="stat-value" style="color:var(--good);">{n_valid_attack}</div><div class="stat-label">Valid attack</div></div>
  <div class="stat-tile"><div class="stat-value" style="color:var(--critical);">{n_invalid}</div><div class="stat-label">Invalid (0% delivered)</div></div>
  <div class="stat-tile"><div class="stat-value" style="color:var(--warning-mark);">{tag_counts.get('anomalous',0)}</div><div class="stat-label">Anomalous (delivered, acc. improved)</div></div>
  <div class="stat-tile"><div class="stat-value" style="color:var(--ink-muted);">{tag_counts.get('diagnostic_only',0)}</div><div class="stat-label">Diagnostic-only</div></div>
  <div class="stat-tile"><div class="stat-value">{n_pending}</div><div class="stat-label">Classification pending</div></div>
  <div class="stat-tile"><div class="stat-value" style="color:var(--ink-muted);">{tag_counts.get('infeasible',0)}</div><div class="stat-label">Structurally infeasible (not a gap)</div></div>
  <div class="stat-tile"><div class="stat-value" style="color:var(--ink-muted);">{tag_counts.get('peer_limited',0)}</div><div class="stat-label">Peer-visibility-limited (per-run)</div></div>
</div>

<section>
  <h2>Run-Validation Ledger</h2>
  <p class="section-dek">Every discovered experiment_id, classified by the documented heuristic in <code>classify_validity()</code> -- delivery-rate bucket crossed with baseline-band position. Inspect the rationale column before citing a borderline case.</p>
  <div class="table-scroll"><table>
    <thead><tr><th>Experiment</th><th>Defense</th><th>Attack</th><th>Delivered</th><th>Rate</th><th>Final Acc.</th><th>Validity</th><th>Rationale</th></tr></thead>
    <tbody>{''.join(ledger_rows_html)}</tbody>
  </table></div>
</section>

<section>
  <h2>Attack Execution Funnel</h2>
  <p class="section-dek">Target-client rows only, staged by the proxy's own <code>phase_gate_open</code> / <code>attack_phase</code> / <code>modified</code> fields.</p>
  {''.join(funnel_html) if funnel_html else '<p style="color:var(--ink-muted);">No attack-condition runs with proxy data found.</p>'}
</section>

<section>
  <h2>Model Impact</h2>
  <p class="section-dek">Final accuracy vs. each defense's own clean-baseline mean, for every attack run with server-side accuracy data (regardless of whether delivery was independently confirmed -- check the Validity column above).</p>
  <div class="table-scroll"><table>
    <thead><tr><th>Defense &middot; Attack</th><th>Baseline mean</th><th>Final acc.</th><th>&Delta;A</th><th>Band position</th></tr></thead>
    <tbody>{''.join(impact_rows_html)}</tbody>
  </table></div>
</section>

<footer>Source: {html.escape(out_dir)} -- regenerate with <code>python3 reports/generate_reports.py --html</code>.</footer>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     help="FL_poison repo root (default: parent of this script's directory)")
    ap.add_argument("--out", default=None, help="Output directory (default: <root>/reports/out)")
    ap.add_argument("--html", action="store_true", help="Also render reports/out/report.html")
    ap.add_argument("--model", default="RNN",
                     help="Model subtree under Result/ to scan (default: RNN, this project's focus). "
                          "Result/ now also holds CNN/Autoencoder/Transformer runs after the filesystem "
                          "restructure -- scanning all of Result/ blindly would mix different model "
                          "architectures into the same baseline pool. Pass --model CNN etc. to switch, "
                          "or --model ALL to scan everything (not recommended without also fixing the "
                          "phase-label parsing, which is RNN-specific -- see parse_server_metrics).")
    args = ap.parse_args()

    root = args.root
    out_dir = args.out or os.path.join(root, "reports", "out")
    os.makedirs(out_dir, exist_ok=True)

    result_dir = os.path.join(root, "Result")
    exclude_prefixes = []
    if args.model.upper() == "ALL":
        result_root = result_dir
    else:
        result_root = os.path.join(result_dir, args.model)
        # Result/ may hold sibling model subtrees (CNN, Autoencoder, ...) --
        # since `root` (repo root) is also a search root and its recursive
        # glob would otherwise still walk into them, exclude explicitly.
        if os.path.isdir(result_dir):
            exclude_prefixes = [
                os.path.join(result_dir, name)
                for name in os.listdir(result_dir)
                if name != args.model and os.path.isdir(os.path.join(result_dir, name))
            ]
    roots = [root, result_root]
    records = build_run_records(roots, exclude_prefixes)

    if not records:
        print("No runs discovered under:", roots, file=sys.stderr)
        sys.exit(1)

    baseline_stats = compute_baseline_stats(records)

    ledger_path = write_ledger(records, baseline_stats, out_dir)
    funnel_path = write_funnel(records, out_dir)
    impact_path = write_model_impact(records, baseline_stats, out_dir)
    json_path = write_json_dump(records, baseline_stats, out_dir)

    written = [ledger_path, funnel_path, impact_path, json_path]
    if args.html:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        html_str = render_html(records, baseline_stats, out_dir, generated_at)
        html_path = os.path.join(out_dir, "report.html")
        with open(html_path, "w") as f:
            f.write(html_str)
        written.append(html_path)

    print(f"Discovered {len(records)} distinct experiment_id runs.")
    print("Baseline stats:")
    for defense, s in sorted(baseline_stats.items()):
        dup_note = f" ({s['n_duplicate_files_collapsed']} byte-identical duplicate files collapsed)" if s["n_duplicate_files_collapsed"] else ""
        print(f"  {defense:14s} n={s['n']}  mean={s['mean']:.4f}  range=[{s['min']:.4f}, {s['max']:.4f}]{dup_note}")
    print()
    print("Wrote:")
    for p in written:
        print(" ", p)


if __name__ == "__main__":
    main()
