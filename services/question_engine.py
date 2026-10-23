"""Rule-based question interpretation engine — no AI/ML, configurable keyword maps."""
from __future__ import annotations

from dataclasses import dataclass, field
import re

from .column_mapping_service import columns_by_role, role_label


METRIC_KEYWORDS = {
    "revenue": ["revenue", "sales", "income", "earnings", "turnover", "amount"],
    "expense": ["expense", "cost", "spending", "expenditure"],
    "profit": ["profit", "margin", "profitability"],
    "performance": ["performance", "score", "rating", "productivity"],
    "quantity": ["quantity", "units", "count", "volume", "number of"],
}

GROUP_KEYWORDS = {
    "service_category": ["service", "category", "type", "work type"],
    "department": ["department", "team", "unit", "division"],
    "region": ["region", "area", "zone", "location", "geography"],
    "product": ["product", "item", "sku"],
    "employee": ["employee", "staff", "worker", "manager"],
    "customer": ["customer", "client"],
}

OPERATION_KEYWORDS = {
    "highest": ["highest", "most", "top", "best", "max", "maximum", "largest", "greatest"],
    "lowest": ["lowest", "least", "bottom", "worst", "min", "minimum", "smallest"],
    "trend": ["trend", "over time", "change", "growth", "changed", "monthly", "over the"],
    "compare": ["compare", "comparison", "versus", " vs ", "difference"],
    "distribution": ["distribution", "spread", "histogram"],
    "outlier": ["outlier", "unusual", "anomaly", "strange"],
    "what_if": ["what if", "what happens if", "simulate", "scenario", "reduce", "increase"],
    "summary": ["summarize", "summary", "overview", "analyze", "patterns", "insights"],
}


@dataclass
class Interpretation:
    metric_role: str = ""
    group_role: str = ""
    operation: str = "summary"
    confidence: str = "low"
    needs_clarification: bool = False
    clarification: str = ""
    matched_keywords: list[str] = field(default_factory=list)


def _find_role(text: str, keyword_map: dict[str, list[str]]) -> str:
    text_lower = text.lower()
    for role, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text_lower:
                return role
    return ""


def _find_operation(text: str) -> str:
    text_lower = text.lower()
    for op, keywords in OPERATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return op
    return "summary"


def interpret(question: str, mappings: dict[str, str]) -> Interpretation:
    if not question.strip():
        return Interpretation(needs_clarification=True, clarification="Please enter a question.")

    metric_role = _find_role(question, METRIC_KEYWORDS)
    group_role = _find_role(question, GROUP_KEYWORDS)
    operation = _find_operation(question)

    matched = []
    if metric_role:
        matched.append(role_label(metric_role))
    if group_role:
        matched.append(role_label(group_role))

    interp = Interpretation(
        metric_role=metric_role, group_role=group_role,
        operation=operation, matched_keywords=matched,
    )

    if operation == "what_if":
        interp.confidence = "high"
        return interp

    if not metric_role and not group_role and operation == "summary":
        interp.confidence = "medium"
        return interp

    available_metric = bool(metric_role and columns_by_role(mappings, metric_role))
    available_group = bool(group_role and columns_by_role(mappings, group_role))

    if metric_role and not available_metric:
        interp.needs_clarification = True
        interp.clarification = (
            f"Your question mentions {role_label(metric_role)}, but no matching column was found. "
            "Please confirm which column to use."
        )
        interp.confidence = "low"
        return interp

    if group_role and not available_group:
        interp.needs_clarification = True
        interp.clarification = (
            f"Your question mentions grouping by {role_label(group_role)}, but no matching column was found. "
            "Please confirm which column to use."
        )
        interp.confidence = "low"
        return interp

    if not metric_role and available_group:
        numeric_roles = [r for r in ["revenue", "expense", "profit", "performance", "quantity"]
                         if columns_by_role(mappings, r)]
        if len(numeric_roles) == 1:
            interp.metric_role = numeric_roles[0]
            interp.confidence = "medium"
        elif len(numeric_roles) > 1:
            interp.needs_clarification = True
            interp.clarification = (
                f"Which metric would you like to analyze by {role_label(group_role)}? "
                f"Available: {', '.join(role_label(r) for r in numeric_roles)}."
            )
            interp.confidence = "low"
        return interp

    interp.confidence = "high" if (metric_role and group_role) else "medium"
    return interp


SUGGESTED_QUESTIONS = [
    "Which service category generates the highest revenue?",
    "Which products are the most profitable?",
    "Which department has the highest average performance?",
    "How has revenue changed over time?",
    "Which region generates the most sales?",
    "What are the major patterns in my data?",
    "What happens if I reduce costs by 10%?",
    "Compare two departments.",
    "Find unusual values in this dataset.",
    "Analyze this dataset and summarize the most important findings.",
    "What is the total revenue across all categories?",
    "Which column has the most missing values?",
    "What is the average value of each numeric column?",
    "How are the numeric columns correlated with each other?",
    "Which category appears most frequently in the data?",
    "What is the distribution of each numeric column?",
    "Show me the top 10 records by the highest value.",
    "What is the year-over-year growth trend?",
    "Which records have the lowest values?",
    "Summarize the dataset with key statistics.",
]

OTHER_QUESTIONS = [
    "Show me a complete overview of my dataset.",
    "What is the relationship between revenue and expenses?",
    "Which records are outliers in my data?",
    "What is the median value of each numeric column?",
    "How many unique values are in each column?",
    "What is the total count of records per category?",
    "Which column contributes most to the overall total?",
    "What is the range (min to max) of each numeric column?",
    "Are there any seasonal patterns in my time-based data?",
    "What is the percentage breakdown of each category?",
]

GOAL_BUTTONS = [
    ("Increase Revenue", "revenue"),
    ("Improve Profitability", "profit"),
    ("Reduce Costs", "expense"),
    ("Improve Employee Performance", "performance"),
    ("Compare Departments", "department"),
    ("Analyze Service Performance", "service_category"),
    ("Analyze Product Performance", "product"),
    ("Explore My Data", "summary"),
    ("Create a What-If Scenario", "what_if"),
]