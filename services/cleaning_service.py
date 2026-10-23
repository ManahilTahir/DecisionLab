"""Cleaning & formatting service — duplicates, nulls, date formatting, type conversion."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
import pandas as pd
import numpy as np


DATE_FORMATS = {
    "YYYY-MM-DD (ISO)": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y",
    "DD-MM-YYYY": "%d-%m-%Y",
    "YYYY/MM/DD": "%Y/%m/%d",
    "Month DD, YYYY": "%B %d, %Y",
    "DD-Mon-YYYY": "%d-%b-%Y",
}


@dataclass
class CleanResult:
    df: pd.DataFrame
    changed: bool
    message: str


def remove_duplicates(df: pd.DataFrame) -> CleanResult:
    before = len(df)
    cleaned = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(cleaned)
    return CleanResult(cleaned, removed > 0, f"Removed {removed} duplicate row(s). {len(cleaned)} rows remain.")


def handle_nulls(df: pd.DataFrame, column: str, strategy: str, fill_value: str = "") -> CleanResult:
    if column not in df.columns:
        return CleanResult(df, False, "Column not found.")
    cleaned = df.copy()
    null_count = int(cleaned[column].isna().sum())
    if null_count == 0:
        return CleanResult(df, False, f"No missing values in '{column}'.")

    if strategy == "drop":
        cleaned = cleaned.dropna(subset=[column]).reset_index(drop=True)
        msg = f"Dropped {null_count} row(s) with missing '{column}'."
    elif strategy == "mean":
        val = pd.to_numeric(cleaned[column], errors="coerce").mean()
        cleaned[column] = cleaned[column].fillna(val)
        msg = f"Filled {null_count} missing value(s) in '{column}' with mean ({val:.2f})."
    elif strategy == "median":
        val = pd.to_numeric(cleaned[column], errors="coerce").median()
        cleaned[column] = cleaned[column].fillna(val)
        msg = f"Filled {null_count} missing value(s) in '{column}' with median ({val:.2f})."
    elif strategy == "mode":
        mode_vals = cleaned[column].mode()
        if not mode_vals.empty:
            val = mode_vals.iloc[0]
            cleaned[column] = cleaned[column].fillna(val)
            msg = f"Filled {null_count} missing value(s) in '{column}' with mode ({val})."
        else:
            return CleanResult(df, False, "Could not determine mode.")
    elif strategy == "custom":
        cleaned[column] = cleaned[column].fillna(fill_value)
        msg = f"Filled {null_count} missing value(s) in '{column}' with '{fill_value}'."
    else:
        return CleanResult(df, False, "Unknown strategy.")
    return CleanResult(cleaned, True, msg)


def _parse_date_robust(value) -> pd.Timestamp:
    """Parse a single date value trying multiple strategies so mixed formats survive."""
    if pd.isna(value):
        return pd.NaT
    for kwargs in ({}, {"dayfirst": True}, {"dayfirst": False}):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                result = pd.to_datetime(value, errors="raise", **kwargs)
            if not pd.isna(result):
                return result
        except (ValueError, TypeError):
            continue
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
                "%Y/%m/%d", "%d.%m.%Y", "%m-%d-%Y", "%b %d, %Y", "%d-%b-%Y"):
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


def format_dates(df: pd.DataFrame, column: str, target_format: str) -> CleanResult:
    if column not in df.columns:
        return CleanResult(df, False, "Column not found.")
    cleaned = df.copy()
    parsed = cleaned[column].apply(_parse_date_robust)
    parsed = pd.to_datetime(parsed, errors="coerce")
    failed = int(parsed.isna().sum())
    success = len(parsed) - failed
    cleaned[column] = parsed.dt.strftime(target_format)
    if failed > 0:
        msg = f"Formatted {success} date(s) to '{target_format}'. {failed} could not be parsed (set to NaT)."
    else:
        msg = f"Formatted all {success} date(s) to '{target_format}'."
    return CleanResult(cleaned, True, msg)


def convert_type(df: pd.DataFrame, column: str, target_type: str) -> CleanResult:
    if column not in df.columns:
        return CleanResult(df, False, "Column not found.")
    cleaned = df.copy()
    try:
        if target_type == "numeric":
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        elif target_type == "text":
            cleaned[column] = cleaned[column].astype(str)
        elif target_type == "datetime":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")
        else:
            return CleanResult(df, False, "Unknown target type.")
    except Exception as exc:
        return CleanResult(df, False, f"Conversion failed: {exc}")
    return CleanResult(cleaned, True, f"Converted '{column}' to {target_type}.")


def standardize_text(df: pd.DataFrame, column: str, strip: bool = True, title_case: bool = False) -> CleanResult:
    if column not in df.columns:
        return CleanResult(df, False, "Column not found.")
    cleaned = df.copy()
    s = cleaned[column].astype(str)
    if strip:
        s = s.str.strip()
    if title_case:
        s = s.str.title()
    cleaned[column] = s
    return CleanResult(cleaned, True, f"Standardized text in '{column}'.")


def null_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing > 0:
            rows.append({"Column": col, "Missing": missing, "%": round(missing / len(df) * 100, 2)})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Column", "Missing", "%"])