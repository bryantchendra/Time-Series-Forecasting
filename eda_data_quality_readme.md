# EDA tools and data-quality files

This section explains the three EDA/data-quality items added during Day 2-3 prep. It is written so the team can drop it into the main README.

---

## 1. `utils/eda.py` — helper functions for EDA tests

`utils/eda.py` contains reusable helper functions for common time-series checks.

The main point is consistency: every test returns results in the same dictionary format, so we can easily combine the outputs into one table.

Each function returns these fields:

```text
series, test_name, statistic, p_value, critical_values, null, conclusion
```

### Functions

| function | purpose |
|---|---|
| `adf_test(series, regression="c", autolag="AIC", alpha=0.05)` | Tests whether a series has a unit root. In simple terms: checks whether the series is likely non-stationary. |
| `kpss_test(series, regression="c", nlags="auto", alpha=0.05)` | Another stationarity test, but with the opposite null hypothesis to ADF. Useful as a second check. |
| `arch_lm_test(series, nlags=12, alpha=0.05)` | Checks whether volatility clusters over time. This matters for GARCH-style models. |
| `johansen_test(data, det_order=0, k_ar_diff=1, test="trace", alpha=0.05)` | Checks whether multiple related series move together in the long run. Useful for VECM. |
| `stl_decompose(series, period=None, seasonal=7, robust=False)` | Splits a time series into trend, seasonal, and residual components. |

### How to use

```python
from utils.eda import adf_test, kpss_test, arch_lm_test

results = []

for name, s in series_dict.items():
    results.append(adf_test(s, name=name))
    results.append(kpss_test(s, name=name))
    results.append(arch_lm_test(s, name=name))

results_df = pd.DataFrame(results)
```

### Where this helps

- **EDA report:** run the same set of checks across all 15 series and store the results in one table.
- **Day 4 ARIMA model:** use `adf_test` and `kpss_test` to decide whether the series should be differenced.
- **VECM model:** use `johansen_test` on related price series such as Brent + WTI, or Brent + heating oil + jet fuel.

### Things to watch out for

- **KPSS p-values are capped.** They are clipped between `0.01` and `0.10`, so a boundary value does not give the full story. Check the test statistic against the critical values as well.
- **Use `arch_lm_test` on returns or residuals, not price levels.** It is meant to test volatility clustering, so price levels are usually the wrong input.
- **`johansen_test` does not return a p-value.** Statsmodels does not provide one. Compare the test statistic against the critical values instead.
- **`stl_decompose` usually needs `period=`.** Unless the series has a clear datetime frequency, pass the period manually.
- **ADF/KPSS decision guide for ARIMA differencing:**
  - ADF rejects and KPSS does not reject: likely stationary, use `d=0`.
  - ADF does not reject and KPSS rejects: likely has a unit root, use `d=1`.
  - Both reject: possible structural break or changing variance; check volatility and break events.

---

## 2. `data/quality/structural_breaks.csv` — event log

This file records 9 major market/event shocks from February 2020 to May 2026.

It is the shared event log for:

- plot shading,
- rolling-origin retrain cut-offs,
- event dummy variables,
- report context.

Columns:

```text
event, start_date, end_date, notes, citation
```

The file is also linked to `utils/plot.py`, especially:

```python
overlay_breaks
SHORT_BREAK_LABELS
```

These keep event shading consistent across all time-series figures.

### How to use

```python
import pandas as pd
from utils.plot import overlay_breaks, SHORT_BREAK_LABELS

breaks = pd.read_csv(
    "data/quality/structural_breaks.csv",
    parse_dates=["start_date", "end_date"]
)

fig, ax = plt.subplots(figsize=(12, 5))
prices["Brent"].plot(ax=ax)

overlay_breaks(
    ax,
    breaks,
    short_labels=SHORT_BREAK_LABELS
)
```

For a zoomed plot, pass `date_range=`. This stops labels outside the plot area from messing up the layout.

```python
brent_zoom = brent.loc["2024":]

brent_zoom.plot(ax=ax)

overlay_breaks(
    ax,
    breaks,
    short_labels=SHORT_BREAK_LABELS,
    date_range=(brent_zoom.index.min(), brent_zoom.index.max())
)
```

### Where this helps

- **Plot overlays:** add shaded event bands to time-series charts.
- **Rolling-origin cut-offs:** use `breaks.start_date.tolist()` as natural retraining points.
- **Dummy variables:** create indicator columns for whether a date falls inside a specific event window.
- **Report writing:** use the dated and cited events to explain why certain price movements happened.

### Things to watch out for

- **The 2026 Iran War row is ongoing.** Its `end_date` is the latest data snapshot, not the confirmed end of the event. Update this when the data is refreshed.
- **COVID onset and the April 2020 oil-price collapse are separate rows.** They are related but not the same shock. Keeping them separate gives us more modelling flexibility.
- **Dates show acute shock windows, not full long-run regimes.** For example, Ukraine-related price effects continued after March 2022, but the event window only captures the sharp initial shock. Extend the window in modelling code if needed.
- **Citation URLs are in the `citation` column.** Before using exact wording in the final report, spot-check the sources.

---

## 3. `data/quality/outlier_flags.csv` — return outlier flags

This file flags dates where individual series had unusually large moves.

It contains around 2,400 rows. Each row is one flagged observation:

```text
series, date, return, z_score, flag_reason
```

The method is:

- compute **log returns** when a series is almost always positive,
- fall back to **first differences** if a series has more than 1% non-positive values,
- flag observations using IQR fences,
- add an event suffix if the flagged date falls inside a structural break window.

In the current data, every series stays above the 1% non-positive threshold, so all flags use log returns. The first-differences path is only there as a safety net for future data updates (for example if a spread series starts going negative more often).

Both moderate and extreme flags are included:

- `1.5 × IQR` means outlier,
- `3.0 × IQR` means extreme outlier.

### How to use

```python
flags = pd.read_csv(
    "data/quality/outlier_flags.csv",
    parse_dates=["date"]
)

# Conservative modelling subset
extreme = flags[flags.flag_reason.str.startswith("iqr_extreme")]

# Extreme dates for one series
brent_outliers = extreme.query("series == 'Brent'").date.tolist()
```

### `flag_reason` values

| reason | meaning |
|---|---|
| `iqr_outlier_logret` | More than 1.5 × IQR away, based on log returns. |
| `iqr_extreme_logret` | More than 3.0 × IQR away, based on log returns. This is the stricter flag. |
| `iqr_outlier_diff` | More than 1.5 × IQR away, based on first differences. Only fires when a series has more than 1% non-positive values. Does not appear in the current CSV. |
| `iqr_extreme_diff` | More than 3.0 × IQR away, based on first differences. Same condition as above. Does not appear in the current CSV. |
| `non_positive_price` | Return could not be calculated because the price was zero or negative. Example: WTI in April 2020. |
| `...; event: <name>` | Added when the flagged date falls inside a structural break window. |

### Where this helps

- **GARCH models:** add dummy variables for `iqr_extreme_*` dates so one-day shocks do not dominate the volatility model.
- **Winsorisation:** use the flags to identify which returns would be capped.
- **Data-quality audit:** confirm that known extreme events, such as WTI April 2020, are captured.
- **Report writing:** use the file to support the data-quality section.

### Things to watch out for

- **Spread series have more flags than price series.** Examples include `JetBrent_crack` and `BrentWTI_spread`. This happens because spreads often have a tighter normal range, so jumps look more extreme.
- **For modelling, prefer `iqr_extreme`.** The 1.5 × IQR rule can flag a lot of financial-return observations. The 3.0 × IQR rule is more conservative.
- **`BrentWTI_spread` has some negative values.** Brent being below WTI is uncommon but possible. This matters before fitting a Brent-WTI VECM.
- **The IQR is calculated on the full sample.** If volatility changes across regimes, a full-sample IQR can under-flag high-volatility periods and over-flag low-volatility periods.
- **A 5-7% outlier rate using 1.5 × IQR is not automatically a bug.** Financial returns are heavy-tailed, so this is plausible. Use `iqr_extreme` for the stricter subset.

### How to regenerate

Re-run the bottom cell of:

```text
notebooks/01_data_acquisition.ipynb
```

after updating either of these files:

```text
data/processed/prices.parquet
data/quality/structural_breaks.csv
```
