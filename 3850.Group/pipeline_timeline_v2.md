# Full Pipeline Timeline v2 (May 15 → May 29, 2026)

**Course:** QBUS3850 Group Assignment
**Persona:** Qantas Group — joint fuel + AUDUSD hedger
**Team:** 5 members
**Today:** Fri 15 May 2026
**Due:** Fri 29 May 2026
**Window:** 14 calendar days · 10 weekdays + 4 weekend days

> **Changes from v1:** persona locked to Qantas (real hedger with public disclosures); data sources expanded to Yahoo + EIA + FRED (EIA needed for exogenous inventory data, USGC Jet, and refinery utilisation); basket revised (dropped JETS, KRBN, XLE; added cracks, AUDUSD, USGC Jet); methodology deepened (forward curve baseline, VECM with Johansen, DCC-GARCH, Diebold-Mariano tests, CRPS/pinball loss); frequency-dynamics subsection added for rubric coverage. Operational structure, hand-off protocol, and role split kept from v1.

---

## 1. Project Framing (Locked)

**Persona:** Qantas Group (ASX: QAN). Australian flag carrier, active hedger. FY25 disclosures show ~77–81% of forward fuel hedged via Brent + Singapore Jet Kerosene swaps + option structures.

**Exposure being modelled:** AUD cost per barrel of fuel consumed = (USD jet fuel price) × (AUDUSD), so the hedging problem has two axes — commodity and FX. Both must be modelled.

**Business decision being supported:** how much fuel exposure to hedge, on what tenor, with what instrument.

**Forecast types delivered:**
- Point forecasts → fuel budget submission to board
- Prediction intervals → hedge sizing (wider interval ⇒ larger hedge)
- Distribution → quantile-based hedge sizing and (optional) collar strike selection

---

## 2. Series Basket (15 series — same nature, +2 FX auxiliary)

### 2.1 Tradable hedge instruments (Yahoo Finance)
| # | Instrument | Ticker | Role |
|---|---|---|---|
| 1 | WTI Crude | `CL=F` | Inter-crude relative; second hedge candidate |
| 2 | Brent Crude | `BZ=F` | **Primary Qantas hedge instrument** |
| 3 | NYMEX Heating Oil (ULSD) | `HO=F` | **Academic-standard jet fuel proxy** (Adams & Gerner 2012) |
| 4 | RBOB Gasoline | `RB=F` | Refined product, refinery economics |
| 5 | Henry Hub Natural Gas | `NG=F` | Refinery operating cost driver |
| 6 | Dutch TTF Gas | `TTF=F` | European energy context |
| 7 | US Oil Fund | `USO` | ETF alternative to `CL=F` hedge |
| 8 | US Natural Gas Fund | `UNG` | ETF alternative to `NG=F` hedge |
| 9 | US Gasoline Fund | `UGA` | ETF alternative to `RB=F` hedge |

### 2.2 Physical jet benchmark (EIA, daily)
| # | Series | Source | Role |
|---|---|---|---|
| 10 | USGC Kerosene-Type Jet Fuel Spot | EIA `EER_EPJK_PF4_RGC_DPG` | True jet fuel benchmark; basis risk vs `HO=F` is hedgeable |

### 2.3 Cracks and spreads (computed from above)
| # | Spread | Definition | Role |
|---|---|---|---|
| 11 | Jet–Brent crack | USGC Jet − `BZ=F` | **Where the basis risk lives**; central to the hedging story |
| 12 | HO–Brent crack | `HO=F` − `BZ=F` | Refining margin proxy |
| 13 | Brent–WTI spread | `BZ=F` − `CL=F` | Inter-crude relative dynamics |

### 2.4 FX (auxiliary axis — 2 series, separate from energy basket)
| # | Series | Ticker | Role |
|---|---|---|---|
| 14 | AUDUSD | `AUDUSD=X` | **Multiplies onto every USD energy forecast** |
| 15 | US Dollar Index | `DX-Y.NYB` | Broader USD regime indicator |

**Energy basket total: 13 series (Layers 1–3) ✓ exceeds rubric minimum of 10.**
**FX auxiliary: 2 series — framed as parallel exposure, not counted toward the 10+ same-nature requirement.**

### 2.5 Exogenous drivers (features, NOT forecast targets)
Pulled into a parallel `exogenous_features.parquet` and used as ARIMAX regressors / LightGBM features:
- EIA weekly distillate stocks (Wed 10:30 EST release schedule — qualifies as "available ahead of time")
- EIA weekly crude oil inventories
- EIA refinery utilisation rate
- VIX (`^VIX`), Oil VIX (`^OVX`)
- 3-month T-bill (`^IRX`), 10-year Treasury (`^TNX`)

### 2.6 Dropped from v1 (with reasons)
- `JETS` (airline equity ETF) — airline stock prices are driven by many factors beyond fuel/output; methodologically dodgy as a "natural hedge anchor"
- `KRBN` (carbon ETF) — Australian carbon system differs from EU/RGGI; underlying `KEUA` was liquidated March 2026
- `XLE` (energy sector ETF) — duplicative of underlying commodities

---

## 3. Member Roles

| Member | Primary role |
|---|---|
| **M1** | Data acquisition (Yahoo + EIA + FRED), tracking-gap diagnostic, EDA scaffolding, figures |
| **M2** | Simple/explainable model (ETS, ARIMA, naive, forward-curve baseline) + frequency dynamics analysis + metrics framework |
| **M3** | Max-performance model (Auto-ARIMA, ARIMA-X, SARIMA, VECM with Johansen, univariate GARCH, **DCC-GARCH**) + Diebold-Mariano testing |
| **M4** | Creative model (Kalman dynamic hedge ratio) + 4-strategy backtest engine + CRPS/pinball loss computation |
| **M5** | Report writing, figures polish, notebook integration, reproducibility check |

---

## 4. Phase 1 — Setup & Data (May 15–16, 2 days)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 0 | **Fri 15 May** | All 5 | Plan handover + kickoff. M1 starts Yahoo pulls (15 tradable/FX/index tickers). M5 sets up repo + notebook scaffold. |
| 1 | **Sat 16 May** | M1 | EIA pulls (USGC Jet, distillates, crude inventories, refinery util via `eiapy` or HTTP). Compute cracks/spreads. Output `data/processed/prices.parquet` (15 series) + `exogenous_features.parquet`. Run tracking-gap diagnostic (USO↔CL=F, UNG↔NG=F, UGA↔RB=F). Missingness + outlier report. |

**Checkpoint 1 (end of Sat):** data is locked. Everyone codes against `prices.parquet` from here. No re-pulls.

---

## 5. Phase 2 — EDA (May 17–18, 2 days)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 2 | **Sun 17 May** | M1 + M5 | M1: ADF + KPSS stationarity; STL decomposition on all series; vol-clustering (squared-return ACF + ARCH-LM); structural breaks (COVID 2020, Ukraine 2022, Iran 2024–25). M5 starts drafting Dataset & Business Context. |
| 3 | **Mon 18 May** | M1 + M5 | M1: **Johansen cointegration tests** on Brent–WTI, HO–Brent, HO–RBOB, jet–Brent; cross-correlation lag analysis; rolling correlation heatmaps. EDA figures finalised (8–10 figures). EDA narrative draft handed to M5. |

**Checkpoint 2 (end of Mon):** EDA section essentially written. Stylised facts confirmed and documented.

---

## 6. Phase 3 — Model Builds in Parallel (May 19–23, 5 days)

All members work against `data/processed/prices.parquet`. Hand-off artifacts standardised on Day 4 morning.

| Day | Date | M2 (Simple + Frequency) | M3 (Max-perf + DM) | M4 (Creative + Backtest) |
|---|---|---|---|---|
| 4 | **Tue 19 May** | Random walk, seasonal naive, ETS, low-order ARIMA on 3 pilots (Brent, HO, USGC Jet). **Pull forward-curve baseline** (CL2/CL3/CL6/CL12 from Yahoo month codes — non-negotiable benchmark). | Auto-ARIMA scaffold; ARIMA-X with EIA distillate stocks + AUDUSD as exogenous on 3 pilots. | Backtest engine skeleton — 4 strategies (no hedge / naive 50% / naive 100% / model-driven) on Brent pilot. **Sanity test:** spot cost = realised_price × volume × FX. |
| 5 | **Wed 20 May** | Roll out simple to all 13 energy series. MAE / MAPE / **pinball loss** table. Winner per series. | SARIMA where seasonality significant (NG, TTF, RB). **Univariate GARCH(1,1)** per series for prediction intervals. | **Ederington static OLS min-var hedge ratio** as baseline. Kalman dynamic hedge ratio on jet–Brent and jet–HO crack pairs. |
| 6 | **Thu 21 May** | Simple model frozen. Hand outputs to M5. | **VECM on cointegrated pairs** identified in EDA. Johansen rank tests. **DCC-GARCH** for time-varying covariance matrices. | Roll out Kalman to all hedge-relevant series. **Integrate DCC-GARCH covariances** from M3 into dynamic min-var hedge ratio. |
| 7 | **Fri 22 May** | **Frequency dynamics:** same model at daily vs weekly vs monthly aggregation. One subsection for the report. | Model combination weighted by inverse MAE. **Diebold-Mariano tests** for pairwise model significance. | Full 4-strategy backtest on all hedge-relevant series. **CRPS and pinball loss** for distributional forecast quality. |
| 8 | **Sat 23 May** | Spare — help M3/M4 debug or polish figures. | Max-perf frozen. Hand outputs to M5. | Backtest results table. Sensitivity analysis on Qantas volume assumption (~30M barrels-equivalent annual fuel from FY25 disclosure). |

**Checkpoint 3 (end of Sat):** all 3 models produce forecasts on full holdout for all series; backtest engine runs end-to-end.

---

## 7. Phase 4 — Validation & Cost Analysis (May 24–25, 2 days)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 9 | **Sun 24 May** | M3 + M4 | **Rolling-origin validation** across 6 cut-offs (covering COVID, Ukraine, Iran in turn). Per-horizon metrics — MAE, MAPE, **CRPS, pinball, 80%/95% PI coverage, Diebold-Mariano p-values**. Horizons: 1 day, 5 days, 1 month, 1 quarter. |
| 10 | **Mon 25 May** | M4 | Final cost comparison: per strategy × per model — mean AUD cost/barrel, std monthly AUD cost, **P95 worst-month overrun**, bps savings vs no-hedge, Sharpe-like (savings ÷ vol reduction). Bootstrap CIs on cost-savings estimates. |

**Checkpoint 4 (end of Mon):** all results numbers final. Writing-only from here.

---

## 8. Phase 5 — Report Drafting (May 26–27, 2 days)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 11 | **Tue 26 May** | All 5 | Each member writes their section draft in parallel:<br>• M1: EDA (3 pages)<br>• M2: Simple model + frequency dynamics subsection<br>• M3: Max-performance model (largest part of methodology)<br>• M4: Creative + 4-strategy backtest results<br>• M5: Executive Summary + Dataset & Business Context + Conclusions/Limitations |
| 12 | **Wed 27 May** | M5 + M1 | M5 stitches sections; enforces 15-page budget; consistent voice and figure style. **Clean-env "Run all cells" dry-run #1.** M1 polishes figures. |

**Checkpoint 5 (end of Wed):** PDF at 14 of 15 pages, no broken figures.

---

## 9. Phase 6 — Integration & Reproducibility (May 28, 1 day)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 13 | **Thu 28 May** | M5 | Combine into single submission notebook. Run all cells from clean kernel in fresh conda env. Export `prices.csv` alongside notebook. PDF final pass — typography, references, cross-references. Each member reviews their own section once more. |

**Checkpoint 6:** notebook runs end-to-end with no errors. PDF is final.

---

## 10. Phase 7 — Submission (May 29)

| Day | Date | Owner | Deliverable |
|---|---|---|---|
| 14 | **Fri 29 May** | All 5 | Final read-through — each member proof-reads someone else's section. Submit before deadline. |

---

## 11. Critical-Path Risks (Priority Order)

1. **Kalman hedge-ratio convergence on noisy series (Day 5–7)** — fallback to OU mean-reversion on cracks, or rolling-window OLS hedge ratio. **Decision deadline: end of Day 7 (Fri 22 May).**
2. **DCC-GARCH convergence on 13-series basket** — multivariate GARCH is hard to fit on large baskets. Fallback to univariate GARCH per series + rolling-window OLS covariance for dynamic hedge ratios. **Decision deadline: end of Day 6 (Thu 21 May).**
3. **EIA API rate limits or downtime (Day 0–1)** — mitigation: pull on Day 1, cache aggressively, never re-pull mid-project. Have a fallback static CSV download from EIA's web bulk-download page in case the API misbehaves.
4. **VECM rank ambiguity (Johansen returns conflicting trace vs eigenvalue ranks) (Day 6)** — fallback to bivariate VECM on jet–Brent crack only; report robustness across rank choices.
5. **Forward-curve gaps in Yahoo (CL2/CL3/CL6/CL12 sometimes missing)** — mitigation: forward-fill within a contract, splice across contracts with rollover adjustment; if it fails, synthesize from cost-of-carry using `^IRX`.
6. **Backtest engine bugs (Day 4–6)** — sanity test on Day 4: spot cost = realised_price × volume × FX (no model). This must match exactly before any hedge logic is layered on.
7. **15-page squeeze (Day 11–12)** — each section has a fixed page budget; appendix-style detail lives in the notebook (notebook is unbounded).
8. **"Run all cells" failure on Day 13** — clean-env dry-run is on Day 12, NOT Day 13. Buffer is built in.

---

## 12. Built-in Buffers

- **3 weekend days** (Sat 16, Sun 17, Sun 24) — used for EDA depth and validation, not idle
- **Sat 23 May** — half-buffer for model debugging
- **M5 owns integration** from Day 11 so writing and code never block each other
- **One full day (Thu 28 May)** for reproducibility — not crammed onto submission day

---

## 13. Hand-off Protocol Between Members

| Hand-off | Artifact path |
|---|---|
| M1 → all | `data/processed/prices.parquet` (15 series, daily, aligned) |
| M1 → all | `data/processed/exogenous_features.parquet` (EIA inventories, FX, rates, VIX) |
| M1 → all | `data/quality/tracking_gap_report.csv` |
| M2/M3/M4 → M5 | `forecasts/<model_name>/<series>_<horizon>.parquet` (point + quantile forecasts) |
| M3 → M4 | `models/dcc_garch/cov_matrices.parquet` (time-varying covariance for dynamic hedge ratios) |
| M4 → M5 | `results/hedge_strategy_comparison.csv` (per strategy × per model) |
| M4 → M5 | `results/forecast_distributional_metrics.csv` (CRPS, pinball) |
| M3 → M5 | `results/diebold_mariano_tests.csv` (pairwise model p-values) |

Standardise these hand-offs on Day 4 morning to save friction all week.

---

## 14. Daily Stand-up Cadence

- **Mon / Wed / Fri @ 15:00** — 15-minute stand-up: blockers, hand-off status, risk-check
- **Sun evening** — written status summary by M5 in `docs/cowork.md` (one line per member)

---

## 15. Member Workload Profile

| Member | Heavy days | Spare days | Notes |
|---|---|---|---|
| M1 | Days 0–3 (data + EDA) | Days 4–9 | Spare days support M3/M4 figures and DCC-GARCH integration |
| M2 | Days 4–7 (simple + frequency) | Days 8, 10, 13+ | Spare days for buffer; report writing later |
| M3 | Days 4–9 (max-perf + DM tests + validation) | Days 11–12 | Spare day for buffer; report writing later |
| M4 | Days 4–10 (creative + backtest + cost analysis) | Days 11–12 | **Heaviest workload — most demanding role** |
| M5 | Days 2–3, 11–14 (drafting + integration + repro) | Days 4–10 (light) | Light early, heavy late; can support modelling debug if needed |

---

## 16. 15-Page Report Allocation

| Section | Pages | Owner |
|---|---|---|
| Executive Summary | 1.0 | M5 |
| Dataset & Business Context (Qantas hedging story) | 1.5 | M5 |
| EDA & Preprocessing (incl. cointegration, vol clustering, frequency-dynamics teaser) | 3.0 | M1 |
| Methodology — Simple + frequency dynamics | 1.5 | M2 |
| Methodology — Max performance (VECM, DCC-GARCH, ARIMA-X) | 3.0 | M3 |
| Methodology — Creative (Kalman dynamic hedge ratio) | 1.5 | M4 |
| Validation & Results (4-strategy backtest, DM tests, distributional metrics) | 2.0 | M4 + M3 |
| Conclusions, Impact & Limitations | 1.5 | M5 |
| **Total** | **15.0** | |

---

## 17. Rubric Coverage Map

| Component | Weight | How we deliver |
|---|---|---|
| Dataset Interestingness | 15% | Heteroskedasticity (univariate + DCC-GARCH), seasonality (NG/TTF/RB), VAR/VECM (cointegrated cracks), exogenous (EIA inventories + AUDUSD), structural breaks (COVID/Ukraine/Iran), **frequency dynamics** (daily vs monthly subsection) |
| Relevant Business Problem | 10% | Concrete Qantas hedging decision with public disclosures cited; 4 hedge strategies; joint commodity + FX axis |
| EDA & Suitability | 15% | STL + ARCH-LM + Johansen + structural-break tests; rolling correlations; tracking-gap diagnostic |
| Simple Explainable Model | 10% | Naive RW + seasonal naive + ETS + low-order ARIMA + **forward-curve benchmark**; per-series winner |
| Maximum Performance Model | 20% | Auto-ARIMA + ARIMA-X with EIA exogenous + SARIMA + VECM (Johansen ranks) + GARCH + **DCC-GARCH** + model combination + **DM tests** |
| Creative Model | 10% | Kalman state-space dynamic hedge ratio — directly produces the business decision |
| Conclusions | 10% | Plain-language cost savings vs naive; tradeoffs across 4 hedge strategies; limitations explicitly named |
| Visual Presentation | 10% | Single notebook, consistent figure style, 8–10 polished EDA figures, compact result tables |

---

## 18. Submission Checklist (Fri 29 May morning)

- [ ] PDF report exactly 15 pages or fewer (no appendix)
- [ ] Single Jupyter notebook executes cleanly via "Run all cells" in clean conda env
- [ ] `prices.csv` in the same folder as the notebook
- [ ] All figures programmatically generated (not pasted images)
- [ ] References list present (Qantas FY25 AR, Adams & Gerner 2012, JTRF 2016, Ederington 1979, Engle DCC paper, Johansen 1991)
- [ ] Admin log (internal) up-to-date
- [ ] Final read-through by 2 members different from the section author
- [ ] Submit before deadline

---

## 19. What v2 Adds Over v1 (Quick Reference)

| Area | v1 | v2 |
|---|---|---|
| Persona | Generic airline/freight | **Qantas Group with public disclosures** |
| Data sources | Yahoo only | Yahoo + EIA + FRED |
| Jet fuel | `HO=F` proxy only | `HO=F` proxy **+ USGC Jet from EIA** |
| FX | DXY context only | **AUDUSD as primary forecast target** |
| Cracks/spreads | Not computed | Jet–Brent, HO–Brent, Brent–WTI |
| Dropped | — | JETS, KRBN, XLE |
| Baselines | RW, seasonal naive | RW, seasonal naive, **forward curve** |
| GARCH | Univariate (PI only) | Univariate **+ DCC-GARCH for dynamic hedge ratio** |
| VECM | Mentioned | **Johansen rank tests explicit** |
| Statistical testing | — | **Diebold-Mariano** |
| Distributional metrics | PI coverage | PI coverage **+ CRPS + pinball loss** |
| Frequency dynamics | — | **Subsection — bonus rubric points** |
| Hedge strategies | 4 (no/50%/100%/model) | 4 (kept) |
| Cost metrics | Mean, std, P95, bps | Mean, std, P95, bps **+ Sharpe-like** |
| Operations | Kept as-is from v1 | Kept as-is from v1 |

---

*End of Option A v2 timeline.*