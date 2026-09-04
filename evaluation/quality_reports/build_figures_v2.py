import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/tmp/claude-1000/-home-lawrence-Lawrence-FL-poison/3b6d8e61-2284-4915-8f6e-e313659a390c/scratchpad/quality_reports_v2"
TABLES = os.path.join(OUT, "tables")
FIGURES = os.path.join(OUT, "figures")
TRACKS = ["RNN", "CNN", "Autoencoder"]
CONDITIONS = ["Baseline", "Attack"]
COLOR = {"Baseline": "#2471A3", "Attack": "#C0392B"}

def parse(v):
    if v == "N/A": return np.nan, np.nan
    m, s = v.split(" ± ")
    return float(m), float(s)

def save(fig, name):
    fig.savefig(os.path.join(FIGURES, f"{name}.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES, f"{name}.eps"), bbox_inches="tight")
    plt.close(fig)

tbl01 = pd.read_csv(os.path.join(TABLES, "tbl01_phase_inference_quality.csv"))
fig, ax = plt.subplots(figsize=(12, 5))
labels, means, sds = [], [], []
for _, row in tbl01.iterrows():
    for ph in ["IDLE","DOWNLOAD","TRAINING","UPLOAD"]:
        m, s = parse(row[ph])
        if pd.isna(m): continue
        labels.append(f"{row['Model']}\n{row['Condition']}\n{ph}")
        means.append(m); sds.append(s)
x = np.arange(len(labels))
ax.bar(x, means, yerr=sds, capsize=3, color="#4A6FA5")
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=8)
ax.set_yscale("log"); ax.set_ylabel("Duration (s), log scale")
ax.set_title("Phase Inference Quality: Mean Phase Duration (mean ± SD across experiments)")
save(fig, "fig01_phase_inference_quality")

for tbl_name, val_col, title, fname in [
    ("tbl13_round_tracking_quality.csv", "Round Tracking Quality", "Round Tracking Quality", "fig13_round_tracking_quality"),
    ("tbl02_phase_transition_quality.csv", "Sequence Quality", "Phase Transition (Sequence) Quality", "fig02_phase_transition_quality"),
]:
    df = pd.read_csv(os.path.join(TABLES, tbl_name))
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(len(TRACKS)); width = 0.35
    for i, cond in enumerate(CONDITIONS):
        sub = df[df["Condition"] == cond].set_index("Model").reindex(TRACKS)
        m = sub[val_col].apply(lambda v: parse(v)[0]) * 100
        s = sub[val_col].apply(lambda v: parse(v)[1]) * 100
        ax.bar(x + (i - 0.5) * width, m, width, yerr=s, capsize=3, label=cond, color=COLOR[cond])
    ax.set_xticks(x); ax.set_xticklabels(TRACKS)
    ax.set_ylabel("Valid (%)"); ax.set_ylim(0, 110)
    ax.set_title(title + " (mean ± SD across experiments)"); ax.legend()
    save(fig, fname)

tbl11 = pd.read_csv(os.path.join(TABLES, "tbl11_phase_classification_quality.csv"))
fig, ax = plt.subplots(figsize=(11, 5))
labels = tbl11["Model"] + "\n" + tbl11["Condition"] + "\n" + tbl11["Phase"]
f1_m = tbl11["F1"].apply(lambda v: parse(v)[0])
f1_s = tbl11["F1"].apply(lambda v: parse(v)[1])
x = np.arange(len(labels))
ax.bar(x, f1_m, yerr=f1_s, capsize=3, color="#4A6FA5")
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=65, ha="right", fontsize=8)
ax.set_ylim(0, 1.05); ax.set_ylabel("F1 score")
ax.set_title("Phase Classification Quality (mean ± SD across experiments)")
save(fig, "fig11_phase_classification_quality")

tbl12 = pd.read_csv(os.path.join(TABLES, "tbl12_phase_confusion_matrix.csv"))
LABELS = ["DOWNLOAD","TRAINING","UPLOAD","NONE"]
combos = [(t,c) for t in TRACKS for c in CONDITIONS]
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
for ax, (track, cond) in zip(axes.flat, combos):
    sub = tbl12[(tbl12["Model"]==track) & (tbl12["Condition"]==cond)]
    mat = sub.pivot(index="True phase", columns="Predicted phase", values="Count").reindex(index=LABELS, columns=LABELS).fillna(0)
    row_sums = mat.values.sum(axis=1, keepdims=True)
    mat_norm = np.divide(mat.values, row_sums, out=np.zeros_like(mat.values, dtype=float), where=row_sums!=0)
    im = ax.imshow(mat_norm, vmin=0, vmax=1, cmap="Blues")
    ax.set_xticks(range(4)); ax.set_xticklabels(LABELS, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(4)); ax.set_yticklabels(LABELS, fontsize=8)
    ax.set_title(f"{track} {cond}", fontsize=10)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{mat.values[i,j]:.0f}", ha="center", va="center", fontsize=7,
                     color="white" if mat_norm[i,j] > 0.5 else "black")
fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.6, label="Row-normalized fraction")
fig.suptitle("Phase Confusion Matrix (summed across experiments; true=client log, pred=analyzer phase_log)")
save(fig, "fig12_phase_confusion_matrix")

tbl14 = pd.read_csv(os.path.join(TABLES, "tbl14_phase_detection_latency.csv"))
fig, ax = plt.subplots(figsize=(7.5, 4.5))
good = tbl14[tbl14["Decision Lag (ms)"].notna()].copy()
good["mean"] = good["Decision Lag (ms)"].apply(lambda v: parse(v)[0])
good["sd"] = good["Decision Lag (ms)"].apply(lambda v: parse(v)[1])
labels = good["Model"] + "\n" + good["Condition"]
ax.bar(labels, good["mean"], yerr=good["sd"], capsize=4, color="#4A6FA5")
ax.set_ylabel("Decision lag (ms)")
ax.set_title("Phase Detection Latency (mean ± SD across experiments)")
save(fig, "fig14_phase_detection_latency")

print("done:", os.listdir(FIGURES))
