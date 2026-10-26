from __future__ import annotations

import pandas as pd

from src.metrics import aggregate_by, pareto_analysis, product_analysis, totals


def time_analysis(frame: pd.DataFrame, frequency: str = "month") -> pd.DataFrame:
    if frequency == "quarter":
        period = frame["Order Date"].dt.to_period("Q").astype("string")
    else:
        period = frame["Order Date"].dt.to_period("M").astype("string")
    work = frame.assign(Period=period)
    return aggregate_by(work, "Period").sort_values("Period")


def pareto_summary(frame: pd.DataFrame) -> dict[str, tuple[int, float]]:
    products = product_analysis(frame)
    _, revenue_count, revenue_coverage = pareto_analysis(products, "Sales")
    _, profit_count, profit_coverage = pareto_analysis(products, "Gross Profit")
    return {
        "revenue": (revenue_count, revenue_coverage),
        "profit": (profit_count, profit_coverage),
    }


def comparison_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "products": product_analysis(frame),
        "divisions": aggregate_by(frame, "Division").sort_values("Gross Profit", ascending=False),
        "regions": aggregate_by(frame, "Region").sort_values("Gross Profit", ascending=False),
        "states": aggregate_by(frame, "State/Province").sort_values("Gross Profit", ascending=False),
    }


def overall_metrics(frame: pd.DataFrame) -> dict[str, float]:
    return totals(frame)
