# Data Quality and Cleaning Record

## Source and scope

- Source file: `data/Nassau Candy Distributor.csv` (provided Google Drive file).
- Shape: **10,194 rows × 18 source columns**.
- All source rows are retained; **10,194 rows** remain in the analyzed data.
- Parsed order-date range: **2024-01-02 to 2025-12-31**.
- Parsed ship-date range: **2026-06-30 to 2030-06-28**.
- Columns: Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Country/Region, City, State/Province, Postal Code, Division, Region, Product ID, Product Name, Sales, Units, Gross Profit, Cost.
- Product labels: 15 distinct IDs/names; division labels: Chocolate, Other, Sugar.

## Normalized field types

| Field | Type |
|---|---|
| Row ID | string |
| Order ID | string |
| Order Date | datetime64[us] |
| Ship Date | datetime64[us] |
| Ship Mode | str |
| Customer ID | string |
| Country/Region | str |
| City | string |
| State/Province | string |
| Postal Code | string |
| Division | string |
| Region | string |
| Product ID | string |
| Product Name | string |
| Sales | float64 |
| Units | int64 |
| Gross Profit | float64 |
| Cost | float64 |

## Validation results

| Check | Result |
|---|---:|
| Missing source cells | 0 |
| Exact duplicate records | 0 |
| Duplicate Row IDs | 0 |
| Invalid order / ship dates | 0 / 0 |
| Zero / negative sales | 0 / 0 |
| Zero / negative cost | 0 / 0 |
| Negative gross profit | 0 |
| Missing / nonpositive units | 0 / 0 |
| Gross profit reconciliation mismatches | 0 |
| Product ID/name conflicts | 0 / 0 |
| Whitespace-only label differences (Division / Region / Product ID / Product Name / State / City) | 0 / 0 / 0 / 0 / 0 / 0 |
| IQR outliers: Sales / Cost / Gross Profit / Units | 245 / 397 / 217 / 175 |

## Cleaning and interpretation decisions

1. Required columns are checked; ID-like fields and postal codes are loaded as text so identifiers are not treated as quantities.
2. Numeric fields are parsed as numbers and dates are parsed strictly as **day-month-year** (`%d-%m-%Y`). Invalid parses are retained as missing and reported; none occur in this file.
3. Whitespace is trimmed from product/division/geographic labels. No labels were recoded, and no rows were removed.
4. Exact duplicate records and duplicate Row IDs were checked; neither was found.
5. `Gross Profit = Sales - Cost` is checked with a floating-point tolerance of 1e-9. All records reconcile.
6. IQR outliers use the 1.5×IQR rule on each row-level numeric field. They are review flags, not grounds for deletion.
7. Every parsed ship date is more than 365 days after its order date: gap range **904–1,642 days**, median **1,274 days**. The dates are preserved without correction; time-based analysis uses Order Date. Confirm these fields with the data owner before interpreting fulfillment timing.
8. Product IDs consistently map to product names, but one apparent prefix/division exception occurs in **6 rows**: **OTH-FIZ-56000 recorded in Sugar**. Since the prefix convention is not documented, the recorded Division is kept unchanged.
9. No currency code is specified; financial values are reported in source units without assigning a currency.
