# Evaluation of the Present Research Against the RQ1–RQ5 Framework

*Compiled from real experimental logs in this repository (`Result/RNN`, `Result/CNN`, `Result/Autoencoder`, plus prior-session extraction scripts). Every number below traces to a specific file; every gap is stated as a gap, not filled in. No condition, run, or metric described here was fabricated or estimated without a labeled source. Methodology (field mappings, formulas, master-join schema) follows a more precise specification provided 2026-07-26; every claim from that specification was independently re-verified against this repository's actual files before being incorporated — several numbers matched exactly, one factual claim (about which server run matches the flagship proxy run) did not and is corrected below.*

---

## 0. Scope-limiting finding — read this before the rest

The framework's "Experimental controls" section requires **six** conditions per attack/defense pair: clean baseline, passive monitoring (no proxy), proxy forwarding without manipulation, blind poisoning, phase-aware poisoning, and an oracle attack.

**Corrected 2026-07-26, per direct clarification on this system's architecture: the existing `baseline` condition satisfies both "passive monitoring" and "proxy forwarding without manipulation," not just "clean baseline."** This codebase's proxy/analyzer is architecturally always in the traffic path — even in `baseline` (no-attack) runs, `analyzer_decision_log`/`analyzer_phase_log`/`analyzer_round_log` are populated (every row `action=skip, reason=attack_disabled`, verified directly across RNN and CNN), meaning the proxy is actively forwarding and the analyzer is actively observing every round, just never triggering. There is no separate "analyzer watching without being in-path" mode and no separate "proxy relaying with the analysis logic switched off" mode in this codebase — those two framework-distinct conditions collapse onto the same measured `baseline` data here, by design of the architecture, not by a missing experiment. **What likely does *not* exist as a separate condition is the framework's literal "clean baseline" in the strictest sense (zero interception layer at all, direct client-server) — this codebase's `baseline` already includes the full proxy/analyzer pipeline, just with poisoning disabled**, so a truly interception-free control was probably never run either; not confirmed by a direct search for such a mode, but consistent with everything else observed about this architecture.

**Revised count: 3 of the framework's 6 labels are satisfied by 2 distinct measured datasets** — `baseline` covers "passive monitoring" and "proxy forwarding without manipulation" simultaneously; `attack`/`poisoned` covers "phase-aware poisoning." Confirmed still absent:

- Directory audit of `Result/RNN`, `Result/CNN`, `Result/Autoencoder` — every condition folder is either `baseline`, `attack`, or `poisoned` (a legacy synonym for `attack`). No `passive`, `forward_only`, `blind`, or `oracle` folders exist anywhere.
- Source audit of `poison_live.py` / `analyzer.py` — no `--mode passive`, no un-gated forwarding path, no blind-trigger code path (random/periodic/continuous trigger timers), and no attack schedule knob (sparse/burst/alternating-target). The proxy's dispatch logic is *architecturally* phase-gated — there is no alternate "blind" code path to switch to for comparison, not just a missing config flag.
- `defense_oracle.py` exists but is **not** the framework's oracle-attack condition. It's a local surrogate the attacker's own crafting logic can consult to predict whether a candidate update would survive Krum/Median/etc. before sending it — a defense oracle, not a ground-truth-triggered attack oracle. Its output fields (`oracle_krum_flagged`, `oracle_flame_selected`, etc.) exist in `proxy_attack_events` schema but are **empty in every row checked** (field `surrogate_disabled_by_operator` confirms this surrogate was switched off for the runs on disk).

**Consequence for this evaluation:** every RQ2/RQ4 comparison against "random triggering," "periodic triggering," "continuous manipulation," or "oracle triggering" is **not computable from existing data** — those conditions were never run. This is the single largest gap between the framework and the present research.

---

## 0.5 Master join — canonical identity schema, verified against real files

The framework specifies that `experiment_id`, `run_id`, `condition`, `round`, `client_ip`, `attack_id`, and `ts_wall_ns` must be propagated consistently across proxy, analyzer, server, and client logs for any cross-file join to be trustworthy, with canonical identity `client.src_ip = analyzer.client_id = proxy.client_ip = server.client_ip`.

**Checked directly against this repository:**

- **`experiment_id`/`run_id` propagation is mostly reliable but not perfectly so.** This project has documented (and this session found fresh instances of) digit-level corruption in `experiment_id` between proxy and server logs — 5 confirmed instances project-wide as of this session, always a single-digit drop/substitution, always resolvable by cross-checking defense+attack+timestamp proximity. Never silently trust an ID match without spot-checking; this report's own RQ3/RQ4 pulls below re-verify `experiment_id` agreement between proxy and server before using any cell.
- **`client_ip` is NOT reliably the join key across all tracks — but CNN's is now largely fixed in place (2026-07-26).** RNN's `server_client_defense_log` populates `client_ip` consistently. CNN's did not for any run before 2026-07-23 13:51 (a mid-campaign fix boundary, confirmed this session), and even after that fix, 3 of 5 clients could share an identical placeholder value (`127.0.0.1`) rather than distinct real IPs. Two identification methods were used: **behavioral matching** (matching per-round anomaly signal against known delivered-round timing from the proxy log — used first, see RQ4) and, later, **norm-correlation identification**: correlating the server's per-round `update_l2_norm` (per opaque `client_id` hash) against the proxy's per-round `genuine_update_l2_norm` (per real IP) across all 100 rounds of an experiment. The corrected `client_ip` was then written directly into `server_client_defense_log` and matching `*_inference_clients.csv` files for **25 of 32 CNN attack experiments** (originals preserved as `.bak`); **7 remain unresolved** (mostly `scale`-attacked cells, where the identification margin was too thin, <0.02, to trust — left in their original broken state rather than guessed) and **12 baseline-condition files remain unfixed** (no `proxy_attack_events` exists for baseline runs, so there's no ground-truth signal to correlate against; the only alternative tested, `payload_bytes`, doesn't discriminate between clients). One important methodological note from doing this: a first attempt let a fully free 5-way correlation assignment override an already-correct pre-existing IP in pursuit of maximizing total correlation — caught by re-verifying against a known-correct value, fixed by anchoring pre-existing valid IPs and identifying the attack target specifically (via the proxy's own `modified` ground-truth flag) rather than trusting a global optimization blindly. Where the behavioral method and the norm-correlation method were both computed for the same cell (`flame × sign_flip`), they agreed exactly (83% FLAME admission) — good cross-validation of both approaches.
- **The gateway address `10.42.0.1` genuinely appears as a pseudo-client.** Verified directly: `analyzer_decision_log` for the RNN `flame × min_max` run contains exactly six distinct `client_id` values — the five real FL clients (`.18`, `.47`, `.59`, `.145`, `.210`) plus `10.42.0.1` (7,770 rows, always `IDLE`/`skip`). This is the hotspot's own gateway address (confirmed against `launch_5G.sh`, which configures `10.42.0.1` as the hotspot's self-address on the `10.42.0.0/24` subnet) — the analyzer tracks every flow on the subnet, not just the five FL participants, so the gateway shows up as a sixth "client" that must be excluded from any classification metric. **This exclusion is now applied wherever client-count-based metrics are computed in this report.**
- **Correction (2026-07-26): client-side ground truth does exist — this report previously stated it didn't, which was wrong.** `Result/<track>/client1`–`client5` are genuinely empty on every track, but a **separate, top-level `client_results/` directory** (`client_results/client-1/`, `client_results/client-4/`) contains real `client_metrics_log_*.csv` files — 98 RNN + 27 CNN + 42 Autoencoder files for client-1, 78 RNN + 27 CNN + 41 Autoencoder for client-4. Schema confirmed by direct inspection: `experiment_id`, `client_id`, `round`, `phase` (`download`/`fit`/`upload`, no separate `evaluate` row — accuracy/precision/recall/F1/loss are embedded in the `fit` row, exactly matching the framework's stated limitation), `phase_start`/`phase_end`/`phase_duration_s`, `fit_duration_s`, `upload_duration_s`, `src_ip`, `grpc_error_count`/`retry_count`/`disconnect_count`. This was missed for the entirety of this evaluation because the search was scoped to `Result/` only; it should not have been.
  - Only 2 of the project's 5 physical clients have synced data (client-2/3/5 folders contain only an empty Syncthing marker, `.stfolder` — this repo mirrors client-side logs from physical devices via Syncthing, and three haven't connected/synced).
  - **`client_id`/`src_ip` are not fixed per physical client — they vary by track and run.** Client-4 is consistently `10.42.0.210` across every Autoencoder file checked (i.e., client-4 *is* the attacked target in every Autoencoder cell analyzed this session) but shows `127.0.0.1` on CNN — a different assignment per track, not a stable physical-to-logical mapping. Client-1 is consistently `10.42.0.47`.
  - **`experiment_id` format differs by design between client and server/proxy logs** — client uses a human-readable timestamp format (`exp_20260726_023419`), server/proxy use epoch-prefixed IDs (`exp_1785047317`). These are not the same ID for the same run and will never string-match; joining requires timestamp-proximity + round/defense/attack context, the same reconciliation method already used elsewhere in this project for corrupted IDs. Spot-checked once (client-4 × `flame × min_sum` Autoencoder): client's round-1 `fit` phase ends at wall-clock 02:34:34.9; server logs its round-1 aggregate result at 02:34:46.9 — a ~12s gap, physically consistent with upload+aggregation latency, not a mismatch.
  - **This unlocks real RQ1/RQ2 ground truth for two clients across all three tracks** — not yet computed in this report (a systematic per-cell join is a substantial follow-up task, not a quick correction), but the blocking claim above no longer holds. Treat every "not computable — no client ground truth" statement below as "not yet computed, now unblocked for client-1/client-4" rather than a hard capability gap.

---

## RQ1 — Phase Classification and Client Fingerprinting

### Phase label normalization

The framework specifies client-side labels (`download`/`train`/`upload`) map to analyzer labels (`DOWNLOAD`/`TRAINING`/`UPLOAD`). This project's own phase vocabulary (confirmed via `server_run_manifest.json`'s `client_phase_sequence`/`server_phase_sequence` fields) uses `download`/`fit`/`upload` — `fit` is this project's equivalent of the framework's `train`. Noted for terminology consistency; no functional difference.

### Phase and round quality — final methodology (2026-07-26): ground-truth-validated, correctly aggregated, full 5-client sample on CNN/Autoencoder, corrected 4-client sample on RNN (see below)

This section has now been revised five times; this is the final version and supersedes all prior ones (summarized: a timestamp-anchored pass, two `round`-identity passes using `analyzer_decision_log` presence and `analyzer_phase_log` duration, a ground-truth pass with a real aggregation bug, then a correctly-aggregated pass that rested on only 2 of 5 clients — see below for why that changed). The user supplied two reference scripts (`five.py`/`combine_five_experiments.py`, `final.py`/`generate_final_tables_and_figures.py`) from a prior evaluation pass, whose table format this section reproduces: **Round Tracking Quality**, **Phase Transition (Sequence) Quality**, **Phase Inference Quality**, **Phase Classification Quality** (precision/recall/F1) with a **confusion matrix**, and **Phase Detection Latency**. The originals computed sequence quality and phase duration purely from the analyzer's own logs, self-referentially, with no client comparison — instructed correction: **client log = ground truth, `analyzer_round_log`/`analyzer_phase_log` = prediction.** Full tables and figures (PNG+EPS) at [`evaluation/quality_reports/`](quality_reports/), generating scripts and a per-experiment audit trail (`per_experiment_summary.csv`) included for reproducibility.

**Ground truth expanded from 2 of 5 clients to all 5 clients (2026-07-26), after fixing several client-identity bugs found while onboarding the new data — each verified and corrected in place, `.bak` originals preserved:**
- **CNN's `src_ip = 127.0.0.1` (loopback) logging bug**, first found on client-4, turned out to affect **client-2 and client-5 as well** — 3 of 5 clients, CNN-specific, RNN/Autoencoder unaffected on the same machines. This is consistent enough across independent physical machines to suspect the CNN client launcher itself (not a per-machine network fault); corrected to each client's real IP (verified against its own RNN/Autoencoder logs) rather than investigated further given the deadline.
- **client-3's CNN logs were corrupted in a different way**: 4 of 44 files had `src_ip` populated with 299 of 300 rows showing implausible, often out-of-range values (e.g. `10.42.0.421`, impossible on a `/24` subnet) instead of its real IP. Corrected to `10.42.0.145` (confirmed via the other 40 already-clean files and client-3's RNN/Autoencoder logs).
- **client-5 showed two different IPs across tracks** (`10.42.0.145` on part of its RNN history, `10.42.0.59` elsewhere) — checked for a real identity collision with client-3 first (none: the date ranges don't overlap, `10.42.0.145` was client-5's address only through 2026-07-18, then reassigned before client-3 ever used it) before correcting client-5's full history to its confirmed current identity, `10.42.0.59`, per direct instruction.
- **RNN's "full 5-client" claim was checked directly (2026-07-26) and found wrong — two separate issues, corrected differently.** (1) **client-1's RNN logs were genuinely misfiled**: they live under a non-standard `client_results/client-1/RNN/New_RNN/poisoning/` dump instead of the `baseline/<defense>/exp<N>` / `attack/<defense>/<attack>/exp<N>` structure every other client uses, so the path-mirroring join used to find each client's matching analyzer log silently found nothing for client-1 — 0 of 98 files joined. Recovered via timestamp+round-range verified matching against `Result/RNN/proxy/**/analyzer_round_log_*.csv` (69 of 70 candidates within a 20-minute window matched their analyzer file's own round range for client-1's IP exactly; the 70th was off by one round, still accepted) — 56 of a possible 62 RNN experiments recovered (30/30 baseline, 26/32 attack); 5 remaining attack experiments have no current-campaign match because their analyzer folders were overwritten by a later rerun (same overwrite pattern documented for Autoencoder's Trimmed-Mean `exp2`/`exp3`, §0.5), 1 further file is a genuine remaining gap. (2) **client-3 has zero RNN baseline files anywhere — a real, structural absence, not a bug**: its `client_results/client-3/RNN/baseline/*/` folders exist but are empty for all 6 defenses (confirmed by direct listing), while its `attack/*/` folders have real data (29 files across 6 defenses). RNN baseline was therefore a **3-client sample** (client-2/4/5 only) before this fix, not 5; with client-1 recovered it is now a **4-client sample** (client-2/4/5 + client-1) — client-3 remains absent from baseline and cannot be recovered because no baseline data exists for it. RNN attack-condition client counts varied per experiment before the fix (2–4 clients); with client-1 recovered, 20 of 32 attack experiments now have all 5 clients, the rest 4. All numbers below reflect this correction.

**Method** unchanged from the prior pass — see the four bullet points below — now run over all 5 clients instead of 2:
- **Round Tracking Quality** = per experiment, client's true rounds that also appear in `analyzer_round_log` ÷ total client rounds; then mean±SD across experiments.
- **Phase Transition (Sequence) Quality** = per experiment, client's true rounds where `analyzer_phase_log` shows `download`→`fit`→`upload` present *and in the correct order* ÷ total client rounds; then mean±SD across experiments.
- **Phase Inference Quality** = per experiment, mean of `analyzer_phase_log`'s `phase_duration_s` restricted to client-confirmed rounds; then mean±SD across experiments.
- **Phase Classification Quality** = real precision/recall/F1 via max-overlap matching (client-logged phase instance assigned the analyzer `phase_log` segment with the greatest time overlap, `NONE` if none overlaps at all) — one predicted label per true instance; computed per experiment, then mean±SD across experiments.
- **Phase Confusion Matrix** = summed across all experiments. **Phase Detection Latency** = `decision_lag_ms` from `analyzer_decision_log`, mean per experiment then mean±SD across experiments.

**Round Tracking Quality and Phase Transition Quality — CNN and Autoencoder remain effectively perfect, but RNN drops meaningfully once all 5 clients are included:**

| Track | Condition | N experiments | Round Tracking Quality | Sequence Quality |
|---|---|---|---|---|
| RNN | Baseline | 30 | 0.982 ± 0.039 | 0.982 ± 0.039 |
| RNN | Attack | 32 | 0.892 ± 0.066 | 0.892 ± 0.066 |
| CNN | Baseline | 12 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| CNN | Attack | 32 | 0.996 ± 0.006 | 0.996 ± 0.007 |
| Autoencoder | Baseline | 11 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| Autoencoder | Attack | 31 | 0.992 ± 0.005 | 0.992 ± 0.005 |

**This is a real finding, not an artifact of one bad file, and it survives the client-1/client-3 correction above.** RNN's attack-condition round tracking quality, ≈100% on the original 2-client sample, is 89.2% ± 6.6% once client-1 is recovered and client-3's genuine baseline absence is accounted for (previously reported as 87.2% on an under-counted, inconsistently-sized client group — the corrected figure is close but not identical, since the client mix per experiment changed). Every experiment folder shows some genuine gap between the client's logged rounds and what the analyzer's `round_log` captured for that client — CNN and Autoencoder do not show this pattern to nearly the same degree. Worth investigating further post-deadline: whether this is specific to the physical clients that had logging/filing issues (client-1's misfiled RNN logs, client-3's total baseline absence) pointing at something inconsistent about those two machines' RNN setups specifically, or a genuine RNN-track-specific analyzer limitation.

**Phase Inference Quality** (mean±SD duration in seconds, across experiments; full 5-client sample on CNN/Autoencoder, 4-client on RNN per §0.5):

| Track | Condition | N experiments | IDLE | DOWNLOAD | TRAINING (`fit`) | UPLOAD |
|---|---|---|---|---|---|---|
| RNN | Baseline | 30 | 116.64 ± 57.11 | 0.279 ± 0.043 | 0.761 ± 0.356 | 1.268 ± 0.780 |
| RNN | Attack | 32 | 118.75 ± 123.76 | 0.303 ± 0.032 | 0.592 ± 0.460 | 1.580 ± 1.062 |
| CNN | Baseline | 12 | 16.00 ± 32.18 | 4.780 ± 0.315 | 0.142 ± 0.212 | 6.210 ± 0.441 |
| CNN | Attack | 32 | 7.45 ± 7.08 | 3.112 ± 0.278 | 0.689 ± 0.215 | 5.482 ± 0.466 |
| Autoencoder | Baseline | 11 | 46.03 ± 74.02 | 3.033 ± 0.239 | 0.260 ± 0.436 | 6.370 ± 0.917 |
| Autoencoder | Attack | 31 | 22.74 ± 49.71 | 1.621 ± 0.153 | 0.328 ± 0.151 | 6.446 ± 0.465 |

The qualitative pattern from the 2-client pass holds (TRAINING remains small and high-variance on CNN and Autoencoder specifically), though the exact magnitudes shifted with the larger, more representative sample — a reminder that even the "final" 2-client numbers in the prior pass should not have been treated as fully converged.

**Phase inference reports — per-phase precision, recall, and F1.** For phase \(c\):

$$P_c = \frac{TP_c}{TP_c + FP_c}, \qquad R_c = \frac{TP_c}{TP_c + FN_c}, \qquad F1_c = \frac{2 P_c R_c}{P_c + R_c}$$

\(TP_c\), \(FP_c\), \(FN_c\) come from the max-overlap confusion matrix defined above (each client-logged phase instance assigned the analyzer `phase_log` segment with the greatest time overlap, `NONE` if none overlaps) — one predicted label per true instance, summed per experiment then combined per (track, condition, phase) below.

**Phase Classification Quality — real precision/recall/F1 (full 5-client sample on CNN/Autoencoder, 4-client on RNN per §0.5). `UPLOAD` still collapses to (near-)zero everywhere:**

| Track | Condition | Phase | N experiments | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| RNN | Baseline | DOWNLOAD | 30 | 0.501 ± 0.056 | 0.658 ± 0.170 | 0.559 ± 0.087 |
| RNN | Baseline | TRAINING | 30 | 0.300 ± 0.043 | 0.273 ± 0.034 | 0.283 ± 0.025 |
| RNN | Baseline | UPLOAD | 30 | 0.422 ± 0.495 | 0.015 ± 0.026 | 0.027 ± 0.048 |
| RNN | Attack | DOWNLOAD | 32 | 0.459 ± 0.145 | 0.389 ± 0.214 | 0.399 ± 0.189 |
| RNN | Attack | TRAINING | 32 | 0.256 ± 0.125 | 0.191 ± 0.102 | 0.214 ± 0.112 |
| RNN | Attack | UPLOAD | 32 | 0.031 ± 0.177 | 0.001 ± 0.003 | 0.001 ± 0.006 |
| CNN | Baseline | DOWNLOAD | 12 | 0.307 ± 0.012 | 0.744 ± 0.095 | 0.434 ± 0.026 |
| CNN | Baseline | TRAINING | 12 | 0.197 ± 0.089 | 0.019 ± 0.033 | 0.031 ± 0.048 |
| CNN | Baseline | UPLOAD | 12 | 0.250 ± 0.452 | 0.018 ± 0.036 | 0.034 ± 0.066 |
| CNN | Attack | DOWNLOAD | 32 | 0.431 ± 0.044 | 0.831 ± 0.140 | 0.565 ± 0.061 |
| CNN | Attack | TRAINING | 32 | 0.245 ± 0.053 | 0.160 ± 0.076 | 0.189 ± 0.067 |
| CNN | Attack | UPLOAD | 32 | 0.219 ± 0.420 | 0.024 ± 0.057 | 0.042 ± 0.097 |
| Autoencoder | Baseline | DOWNLOAD | 11 | 0.295 ± 0.013 | 0.756 ± 0.127 | 0.420 ± 0.021 |
| Autoencoder | Baseline | TRAINING | 11 | 0.306 ± 0.102 | 0.035 ± 0.055 | 0.053 ± 0.076 |
| Autoencoder | Baseline | UPLOAD | 11 | 0.091 ± 0.302 | 0.001 ± 0.003 | 0.002 ± 0.006 |
| Autoencoder | Attack | DOWNLOAD | 31 | 0.348 ± 0.064 | 0.650 ± 0.107 | 0.443 ± 0.031 |
| Autoencoder | Attack | TRAINING | 31 | 0.310 ± 0.092 | 0.081 ± 0.041 | 0.126 ± 0.059 |
| Autoencoder | Attack | UPLOAD | 31 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |

**The `UPLOAD` finding is now more nuanced than "exactly zero everywhere."** Autoencoder-Attack still lands at a clean 0.000 ± 0.000 (every experiment independently zero), consistent with the ground-truth definition mismatch already flagged in RQ2 (client logs upload *serialization*, analyzer detects upload *transmission* — different real-world events, rarely overlapping in time). But with the fuller client sample, **CNN and RNN now show small but genuinely nonzero UPLOAD scores** (CNN Attack F1 = 0.042 ± 0.097, RNN Baseline F1 = 0.027 ± 0.048) — the definition-mismatch problem still dominates, but it isn't a perfect, universal zero anymore. Also worth noting directly: DOWNLOAD and TRAINING scores generally *dropped* relative to the 2-client pass (e.g. RNN Attack DOWNLOAD F1 was 0.419 ± 0.427, now 0.399 ± 0.189) — tighter SDs, lower means, both more representative of the true population than the earlier 2-client estimate.

**Phase Detection Latency** (`decision_lag_ms`, mean±SD across experiments; full 5-client sample on CNN/Autoencoder, 4-client on RNN per §0.5):

| Track | Condition | N experiments | Decision Lag (ms) |
|---|---|---|---|
| RNN | Baseline | 0 | N/A |
| RNN | Attack | 31 | 28.294 ± 14.374 |
| CNN | Baseline | 0 | N/A |
| CNN | Attack | 32 | 298.367 ± 68.825 |
| Autoencoder | Baseline | 1 | 587.363 ± 0.000 |
| Autoencoder | Attack | 29 | 401.329 ± 31.407 |

**Every "Baseline" `N/A` was double-checked directly against the raw `analyzer_decision_log` for this update (RNN and CNN both re-verified, not assumed to be identical), and it's structurally correct, not a gap.** In every single baseline experiment, on every track, `decision_lag_ms` is a constant `-1.0` sentinel across 100% of rows (verified: 20,015 rows for one RNN baseline file, 222,520 rows for one CNN baseline file, both showing `action=skip, reason=attack_disabled` on every row, zero exceptions). `decision_lag_ms` only takes a real value when the analyzer evaluates an actual trigger decision, which by definition only happens when the attack logic is active — baseline runs never activate it. There is nothing to average in a baseline condition; `N/A` is the correct report, not a missing measurement.

RNN's decision lag remains far lower than CNN's or Autoencoder's, consistent with its much smaller model producing much less packet-processing work per decision — though the absolute numbers moved with the larger sample (RNN 28.3ms vs. the prior pass's 6.3ms; the earlier n=30 baseline-N=0 pattern holds, since baseline never triggers attack decisions). **The Autoencoder-Baseline n=1 row is a known artifact, not a real baseline decision-lag measurement**: it comes from the `trimmed_mean/exp2` folder, which — per an explicit, deliberate user action this session — now holds the proxy/server data originally generated as a new baseline run, and that folder's `analyzer_decision_log` shows attack-like trigger activity inconsistent with a pure baseline run. Treat this single value as noise, not a finding.

**Phase temporal IoU and boundary error (\(E_{\mathrm{start}}\), \(E_{\mathrm{end}}\)):** not computed as a separate metric, though the max-overlap assignment above is a close relative (uses interval overlap directly, just for label assignment rather than as its own reported statistic).

### Client fingerprinting (identity, not phase) — confirmed structurally absent

**Checked directly in `analyzer.py`, `poison_live.py`, and `peer_fingerprint.py`: no field or function named `predicted_client_id`, `fingerprint_confidence`, `fingerprint_model`, or `unknown_client_score` exists anywhere in the codebase.** The analyzer's `client_id` field (used throughout this report and this project) is the flow-associated IP address itself, not a classifier's output — confirmed by direct inspection (the `10.42.0.1` gateway-address rows above use `client_id: 10.42.0.1`, i.e., the literal IP, with no separate "predicted identity" field alongside it). **This means client fingerprinting cannot be evaluated as an open-set classification problem with the current instrumentation, full stop — not a missing extraction, a missing capability.** A learned classifier producing the four fields above would need to be built and logged before `Acc_fingerprint`, macro F1, a client confusion matrix, unknown-client AUROC, or false-acceptance rate become computable.

### Evaluation-phase limitation

This project's phase vocabulary has exactly three values confirmed in every extraction checked this session: `download`, `fit`(=train), `upload` (plus `idle`/`MISSING` as a boundary artifact, not a fourth operational phase). **No `evaluate` phase exists anywhere in this project's logged data.** Consistent with the framework's stated limitation: evaluation work is embedded inside the `fit`/train measurement (via an `evaluation_duration_s`-style sub-field in the now-absent client logs) rather than logged as its own row. Claiming a separate EVALUATE-phase classification result would require new client-side instrumentation, not a different extraction from existing files.

### Evaluation-split methodology

`rq_metrics_result.json`'s per-cell breakdowns are keyed by whole `(defense, attack)` experimental runs, not individual traffic windows — satisfying the framework's requirement to avoid adjacent-window leakage. Met, though as a byproduct of file organization rather than a deliberately designed held-out split (there is no train/test split at all here — this is descriptive evaluation against ground truth, not a generalization test).

### Generalization and ablation

**Not run.** No experiments vary network load, round number, client device, or IID/non-IID distribution. No feature-ablation comparison (volume/timing/direction/transport/full) exists. New experiments would be needed, not a different extraction.

---

## RQ2 — Selective Synchronization with Upload Windows

### Ground-truth caveat on client upload timing (from the framework, structurally confirmed relevant here)

The framework notes that a client's own logged `upload_duration_s` typically measures **parameter serialization only**, not full network transmission — exact synchronization needs independent transport fields (`wire_upload_start_ns`, `wire_upload_end_ns`, `actual_upload_bytes`, `actual_upload_packets`). **Now checkable against a real file (`client_results/`, §0.5), and confirmed true rather than assumed:** the client's own `upload` row carries a `note` field stating plainly *"This row records client side parameter serialisation. The actual Flower transmission happens after fit returns, so network counters may under represent the full outbound transfer."* — the client's `upload_duration_s` (e.g. 0.101s in the row checked) is exactly the serialization caveat the framework describes, self-documented by the logging code itself. **The client schema does not include `wire_upload_start_ns`/`actual_upload_bytes`/`actual_upload_packets`** — so this is a partial unlock: phase-level timing (`phase_start`/`phase_end`/`phase_duration_s`) is now available client-side, but the specific wire-transport fields the framework wants for exact synchronization are still absent from this schema. The only upload-timing ground truth at the wire level remains analyzer-side (`analyzer_wire_upload_log`), which should not be the sole ground truth used to evaluate that same analyzer — this specific limitation stands even with the client-log correction above.

### Transition-detection latency — all three tracks (2026-07-26 update)

**The prior version of this table covered RNN only; recomputed here for all three tracks** using the full 5-client ground truth (`client_results/`) matched against `analyzer_phase_log` by `(client, round, phase)` — `analyzer-reported phase start − client-log true phase start`, in seconds. A small number of matches (2–11% depending on track) showed implausible multi-hour latencies, traced to round-1-inherits-a-stale-idle-boundary edge cases rather than real detection lag; those are excluded (`|latency| > 60s`) and the exclusion rate is reported per track rather than silently dropped.

| Track | Phase | n (after outlier exclusion) | Excluded as outliers | Mean | Median | p95 | Min | Max |
|---|---|---|---|---|---|---|---|---|
| RNN | download | 16,833 | 11.11% | +2.53s | −0.01s | +15.48s | −1.09s | +59.94s |
| RNN | fit | 16,833 | 11.12% | +2.81s | +0.26s | +15.75s | −0.60s | +59.78s |
| RNN | upload | 16,831 | 11.12% | +2.74s | +0.16s | +15.63s | −0.76s | +59.63s |
| CNN | download | 19,667 | 2.37% | −1.45s | −2.03s | +6.99s | −58.15s | +57.93s |
| CNN | fit | 19,689 | 2.26% | +2.09s | +0.97s | +9.82s | −59.99s | +50.52s |
| CNN | upload | 19,663 | 2.39% | +0.95s | +0.05s | +9.03s | −56.03s | +49.62s |
| Autoencoder | download | 19,789 | 2.92% | +0.59s | −1.01s | +15.09s | −41.52s | +42.66s |
| Autoencoder | fit | 19,789 | 2.92% | +2.56s | +0.28s | +16.32s | −36.29s | +44.40s |
| Autoencoder | upload | 19,788 | 2.92% | +2.37s | +0.15s | +16.32s | −23.71s | +44.30s |

Positive = analyzer detects late. **The qualitative pattern is consistent across all three tracks**: `download` is detected right around the true boundary (median within ±2s, sometimes slightly early); `fit` and `upload` are both detected modestly late (median +0.15–0.28s), consistent with the silence-based training-detection mechanism documented in RQ1. RNN shows a notably higher outlier-exclusion rate (11%) than CNN/Autoencoder (2–3%) — not yet explained, flagged rather than investigated further given the deadline.

### Selective modification rate and spillover rate — computed fresh for this report

\(R_{\mathrm{selective}} = \frac{\#(\text{targeted}=1 \land \text{modified}=1)}{\#(\text{eligible targeted uploads after warmup})}\), \(R_{\mathrm{spill}} = \frac{\#(\text{targeted}=0 \land \text{modified}=1)}{\#(\text{targeted}=0)}\)

RNN `flame × min_max` (`exp_1784659861`, 100 targeted rows, 400 non-targeted rows, 20-message warmup):

| Metric | Result |
|---|---|
| \(R_{\mathrm{selective}}\) | 80/80 = 100% |
| \(R_{\mathrm{spill}}\) | 0/400 = 0% |

**This is a real, clean, computed result:** once past warmup, every single eligible targeted round was modified, and zero non-targeted rounds were ever touched. Internal selectivity is perfect for this cell — the proxy never poisons the wrong client once its gate is open, and never misses an eligible round either. This confirms the framework's own observation about this run ("20 retained for warmup, 80 modified, all 400 non-target observations unmodified") — independently re-derived here from the raw file, not copied from the earlier claim.

### Trigger precision/recall, strict synchronization \(S_{\mathrm{exact}}\), latency \(L_i\)

\(S_{\mathrm{exact}} = \frac{1}{N}\sum_i \mathbb{I}(t_i^{\mathrm{trigger}} \in [t_i^{\mathrm{start}}, t_i^{\mathrm{end}}] \land \hat{c}_i = c_i \land \hat{r}_i = r_i)\)

**Not computed.** \(S_{\mathrm{exact}}\) and \(L_i\) (trigger latency relative to true upload start) both require the client-side `wire_upload_start_ns`/actual-round ground truth that doesn't exist in this repository (§0.5). What can be substituted: `analyzer_wire_upload_log`'s self-reported upload window, cross-checked against `proxy_attack_events`' own `modified`/`fl_round`/timestamp fields — but per the caveat above, this substitution evaluates the analyzer partly against its own output, not independent ground truth, so it is not reported here as if it were \(S_{\mathrm{exact}}\).

Trigger precision/recall (`Precision_trigger`, `Recall_trigger` — triggers inside true uploads, true uploads containing a trigger): **not computed.** Client-side phase timing now exists (§0.5) and could support a looser version of this (trigger falling within the client's own logged `[phase_start, phase_end]` for `upload`), but the framework's specific wire-level ground truth (`wire_upload_start_ns` etc.) is still absent from the client schema — see the caveat above.

Upload coverage (targeted rounds that were actually delivered, using proxy-side data only, not requiring client ground truth): **79/100 = 79%** for the RNN `fedavg × min_max` flagship cell (`exp_1784851252`) previously reported; **80/100 = 80%** for `flame × min_max` (`exp_1784659861`, this section's flagship cell) — consistent, tight range across cells.

### Comparison against random/periodic/continuous/oracle triggering

**Not computable** — see Section 0.

### Network-condition robustness

**Not controlled or varied as an experiment.** Whatever robustness the phase-aware method shows (e.g., the `fit`-phase latency tail above) is incidental to real deployment variance, not a designed robustness study.

---

## RQ3 — Adversarial Construction in True Update Space

**Scope note (2026-07-26): the tables below now cover all three architectures explicitly — RNN, CNN, and Autoencoder — using the same flagship cell (`flame × min_max`) on each track for direct comparability.** Prior versions of this section reported RNN only (`proxy_attack_events_20260721_145216.csv`, `exp_1784659861`) without labeling every subsection by track, which read as ambiguous. That RNN cell is the same one examined in the compatibility review discussed 2026-07-26; the flagged mismatch there was traced to a file-selection error in that other review (it cited two `flame × noise` server runs as the only options), not a real gap in this repository — the actual matching server file (`server_metrics_log_20260721_145101.csv`, same `experiment_id`/`run_id`, logged one second apart) exists and is used throughout this project. CNN and Autoencoder use their own `flame × min_max` cells (`Result/CNN/proxy/attack/flame/min_max/exp1/`, `Result/Autoencoder/proxy/attack/flame/min_max/exp1/`), 500 rows / 80 modified each, same structure.

### Reconstruction and protocol validity — RNN, CNN, Autoencoder

| Track | `reconstruction_valid` | `finite_values_valid` | `wire_compatible` | Targeted → delivered |
|---|---|---|---|---|
| RNN | 80/80 = 100% | 80/80 = 100% | 80/80 = 100% | 80/100 = 80% |
| CNN | 80/80 = 100% | 80/80 = 100% | 80/80 = 100% | 80/100 = 80% |
| Autoencoder | 80/80 = 100% | 80/80 = 100% | 80/80 = 100% | 80/100 = 80% |

**Every delivered round on every architecture produced a structurally valid, finite, wire-compatible substitute — this is a genuine cross-architecture finding, not just an RNN result.** A second independent signal (`rq3_results_rnn.json`, hash-based verification against the client's own logged update rather than structural field checks) corroborates this from a different angle across 15 RNN cells checked, zero mismatches; not re-run for CNN/Autoencoder for this report.

### Geometry preservation — R_norm and S_cos, now with the envelope-containment check, RNN vs. CNN vs. Autoencoder

| Track | \(S_{\mathrm{cos}}\) (cosine, projected→genuine) | \(R_{\mathrm{norm}}\) (projected÷genuine norm) | `envelope_coordinate_containment_fraction` | `envelope_norm_containment_fraction` |
|---|---|---|---|---|
| RNN | −0.181 | 0.409 | 0.0 | 0.0 |
| CNN | −0.047 | 0.513 | 0.0 | 0.0 |
| Autoencoder | −0.046 | 0.220 | 0.0 | 0.0 |

**The envelope-containment finding is now confirmed across all three architectures, not just RNN — this is a substantially stronger result than previously reported.** `envelope_coordinate_containment_fraction` and `envelope_norm_containment_fraction` are exactly 0.0 on every one of the 80 delivered rows, on every track, with zero exceptions anywhere. These are the *live envelope engine's own internal self-check fields* — the system's own record of whether the crafted substitute stayed inside the benign coordinate/norm band it was supposed to be constructed within. A flat 0.0 across every row, every track, means that by the engine's own accounting, **the substitute did not verify as contained within its intended stealth envelope for this attack type, on any architecture.** This directly qualifies the "magnitude-conservative, stealthy on norm" framing this project has used for `min_max` — a norm ratio well under 1.0 (true on all three tracks: 0.41/0.51/0.22) is not automatically the same claim as "verified inside the benign envelope," and every track's own diagnostics say the second, stronger claim does not hold. **This should be investigated directly at the code level (why does the engine's own containment check register zero universally, and is that expected behavior for `min_max` specifically, or a bug/miscalibration) before RQ3 is described as "successful" for this attack type in any paper draft — the fact that it's universal across three independently-trained architectures makes a systematic engine issue more likely than an architecture-specific quirk.** Also worth noting: cosine and norm-ratio values differ meaningfully by architecture (RNN's cosine −0.181 is 4× more negative than CNN/Autoencoder's ≈−0.047; CNN's norm ratio 0.513 is over 2× Autoencoder's 0.220) — the envelope-containment failure is universal across architectures for `min_max`, but the underlying geometry it's failing to contain is architecture-dependent, consistent with each model's different parameter-space structure.

**Correction (2026-07-26, `netphaser_appendix_tables.md` Table 23): the 0.0 envelope-containment result is attack-specific, not universal across attack types.** A full sweep across all 5 attacks (not just `min_max`) shows `min_max`, `min_sum`, and `krum_optimal` — the three attacks that target specific coordinates or ranks — genuinely fail containment at 0.00% on every architecture, confirming the finding above. But `sign_flip`, `scale`, and `noise` — direction-flip and magnitude-perturbation attacks — stay substantially *inside* their envelope: 89–98% on RNN, 56–64% on CNN, 68–93% on Autoencoder. Any paper claim about envelope-containment failure should be scoped to the three geometry-targeting attacks, not stated as a blanket "this engine's stealth envelope never holds" claim.

### Reconstruction error \(E_{\mathrm{rec}}\)

**Still not computed, for a narrower reason than previously stated.** The client-side logs found (§0.5) carry a `weight_hash` field (present on `upload` rows) — useful corroboration for the existing binary hash-verification check (`rq3_results_rnn.json`) — but **not the raw parameter/update arrays themselves**, which a CSV log wouldn't carry regardless. The continuous \(E_{\mathrm{rec}}\) formula needs the actual \(\Delta w_i^t\) values, which live in `server_raw_updates_*/round_NNNN_updates.npz` archives on the server side, not in any client log. A real \(E_{\mathrm{rec}}\) computation would mean loading a client's local model checkpoint (not currently logged anywhere either) and diffing it against the corresponding `.npz` archive — a genuinely new extraction, not blocked by a missing file so much as by needing to build the comparison from two different large-array sources that were never designed to be joined this way.

### Per-attack-type sweep, sparsity, clipping compliance

**Not computed for this report** beyond the one flagship cell. The fields exist in every `proxy_attack_events` file; a full sweep across `sign_flip`/`scale`/`noise`/`min_sum` was not performed.

---

## RQ4 — Robust Aggregation Under Dynamic Byzantine Conditions

### Detection-quality confusion matrix — computed fresh for this report

Using the framework's TP/FN/FP/TN definitions (\(M_{r,c}\) = proxy ground truth that round r's update from client c was modified; \(\mathrm{inferred\_suspicious}\) = server's own flag), joined on `round` for the target client, `flame × min_max`, **now covering all three tracks (CNN unblocked 2026-07-26 — see §0.5 for the fix)**:

| Track | TP | FN | FP | TN | Precision | Recall |
|---|---|---|---|---|---|---|
| RNN | 36 | 24 | 12 | 6 | 0.75 | 0.60 |
| CNN | 76 | 4 | 9 | 11 | 0.89 | 0.95 |
| Autoencoder | 53 | 27 | 6 | 14 | 0.90 | 0.66 |

**FLAME's per-round suspicion flag is dramatically more reliable on CNN than on either other track — the strongest, most reliable detection signal found anywhere in this project.** CNN catches 95% of truly-poisoned rounds (vs. 66% Autoencoder, 60% RNN) while keeping a low false-alarm rate (9 of 20 clean rounds flagged, 45% — better than RNN's 67% though worse than Autoencoder's 30%). RNN remains the weakest: it catches only 60% of truly-poisoned rounds and wrongly flags 67% of clean rounds (12 of 18) as suspicious. On every track, the suspicion mechanism is separate from (and evidently not the sole thing driving) the cluster-admission mechanism reported below — even CNN's strong 0.95 recall still misses 5% of real attack rounds if relied on alone.

### Per-client inference detail — CNN `flame × min_max`, exp1

The server's own per-client inference summary for this exact cell (`Result/CNN/server/attack/flame/min_max/exp1/flame_run_01_20260723_183859_inference_clients.csv`), all 5 clients, 100 rounds each:

| Client IP | Suspicious rounds | Suspicious rate | Included rounds | Included rate | Mean inference rank | Best inference rank |
|---|---|---|---|---|---|---|
| 10.42.0.210 (target) | 84 | 84% | 16 | 16% | 3.02 | 1.0 |
| 10.42.0.59 | 27 | 27% | 73 | 73% | 2.83 | 1.0 |
| 10.42.0.145 | 27 | 27% | 73 | 73% | 3.20 | 1.0 |
| 10.42.0.18 | 26 | 26% | 74 | 74% | 3.09 | 1.0 |
| 10.42.0.47 | 22 | 22% | 78 | 78% | 2.86 | 1.0 |

`mean_inference_score`/`max_inference_score` are 0.0 for every client in this file — not populated for this run, not a real zero finding. The target's suspicious rate (84%) and included rate (16%) cross-validate the confusion-matrix row above (TP=76 of 80 truly-modified rounds correctly flagged, recall 0.95) — 84 flagged vs. 85 = TP+FP, consistent within one round. **Mean inference rank does not separate the target from benign clients** (3.02 vs. a 2.83–3.20 range for the four benign clients) — every client also reaches `best_inference_rank` 1.0 at least once, so rank alone is not a usable discriminator here; the suspicious-flag and inclusion-rate columns are what actually separate the malicious client from the benign four.

### FLAME — malicious cluster membership and clipping survival

`flame × sign_flip`, target `10.42.0.210`, 100 rounds — **now three-way comparable across RNN, CNN, and Autoencoder:**

| Track | Rounds in FLAME's main cluster | Rounds clipped | ΔAcc |
|---|---|---|---|
| RNN | 86/100 = 86% | 18/100 = 18% | −17.86pp |
| CNN | 83/100 = 83% | 21/100 = 21% | +0.78pp |
| Autoencoder | 81/100 = 81% | 95/100 = 95% | see `cross_architecture_comparison.md` §4 |

**The CNN admission number is now doubly verified — the original behavioral-identification workaround (matching per-round anomaly signal, used when `client_ip` was known to be broken) and the corrected `client_ip` field (fixed 2026-07-26 via norm-correlation identification, §0.5) independently agree on exactly 83%.** That agreement is itself useful evidence the identification methodology is sound. **Admission rates cluster tightly across all three architectures (81–86%) despite wildly different accuracy outcomes — this strengthens, not weakens, the original RNN/CNN puzzle.** FLAME's clustering step isn't behaving differently across architectures at the admission stage; something downstream of admission is. **Clip rate is where the tracks actually diverge: CNN 21%, RNN 18% — similar — but Autoencoder's 95% is a dramatic outlier**, more than 4× either other track. On Autoencoder, FLAME almost always admits the malicious client into the main cluster *and* clips its contribution afterward, while RNN and CNN mostly admit it *without* clipping. If clipping is supposed to bound the damage a malicious update can do even after admission, Autoencoder's near-universal clipping combined with its own defense-instability findings (§3 of `cross_architecture_comparison.md`) suggests clipping alone isn't sufficient protection either — worth a direct follow-up on whether Autoencoder's high clip rate is actually containing damage or just adding noise on top of an already-unstable aggregation. Leading hypothesis for the RNN/CNN admission-outcome mismatch specifically remains unconfirmed: CNN's 11.2M-parameter model likely dilutes one client's equal-weighted contribution far more than RNN's ~20K-parameter model does — would need \(I_{\mathrm{agg}}\), still not computed for any track.

### Krum — selection rank, and a genuine anomaly, now compared across tracks

`krum × min_sum`, target `10.42.0.210`, 100 rounds:

| Track | \(R_{\mathrm{admit}}\) | `krum_rank` distribution | ΔAcc |
|---|---|---|---|
| RNN | 0/100 = 0% | rank 3 (80×), rank 4 (5×), rank 5 (15×) | −27.76pp |
| CNN | 82/100 = 82% | rank 1 (82×), rank 2 (6×), rank 3 (1×), rank 4 (2×), rank 5 (9×) | −15.37pp |
| Autoencoder | 66/100 = 66% | rank 1 (66×), rank 2 (13×), rank 5 (21×) | see `cross_architecture_comparison.md` |

**Now a three-way divergence, and CNN is the most extreme of all: Krum admits the malicious client 0% of the time on RNN, 66% on Autoencoder, and 82% on CNN — with rank 1 (best match) in 82 of those 82 admitted rounds, i.e. every single time it's admitted, it's admitted as Krum's single best pick.** This is the opposite pattern from RNN in every respect: not just "sometimes admitted," but "admitted as the top candidate whenever admitted at all." This directly contradicts any assumption that Krum's distance-based selection behaves similarly across architectures — on CNN and Autoencoder, `min_sum`'s update-space geometry apparently looks like a *good* candidate to Krum's nearest-neighbor logic most of the time, while on RNN it never does. Notably, **CNN's ΔAcc (−15.37pp) is smaller than RNN's (−27.76pp) despite CNN admitting the attacker far more often (82% vs. 0%)** — high admission does not translate to proportionally worse damage here, reinforcing the RQ4 FLAME finding above that admission rate alone doesn't predict outcome; something in the aggregation step downstream of admission matters more. Given Autoencoder's own baseline instability (§3, `cross_architecture_comparison.md`) and Krum's uniquely severe, reproducible baseline collapse there (~19%, both runs), whatever makes Krum's baseline collapse on Autoencoder (with zero attackers) may be mechanistically related to why a malicious `min_sum` update looks "normal" to Krum once an attacker is present — worth investigating as one unified question rather than separate anomalies, and CNN's data (stable baseline, high admission, moderate damage) is a useful third reference point for that investigation.

**RNN's own anomaly stands as before, unresolved:** Krum's selection log shows the malicious update was never chosen, across 100 rounds — yet final accuracy is 27.76pp below baseline, Krum's largest documented collapse on RNN specifically. \(R_{\mathrm{admit}}=0\%\) by the direct definition, but the model still collapsed. Three honest candidate explanations remain unconfirmed (peer-geometry corruption without direct selection; baseline noise, ruled out as a full explanation since −27.76pp exceeds the documented 7.8pp baseline spread by more than 3×; a logging/aggregation mismatch worth a direct code check) — this remains the most important open finding in the whole evaluation and should be resolved by checking the Krum implementation, not smoothed into a story.

### Aggregate displacement \(I_{\mathrm{agg}}\), coordinate-median influence, phase-aware-vs-blind

**\(I_{\mathrm{agg}}\) not computed** — needs counterfactual re-aggregation. **Coordinate-median fields exist** in `server_client_defense_log` for Median/Trimmed-Mean rounds but weren't pulled. **Phase-aware vs. blind: not computable**, §0.

### Dynamic Byzantine conditions

**Not implemented** — no attack-scheduling knob exists in `poison_live.py`; every attack poisons every eligible round for the run's full duration. The framework's "attacker should not poison every round" requirement doesn't match how this codebase currently operates.

---

## RQ5 — Learning and System Impacts

### Global accuracy, precision, F1

**All three architectures now have complete or near-complete 6-defense × 5-attack matrices** — RNN and CNN's full 30/30 cells (`tables_ieee/csv/*.csv`, `tables_ieee/latex/*.tex`), Autoencoder's full 30/30 cells (`cross_architecture_comparison.md` §4). Prior versions of this table omitted Autoencoder entirely despite its matrix already being complete elsewhere in this project — fixed below.

| Track | Best clean baseline | Worst confirmed attack cell | ΔAcc |
|---|---|---|---|
| RNN | FedAvg 78.33% (n=5) | Krum × min_sum: 34.85% | −27.76pp |
| CNN | FedAvg 65.07% (n=2) | Krum × min_max: 39.65% | −20.42pp |
| Autoencoder | FedAvg 64.05% (n=2) | FLAME × min_sum: 30.47% | −23.81pp |

Krum's Autoencoder cells (18.58–19.82%) are lower still but excluded from this ranking — floor effect, not a genuine attack outcome (see §RQ4).

Macro F1 available for all 60 RNN/CNN cells in the same tables; Autoencoder's per-cell accuracy/precision/F1/ΔAcc for all 30 cells is in `cross_architecture_comparison.md` §4, not yet exported to a matching `tables_ieee`-style CSV/LaTeX pair.

**Autoencoder-specific findings, not present on RNN/CNN, worth stating directly rather than folding into a single cross-track number:** `scale` reverses from RNN/CNN's "harmless" classification on every healthy-baseline defense tested (FedAvg, Multi-Krum, Median, FLAME — 4/4, now complete); `noise` reverses on 3 of 4; direction-aware/peer-crafted attacks (`sign_flip`/`min_max`/`min_sum`) never reverse on any defense. **Krum's own baseline is collapsed (≈19%, both runs) before any attack runs at all**, making its attacked-condition ΔAcc uninterpretable by the framework's own definition (no accuracy left to lose) — excluded from the "worst confirmed cell" ranking above for that reason, not omitted by oversight. **FLAME is the most-damaged defense overall on Autoencoder** (mean ΔAcc −19.65pp across its five attacks), worse than plain FedAvg averaging (−12.13pp) — the opposite of what FLAME's more sophisticated clustering design would predict. Full detail, including the full 6×5 cell table: `cross_architecture_comparison.md` §4.

### AULC, convergence delay — formulas now specified, still not computed

\(\mathrm{AULC} = \frac{1}{R}\sum_{r=1}^R \mathrm{Acc}_r\), \(D_{\mathrm{conv}} = r^{\mathrm{attack}}(\tau) - r^{\mathrm{clean}}(\tau)\)

Raw learning-curve trajectories exist (`rq5_cnn_data.json`, `rq4_full_data.json`) with full per-round accuracy for several cells. **Both formulas are now precisely specified but still not computed** — mechanical follow-up on existing data, not a new experiment.

### Target-class metrics for targeted attacks

**Not applicable** — every attack in this project (`sign_flip`/`scale`/`noise`/`min_max`/`min_sum`) is untargeted. Not a gap; the metric doesn't apply to the current attack set.

### Systems evaluation

| Metric | Status | Value |
|---|---|---|
| Process CPU / memory (proxy) | available, all 3 tracks | RNN 0.78% CPU / 60.2MB RSS; CNN 6.75% CPU / 413.4MB RSS; Autoencoder 6.03% CPU / 310.1MB RSS |
| Round/phase duration | partially available | field-mapping issue on first extraction attempt |
| Decision/poisoning latency | covered under RQ2 | — |
| Throughput/goodput/bytes | partially available | `analyzer_wire_upload_log`, not computed |
| RTT, retransmits, packet loss, dup ACKs | not tracked | — |
| Client disconnection rate | not queried | `server_failure_log` likely covers this |

Proxy CPU/RSS scales with each architecture's parameter count (RNN ~20K, CNN ~11.2M) — not architecture-independent; full detail in `cross_architecture_comparison.md` §7. `sniffer.py` exists but its output isn't joined into any CSV with RTT/retransmit/packet-loss fields — a genuine instrumentation gap.

### \(O_{\mathrm{proxy}}\) and \(O_{\mathrm{poison}}\) — \(O_{\mathrm{poison}}\) now computable, per the §0 correction

\(O_{\mathrm{proxy}} = \frac{T_{\mathrm{proxy\ only}} - T_{\mathrm{clean}}}{T_{\mathrm{clean}}} \times 100\), \(O_{\mathrm{poison}} = \frac{T_{\mathrm{phase\ aware\ attack}} - T_{\mathrm{proxy\ only}}}{T_{\mathrm{proxy\ only}}} \times 100\)

**Per the corrected §0 mapping, `baseline` = \(T_{\mathrm{proxy\ only}}\) (proxy present and forwarding, analyzer fully active, poisoning disabled) — so \(O_{\mathrm{poison}}\) is now directly computable from existing data, using mean round duration (`analyzer_round_log`'s `round_duration_s`) per track:**

| Track | \(T_{\mathrm{proxy\ only}}\) median round duration | Baseline n rounds / experiments | \(T_{\mathrm{phase\ aware\ attack}}\) median round duration | Attack n rounds / experiments | \(O_{\mathrm{poison}}\) |
|---|---|---|---|---|---|
| RNN | 2.0054s | 14,696 / 30 | 1.9680s | 26,549 / 48 | −1.86% |
| CNN | 10.8690s | 6,000 / 12 | 9.0494s | 19,522 / 32 | −16.74% |
| Autoencoder | 8.9488s | 6,000 / 12 | 8.2806s | 18,637 / 31 | −7.47% |

**This is a genuinely surprising result, reported as computed rather than adjusted to match expectation: poisoning-enabled rounds are *faster* than baseline rounds on every single track, not slower.** Median used rather than mean specifically because round-duration means are heavily right-skewed by rare long-idle-gap rounds (the same phenomenon documented in RQ1's phase-duration analysis); mean-based figures would show the same direction but exaggerated magnitude. This contradicts the intuitive expectation that adding poisoning logic (update reconstruction, envelope projection, substitution) should add processing time to the round — instead, attack-condition rounds run 1.9–16.7% *faster*. Candidate explanations, none confirmed: (a) attack-condition experiments may have systematically different network/client conditions (different days, different concurrent load) that swamp any genuine per-round poisoning cost — the sample sizes differ substantially between conditions (e.g. CNN: 12 baseline experiments vs. 32 attack experiments), so this isn't a controlled apples-to-apples comparison in the strict sense; (b) poisoning logic may only add meaningful latency on the ~20% of rounds that are actually targeted and modified, diluted into near-invisibility when averaged across all 100 rounds per experiment (only 80 of 100 rounds are typically eligible+modified per the \(R_{\mathrm{selective}}\) finding in RQ2); (c) a genuine but small effect in the opposite direction (e.g., poisoned updates being simpler/more compressible, or some benign client behavior differing between conditions) cannot be ruled out from this data alone. **\(O_{\mathrm{proxy}}\) remains not computable** — it requires \(T_{\mathrm{clean}}\), a truly interception-free condition (no proxy/analyzer in the path at all), which per the §0 correction likely was never run in this codebase; `baseline` already includes the full proxy/analyzer pipeline, so it cannot serve as both \(T_{\mathrm{clean}}\) and \(T_{\mathrm{proxy\ only}}\) simultaneously.

### Required experimental comparison — 6 conditions specified, 3 satisfied by 2 measured datasets (corrected 2026-07-26)

| Condition | Purpose | Present in this repo? |
|---|---|---|
| Clean FL | Baseline | ✅ |
| Passive analyzer | Analyzer overhead | ✅ |
| Proxy forwarding only | Transport overhead | ✅ |
| Blind poisoning | Conventional-attack comparison | ❌ |
| Phase-aware poisoning | Proposed attack | ✅ |
| Oracle timing | Max achievable sync | ❌ |

The first three rows are all satisfied by the single `baseline` condition: this architecture's proxy/analyzer is always in-path even with poisoning disabled, so the three framework-distinct conditions collapse onto one measured dataset (§0).

---

## Statistical Validity

Framework requires **n≥5 independent runs**, paired tests, mean/SD/95% CI, effect sizes.

**This project has never claimed to meet that bar.** RNN baselines n=5 (meets it); RNN attack cells n=1 each (doesn't); CNN baselines n=2; CNN attack cells mostly n=1, with two cells having a second confirmation (FedAvg×min-max, FLAME×noise, both agreeing in direction/magnitude — reassuring, not statistical validation). No paired tests, CIs, or effect sizes exist anywhere, because n=1 makes them undefined for nearly every cell. Meeting this bar requires re-running most of the attack matrix 4+ more times each — a data-collection task, not an analysis task.

---

## Connected Evidence Chain — Synthesis

$$\text{Traffic inference} \rightarrow \text{precise synchronization} \rightarrow \text{valid substitute} \rightarrow \text{aggregator admission} \rightarrow \text{learning and system impact}$$

For `flame × min_max`, RNN (`exp_1784659861`, the cell most completely evidenced across every stage this session):

1. **Traffic inference (RQ1):** round tracking and phase transition quality both ≈100% on this track; DOWNLOAD/TRAINING phase classification F1 real but moderate and high-variance (0.42 ± 0.43 / 0.54 ± 0.24, attack condition), UPLOAD F1 = 0.000 ± 0.000 due to the client/analyzer ground-truth definition gap (see RQ1 above), though this specific cell's own numbers weren't separately re-pulled.
2. **Synchronization (RQ2):** \(R_{\mathrm{selective}}=100\%\), \(R_{\mathrm{spill}}=0\%\) — perfect internal selectivity once past warmup; 80% upload coverage.
3. **Valid substitute (RQ3):** 100% protocol-valid/finite/wire-compatible. **But envelope self-containment checks are 0.0 on every row** — the substitute is norm-conservative (R_norm≈0.41) but does not verify as staying inside its own intended stealth envelope. This is a real crack in the chain at this stage, not previously surfaced.
4. **Aggregator admission (RQ4):** Not pulled for this exact cell (min_max × FLAME); the comparable `sign_flip × FLAME` cell shows 86% (RNN) / 83% (CNN) admission — high, consistent across architectures.
5. **Impact (RQ5):** −9.07pp for `flame × min_max` (RNN) — real degradation, smaller than sign_flip's −17.86pp on the same defense.

**The `krum × min_sum` case remains the sharpest break in the chain project-wide:** zero measured admission (RQ4) alongside the largest accuracy collapse anywhere (RQ5, −27.76pp) — an unexplained disconnect, not a smoothed narrative, and still the most important open question this evaluation has surfaced.

### Summary table

| RQ | Core requirement met? | Biggest gap |
|---|---|---|
| RQ1 | Round tracking/sequence quality ≈100% on CNN/Autoencoder, 89.2% on RNN under attack (4-client sample — client-3 has no RNN baseline data, §0.5). Phase classification: DOWNLOAD/TRAINING moderate on every track, UPLOAD near-zero. Client fingerprinting: absent | RNN's round-tracking gap under attack not yet explained; phase temporal IoU/boundary-error not computed |
| RQ2 | \(R_{\mathrm{selective}}\)=100%, \(R_{\mathrm{spill}}\)=0% (RNN flagship cell); transition-detection latency computed for all 3 tracks | \(S_{\mathrm{exact}}\)/\(L_i\)/trigger P-R still blocked; no blind/random/periodic/oracle comparison conditions exist |
| RQ3 | Protocol validity 100%, R_norm/S_cos computed for all 3 tracks; envelope self-containment = 0.0 on every row, every track | \(E_{\mathrm{rec}}\) still not computed; per-attack-type sweep beyond the flagship cell not done |
| RQ4 | FLAME admission 86%/83%/81% (RNN/CNN/Autoencoder); Krum admission 0%/82%/66%; detection confusion matrix computed for all 3 tracks | Krum×min_sum's RQ4→RQ5 disconnect on RNN unresolved |
| RQ5 | Accuracy/precision/F1 matrix includes all 3 tracks; \(O_{\mathrm{poison}}\) computed for all 3 tracks — poisoning rounds run 1.9–16.7% faster than baseline on every track | No RTT/packet-loss data; \(O_{\mathrm{proxy}}\) not separable; AULC/D_conv formulas specified but not computed |
| Controls | 3 of 6 framework conditions satisfied, by 2 measured datasets | Blind/random/periodic/continuous/oracle triggering never implemented; true interception-free "clean" condition likely never run |
| Statistics | n=5 met for RNN baselines only | Virtually every attack cell is n=1 |

RQ1: final ground-truth-validated methodology (client log = truth, `analyzer_round_log`/`phase_log` = prediction) — full 5-client sample on CNN/Autoencoder, 4-client on RNN, after fixing several client-identity bugs (CNN `127.0.0.1` loopback on 3 of 5 clients, client-3's corrupted `src_ip`, a client-5 IP-history correction, client-1's misfiled RNN logs) and confirming client-3 has no RNN baseline data at all — the RNN round-tracking gap is a real finding, visible once client identity issues were fixed and the sample was expanded/corrected; UPLOAD's near-zero F1 traces to a client/analyzer ground-truth definition mismatch, not a detection failure; client fingerprinting is structurally absent (no classifier fields exist in the codebase).

RQ3: the 0.0 envelope self-containment result holds across all three architectures, not just RNN, so it needs investigation before calling this attack "stealthy" by the engine's own standard.

RQ4: FLAME clip rate diverges sharply by architecture (18% RNN vs. 21% CNN vs. 95% Autoencoder); Krum admission is a dramatic 3-way divergence (0% RNN, 82% CNN, 66% Autoencoder) reached after the CNN `client_ip` correction (§0.5) unblocked its Krum and confusion-matrix data.

Controls: `baseline` covers both "passive monitoring" and "proxy forwarding without manipulation" simultaneously, since this architecture's proxy/analyzer is always in-path.

---

*This report deliberately does not smooth gaps into a single clean narrative. Where a specific external claim about this repository's files was checked and found accurate (the RQ3 envelope numbers, the gateway-IP finding), that's stated as verified. Where a claim was checked and found incorrect for this repository (the "no matching server run exists" conclusion), that's corrected with the specific evidence, not silently dropped. Where a metric genuinely can't be computed with current instrumentation (client fingerprinting), that's stated as a capability gap, not a to-do item.*
