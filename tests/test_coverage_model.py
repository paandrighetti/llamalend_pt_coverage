"""
Unit tests for coverage_model. Run standalone:  python tests/test_coverage_model.py
(Also discoverable by pytest.)
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coverage_model import (  # noqa: E402
    DepthCurve,
    LiquidityAdjustments,
    MarketParams,
    Stress,
    coverage_ratio,
    heuristic_depth_agnostic_ceiling,
    liquidatable_volume,
    solve_debt_ceiling,
    stressed_liquidity,
)


def _market(band_drop: float = 0.10) -> MarketParams:
    return MarketParams("PT-X", "X", 0.5, 0.90, 0.80, 100e6, soft_liq_band_drop=band_drop)


def _stress() -> Stress:
    return Stress(0.03, 0.04, 2.0)


def _adj() -> LiquidityAdjustments:
    return LiquidityAdjustments(0.02, 0.15, 0.5)


def _depth() -> DepthCurve:
    sizes = np.linspace(1e5, 50e6, 60)
    impacts = (sizes / (0.68 * 100e6)) ** 1.5
    return DepthCurve(sizes, impacts)


def test_collateral_shock_first_order():
    s = Stress(0.05, 0.04, 1.0)
    assert abs(s.collateral_shock - (1 - 0.95 * 0.96)) < 1e-12


def test_vliq_increasing_in_debt():
    m, s = _market(), _stress()
    v = [liquidatable_volume(d, m, s) for d in (1e6, 5e6, 20e6)]
    assert v[0] < v[1] < v[2]


def test_conservative_geq_central():
    m, s = _market(), _stress()
    assert liquidatable_volume(7e6, m, s, conservative=True) >= \
        liquidatable_volume(7e6, m, s, conservative=False)


def test_lstress_decreasing_in_haircut_and_rho():
    d = _depth()
    base = stressed_liquidity(d, LiquidityAdjustments(0.02, 0.10, 0.8))
    more_haircut = stressed_liquidity(d, LiquidityAdjustments(0.02, 0.30, 0.8))
    less_rho = stressed_liquidity(d, LiquidityAdjustments(0.02, 0.10, 0.4))
    assert more_haircut < base
    assert less_rho < base


def test_cr_decreasing_in_debt():
    d, m, s, a = _depth(), _market(), _stress(), _adj()
    crs = [coverage_ratio(x, d, m, s, a) for x in (1e6, 3e6, 10e6, 30e6)]
    assert all(crs[i] > crs[i + 1] for i in range(len(crs) - 1))


def test_cr_is_one_at_dstar():
    d, m, s, a = _depth(), _market(), _stress(), _adj()
    dstar = solve_debt_ceiling(d, m, s, a)
    assert abs(coverage_ratio(dstar, d, m, s, a) - 1.0) < 1e-9


def test_closed_form_matches_bisection():
    d, m, s, a = _depth(), _market(), _stress(), _adj()
    dstar = solve_debt_ceiling(d, m, s, a)

    # independent bisection on CR(D) - 1 = 0
    lo, hi = 1.0, 1e12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if coverage_ratio(mid, d, m, s, a) - 1.0 > 0:
            lo = mid
        else:
            hi = mid
    bisect = 0.5 * (lo + hi)
    assert abs(dstar - bisect) / dstar < 1e-6


def test_depth_curve_clamps_and_interpolates():
    d = _depth()
    # below smallest impact -> ~0
    assert d.max_volume_at_slippage(0.0) <= d.sizes[0] + 1e-9
    # above largest impact -> clamp to largest size
    assert d.max_volume_at_slippage(10.0) == d.sizes[-1]
    # interior monotonic
    assert d.max_volume_at_slippage(0.01) < d.max_volume_at_slippage(0.05)


def test_zero_shock_gives_infinite_ceiling():
    d, m, a = _depth(), _market(), _adj()
    s0 = Stress(0.0, 0.0, 1.0)  # exactly no shock
    # frac == 0 -> no liquidation pressure -> unbounded ceiling
    assert solve_debt_ceiling(d, m, s0, a) == float("inf")
    # and a tiny (non-zero) shock yields a large but FINITE ceiling
    tiny = solve_debt_ceiling(d, m, Stress(1e-9, 0.0, 1.0), a)
    assert np.isfinite(tiny) and tiny > solve_debt_ceiling(d, m, _stress(), a)


def test_input_validation():
    for bad in (
        lambda: MarketParams("p", "u", 0.5, 0.9, 0.95, 1e6),   # repr > max
        lambda: Stress(1.2, 0.0, 1.0),                          # depeg >= 1
        lambda: LiquidityAdjustments(0.02, 0.10, 1.5),          # rho > 1
        lambda: DepthCurve([1, 1], [0.0, 0.1]),                 # non-increasing size
    ):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("expected validation error was not raised")


def test_heuristic_scales_down_with_vol():
    m = _market()
    hi_vol = heuristic_depth_agnostic_ceiling(m, 0.30)
    lo_vol = heuristic_depth_agnostic_ceiling(m, 0.05)
    assert hi_vol < lo_vol


def _run_all() -> None:
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
