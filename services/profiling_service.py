"""Data profiling service — inspects a DataFrame and reports structure/quality."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import warnings

import numpy as np
import pandas as pd


@dataclass
class ColumnInfo:
    name: str
    dtype: str
    inferred_role: str
    missing_count: int
    missing_pct: float
    unique_count: int
    is_numeric: bool
    is_categorical: bool
    is_datetime: bool
    sample_values: list[Any] = field(default_factory=list)
    stats: dict[str, float] = field(default_factory=dict)


@dataclass
class Profile:
    n_rows: int
    n_cols: int
    columns: list[ColumnInfo]
    numerical_columns: list[str]
    categorical_columns: list[str]
    datetime_columns: list[str]
    duplicate_count: int
    total_missing: int
    memory_mb: float


def _infer_role(col: pd.Series, name: str) -> str:
    lname = name.lower().strip()
    if col.dtype.kind == "M":
        return "datetime"
    if col.dtype.kind in "biufc":
        if "revenue" in lname or "sales" in lname or "income" in lname or "earnings" in lname or "turnover" in lname or "amount" in lname:
            return "revenue"
        if "expense" in lname or "cost" in lname:
            return "expense"
        if "profit" in lname:
            return "profit"
        if "price" in lname:
            return "price"
        if "salary" in lname:
            return "salary"
        if "score" in lname or "performance" in lname or "rating" in lname:
            return "performance"
        if "count" in lname or "units" in lname or "qty" in lname or "quantity" in lname:
            return "quantity"
        return "numeric"
    nunique = col.nunique(dropna=True)
    if nunique <= 30:
        if "department" in lname or "team" in lname or "unit" in lname:
            return "department"
        if "service" in lname or "category" in lname or "type" in lname or "work" in lname:
            return "service_category"
        if "region" in lname or "area" in lname or "zone" in lname or "location" in lname:
            return "region"
        if "status" in lname or "state" in lname:
            return "status"
        if "client" in lname or "customer" in lname:
            return "customer"
        if "employee" in lname or "staff" in lname or "worker" in lname or "manager" in lname:
            return "employee"
        if "role" in lname or "title" in lname or "position" in lname:
            return "role"
        if "product" in lname or "item" in lname:
            return "product"
        return "categorical"
    return "identifier"


def _try_datetime(col: pd.Series) -> pd.Series:
    if col.dtype.kind == "M":
        return col
    if col.dtype.kind in "OUS":
        sample = col.dropna().astype(str).head(20)
        if sample.empty:
            return col
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", None):
            try:
                kw = {} if fmt is None else {"format": fmt}
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    converted = pd.to_datetime(sample, errors="raise", **kw)
                if not converted.isna().all():
                    return pd.to_datetime(col, errors="coerce", **kw)
            except (ValueError, TypeError):
                continue
    return col


def profile_dataframe(df: pd.DataFrame) -> Profile:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind in "OUS":
            converted = _try_datetime(df[c])
            if converted.dtype.kind == "M":
                df[c] = converted

    columns: list[ColumnInfo] = []
    numerical, categorical, datetimes = [], [], []
    total_missing = 0

    for c in df.columns:
        col = df[c]
        missing = int(col.isna().sum())
        total_missing += missing
        nunique = int(col.nunique(dropna=True))
        is_num = col.dtype.kind in "biufc"
        is_dt = col.dtype.kind == "M"
        is_cat = not is_num and not is_dt
        role = _infer_role(col, c)

        sample_vals = []
        if not col.empty:
            sample_vals = [str(v) for v in col.dropna().head(3).tolist()]

        stats: dict[str, float] = {}
        if is_num and not col.dropna().empty:
            clean = col.dropna().astype(float)
            stats = {
                "min": float(clean.min()),
                "max": float(clean.max()),
                "mean": float(clean.mean()),
                "median": float(clean.median()),
                "std": float(clean.std(ddof=0)) if len(clean) > 1 else 0.0,
            }

        info = ColumnInfo(
            name=c, dtype=str(col.dtype), inferred_role=role,
            missing_count=missing, missing_pct=round(missing / len(df) * 100, 2) if len(df) else 0.0,
            unique_count=nunique, is_numeric=is_num, is_categorical=is_cat, is_datetime=is_dt,
            sample_values=sample_vals, stats=stats,
        )
        columns.append(info)
        if is_num:
            numerical.append(c)
        elif is_dt:
            datetimes.append(c)
        else:
            categorical.append(c)

    return Profile(
        n_rows=len(df), n_cols=len(df.columns), columns=columns,
        numerical_columns=numerical, categorical_columns=categorical,
        datetime_columns=datetimes,
        duplicate_count=int(df.duplicated().sum()),
        total_missing=total_missing,
        memory_mb=round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3),
    )


def summary_dict(profile: Profile) -> dict[str, Any]:
    return {
        "Rows": profile.n_rows,
        "Columns": profile.n_cols,
        "Numerical columns": len(profile.numerical_columns),
        "Categorical columns": len(profile.categorical_columns),
        "Date columns": len(profile.datetime_columns),
        "Missing values": profile.total_missing,
        "Duplicate rows": profile.duplicate_count,
        "Memory (MB)": profile.memory_mb,
    }