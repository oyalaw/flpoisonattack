import pandas as pd, numpy as np, pickle, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/tmp/claude-1000/-home-lawrence-Lawrence-FL-poison/3b6d8e61-2284-4915-8f6e-e313659a390c/scratchpad/quality_reports_v2"
TABLES = os.path.join(OUT, "tables")
FIGURES = os.path.join(OUT, "figures")
TRACKS = ["RNN", "CNN", "Autoencoder"]
CONDITIONS = ["baseline", "attack"]
PHASES = ["IDLE","DOWNLOAD","TRAINING","UPLOAD"]
COLOR = {"baseline": "#2471A3", "attack": "#C0392B"}

with open(os.path.join(OUT, "per_experiment.pkl"), "rb") as f:
    rows = pickle.load(f)
per_exp_df = pd.DataFrame(rows)

def mean_sd(series):
    x = pd.to_numeric(series, errors="coerce").dropna()
    if len(x) == 0: return np.nan, np.nan, 0
    if len(x) == 1: return float(x.iloc[0]), 0.0, 1
    return float(x.mean()), float(x.std(ddof=1)), int(len(x))

def fmt(mean, sd):
    if pd.isna(mean): return "N/A"
    sd = 0.0 if pd.isna(sd) else sd
    return f"{mean:.3f} ± {sd:.3f}"

# ============ tbl01: Phase Inference Quality — mean±SD ACROSS experiments ============
rows01 = []
for track in TRACKS:
    for cond in CONDITIONS:
        g = per_exp_df[(per_exp_df.track==track) & (per_exp_df.condition==cond)]
        row = {"Model": track, "Condition": cond.capitalize(), "N_experiments": len(g)}
        for ph in PHASES:
            m, s, n = mean_sd(g[f"phase_{ph.lower()}_duration_mean_s"])
            row[ph] = fmt(m, s)
        rows01.append(row)
tbl01 = pd.DataFrame(rows01)
tbl01.to_csv(os.path.join(TABLES, "tbl01_phase_inference_quality.csv"), index=False)
print(tbl01.to_string(index=False)); print()

# ============ tbl02/tbl13: Round Tracking & Phase Transition Quality — mean±SD across experiments ============
rows_round, rows_seq = [], []
for track in TRACKS:
    for cond in CONDITIONS:
        g = per_exp_df[(per_exp_df.track==track) & (per_exp_df.condition==cond)]
        m, s, n = mean_sd(g["round_quality"])
        rows_round.append({"Model": track, "Condition": cond.capitalize(), "N_experiments": n, "Round Tracking Quality": fmt(m, s)})
        m2, s2, n2 = mean_sd(g["seq_quality"])
        rows_seq.append({"Model": track, "Condition": cond.capitalize(), "N_experiments": n2, "Sequence Quality": fmt(m2, s2)})
tbl13 = pd.DataFrame(rows_round)
tbl02 = pd.DataFrame(rows_seq)
tbl13.to_csv(os.path.join(TABLES, "tbl13_round_tracking_quality.csv"), index=False)
tbl02.to_csv(os.path.join(TABLES, "tbl02_phase_transition_quality.csv"), index=False)
print(tbl13.to_string(index=False)); print()
print(tbl02.to_string(index=False)); print()

# ============ tbl11: Phase Classification Quality — mean±SD across experiments ============
rows11 = []
for track in TRACKS:
    for cond in CONDITIONS:
        g = per_exp_df[(per_exp_df.track==track) & (per_exp_df.condition==cond)]
        for ph in ["download","training","upload"]:
            pm, ps, pn = mean_sd(g[f"{ph}_precision"])
            rm, rs, rn = mean_sd(g[f"{ph}_recall"])
            fm, fs, fn = mean_sd(g[f"{ph}_f1"])
            rows11.append({"Model": track, "Condition": cond.capitalize(), "Phase": ph.upper(),
                            "N_experiments": pn,
                            "Precision": fmt(pm, ps), "Recall": fmt(rm, rs), "F1": fmt(fm, fs)})
tbl11 = pd.DataFrame(rows11)
tbl11.to_csv(os.path.join(TABLES, "tbl11_phase_classification_quality.csv"), index=False)
print(tbl11.to_string(index=False)); print()

# ============ tbl12: Phase Confusion Matrix — SUM of per-experiment confusion matrices ============
LABELS = ["DOWNLOAD","TRAINING","UPLOAD","NONE"]
cm_rows = []
for track in TRACKS:
    for cond in CONDITIONS:
        g = per_exp_df[(per_exp_df.track==track) & (per_exp_df.condition==cond)]
        total_cm = np.zeros((4,4), dtype=int)
        for cm in g["_cm"]:
            if cm is not None:
                total_cm += cm
        for i, tl in enumerate(LABELS):
            for j, pl in enumerate(LABELS):
                cm_rows.append({"Model": track, "Condition": cond.capitalize(), "True phase": tl, "Predicted phase": pl, "Count": int(total_cm[i,j])})
tbl12 = pd.DataFrame(cm_rows)
tbl12.to_csv(os.path.join(TABLES, "tbl12_phase_confusion_matrix.csv"), index=False)

# ============ tbl14: Phase Detection Latency — mean±SD across experiments ============
rows14 = []
for track in TRACKS:
    for cond in CONDITIONS:
        g = per_exp_df[(per_exp_df.track==track) & (per_exp_df.condition==cond)]
        m, s, n = mean_sd(g["decision_lag_mean_ms"])
        rows14.append({"Model": track, "Condition": cond.capitalize(), "N_experiments": n, "Decision Lag (ms)": fmt(m, s)})
tbl14 = pd.DataFrame(rows14)
tbl14.to_csv(os.path.join(TABLES, "tbl14_phase_detection_latency.csv"), index=False)
print(tbl14.to_string(index=False))

per_exp_df.drop(columns=["_cm"]).to_csv(os.path.join(TABLES, "per_experiment_summary.csv"), index=False)
print("\nSaved. Per-experiment audit trail in per_experiment_summary.csv")
