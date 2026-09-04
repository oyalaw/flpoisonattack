# Cross-Architecture Comparative Analysis — RNN vs. CNN vs. Autoencoder

*Extends [`evaluation_framework_report.md`](evaluation_framework_report.md), which evaluated the RQ1–RQ5 framework mostly against RNN. This document compares all three model tracks in this repository side by side, on every dimension where real data exists.*

---

## 1. Data completeness — the precondition for any comparison

| Track | Client logs | Proxy logs | Server logs | Attack cells populated |
|---|---|---|---|---|
| **RNN** | present | present | present | 30/30 |
| **CNN** | present | present | present | 30/30 |
| **Autoencoder** | present | present | present | 30/30 |

Client logs (all three tracks) come from `client_results/`, covering 2 of 5 physical clients each.

**Correction (2026-07-26): the "Autoencoder is missing client-side logs, unlike RNN/CNN" claim below was wrong, and so was the implied asymmetry.** All three tracks' `Result/<track>/client1`–`client5` directories are equally empty — that part was checked correctly. What was missed is a **separate, top-level `client_results/` directory** (`client_results/client-1/`, `client_results/client-4/`) that mirrors real client-side logs from 2 of the project's 5 physical clients (the other 3 have unsynced Syncthing folders, `.stfolder` markers only) — and it covers **all three tracks equally**: RNN (98/78 files for client-1/client-4), CNN (27/27), Autoencoder (42/41). There is no RNN/CNN-vs-Autoencoder asymmetry on this dimension at all; every track has the same 2-of-5-clients coverage. Schema and further detail in `evaluation_framework_report.md` §0.5. **Phase-classification quality for all three tracks is now computed with real precision/recall/F1 against client-log ground truth (§5, 2026-07-26) — round tracking is ≈100% on CNN/Autoencoder but drops to 89.2% on RNN under attack. RNN's sample is 4 of 5 clients, not 5: client-3 has zero RNN baseline files anywhere (real absence, not a bug) and client-1's RNN logs were misfiled and had to be recovered via timestamp-matching, both corrected 2026-07-26 — see `evaluation_framework_report.md` §0.5 for full detail.**

---

## 2. Baseline model quality — 3-way comparison (RNN, CNN, Autoencoder)

Source: final-round `global_accuracy` pulled directly from each experiment's own `server_metrics_log_*.csv`, deduplicated by file hash, per defense per track (RNN n=5, CNN n=2, Autoencoder n=2 runs per defense).

| Defense | RNN acc | CNN acc | Autoencoder acc |
|---|---|---|---|
| FedAvg | 78.33% ± 0.58pp | 65.07% ± 0.31pp | 64.05% ± 2.57pp |
| Median | 77.22% ± 3.09pp | 61.71% ± 0.06pp | 63.78% ± 2.35pp |
| Trimmed-Mean | 76.76% ± 2.93pp | 63.93% ± 0.25pp | 67.31% ± 2.26pp |
| Multi-Krum | 76.73% ± 1.72pp | 64.38% ± 0.02pp | 51.18% ± 0.41pp |
| FLAME | 72.97% ± 3.84pp | 63.37% ± 0.15pp | 54.28% ± 5.49pp |
| Krum | 62.61% ± 2.82pp | 60.07% ± 0.11pp | 19.15% ± 0.61pp |

**The immediate cross-architecture finding:** RNN and CNN both show a *mild, consistent* defense-dependent accuracy gap — Krum is the worst defense on both (roughly 8–16 percentage points below FedAvg), but every defense stays in a broadly usable range (60–78%) on both tracks. **Autoencoder does not follow this pattern at all.** On Autoencoder, defense choice alone — with zero attackers present — is the difference between a working classifier (FedAvg/Median/FLAME/Multi-Krum/Trimmed-Mean, 51–68%) and one that has collapsed to near the 5-class random-guess floor (Krum, 19%). This is not a smaller version of the RNN/CNN pattern — it's a qualitatively different failure mode that only shows up on this architecture.

---

## 3. Within-architecture defense stability — where the story gets more interesting

This is the comparison the framework doesn't explicitly ask for but the data demands, because **RNN and CNN's baselines are stable run-to-run; Autoencoder's are not**, and that instability is itself architecture-specific.

| Track | Defense | n | Runs (accuracy%) | Spread |
|---|---|---|---|---|
| RNN | Krum | 5 | 58.6–66.3% range | 7.7pp |
| CNN | every defense | 2 | tight pairs, see `tables_ieee` | <1pp typical |
| Autoencoder | FedAvg | 2 | 62.24, 65.87 | 3.6pp |
| Autoencoder | Median | 2 | 65.44, 62.11 | 3.3pp |
| Autoencoder | Multi-Krum | 2 | 51.47, 50.89 | 0.6pp |
| Autoencoder | FLAME | 2 | 58.16, 50.40 | 7.8pp |
| Autoencoder | Krum | 2 | 19.58, 18.72 | 0.9pp |
| Autoencoder | Trimmed-Mean | 2 | 65.72, 68.91 | 3.19pp |

Krum's collapse on Autoencoder is *reproducible* (both runs land within 1pp of each other, both near-random) — that reads like a real, structural interaction between Krum's distance-based selection and this architecture's update geometry, not noise. Trimmed-Mean reads as stable on the two runs currently on disk.

**This pattern has no counterpart on RNN or CNN.** Neither track has ever shown a defense collapsing to near-random accuracy in a clean baseline run, at any point in this project. Whatever is happening is either Autoencoder-architecture-specific, or specific to this dataset/task pairing — it cannot currently be distinguished between those two explanations with the data on hand, and doing so would need either (a) the same defenses run on a different architecture with the same task, or (b) a different task on the Autoencoder architecture. Neither exists yet.

---

## 4. Attack impact — RNN, CNN, and Autoencoder (30/30 cells, all 6 defenses complete)

Full 30-cell matrices for all three tracks now exist (`tables_ieee/` for RNN/CNN, §4 below for Autoencoder); headline comparison:

| | RNN | CNN | Autoencoder |
|---|---|---|---|
| Best clean defense | FedAvg, 78.33% | FedAvg, 65.07% | Trimmed-Mean, 67.31% |
| Worst attacked cell | Krum × min-sum, 34.85% | Krum × min-max, 39.65% | Krum × min-sum, 18.58% |
| Worst attacked cell excl. Krum | n/a | n/a | FLAME × min-sum, 30.47% |
| Worst ΔAcc | −27.76pp | −20.42pp | −24.13pp |

Per-attack effectiveness (mean ΔAcc across FedAvg, Multi-Krum, Median, FLAME — Krum excluded for floor-effect consistency across tracks, Trimmed-Mean excluded since it carries its own separately-tracked baseline):

| Attack | RNN mean ΔAcc | CNN mean ΔAcc | Autoencoder mean ΔAcc |
|---|---|---|---|
| sign_flip | −6.91pp | −1.84pp | −10.92pp |
| scale | +0.21pp | +1.59pp | −11.24pp |
| noise | +0.66pp | +1.00pp | −12.59pp |
| min_max | −11.61pp | −3.15pp | −14.47pp |
| min_sum | −11.31pp | −2.38pp | −12.82pp |

**Krum is the worst-performing defense under attack on both RNN and CNN** — consistent with Krum also being the weakest *baseline* performer on both tracks (§2), so its poor attacked-condition showing is at least partly inherited from an already-weaker starting point, not purely an attack-susceptibility story. Krum's baseline is 62.61% (RNN) / 60.07% (CNN) vs. FedAvg's 78.33%/65.07% — Krum starts 12–16pp behind even with no attacker.

**Autoencoder breaks this pattern.** Krum's baseline is already collapsed to 19.15% (§2) before any attacker runs, so its attacked cells (18.58–19.82%) look like the worst raw accuracy in the matrix but reflect almost no attack-driven movement (±0.7pp) — a floor effect, not attack susceptibility. Excluding Krum, the worst raw-accuracy cell is FLAME × min_sum (30.47%), and the single biggest point-drop anywhere in the matrix is Trimmed-Mean × min_max (−24.13pp) — worst-raw-accuracy and worst-ΔAcc point to different defenses, unlike RNN and CNN where Krum leads both measures.

The per-attack table makes the reversal finding directly visible as numbers rather than a yes/no label: `scale` and `noise` are mildly *positive* on RNN and CNN (+0.21 to +1.59pp) but consistently *negative* on Autoencoder (−11.24pp, −12.59pp) — the same two attacks that are harmless-to-helpful on the other two architectures are the ones that turn harmful here. `sign_flip`/`min_max`/`min_sum` stay negative on all three tracks, but hit roughly 2–6× harder on Autoencoder than on CNN.

### All six defenses now have complete attack rows — final synthesis

Every cell delivery-confirmed (80/100 or 80/101, the latter reflecting a documented one-round analyzer mislabeling artifact — see conversation record 2026-07-26 — that doesn't affect delivery counting). All figures are ΔAcc vs. each defense's own baseline mean, except Trimmed-Mean (baseline stability uncertain — see its own subsection below).

| Attack | FedAvg (64.05%) | Krum (19.15%) | Multi-Krum (51.18%) | Median (63.78%) | FLAME (54.28%) |
|---|---|---|---|---|---|
| sign_flip | −9.91pp | +0.39pp | −4.11pp | −7.53pp | −22.14pp |
| scale | −11.19pp | +0.45pp | −2.58pp | −10.73pp | −20.45pp |
| noise | −14.46pp | −0.43pp | +6.33pp | −20.75pp | −21.46pp |
| min_max | −17.04pp | +0.67pp | −9.82pp | −20.61pp | −10.40pp |
| min_sum | −8.06pp | −0.57pp | −7.10pp | −12.31pp | −23.81pp |
| mean ΔAcc | −12.13pp | n/a | −3.46pp | −14.39pp | −19.65pp |

Krum's mean ΔAcc is not meaningful (floor effect — every attack lands within ~1.2pp of its own already-collapsed baseline, no accuracy left to lose), shown as n/a rather than a misleading average.

**The headline result once every defense is in: FLAME is the most-damaged defense on Autoencoder, by a wide margin — the opposite of what its design intent would predict.** FLAME is a more sophisticated, clustering-based defense than FedAvg's plain averaging, yet its mean degradation (−19.65pp) is more than 1.6× FedAvg's (−12.13pp) and nearly 6× Multi-Krum's (−3.46pp). This is worth stating plainly rather than softening: **on this architecture, the more "advanced" Byzantine-robust defense (FLAME) is not more robust than plain averaging — it's the least robust healthy defense tested.**

**Cross-defense pattern, now complete across four defenses with single well-defined baselines (FedAvg, Multi-Krum, Median, FLAME):**

| Attack | Defenses where it reverses (harmless-on-RNN/CNN → harmful here) | Rate |
|---|---|---|
| `scale` | FedAvg, Multi-Krum, Median, FLAME | 4/4 |
| `noise` | FedAvg, Median, FLAME | 3/4 |
| `sign_flip` | none | 0/4 |
| `min_max` | none | 0/4 |
| `min_sum` | none | 0/4 |

This is now a strongly confirmed, four-defense-deep pattern, not a provisional read from one or two cells: **`scale` universally crosses from harmless to harmful on Autoencoder, regardless of defense mechanism. `noise` does the same on three of four defenses — Multi-Krum is the sole, consistent exception where the RNN/CNN pattern survives intact.** Direction-aware and peer-crafted attacks (`sign_flip`, `min_max`, `min_sum`) never reverse anywhere — whatever is different about this architecture, it specifically affects magnitude-only perturbation, not direction-based or peer-geometry-based crafting.

**FLAME's own internal pattern is a second, distinct finding layered on top of the cross-defense one:** four of FLAME's five attacks (scale, noise, sign_flip, min_sum) cluster tightly within 3.4 points of each other (−20.45 to −23.81pp) — FLAME doesn't discriminate between attack types the way other defenses do, it's just severely damaged by almost everything. `min_max` is FLAME's one exception, at less than half the severity (−10.40pp) of the other four. **This mirrors — and inverts — the `scale`-is-the-exception pattern every other defense shows: FLAME's odd-one-out attack is `min_max`, not `scale`.** No defense in this dataset has the same "exception attack" as any other: FedAvg/Multi-Krum/Median all have `scale` as their point of surprise (though in FedAvg/Median's case `noise` joins it), Trimmed-Mean has `scale` playing the opposite role (mildest, not harshest), and FLAME has `min_max` alone standing apart from an otherwise uniform wall of damage.

Magnitude ranking (mean ΔAcc, most to least damaged): **FLAME (−19.65pp) > Median (−14.39pp) > FedAvg (−12.13pp) > Multi-Krum (−3.46pp)**. Multi-Krum is consistently the mildest-hit defense across every attack type checked — its hits run at roughly a third of FLAME's magnitude for the same attacks.

**Two distinct data-quality bugs surfaced while building this table, both worth flagging on their own, and both now fixed:**

1. One `median × noise` run turned out to be mislabeled — its folder said `median`, but the server log's own `requested_defense`/`effective_defense`/`condition` fields all said `trimmed_mean`, while the *proxy* log's `active_defense` field said `median` — a genuine proxy/server configuration mismatch within a single run, not just a filename issue. That run was excluded and replaced with a verified rerun. This is the same bug class documented earlier in this project for a `multi-krum/noise` run — three confirmed instances project-wide now, pointing to a systemic issue in how the active-defense parameter propagates to the proxy vs. the server at launch.
2. A `trimmed_mean × sign_flip` run's proxy-side `experiment_id`/`run_id` read `exp_1765031223`/`run_1765031223` against the server's `exp_1785031223`/`run_1785031223` — a single digit substituted (8→6), the same recurring experiment_id-corruption class documented multiple times earlier in this project. Corrected directly in `proxy_attack_events_*.csv` (500 rows) and `proxy_run_manifest_*.json` (top-level and nested `configuration` fields) after confirming defense/attack/timing all matched the server side; originals preserved as `.bak`.

Both checks (defense-field agreement, experiment_id agreement) are now applied to every new Autoencoder result before it's reported — this table reflects that standard.

### Trimmed-Mean — complete row (5/5), and the pattern is real but not as clean as it looked at 4/5

All five attacks have now landed against Trimmed-Mean:

| Attack | Accuracy | vs. healthy baseline (65.72%) |
|---|---|---|
| min_max | 41.59% | −24.13pp |
| min_sum | 44.77% | −20.95pp |
| sign_flip | 49.82% | −15.90pp |
| noise | 53.08% | −12.64pp |
| scale | 57.63% | −8.09pp |

None land near the healthy baseline, which was the first real finding — but they don't converge on one another either. **Four attacks (min_max, min_sum, sign_flip, noise) cluster in a 41.59–53.08% band (11.5-point spread)**, well clear of the baseline. **`scale` sits apart, 4.5 points above that cluster and closer to the healthy baseline than any other attack** — the same "scale behaves unlike the other four" pattern already established, just showing up in a different form here. On FedAvg, Multi-Krum, and Median, `scale` stood out by being unexpectedly *harmful* (reversing from RNN/CNN's harmless norm). Here, `scale` stands out by being the *least* harmful of Trimmed-Mean's five attacks — same attack, same architecture, opposite kind of anomaly depending on which defense is running.

**Corrected framing (this supersedes the "all attacks converge on one failure state" hypothesis floated when only 3–4 results were in):** Trimmed-Mean's four non-`scale` attacks do cluster tightly in an intermediate zone clear of the healthy baseline — that part holds with n=4 and is worth keeping as a finding. But it's not "every attack collapses Trimmed-Mean to the same state" — it's "four mechanistically different attacks land in the same zone, and `scale` doesn't." The honest generalization is narrower than the mid-investigation version of this claim, and `scale`'s consistent oddness (in whichever direction) across all four healthy defenses tested is turning out to be the most robust single pattern in the entire Autoencoder dataset, more robust than any claim about the other four attacks converging.

With FLAME's row now complete, all six defenses are represented in this section.

---

## 5. RQ1 phase-classification quality — final methodology (2026-07-26): ground-truth-validated, full 5-client sample

**This section now points to `evaluation_framework_report.md`'s RQ1 section as the single source of truth rather than duplicating its tables** — that report has gone through a fifth and final revision this session (duration-based scoring replaced with real precision/recall/F1 via max-overlap matching against client-log ground truth, then re-run once ground truth expanded from 2 of 5 clients to all 5 after several client-identity bugs were found and fixed: CNN's `127.0.0.1` loopback bug on 3 of 5 clients, client-3's corrupted `src_ip` field, and a client-5 IP-history correction). Duplicating the full tables here risked exactly the kind of drift that happened before (this section still showed duration-collapse numbers from an earlier pass after the other report had already moved past them).

**Headline results:** Round Tracking Quality and Phase Transition (Sequence) Quality are ≈100% on CNN and Autoencoder (genuine full 5-client samples), but **RNN drops to 89.2% ± 6.6% on attack-condition round tracking**, on a 4-of-5-client sample — a real, broad-based finding across nearly every RNN attack experiment (range 69.0–99.0%), only visible once client identity issues were fixed; the original 2-client sample had suggested near-perfect tracking. Phase classification F1 (`DOWNLOAD`/`TRAINING`) is moderate and real on every track; `UPLOAD` is still close to zero everywhere due to the client/analyzer ground-truth definition mismatch (client logs serialization, analyzer detects wire transmission — different events), though with the fuller sample CNN and RNN now show small nonzero UPLOAD scores rather than a clean universal zero. Full tables, per-track/per-condition breakdowns, and the exact methodology are in `evaluation_framework_report.md` §RQ1 → "Phase and round quality — final methodology."

---

## 6. RQ3/RQ4 mechanism data — resolved for RNN and CNN here; RNN/CNN/Autoencoder now all three-way compared in `evaluation_framework_report.md`

**Update (2026-07-26): RQ3 and RQ4 now have real, directly-computed numbers for all three architectures — see `evaluation_framework_report.md` §RQ3/§RQ4 for the full three-way tables, not duplicated here.** Headline additions: envelope-containment failure (0.0 on every delivered row) confirmed on all three architectures; FLAME main-cluster admission clusters tightly across all three (81–86%) despite very different accuracy outcomes; clip rate is where CNN/RNN (18–21%, similar) diverge sharply from Autoencoder (95%, over 4× either). **CNN's `client_ip` blocker is now largely resolved** (25 of 32 CNN attack experiments corrected via norm-correlation identification, §0.5 of the main report) — this unblocked CNN's Krum admission and detection-confusion-matrix tables, previously marked blocked. Result: **Krum admits the malicious client 0% of rounds on RNN, 66% on Autoencoder, and 82% on CNN** (rank 1 — best match — in every one of those admitted CNN rounds) — a three-way divergence, not a two-way one. Detection quality is strongest on CNN too (P=0.89/R=0.95, beating both Autoencoder's P=0.90/R=0.66 and RNN's P=0.75/R=0.60). Where the behavioral-identification method (used before the fix) and the corrected `client_ip` field could both be checked against the same cell (`flame × sign_flip`), they agreed exactly (83% FLAME admission) — solid cross-validation that both approaches are sound.

For RNN's `fedavg × min_max` and `krum × min_sum` specifically (a different cell pair than the RQ3/RQ4 flagship cells above), real per-round geometry and admission data was pulled directly (see `evaluation_framework_report.md` §RQ3/RQ4): S_cos ≈ −0.11, R_norm ≈ 0.48, FLAME main-cluster admission 86%, Krum selection 0/100 despite a −27.76pp collapse.

**The CNN gap noted in an earlier version of this report turned out to be more specific than first described, and is now resolved.** RNN's `server_client_defense_log` identifies clients by IP address (`client_ip`) consistently, making a straightforward join possible. CNN's does not — but investigating properly (rather than leaving it as a stated-but-unverified gap) turned up two separate things:

1. **`client_ip` is not universally blank in CNN's logs — it's a mid-campaign fix.** Every CNN run through `trimmed_mean × sign_flip` (2026-07-23 13:51) has it blank; every run from `trimmed_mean × scale` (2026-07-23 14:13) onward has it populated — a clean timestamp boundary, not a random subset. Something in the logging pipeline was fixed partway through the CNN campaign.
2. **But even after the fix, `client_ip` isn't reliably usable for identification**, checked directly on `flame × sign_flip` (post-fix): of 5 clients, 3 share the identical placeholder value `127.0.0.1`, one shows a real IP (`10.42.0.47`) that isn't the actual target, and the true target (`10.42.0.210`, confirmed from the proxy side) doesn't appear in the server's IP column at all. IP-matching would have silently picked the wrong client or failed outright.

**Resolved instead by identifying the target behaviorally**, using delivered-round timestamps from the proxy log as ground truth and checking which client's per-round anomaly signal (`flame_cosine_distance_to_peer_mean`) actually shifts on those specific rounds: one client's mean distance drops from 0.870 (clean rounds) to 0.260 (delivered rounds) while the other four stay flat at ~0.82–0.87 regardless — an unambiguous signature. This method doesn't depend on `client_ip` being populated at all, so it generalizes to every CNN cell, not just the post-fix ones.

**Real result, CNN `flame × sign_flip`:** main-cluster admission 83/100 (83%), clipped 21/100, final accuracy 64.15% (ΔA = **+0.78pp**, harmless/anomalous — this project's existing classification for this cell, now independently corroborated).

**The comparison to RNN is the actual finding, and it's a genuine surprise:** RNN's same cell showed 86% admission and a **−17.86pp** collapse. **Admission rates are nearly identical (83% vs. 86%) despite completely opposite outcomes (harmless vs. devastating).** FLAME's clustering step isn't behaving differently across architectures — it lets the attacker in at almost the same rate either way. What differs is what happens *after* admission. The leading hypothesis (not yet confirmed, would need the aggregation-displacement metric \(I_{\mathrm{agg}}\) from `evaluation_framework_report.md`, still not computed for either track) is that CNN's much higher parameter count (11.2M vs. RNN's ~20K) dilutes one admitted malicious client's equal-weighted contribution to the aggregate far more than RNN's smaller model does — same admission, much smaller per-client leverage. This reframes the earlier open question from that report ("is this a fluke of n=1, or does FLAME's clustering genuinely behave differently against CNN's higher-dimensional update?") — the answer, on this evidence, is that the *clustering* doesn't differ; something downstream of it does.

---

## 7. Systems/resource footprint — computed for all three tracks; the earlier "architecture-independent" claim was wrong

**Correction (2026-07-26): this section previously asserted proxy overhead was architecture-independent and only pulled RNN's numbers on that assumption. That assumption was never checked and turned out to be wrong — the data existed for all three tracks the whole time (32 CNN files, 31 Autoencoder files, `proxy_resource_log_*.csv`) and simply hadn't been pulled.**

| Track | n files | n samples | Mean CPU% | Median CPU% | Max CPU% | Mean RSS | Median RSS | Max RSS |
|---|---|---|---|---|---|---|---|---|
| RNN | 57 | 47,976 | 0.78% | 0.0% | 1129% | 60.2 MB | 64.5 MB | 72.9 MB |
| CNN | 32 | 38,918 | 6.75% | 4.0% | 934% | 413.4 MB | 435.8 MB | 541.2 MB |
| Autoencoder | 31 | 31,544 | 6.03% | 2.0% | 729% | 310.1 MB | 340.3 MB | 415.4 MB |

**Proxy resource overhead scales with model size — it is not architecture-independent.** CNN's mean CPU is 8.7× RNN's, mean RSS is 6.9×; Autoencoder is similarly elevated (7.8×/5.1×). This tracks the actual parameter-count difference between the three architectures (RNN ~20K params, CNN ~11.2M, Autoencoder intermediate) — the proxy has to parse, hash, and rewrite proportionally larger gRPC messages per round, and that cost shows up directly in CPU and resident memory. Median values sit well below the means for all three tracks (RNN's median CPU is 0%), meaning usage is bursty — brief heavy spikes (message parsing/hashing on large payloads) rather than sustained load, consistent across tracks; the extreme max values (700–1100%+) likely reflect brief multi-core spikes during those bursts rather than sustained saturation, though this wasn't separately verified.

This means the earlier `O_proxy` discussion (§ RQ5 of `evaluation_framework_report.md`, still blocked by the missing "proxy-forwarding-only" control condition) would need **per-track** clean/proxy-only baselines if it's ever computed — a single RNN-derived overhead number would have been silently wrong for the other two tracks by a factor of 5–9×.

---

## 8. Summary — what's actually comparable right now

| Dimension | RNN | CNN | Autoencoder |
|---|---|---|---|
| Baseline accuracy/precision/F1 | full | full | full, all 6 defenses |
| Baseline stability | stable | stable | unstable, Krum reproducibly collapsed; Trimmed-Mean collapse observed once, currently unverifiable |
| Attack matrix (ΔAcc) | 30/30 | 30/30 | 30/30 |
| RQ1 round tracking (attack) | 89.2% (4/5 clients) | ≈100% | ≈100% |
| RQ1 TRAINING F1 (attack) | — | 0.19 | 0.13 |
| RQ3/RQ4 admission mechanism | pulled | pulled | pulled |
| Systems overhead: mean CPU / RSS | 0.78% / 60.2MB | 6.75% / 413.4MB | 6.03% / 310.1MB |
| Data-quality issues found and fixed | 3 corrupted experiment_ids | 44 `client_ip` fields (25 fixed, 7 unresolved, 12 unfixable) | 2 issues (1 defense-mismatch, 1 corrupted experiment_id) |

**Bottom line for a paper claiming cross-architecture generality:** RNN and CNN support that claim well — the same qualitative patterns (Krum weakest baseline and worst-attacked, sign_flip/min_max/min_sum harmful, scale/noise harmless, RNN hit consistently larger than CNN's) hold on both, independently measured. **Autoencoder's attack matrix is now complete across all six defenses, and the picture that emerges is specific and defensible, not a vague "it's different":**

- **Baseline behavior contradicts RNN/CNN on defense stability** (Krum reproducibly collapses to ~19%) — visible before any attack runs, still unexplained.
- **`scale` reverses on every one of the four defenses with a single well-defined baseline (4/4)** — FedAvg, Multi-Krum, Median, and now FLAME. This is the strongest, most consistent finding in the entire Autoencoder dataset.
- **`noise` reverses on three of four (FedAvg, Median, FLAME)**, staying harmless — even positive — only on Multi-Krum, which is the sole defense where the RNN/CNN pattern survives fully intact.
- **`sign_flip`/`min_max`/`min_sum` never reverse on any defense** — direction-aware and peer-crafted attacks behave identically to RNN/CNN everywhere. Whatever is different about this architecture is specific to magnitude-only perturbation.
- **FLAME is the most-damaged defense overall (mean ΔAcc −19.65pp), more than plain FedAvg averaging (−12.13pp) and nearly 6× Multi-Krum (−3.46pp)** — a genuinely surprising, headline-worthy result: the more sophisticated clustering-based defense is *less* robust than simple averaging on this architecture, not more. FLAME's own row has a distinct internal shape too — four of five attacks cluster within 3.4 points of each other (severe, uniform damage), with `min_max` alone sitting apart as its one milder attack, the mirror image of every other defense's `scale`-is-the-exception pattern.
- **Trimmed-Mean shows a within-defense pattern**: four attacks cluster in an intermediate zone clear of the healthy baseline, while `scale` again stands apart — this time as the *mildest*, not the harshest, the opposite role it plays everywhere else.
- **Krum's complete row remains unusable evidence for or against generality** — floor effect, no accuracy left to lose.
- **Magnitude ranking, most to least damaged: FLAME > Median > FedAvg > Multi-Krum**, a roughly 6× spread from worst to mildest defense for the same attack set.
- **Phase and round quality, now ground-truth-validated (§5), flips the earlier read again — RNN is the track with the open question, not CNN/Autoencoder.** Round tracking and sequence quality are ≈100% on CNN and Autoencoder (genuine 5-client samples) but drop to 89.2% ± 6.6% on RNN under attack, on a 4-of-5-client sample (client-3 has no RNN baseline data at all), broadly across nearly every RNN attack experiment (69–99.0% range), only visible once the original 2-client sample was expanded and client identity issues were fixed. Phase classification F1 for `DOWNLOAD`/`TRAINING` is real and moderate on every track; `UPLOAD` stays near-zero everywhere from the client/analyzer ground-truth definition mismatch (documented in RQ2). Autoencoder's operational profile still differs from RNN/CNN structurally on baseline instability (§3) and attack-type reversal (above).
- **Proxy systems overhead scales with model size, not architecture identity per se** (§7) — CNN and Autoencoder both run the proxy at 6–7% mean CPU and 300–400MB RSS, roughly 6–9× RNN's footprint, tracking each architecture's parameter count. Worth remembering for any future systems-overhead claim: a number pulled from one track cannot be assumed to generalize to the others, checked here after initially assuming otherwise.
- **Admission mechanism (RQ3/RQ4), now complete for all three architectures (§6), splits into one attack-specific finding and one sharply divergent one.** Attack-specific: envelope self-containment is exactly 0.0 on every delivered row, on every track, for `min_max`/`min_sum`/`krum_optimal` — the geometry-targeting attacks — the crafted substitute never verifies as staying inside its own intended stealth envelope for those three. But a full attack sweep (`evaluation_framework_report.md`'s NetPhaser appendix, Table 23) shows `sign_flip`/`scale`/`noise` stay substantially inside envelope (56–98% depending on architecture) — this is not a universal engine failure, it's specific to attacks that target coordinates/ranks directly. Divergent: Krum's admission of the malicious client is 0% (RNN), 66% (Autoencoder), 82% (CNN) — and on CNN, every admitted round ranks the malicious update *first* by Krum's own distance metric, the opposite pattern from RNN's complete rejection. Higher admission doesn't mean proportionally worse damage (CNN's ΔAcc for this cell, −15.37pp, is smaller than RNN's −27.76pp despite 82 points higher admission) — something downstream of admission, not admission itself, appears to be the deciding factor.

**The one claim that holds everywhere `scale` was tested: it never behaves like the "normal case" for whatever defense it's up against** — harsh on four defenses, uniquely mild on the fifth (Trimmed-Mean). The right framing for a paper is not "Autoencoder is more vulnerable to poisoning" broadly, but three specific, evidenced claims: (1) magnitude-only perturbation (`scale`, and to a lesser extent `noise`) crosses from harmless to harmful on this architecture in a way it never does on RNN/CNN, largely independent of defense; (2) defense sophistication does not predict robustness here — FLAME's clustering mechanism performs worse than FedAvg's plain averaging, inverting the ranking RNN/CNN would suggest; (3) the phase-detection pipeline this whole attack depends on has an open reliability question on RNN specifically — round tracking drops to 89.2% under attack on RNN's 4-of-5-client sample, a gap CNN and Autoencoder (genuine 5-client samples) don't show — worth checking whether that affects attack *delivery* rates too, not just RQ1's classification metric.
