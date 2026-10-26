from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_cleaning import FACTORY_COORDINATES, load_data, quality_report
from src.metrics import aggregate_by, product_analysis, totals

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "Nassau Candy Distributor.csv"
REPORTS_DIR = ROOT / "reports"


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


def markdown_table(frame: pd.DataFrame, columns: list[str], labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    table = frame[columns].copy()
    table = table.rename(columns=labels)
    headers = [str(column) for column in table.columns]
    rows: list[list[str]] = []
    for _, row in table.iterrows():
        formatted = []
        for column, value in row.items():
            if pd.isna(value):
                formatted.append("—")
            elif pd.api.types.is_number(value):
                if str(column).endswith("%"):
                    formatted.append(f"{value:.2f}%")
                elif column in {"Units", "Rows"}:
                    formatted.append(f"{value:,.0f}")
                else:
                    formatted.append(f"{value:,.2f}")
            else:
                formatted.append(str(value).replace("|", "\\|"))
        rows.append(formatted)
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
            *("| " + " | ".join(row) + " |" for row in rows),
        ]
    )


def generate_reports(frame: pd.DataFrame, output_dir: Path = REPORTS_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    quality = quality_report(frame)
    overall = totals(frame)
    products = product_analysis(frame)
    divisions = aggregate_by(frame, "Division").sort_values("Gross Profit", ascending=False)
    regions = aggregate_by(frame, "Region").sort_values("Gross Profit", ascending=False)
    states = aggregate_by(frame, "State/Province").sort_values("Gross Profit", ascending=False)
    cities = aggregate_by(frame, "City").sort_values("Gross Profit", ascending=False)
    state_median_sales = states["Sales"].median()
    material_states = states[states["Sales"].ge(state_median_sales)]
    lowest_material_state = material_states.sort_values("Gross Margin %").iloc[0]
    sales_median = products["Sales"].median()
    profit_median = products["Gross Profit"].median()
    margin_q1 = products["Gross Margin %"].quantile(0.25)
    margin_q3 = products["Gross Margin %"].quantile(0.75)
    high_sales_low_margin = products[
        products["Sales"].ge(sales_median) & products["Gross Margin %"].lt(margin_q1)
    ].sort_values("Sales", ascending=False)
    cost_heavy = products.nlargest(5, "Cost")

    by_year = frame.assign(Year=frame["Order Date"].dt.year.astype("string"))
    annual = aggregate_by(by_year, "Year").sort_values("Year")
    monthly = frame.assign(Month=frame["Order Date"].dt.to_period("M").astype("string"))
    monthly = aggregate_by(monthly, "Month")
    monthly_high_sales = monthly.loc[monthly["Sales"].idxmax()]
    monthly_low_sales = monthly.loc[monthly["Sales"].idxmin()]
    monthly_high_margin = monthly.loc[monthly["Gross Margin %"].idxmax()]
    monthly_low_margin = monthly.loc[monthly["Gross Margin %"].idxmin()]
    monthly_margin_std = monthly["Gross Margin %"].std()
    revenue_sorted = products.sort_values("Sales", ascending=False).reset_index(drop=True)
    profit_sorted = products.sort_values("Gross Profit", ascending=False).reset_index(drop=True)

    quality_md = f"""# Data Quality and Cleaning Record

## Source and scope

- Source file: `data/Nassau Candy Distributor.csv` (provided Google Drive file).
- Shape: **{quality['rows']:,} rows × {quality['columns']} source columns**.
- All source rows are retained; **{quality['rows_retained']:,} rows** remain in the analyzed data.
- Parsed order-date range: **{frame['Order Date'].min():%Y-%m-%d} to {frame['Order Date'].max():%Y-%m-%d}**.
- Parsed ship-date range: **{frame['Ship Date'].min():%Y-%m-%d} to {frame['Ship Date'].max():%Y-%m-%d}**.
- Columns: {", ".join(quality['column_names'])}.
- Product labels: {quality['product_count']} distinct IDs/names; division labels: {", ".join(quality['division_labels'])}.

## Normalized field types

| Field | Type |
|---|---|
{chr(10).join(f"| {column} | {dtype} |" for column, dtype in quality['source_dtypes'].items())}

## Validation results

| Check | Result |
|---|---:|
| Missing source cells | {sum(quality['missing_values'].values()):,} |
| Exact duplicate records | {quality['exact_duplicates']:,} |
| Duplicate Row IDs | {quality['duplicate_row_ids']:,} |
| Invalid order / ship dates | {quality['invalid_dates']['Order Date']:,} / {quality['invalid_dates']['Ship Date']:,} |
| Zero / negative sales | {quality['zero_sales']:,} / {quality['negative_sales']:,} |
| Zero / negative cost | {quality['zero_cost']:,} / {quality['negative_cost']:,} |
| Negative gross profit | {quality['negative_gross_profit']:,} |
| Missing / nonpositive units | {quality['missing_units']:,} / {quality['invalid_or_nonpositive_units']:,} |
| Gross profit reconciliation mismatches | {quality['gross_profit_mismatches']:,} |
| Product ID/name conflicts | {quality['product_id_name_conflicts']:,} / {quality['product_name_id_conflicts']:,} |
| Whitespace-only label differences (Division / Region / Product ID / Product Name / State / City) | {quality['label_whitespace'].get('Division', 0):,} / {quality['label_whitespace'].get('Region', 0):,} / {quality['label_whitespace'].get('Product ID', 0):,} / {quality['label_whitespace'].get('Product Name', 0):,} / {quality['label_whitespace'].get('State/Province', 0):,} / {quality['label_whitespace'].get('City', 0):,} |
| IQR outliers: Sales / Cost / Gross Profit / Units | {quality['outliers_iqr']['Sales']:,} / {quality['outliers_iqr']['Cost']:,} / {quality['outliers_iqr']['Gross Profit']:,} / {quality['outliers_iqr']['Units']:,} |

## Cleaning and interpretation decisions

1. Required columns are checked; ID-like fields and postal codes are loaded as text so identifiers are not treated as quantities.
2. Numeric fields are parsed as numbers and dates are parsed strictly as **day-month-year** (`%d-%m-%Y`). Invalid parses are retained as missing and reported; none occur in this file.
3. Whitespace is trimmed from product/division/geographic labels. No labels were recoded, and no rows were removed.
4. Exact duplicate records and duplicate Row IDs were checked; neither was found.
5. `Gross Profit = Sales - Cost` is checked with a floating-point tolerance of 1e-9. All records reconcile.
6. IQR outliers use the 1.5×IQR rule on each row-level numeric field. They are review flags, not grounds for deletion.
7. Every parsed ship date is more than 365 days after its order date: gap range **{quality['date_gap_min']:,}–{quality['date_gap_max']:,} days**, median **{quality['date_gap_median']:,.0f} days**. The dates are preserved without correction; time-based analysis uses Order Date. Confirm these fields with the data owner before interpreting fulfillment timing.
8. Product IDs consistently map to product names, but one apparent prefix/division exception occurs in **{quality['division_prefix_mismatch_rows']} rows**: **{", ".join(f"{row['Product ID']} recorded in {row['Division']}" for row in quality['division_prefix_mismatches'])}**. Since the prefix convention is not documented, the recorded Division is kept unchanged.
9. No currency code is specified; financial values are reported in source units without assigning a currency.
"""
    (output_dir / "data_quality.md").write_text(quality_md, encoding="utf-8")

    product_table = markdown_table(
        products,
        ["Product ID", "Product Name", "Division", "Sales", "Cost", "Units", "Gross Profit", "Gross Margin %", "Profit per Unit", "Revenue Contribution %", "Profit Contribution %", "Profitability Segment", "Margin Risk"],
    )
    division_table = markdown_table(
        divisions,
        ["Division", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit", "Revenue Contribution %", "Profit Contribution %"],
    )
    region_table = markdown_table(
        regions,
        ["Region", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit", "Revenue Contribution %", "Profit Contribution %"],
    )
    annual_table = markdown_table(
        annual,
        ["Year", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %"],
    )
    monthly_table = markdown_table(
        monthly,
        ["Month", "Sales", "Cost", "Gross Profit", "Units", "Gross Margin %"],
    )
    state_table = markdown_table(
        states.nlargest(10, "Gross Profit"),
        ["State/Province", "Sales", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit"],
    )
    city_table = markdown_table(
        cities.head(10),
        ["City", "Sales", "Gross Profit", "Units", "Gross Margin %", "Profit per Unit"],
    )
    cost_table = markdown_table(
        cost_heavy,
        ["Product Name", "Sales", "Cost", "Gross Profit", "Gross Margin %"],
    )
    high_sales_low_margin_md = (
        markdown_table(
            high_sales_low_margin,
            ["Product Name", "Sales", "Cost", "Gross Profit", "Gross Margin %", "Profit per Unit"],
        )
        if not high_sales_low_margin.empty
        else "_No products meet both thresholds in this dataset._"
    )

    top_revenue_count = int(revenue_sorted["Sales"].cumsum().lt(overall["Sales"] * 0.8).sum() + 1)
    top_profit_count = int(
        profit_sorted["Gross Profit"].cumsum().lt(overall["Gross Profit"] * 0.8).sum() + 1
    )
    revenue_coverage = float(
        revenue_sorted["Sales"].cumsum().iloc[top_revenue_count - 1] / overall["Sales"] * 100
    )
    profit_coverage = float(
        profit_sorted["Gross Profit"].cumsum().iloc[top_profit_count - 1]
        / overall["Gross Profit"]
        * 100
    )
    annual_lines = ""
    if len(annual) >= 2:
        first, last = annual.iloc[0], annual.iloc[-1]
        sales_change = (last["Sales"] / first["Sales"] - 1) * 100
        profit_change = (last["Gross Profit"] / first["Gross Profit"] - 1) * 100
        annual_lines = (
            f"Between {first['Year']} and {last['Year']}, sales changed **{sales_change:+.1f}%** "
            f"and gross profit changed **{profit_change:+.1f}%**. This is a two-year comparison, "
            "not evidence of a long-term trend."
        )

    paper = f"""# Product Line Profitability & Margin Performance Analysis

## 1. Introduction

This report evaluates the provided Nassau Candy Distributor transaction dataset using sales, cost, gross profit, units, product, division, geography, and order date. The objective is to distinguish revenue scale from gross-profit and margin performance.

## 2. Business Problem

Revenue alone can conceal products that contribute comparatively little gross profit or carry weak gross margins. The analysis quantifies product and division contribution and flags concentration and cost/margin patterns. It does not infer operational causes that are absent from the data.

## 3. Objectives

- Establish data quality and preserve anomalous records transparently.
- Compute product/division/regional profitability KPIs.
- Compare products with median-based sales/profit segments and quartile-based margin risk.
- Measure product concentration in revenue and gross profit.
- Examine trends by order month and year.
- Assess whether factory attribution is possible with the supplied inputs.

## 4. Dataset Description

The CSV has **{quality['rows']:,} records**, **{quality['columns']} fields**, **{frame['Product ID'].nunique()} products**, **{frame['Division'].nunique()} divisions**, **{frame['Order ID'].nunique():,} distinct orders**, and **{frame['Customer ID'].nunique():,} distinct customer IDs**. The order-date range is {frame['Order Date'].min():%Y-%m-%d} to {frame['Order Date'].max():%Y-%m-%d}. The source does not specify currency.

## 5. Data Cleaning and Quality

All **{quality['rows']:,} rows** were retained. There are no missing source fields, exact duplicate records, duplicate Row IDs, invalid dates, nonpositive sales/cost/units, or negative gross profits. All rows satisfy `Gross Profit = Sales - Cost` within 1e-9. {quality['outliers_iqr']['Sales']} sales, {quality['outliers_iqr']['Cost']} cost, {quality['outliers_iqr']['Gross Profit']} gross-profit, and {quality['outliers_iqr']['Units']} unit observations are beyond 1.5×IQR and are retained for review.

Dates were parsed as day-month-year. Every order-to-ship gap is **{quality['date_gap_min']:,}–{quality['date_gap_max']:,} days** (median {quality['date_gap_median']:,.0f}), an important anomaly that should be validated with the data owner. No date was adjusted. Product ID/name assignments are stable. One apparent ID-prefix versus Division exception (`OTH-FIZ-56000`, recorded in Sugar) is preserved because the prefix convention is undocumented. Full counts and decisions are in [data_quality.md](./data_quality.md).

## 6. Exploratory Data Analysis

There are **{overall['Product Count']} distinct products** across three divisions. Product records are highly uneven: the five leading Wonka Bar SKUs represent nearly all sales/profit compared with the remaining small-format products. Geography covers {frame['Region'].nunique()} regions, {frame['State/Province'].nunique()} states/provinces, and {frame['City'].nunique()} cities. No coordinates are provided for regions/states/cities, so no geographic map or spatial inference is made.

## 7. KPI Methodology

- **Gross margin %** = total gross profit ÷ total sales × 100.
- **Profit per unit** = total gross profit ÷ total units.
- **Revenue contribution %** = entity sales ÷ filtered total sales × 100.
- **Profit contribution %** = entity gross profit ÷ filtered total gross profit × 100.
- Product quadrants use the median of product total sales and median of product total gross profit in the analysis scope. Values equal to the median are in the high band.
- Product margin risk uses quartiles of aggregate product gross margin: below Q1 is Low Margin / High Risk; Q1 to below Q3 is Medium Margin / Monitor; Q3 and above is High Margin / Low Risk; any negative margin is Negative Margin / Critical. Thresholds are recomputed for the selected scope.
- Pareto count is the minimum number of products whose descending cumulative contribution reaches or exceeds 80%.

## 8. Product Profitability

Overall totals are **{fmt(overall['Sales'])} sales**, **{fmt(overall['Cost'])} cost**, **{fmt(overall['Gross Profit'])} gross profit**, **{fmt(overall['Units'], 0)} units**, **{overall['Gross Margin %']:.2f}% gross margin**, and **{fmt(overall['Profit per Unit'])} profit per unit**.

The median product sales threshold is {fmt(sales_median)}, the median product gross-profit threshold is {fmt(profit_median)}, and the product margin quartiles are Q1 {margin_q1:.2f}% / Q3 {margin_q3:.2f}%. Top gross-profit product is **{products.iloc[0]['Product Name']}** with {fmt(products.iloc[0]['Gross Profit'])} gross profit ({products.iloc[0]['Profit Contribution %']:.2f}% of total).

**Median-based segments**: {", ".join(f"{name}: {int(count)}" for name, count in products["Profitability Segment"].value_counts().sort_index().items())}.

### Product KPI table

{product_table}

## 9. Division Performance

{division_table}

**Chocolate** is the largest division by both sales and gross profit, contributing {divisions.iloc[0]['Revenue Contribution %']:.2f}% of revenue and {divisions.iloc[0]['Profit Contribution %']:.2f}% of gross profit at a {divisions.iloc[0]['Gross Margin %']:.2f}% gross margin. **{divisions.sort_values('Gross Margin %').iloc[0]['Division']}** has the lowest division margin at {divisions['Gross Margin %'].min():.2f}%; division comparisons are weighted ratios of totals, not averages of row margins.

## 10. Pareto Analysis

- **Revenue:** {top_revenue_count} of {len(products)} products ({top_revenue_count / len(products) * 100:.1f}%) produce {revenue_coverage:.2f}% of revenue by the first crossing of 80%.
- **Gross profit:** {top_profit_count} of {len(products)} products ({top_profit_count / len(products) * 100:.1f}%) produce {profit_coverage:.2f}% of gross profit.

This indicates concentration in the analyzed product set. It is a portfolio exposure indicator, not proof of supply, demand, or customer dependency.

## 11. Cost and Margin Diagnostics

Products with sales at/above the product median ({fmt(sales_median)}) and margin below the product 25th percentile ({margin_q1:.2f}%) are classified high-sales/low-margin:

{high_sales_low_margin_md}

The five products with the largest aggregate costs are shown below. High absolute cost is not necessarily excessive cost; the dataset lacks product-level cost standards, input prices, and production benchmarks.

{cost_table}

Across product-level aggregate margins, {int((products['Gross Margin %'] < 0).sum())} products have negative margin. The risk categories and their thresholds are included in the product KPI table.

## 12. Regional Analysis

{region_table}

By total gross profit, {regions.iloc[0]['Region']} is highest ({fmt(regions.iloc[0]['Gross Profit'])}); by gross margin, {regions.sort_values('Gross Margin %', ascending=False).iloc[0]['Region']} is highest ({regions['Gross Margin %'].max():.2f}%). The lowest-margin region is {regions.sort_values('Gross Margin %').iloc[0]['Region']} ({regions['Gross Margin %'].min():.2f}%).

Top states by gross profit:

{state_table}

Among states with sales at or above the median state sales ({fmt(state_median_sales)}), {lowest_material_state['State/Province']} has the lowest gross margin ({lowest_material_state['Gross Margin %']:.2f}%). These comparisons are descriptive and do not support logistics or operational causality.

Top cities by gross profit:

{city_table}

## 13. Factory Analysis

The project supplied five factory coordinates but no product-to-factory mapping. Factory-level sales, cost, gross profit, margin, product counts, and filtered factory attribution therefore **cannot be calculated without inventing assignments**. The dashboard shows the supplied coordinates as an unassigned location map. Provide a mapping keyed by Product ID (preferably effective-dated if assignments change) to enable factory analysis.

{markdown_table(FACTORY_COORDINATES, ['Factory', 'Latitude', 'Longitude'])}

## 14. Time-Based Analysis

Order Date is used because every ship date is 904 days or more after its corresponding order date. No correction is inferred.

{annual_table}

{annual_lines}

Monthly order-date totals and weighted margins:

{monthly_table}

Highest monthly sales occurred in **{monthly_high_sales['Month']}** ({fmt(monthly_high_sales['Sales'])}); lowest occurred in **{monthly_low_sales['Month']}** ({fmt(monthly_low_sales['Sales'])}). Monthly weighted margin ranged from **{monthly_low_margin['Gross Margin %']:.2f}%** ({monthly_low_margin['Month']}) to **{monthly_high_margin['Gross Margin %']:.2f}%** ({monthly_high_margin['Month']}), with a monthly margin standard deviation of {monthly_margin_std:.2f} percentage points. With two years of order dates and anomalous ship dates, these patterns are descriptive only; they do not establish seasonality.

## 15. Key Findings

1. Total gross margin is {overall['Gross Margin %']:.2f}% and gross profit is {fmt(overall['Gross Profit'])} in unspecified source currency units.
2. {top_profit_count} products contribute {profit_coverage:.2f}% of gross profit; product profit concentration is high.
3. Chocolate contributes {divisions.iloc[0]['Profit Contribution %']:.2f}% of gross profit, while Other has the lowest divisional margin ({divisions.sort_values('Gross Margin %').iloc[0]['Gross Margin %']:.2f}%).
4. The high-sales/low-margin test flags {len(high_sales_low_margin)} product(s), using a median-sales / Q1-margin definition.
5. Shipment dates have unusually long intervals relative to order dates; all records are retained pending source validation.
6. Factory profitability is unmeasurable until product assignments are provided.

## 16. Business Recommendations

These are recommendations to investigate, not claims that an action will improve results:

1. **Review pricing and cost basis** for each high-sales/low-margin SKU, comparing contractual price, discount, and current cost evidence before repricing.
2. **Investigate the Other division** and the product(s) in its low-margin tail. Separate mix and price effects from cost effects before changing assortment.
3. **Track concentration** in the top profit-generating products. Scenario-test a disruption to leading SKUs and identify evidence-based diversification options.
4. **Do not treat high absolute cost as excess cost.** Compare cost-heavy products against their own historical/vendor/production standards before proposing optimization.
5. **Validate order and ship date fields** with the source owner before using shipping intervals or calendar-based operating decisions.
6. **Obtain an authoritative Product ID-to-factory mapping** before evaluating factory profitability or manufacturing allocation.
7. **Preserve productive products pending review.** The leading Wonka Bar SKUs contribute the bulk of measured sales and profit; any portfolio changes should consider the economics and customer context not present here.

## 17. Limitations

- The source provides gross profit and cost but not currency, price lists, discounts, returns, overhead, labor, capacity, or product cost standards.
- Product mapping to factories was not supplied; no factory financial findings are available.
- Order-to-ship date intervals are anomalous and may reflect a source issue. Dates were not repaired.
- Only two order-date years are present; seasonal statements are not robust.
- State and city names have no supplied coordinates; maps are not constructed.
- Aggregate margin is a weighted ratio and does not capture variability by customer/order beyond the dashboard's descriptive product/record views.
- The file reflects recorded transactions and does not establish causal effects of pricing, costs, region, or operations.

## 18. Conclusion

The provided data supports a reproducible profitability assessment: sales total {fmt(overall['Sales'])}, gross profit {fmt(overall['Gross Profit'])}, weighted gross margin {overall['Gross Margin %']:.2f}%, and five products reach 80% of gross profit. Concentration, the comparatively low-margin Other division, and the very low product margin(s) merit targeted validation. Data anomalies and the missing factory mapping limit calendar and factory conclusions. The accompanying dashboard and scripts recalculate measures from the CSV and disclose these constraints.
"""
    (output_dir / "research_paper.md").write_text(paper, encoding="utf-8")

    low_margin_products = products.sort_values("Gross Margin %").head(3)
    exec_summary = f"""# Executive Summary

## Performance

The provided file contains {quality['rows']:,} transaction rows for {overall['Product Count']} products. Recorded sales total **{fmt(overall['Sales'])}**, cost **{fmt(overall['Cost'])}**, gross profit **{fmt(overall['Gross Profit'])}**, and weighted gross margin **{overall['Gross Margin %']:.2f}%**. Currency is unspecified. Gross profit reconciles to sales less cost for all rows.

## What drives profit and where is risk?

- **Top profit SKU:** {products.iloc[0]['Product Name']} — {fmt(products.iloc[0]['Gross Profit'])} gross profit ({products.iloc[0]['Profit Contribution %']:.2f}% share).
- **Division:** Chocolate provides {divisions.iloc[0]['Profit Contribution %']:.2f}% of profit at {divisions.iloc[0]['Gross Margin %']:.2f}% margin. Other has the lowest divisional margin ({divisions.sort_values('Gross Margin %').iloc[0]['Gross Margin %']:.2f}%).
- **Concentration:** {top_profit_count} of {len(products)} products ({top_profit_count / len(products) * 100:.1f}%) produce {profit_coverage:.2f}% of gross profit.
- **High sales / low margin:** {", ".join(high_sales_low_margin["Product Name"].tolist()) if not high_sales_low_margin.empty else "none under the median-sales / Q1-margin thresholds"}.
- **Lowest product margins:** {", ".join(f"{row['Product Name']} ({row['Gross Margin %']:.2f}%)" for _, row in low_margin_products.iterrows())}.

## Management actions to consider

1. Review price/discount and cost detail for high-sales, low-margin products before repricing.
2. Diagnose product mix and cost/price drivers in Other; do not assume the cause from this dataset.
3. Monitor exposure to the small group of products producing most gross profit.
4. Benchmark high absolute product costs against approved cost standards before targeting savings.
5. Verify the anomalous order/ship dates with the source owner.
6. Supply an authoritative product-to-factory mapping before judging factory performance.

## Caveats

All {quality['date_anomalies']:,} order-to-ship gaps exceed one year (range {quality['date_gap_min']}–{quality['date_gap_max']} days). No rows were deleted or dates corrected. Factory profitability is unavailable because the product-to-factory mapping is missing. Geographic findings are descriptive and support no logistics claims.

See [the research paper](./research_paper.md) and [the data-quality record](./data_quality.md) for methodology, tables, and limitations.
"""
    (output_dir / "executive_summary.md").write_text(exec_summary, encoding="utf-8")


def main() -> None:
    frame = load_data(DATA_PATH)
    generate_reports(frame)
    print(f"Reports generated in {REPORTS_DIR}")


if __name__ == "__main__":
    main()
