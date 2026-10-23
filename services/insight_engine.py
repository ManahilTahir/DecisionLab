"""Insight engine — evidence-based, auto-generated insights from real data."""
from __future__ import annotations

import pandas as pd

from .analytics_engine import group_aggregate, percentage_contribution, safe_div


def generate_insights(df: pd.DataFrame, mappings: dict[str, str]) -> list[str]:
    insights: list[str] = []
    revenue_cols = [c for c, r in mappings.items() if r == "revenue"]
    expense_cols = [c for c, r in mappings.items() if r == "expense"]
    group_cols = [c for c, r in mappings.items() if r in ("service_category", "department", "region", "product")]

    if revenue_cols and group_cols:
        rev = revenue_cols[0]
        for g in group_cols:
            grouped = group_aggregate(df, g, rev, "sum")
            if grouped.empty:
                continue
            top = grouped.iloc[0]
            contributions = percentage_contribution(grouped, rev)
            top_pct = contributions.iloc[0]["contribution_pct"]
            insights.append(
                f"{top[g]} generated the highest {rev} at {top[rev]:,.2f} "
                f"({top_pct:.1f}% of total)."
            )
            break

    if revenue_cols and expense_cols:
        rev = pd.to_numeric(df[revenue_cols[0]], errors="coerce").sum()
        cost = pd.to_numeric(df[expense_cols[0]], errors="coerce").sum()
        profit = rev - cost
        margin = safe_div(profit, rev) * 100 if rev else float("nan")
        insights.append(
            f"Total revenue is {rev:,.2f}, total cost is {cost:,.2f}, "
            f"giving a profit of {profit:,.2f} (margin {margin:.1f}%)."
        )
    elif revenue_cols and not expense_cols:
        insights.append("Revenue data exists, but cost information is missing, so profitability cannot be calculated.")
    elif not revenue_cols and expense_cols:
        insights.append("Expense data exists, but no revenue column was confirmed.")

    perf_cols = [c for c, r in mappings.items() if r == "performance"]
    dept_cols = [c for c, r in mappings.items() if r == "department"]
    if perf_cols and dept_cols:
        grouped = group_aggregate(df, dept_cols[0], perf_cols[0], "mean")
        if not grouped.empty:
            top = grouped.iloc[0]
            insights.append(
                f"{top[dept_cols[0]]} has the highest average {perf_cols[0]} at {top[perf_cols[0]]:.2f}."
            )

    if not insights:
        insights.append("Not enough confirmed columns to generate specific insights. Confirm column meanings to unlock more.")
    return insights