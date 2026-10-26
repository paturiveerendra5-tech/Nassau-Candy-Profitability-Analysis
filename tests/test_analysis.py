from __future__ import annotations

import unittest
from pathlib import Path

from src.data_cleaning import load_data, quality_report
from src.metrics import pareto_analysis, product_analysis, totals

ROOT = Path(__file__).resolve().parents[1]


class DatasetAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_data(ROOT / "data" / "Nassau Candy Distributor.csv")

    def test_source_rows_and_financial_totals_are_preserved(self) -> None:
        summary = totals(self.data)
        self.assertEqual(len(self.data), 10_194)
        self.assertAlmostEqual(summary["Sales"], 141_783.63, places=2)
        self.assertAlmostEqual(summary["Cost"], 48_340.83, places=2)
        self.assertAlmostEqual(summary["Gross Profit"], 93_442.80, places=2)
        self.assertEqual(summary["Product Count"], 15)

    def test_data_quality_flags_without_dropping_rows(self) -> None:
        quality = quality_report(self.data)
        self.assertEqual(quality["rows_retained"], quality["rows"])
        self.assertEqual(quality["exact_duplicates"], 0)
        self.assertEqual(quality["gross_profit_mismatches"], 0)
        self.assertEqual(quality["date_anomalies"], 10_194)
        self.assertEqual(quality["division_prefix_mismatch_rows"], 6)
        self.assertEqual(len(quality["division_prefix_mismatches"]), 1)

    def test_product_metrics_and_pareto_reach_actual_eighty_percent(self) -> None:
        products = product_analysis(self.data)
        top_product = products.iloc[0]
        self.assertEqual(top_product["Product Name"], "Wonka Bar -Scrumdiddlyumptious")
        self.assertAlmostEqual(products["Revenue Contribution %"].sum(), 100.0)
        self.assertAlmostEqual(products["Profit Contribution %"].sum(), 100.0)

        ordered, count, covered = pareto_analysis(products, "Gross Profit")
        self.assertEqual(count, 5)
        self.assertGreaterEqual(covered, 80.0)
        if count > 1:
            self.assertLess(ordered.iloc[count - 2]["Cumulative Contribution %"], 80.0)


if __name__ == "__main__":
    unittest.main()
