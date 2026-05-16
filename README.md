# QBUS3850 Group Assignment

Time-series forecasting for Qantas Group's joint fuel + AUDUSD hedging strategy.

## Persona

Qantas Group (ASX: QAN). FY25 disclosures show ~77–81% of forward fuel hedged via Brent + Singapore Jet swaps + option structures. Exposure has two axes: USD jet fuel price × AUDUSD. Both modelled.

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd Time-Series-Forecasting

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

## How to run

```bash
jupyter notebook notebooks/01_data_acquisition.ipynb
```

Run all cells. Takes 1-2 minutes. Pulls market data from Yahoo Finance (via `curl_cffi` to bypass Yahoo's yfinance block), reads pre-downloaded EIA XLS files, writes:

- `data/raw/` — one CSV per Yahoo ticker, plus 4 EIA XLS files
- `data/processed/` — three clean parquet files (the hand-off contract — see below)
- `data/quality/` — tracking-gap diagnostics
- `figures/01_acquisition/` — three overview figures

## Hand-off contract for downstream notebooks

Read from `data/processed/`. Never from `data/raw/`. Three files, all indexed by business day with 5-day forward-fill:

| File | Columns | Used by |
|---|---|---|
| `prices.parquet` | **15 series** — 9 tradable (WTI, Brent, HO, RBOB, HH_NG, TTF, USO, UNG, UGA) + USGCJet + 3 cracks/spreads (BrentWTI, JetBrent, HOBrent) + AUDUSD + DXY | M2 EDA, M3 forecast targets |
| `returns.parquet` | Log returns of `prices.parquet` columns | M3 modelling, M4 backtesting |
| `exogenous_features.parquet` | **7 features** — RF, TNX, OilVol, VIX, CrudeStocks, DistStocks, RefineryUtil | M3 exogenous regressors |

## Folder structure
```text
Time-Series-Forecasting/
├── data/
│   ├── raw/                # Yahoo CSVs + EIA XLS files
│   ├── processed/          # Three parquet files (read these downstream)
│   └── quality/            # Tracking-gap diagnostics
├── docs/                   # Project notes
├── figures/
│   └── 01_acquisition/     # Generated figures
├── notebooks/
│   └── 01_data_acquisition.ipynb
├── scripts/
│   └── data_quality.py     # Tracking-gap subprocess
├── requirements.txt
├── pipeline_timeline_v2.md # Master project plan
└── README.md
```

## Refreshing data

**Yahoo** auto-refreshes every 24h (cached in `data/raw/_acquisition_log.csv`). To force a re-pull, delete that log file and re-run the notebook.

**EIA** is a manual download. To refresh, re-download these 4 XLS files into `data/raw/` (no API key needed):

- USGC Jet (daily): https://www.eia.gov/dnav/pet/hist_xls/eer_epjk_pf4_rgc_dpgd.xls
- Crude stocks (weekly): https://www.eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls
- Distillate stocks (weekly): https://www.eia.gov/dnav/pet/hist_xls/WDISTUS1w.xls
- Refinery utilisation (weekly): https://www.eia.gov/dnav/pet/hist_xls/WPULEUS3w.xls

EIA updates weekly (Wednesday afternoons US time).

## Yahoo rate-limit note

Yahoo started blocking `yfinance` requests in 2025. The notebook bypasses this by using `curl_cffi` with browser impersonation. If a teammate hits empty downloads, check that `curl_cffi` is installed and that the `YF_SESSION = curl_requests.Session(impersonate="chrome")` line in cell 1 ran without error.
