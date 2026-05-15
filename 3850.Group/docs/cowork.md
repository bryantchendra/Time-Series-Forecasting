# Cowork ↔ Claude Code log

## Response 001 — Data acquisition notebook

**Prompt:** prompts/cc/prompt_001_data_acquisition.md
**Files created:**
- notebooks/01_data_acquisition.ipynb
- requirements.txt
- scripts/data_quality.py (was missing from the repo at task start — created from OptionC.md Section 7.4 spec)
- data/raw/*.csv (16 files including stub for `Bench`)
- data/raw/_acquisition_log.csv (per-ticker download log)
- data/processed/{prices.parquet, prices.csv, summary.csv}
- data/quality/{tracking_gap_report.csv, scatter_Carbon_vs_KEUA.png, scatter_U_Phys_vs_URA.png, scatter_U_Min_vs_URNM.png}
- figures/01_acquisition/{01_normalised_prices.png, 02_log_returns_small_multiples.png, 03_missing_heatmap.png}

**Outcome:** 15 of 16 tickers downloaded with real data; all 6 acceptance checks pass and the notebook prints "DATA ACQUISITION COMPLETE". `prices.parquet` is 2610 rows × 16 columns covering 2016-01-01 → 2026-01-01 on the business-day calendar.

**Notes / caveats to flag for Cowork:**
- `Bench` (`^SPGSEN` — S&P GSCI Energy TR) returned an empty dataframe from Yahoo Finance on the batched pull *and* on the individual retry. A stub CSV (header only) is written so the file count is stable; the column in `prices.parquet` is entirely NaN. The acquisition log records this as `success=False`. **Action item:** before modelling, decide whether to substitute an alternative benchmark (e.g. `XLE`, an equal-weight basket of the 12 series, or `GSG` ETF) or proceed without a single-instrument benchmark.
- Several series have shorter natural histories that are reported, not patched: TTF (2017-10-23), Carbon/KRBN (2020-07-31), U_Phys/SRUUF (2021-07-22), Coal/COAL (2024-01-24).
- The `data_quality.py` tracking-gap diagnostic produced 4 rows. Coal vs KOL returned `n_obs=0` because the proxy COAL itself only goes back to 2024-01-24, leaving zero overlap with the available KOL history under Yahoo's current response — this row is preserved in the report so the limitation is visible, but downstream EDA should treat the Coal tracking gap as untestable on the current Yahoo data and either pick an alternative reference or drop the row.
- Yahoo rate-limited mid-task during reruns; the notebook's cell-4 now retries empty tickers individually and the cell-14 step skips re-invoking `data_quality.py` if its CSV is <24h old, which keeps reruns from burning the quota.

## Response 002 — Option A parallel notebook

**Prompt:** prompts/cc/prompt_002_option_a_notebook.md
**Files renamed:**
- notebooks/01_data_acquisition.ipynb → notebooks/01c_data_acquisition.ipynb (title also updated to `# 01c — Data Acquisition (QBUS3850 Option C)`)

**Files created:**
- notebooks/01a_data_acquisition.ipynb
- scripts/data_quality_a.py
- data/a/raw/*.csv (16 files) + data/a/raw/_acquisition_log.txt
- data/a/processed/{prices.parquet, prices.csv, summary.csv}
- data/a/quality/{tracking_gap_report.csv, scatter_USO_vs_CL=F.png, scatter_UNG_vs_NG=F.png, scatter_UGA_vs_RB=F.png, scatter_Carbon_vs_KEUA.png}
- figures/01a_acquisition/{01_normalised_prices.png, 02_log_returns_small_multiples.png, 03_missing_heatmap.png}

**Outcome:** All **16 of 16** Option A tickers downloaded with real data (the Option A basket has no analogue of Option C's missing `^SPGSEN`). All 6 acceptance checks pass and the notebook prints "DATA ACQUISITION (OPTION A) COMPLETE". `data/a/processed/prices.parquet` is 2610 rows × 16 columns covering 2016-01-01 → 2026-01-01.

**Notes:**
- Tracking-gap report rows (all 4 produced cleanly): USO↔CL=F corr 0.881, UNG↔NG=F corr 0.858, UGA↔RB=F corr 0.876, KRBN↔KEUA corr 0.689. Annualised tracking errors: USO 21%, UGA 22%, UNG 33%, KRBN 42% — these are the "cost of operational simplicity" numbers OptionA.md §5 calls out for the EDA table.
- Shorter natural histories (reported, not patched): TTF starts 2017-10-23; KRBN/Carbon starts 2020-07-31. All other Option A tickers cover full 2016-01-04 → 2025-12-31.
- Note the UNG mean annual return differential is −0.289 (proxy ann.return −24.3% vs NG futures +4.6%), consistent with the well-known UNG contango drag flagged in OptionA.md §14.
- Option C outputs left untouched. `scripts/data_quality.py` is unchanged.
