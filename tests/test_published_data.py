import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_CURVES = (
    ROOT / "pt_susde_aug13_depth.csv",
    ROOT / "pt_reusd_dec10_depth.csv",
)


class PublishedCurveTests(unittest.TestCase):
    def test_governance_anchor_curves_are_present_and_well_formed(self):
        required = {
            "size_usd",
            "impact",
            "api_price_impact",
            "ts_utc",
            "chain_id",
            "market",
            "pt_address",
            "out_token",
            "api_base",
            "aggregator_enabled",
            "spot_price_arg",
        }
        for path in PUBLISHED_CURVES:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"missing published curve: {path.name}")
                with path.open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertGreaterEqual(len(rows), 5)
                self.assertTrue(required.issubset(rows[0]))
                sizes = [float(row["size_usd"]) for row in rows]
                impacts = [float(row["impact"]) for row in rows]
                self.assertEqual(sizes, sorted(sizes))
                self.assertGreater(sizes[-1], sizes[0])
                self.assertTrue(all(value >= 0.0 for value in impacts))


if __name__ == "__main__":
    unittest.main()
