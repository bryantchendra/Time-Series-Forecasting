"""
utils/eda.py
============

Uniform wrappers around statsmodels stationarity, heteroskedasticity,
cointegration, and decomposition routines.

Every function returns a dict with the same top-level keys:

    series           - series name (or list of names for Johansen)
    test_name        - short label, e.g. "ADF", "KPSS", "ARCH-LM(12)"
    statistic        - test statistic (float, or dict for multi-rank Johansen
                       and STL strengths)
    p_value          - float in [0, 1], or None where not defined
                       (Johansen, STL)
    critical_values  - dict of {level: cv}, nested for Johansen, None for STL
    null             - plain-English statement of H0
    conclusion       - plain-English reading of the result

`stl_decompose` additionally returns a `components` key with the trend,
seasonal, and residual DataFrame. Drop that column before writing the
test-results CSV if you want to stay on the seven-key schema.

Why a wrapper module: the EDA notebook calls these 50+ times across
15 series, and M2 reuses the same ADF/KPSS calls for ARIMA differencing
order selection on Day 4. Write them once, get one schema, cite once.
"""

from __future__ import annotations

import warnings
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import chi2
from statsmodels.stats.diagnostic import het_arch
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.vector_ar.vecm import coint_johansen


__all__ = [
    "adf_test",
    "kpss_test",
    "arch_lm_test",
    "johansen_test",
    "stl_decompose",
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _as_series(x, name: str | None = None) -> pd.Series:
    """Coerce array-like to a pd.Series and drop NaN rows."""
    s = pd.Series(x).dropna()
    if name is not None:
        s.name = name
    return s


def _resolve_name(name: str | None, s: pd.Series) -> str:
    if name is not None:
        return name
    return str(s.name) if s.name is not None else "series"


def _chi2_cvs(df: int) -> dict[str, float]:
    """Upper-tail chi-squared critical values for an ARCH-LM-style test."""
    return {
        "1%":  float(chi2.ppf(0.99, df)),
        "5%":  float(chi2.ppf(0.95, df)),
        "10%": float(chi2.ppf(0.90, df)),
    }


# ---------------------------------------------------------------------------
# unit-root / stationarity
# ---------------------------------------------------------------------------

def adf_test(
    series,
    name: str | None = None,
    regression: str = "c",
    autolag: str | None = "AIC",
    alpha: float = 0.05,
) -> dict:
    """
    Augmented Dickey-Fuller test for a unit root.

    H0: the series has a unit root (non-stationary).
    Reject H0 (small p-value) => evidence of stationarity.

    Parameters
    ----------
    regression : {'c', 'ct', 'ctt', 'n'}
        Trend specification, passed to ``statsmodels.tsa.stattools.adfuller``.
    autolag : {'AIC', 'BIC', 't-stat', None}
        Lag-length selection rule.
    alpha : float
        Significance level used to phrase the ``conclusion`` field.
    """
    s = _as_series(series, name)
    stat, pvalue, _usedlag, _nobs, crit, _icbest = adfuller(
        s, regression=regression, autolag=autolag
    )
    reject = pvalue < alpha
    return {
        "series": _resolve_name(name, s),
        "test_name": "ADF",
        "statistic": float(stat),
        "p_value": float(pvalue),
        "critical_values": {k: float(v) for k, v in crit.items()},
        "null": "unit root (non-stationary)",
        "conclusion": "stationary" if reject else "non-stationary",
    }


def kpss_test(
    series,
    name: str | None = None,
    regression: str = "c",
    nlags: str | int = "auto",
    alpha: float = 0.05,
) -> dict:
    """
    Kwiatkowski-Phillips-Schmidt-Shin test for level- or trend-stationarity.

    H0: the series is (level- or trend-) stationary.
    Reject H0 (small p-value) => evidence of non-stationarity.

    Note: statsmodels clips the p-value to the [0.01, 0.10] lookup range
    and emits a warning at the extremes; that warning is suppressed here.
    When p_value lands on a boundary, inspect statistic vs critical_values.
    """
    s = _as_series(series, name)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stat, pvalue, _lags, crit = kpss(s, regression=regression, nlags=nlags)
    null = "trend-stationary" if regression == "ct" else "level-stationary"
    reject = pvalue < alpha
    return {
        "series": _resolve_name(name, s),
        "test_name": f"KPSS({regression})",
        "statistic": float(stat),
        "p_value": float(pvalue),
        "critical_values": {k: float(v) for k, v in crit.items()},
        "null": null,
        "conclusion": "non-stationary" if reject else null,
    }


# ---------------------------------------------------------------------------
# conditional heteroskedasticity
# ---------------------------------------------------------------------------

def arch_lm_test(
    series,
    name: str | None = None,
    nlags: int = 12,
    alpha: float = 0.05,
) -> dict:
    """
    Engle's ARCH-LM test for autoregressive conditional heteroskedasticity.

    H0: residuals are homoskedastic (no ARCH effects up to ``nlags``).
    Reject H0 (small p-value) => ARCH effects present.

    Best run on residuals of a fitted mean model, or on returns directly
    when the question is about volatility clustering. statsmodels does
    not return critical values; chi-squared(df=nlags) CVs are added here
    so the output schema matches the other tests.
    """
    s = _as_series(series, name)
    lm_stat, lm_pvalue, _f_stat, _f_pvalue = het_arch(s, nlags=nlags)
    reject = lm_pvalue < alpha
    return {
        "series": _resolve_name(name, s),
        "test_name": f"ARCH-LM({nlags})",
        "statistic": float(lm_stat),
        "p_value": float(lm_pvalue),
        "critical_values": _chi2_cvs(df=nlags),
        "null": "no ARCH effects (homoskedastic)",
        "conclusion": "ARCH effects present" if reject else "no ARCH effects",
    }


# ---------------------------------------------------------------------------
# cointegration
# ---------------------------------------------------------------------------

def johansen_test(
    data,
    names: Sequence[str] | None = None,
    det_order: int = 0,
    k_ar_diff: int = 1,
    test: str = "trace",
    alpha: float = 0.05,
) -> dict:
    """
    Johansen cointegration rank test.

    H0 (sequential): cointegration rank <= r, for r = 0, 1, ..., n-1.
    Reports per-rank statistics and an estimated rank.

    Parameters
    ----------
    data : DataFrame or 2D array, shape (n_obs, n_series)
    names : sequence of str, optional
        Defaults to ``data.columns`` if a DataFrame is passed.
    det_order : {-1, 0, 1}
        -1: no deterministic terms, 0: constant, 1: linear trend.
    k_ar_diff : int
        Number of lagged differences in the VECM.
    test : {'trace', 'maxeig'}
        Which Johansen statistic drives the rank decision; both are
        computed by statsmodels.
    alpha : {0.10, 0.05, 0.01}
        Significance level. statsmodels' Johansen CV table only has these.

    Returns
    -------
    dict
        ``statistic`` and ``critical_values`` are nested dicts keyed by
        ``"r<=r"``. ``p_value`` is None — statsmodels does not return
        finite-sample Johansen p-values.
    """
    if test not in {"trace", "maxeig"}:
        raise ValueError("test must be 'trace' or 'maxeig'")
    cv_col = {0.10: 0, 0.05: 1, 0.01: 2}.get(alpha)
    if cv_col is None:
        raise ValueError("alpha must be one of 0.10, 0.05, 0.01")

    if isinstance(data, pd.DataFrame):
        df = data.dropna()
        if names is None:
            names = list(df.columns)
        arr = df.values
    else:
        arr = np.asarray(data, dtype=float)
        arr = arr[~np.isnan(arr).any(axis=1)]
        if names is None:
            names = [f"y{i}" for i in range(arr.shape[1])]

    res = coint_johansen(arr, det_order=det_order, k_ar_diff=k_ar_diff)
    stats = res.lr1 if test == "trace" else res.lr2
    cvs = res.cvt if test == "trace" else res.cvm

    # Estimated rank: largest r* such that H0(rank <= r) is rejected for
    # all r < r*, and not rejected at r = r*.
    rank = 0
    for r, (st, cv_row) in enumerate(zip(stats, cvs)):
        if st > cv_row[cv_col]:
            rank = r + 1
        else:
            break

    stat_dict = {f"r<={r}": float(s) for r, s in enumerate(stats)}
    cv_dict = {
        f"r<={r}": {"10%": float(row[0]), "5%": float(row[1]), "1%": float(row[2])}
        for r, row in enumerate(cvs)
    }

    return {
        "series": list(names),
        "test_name": f"Johansen-{test}",
        "statistic": stat_dict,
        "p_value": None,
        "critical_values": cv_dict,
        "null": "cointegration rank <= r (sequentially for r = 0, 1, ...)",
        "conclusion": f"estimated rank = {rank} at alpha={alpha}",
    }


# ---------------------------------------------------------------------------
# decomposition
# ---------------------------------------------------------------------------

def stl_decompose(
    series,
    name: str | None = None,
    period: int | None = None,
    seasonal: int = 7,
    robust: bool = False,
) -> dict:
    """
    STL (Seasonal-Trend decomposition using Loess).

    Not a hypothesis test: ``p_value``, ``critical_values``, and ``null``
    are None. The ``statistic`` field carries trend and seasonal strength
    measures (Hyndman & Athanasopoulos, FPP3 §6.7):

        F_T = max(0, 1 - Var(R) / Var(T + R))
        F_S = max(0, 1 - Var(R) / Var(S + R))

    where T, S, R are the trend, seasonal, and remainder components.
    The decomposed components are returned in the ``components`` key
    (a DataFrame). Drop that column before writing the test-results CSV.

    Parameters
    ----------
    period : int, optional
        Required unless ``series`` has a DatetimeIndex with an explicit
        frequency.
    seasonal : int
        Length of the seasonal smoother (must be odd, >= 7).
    robust : bool
        Use robust loess iterations (down-weights outliers).
    """
    s = _as_series(series, name)
    if period is None:
        if not (isinstance(s.index, pd.DatetimeIndex) and s.index.freqstr):
            raise ValueError(
                "Pass period= explicitly, or supply a series with a "
                "DatetimeIndex that has an explicit frequency."
            )
        stl = STL(s, seasonal=seasonal, robust=robust)
    else:
        stl = STL(s, period=period, seasonal=seasonal, robust=robust)

    res = stl.fit()
    trend, seasonal_c, resid = res.trend, res.seasonal, res.resid

    var_r = np.nanvar(resid)
    trend_strength    = float(max(0.0, 1.0 - var_r / np.nanvar(trend + resid)))
    seasonal_strength = float(max(0.0, 1.0 - var_r / np.nanvar(seasonal_c + resid)))

    components = pd.DataFrame(
        {"trend": trend, "seasonal": seasonal_c, "resid": resid}
    )

    return {
        "series": _resolve_name(name, s),
        "test_name": "STL",
        "statistic": {
            "trend_strength": trend_strength,
            "seasonal_strength": seasonal_strength,
        },
        "p_value": None,
        "critical_values": None,
        "null": None,
        "conclusion": _describe_strength(trend_strength, seasonal_strength),
        "components": components,
    }


def _describe_strength(trend_strength: float, seasonal_strength: float) -> str:
    """Wang/Smyth/Hyndman (2006)-style banding of F_T and F_S."""
    def band(x: float) -> str:
        if x > 0.64:
            return "strong"
        if x > 0.30:
            return "moderate"
        return "weak"
    return f"{band(trend_strength)} trend; {band(seasonal_strength)} seasonality"
