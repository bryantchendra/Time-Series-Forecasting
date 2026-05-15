# QBUS3850 Group Assignment

Time-series forecasting for Qantas Group's joint fuel + AUDUSD hedging strategy.

## What this project does

Qantas is exposed to two prices: USD jet fuel and AUDUSD. We forecast both, then test hedging strategies that combine futures and FX forwards.

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd Time-Series-Forecasting

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

## How to run

Open the data acquisition notebook first:

```bash
jupyter notebook notebooks/01_data_acquisition.ipynb
```

Run all cells. This pulls market data from Yahoo Finance and saves:
- `data/raw/` — one CSV per ticker
- `data/processed/` — clean parquet files for modelling
- `data/quality/` — diagnostic reports
- `figures/01_acquisition/` — overview figures

## Folder structure
```text
Time-Series-Forecasting/
├── data/
│   ├── raw/             # Raw downloads from Yahoo
│   ├── processed/       # Clean parquet files (read these downstream)
│   └── quality/         # Tracking-gap diagnostics
├── docs/                # Project notes
├── figures/             # Generated charts
├── notebooks/           # Jupyter notebooks
└── scripts/             # Python scripts called by notebooks
```
