"""Universal analytics engine — reusable statistical functions over any dataset."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


def safe_div(num: float, den: float) -> float:
    if den == 0 or pd.isna(den):
        return float("nan")
    return num / den


def describe_numeric(series: pd.Series) -> dict[str, float]:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return {}
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    return {
        "count": float(s.count()),
        "sum": float(s.sum()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "mode": float(s.mode().iloc[0]) if not s.mode().empty else float("nan"),
        "min": float(s.min()),
        "max": float(s.max()),
        "range": float(s.max() - s.min()),
        "std": float(s.std(ddof=0)),
        "var": float(s.var(ddof=0)),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
    }


def group_aggregate(df: pd.DataFrame, group_col: str, metric_col: str, agg: str = "sum") -> pd.DataFrame:
    if group_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame()
    series = pd.to_numeric(df[metric_col], errors="coerce")
    valid = df.loc[series.notna(), [group_col]].copy()
    valid[metric_col] = series.dropna().values
    if valid.empty:
        return pd.DataFrame()
    result = valid.groupby(group_col)[metric_col].agg(agg).reset_index()
    result = result.sort_values(metric_col, ascending=False)
    return result


def percentage_contribution(grouped: pd.DataFrame, value_col: str) -> pd.DataFrame:
    total = grouped[value_col].sum()
    out = grouped.copy()
    out["contribution_pct"] = out[value_col].apply(lambda v: round(safe_div(v, total) * 100, 2))
    return out


def trend_over_time(df: pd.DataFrame, date_col: str, metric_col: str, freq: str = "M") -> pd.DataFrame:
    if date_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame()
    dates = pd.to_datetime(df[date_col], errors="coerce")
    values = pd.to_numeric(df[metric_col], errors="coerce")
    mask = dates.notna() & values.notna()
    if not mask.any():
        return pd.DataFrame()
    tmp = pd.DataFrame({"date": dates[mask], "value": values[mask]})
    tmp = tmp.set_index("date").sort_index()
    resampled = tmp["value"].resample(freq).sum().reset_index()
    resampled.columns = [date_col, metric_col]
    if len(resampled) > 1:
        resampled["growth_pct"] = resampled[metric_col].pct_change().round(4) * 100
    return resampled


def correlation_matrix(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    numeric = df.select_dtypes(include="number")
    if cols:
        numeric = numeric[cols]
    if numeric.shape[1] < 2:
        return pd.DataFrame()
    return numeric.corr().round(3)


def detect_outliers(series: pd.Series, method: str = "iqr") -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return pd.Series(False, index=series.index)
    if method == "iqr":
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return (s < lower) | (s > upper)
    return pd.Series(False, index=series.index)


@dataclass
class AnalysisResult:
    question: str
    metric_col: str = ""
    group_col: str = ""
    operation: str = ""
    summary: dict[str, Any] = field(default_factory=dict)
    grouped: pd.DataFrame | None = None
    trend: pd.DataFrame | None = None
    correlations: pd.DataFrame | None = None
    insights: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)