#!/usr/bin/env python3
"""
Round quality, phase quality, and phase transition quality — CORRECTED aggregation.

Fixes the bug in the first pass: that version pooled every raw phase/round instance
across all experiments into one giant sample before computing mean +/- SD, which is
exactly the "wrong method of pooling all raw rows together" that five.py's own
docstring warns against. This version computes ONE summary value per experiment
folder first (matching five.py's exp1..expN unit), then combines those per-experiment
values into a final mean +/- SD per (Model, Condition) -- genuine between-experiment
variance, not within-experiment noise.

Client log = ground truth. analyzer_round_log / analyzer_phase_log = prediction.
"""
import pandas as pd, numpy as np, glob, os, hashlib
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

ROOT = "/home/lawrence/Lawrence/FL_poison"
OUT = "/tmp/claude-1000/-home-lawrence-Lawrence-FL-poison/3b6d8e61-2284-4915-8f6e-e313659a390c/scratchpad/quality_reports_v2"
TABLES = os.path.join(OUT, "tables")
FIGURES = os.path.join(OUT, "figures")
os.makedirs(TABLES, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)

PHASE_MAP = {"download": "DOWNLOAD", "fit": "TRAINING", "train": "TRAINING", "upload": "UPLOAD"}
TRACKS = ["RNN", "CNN", "Autoencoder"]
CONDITIONS = ["baseline", "attack"]

def dedup(files):
    seen = {}
    for f in sorted(files):
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        seen.setdefault(h, f)
    return list(seen.values())

def find_analyzer_logs(client_path, track):
    parts = client_path.split(os.sep)
    idx = parts.index(track)
    rel = parts[idx+1:-1]
    d = os.path.join(ROOT, "Result", track, "proxy", *rel)
    round_cands = glob.glob(os.path.join(d, "analyzer_round_log_*.csv"))
    phase_cands = glob.glob(os.path.join(d, "analyzer_phase_log_*.csv"))
    decision_cands = glob.glob(os.path.join(d, "analyzer_decision_log_*.csv"))
    return (d, round_cands[0] if round_cands else None,
            phase_cands[0] if phase_cands else None,
            decision_cands[0] if decision_cands else None)

def condition_of(path):
    return "attack" if "/attack/" in path else ("baseline" if "/baseline/" in path else None)

# ---- Gather matched tuples, grouped by EXPERIMENT FOLDER (the aggregation unit) ----
# experiment_key = analyzer folder path (e.g. Result/RNN/proxy/attack/fedavg/noise/exp3)
experiments = {t: {c: {} for c in CONDITIONS} for t in TRACKS}
for track in TRACKS:
    all_files = glob.glob(os.path.join(ROOT, "client_results", "*", track, "**", "client_metrics_log_*.csv"), recursive=True)
    client_files = dedup(all_files)
    for cf in client_files:
        cond = condition_of(cf)
        if cond is None:
            continue
        exp_dir, rlog, plog, dlog = find_analyzer_logs(cf, track)
        if rlog is None or plog is None:
            continue
        experiments[track][cond].setdefault(exp_dir, []).append((cf, rlog, plog, dlog))

print("Experiment folders (aggregation units) per track/condition:")
for t in TRACKS:
    for c in CONDITIONS:
        print(f"  {t} {c}: {len(experiments[t][c])} experiments, {sum(len(v) for v in experiments[t][c].values())} client files")

# ---- Compute ONE summary row per experiment folder ----
def summarize_experiment(track, cond, exp_dir, file_tuples):
    """One row: pools whatever client(s) map to this experiment, but this whole
    experiment contributes exactly ONE value per metric to the final aggregation."""
    round_valid = 0; round_total = 0
    seq_valid = 0; seq_total = 0
    phase_dur = {"IDLE": [], "DOWNLOAD": [], "TRAINING": [], "UPLOAD": []}
    y_true = []; y_pred = []
    decision_lags = []

    for cf, rlog, plog, dlog in file_tuples:
        try:
            cdf = pd.read_csv(cf, usecols=["client_id","round","phase","src_ip","phase_start","phase_end"])
        except Exception:
            continue
        cdf = cdf[cdf["phase"].isin(PHASE_MAP.keys())].copy()
        if cdf.empty or not cdf["src_ip"].notna().any():
            continue
        ip = cdf[cdf["src_ip"] != "127.0.0.1"]["src_ip"].mode()
        if ip.empty:
            continue
        ip = ip.iat[0]

        try:
            rdf = pd.read_csv(rlog, usecols=["client_id","round"])
        except Exception:
            rdf = pd.DataFrame(columns=["client_id","round"])
        try:
            pdf = pd.read_csv(plog, usecols=["client_id","round","phase","phase_start","phase_end","phase_duration_s"])
        except Exception:
            pdf = pd.DataFrame(columns=["client_id","round","phase","phase_start","phase_end","phase_duration_s"])

        r_sub = rdf[rdf["client_id"] == ip]
        p_sub = pdf[pdf["client_id"] == ip].copy()
        p_sub["phase_u"] = p_sub["phase"].map(lambda x: PHASE_MAP.get(x, x.upper() if isinstance(x,str) else x))

        analyzer_rounds = set(r_sub["round"].unique())
        client_rounds = sorted(cdf["round"].unique())
        p_by_round = {r: g.sort_values("phase_start") for r, g in p_sub.groupby("round")}

        for r in client_rounds:
            round_total += 1
            if r in analyzer_rounds:
                round_valid += 1

        for r in client_rounds:
            seq_total += 1
            g = p_by_round.get(r)
            if g is None:
                continue
            phases_in_order = list(g["phase_u"])
            if "DOWNLOAD" in phases_in_order and "TRAINING" in phases_in_order and "UPLOAD" in phases_in_order:
                d_i, t_i, u_i = phases_in_order.index("DOWNLOAD"), phases_in_order.index("TRAINING"), phases_in_order.index("UPLOAD")
                if d_i < t_i < u_i:
                    seq_valid += 1

        for r in client_rounds:
            g = p_by_round.get(r)
            if g is None:
                continue
            for _, row in g.iterrows():
                if row["phase_u"] in phase_dur:
                    phase_dur[row["phase_u"]].append(row["phase_duration_s"])

        cdf_r = cdf.copy()
        cdf_r["phase_u"] = cdf_r["phase"].map(PHASE_MAP)
        for r in client_rounds:
            true_rows = cdf_r[cdf_r["round"] == r]
            g = p_by_round.get(r)
            for _, trow in true_rows.iterrows():
                t_label = trow["phase_u"]; t_start, t_end = trow["phase_start"], trow["phase_end"]
                best_label, best_overlap = "NONE", 0.0
                if g is not None:
                    for _, prow in g.iterrows():
                        ov = max(0.0, min(t_end, prow["phase_end"]) - max(t_start, prow["phase_start"]))
                        if ov > best_overlap:
                            best_overlap = ov; best_label = prow["phase_u"]
                y_true.append(t_label); y_pred.append(best_label)

        if dlog:
            try:
                ddf = pd.read_csv(dlog, usecols=["client_id","decision_lag_ms"])
                lag = pd.to_numeric(ddf[ddf["client_id"] == ip]["decision_lag_ms"], errors="coerce")
                lag = lag[lag > 0]
                decision_lags.extend(lag.tolist())
            except Exception:
                pass

    # collapse this ONE experiment down to single summary values
    row = {
        "track": track, "condition": cond, "experiment": exp_dir,
        "round_quality": round_valid / round_total if round_total else np.nan,
        "seq_quality": seq_valid / seq_total if seq_total else np.nan,
        "n_rounds": round_total,
    }
    for ph in ["IDLE","DOWNLOAD","TRAINING","UPLOAD"]:
        arr = np.array(phase_dur[ph])
        row[f"phase_{ph.lower()}_duration_mean_s"] = arr.mean() if len(arr) else np.nan

    if y_true:
        prec, rec, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=["DOWNLOAD","TRAINING","UPLOAD"], zero_division=0)
        for ph, p, rc, f in zip(["DOWNLOAD","TRAINING","UPLOAD"], prec, rec, f1):
            row[f"{ph.lower()}_precision"] = p
            row[f"{ph.lower()}_recall"] = rc
            row[f"{ph.lower()}_f1"] = f
        cm = confusion_matrix(y_true, y_pred, labels=["DOWNLOAD","TRAINING","UPLOAD","NONE"])
        row["_cm"] = cm
        row["_n_classified"] = len(y_true)
    else:
        for ph in ["download","training","upload"]:
            row[f"{ph}_precision"] = np.nan; row[f"{ph}_recall"] = np.nan; row[f"{ph}_f1"] = np.nan
        row["_cm"] = None
        row["_n_classified"] = 0

    lags = np.array(decision_lags)
    row["decision_lag_mean_ms"] = lags.mean() if len(lags) else np.nan

    return row

per_experiment_rows = []
for track in TRACKS:
    for cond in CONDITIONS:
        for exp_dir, tuples in experiments[track][cond].items():
            per_experiment_rows.append(summarize_experiment(track, cond, exp_dir, tuples))

per_exp_df = pd.DataFrame(per_experiment_rows)
print("\nPer-experiment summary rows:", len(per_exp_df))
print(per_exp_df.groupby(["track","condition"]).size())

import pickle
with open(os.path.join(OUT, "per_experiment.pkl"), "wb") as f:
    pickle.dump(per_experiment_rows, f)
