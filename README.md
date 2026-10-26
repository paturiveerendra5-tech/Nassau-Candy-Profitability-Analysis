# Nassau Candy Profitability Analysis

An end-to-end analysis and Streamlit dashboard for the provided Nassau Candy distributor CSV. The dashboard and reports read the actual source data; no synthetic business values are used.

## Project contents

```text
.
├── app.py
├── data/
│   └── Nassau Candy Distributor.csv
├── notebooks/
│   └── EDA.ipynb
├── reports/
│   ├── data_quality.md
│   ├── executive_summary.md
│   └── research_paper.md
├── src/
│   ├── analysis.py
│   ├── data_cleaning.py
│   ├── metrics.py
│   ├── reporting.py
│   └── visualizations.py
├── tests/
│   └── test_analysis.py
└── requirements.txt
```

## Run locally

Use Python 3.10 or later.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If the CSV is absent, download the source file from [the provided Google Drive dataset](https://drive.google.com/file/d/1c4VDb0Pf7RCgps4aLMiSuLtdaUpU_X49/view) and save it as `data/Nassau Candy Distributor.csv`.

## Rebuild the reports

The markdown reports are generated from the CSV using the same parsing and metric functions:

```powershell
python -m src.reporting
```

## Exploratory Data Analysis notebook

Open `notebooks/EDA.ipynb` in Jupyter or VS Code and run all cells. It loads the local CSV through the shared cleaning and metric modules and displays the actual dataset profile, validation checks, descriptive distributions, product/division/regional summaries, cost and margin diagnostics, Pareto charts, and order-date trends. It retains every source row and calls out the long order-to-ship date intervals. Start Jupyter from the project root so the notebook can locate `data/Nassau Candy Distributor.csv`; it also checks the parent folder when launched from `notebooks`.

## Test

```powershell
python -m unittest discover -s tests -v
```

## Dashboard

Seven dashboard sections cover executive KPIs and trends, product profitability, division performance, cost/margin risk, revenue/profit Pareto, regional results, and factory information. The sidebar filters for order date, division, region, minimum aggregate product margin, and product name apply consistently to the financial views.

Factory coordinates can be mapped, but the product-to-factory mapping referenced in the project requirements was not supplied. Therefore factory-level financials and factory filtering are deliberately unavailable; the factory page shows only the supplied coordinates and explains the limitation. State/city coordinates were also not supplied, so the dashboard does not infer a geographic map.

## Data caveats

- The source does not specify a currency; financial results are in source units.
- All order-to-ship intervals are unusually long (904–1,642 days). Dates are preserved, not corrected, and trend analysis uses Order Date only. Confirm the source dates before interpreting fulfillment timing.
- No rows are removed. IQR outliers are flagged for review rather than discarded.
- See [data_quality.md](reports/data_quality.md), [research_paper.md](reports/research_paper.md), and [executive_summary.md](reports/executive_summary.md) for actual findings, methodology, and limitations.
