"""Scenario engine — what-if simulations using documented financial formulas."""
from __future__ import annotations

from dataclasses import dataclass, field
import pandas as pd

from .analytics_engine import safe_div


@dataclass
class ScenarioResult:
    name: str
    baseline_revenue: float = 0.0
    baseline_cost: float = 0.0
    price_change: float = 0.0
    volume_change: float = 0.0
    cost_change: float = 0.0
    projected_revenue: float = 0.0
    projected_cost: float = 0.0
    projected_profit: float = 0.0
    baseline_profit: float = 0.0
    revenue_delta: float = 0.0
    cost_delta: float = 0.0
    profit_delta: float = 0.0
    profit_delta_pct: float = 0.0
    notes: list[str] = field(default_factory=list)


def run_financial_scenario(
    name: str,
    baseline_revenue: float,
    baseline_cost: float,
    price_change: float = 0.0,
    volume_change: float = 0.0,
    cost_change: float = 0.0,
) -> ScenarioResult:
    projected_revenue = baseline_revenue * (1 + price_change) * (1 + volume_change)
    projected_cost = baseline_cost * (1 + cost_change)
    baseline_profit = baseline_revenue - baseline_cost
    projected_profit = projected_revenue - projected_cost

    res = ScenarioResult(
        name=name,
        baseline_revenue=round(baseline_revenue, 2),
        baseline_cost=round(baseline_cost, 2),
        price_change=price_change, volume_change=volume_change, cost_change=cost_change,
        projected_revenue=round(projected_revenue, 2),
        projected_cost=round(projected_cost, 2),
        baseline_profit=round(baseline_profit, 2),
        projected_profit=round(projected_profit, 2),
        revenue_delta=round(projected_revenue - baseline_revenue, 2),
        cost_delta=round(projected_cost - baseline_cost, 2),
        profit_delta=round(projected_profit - baseline_profit, 2),
        profit_delta_pct=round(safe_div(projected_profit - baseline_profit, abs(baseline_profit)) * 100, 2)
        if baseline_profit else float("nan"),
    )
    res.notes.append("Results are estimates based on simplified linear assumptions.")
    return res


def scenario_to_df(result: ScenarioResult) -> pd.DataFrame:
    return pd.DataFrame([
        {"Metric": "Revenue", "Baseline": result.baseline_revenue,
         "Projected": result.projected_revenue, "Delta": result.revenue_delta},
        {"Metric": "Cost", "Baseline": result.baseline_cost,
         "Projected": result.projected_cost, "Delta": result.cost_delta},
        {"Metric": "Profit", "Baseline": result.baseline_profit,
         "Projected": result.projected_profit, "Delta": result.profit_delta},
    ])