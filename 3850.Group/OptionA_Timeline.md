# Option A — Full Pipeline Timeline (May 12 → May 29, 2026)

**Course:** QBUS3850 Group Assignment
**Persona:** Airline / freight carrier hedger (Option A)
**Team:** 5 members
**Today:** Tue 12 May 2026
**Due:** Fri 29 May 2026
**Window:** 17 calendar days · ~13 weekdays + 4 weekend days

---

## Member Roles (referenced as M1–M5 below)

| Member | Primary role |
|---|---|
| **M1** | Data acquisition, tracking-gap diagnostic, EDA scaffolding, figures |
| **M2** | Simple/explainable model + benchmark hedge strategies + metrics framework |
| **M3** | Max-performance model (Auto-ARIMA / ARIMA-X / SARIMA / VECM / GARCH for PI) |
| **M4** | Creative model (Kalman dynamic hedge ratio) + 4-strategy backtest engine |
| **M5** | Report writing, figures polish, notebook integration, reproducibility check |

---

## Phase 1 — Setup & Data (May 12–14, 3 days)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 0 | **Tue 12 May** | All 5 | Lock in Option A; team reviews `OptionA.md`; assign roles |
| 1 | **Wed 13 May** | M1 | `01a_data_acquisition.ipynb` runs clean; 16 raw CSVs + `prices.parquet` in `data/a/` |
| 2 | **Thu 14 May** | M1 | Tracking-gap diagnostic complete (USO↔CL=F, UNG↔NG=F, UGA↔RB=F, KRBN↔KEUA); summary table populated |

**Checkpoint 1 (end of Thu):** data is locked. No more re-pulls. Everyone codes against `data/a/processed/prices.parquet` from here.

---

## Phase 2 — EDA (May 15–17, 3 days, includes weekend)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 3 | **Fri 15 May** | M1 | STL decomposition for all 12 series; vol-clustering check (squared-return ACF); ARCH-LM tests |
| 4 | **Sat 16 May** | M1 | Cointegration tests (Johansen) on Brent–WTI, HO–RBOB, HH–TTF; structural-break detection |
| 5 | **Sun 17 May** | M1 + M5 | EDA figures finalised; 3-page EDA narrative draft handed to M5 |

**Checkpoint 2 (end of Sun):** EDA section of report is essentially written. All stylised facts confirmed.

---

## Phase 3 — Model Builds in Parallel (May 18–22, 5 weekdays)

All members work against the same `prices.parquet`. Hand-off artifacts are standardised (see Hand-off Protocol below).

| Day | Date | M2 (Simple) | M3 (Max performance) | M4 (Creative + Backtest) |
|---|---|---|---|---|
| 6 | **Mon 18 May** | Naive forward + ETS + low-order ARIMA on 2 pilot series | Auto-ARIMA scaffold; ARIMA-X with USD on 2 pilot series | Backtest engine skeleton: 4 hedge strategies on 1 pilot |
| 7 | **Tue 19 May** | Roll out simple to all 12 series; MAE table | SARIMA where significant; GARCH for prediction intervals | Kalman dynamic hedge ratio on 2 pilots |
| 8 | **Wed 20 May** | Compare simple candidates per series; pick winner per series | VECM on cointegrated pairs; model combination by inverse MAE | Roll out Kalman to all hedge-relevant series |
| 9 | **Thu 21 May** | Simple model frozen; hand outputs to M5 | Max-perf model frozen; hand outputs to M5 | Full 4-strategy backtest on all 12 series |
| 10 | **Fri 22 May** | Spare — help M3/M4 with debugging | Spare — buffer for convergence failures | Backtest results table; comparison vs no-hedge baseline |

**Checkpoint 3 (end of Fri):** all 3 models produce forecasts on full holdout for all 12 series; backtest engine runs end-to-end.

---

## Phase 4 — Validation & Cost Analysis (May 23–24, weekend)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 11 | **Sat 23 May** | M3 + M4 | Rolling-origin validation across 6 cut-offs; per-horizon MAE / MAPE / PI coverage |
| 12 | **Sun 24 May** | M4 | Final cost-comparison table: avg annual cost · std monthly cost · P95 overrun · bps savings vs no-hedge — per strategy per model |

**Checkpoint 4 (end of Sun):** all results numbers are final. No more model tweaks. Writing-only phase.

---

## Phase 5 — Report Drafting (May 25–27, 3 days)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 13 | **Mon 25 May** | M5 + each member | Each member writes their section draft: M1 EDA, M2 simple, M3 max-perf, M4 creative + backtest, M5 exec summary + conclusions |
| 14 | **Tue 26 May** | M5 | Stitch sections; enforce 15-page budget; consistent voice and figure style; **clean-env "Run all cells" dry-run** |
| 15 | **Wed 27 May** | M5 + M1 | Figures polished; tables formatted; cross-references checked; references list |

**Checkpoint 5 (end of Wed):** PDF is 14 of 15 pages; no broken figures.

---

## Phase 6 — Integration & Reproducibility (May 28, 1 day)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 16 | **Thu 28 May** | M5 | Combine into single submission notebook; `Run all cells` from clean kernel in fresh env; export `prices.csv` alongside; PDF final pass |

**Checkpoint 6:** notebook runs end-to-end with no errors. PDF is final.

---

## Phase 7 — Submission (May 29)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 17 | **Fri 29 May** | All 5 | Final read-through (each member proof-reads someone else's section); submit before deadline |

---

## Critical-Path Risks (priority order)

1. **Kalman hedge-ratio convergence on noisy series (Day 7–9)** — if it fails, fall back to OU mean-reversion as the creative model. **Decision deadline: Day 9 (Thu 21 May).**
2. **GARCH PI calibration not hitting 80% / 95% coverage on holdout (Day 7–8)** — fall back to bootstrap intervals. **Decision deadline: Day 8 (Wed 20 May).**
3. **Backtest engine bugs (Day 6–9)** — strictest test: spot-cost backtest should match `(realised_price × volume)` exactly. Build this sanity test on Day 6.
4. **15-page squeeze (Day 14–15)** — each section has a fixed page budget; figures captioned tightly; appendix-style detail stays in notebook.
5. **"Run all cells" failure on Day 16** — clean-env dry-run is on Day 14 (Tue 26 May), NOT Day 16. Buffer is built in.

---

## Built-in Buffers

- **3 weekend days** (May 16, 17, 24) — used for EDA depth and validation, not idle
- **Friday 22 May** — half-buffer for model debugging
- **M5 owns integration** from Day 13 so writing and code never block each other
- **One full day (28 May)** for reproducibility — not crammed in on submission day

---

## Hand-off Protocol Between Members

After each major checkpoint, the downstream member gets a single artifact:

| Hand-off | Artifact path |
|---|---|
| M1 → M2/M3/M4 | `data/a/processed/prices.parquet` (one file, never re-pulled) |
| M2/M3/M4 → M5 | `forecasts/<model_name>/<series>_<horizon>.parquet` |
| M4 → M5 | `results/hedge_strategy_comparison.csv` |

Standardise these handoffs early (Day 6 morning) to save friction all week.

---

## Daily Stand-up Cadence (recommended)

- **Mon / Wed / Fri @ 15:00** — 15-minute stand-up: blockers, hand-off status, risk-check
- **Sun evening** — written status summary by M5 in `docs/cowork.md` (one line per member)

---

## Member Workload Profile

| Member | Heavy days | Spare days | Notes |
|---|---|---|---|
| M1 | Days 1–5 (data + EDA) | Days 6–9 | Spare days support M3/M4 figures |
| M2 | Days 6–9 (simple) | Day 10, Days 13+ | Spare day for buffer; report writing later |
| M3 | Days 6–11 (max-perf + validation) | Days 12–13 | Spare day for buffer; report writing later |
| M4 | Days 6–12 (creative + backtest) | Days 13–14 | **Heaviest workload — most demanding member-role** |
| M5 | Days 5, 13–17 (integration + report) | Days 6–12 (light) | Light early, heavy late |

---

## Submission Checklist (Day 17 morning)

- [ ] PDF report exactly 15 pages or fewer (no appendix)
- [ ] Single Jupyter notebook executes cleanly via "Run all cells" in clean env
- [ ] `prices.csv` in the same folder as the notebook
- [ ] All figures are programmatically generated (not pasted images)
- [ ] References list present
- [ ] Admin log (internal) up-to-date
- [ ] Final read-through by 2 members different from the section author
- [ ] Submit before deadline

---

*End of Option A timeline.*
