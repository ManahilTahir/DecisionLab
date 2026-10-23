"""Report service — exports analysis results and cleaned data."""
from __future__ import annotations

import io
from datetime import datetime

import pandas as pd


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return buf.getvalue()


def build_summary_report(
    question: str,
    mappings: dict[str, str],
    summary: dict,
    insights: list[str],
) -> pd.DataFrame:
    rows = [
        {"Section": "Generated", "Detail": datetime.now().strftime("%Y-%m-%d %H:%M")},
        {"Section": "Question", "Detail": question},
    ]
    for col, role in mappings.items():
        rows.append({"Section": "Column Mapping", "Detail": f"{col} -> {role}"})
    for k, v in summary.items():
        rows.append({"Section": "Summary", "Detail": f"{k}: {v}"})
    for ins in insights:
        rows.append({"Section": "Insight", "Detail": ins})
    return pd.DataFrame(rows)


def safe_filename(text: str) -> str:
    keep = "".join(c if c.isalnum() or c in "-_" else "_" for c in text)
    return keep[:50] or "report"