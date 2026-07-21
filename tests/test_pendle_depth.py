import unittest
from unittest.mock import patch

from pendle_depth import build_depth_curve


def _kwargs():
    return dict(
        base_url="https://example.invalid",
        chain_id=1,
        market="0xmarket",
        pt_address="0xpt",
        out_token="0xout",
        receiver="0xreceiver",
        pt_decimals=18,
        out_decimals=18,
        usd_mark_per_pt=0.99,
        sizes_pt=[1.0, 2.0],
        timeout=1.0,
        pause_s=0.0,
        enable_aggregator=False,
    )


class PendleDepthTests(unittest.TestCase):
    def test_no_quotes_returns_stable_tuple(self):
        with patch("pendle_depth.fetch_swap_quote", return_value={"__error__": "no route"}):
            rows, smallest = build_depth_curve(**_kwargs())
        self.assertEqual(rows, [])
        self.assertIsNone(smallest)

    def test_smallest_execution_is_converted_to_usd(self):
        quotes = [
            {"data": {"amountOut": str(2 * 10**18), "priceImpact": 0.0}},
            {"data": {"amountOut": str(int(3.8 * 10**18)), "priceImpact": 0.05}},
        ]
        with patch("pendle_depth.fetch_swap_quote", side_effect=quotes):
            rows, smallest = build_depth_curve(
                **_kwargs(), out_token_usd_price=0.97
            )
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(smallest, 1.94, places=12)


if __name__ == "__main__":
    unittest.main()
