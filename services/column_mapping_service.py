"""Column mapping service — suggests semantic roles and lets users confirm."""
from __future__ import annotations

import pandas as pd

from .profiling_service import Profile

ROLE_LABELS = {
    "revenue": "Revenue / Sales Amount",
    "expense": "Expense / Cost",
    "profit": "Profit",
    "price": "Unit Price",
    "quantity": "Quantity / Count",
    "salary": "Salary",
    "performance": "Performance Score",
    "datetime": "Date / Time",
    "department": "Department / Team",
    "service_category": "Service / Category",
    "region": "Region / Location",
    "status": "Status",
    "customer": "Customer / Client",
    "employee": "Employee",
    "role": "Role / Title",
    "product": "Product / Item",
    "identifier": "Identifier",
    "numeric": "Other Numeric",
    "categorical": "Other Categorical",
}

ALL_ROLES = list(ROLE_LABELS.keys())


def suggest_mappings(profile: Profile) -> dict[str, str]:
    return {col.name: col.inferred_role for col in profile.columns}


def role_label(role: str) -> str:
    return ROLE_LABELS.get(role, role)


def find_role(profile: Profile, role: str) -> str | None:
    for col in profile.columns:
        if col.inferred_role == role:
            return col.name
    return None


def columns_by_role(mappings: dict[str, str], role: str) -> list[str]:
    return [name for name, r in mappings.items() if r == role]


def has_revenue(mappings: dict[str, str]) -> bool:
    return bool(columns_by_role(mappings, "revenue"))


def has_expense(mappings: dict[str, str]) -> bool:
    return bool(columns_by_role(mappings, "expense") or columns_by_role(mappings, "cost"))


def has_profit(mappings: dict[str, str]) -> bool:
    return bool(columns_by_role(mappings, "profit"))


def can_compute_profitability(mappings: dict[str, str]) -> bool:
    return has_revenue(mappings) and has_expense(mappings)