"""Tracking-gap diagnostic for Option A ETF hedging instruments vs underlying futures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
QUALITY_DIR = PROJECT_ROOT / "data" / "quality"
QUALITY_DIR.mkdir(parents=True, exist_ok=True)

START = "2016-01-01"
END = "2026-05-15"
TRADING_DAYS = 252

PAIRS = [
    {"proxy_name": "USO", "proxy_symbol": "USO", "ref_symbol": "CL=F"},
    {"proxy_name": "UNG", "proxy_symbol": "UNG", "ref_symbol": "NG=F"},
    {"proxy_name": "UGA", "proxy_symbol": "UGA", "ref_symbol": "RB=F"},
]


def _adj_close(symbol: str) -> pd.Series:
    df = yf.download(
        symbol, start=START, end=END,
        auto_adjust=False, progress=False, group_by="column",
    )
    if df is None or df.empty:
        return pd.Series(dtype=float, name=symbol)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    s = df[col].copy()
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    s.name = symbol
    return s


def _metrics(proxy_ret: pd.Series, ref_ret: pd.Series) -> dict:
    joined = pd.concat([proxy_ret, ref_ret], axis=1, join="inner").dropna()
    if joined.shape[0] < 30:
        return {
            "n_obs": int(joined.shape[0]),
            "correlation": np.nan, "r_squared": np.nan, "beta": np.nan,
            "tracking_error_ann": np.nan, "mean_ann_diff": np.nan,
            "proxy_ann_return": np.nan, "proxy_ann_vol": np.nan,
            "ref_ann_return": np.nan, "ref_ann_vol": np.nan,
        }
    p = joined.iloc[:, 0].to_numpy()
    r = joined.iloc[:, 1].to_numpy()
    corr = float(np.corrcoef(p, r)[0, 1])
    var_r = float(np.var(r, ddof=1))
    beta = float(np.cov(p, r, ddof=1)[0, 1] / var_r) if var_r > 0 else np.nan
    diff = p - r
    return {
        "n_obs": int(joined.shape[0]),
        "correlation": corr,
        "r_squared": corr ** 2,
        "beta": beta,
        "tracking_error_ann": float(np.std(diff, ddof=1) * np.sqrt(TRADING_DAYS)),
        "mean_ann_diff": float(np.mean(diff) * TRADING_DAYS),
        "proxy_ann_return": float(np.mean(p) * TRADING_DAYS),
        "proxy_ann_vol": float(np.std(p, ddof=1) * np.sqrt(TRADING_DAYS)),
        "ref_ann_return": float(np.mean(r) * TRADING_DAYS),
        "ref_ann_vol": float(np.std(r, ddof=1) * np.sqrt(TRADING_DAYS)),
    }


def _scatter_and_cumret(proxy_ret: pd.Series, ref_ret: pd.Series,
                        proxy_label: str, ref_label: str, out_path: Path) -> None:
    joined = pd.concat([proxy_ret, ref_ret], axis=1, join="inner").dropna()
    if joined.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    axes[0].scatter(joined.iloc[:, 1], joined.iloc[:, 0], s=6, alpha=0.4)
    lo = float(min(joined.min()))
    hi = float(max(joined.max()))
    axes[0].plot([lo, hi], [lo, hi], color="black", lw=0.8, ls="--")
    axes[0].set_xlabel(f"{ref_label} daily log return")
    axes[0].set_ylabel(f"{proxy_label} daily log return")
    axes[0].set_title(f"Return scatter — {proxy_label} vs {ref_label}")
    axes[0].grid(alpha=0.3)

    cum = joined.cumsum().apply(np.exp)
    axes[1].plot(cum.index, cum.iloc[:, 0], label=proxy_label, lw=1.0)
    axes[1].plot(cum.index, cum.iloc[:, 1], label=ref_label, lw=1.0)
    axes[1].set_ylabel("Cumulative return (rebased = 1.0)")
    axes[1].set_title(f"Cumulative return — {proxy_label} vs {ref_label}")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    prices_path = PROCESSED_DIR / "prices.parquet"
    if not prices_path.exists():
        print(f"[ERROR] {prices_path} not found. Run the Option A data-acquisition notebook first.",
              file=sys.stderr)
        return 1

    prices = pd.read_parquet(prices_path)
    prices.index = pd.to_datetime(prices.index)

    rows = []
    for pair in PAIRS:
        pname = pair["proxy_name"]
        psym = pair["proxy_symbol"]
        rsym = pair["ref_symbol"]
        print(f"[GAP] {pname} ({psym}) vs reference {rsym}")

        if pname not in prices.columns:
            print(f"  [SKIP] {pname} missing from prices.parquet")
            continue
        proxy_px = prices[pname].dropna()
        proxy_ret = np.log(proxy_px).diff().dropna()

        ref_px = _adj_close(rsym).dropna()
        if ref_px.empty:
            print(f"  [SKIP] reference {rsym} returned no data from Yahoo")
            continue
        ref_ret = np.log(ref_px.astype(float)).diff().dropna()
        ref_ret.name = rsym

        m = _metrics(proxy_ret.rename(pname), ref_ret)
        row = {"proxy": pname, "proxy_symbol": psym, "reference_symbol": rsym, **m}
        rows.append(row)

        out_png = QUALITY_DIR / f"scatter_{pname}_vs_{rsym}.png"
        _scatter_and_cumret(proxy_ret, ref_ret, pname, rsym, out_png)
        print(f"  [OK] n={m['n_obs']}, corr={m['correlation']:.3f}, "
              f"TE_ann={m['tracking_error_ann']:.4f}")

    if not rows:
        print("[ERROR] No tracking-gap pairs produced — aborting.", file=sys.stderr)
        return 2

    report = pd.DataFrame(rows)
    report_path = QUALITY_DIR / "tracking_gap_report.csv"
    report.to_csv(report_path, index=False)
    print(f"[WROTE] {report_path} ({len(report)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
