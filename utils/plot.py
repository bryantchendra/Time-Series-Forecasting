"""
utils/plot.py
=============

Plotting helpers for the EDA notebook. The main export is
``overlay_breaks``, which shades structural-break windows on a
time-series axis and labels each event at the top.

Typical use::

    from utils.plot import overlay_breaks, SHORT_BREAK_LABELS

    fig, ax = plt.subplots(figsize=(12, 5))
    prices["Brent"].plot(ax=ax)
    overlay_breaks(ax, breaks, short_labels=SHORT_BREAK_LABELS)

For plots zoomed to a sub-range of the event log, pass ``date_range``
so out-of-range events are dropped before drawing — otherwise the
off-axes text artists confuse ``tight_layout``::

    overlay_breaks(
        ax, breaks,
        short_labels=SHORT_BREAK_LABELS,
        date_range=("2024-01-01", "2026-05-19"),
    )

Why a wrapper: the EDA notebook overlays structural breaks on 15+
figures, M3 reuses the same shading for the rolling-origin diagnostic
plots on Day 4-5, and M5 uses the same labels in the final report.
One helper, one label scheme, consistent everywhere.
"""

from __future__ import annotations

import pandas as pd


__all__ = [
    "overlay_breaks",
    "SHORT_BREAK_LABELS",
]


SHORT_BREAK_LABELS: dict[str, str] = {
    "COVID onset":                              "COVID",
    "Oil price collapse":                       "WTI -$37",
    "Russia invades Ukraine":                   "Ukraine",
    "Israel-Hamas war begins":                  "Oct 7",
    "Iran first direct strike on Israel":       "Iran #1",
    "Iran second direct strike on Israel":      "Iran #2",
    "Liberation Day tariffs":                   "Tariffs",
    "Israel-Iran 12-Day War":                   "12-Day War",
    "2026 Iran War / Strait of Hormuz closure": "Hormuz 2026",
}


def overlay_breaks(
    ax,
    breaks: pd.DataFrame,
    *,
    short_labels: dict[str, str] | None = None,
    pad_top: float = 0.12,
    date_range: tuple | None = None,
) -> None:
    """Shade structural-break windows on a time-series axis.

    Parameters
    ----------
    ax : matplotlib Axes
        Axes with the time series already plotted.
    breaks : DataFrame
        Must have columns 'event', 'start_date', 'end_date' (Timestamps).
    short_labels : dict, optional
        Mapping ``{event_name: short_string}`` for crowded plots. Events
        not in the dict fall back to their full ``event`` value.
    pad_top : float
        Fraction of the y-range to add on top for label headroom.
        Default 0.12.
    date_range : (start, end) tuple of date-like, optional
        If provided, only events overlapping this range are drawn. Pass
        this whenever the axes xlim is narrower than the full event log
        (e.g. zooming to 2024+) — otherwise off-axes text artists will
        break ``tight_layout``.
    """
    # Lock x autoscale so out-of-range spans don't expand the view
    ax.set_autoscalex_on(False)

    # Headroom on top for labels
    y_min, y_max = ax.get_ylim()
    ax.set_ylim(y_min, y_max + (y_max - y_min) * pad_top)
    y_label = ax.get_ylim()[1]

    # Drop events outside the visible window, if a range was given
    if date_range is not None:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        breaks = breaks[(breaks.end_date >= start) & (breaks.start_date <= end)]

    for _, row in breaks.iterrows():
        ax.axvspan(row.start_date, row.end_date, alpha=0.15, color="grey")
        label = (short_labels or {}).get(row.event, row.event)
        ax.text(
            row.start_date, y_label, label,
            rotation=90, va="top", ha="right",
            fontsize=7, alpha=0.7,
        )