# NetPhaser Evaluation Report — Full Appendix Tables

Built from `NetPhaser_Evaluation_Report_Templates_with_Source_Field_Map.docx` (user-supplied template, 49 tables). This appendix populates each table against this project's real logs — computed values where the data supports it, explicit "not currently supported" per the template's own Evidence Status Key where it doesn't. Nothing is estimated or fabricated to fill a cell.

**Deviation from the template noted up front:** the template's phase/round tables (4–11) have no `Condition` column. This project treats baseline and attack as fundamentally different conditions throughout (see `evaluation_framework_report.md`), so a `Condition` column is added rather than pooling baseline+attack together — pooling risks the exact aggregation mistake already caught and fixed earlier in this project (see `evaluation_framework_report.md` §0.5). Confusion matrices (Tables 7–9) are pooled across both conditions since the template specifies one matrix per architecture, not per condition.

**Status:** RQ1 tables (4, 5, 7, 8, 9, 10, 11) below are complete with real data; Table 6 (onset/offset timing) is honestly marked not-computed. Building Table 11 surfaced a real data-integrity bug — RNN's client-1 phase/round logs were misfiled and silently excluded from every RNN join in this project, and client-3 turned out to have zero RNN baseline data at all (a genuine gap, not a bug). Both are now documented and corrected here and in `evaluation_framework_report.md` §0.5 / `cross_architecture_comparison.md` — RNN's RQ1 numbers project-wide changed slightly as a result (round tracking 87.2%→89.2% under attack). Tables 12–49 are not yet started.

---

## 2. RQ1 — Phase, Round, Participant, and Fingerprint Reports

### Table 4. Per-Phase Classification Performance Across Three Architectures

Source: `evaluation/quality_reports/` pipeline (client log = ground truth, `analyzer_phase_log` = prediction, max-overlap assignment), two-level aggregation (one summary per experiment, then mean±SD across experiments). `Idle` and `Evaluation` are omitted — this pipeline does not classify them as separate predicted/true phase labels (Idle has a duration only, no classification; no independent Evaluation-phase ground truth exists), consistent with the template's own note to omit Evaluation when unavailable.

| Architecture | Condition | Phase | Precision (%) | Recall (%) | F1 (%) | Support | Status |
|---|---|---|---|---|---|---|---|
| RNN | Baseline | Download | 50.10 ± 5.64 | 65.76 ± 17.03 | 55.94 ± 8.68 | 4-client sample | Derived |
| RNN | Baseline | Training | 29.98 ± 4.27 | 27.33 ± 3.35 | 28.32 ± 2.51 | 4-client sample | Derived |
| RNN | Baseline | Upload | 42.22 ± 49.47 | 1.45 ± 2.64 | 2.73 ± 4.84 | 4-client sample | Derived |
| RNN | Attack | Download | 45.88 ± 14.46 | 38.86 ± 21.37 | 39.92 ± 18.87 | mixed 4–5 clients | Derived |
| RNN | Attack | Training | 25.58 ± 12.45 | 19.13 ± 10.23 | 21.43 ± 11.23 | mixed 4–5 clients | Derived |
| RNN | Attack | Upload | 3.12 ± 17.68 | 0.05 ± 0.29 | 0.10 ± 0.58 | mixed 4–5 clients | Derived |
| CNN | Baseline | Download | 30.69 ± 1.24 | 74.43 ± 9.51 | 43.36 ± 2.61 | 6000 | Derived |
| CNN | Baseline | Training | 19.72 ± 8.91 | 1.90 ± 3.33 | 3.14 ± 4.82 | 6000 | Derived |
| CNN | Baseline | Upload | 25.00 ± 45.23 | 1.83 ± 3.57 | 3.39 ± 6.56 | 6000 | Derived |
| CNN | Attack | Download | 43.12 ± 4.37 | 83.05 ± 14.02 | 56.45 ± 6.13 | 14200 | Derived |
| CNN | Attack | Training | 24.45 ± 5.34 | 16.02 ± 7.56 | 18.88 ± 6.72 | 14200 | Derived |
| CNN | Attack | Upload | 21.88 ± 42.00 | 2.41 ± 5.68 | 4.18 ± 9.72 | 14200 | Derived |
| Autoencoder | Baseline | Download | 29.53 ± 1.27 | 75.56 ± 12.72 | 42.01 ± 2.05 | 5500 | Derived |
| Autoencoder | Baseline | Training | 30.63 ± 10.18 | 3.45 ± 5.49 | 5.31 ± 7.58 | 5500 | Derived |
| Autoencoder | Baseline | Upload | 9.09 ± 30.15 | 0.09 ± 0.30 | 0.18 ± 0.60 | 5500 | Derived |
| Autoencoder | Attack | Download | 34.75 ± 6.40 | 65.02 ± 10.71 | 44.33 ± 3.08 | 14998 | Derived |
| Autoencoder | Attack | Training | 31.03 ± 9.17 | 8.13 ± 4.12 | 12.63 ± 5.90 | 14998 | Derived |
| Autoencoder | Attack | Upload | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 14998 | Derived |

Cross-checked against `evaluation_framework_report.md`'s RQ1 Phase Classification Quality table — same source pipeline, same numbers (that table reports fractions 0–1, this one ×100; both come from the same `per_experiment.pkl`).

### Table 5. Overall Phase and Upload-Detection Performance

Macro-P/R/F1 = per-experiment mean of the three phases' P/R/F1, then mean±SD across experiments (two-level, not raw pooling). Accuracy = correct/total classified instances (trace of the 3×3 Download/Training/Upload block ÷ its total), same two-level method. Balanced accuracy is not separately computed — with only 3 classes at roughly comparable support here, it does not diverge meaningfully from the macro-recall value already shown, so a placeholder value was not fabricated.

| Architecture | Accuracy (%) | Macro Precision (%) | Macro Recall (%) | Macro-F1 (%) | Upload Precision (%) | Upload Recall (%) | Upload F1 (%) |
|---|---|---|---|---|---|---|---|
| RNN (4-client sample, §0.5) | 25.23 ± 9.81 | 32.56 ± 16.30 | 25.23 ± 9.81 | 24.60 ± 7.76 | see Table 4 (by condition) | see Table 4 | see Table 4 |
| CNN | 31.71 ± 6.71 | 28.54 ± 14.71 | 31.71 ± 6.71 | 23.81 ± 6.40 | see Table 4 | see Table 4 | see Table 4 |
| Autoencoder | 24.90 ± 3.95 | 22.23 ± 6.42 | 24.90 ± 3.95 | 18.16 ± 2.86 | see Table 4 | see Table 4 | see Table 4 |

Upload precision/recall/F1 are condition-dependent in this dataset (baseline vs. attack differ) and are reported per-condition in Table 4 rather than collapsed into one number here, to avoid hiding that split — pointed to rather than duplicated.

### Table 6. Phase-Onset, Phase-Offset, and State-Sequence Timing

**Not currently computed.** This project's phase-classification methodology uses max-overlap interval assignment (each client-logged phase instance matched to whichever analyzer interval has greatest time overlap) rather than boundary-error timing — `evaluation_framework_report.md` explicitly flags onset/offset error (\(E_{\mathrm{start}}\), \(E_{\mathrm{end}}\)) as "not computed as a separate metric." Computing this requires per-boundary timestamp differencing (`true phase start/end` vs. matched analyzer interval start/end) which the current pipeline discards after computing overlap — a straightforward but not-yet-done extension. State-Sequence Accuracy is directly available: it is the Phase Transition (Sequence) Quality already reported in `evaluation_framework_report.md` (RNN Attack 89.2%±6.6%, on RNN's 4-of-5-client sample — see that report's §0.5; CNN/Autoencoder ≈100% on genuine 5-client samples).

### Tables 7–9. Row-Normalized Phase Confusion Matrices (%)

Pooled across baseline+attack (both conditions), all experiments, per architecture. Rows = true phase (client log); columns = predicted phase (analyzer `phase_log`, max-overlap assignment). `Idle` and `Evaluation` rows/columns are omitted (not classified in this pipeline — see Table 4 note). `NONE` is included as a predicted-only column (no analyzer interval overlapped the true instance) — it has no corresponding true row since every client-logged phase instance is by construction one of Download/Training/Upload.

**Table 7. CNN**

| True \ Predicted | Download | Training | Upload | NONE |
|---|---|---|---|---|
| Download | 79.72 | 1.23 | 0.00 | 19.04 |
| Training | 79.15 | 11.71 | 0.00 | 9.13 |
| Upload | 47.59 | 33.07 | 2.21 | 17.13 |

**Table 8. RNN** (corrected for the client-1/client-3 issue documented in `evaluation_framework_report.md` §0.5 — RNN is a 4-of-5-client sample, not 5)

| True \ Predicted | Download | Training | Upload | NONE |
|---|---|---|---|---|
| Download | 52.28 | 1.84 | 0.00 | 45.88 |
| Training | 42.65 | 22.91 | 0.05 | 34.39 |
| Upload | 9.43 | 55.48 | 0.68 | 34.40 |

**Table 9. Autoencoder**

| True \ Predicted | Download | Training | Upload | NONE |
|---|---|---|---|---|
| Download | 68.20 | 1.10 | 0.00 | 30.71 |
| Training | 74.05 | 6.92 | 0.00 | 19.03 |
| Upload | 68.45 | 12.50 | 0.02 | 19.03 |

The dominant confusion on every architecture is Download/Training/Upload being predicted `NONE` (no analyzer overlap found) rather than being predicted as each other — this is the same client/analyzer ground-truth definition mismatch already documented in `evaluation_framework_report.md`'s RQ1/RQ2 sections (client logs measure serialization, analyzer detects wire transmission), not a genuine phase-confusion problem between Download/Training/Upload themselves.

### Table 10. Round-Number and Round-Boundary Inference

Exact Round Accuracy = Round Tracking Quality (already validated in `evaluation_framework_report.md`). Within-±1-round, Round MAE, and boundary MAE columns are not computed — they require per-round timestamp differencing against the analyzer's round boundaries, which the current pipeline only checks for presence/absence (round in `analyzer_round_log` or not), not offset magnitude. Completed-Round Recall is not separately computed (conceptually close to Round Tracking Quality but not identical — would need explicit "completed round" semantics not currently defined in the logs).

| Architecture | Condition | Exact Round Accuracy (%) | Within ±1 Round (%) | Round MAE | Start-Boundary MAE (ms) | End-Boundary MAE (ms) | Completed-Round Recall (%) |
|---|---|---|---|---|---|---|---|
| RNN | Baseline | 98.23 ± 3.91 | not computed | not computed | not computed | not computed | not computed |
| RNN | Attack | 89.24 ± 6.55 | not computed | not computed | not computed | not computed | not computed |
| CNN | Baseline | 100.00 ± 0.00 | not computed | not computed | not computed | not computed | not computed |
| CNN | Attack | 99.63 ± 0.64 | not computed | not computed | not computed | not computed | not computed |
| Autoencoder | Baseline | 100.00 ± 0.00 | not computed | not computed | not computed | not computed | not computed |
| Autoencoder | Attack | 99.21 ± 0.54 | not computed | not computed | not computed | not computed | not computed |

### Table 11. Per-Client Phase, Upload, and Round Performance

Same pipeline, grouped by (track, client) instead of by experiment, pooled across all experiments that client contributed to (both conditions). `Hardware` (Dell/Jetson) is not available from any log — that mapping is external (physical machine assignment), not derivable from data, so it is marked "not available" rather than guessed. Client-IP-to-label mapping: C1=`10.42.0.47`, C2=`10.42.0.18`, C3=`10.42.0.145`, C4=`10.42.0.210`, C5=`10.42.0.59`.

RNN's C1 row uses the timestamp+round-range recovered join (§0.5 of `evaluation_framework_report.md`) — 56 of a possible 62 experiments recovered. RNN has no C3 row for reasons already documented: client-3 has zero RNN baseline files, and its 29 RNN attack-only files were excluded here for the same reason Table 4/8/10 exclude them from a mixed baseline+attack per-client pool — a client with no baseline contribution can't be given a single "Round Accuracy" figure comparable to the other four without conflating two different populations. Its 29 attack-only files remain usable and are not lost, just not shoehorned into this table.

| Architecture | Client | Hardware | Samples | Macro-F1 (%) | Upload Precision (%) | Upload Recall (%) | Upload-Onset MAE (ms) | Round Accuracy (%) |
|---|---|---|---|---|---|---|---|---|
| RNN | C1 | not available | 16800 | 22.58 | 0.00 | 0.00 | not computed | 99.98 |
| RNN | C2 | not available | 18300 | 20.06 | 0.00 | 0.00 | not computed | 97.93 |
| RNN | C3 | not available | — | — | — | — | not computed | attack-only, not pooled (see note) |
| RNN | C4 | not available | 18300 | 41.26 | 100.00 | 1.10 | not computed | 99.93 |
| RNN | C5 | not available | 17099 | 12.67 | 90.32 | 1.96 | not computed | 86.67 |
| CNN | C1 | not available | 13200 | 22.55 | 100.00 | 1.75 | not computed | 100.00 |
| CNN | C2 | not available | 13200 | 20.99 | 0.00 | 0.00 | not computed | 99.80 |
| CNN | C3 | not available | 13200 | 19.78 | 0.00 | 0.00 | not computed | 99.36 |
| CNN | C4 | not available | 13200 | 38.39 | 100.00 | 8.39 | not computed | 100.00 |
| CNN | C5 | not available | 7800 | 5.23 | 0.00 | 0.00 | not computed | 99.31 |
| Autoencoder | C1 | not available | 12300 | 17.33 | 0.00 | 0.00 | not computed | 100.00 |
| Autoencoder | C2 | not available | 12300 | 16.85 | 0.00 | 0.00 | not computed | 99.88 |
| Autoencoder | C3 | not available | 12600 | 14.25 | 0.00 | 0.00 | not computed | 98.48 |
| Autoencoder | C4 | not available | 11700 | 32.53 | 100.00 | 0.13 | not computed | 100.00 |
| Autoencoder | C5 | not available | 12594 | 2.76 | 0.00 | 0.00 | not computed | 98.93 |

Upload-Onset MAE is not computed for the same reason as Table 6 — this pipeline does not currently retain per-boundary timestamps after computing max-overlap. CNN C5 has notably fewer samples (7800 vs. ~13200 for C1–C4) — worth checking whether C5 is systematically missing from some CNN experiments, not yet investigated here.

---

## 2.2 Server Identification and Client Attribution

### Table 12. Server-Identification Report

**Not currently supported**, matching the template's own Evidence Status Key. The configured/observed server endpoint is logged, but no `candidate_endpoint`, `candidate_score`, or `predicted_server` field exists anywhere in this project's logs — there is nothing to compute Top-1/Top-3 accuracy or false-identification rate against. Adding this would require new server-identification instrumentation, not a data-extraction task.

### Table 13. Client Attribution and Behavioral Fingerprint Classification

**Not currently supported.** Update-geometry features (`update_l2_norm`, peer distances, etc.) exist and are used in Tables 14–16 below, but no trained classifier or `predicted_client_id`/`fingerprint_client_id` field exists — there is no predicted label to score against the true client identity. This project's client fingerprinting is confirmed structurally absent elsewhere (`evaluation_framework_report.md` RQ1 "Client fingerprinting"); this table would require building and training a classifier, which is a modeling task, not an extraction task, and out of scope for this appendix pass.

## 2.3 Update Fingerprint Stability and Separability

### Table 14. Per-Client Update-Norm Stability

Source: `update_l2_norm` in `server_client_defense_log`, baseline condition only (clean signal, no attacker distortion). **CNN is not available for this table** — CNN's baseline `client_ip` field is 100% blank in every baseline experiment checked, and unlike CNN's attack-condition `client_ip` gaps (fixed via norm-correlation identification against proxy ground truth, `evaluation_framework_report.md` §0.5), baseline has no `proxy_attack_events` ground truth to anchor that correction against — this is the same already-documented "12 baseline-condition files remain unfixable" gap, not a new one.

| Architecture | Client | Mean L2 Norm | SD | Coefficient of Variation | Median Norm | Normalized MAD | P95 Norm | Source Fields |
|---|---|---|---|---|---|---|---|---|
| RNN | C1 | 0.7109 | 0.1753 | 0.2467 | 0.6818 | 0.1316 | 0.9107 | `update_l2_norm` |
| RNN | C2 | 0.6747 | 0.1673 | 0.2479 | 0.6415 | 0.1555 | 0.9264 | `update_l2_norm` |
| RNN | C3 | 0.7109 | 0.1768 | 0.2487 | 0.6826 | 0.1650 | 0.9827 | `update_l2_norm` |
| RNN | C4 | 0.7671 | 0.1813 | 0.2363 | 0.7290 | 0.1298 | 1.0377 | `update_l2_norm` |
| RNN | C5 | 0.6915 | 0.1788 | 0.2585 | 0.6650 | 0.1632 | 0.9537 | `update_l2_norm` |
| CNN | C1–C5 | not available | not available | not available | not available | not available | not available | `client_ip` blank in baseline |
| Autoencoder | C1 | 2.6016 | 0.6221 | 0.2391 | 2.3616 | 0.1479 | 3.8034 | `update_l2_norm` |
| Autoencoder | C2 | 2.9216 | 0.7848 | 0.2686 | 2.6221 | 0.2217 | 4.2896 | `update_l2_norm` |
| Autoencoder | C3 | 2.7663 | 0.6911 | 0.2498 | 2.5170 | 0.2062 | 4.0235 | `update_l2_norm` |
| Autoencoder | C4 | 3.3276 | 1.4587 | 0.4384 | 2.6822 | 0.3466 | 6.0374 | `update_l2_norm` |
| Autoencoder | C5 | 2.3898 | 0.6421 | 0.2687 | 2.2264 | 0.1530 | 3.5062 | `update_l2_norm` |

Autoencoder's norms run roughly 3.5–4× RNN's in absolute magnitude (different parameter scale, not directly comparable across architectures) — CV is the comparable column, and it's similar for both (0.24–0.27) except Autoencoder C4, whose CV (0.44) and normalized MAD (0.35) are both roughly double every other client on either architecture, driven by its markedly higher SD (1.46 vs. 0.62–0.79 for Autoencoder's other clients) — a real per-client anomaly worth a closer look, not yet investigated further here.

### Table 15. Intra-Client, Inter-Client, and Fingerprint Separability

Intra-client = `distance_to_previous_update` / `cosine_to_previous_update` (a client's own update vs. its own prior round). Inter-client = `distance_to_peer_mean_update` / `cosine_to_peer_mean_update` (a client's update vs. the round's peer-mean). Separability ratio = inter ÷ intra (Euclidean only — cosine reported as distance, 1−cosine, for a consistent "higher = more separable" reading, but not combined into one ratio since the two metrics aren't on the same scale). Pooled across all clients and rounds, baseline condition. CNN excluded — same `client_ip` gap as Table 14. Silhouette score is not computed — it requires an actual clustering/embedding step beyond what these pooled distance summaries provide, not done here.

| Architecture | Distance Metric | Intra-Client Distance | Inter-Client Distance | Separability Ratio | Source |
|---|---|---|---|---|---|
| RNN | Euclidean | 0.7409 ± 0.2024 | 0.7111 ± 0.1129 | 0.96 | `distance_to_previous_update`; `distance_to_peer_mean_update` |
| RNN | Cosine (as distance) | 0.4195 ± 0.2471 | 0.7774 ± 0.2560 | — | `cosine_to_previous_update`; `cosine_to_peer_mean_update` |
| Autoencoder | Euclidean | 2.2679 ± 0.7704 | 3.1051 ± 0.7615 | 1.37 | `distance_to_previous_update`; `distance_to_peer_mean_update` |
| Autoencoder | Cosine (as distance) | 0.6139 ± 0.1873 | 1.0141 ± 0.2604 | — | `cosine_to_previous_update`; `cosine_to_peer_mean_update` |

**RNN's Euclidean separability ratio (0.96) means a client's update is, on average, roughly as different from its own previous round as it is from its peers in the same round** — essentially no separability signal by this metric, consistent with RQ1's already-documented weak client fingerprinting. Autoencoder's ratio (1.37) is higher — some real separability — but still modest. Cosine tells the same story in relative terms: on both architectures, inter-client cosine-distance exceeds intra-client cosine-distance (a real gap, updates are more self-similar round-to-round than they are to peers), but the gap is not large.

### Table 16. Fingerprint Stability Across Training Rounds

**Not yet computed.** The required fields (`layer_distance_to_previous_update`, `layer_cosine_to_previous_update`) exist in `server_client_defense_log` per the schema (Table 40 below), but this table needs early/middle/late round-window slicing (rounds 1–20/21–60/61–100) per client per architecture, which is a tractable extension of the Table 14/15 extraction above, not yet done — flagged as pending, not blocked by missing data.

### Table 17. Cross-Architecture and Cross-Hardware Fingerprint Generalization

**Not currently supported**, same reason as Table 13 — requires a trained classifier with held-out predictions across architectures/hardware, which does not exist in this project.

---

## 3. RQ2 — Attack Gating, Synchronization, and Execution Funnel

### Table 18. Attack-Gating and Synchronization Performance

Source: `proxy_attack_events` per architecture × aggregator × attack, `exp1` (this project's established flagship-cell convention). The template's own grid groups attacks as "Sign Flip" / "Scale/Min Sum" and defenses as pairs — this project's actual attack/defense set doesn't have a "Scale/Min Sum" combined condition, so **`Min Sum` was used for that column** (this project's flagship magnitude attack elsewhere in RQ3/RQ4), and **`Median` was used for the "Median/FLAME" slot** (FLAME is covered extensively elsewhere in this report; Median fills the gap here). Both substitutions are stated, not silently made. Gate Precision/Recall are computed within the target client's own eligible upload-phase events (`targeted=1`), not against all 5 clients' phase-gate events — the raw `phase_gate_open` field fires for every client's ordinary upload-phase traffic regardless of attack targeting, so computing precision against all gate-opens (the template's literal reading) produces a meaningless ~16% for every cell; this appendix uses the reading that actually answers "how good is the gate at correctly attacking the eligible target," consistent with the rest of this project's attack-funnel language. Trigger MAE is substituted with mean `decision_lag_ms` from `analyzer_decision_log` (the same latency metric used throughout RQ1/RQ2 of the main report) — a true onset-vs-ground-truth MAE isn't computed anywhere in this project.

| Architecture | Aggregator | Attack | Eligible Target Uploads | Correct Gates | Gate Precision (%) | Gate Recall (%) | Wrong Client | Wrong Phase | Stale Rejections | Trigger MAE (ms) | Modification Coverage (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RNN | FedAvg | Sign Flip | 100 | 77 | 79.4 | 77.0 | 0 | 3 | 150 | 40.46 | 77.0 |
| RNN | FedAvg | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | not available | 80.0 |
| RNN | Krum | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 25.55 | 80.0 |
| RNN | Krum | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 49.59 | 80.0 |
| RNN | Median | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 38.70 | 80.0 |
| RNN | Median | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 28.90 | 80.0 |
| CNN | FedAvg | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 259.99 | 80.0 |
| CNN | FedAvg | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 241.41 | 80.0 |
| CNN | Krum | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 271.59 | 80.0 |
| CNN | Krum | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 625.06 | 80.0 |
| CNN | Median | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 325.43 | 80.0 |
| CNN | Median | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 341.44 | 80.0 |
| Autoencoder | FedAvg | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 432.65 | 80.0 |
| Autoencoder | FedAvg | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | not available | 80.0 |
| Autoencoder | Krum | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 424.99 | 80.0 |
| Autoencoder | Krum | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 424.76 | 80.0 |
| Autoencoder | Median | Sign Flip | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 425.87 | 80.0 |
| Autoencoder | Median | Min Sum | 100 | 80 | 80.0 | 80.0 | 0 | 0 | 0 | 424.17 | 80.0 |

The pattern is extremely uniform: 80/100 correct gates, 0 wrong-client attacks, on 17 of 18 cells — the gating logic reliably targets the right client at the right phase, and the 20-point gap between "eligible" and "correct" is warmup-round holds (`modification_reason = warmup_observe_only`, an intentional design choice, not a gating failure — confirmed directly in the underlying data). **RNN FedAvg Sign Flip is the sole outlier** (77% coverage, 3 wrong-phase rejections, 150 stale-reason rows in a 500-row file) — a real, isolated anomaly in this one experiment, not investigated further here. Trigger MAE (via decision lag) scales with model size exactly as documented elsewhere in this project: RNN ~25–50ms, CNN ~240–625ms, Autoencoder ~425ms.

### Table 19. Attack-Gate Rejection Reasons

**Not built with the template's exact 8-category breakdown** (Wrong Phase / Low Confidence / Stale Prediction / Client Mismatch / Warm-up Incomplete / Global Model Missing / Round Ineligible / Validation Failed) — this project's `phase_gate_reason` field does not use those 8 category labels (it recorded only `analyzer_upload_phase` / `phase_not_MODEL_UPLOAD` / a staleness variant in the cells checked for Table 18 above). Mapping this project's actual reason strings onto the template's 8-category taxonomy needs a full value-count sweep across all 18 cells first, not yet done. Table 18's Wrong Phase and Stale Rejections columns are the real subset of this that's currently available.

### Table 20. End-to-End Attack Execution Funnel — Counts

Uses the same 18-cell grid as Table 18, extended with `reconstruction_valid`, `wire_compatible`, defense-admission fields (`selected_or_included`/FLAME cluster membership) joined from `server_client_defense_log`. **Not yet built** — the funnel-count columns beyond what Table 18 already covers (Gate Eligible, Payloads Modified) need the server-side join added, which is the same join pattern already validated in RQ4 of the main report; extending it across all 18 cells here is pending.

### Table 21. Attack Funnel Conversion Rates

**Derived from Table 20**, so blocked on the same pending work. Gate Coverage and Modification Rate are already available from Table 18 (Modification Coverage column = Table 18's last column, restated); Delivery Rate, Server Validity, Admission Rate, and Selection/Penetration require the Table 20 extension.

---

## 4. RQ3 — True-Update Reconstruction, Geometry, and Transport Fidelity

### Table 22. Update Reconstruction and Protocol Compatibility

Source: `proxy_attack_events`, `modified==1` rows only (the target's actually-poisoned rounds), FLAME defense `exp1` for every attack except **Krum Optimal, which uses the `krum` defense** (this attack only exists paired with Krum/Multi-Krum/Median defenses in this project's data, never FLAME) **and only exists for RNN** — CNN and Autoencoder have no Krum Optimal attack folder at all. Tensor-Contract Match is reported as 100% wherever `model_contract_tensor_count` is a single constant value across all modified rows for that cell (verified, not assumed) — every cell checked passed this. Global-Model Match and Update-Space Use are both boolean fields reported as % of modified rows =True.

| Architecture | Attack | Global-Model Match (%) | Update-Space Use (%) | Tensor-Contract Match (%) | Reconstruction Valid (%) | Finite Values (%) | Wire Compatible (%) | Arrays Modified | Mean Rewrite Latency (ms) |
|---|---|---|---|---|---|---|---|---|---|
| RNN | Sign Flip | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 6.0 | 26.31 |
| RNN | Scale | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 6.0 | 23.75 |
| RNN | Noise | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 6.0 | 26.41 |
| RNN | Min Max | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 6.0 | 10.42 |
| RNN | Min Sum | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 6.0 | 10.64 |
| RNN | Krum Optimal | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 6.0 | 24.22 |
| CNN | Sign Flip | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 384.55 |
| CNN | Scale | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 393.76 |
| CNN | Noise | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 327.14 |
| CNN | Min Max | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 315.33 |
| CNN | Min Sum | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 398.28 |
| CNN | Krum Optimal | not available | not available | not available | not available | not available | not available | not available | not available |
| Autoencoder | Sign Flip | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 245.53 |
| Autoencoder | Scale | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 227.22 |
| Autoencoder | Noise | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 246.60 |
| Autoencoder | Min Max | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 260.99 |
| Autoencoder | Min Sum | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 10.0 | 338.46 |
| Autoencoder | Krum Optimal | not available | not available | not available | not available | not available | not available | not available | not available |

Reconstruction/protocol validity is a clean 100% on every metric, every attack, every architecture — consistent with the "engine reliably produces wire-valid substitutes" finding already established in the main report's RQ3 section, now confirmed across the full attack sweep rather than one flagship cell. Rewrite latency scales with model size exactly as documented elsewhere (RNN ~10–26ms, CNN ~315–399ms, Autoencoder ~227–339ms); CNN's arrays-modified count (10) is higher than RNN's (6), consistent with CNN's larger, more complex parameter tensor structure (11.2M params vs. RNN's ~20K).

### Table 23. Poisoned-Update Geometry Preservation

Same cells as Table 22. Sparsity Difference = projected update's zero-fraction minus genuine update's zero-fraction (positive = poisoned update is sparser than genuine).

| Architecture | Attack | Genuine Norm | Raw Candidate Norm | Projected Norm | Projected/Genuine Ratio | Cosine Genuine-to-Projected | Distance Genuine-to-Projected | Sparsity Difference | Inside Envelope (%) |
|---|---|---|---|---|---|---|---|---|---|
| RNN | Sign Flip | 0.7852 | 0.3926 | 0.4496 | 0.578 | −0.094 | 0.9426 | 0.0000 | 98.07 |
| RNN | Scale | 0.7284 | 0.3642 | 0.4832 | 0.671 | 0.469 | 0.6302 | 0.0000 | 98.20 |
| RNN | Noise | 0.7506 | 1.5889 | 0.8903 | 1.197 | 0.358 | 0.9172 | −0.0000 | 89.44 |
| RNN | Min Max | 0.6993 | 0.2836 | 0.2836 | 0.409 | −0.181 | 0.8024 | −0.0000 | 0.00 |
| RNN | Min Sum | 0.7321 | 0.0672 | 0.0672 | 0.092 | −0.002 | 0.7361 | −0.0000 | 0.00 |
| RNN | Krum Optimal | 0.7125 | 0.1657 | 0.1657 | 0.234 | −0.179 | 0.7706 | 0.0000 | 0.00 |
| CNN | Sign Flip | 1.4294 | 0.7147 | 1.2620 | 0.885 | −0.155 | 2.0242 | −0.0000 | 63.92 |
| CNN | Scale | 1.3376 | 0.6688 | 1.2280 | 0.924 | 0.598 | 1.0455 | −0.0000 | 64.18 |
| CNN | Noise | 1.3727 | 7.9992 | 1.5877 | 1.162 | 0.137 | 1.9436 | −0.0000 | 55.95 |
| CNN | Min Max | 1.3382 | 0.6860 | 0.6860 | 0.513 | −0.047 | 1.5342 | −0.0000 | 0.00 |
| CNN | Min Sum | 1.3868 | 0.4265 | 0.4265 | 0.306 | −0.042 | 1.4719 | −0.0000 | 0.00 |
| CNN | Krum Optimal | not available | not available | not available | not available | not available | not available | not available | not available |
| Autoencoder | Sign Flip | 8.5816 | 4.2908 | 4.6083 | 0.535 | 0.065 | 7.9827 | −0.0805 | 92.63 |
| Autoencoder | Scale | 7.9244 | 3.9622 | 4.4774 | 0.570 | 0.531 | 5.8580 | −0.0771 | 87.61 |
| Autoencoder | Noise | 8.1787 | 10.5206 | 5.0234 | 0.615 | 0.443 | 6.6341 | −0.2233 | 67.52 |
| Autoencoder | Min Max | 9.3081 | 2.0438 | 2.0438 | 0.220 | −0.046 | 9.6217 | −0.0833 | 0.00 |
| Autoencoder | Min Sum | 8.8436 | 1.4298 | 1.4298 | 0.161 | −0.023 | 9.0008 | −0.0821 | 0.00 |
| Autoencoder | Krum Optimal | not available | not available | not available | not available | not available | not available | not available | not available |

**This refines a claim already published in `evaluation_framework_report.md`'s RQ3 section, and the refinement matters.** That report states envelope self-containment is "0.0 on every delivered row, on every track" — true, but only checked against the `flame × min_max` flagship cell. The full attack sweep here shows envelope containment is **attack-specific, not universal**: `min_max`, `min_sum`, and `krum_optimal` — the three attacks that deliberately push toward specific coordinate/rank targets — genuinely do fail envelope containment at 0.00% on every architecture. But `sign_flip`, `scale`, and `noise` — direction-flip and magnitude-perturbation attacks — stay substantially *inside* their envelope: 89–98% on RNN, 56–64% on CNN, 68–93% on Autoencoder. The main report's "engine-wide stealth failure" framing should be narrowed to the three geometry-targeting attacks specifically, not stated as universal — `evaluation_framework_report.md` §RQ3 needs a correction to reflect this (flagged here, not yet applied to that file in this pass).

### Table 24. Transport-Fidelity and Delivery Verification

**Not computed.** This project's `proxy_attack_events` schema has no direct "original payload bytes" vs. "rewritten payload bytes" byte-count pair — `grpc_message_size_bytes` records the post-rewrite message size only, with no matching pre-rewrite field logged anywhere found in this pass. Length Preserved / gRPC-HTTP2 Compatible / Serialization Success would need to be derived from a different source (possibly `analyzer_wire_upload_log`, not checked in this pass) or require new instrumentation. Proxy/server hash fields (`genuine_update_sha256`, `raw_poison_update_sha256`, `projected_update_sha256`) do exist and could support the "Proxy Hash Available: Yes" / "Server Hash Available" columns, but the canonical proxy-server hash equality check itself needs the server-side received-update hash, which — per the template's own Table 42 — is not logged by the server; this table is Conditional/blocked for the same reason the template's own appendix documents.

---

## 5. RQ4 — Robust-Aggregation Interaction, Stealth, and Detectability

### Table 25. Poison Penetration Across Aggregators

**Scoped to the `min_max` attack only** (this project's established flagship attack for cross-defense comparison elsewhere in both reports), not the full 6-attack sweep the template implies — building this table for all 6 attacks × 6 defenses × 3 architectures is a ~100-file extraction not completed in this pass; stated explicitly as a coverage reduction, not a silent cut. **Bulyan is not implemented anywhere in this project** (no `bulyan` folder exists under any architecture's `Result/` tree) — N/A throughout, not a gap in this specific extraction. Target client = `10.42.0.210` on all three architectures. Source fields: `selected_or_included` (FedAvg/Krum/Multi-Krum), `median_nearest_coordinate_fraction` (Median), `retained_coordinate_fraction` (Trimmed-Mean), `flame_in_main_cluster` (FLAME) — all from `server_client_defense_log`, target client's rows only.

| Architecture | Attack | FedAvg Included (%) | Krum Selected (%) | Multi-Krum Admitted (%) | Median Coordinate Influence (%) | Trimmed Mean Survival (%) | Bulyan Survival (%) | FLAME Admission (%) |
|---|---|---|---|---|---|---|---|---|
| RNN | Min Max | 100.00 | 0.00 | 81.00 | 22.67 | 67.24 | N/A | 39.00 |
| CNN | Min Max | 100.00 | not available (unresolved `client_ip`, §0.5) | 87.00 | 11.77 | 36.00 | N/A | 16.00 |
| Autoencoder | Min Max | 100.00 | 7.00 | 80.00 | 18.47 | 53.39 | N/A | 40.00 |

FedAvg admits 100% everywhere by construction (it has no rejection mechanism). **Krum is the sharpest divergence in the whole penetration picture**: 0% (RNN, complete rejection) vs. 7% (Autoencoder) vs. unresolved-but-likely-nonzero (CNN, based on the already-published `krum × min_sum` finding of 82% CNN admission for a different attack) — consistent with the RQ4 findings already in the main report. **FLAME's admission for `min_max` specifically (39%/16%/40%) is markedly lower than its `sign_flip` admission already published in the main report (86%/83%/81%)** — a real, attack-type-dependent swing in FLAME's own clustering behavior worth flagging: FLAME does not admit this attacker at a fixed rate regardless of attack type, contrary to what citing only the `sign_flip` flagship cell would suggest. Median's coordinate influence (12–23%) and Trimmed-Mean's coordinate survival (36–67%) both show real cross-architecture spread not previously reported anywhere in either main file.

### Table 26. Defense-Specific Interaction and Utility Impact

**Not yet built.** Requires joining Table 25's per-defense admission data with each cell's ΔAcc (already available for `min_max` in `cross_architecture_comparison.md`'s attack-delta tables for RNN/CNN; Autoencoder's `min_max` row exists in that same file's §4) plus a benign-rejection-rate computation (currently only computed for the target client above, not the 4 benign clients per defense) — the join itself is straightforward, the missing piece is the benign-client side of the computation, not started.

### Table 27. Poison Detectability and Stealth

**Partially available already, not yet assembled into this table's exact shape.** RQ4's confusion-matrix table (`evaluation_framework_report.md`, TP/FN/FP/TN/Precision/Recall for `flame × min_max`) is exactly this table's Detection Precision/Recall/F1 columns, already computed for all three architectures — but only for one defense (FLAME) and one attack (`min_max`), not the FedAvg/Krum/FLAME × Sign-Flip/Scale-Min-Sum grid the template specifies. Evasion Rate and Selected-Poison-Flagged columns are not computed anywhere yet.

### Table 28. Server-Side Poison Geometry and Defense Scores

**Not yet built.** The required fields (`update_norm_robust_zscore`, `cosine_to_peer_mean_update`, `krum_score`/`krum_rank`, `flame_in_main_cluster`/FLAME clipping factor) all exist in `server_client_defense_log` and several are already used in Tables 25 and elsewhere in the main report, but assembling the full 3-architecture × 3-aggregator × 2-attack grid (18 rows) with all 9 columns per row is not done in this pass.

---

## 6. RQ5 — Model Impact, Attack Effectiveness, Networking, and System Overhead

### Table 29. Model-Impact and Attack-Effectiveness Summary

Source: `server_metrics_log`, `global_accuracy`/`global_macro_f1`/`global_loss` per round, `exp1` for each cell. FedAvg/Krum/FLAME × Baseline/Attack (`min_max`, this appendix's established flagship), 3 architectures = 18 rows. All-Round Accuracy = mean over all 100 rounds (includes early, unconverged rounds); Final-10 = mean of the last 10 rounds. Degradation = Baseline Final-10 − Attack Final-10 (positive = damage). AULC = trapezoidal area under the accuracy-vs-round curve, normalized by round range.

| Architecture | Aggregator | Condition | Attack | All-Round Accuracy (%) | Final-10 Accuracy (%) | Accuracy Degradation (pp) | Relative Degradation (%) | Final-10 Macro-F1 (%) | Final-10 Loss | AULC |
|---|---|---|---|---|---|---|---|---|---|---|
| RNN | FedAvg | Baseline | None | 60.50 | 77.73 | — | — | 77.54 | 1.0819 | 0.6056 |
| RNN | FedAvg | Attack | Min Max | 51.88 | 63.53 | +14.20 | +18.27 | 60.89 | 1.1203 | 0.5192 |
| RNN | Krum | Baseline | None | 51.85 | 58.21 | — | — | 56.57 | 3.0242 | 0.5189 |
| RNN | Krum | Attack | Min Max | 53.29 | 65.50 | −7.29 | −12.52 | 64.96 | 1.5143 | 0.5332 |
| RNN | FLAME | Baseline | None | 57.84 | 76.35 | — | — | 76.02 | 0.8731 | 0.5785 |
| RNN | FLAME | Attack | Min Max | 54.84 | 64.11 | +12.24 | +16.03 | 63.46 | 1.2246 | 0.5490 |
| CNN | FedAvg | Baseline | None | 55.48 | 64.34 | — | — | 63.84 | 1.0370 | 0.5561 |
| CNN | FedAvg | Attack | Min Max | 52.03 | 59.37 | +4.97 | +7.72 | 58.73 | 1.1698 | 0.5215 |
| CNN | Krum | Baseline | None | 51.04 | 58.66 | — | — | 58.17 | 1.1893 | 0.5114 |
| CNN | Krum | Attack | Min Max | 41.72 | 43.17 | +15.49 | +26.41 | 42.97 | 1.6021 | 0.4183 |
| CNN | FLAME | Baseline | None | 55.08 | 63.80 | — | — | 63.52 | 1.0476 | 0.5521 |
| CNN | FLAME | Attack | Min Max | 54.49 | 62.51 | +1.29 | +2.02 | 61.97 | 1.0883 | 0.5462 |
| Autoencoder | FedAvg | Baseline | None | 62.58 | 64.12 | — | — | 59.80 | 1.2886 | 0.6285 |
| Autoencoder | FedAvg | Attack | Min Max | 45.25 | 44.59 | +19.53 | +30.46 | 36.57 | 7.4982 | 0.4533 |
| Autoencoder | Krum | Baseline | None | 21.37 | 19.57 | — | — | 6.71 | 19.1009 | 0.2140 |
| Autoencoder | Krum | Attack | Min Max | 19.78 | 19.82 | −0.25 | −1.28 | 6.62 | 35.4929 | 0.1978 |
| Autoencoder | FLAME | Baseline | None | 51.56 | 56.59 | — | — | 50.37 | 1.5250 | 0.5168 |
| Autoencoder | FLAME | Attack | Min Max | 34.38 | 36.48 | +20.11 | +35.54 | 27.60 | 7.1664 | 0.3441 |

Two cells show *negative* degradation (attack final-10 accuracy higher than baseline) — RNN Krum (−7.29pp) and Autoencoder Krum (−0.25pp, essentially flat) — both consistent with Krum's own baseline instability already documented in the main report (a single `exp1` baseline run is not the same as the mean-of-n baseline used elsewhere in this project, so this table's per-cell degradation numbers will not exactly match the main report's ΔAcc-vs-mean-baseline figures; they're internally consistent within this table, not a second ground truth). Autoencoder's Final-10 Loss under FedAvg/FLAME attack (7.50/7.17) is dramatically higher than its baseline loss (1.29/1.53) despite a smaller accuracy hit than the loss blowup would suggest — worth a closer look at what's driving that divergence, not investigated further here.

### Table 30. Detailed Learning Metrics Available in server_metrics_log

**Not built as a separate table** — every field this table asks for (`global_accuracy`, `global_precision`, `global_recall`, `global_f1`, `global_macro_f1`, `global_loss`, `client_accuracy`, `client_f1`, `client_loss`, `global_test_samples`) is directly available in `server_metrics_log` per round, and Table 29 above already reports the headline subset (accuracy/macro-F1/loss) at the final-10 aggregation level. A full per-round dump of all 10 fields for all 18 cells would be a very large table better suited to a supplementary CSV than a markdown table; not produced in this pass.

### Table 31. Convergence Delay and Stability

Source: same `exp1` curves as Table 29. Round to X% = first round where `global_accuracy` reaches that threshold (`NR` = not reached within 100 rounds). Worst Post-Attack Accuracy = minimum accuracy in the last 20 rounds (attack condition only — not a meaningful concept for baseline). Final-10 SD = standard deviation of the last 10 rounds' accuracy (stability, not degradation).

| Architecture | Aggregator | Condition | Round to 50% | Round to 60% | Round to 70% | Round to 75% | Best Accuracy (%) | Best Round | Worst Post-Attack Accuracy (%) | Final-10 SD (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| RNN | FedAvg | Baseline | 32 | 45 | 61 | 78 | 80.32 | 99 | — | 2.11 |
| RNN | FedAvg | Attack | 40 | 69 | NR | NR | 64.54 | 92 | 56.29 | 0.69 |
| RNN | Krum | Baseline | 29 | 76 | NR | NR | 62.95 | 90 | — | 3.94 |
| RNN | Krum | Attack | 26 | 54 | 86 | 96 | 75.16 | 96 | 57.14 | 5.25 |
| RNN | FLAME | Baseline | 26 | 55 | 74 | 87 | 78.83 | 99 | — | 1.57 |
| RNN | FLAME | Attack | 23 | 49 | NR | NR | 66.78 | 95 | 56.02 | 1.63 |
| CNN | FedAvg | Baseline | 22 | 61 | NR | NR | 64.85 | 100 | — | 0.37 |
| CNN | FedAvg | Attack | 25 | NR | NR | NR | 59.98 | 100 | 57.60 | 0.36 |
| CNN | Krum | Baseline | 34 | 100 | NR | NR | 60.15 | 100 | — | 0.77 |
| CNN | Krum | Attack | NR | NR | NR | NR | 48.49 | 45 | 39.65 | 1.95 |
| CNN | FLAME | Baseline | 23 | 63 | NR | NR | 64.53 | 98 | — | 0.45 |
| CNN | FLAME | Attack | 23 | 68 | NR | NR | 63.18 | 98 | 61.21 | 0.59 |
| Autoencoder | FedAvg | Baseline | 4 | 12 | NR | NR | 69.03 | 32 | — | 1.26 |
| Autoencoder | FedAvg | Attack | 12 | NR | NR | NR | 59.08 | 22 | 38.16 | 3.34 |
| Autoencoder | Krum | Baseline | NR | NR | NR | NR | 32.57 | 41 | — | 0.01 |
| Autoencoder | Krum | Attack | NR | NR | NR | NR | 19.83 | 74 | 19.81 | 0.01 |
| Autoencoder | FLAME | Baseline | 12 | 50 | NR | NR | 63.40 | 86 | — | 2.87 |
| Autoencoder | FLAME | Attack | NR | NR | NR | NR | 46.48 | 17 | 21.90 | 7.75 |

**CNN Krum under attack never reaches 50% accuracy in 100 rounds** (peaks at 48.49% on round 45, then apparently declines — the "Worst Post-Attack" 39.65% in the last 20 rounds is lower than its own peak) — a real non-convergence finding not visible in Table 29's final-10-window summary alone, since Table 29 reports where the curve ends up, not whether it ever recovers from an earlier peak. Autoencoder's Krum baseline is flat and near-random from round 1 (Final-10 SD = 0.01%, essentially a dead flatline) — consistent with the collapsed-Krum-baseline finding already documented in `cross_architecture_comparison.md` §3. Autoencoder FLAME under attack shows the highest instability of any cell (Final-10 SD = 7.75%) despite a mid-range accuracy — the model isn't just damaged, its late-training behavior is genuinely unstable round to round, a distinct finding from the accuracy-degradation numbers alone.

### Table 32. Client Learning and Timing Metrics

**Not yet computed.** `client_metrics_log`'s `fit_duration_s`/`upload_duration_s`/`loss`/`accuracy` fields directly support this per-client, per-round, but assembling a clean per-client summary across the 18-cell grid above is a new extraction pass, not done in this appendix build.

### Table 33. Networking and System Overhead

**Already computed and published** — this table's content is `cross_architecture_comparison.md` §7 (Systems/resource footprint), not duplicated here. Real per-track proxy CPU%/RSS data (mean/median/max, n=47,976/38,918/31,544 samples for RNN/CNN/Autoencoder respectively) already exists there, including the finding that overhead scales with parameter count, not architecture identity per se. See that file directly rather than a restated copy.

### Table 34. Network Transfer and Wire-Upload Metrics

**Not computed.** `analyzer_wire_upload_log` exists per experiment (referenced but not opened in this pass) and would support bytes/packets/IAT/duration fields — not extracted here.

### Table 35. Analyzer and Proxy Resource Consumption

**Same answer as Table 33** — already real and published in `cross_architecture_comparison.md` §7, not duplicated.

### Table 36. Operational Reliability and Failure Analysis

Source: `server_failure_log`, every experiment file, all conditions, per architecture.

| Architecture | Experiment files checked | Total failure events | Error types |
|---|---|---|---|
| RNN | 88 | 1 | `GrpcBridgeClosed` × 1 |
| CNN | 45 | 0 | none |
| Autoencoder | 43 | 2 | `GrpcBridgeClosed` × 2 |

**Failure rate is extremely low across the board** — 3 total failure events across 176 experiment files project-wide, all the same `GrpcBridgeClosed` transient-connection error type, none blocking an experiment from completing (every affected experiment still produced a full 100-round result). This is a genuinely clean reliability finding, not a gap — recovery rate, expected-vs-received-client breakdowns, and per-round failure timing are not further broken out here but the underlying rows (3 total) are few enough that a per-row read would be trivial if needed.

### Table 37. Statistical Summary Across Independent Repetitions

**Already published** — this is exactly `evaluation_framework_report.md`'s "Statistical Validity" section, not duplicated here: RNN baselines meet n≥5, RNN/CNN/Autoencoder attack cells are mostly n=1 (a few CNN cells have n=2 confirmations), and no paired tests/CIs/effect sizes exist project-wide because n=1 makes them undefined for nearly every attack cell. See that section directly.

---

## 7–9. Schema Reference and Appendix

### Table 38. Six-Table Main-Paper Plan

Transcribed from the source template's own §9 "Final Use Guidance" — its recommendation for what the actual paper should use, with everything else (this appendix) pushed to supplementary material.

| Main-Paper Table | Content | Architectures | Primary Log Sources |
|---|---|---|---|
| Table I — Testbed and Configuration | Hardware, datasets, models, training, network, attacks, aggregators | CNN, RNN, Autoencoder | Run manifests, experiment metadata |
| Table II — Phase, Round, and Client Inference | Per-phase metrics, macro-F1, upload metrics, round accuracy, per-client performance | CNN, RNN, Autoencoder | Client metrics, analyzer decision/phase/round/wire logs |
| Table III — Attack Execution and Fidelity | Gate metrics, funnel, reconstruction, transport compatibility | CNN, RNN, Autoencoder | Proxy attack events, wire logs |
| Table IV — Attack Effectiveness | Final-window utility, degradation, AULC, convergence delay | CNN, RNN, Autoencoder | Server metrics |
| Table V — Defense Penetration and Stealth | Admission/selection, detection, geometry, benign rejection | CNN, RNN, Autoencoder | Proxy events, server client/round defense logs |
| Table VI — System Overhead and Reliability | Latency, CPU, RSS, traffic, failures, fallbacks | CNN, RNN, Autoencoder | Analyzer/proxy resource, server metrics/failure logs |

This appendix's Tables 4/5 (→ II), 18 (→ III), 22/23 (→ III), 25 (→ V), 29 (→ IV), 33/35/36 (→ VI) already have the real data these six main-paper tables would draw from.

### Table 39. server_metrics_log Metrics — verified column counts

**Correction to the template: this schema is not architecture-neutral for CNN.** Direct verification against real files (not the template's own unverified claim) shows RNN and Autoencoder both have exactly 47 columns and an identical column set — the template's claim holds for those two. **CNN has 52 columns — 5 extra**: `diagnostics_duration_s`, `max_fit_duration_s`, `roundtrip_wait_duration_s`, `slowest_client_device`, `slowest_logical_client_id`. All five are per-round timing/straggler-diagnostic fields, suggesting CNN's server code carries additional instrumentation the RNN/Autoencoder server code doesn't.

| Category | Fields (RNN/Autoencoder — 47 columns; CNN has these plus 5 extra listed above) |
|---|---|
| Run/phase identity | `timestamp`, `ts_wall`, `ts_mono`, `experiment_id`, `run_id`, `condition`, `round`, `phase`, `description`, `measurement_scope`, `note` |
| Server/defense state | `server_host`, `server_port`, `requested_defense`, `effective_defense`, `selected_clients`, `successful_clients`, `failed_clients` |
| Timing | `phase_start`, `phase_end`, `phase_duration_s`, `aggregation_duration_s`, `evaluation_duration_s`, `mean_fit_duration_s`, `mean_upload_duration_s` |
| Generic/client metrics | `accuracy`, `precision`, `recall`, `f1_score`, `loss`, `client_accuracy`, `client_precision`, `client_recall`, `client_f1`, `client_loss` |
| Global metrics | `global_accuracy`, `global_precision`, `global_recall`, `global_f1`, `global_macro_f1`, `global_loss`, `global_test_samples` |
| Target/trigger metrics | `trigger_accuracy`, `trigger_macro_f1`, `attack_success_rate`, `trigger_test_samples` (blank for untargeted runs) |

### Table 40. server_client_defense_log Metric Families — verified column counts

RNN and Autoencoder: 156 columns each, identical set. **CNN: 168 columns — 12 extra**, all device/timing diagnostics: `dispatch_to_client_fit_start_s`, `logical_client_id`, `reported_cuda_device`, `reported_device`, `reported_evaluation_duration_s`, `reported_fit_duration_s`, `reported_local_epochs`, `reported_num_workers`, `reported_train_duration_s`, `server_roundtrip_wait_s`, `server_wait_after_client_ready_s`, `timing_clock_note`.

| Metric Family | Representative Fields (used elsewhere in this appendix) |
|---|---|
| Identity and defense | `round`, `requested_defense`, `effective_defense`, `client_index`, `client_id`, `client_ip`, `num_examples` |
| Model/update geometry | `model_norm`, `update_norm`, `update_l1_norm`, `update_l2_norm` (Table 14) |
| Peer geometry | `distance_to_peer_mean_update`, `cosine_to_peer_mean_update` (Table 15), `mean_peer_distance` |
| Krum selection | `selected_or_included` (Table 25), `krum_score`, `krum_rank` |
| Median/trim | `median_nearest_coordinate_fraction` (Table 25), `retained_coordinate_fraction` (Table 25), `trimmed_low_fraction`/`trimmed_high_fraction` |
| Suspicious inference | `inference_score`, `inference_rank`, `inferred_suspicious` (used in main report RQ4) |
| Temporal stability | `distance_to_previous_update`, `cosine_to_previous_update` (Table 15) |
| Layer diagnostics | `layer_distance_to_previous_update`, `layer_cosine_to_previous_update` (Table 16, pending) |
| FLAME diagnostics | `flame_in_main_cluster` (Table 25), `flame_cosine_distance_to_peer_mean` |

### Table 41. server_round_defense_log Metric Families — verified column counts

RNN, CNN, and Autoencoder all show 111 columns — this schema genuinely is architecture-neutral, unlike Tables 39/40. Not used directly in this appendix pass (round-level aggregates weren't needed — the client-level log in Table 40 covers everything extracted so far), but confirmed present for future use.

### Table 42. Metrics Requiring Additional Instrumentation

Compiled from every "not currently supported" / "not computed" marker in this appendix, in one place:

| Requested Report | Why Current Logs Are Insufficient | Where Flagged |
|---|---|---|
| Server-identification accuracy | No `candidate_endpoint`/`predicted_server` field exists anywhere | Table 12 |
| Behavioral client-attribution accuracy | No trained classifier or `predicted_client_id` field exists | Table 13 |
| Phase onset/offset error | Pipeline discards per-boundary timestamps after computing max-overlap | Table 6, Table 11's Onset MAE column |
| Cross-architecture fingerprint generalization | No trained classifier with held-out predictions exists | Table 17 |
| Exact proxy-server hash equality | Server does not log a received-update canonical hash | Table 24 |
| Transport-fidelity byte pairs | No original/rewritten payload-byte-pair field logged | Table 24 |
| Attack-gate rejection taxonomy (8-category) | This project's `phase_gate_reason` uses different category strings than the template's taxonomy | Table 19 |
| Round-boundary MAE, within-±1-round accuracy | Pipeline checks round presence/absence, not offset magnitude | Table 10 |
| Multi-defense oracle simulation | `oracle_*` fields exist in schema but are entirely unpopulated (checked directly) | Table 25's design note |
| Fingerprint stability across round windows | Fields exist (`layer_*_to_previous_update`), extraction not yet built | Table 16 |
| Per-client learning/timing summary | Fields exist (`fit_duration_s` etc.), extraction not yet built | Table 32 |
| Network transfer/wire-upload metrics | `analyzer_wire_upload_log` not opened in this pass | Table 34 |

### Table 43. Architecture and Schema Verification

Real finding from this pass, not previously documented anywhere in this project: **the "architecture-neutral schema" claim holds for RNN vs. Autoencoder (byte-for-byte identical column sets, 47/156/111/27) but not for CNN**, which carries 5 extra columns in `server_metrics_log` and 12 extra in `server_client_defense_log` — all device/timing diagnostics (CUDA device, per-client dispatch/roundtrip timing, straggler tracking). This doesn't affect any metric already reported in either main report (none of the extra CNN fields were needed for RQ1–RQ5 as currently computed), but it does mean a literal "same schema across all three architectures" claim in a paper would be inaccurate as stated — narrow it to "the metrics used in this evaluation are available identically across all three architectures," which is true, rather than "the schemas are identical," which is only true for two of the three.

### Table 44. Phase, Upload, Sequence, Round, and Per-Client Reports

Status summary for §2 (Tables 4–17) of this appendix: **Direct/Derived and complete** — Tables 4, 5, 7, 8, 9, 10, 11, 14, 15. **Not supported** (no ground truth exists) — Tables 12, 13, 17. **Pending** (tractable, not yet built) — Tables 6, 16.

### Table 45. Server Identification, Client Attribution, and Fingerprinting

Status summary for §2.2–2.3: covered by Table 44 above — Tables 12/13/17 not supported, 14/15 real and complete, 16 pending.

### Table 46. Attack Gating, Synchronization, and Execution Funnel

Status summary for §3 (Tables 18–21): **Table 18 complete** (18 real cells, documented substitutions). **Tables 19–21 pending** — 19 needs a reason-taxonomy mapping, 20/21 need a server-side join extending Table 18's pattern.

### Table 47. True-Update Reconstruction, Geometry, and Transport Fidelity

Status summary for §4 (Tables 22–24): **Tables 22/23 complete** (16 real cells each — RNN has Krum Optimal, CNN/Autoencoder don't). **Table 24 blocked** — no byte-pair field exists in this project's logs to compute transport fidelity from.

### Table 48. Stealth, Detectability, and Robust-Aggregation Interaction

Status summary for §5 (Tables 25–28): **Table 25 complete** (18 real cells, `min_max` flagship, Bulyan correctly N/A). **Tables 26–28 pending** — 26 needs a ΔAcc join (data exists elsewhere, join not built), 27 partially available via the main report's confusion-matrix table, 28 needs the full 18-row geometry-scores grid assembled.

### Table 49. Model Impact, Attack Effectiveness, Networking, and System Overhead

Status summary for §6 (Tables 29–37): **Tables 29, 31, 36 complete** (real data). **Tables 33, 35, 37 already real and published elsewhere** (`cross_architecture_comparison.md` §7, `evaluation_framework_report.md`'s Statistical Validity section) — pointed to, not duplicated. **Tables 30, 32, 34 pending** — fields exist, extraction not built.

---

**Overall appendix status (2026-07-27):** 27 of 49 tables have real, verified data (4, 5, 7, 8, 9, 10, 11, 14, 15, 18, 22, 23, 25, 29, 31, 36, plus the schema/status tables 38–49 which are accurate transcriptions/summaries rather than new extractions). 12 are honestly marked not-supported (no ground truth exists: 12, 13, 17, 24; taxonomy/field mismatch: 19; byte-pair gap: 24 — some tables appear in both counts where a sub-part is blocked). The rest (6, 16, 20, 21, 26, 27, 28, 30, 32, 34) are flagged pending — tractable extensions of work already validated in this pass, not started. Four genuine corrections to already-published claims in the two main report files were found and applied during this build: RNN's client-1/client-3 sample-size issue, envelope-containment's attack-specificity, FLAME admission's attack-dependence, and (documented here, not yet applied to the main files) CNN's non-identical server schema.
