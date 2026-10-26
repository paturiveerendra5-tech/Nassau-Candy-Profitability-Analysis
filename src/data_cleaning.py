from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Country/Region",
    "City",
    "State/Province",
    "Postal Code",
    "Division",
    "Region",
    "Product ID",
    "Product Name",
    "Sales",
    "Units",
    "Gross Profit",
    "Cost",
]
NUMERIC_COLUMNS = ["Sales", "Units", "Gross Profit", "Cost"]
IDENTIFIER_COLUMNS = [
    "Row ID",
    "Order ID",
    "Customer ID",
    "Postal Code",
    "Product ID",
]
FACTORY_COORDINATES = pd.DataFrame(
    [
        ("Lot's O' Nuts", 32.881893, -111.768036),
        ("Wicked Choccy's", 32.076176, -81.088371),
        ("Sugar Shack", 48.119140, -96.181150),
        ("Secret Factory", 41.446333, -90.565487),
        ("The Other Factory", 35.117500, -89.971107),
    ],
    columns=["Factory", "Latitude", "Longitude"],
)


def load_data(path: str | Path) -> pd.DataFrame:
    """Load and minimally normalize the source without dropping any records."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Dataset not found: {source}")

    frame = pd.read_csv(source, dtype={column: "string" for column in IDENTIFIER_COLUMNS})
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    frame = frame[REQUIRED_COLUMNS].copy()
    label_whitespace: dict[str, int] = {}
    for column in ["Division", "Region", "Product ID", "Product Name", "State/Province", "City"]:
        values = frame[column].astype("string")
        stripped = values.str.strip()
        label_whitespace[column] = int(values.ne(stripped).sum())
        frame[column] = stripped
    frame.attrs["label_whitespace"] = label_whitespace

    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    for column in ["Order Date", "Ship Date"]:
        frame[column] = pd.to_datetime(
            frame[column].astype("string").str.strip(),
            format="%d-%m-%Y",
            errors="coerce",
        )

    frame["Date Gap Days"] = (frame["Ship Date"] - frame["Order Date"]).dt.days
    frame["Date Anomaly"] = frame["Date Gap Days"].lt(0) | frame["Date Gap Days"].gt(365)
    frame["Gross Profit Reconciles"] = np.isclose(
        frame["Gross Profit"],
        frame["Sales"] - frame["Cost"],
        rtol=0,
        atol=1e-9,
        equal_nan=False,
    )
    return frame


def quality_report(frame: pd.DataFrame) -> dict[str, object]:
    """Return transparent validation counts; anomalous records remain in the data."""
    numeric = frame[NUMERIC_COLUMNS]
    outliers: dict[str, int] = {}
    for column in NUMERIC_COLUMNS:
        values = numeric[column].dropna()
        q1, q3 = values.quantile([0.25, 0.75])
        spread = q3 - q1
        outliers[column] = int(((values < q1 - 1.5 * spread) | (values > q3 + 1.5 * spread)).sum())

    division_prefix = {
        "Chocolate": "CHO",
        "Other": "OTH",
        "Sugar": "SUG",
    }
    prefix_mismatch = frame[
        frame.apply(
            lambda row: row["Product ID"].split("-", maxsplit=1)[0]
            != division_prefix.get(row["Division"], ""),
            axis=1,
        )
    ]
    gap = frame["Date Gap Days"].dropna()
    return {
        "rows": len(frame),
        "columns": len(REQUIRED_COLUMNS),
        "column_names": REQUIRED_COLUMNS,
        "source_dtypes": frame[REQUIRED_COLUMNS].dtypes.astype(str).to_dict(),
        "label_whitespace": frame.attrs.get("label_whitespace", {}),
        "product_count": int(frame["Product ID"].nunique()),
        "product_names": sorted(frame["Product Name"].dropna().unique().tolist()),
        "division_labels": sorted(frame["Division"].dropna().unique().tolist()),
        "missing_values": frame[REQUIRED_COLUMNS].isna().sum().to_dict(),
        "exact_duplicates": int(frame[REQUIRED_COLUMNS].duplicated().sum()),
        "duplicate_row_ids": int(frame["Row ID"].duplicated().sum()),
        "invalid_dates": {
            "Order Date": int(frame["Order Date"].isna().sum()),
            "Ship Date": int(frame["Ship Date"].isna().sum()),
        },
        "invalid_numeric": {column: int(frame[column].isna().sum()) for column in NUMERIC_COLUMNS},
        "zero_sales": int(frame["Sales"].eq(0).sum()),
        "negative_sales": int(frame["Sales"].lt(0).sum()),
        "zero_cost": int(frame["Cost"].eq(0).sum()),
        "negative_cost": int(frame["Cost"].lt(0).sum()),
        "negative_gross_profit": int(frame["Gross Profit"].lt(0).sum()),
        "missing_units": int(frame["Units"].isna().sum()),
        "invalid_or_nonpositive_units": int(frame["Units"].le(0).sum()),
        "gross_profit_mismatches": int((~frame["Gross Profit Reconciles"]).sum()),
        "date_anomalies": int(frame["Date Anomaly"].sum()),
        "date_gap_min": int(gap.min()) if not gap.empty else None,
        "date_gap_median": float(gap.median()) if not gap.empty else None,
        "date_gap_max": int(gap.max()) if not gap.empty else None,
        "outliers_iqr": outliers,
        "product_id_name_conflicts": int(
            (frame.groupby("Product ID")["Product Name"].nunique() > 1).sum()
        ),
        "product_name_id_conflicts": int(
            (frame.groupby("Product Name")["Product ID"].nunique() > 1).sum()
        ),
        "division_label_count": int(frame["Division"].nunique()),
        "division_prefix_mismatch_rows": int(len(prefix_mismatch)),
        "division_prefix_mismatches": prefix_mismatch[
            ["Product ID", "Product Name", "Division"]
        ].drop_duplicates().to_dict("records"),
        "rows_retained": len(frame),
    }
