from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import time_analysis
from src.data_cleaning import FACTORY_COORDINATES, load_data, quality_report
from src.metrics import aggregate_by, product_analysis, totals
from src.visualizations import pareto_chart, product_scatter

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "Nassau Candy Distributor.csv"

st.set_page_config(page_title="Nassau Candy | Profitability", page_icon="🍬", layout="wide")


@st.cache_data
def get_data(path: str) -> pd.DataFrame:
    return load_data(path)


def number(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


def show_metrics(frame: pd.DataFrame) -> None:
    summary = totals(frame)
    cards = [
        ("Total Sales", summary["Sales"]),
        ("Total Cost", summary["Cost"]),
        ("Gross Profit", summary["Gross Profit"]),
        ("Gross Margin %", summary["Gross Margin %"]),
        ("Total Units", summary["Units"]),
        ("Profit per Unit", summary["Profit per Unit"]),
        ("Product Count", summary["Product Count"]),
        ("Division Count", summary["Division Count"]),
    ]
    for offset in (0, 4):
        columns = st.columns(4)
        for column, (label, value) in zip(columns, cards[offset : offset + 4]):
            display = f"{number(value)}%" if label == "Gross Margin %" else number(value)
            column.metric(label, display)


def format_table(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    existing = [column for column in columns if column in frame.columns]
    return frame[existing].style.format(
        {
            column: "{:,.2f}"
            for column in existing
            if pd.api.types.is_numeric_dtype(frame[column])
        }
    )


try:
    data = get_data(str(DATA_PATH))
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load the required dataset: {error}")
    st.stop()

quality = quality_report(data)
st.title("Nassau Candy | Product Line Profitability")
st.caption("Analysis uses the provided distributor CSV. Currency units are not specified in the source.")

with st.sidebar:
    st.header("Global filters")
    valid_dates = data["Order Date"].dropna()
    if valid_dates.empty:
        st.error("No valid order dates are available; date filtering cannot be applied.")
        st.stop()
    date_range = st.date_input(
        "Order date range",
        value=(valid_dates.min().date(), valid_dates.max().date()),
        min_value=valid_dates.min().date(),
        max_value=valid_dates.max().date(),
    )
    division_choices = sorted(data["Division"].dropna().unique().tolist())
    divisions = st.multiselect("Division", division_choices, default=division_choices)
    region_choices = sorted(data["Region"].dropna().unique().tolist())
    regions = st.multiselect("Region", region_choices, default=region_choices)
    min_margin = st.slider("Minimum product gross margin (%)", -100.0, 100.0, -100.0, 1.0)
    product_search = st.text_input("Product search")
    st.selectbox(
        "Factory filter",
        ["Unavailable — product-to-factory mapping missing"],
        disabled=True,
    )
    st.caption("Factory financial attribution remains disabled until a product mapping is supplied.")
    page = st.selectbox(
        "Dashboard",
        [
            "Executive Overview",
            "Product Profitability",
            "Division Performance",
            "Cost & Margin Diagnostics",
            "Pareto Analysis",
            "Regional Analysis",
            "Factory Analysis",
        ],
    )

filtered = data.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["Order Date"].dt.date.between(start_date, end_date)
    ]
if divisions:
    filtered = filtered[filtered["Division"].isin(divisions)]
else:
    filtered = filtered.iloc[0:0]
if regions:
    filtered = filtered[filtered["Region"].isin(regions)]
else:
    filtered = filtered.iloc[0:0]
if product_search.strip():
    filtered = filtered[
        filtered["Product Name"].str.contains(product_search.strip(), case=False, na=False)
    ]

selected_products = product_analysis(filtered)
if not selected_products.empty and min_margin > 0:
    eligible_ids = selected_products.loc[
        selected_products["Gross Margin %"].ge(min_margin), "Product ID"
    ]
    filtered = filtered[filtered["Product ID"].isin(eligible_ids)]

with st.expander("Data quality and interpretation notes", expanded=False):
    st.write(
        f"Loaded {quality['rows']:,} rows across {quality['columns']} source columns; "
        f"{quality['rows_retained']:,} rows are retained. "
        f"Exact duplicate records: {quality['exact_duplicates']:,}; "
        f"missing source cells: {sum(quality['missing_values'].values()):,}."
    )
    st.warning(
        f"All {quality['date_anomalies']:,} parsed order-to-ship intervals exceed one year "
        f"(range {quality['date_gap_min']}–{quality['date_gap_max']} days; "
        f"median {quality['date_gap_median']:,.0f} days). Dates are not corrected; "
        "time analysis uses Order Date."
    )
    if quality["division_prefix_mismatch_rows"]:
        st.warning(
            "One product ID prefix does not match the apparent division code: "
            + ", ".join(
                f"{row['Product ID']} ({row['Division']})"
                for row in quality["division_prefix_mismatches"]
            )
            + ". The recorded Division value is preserved."
        )
    if quality["gross_profit_mismatches"]:
        st.warning(
            f"{quality['gross_profit_mismatches']:,} records do not reconcile "
            "Gross Profit = Sales - Cost within tolerance."
        )

if filtered.empty:
    st.warning("No rows match the selected filters. Adjust the filters to continue.")
    st.stop()

products = product_analysis(filtered)
divisions_summary = aggregate_by(filtered, "Division")
regions_summary = aggregate_by(filtered, "Region")
states_summary = aggregate_by(filtered, "State/Province")
cities_summary = aggregate_by(filtered, "City")

if page == "Executive Overview":
    st.subheader("Executive Overview")
    show_metrics(filtered)
    st.markdown(
        "All displayed measures respond to the sidebar filters. Product margin filtering is "
        "applied to each product's aggregate margin within the filtered records."
    )
    frequency = st.radio("Trend period", ["Month", "Quarter"], horizontal=True)
    trend = time_analysis(filtered, "quarter" if frequency == "Quarter" else "month")
    metric_choice = st.selectbox("Trend measure", ["Sales", "Cost", "Gross Profit", "Units", "Gross Margin %"])
    st.plotly_chart(
        px.line(trend, x="Period", y=metric_choice, markers=True, title=f"{metric_choice} by {frequency.lower()}"),
        width="stretch",
    )
    st.dataframe(
        format_table(
            trend,
            ["Period", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %"],
        ),
        width="stretch",
        hide_index=True,
    )

elif page == "Product Profitability":
    st.subheader("Product Profitability")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Top products by gross profit")
        st.dataframe(
            format_table(
                products.nlargest(10, "Gross Profit"),
                ["Product Name", "Division", "Sales", "Cost", "Units", "Gross Profit", "Gross Margin %", "Profit per Unit", "Profit Contribution %"],
            ),
            width="stretch",
            hide_index=True,
        )
    with right:
        st.markdown("#### Top products by gross margin")
        st.dataframe(
            format_table(
                products.nlargest(10, "Gross Margin %"),
                ["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %", "Profit per Unit"],
            ),
            width="stretch",
            hide_index=True,
        )
    st.plotly_chart(
        product_scatter(
            products,
            "Sales",
            "Gross Profit",
            "Gross Margin %",
            "Product sales vs gross profit",
        ),
        width="stretch",
    )
    st.caption(
        "Profitability segments use median product sales and median product gross profit "
        "within the current filter selection."
    )
    st.dataframe(
        format_table(
            products.sort_values("Sales", ascending=False),
            ["Product Name", "Division", "Sales", "Cost", "Units", "Gross Profit", "Gross Margin %", "Profit per Unit", "Revenue Contribution %", "Profit Contribution %", "Profitability Segment"],
        ),
        width="stretch",
        hide_index=True,
    )

elif page == "Division Performance":
    st.subheader("Division Performance")
    st.plotly_chart(
        px.bar(divisions_summary, x="Division", y=["Sales", "Gross Profit"], barmode="group", title="Revenue vs gross profit by division"),
        width="stretch",
    )
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.bar(divisions_summary, x="Division", y="Gross Margin %", title="Weighted gross margin by division"),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            px.box(products, x="Division", y="Gross Margin %", points="all", title="Product margin distribution by division"),
            width="stretch",
        )
    st.dataframe(
        format_table(
            divisions_summary,
            ["Division", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit", "Revenue Contribution %", "Profit Contribution %"],
        ),
        width="stretch",
        hide_index=True,
    )

elif page == "Cost & Margin Diagnostics":
    st.subheader("Cost & Margin Diagnostics")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.scatter(products, x="Sales", y="Cost", color="Gross Margin %", hover_name="Product Name", title="Product sales vs cost"),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            px.scatter(products, x="Cost", y="Gross Margin %", color="Division", hover_name="Product Name", title="Product cost vs gross margin"),
            width="stretch",
        )
    margin_q1 = products["Gross Margin %"].quantile(0.25)
    sales_median = products["Sales"].median()
    cost_q3 = products["Cost"].quantile(0.75)
    high_sales_low_margin = products[
        products["Sales"].ge(sales_median) & products["Gross Margin %"].lt(margin_q1)
    ]
    cost_heavy = products[products["Cost"].gt(cost_q3)].sort_values("Cost", ascending=False)
    st.caption(
        f"High-sales/low-margin means sales at or above the product median "
        f"({number(sales_median)}) and margin below the product 25th percentile "
        f"({number(margin_q1)}%). Cost-heavy means product cost above its 75th percentile "
        f"({number(cost_q3)}). Negative-margin products are flagged Critical."
    )
    st.markdown("#### Margin risk categories")
    st.dataframe(
        format_table(
            products.sort_values("Gross Margin %"),
            ["Product Name", "Division", "Sales", "Cost", "Gross Profit", "Gross Margin %", "Margin Risk"],
        ),
        width="stretch",
        hide_index=True,
    )
    st.markdown("#### High-sales / low-margin products")
    st.dataframe(format_table(high_sales_low_margin, ["Product Name", "Sales", "Cost", "Gross Profit", "Gross Margin %"]), width="stretch", hide_index=True)
    st.markdown("#### Cost-heavy products")
    st.dataframe(format_table(cost_heavy, ["Product Name", "Sales", "Cost", "Gross Profit", "Gross Margin %"]), width="stretch", hide_index=True)

elif page == "Pareto Analysis":
    st.subheader("Pareto Analysis")
    revenue, profit = st.columns(2)
    for column, metric, title in [
        (revenue, "Sales", "Revenue Pareto"),
        (profit, "Gross Profit", "Gross profit Pareto"),
    ]:
        ordered = products.sort_values(metric, ascending=False).reset_index(drop=True)
        cumulative = ordered[metric].cumsum() / ordered[metric].sum() * 100
        count = int(cumulative.lt(80).sum() + 1)
        coverage = float(cumulative.iloc[count - 1])
        column.metric(
            f"Products to reach 80% {metric.lower()}",
            f"{count} / {len(ordered)}",
            f"{count / len(ordered) * 100:.1f}% of products; {coverage:.1f}% covered",
        )
        column.plotly_chart(pareto_chart(products, metric, title), width="stretch")

elif page == "Regional Analysis":
    st.subheader("Regional Analysis")
    st.plotly_chart(
        px.bar(regions_summary, x="Region", y=["Sales", "Gross Profit"], barmode="group", title="Sales and gross profit by region"),
        width="stretch",
    )
    st.plotly_chart(
        px.bar(regions_summary, x="Region", y="Gross Margin %", title="Weighted gross margin by region"),
        width="stretch",
    )
    state_choice = st.radio("State table ranking", ["Sales", "Gross Profit", "Gross Margin %"], horizontal=True)
    st.dataframe(
        format_table(
            states_summary.sort_values(state_choice, ascending=False),
            ["State/Province", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit", "Revenue Contribution %", "Profit Contribution %"],
        ),
        width="stretch",
        hide_index=True,
    )
    st.markdown("#### Top cities")
    city_choice = st.radio(
        "Rank cities by",
        ["Sales", "Gross Profit", "Gross Margin %"],
        horizontal=True,
        key="city_ranking",
    )
    st.dataframe(
        format_table(
            cities_summary.nlargest(20, city_choice),
            ["City", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit"],
        ),
        width="stretch",
        hide_index=True,
    )
    st.caption("No state/city coordinates are provided, so a geographic map is not inferred.")

else:
    st.subheader("Factory Analysis")
    st.info(
        "Factory coordinates are available, but the required product-to-factory mapping is not. "
        "Factory sales, cost, profit, margin, product counts, and factory filtering cannot be "
        "calculated without that mapping; no attribution is inferred."
    )
    st.dataframe(FACTORY_COORDINATES, width="stretch", hide_index=True)
    figure = px.scatter_geo(
        FACTORY_COORDINATES,
        lat="Latitude",
        lon="Longitude",
        text="Factory",
        hover_name="Factory",
        scope="usa",
        title="Provided factory locations (not financial attribution)",
    )
    figure.update_traces(marker=dict(size=12))
    st.plotly_chart(figure, width="stretch")
