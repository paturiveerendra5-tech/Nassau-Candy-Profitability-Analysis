# Product Line Profitability & Margin Performance Analysis

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

The CSV has **10,194 records**, **18 fields**, **15 products**, **3 divisions**, **8,549 distinct orders**, and **5,044 distinct customer IDs**. The order-date range is 2024-01-02 to 2025-12-31. The source does not specify currency.

## 5. Data Cleaning and Quality

All **10,194 rows** were retained. There are no missing source fields, exact duplicate records, duplicate Row IDs, invalid dates, nonpositive sales/cost/units, or negative gross profits. All rows satisfy `Gross Profit = Sales - Cost` within 1e-9. 245 sales, 397 cost, 217 gross-profit, and 175 unit observations are beyond 1.5×IQR and are retained for review.

Dates were parsed as day-month-year. Every order-to-ship gap is **904–1,642 days** (median 1,274), an important anomaly that should be validated with the data owner. No date was adjusted. Product ID/name assignments are stable. One apparent ID-prefix versus Division exception (`OTH-FIZ-56000`, recorded in Sugar) is preserved because the prefix convention is undocumented. Full counts and decisions are in [data_quality.md](./data_quality.md).

## 6. Exploratory Data Analysis

There are **15 distinct products** across three divisions. Product records are highly uneven: the five leading Wonka Bar SKUs represent nearly all sales/profit compared with the remaining small-format products. Geography covers 4 regions, 59 states/provinces, and 542 cities. No coordinates are provided for regions/states/cities, so no geographic map or spatial inference is made.

## 7. KPI Methodology

- **Gross margin %** = total gross profit ÷ total sales × 100.
- **Profit per unit** = total gross profit ÷ total units.
- **Revenue contribution %** = entity sales ÷ filtered total sales × 100.
- **Profit contribution %** = entity gross profit ÷ filtered total gross profit × 100.
- Product quadrants use the median of product total sales and median of product total gross profit in the analysis scope. Values equal to the median are in the high band.
- Product margin risk uses quartiles of aggregate product gross margin: below Q1 is Low Margin / High Risk; Q1 to below Q3 is Medium Margin / Monitor; Q3 and above is High Margin / Low Risk; any negative margin is Negative Margin / Critical. Thresholds are recomputed for the selected scope.
- Pareto count is the minimum number of products whose descending cumulative contribution reaches or exceeds 80%.

## 8. Product Profitability

Overall totals are **141,783.63 sales**, **48,340.83 cost**, **93,442.80 gross profit**, **38,654 units**, **65.91% gross margin**, and **2.42 profit per unit**.

The median product sales threshold is 597.50, the median product gross-profit threshold is 104.00, and the product margin quartiles are Q1 48.33% / Q3 68.06%. Top gross-profit product is **Wonka Bar -Scrumdiddlyumptious** with 19,357.50 gross profit (20.72% of total).

**Median-based segments**: High sales / High profit: 7, High sales / Low profit: 1, Low sales / High profit: 1, Low sales / Low profit: 6.

### Product KPI table

| Product ID | Product Name | Division | Sales | Cost | Units | Gross Profit | Gross Margin % | Profit per Unit | Revenue Contribution % | Profit Contribution % | Profitability Segment | Margin Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHO-SCR-58000 | Wonka Bar -Scrumdiddlyumptious | Chocolate | 27,874.80 | 8,517.30 | 7,743 | 19,357.50 | 69.44% | 2.50 | 19.66% | 20.72% | High sales / High profit | High Margin / Low Risk |
| CHO-TRI-54000 | Wonka Bar - Triple Dazzle Caramel | Chocolate | 28,485.00 | 9,874.80 | 7,596 | 18,610.20 | 65.33% | 2.45 | 20.09% | 19.92% | High sales / High profit | Medium Margin / Monitor |
| CHO-MIL-31000 | Wonka Bar - Milk Chocolate | Chocolate | 26,867.75 | 9,424.38 | 8,267 | 17,443.37 | 64.92% | 2.11 | 18.95% | 18.67% | High sales / High profit | Medium Margin / Monitor |
| CHO-NUT-13000 | Wonka Bar - Nutty Crunch Surprise | Chocolate | 23,574.95 | 6,755.00 | 6,755 | 16,819.95 | 71.35% | 2.49 | 16.63% | 18.00% | High sales / High profit | High Margin / Low Risk |
| CHO-FUD-51000 | Wonka Bar - Fudge Mallows | Chocolate | 24,890.40 | 8,296.80 | 6,914 | 16,593.60 | 66.67% | 2.40 | 17.56% | 17.76% | High sales / High profit | Medium Margin / Monitor |
| OTH-LIC-15000 | Lickable Wallpaper | Other | 7,860.00 | 3,930.00 | 393 | 3,930.00 | 50.00% | 10.00 | 5.54% | 4.21% | High sales / High profit | Medium Margin / Monitor |
| OTH-GUM-21000 | Wonka Gum | Other | 597.50 | 286.80 | 478 | 310.70 | 52.00% | 0.65 | 0.42% | 0.33% | High sales / High profit | Medium Margin / Monitor |
| SUG-EVE-47000 | Everlasting Gobstopper | Sugar | 130.00 | 26.00 | 13 | 104.00 | 80.00% | 8.00 | 0.09% | 0.11% | Low sales / High profit | High Margin / Low Risk |
| OTH-KAZ-38000 | Kazookles | Other | 1,205.75 | 1,113.00 | 371 | 92.75 | 7.69% | 0.25 | 0.85% | 0.10% | High sales / Low profit | Low Margin / High Risk |
| SUG-HAI-55000 | Hair Toffee | Sugar | 76.50 | 17.00 | 17 | 59.50 | 77.78% | 3.50 | 0.05% | 0.06% | Low sales / Low profit | High Margin / Low Risk |
| OTH-FIZ-56000 | Fizzy Lifting Drinks | Sugar | 78.75 | 31.50 | 21 | 47.25 | 60.00% | 2.25 | 0.06% | 0.05% | Low sales / Low profit | Medium Margin / Monitor |
| SUG-LAF-25000 | Laffy Taffy | Sugar | 53.73 | 20.25 | 27 | 33.48 | 62.31% | 1.24 | 0.04% | 0.04% | Low sales / Low profit | Medium Margin / Monitor |
| SUG-SWE-91000 | SweeTARTS | Sugar | 61.50 | 32.80 | 41 | 28.70 | 46.67% | 0.70 | 0.04% | 0.03% | Low sales / Low profit | Low Margin / High Risk |
| SUG-NER-92000 | Nerds | Sugar | 15.00 | 8.00 | 10 | 7.00 | 46.67% | 0.70 | 0.01% | 0.01% | Low sales / Low profit | Low Margin / High Risk |
| SUG-FUN-75000 | Fun Dip | Sugar | 12.00 | 7.20 | 8 | 4.80 | 40.00% | 0.60 | 0.01% | 0.01% | Low sales / Low profit | Low Margin / High Risk |

## 9. Division Performance

| Division | Sales | Cost | Gross Profit | Units | Gross Margin % | Profit per Unit | Revenue Contribution % | Profit Contribution % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chocolate | 131,692.90 | 42,868.28 | 88,824.62 | 37,275 | 67.45% | 2.38 | 92.88% | 95.06% |
| Other | 9,663.25 | 5,329.80 | 4,333.45 | 1,242 | 44.84% | 3.49 | 6.82% | 4.64% |
| Sugar | 427.48 | 142.75 | 284.73 | 137 | 66.61% | 2.08 | 0.30% | 0.30% |

**Chocolate** is the largest division by both sales and gross profit, contributing 92.88% of revenue and 95.06% of gross profit at a 67.45% gross margin. **Other** has the lowest division margin at 44.84%; division comparisons are weighted ratios of totals, not averages of row margins.

## 10. Pareto Analysis

- **Revenue:** 5 of 15 products (33.3%) produce 92.88% of revenue by the first crossing of 80%.
- **Gross profit:** 5 of 15 products (33.3%) produce 95.06% of gross profit.

This indicates concentration in the analyzed product set. It is a portfolio exposure indicator, not proof of supply, demand, or customer dependency.

## 11. Cost and Margin Diagnostics

Products with sales at/above the product median (597.50) and margin below the product 25th percentile (48.33%) are classified high-sales/low-margin:

| Product Name | Sales | Cost | Gross Profit | Gross Margin % | Profit per Unit |
| --- | --- | --- | --- | --- | --- |
| Kazookles | 1,205.75 | 1,113.00 | 92.75 | 7.69% | 0.25 |

The five products with the largest aggregate costs are shown below. High absolute cost is not necessarily excessive cost; the dataset lacks product-level cost standards, input prices, and production benchmarks.

| Product Name | Sales | Cost | Gross Profit | Gross Margin % |
| --- | --- | --- | --- | --- |
| Wonka Bar - Triple Dazzle Caramel | 28,485.00 | 9,874.80 | 18,610.20 | 65.33% |
| Wonka Bar - Milk Chocolate | 26,867.75 | 9,424.38 | 17,443.37 | 64.92% |
| Wonka Bar -Scrumdiddlyumptious | 27,874.80 | 8,517.30 | 19,357.50 | 69.44% |
| Wonka Bar - Fudge Mallows | 24,890.40 | 8,296.80 | 16,593.60 | 66.67% |
| Wonka Bar - Nutty Crunch Surprise | 23,574.95 | 6,755.00 | 16,819.95 | 71.35% |

Across product-level aggregate margins, 0 products have negative margin. The risk categories and their thresholds are included in the product KPI table.

## 12. Regional Analysis

| Region | Sales | Cost | Gross Profit | Units | Gross Margin % | Profit per Unit | Revenue Contribution % | Profit Contribution % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pacific | 46,301.53 | 15,815.59 | 30,485.94 | 12,466 | 65.84% | 2.45 | 32.66% | 32.63% |
| Atlantic | 41,197.24 | 14,223.54 | 26,973.70 | 11,159 | 65.47% | 2.42 | 29.06% | 28.87% |
| Interior | 32,037.60 | 10,755.11 | 21,282.49 | 8,820 | 66.43% | 2.41 | 22.60% | 22.78% |
| Gulf | 22,247.26 | 7,546.59 | 14,700.67 | 6,209 | 66.08% | 2.37 | 15.69% | 15.73% |

By total gross profit, Pacific is highest (30,485.94); by gross margin, Interior is highest (66.43%). The lowest-margin region is Atlantic (65.47%).

Top states by gross profit:

| State/Province | Sales | Gross Profit | Units | Gross Margin % | Profit per Unit |
| --- | --- | --- | --- | --- | --- |
| California | 27,917.40 | 18,479.42 | 7,667 | 66.19% | 2.41 |
| New York | 15,541.03 | 10,222.44 | 4,224 | 65.78% | 2.42 |
| Texas | 13,416.09 | 8,909.53 | 3,724 | 66.41% | 2.39 |
| Pennsylvania | 8,027.03 | 5,225.47 | 2,153 | 65.10% | 2.43 |
| Washington | 6,921.15 | 4,566.64 | 1,883 | 65.98% | 2.43 |
| Illinois | 6,898.96 | 4,557.68 | 1,845 | 66.06% | 2.47 |
| Ohio | 6,768.95 | 4,413.03 | 1,759 | 65.20% | 2.51 |
| Florida | 4,804.02 | 3,207.11 | 1,379 | 66.76% | 2.33 |
| North Carolina | 3,450.86 | 2,331.16 | 983 | 67.55% | 2.37 |
| Arizona | 3,587.55 | 2,290.11 | 862 | 63.83% | 2.66 |

Among states with sales at or above the median state sales (856.41), Alabama has the lowest gross margin (62.52%). These comparisons are descriptive and do not support logistics or operational causality.

Top cities by gross profit:

| City | Sales | Gross Profit | Units | Gross Margin % | Profit per Unit |
| --- | --- | --- | --- | --- | --- |
| New York City | 12,514.90 | 8,240.51 | 3,417 | 65.85% | 2.41 |
| Los Angeles | 10,408.75 | 6,898.61 | 2,879 | 66.28% | 2.40 |
| Philadelphia | 7,415.52 | 4,813.82 | 1,981 | 64.92% | 2.43 |
| San Francisco | 7,018.61 | 4,650.77 | 1,935 | 66.26% | 2.40 |
| Seattle | 5,893.39 | 3,880.68 | 1,590 | 65.85% | 2.44 |
| Houston | 5,429.41 | 3,547.43 | 1,466 | 65.34% | 2.42 |
| Chicago | 4,263.92 | 2,800.58 | 1,132 | 65.68% | 2.47 |
| Columbus | 3,357.39 | 2,159.03 | 836 | 64.31% | 2.58 |
| San Diego | 2,348.88 | 1,567.52 | 670 | 66.73% | 2.34 |
| Springfield | 2,375.00 | 1,540.12 | 649 | 64.85% | 2.37 |

## 13. Factory Analysis

The project supplied five factory coordinates but no product-to-factory mapping. Factory-level sales, cost, gross profit, margin, product counts, and filtered factory attribution therefore **cannot be calculated without inventing assignments**. The dashboard shows the supplied coordinates as an unassigned location map. Provide a mapping keyed by Product ID (preferably effective-dated if assignments change) to enable factory analysis.

| Factory | Latitude | Longitude |
| --- | --- | --- |
| Lot's O' Nuts | 32.88 | -111.77 |
| Wicked Choccy's | 32.08 | -81.09 |
| Sugar Shack | 48.12 | -96.18 |
| Secret Factory | 41.45 | -90.57 |
| The Other Factory | 35.12 | -89.97 |

## 14. Time-Based Analysis

Order Date is used because every ship date is 904 days or more after its corresponding order date. No correction is inferred.

| Year | Sales | Cost | Gross Profit | Units | Gross Margin % |
| --- | --- | --- | --- | --- | --- |
| 2024 | 57,956.20 | 19,804.77 | 38,151.43 | 15,899 | 65.83% |
| 2025 | 83,827.43 | 28,536.06 | 55,291.37 | 22,755 | 65.96% |

Between 2024 and 2025, sales changed **+44.6%** and gross profit changed **+44.9%**. This is a two-year comparison, not evidence of a long-term trend.

Monthly order-date totals and weighted margins:

| Month | Sales | Cost | Gross Profit | Units | Gross Margin % |
| --- | --- | --- | --- | --- | --- |
| 2024-01 | 2,093.90 | 727.76 | 1,366.14 | 566 | 65.24% |
| 2024-02 | 1,379.87 | 471.28 | 908.59 | 398 | 65.85% |
| 2024-03 | 4,138.90 | 1,467.74 | 2,671.16 | 1,125 | 64.54% |
| 2024-04 | 3,988.22 | 1,375.41 | 2,612.81 | 1,079 | 65.51% |
| 2024-05 | 3,951.52 | 1,336.08 | 2,615.44 | 1,099 | 66.19% |
| 2024-06 | 3,518.76 | 1,188.04 | 2,330.72 | 1,010 | 66.24% |
| 2024-07 | 3,865.38 | 1,300.12 | 2,565.26 | 1,107 | 66.37% |
| 2024-08 | 4,477.65 | 1,531.78 | 2,945.87 | 1,227 | 65.79% |
| 2024-09 | 7,912.10 | 2,705.40 | 5,206.70 | 2,105 | 65.81% |
| 2024-10 | 4,815.98 | 1,696.52 | 3,119.46 | 1,237 | 64.77% |
| 2024-11 | 8,917.71 | 2,970.40 | 5,947.31 | 2,545 | 66.69% |
| 2024-12 | 8,896.21 | 3,034.24 | 5,861.97 | 2,401 | 65.89% |
| 2025-01 | 3,489.10 | 1,160.29 | 2,328.81 | 1,003 | 66.75% |
| 2025-02 | 2,553.65 | 876.10 | 1,677.55 | 669 | 65.69% |
| 2025-03 | 5,423.24 | 1,834.86 | 3,588.38 | 1,506 | 66.17% |
| 2025-04 | 4,922.44 | 1,656.34 | 3,266.10 | 1,376 | 66.35% |
| 2025-05 | 6,555.68 | 2,226.58 | 4,329.10 | 1,776 | 66.04% |
| 2025-06 | 6,214.93 | 2,091.04 | 4,123.89 | 1,702 | 66.35% |
| 2025-07 | 6,057.67 | 2,074.62 | 3,983.05 | 1,630 | 65.75% |
| 2025-08 | 5,740.10 | 1,944.70 | 3,795.40 | 1,603 | 66.12% |
| 2025-09 | 11,457.60 | 3,958.77 | 7,498.83 | 3,010 | 65.45% |
| 2025-10 | 7,345.89 | 2,512.24 | 4,833.65 | 1,936 | 65.80% |
| 2025-11 | 11,728.86 | 3,978.20 | 7,750.66 | 3,248 | 66.08% |
| 2025-12 | 12,338.27 | 4,222.32 | 8,115.95 | 3,296 | 65.78% |

Highest monthly sales occurred in **2025-12** (12,338.27); lowest occurred in **2024-02** (1,379.87). Monthly weighted margin ranged from **64.54%** (2024-03) to **66.75%** (2025-01), with a monthly margin standard deviation of 0.53 percentage points. With two years of order dates and anomalous ship dates, these patterns are descriptive only; they do not establish seasonality.

## 15. Key Findings

1. Total gross margin is 65.91% and gross profit is 93,442.80 in unspecified source currency units.
2. 5 products contribute 95.06% of gross profit; product profit concentration is high.
3. Chocolate contributes 95.06% of gross profit, while Other has the lowest divisional margin (44.84%).
4. The high-sales/low-margin test flags 1 product(s), using a median-sales / Q1-margin definition.
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

The provided data supports a reproducible profitability assessment: sales total 141,783.63, gross profit 93,442.80, weighted gross margin 65.91%, and five products reach 80% of gross profit. Concentration, the comparatively low-margin Other division, and the very low product margin(s) merit targeted validation. Data anomalies and the missing factory mapping limit calendar and factory conclusions. The accompanying dashboard and scripts recalculate measures from the CSV and disclose these constraints.
