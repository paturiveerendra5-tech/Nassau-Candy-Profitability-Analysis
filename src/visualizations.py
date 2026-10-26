from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def pareto_chart(frame: pd.DataFrame, value: str, title: str) -> go.Figure:
    ordered = frame.sort_values(value, ascending=False).copy()
    ordered["Cumulative %"] = ordered[value].cumsum() / ordered[value].sum() * 100
    figure = go.Figure()
    figure.add_bar(x=ordered["Product Name"], y=ordered[value], name=value)
    figure.add_scatter(
        x=ordered["Product Name"],
        y=ordered["Cumulative %"],
        name="Cumulative contribution %",
        yaxis="y2",
        mode="lines+markers",
    )
    figure.add_hline(y=80, line_dash="dash", line_color="#d97706", yref="y2")
    figure.update_layout(
        title=title,
        xaxis_title="Product",
        yaxis=dict(title=value),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
        legend=dict(orientation="h", y=1.12),
    )
    return figure


def product_scatter(products: pd.DataFrame, x: str, y: str, color: str, title: str):
    return px.scatter(
        products,
        x=x,
        y=y,
        color=color,
        hover_name="Product Name",
        hover_data=["Product ID", "Division", "Gross Margin %", "Profit per Unit"],
        title=title,
        color_continuous_scale="RdYlGn",
    )
