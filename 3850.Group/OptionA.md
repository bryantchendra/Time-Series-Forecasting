# Option A — Airline / Freight Carrier (Hedger)

**Status:** Detailed plan for team review (parallel to OptionC.md)
**Date:** 2026-05-12
**Constraints:** 5 team members, 2 weeks, 15-page PDF limit
**Persona contrast with C:** A *consumes* energy and hedges cost exposure. C *trades* energy for P&L. Different forecast target, different business metric, same Yahoo-only data discipline.

---

## 1. Business Persona

A regional **airline or freight carrier** that:
- **Decides:** how much fuel exposure to hedge, what tenor, which instrument
- **Cares about:** budget certainty, downside protection on cost spikes, P95 worst-month overrun
- **Forecast type needed:** point forecast (budget submission) + prediction intervals (hedge sizing) + scenario simulations (board-level risk reporting)
- **Why this persona suits the dataset:** energy is an input cost; forecast errors directly hit P&L from the consumption side; hedge decision is forecast-driven

---

## 2. Forecast Targets

- **Price levels** (not returns) — hedger forecasts cost in $/unit
- **Prediction interval coverage** — for hedge sizing (e.g. larger hedge when 80% interval is wide)
- **Optional:** scenario paths from simulated forecasts for stress testing

---

## 3. Dataset (12 series — all Yahoo Finance)

### 3.1 Proposed instruments

| # | Instrument | Yahoo ticker | Type | Role for the airline |
|---|---|---|---|---|
| 1 | WTI Crude | `CL=F` | Futures (direct) | Upstream input; crack-spread context |
| 2 | Brent Crude | `BZ=F` | Futures (direct) | International route fuel reference |
| 3 | RBOB Gasoline | `RB=F` | Futures (direct) | Ground fleet, employee travel |
| 4 | Heating Oil / ULSD | `HO=F` | Futures (direct) | **Jet fuel proxy** + diesel for ground ops |
| 5 | Henry Hub Natural Gas | `NG=F` | Futures (direct) | Hangar / facility heating |
| 6 | TTF Dutch Gas | `TTF=F` | Futures (direct) | European facility heating |
| 7 | USO (US Oil Fund) | `USO` | ETF | Alternative crude hedge instrument |
| 8 | UNG (US Natural Gas Fund) | `UNG` | ETF | Alternative gas hedge instrument |
| 9 | UGA (US Gasoline Fund) | `UGA` | ETF | Alternative gasoline hedge instrument |
| 10 | XLE Energy Sector | `XLE` | ETF | Cross-hedge via energy equity exposure |
| 11 | JETS Airline ETF | `JETS` | ETF | **Reverse-side check** — output prices for the industry; natural-hedge anchor |
| 12 | KRBN Carbon | `KRBN` | ETF | EU ETS Aviation cost (EU flights in scope) |

### 3.2 Auxiliary data

| Purpose | Yahoo ticker |
|---|---|
| Discount rate (PV of forward / option) | `^IRX` |
| USD index (FX risk for non-US carriers) | `DX-Y.NYB` |
| Oil-vol risk indicator (hedge sizing) | `^OVX` |
| Equity risk indicator | `^VIX` |

### 3.3 Frequency & history

- **Daily prices, full OHLCV**
- **10 years:** 2016-01-01 to 2026-01-01 (TTF starts ~2018, UGA starts ~2008 — keep native histories)

---

## 4. Where to Get the Data

Single source: **Yahoo Finance via `yfinance`** (same discipline as Option C).

Output directories (parallel to but separate from Option C's):
- `data/a/raw/` — one CSV per ticker (full OHLCV)
- `data/a/processed/prices.parquet` and `prices.csv` — wide aligned
- `data/a/processed/summary.csv` — per-ticker metadata
- `data/a/quality/tracking_gap_report.csv` — ETF-vs-futures gap analysis
- `figures/01a_acquisition/` — overview figures

---

## 5. ETF-vs-Futures Tracking Gap (A's version of the gap check)

For Option A, the **ETFs in the basket ARE the actual hedging instruments** an airline could use. The relevant question is: do these ETFs track the underlying futures cleanly enough to be a viable hedge?

| Hedging ETF | Underlying futures | What the gap check shows |
|---|---|---|
| `USO` | `CL=F` (WTI) | How closely the US Oil Fund tracks WTI front-month |
| `UNG` | `NG=F` (Henry Hub) | UNG vs gas futures — known to suffer from contango drag |
| `UGA` | `RB=F` (RBOB) | UGA vs gasoline futures |
| `KRBN` | `KEUA` (pure EUA, until liquidation Mar 2026) | Mixed-carbon ETF vs pure EUA |

`scripts/data_quality_a.py` runs the same metric pack as Option C (correlation, R², tracking error, beta) and saves a parallel report.

**Why this is interesting for the rubric:** in Option A the gap check has direct business meaning — the airline can choose whether to hedge with futures (operationally complex) or ETFs (simple, retail-style). The measured tracking error is the cost of operational simplicity.

---

## 6. Three Required Models

### 6.1 Simple (10%)
- ETS / low-order ARIMA on **price levels** (hedger forecasts costs, not returns)
- Seasonal ARIMA for HH gas, TTF, RBOB (winter heating, summer driving)
- Naive 1-month-forward as a do-nothing hedge benchmark
- Selection: lowest MAE in $/unit on rolling holdout

### 6.2 Max performance (20%)
- Auto-ARIMA per series
- **ARIMA-X with USD as exogenous** (refined products priced in USD)
- SARIMA where seasonality is significant
- VECM on cointegrated pairs (Brent–WTI, HO–RBOB)
- **GARCH for prediction interval calibration** — used to size hedges, not P&L positions
- Model combination weighted by inverse MAE

### 6.3 Creative (10%)
**Recommended:** Dynamic hedge-ratio via **state-space Kalman filter**

Why:
- Course material covers state-space and time-varying parameters
- The hedge ratio IS the decision the airline makes — direct business application
- Adapts as the relationship between jet-fuel proxy (`HO=F`) and hedge instrument (`USO`, `CL=F`) drifts

**Alternatives** (pick one):
- **Crack-spread Ornstein-Uhlenbeck** — Brent-WTI and HO-CL spreads as mean-reverting
- **Cross-asset regression on `JETS`** — natural-hedge anchor via equity output price
- **LightGBM with seasonal + macro features** — non-linear price level forecaster

---

## 7. Custom Business Metric

Compare four hedge strategies on realised prices:

1. **No hedge** — pay spot every month
2. **Naive 100% 1-month forward** — textbook full hedge
3. **Naive 50% 1-month forward** — partial hedge
4. **Model-driven dynamic hedge** — hedge ratio sized by forecast prediction interval

**Report per strategy:**
- Average annual fuel cost ($)
- **Standard deviation of monthly fuel cost** (budget certainty)
- **P95 worst-month overrun** (board-level risk)
- Cost savings vs no-hedge baseline (in basis points of revenue, with an assumed revenue level)

This is a richer business-metric story than Option C's Sharpe — direct managerial decision support.

---

## 8. EDA — A-specific stylised facts

In addition to the C-style checks:
- **STL decomposition** on HH gas, TTF, RBOB — strong yearly cycles
- **Cointegration** between fuel inputs and `JETS` output prices (natural hedge?)
- **Cross-correlation lag analysis** — does WTI lead HO by N days?
- **Term-structure caveat** — Yahoo gives front-month only; full curve would be better (acknowledged in Limitations)

---

## 9. Validation

- **Rolling-origin / expanding window**
- **Forecast horizons:**
  - Short: 1 week (budget refresh)
  - Medium: 1 month (hedge refresh)
  - Long: 1 quarter (board fuel budget)
- **Per-horizon metrics:** MAE, MAPE, **80% / 95% prediction-interval coverage**, total annual cost of the resulting hedge strategy

---

## 10. 15-Page Allocation

| Section | Pages |
|---|---|
| Executive Summary | 1.0 |
| Dataset & Business Context | 1.5 |
| EDA | 3.0 |
| Methodology — Simple, Max, Creative | 6.0 |
| Validation & Results (4 hedge strategies) | 2.0 |
| Conclusions, Impact, Limitations | 1.5 |
| **Total** | **15.0** |

---

## 11. 5-Person Workstream Split

| Member | Primary role |
|---|---|
| 1 | Data acquisition (`yfinance`), tracking-gap diagnostic, EDA scaffolding |
| 2 | Simple model + benchmarks (no-hedge / naive forwards) |
| 3 | Max performance (ARIMA-X / SARIMA / VECM / GARCH for PI) |
| 4 | Creative (Kalman hedge ratio) + backtest engine for 4 hedge strategies |
| 5 | Report writing, figures, notebook integration, reproducibility check |

---

## 12. Two-Week Timeline

| Day | Milestone |
|---|---|
| 1–2 | Data pulled, EDA scaffolded, quality issues catalogued |
| 3–5 | Three models on 2–3 pilot series; PI calibration framework live |
| 6–8 | Roll out to full basket; **4-hedge-strategy backtest engine** live (Day 6 dedicated to Member 4) |
| 9–11 | Rolling-origin validation; cost-comparison tables generated |
| 12–13 | Report draft + figures |
| 14 | Reproducibility check |

---

## 13. Rubric Coverage

| Component | Weight | Option A delivery |
|---|---|---|
| Dataset Interestingness | 15% | Heteroskedasticity (GARCH for PI), seasonality (HH, TTF, RBOB), VAR/VECM (crack spreads), exogenous (USD, OVX) |
| Relevant Business Problem | 10% | Concrete corporate decision; 4 hedge strategies; multi-stakeholder metrics |
| EDA & Suitability | 15% | STL on seasonals + cointegration + cross-correlation; structural breaks |
| Simple Explainable Model | 10% | Naive forward + ETS/ARIMA on levels; interpretable coefficients |
| Max Performance Model | 20% | Auto-ARIMA + ARIMA-X + SARIMA + VECM + GARCH-for-PI |
| Creative Model | 10% | Kalman dynamic hedge ratio (or OU / cross-asset / LightGBM alt) |
| Conclusions | 10% | Plain-language cost savings; tradeoffs across hedge strategies |
| Visual Presentation | 10% | Single notebook, consistent style |

---

## 14. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Hedge-strategy backtest engine is more complex than C's | Build it incrementally; Day 6 dedicated; reuse on all 4 strategies |
| `HO=F` ≠ jet fuel — proxy gap is structural | Acknowledge in EDA; quantify HO-vs-jet cracker spread literature; note as limitation |
| Yahoo front-month only — no full term structure | Acknowledge in Limitations; production system would use ICE/CME curves |
| ETF tracking error vs futures matters for hedge effectiveness | `scripts/data_quality_a.py` measures it; included as EDA table |
| GARCH PI calibration tricky | Validate empirical coverage on holdout; fall back to bootstrap intervals |
| 15-page squeeze with 4-strategy comparison | Use compact tables; one figure compares all 4 strategies |

---

## 15. Open Decisions (team to lock in)

- [ ] Confirm 12-series basket exactly as listed in Section 3.1
- [ ] Confirm history window (2016–2026 with native inceptions, or uniform 2018–2026)
- [ ] Confirm forecast horizons (1w / 1m / 1q proposed)
- [ ] Confirm creative model choice (Kalman vs OU vs cross-asset vs LightGBM)
- [ ] Confirm assumed revenue level for cost-as-bps-of-revenue metric
- [ ] Confirm whether to include `KRBN` (only relevant if EU operations matter)

---

## 16. Comparison Snapshot — A vs C

| Dimension | Option A (Airline hedger) | Option C (CTA trader) |
|---|---|---|
| Forecast target | Price levels | Returns + volatility |
| Business metric | Cost saved + budget variance + P95 overrun | Sharpe + drawdown + hit rate |
| GARCH role | Prediction interval calibration | Position sizing |
| Creative model fit | Kalman dynamic hedge ratio | Regime-switching AR-GARCH |
| Seasonality story | Stronger | Weaker |
| Narrative strength | Stronger (concrete decision) | Solid (long/short signal) |
| 2-week risk | Higher (4-strategy engine) | Lower |

---

*End of Option A plan.*
