from __future__ import annotations

import pandas as pd

FINANCIAL_METRICS = ["Sales", "Cost", "Gross Profit", "Units"]
PRODUCT_KEYS = ["Product ID", "Product Name", "Division"]


def totals(frame: pd.DataFrame) -> dict[str, float]:
    sales = float(frame["Sales"].sum())
    cost = float(frame["Cost"].sum())
    profit = float(frame["Gross Profit"].sum())
    units = float(frame["Units"].sum())
    return {
        "Sales": sales,
        "Cost": cost,
        "Gross Profit": profit,
        "Units": units,
        "Gross Margin %": profit / sales * 100 if sales else 0.0,
        "Profit per Unit": profit / units if units else 0.0,
        "Product Count": int(frame["Product ID"].nunique()),
        "Division Count": int(frame["Division"].nunique()),
    }


def aggregate_by(frame: pd.DataFrame, keys: str | list[str]) -> pd.DataFrame:
    group_keys = [keys] if isinstance(keys, str) else keys
    summary = (
        frame.groupby(group_keys, dropna=False, observed=True)[FINANCIAL_METRICS]
        .sum()
        .reset_index()
    )
    sales = summary["Sales"]
    units = summary["Units"]
    summary["Gross Margin %"] = summary["Gross Profit"].div(sales.where(sales.ne(0))).mul(100)
    summary["Profit per Unit"] = summary["Gross Profit"].div(units.where(units.ne(0)))
    total_sales = float(summary["Sales"].sum())
    total_profit = float(summary["Gross Profit"].sum())
    summary["Revenue Contribution %"] = (
        summary["Sales"].div(total_sales).mul(100) if total_sales else 0.0
    )
    summary["Profit Contribution %"] = (
        summary["Gross Profit"].div(total_profit).mul(100) if total_profit else 0.0
    )
    return summary


def product_analysis(frame: pd.DataFrame) -> pd.DataFrame:
    products = aggregate_by(frame, PRODUCT_KEYS)
    products["Profit Rank"] = products["Gross Profit"].rank(method="dense", ascending=False).astype(int)
    products["Margin Rank"] = products["Gross Margin %"].rank(method="dense", ascending=False).astype(int)

    sales_median = products["Sales"].median()
    profit_median = products["Gross Profit"].median()
    products["Sales Band"] = products["Sales"].ge(sales_median).map(
        {True: "High sales", False: "Low sales"}
    )
    products["Profit Band"] = products["Gross Profit"].ge(profit_median).map(
        {True: "High profit", False: "Low profit"}
    )
    products["Profitability Segment"] = products["Sales Band"] + " / " + products["Profit Band"]

    q1, q3 = products["Gross Margin %"].quantile([0.25, 0.75])
    products["Margin Risk"] = "Medium Margin / Monitor"
    products.loc[products["Gross Margin %"].lt(0), "Margin Risk"] = "Negative Margin / Critical"
    products.loc[
        products["Gross Margin %"].ge(0) & products["Gross Margin %"].lt(q1),
        "Margin Risk",
    ] = "Low Margin / High Risk"
    products.loc[
        products["Gross Margin %"].ge(q3), "Margin Risk"
    ] = "High Margin / Low Risk"
    return products.sort_values("Gross Profit", ascending=False).reset_index(drop=True)


def pareto_analysis(products: pd.DataFrame, value: str) -> tuple[pd.DataFrame, int, float]:
    ordered = products.sort_values(value, ascending=False).copy().reset_index(drop=True)
    total = float(ordered[value].sum())
    contribution = ordered[value].div(total) if total else 0.0
    ordered["Contribution %"] = contribution * 100
    ordered["Cumulative Contribution %"] = contribution.cumsum() * 100
    count = (
        int(ordered["Cumulative Contribution %"].lt(80).sum() + 1)
        if total and not ordered.empty
        else 0
    )
    covered = (
        float(ordered.iloc[count - 1]["Cumulative Contribution %"])
        if count
        else 0.0
    )
    return ordered, count, covered
