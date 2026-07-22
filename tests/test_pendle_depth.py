import csv
import unittest
from pathlib import Path
from unittest.mock import patch

from pendle_depth import (
    QuoteCollectionError,
    build_depth_curve,
    fetch_swap_quote,
)


ROOT = Path(__file__).resolve().parents[1]


def _kwargs(**overrides):
    values = {
        "base_url": "https://example.invalid",
        "chain_id": 1,
        "market": "0xmarket",
        "pt_address": "0xpt",
        "out_token": "0xout",
        "receiver": "0xreceiver",
        "pt_decimals": 18,
        "out_decimals": 18,
        "usd_mark_per_pt": 0.99,
        "sizes_pt": [1.0, 2.0],
        "timeout": 120.0,
        "pause_s": 0.0,
        "enable_aggregator": False,
    }
    values.update(overrides)
    return values


def _convert_quote(amount_out_wei: int, price_impact: float) -> dict:
    return {
        "action": "swap",
        "inputs": [{"token": "0xpt", "amount": str(10**18)}],
        "routes": [
            {
                "outputs": [
                    {
                        "token": "0xout",
                        "amount": str(amount_out_wei),
                    }
                ],
                "data": {"priceImpact": price_impact},
            }
        ],
    }


class PendleDepthTests(unittest.TestCase):
    def test_explicit_no_route_returns_stable_empty_tuple(self):
        with patch(
            "pendle_depth.fetch_swap_quote",
            return_value={"routes": []},
        ):
            rows, smallest = build_depth_curve(**_kwargs())

        self.assertEqual(rows, [])
        self.assertIsNone(smallest)

    def test_technical_failure_aborts_measurement(self):
        response = {
            "__error__": "upstream unavailable",
            "__status__": 500,
            "__kind__": "server_error",
        }

        with patch(
            "pendle_depth.fetch_swap_quote",
            return_value=response,
        ):
            with self.assertRaises(QuoteCollectionError) as caught:
                build_depth_curve(**_kwargs())

        self.assertIn(
            "technical measurement failure",
            str(caught.exception),
        )
        self.assertIn("server_error", str(caught.exception))

    def test_schema_failure_aborts_measurement(self):
        with patch(
            "pendle_depth.fetch_swap_quote",
            return_value={"unexpected": "shape"},
        ):
            with self.assertRaises(QuoteCollectionError) as caught:
                build_depth_curve(**_kwargs())

        self.assertIn("schema_error", str(caught.exception))

    def test_smallest_execution_is_converted_to_usd(self):
        quotes = [
            _convert_quote(2 * 10**18, 0.0),
            _convert_quote(int(3.8 * 10**18), 0.05),
        ]

        with patch(
            "pendle_depth.fetch_swap_quote",
            side_effect=quotes,
        ):
            rows, smallest = build_depth_curve(
                **_kwargs(),
                out_token_usd_price=0.97,
            )

        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(smallest, 1.94, places=12)
        self.assertAlmostEqual(rows[1][1], 0.05, places=12)

    def test_successful_quotes_are_sorted_by_size(self):
        # Input grid is intentionally reversed.
        quotes = [
            # 2 PT sold for 3.8 output tokens = 1.9 per PT.
            _convert_quote(int(3.8 * 10**18), 0.05),
            # 1 PT sold for 2 output tokens = 2.0 per PT.
            _convert_quote(2 * 10**18, 0.0),
        ]

        with patch(
            "pendle_depth.fetch_swap_quote",
            side_effect=quotes,
        ):
            rows, smallest = build_depth_curve(
                **_kwargs(sizes_pt=[2.0, 1.0])
            )

        self.assertEqual([row[0] for row in rows], [0.99, 1.98])
        self.assertAlmostEqual(smallest, 2.0, places=12)
        self.assertAlmostEqual(rows[0][1], 0.0, places=12)
        self.assertAlmostEqual(rows[1][1], 0.05, places=12)

    def test_fetch_uses_recommended_v3_convert_payload(self):
        with patch(
            "pendle_depth._post",
            return_value={"routes": []},
        ) as post:
            result = fetch_swap_quote(
                base_url="https://api.example",
                chain_id=1,
                market="0xignored-market",
                token_in="0xpt",
                token_out="0xout",
                amount_in_wei=123,
                receiver="0xreceiver",
                enable_aggregator=False,
                timeout=120.0,
                use_limit_order=False,
            )

        self.assertEqual(result, {"routes": []})

        post.assert_called_once_with(
            "https://api.example/v3/sdk/1/convert",
            {
                "receiver": "0xreceiver",
                "slippage": 0.01,
                "enableAggregator": False,
                "inputs": [{"token": "0xpt", "amount": "123"}],
                "outputs": ["0xout"],
                "useLimitOrder": False,
            },
            120.0,
            soft=False,
        )

    def test_legacy_response_shape_remains_readable(self):
        legacy = [
            {
                "data": {
                    "amountOut": str(2 * 10**18),
                    "priceImpact": 0.0,
                }
            },
            {
                "data": {
                    "amountOut": str(int(3.8 * 10**18)),
                    "priceImpact": 0.05,
                }
            },
        ]

        with patch(
            "pendle_depth.fetch_swap_quote",
            side_effect=legacy,
        ):
            rows, smallest = build_depth_curve(**_kwargs())

        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(smallest, 2.0, places=12)

    def test_published_anchor_csvs_are_present_and_structured(self):
        for filename in (
            "pt_susde_aug13_depth.csv",
            "pt_reusd_dec10_depth.csv",
        ):
            with self.subTest(filename=filename):
                path = ROOT / filename

                self.assertTrue(path.is_file())

                with path.open(
                    newline="",
                    encoding="utf-8-sig",
                ) as handle:
                    reader = csv.DictReader(handle)
                    rows = list(reader)

                self.assertGreater(len(rows), 0)
                self.assertIn("size_usd", reader.fieldnames or [])
                self.assertIn("impact", reader.fieldnames or [])


if __name__ == "__main__":
    unittest.main()
