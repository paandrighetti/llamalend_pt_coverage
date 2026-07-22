"""
Liquidity-horizon coverage model for sizing Pendle PT debt ceilings in LlamaLend.

Pure computation: no network, no I/O. Fully unit-tested (see tests/).

PRINCIPLE
---------
A Pendle Principal Token (PT) is, economically, a zero-coupon claim that redeems
1:1 for an underlying asset at a fixed maturity. On LlamaLend, PT collateral is
liquidated through LLAMMA (Lending-Liquidating AMM Algorithm), which converts
collateral into crvUSD *continuously* across price bands. Completing that
conversion ultimately requires selling the PT into its secondary liquidity
(mostly the Pendle AMM). Under stress, the event that forces the sale
(an underlying depeg / a widening PT discount) is the same event that drains
PT secondary liquidity -- this is wrong-way (procyclical) risk.

We therefore size the debt ceiling D so that the PT collateral the market is
forced to unwind under a correlated stress (V_liq) can be absorbed by the
stressed secondary liquidity (L_stress) within an acceptable slippage bound.
This transposes the Basel III Liquidity Coverage Ratio (BCBS 238) survival-
horizon logic to on-chain lending:

    Coverage ratio:   CR(D) = L_stress / V_liq(D)
    Ceiling:          D* = max { D : CR(D) >= 1 }

D* is an INDICATIVE ceiling under the stated assumptions, not a guarantee.

SCOPE AND ASSUMPTIONS (v0.2)
----------------------------
* Static coverage constraint, not a simulation. There is no dynamic model of
  LLAMMA band traversal, oracle path, arbitrage, or de-liquidation.
* The liquidation horizon H (StressScenario.horizon_days) enters through the
  CALIBRATION of the stress inputs (depeg, discount widening and withdrawal
  fraction are H-horizon stressed moves), not through the mechanical formula.
  Stressed depth is treated as instantaneous capacity: no replenishment or
  daily-volume term is modelled, which is conservative for multi-day horizons.
* The maturity effect enters through the exogenous maturity haircut h(tau)
  supplied per market/family; maturity_years itself feeds the depth-agnostic
  BENCHMARK (volatility factor), not the coverage ceiling.
* A single representative LTV stands in for the borrower distribution, and the
  soft-liquidated fraction is a linear proxy in the collateral shock. Both are
  coarse stand-ins for LLAMMA band mechanics.
* Every unit unwound by LLAMMA is assumed to hit Pendle secondary liquidity
  one-for-one (no OTC absorption, no holders of last resort): conservative.

All monetary quantities are expressed in a single quote unit (USD or the
underlying), consistently with the depth curve.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


# --------------------------------------------------------------------------- #
# Inputs
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MarketParams:
    """Static description of a candidate PT LlamaLend market."""

    pt_symbol: str
    underlying_symbol: str
    maturity_years: float           # tau, years; benchmark + records only (see SCOPE)
    max_ltv: float                  # protocol bound; validates representative_ltv only
    representative_ltv: float       # assumed average LTV of outstanding debt (<= max_ltv)
    pool_tvl_usd: float             # PT secondary-venue TVL (context / heuristic only)
    # Collateral price drop (fraction) that pushes a position held at
    # `representative_ltv` fully through its soft-liquidation band range.
    # This is a proxy for the LLAMMA band width and is the most model-dependent
    # input; pending a live v2 market it is set parametrically (sensitivity-tested).
    soft_liq_band_drop: float = 0.10

    def __post_init__(self) -> None:
        if not (0.0 < self.representative_ltv <= self.max_ltv < 1.0):
            raise ValueError("require 0 < representative_ltv <= max_ltv < 1")
        if self.maturity_years <= 0.0:
            raise ValueError("maturity_years must be > 0")
        if not (0.0 < self.soft_liq_band_drop < 1.0):
            raise ValueError("soft_liq_band_drop must be in (0,1)")
        if self.pool_tvl_usd < 0.0:
            raise ValueError("pool_tvl_usd must be >= 0")


@dataclass(frozen=True)
class Stress:
    """A correlated stress scenario applied to the PT collateral."""

    underlying_depeg: float         # d: fractional drop in the underlying (0.05 = 5%)
    pt_discount_widen: float        # w: extra fractional drop from PT discount widening
    horizon_days: float             # H: calibration horizon of the stress inputs (see SCOPE)

    def __post_init__(self) -> None:
        for name, v in (("underlying_depeg", self.underlying_depeg),
                        ("pt_discount_widen", self.pt_discount_widen)):
            if not (0.0 <= v < 1.0):
                raise ValueError(f"{name} must be in [0,1)")
        if self.horizon_days <= 0.0:
            raise ValueError("horizon_days must be > 0")

    @property
    def collateral_shock(self) -> float:
        """First-order combined drop in PT collateral value: 1 - (1-d)(1-w)."""
        return 1.0 - (1.0 - self.underlying_depeg) * (1.0 - self.pt_discount_widen)


@dataclass(frozen=True)
class LiquidityAdjustments:
    """Adjustments mapping calm-market depth to stressed absorbable volume."""

    sigma_max: float                # max acceptable execution slippage (0.02 = 2%)
    maturity_haircut: float         # h(tau) in [0,1): reduces effective absorbable volume
    wrongway_rho: float             # rho in (0,1]: stress depth-contraction multiplier

    def __post_init__(self) -> None:
        if not (0.0 < self.sigma_max < 1.0):
            raise ValueError("sigma_max must be in (0,1)")
        if not (0.0 <= self.maturity_haircut < 1.0):
            raise ValueError("maturity_haircut must be in [0,1)")
        if not (0.0 < self.wrongway_rho <= 1.0):
            raise ValueError("wrongway_rho must be in (0,1]")


# --------------------------------------------------------------------------- #
# Depth / slippage curve
# --------------------------------------------------------------------------- #
class DepthCurve:
    """
    PT secondary-liquidity price-impact curve.

    `sizes` are sell sizes (in the quote unit) and `impacts` are the
    corresponding fractional price impacts (slippage), both strictly
    increasing. Built from a real Pendle quote grid (see pendle_depth.py)
    or from a synthetic generator (see synthetic.py).
    """

    def __init__(self, sizes: Sequence[float], impacts: Sequence[float]):
        s = np.asarray(sizes, dtype=float)
        i = np.asarray(impacts, dtype=float)
        if s.ndim != 1 or i.ndim != 1 or s.size != i.size or s.size < 2:
            raise ValueError("sizes and impacts must be 1-D arrays of equal length >= 2")
        if np.any(np.diff(s) <= 0):
            raise ValueError("sizes must be strictly increasing")
        if np.any(np.diff(i) < 0):
            raise ValueError("impacts must be non-decreasing")
        if s[0] < 0 or i[0] < 0:
            raise ValueError("sizes and impacts must be non-negative")
        self.sizes = s
        self.impacts = i

    def max_volume_at_slippage(self, sigma_max: float) -> float:
        """
        Largest sell size whose price impact does not exceed `sigma_max`.

        Conservative clamping: if sigma_max exceeds the largest observed impact,
        we return the largest observed size rather than extrapolating beyond the
        measured curve.
        """
        if sigma_max <= self.impacts[0]:
            # even the smallest measured trade exceeds the bound -> ~0 absorbable
            return float(self.sizes[0]) if sigma_max >= self.impacts[0] else 0.0
        if sigma_max >= self.impacts[-1]:
            return float(self.sizes[-1])
        return float(np.interp(sigma_max, self.impacts, self.sizes))


# --------------------------------------------------------------------------- #
# Core quantities
# --------------------------------------------------------------------------- #
def liquidatable_volume(
    debt_ceiling: float,
    market: MarketParams,
    stress: Stress,
    conservative: bool = False,
) -> float:
    """
    V_liq: PT collateral value that must be unwound under `stress`, as a
    function of the market debt ceiling.

    collateral_value = debt_ceiling / representative_ltv
    fraction unwound  = 1.0 (conservative upper bound: whole market unwinds), or
                        min(1, collateral_shock / soft_liq_band_drop) otherwise.
    """
    if debt_ceiling < 0.0:
        raise ValueError("debt_ceiling must be >= 0")
    collateral_value = debt_ceiling / market.representative_ltv
    if conservative:
        frac = 1.0
    else:
        frac = min(1.0, stress.collateral_shock / market.soft_liq_band_drop)
    return collateral_value * frac


def stressed_liquidity(depth: DepthCurve, adj: LiquidityAdjustments) -> float:
    """
    L_stress: PT volume absorbable within `sigma_max` under stress.

    Calm-market absorbable volume at sigma_max, reduced by the maturity haircut
    (1 - h(tau)) and the wrong-way depth-contraction multiplier rho. Both are
    volume-side reductions representing 'effective absorbable PT under stress'.
    """
    l_raw = depth.max_volume_at_slippage(adj.sigma_max)
    return l_raw * (1.0 - adj.maturity_haircut) * adj.wrongway_rho


def coverage_ratio(
    debt_ceiling: float,
    depth: DepthCurve,
    market: MarketParams,
    stress: Stress,
    adj: LiquidityAdjustments,
    conservative: bool = False,
) -> float:
    """CR(D) = L_stress / V_liq(D). Returns +inf when V_liq == 0."""
    v = liquidatable_volume(debt_ceiling, market, stress, conservative)
    if v <= 0.0:
        return float("inf")
    return stressed_liquidity(depth, adj) / v


def solve_debt_ceiling(
    depth: DepthCurve,
    market: MarketParams,
    stress: Stress,
    adj: LiquidityAdjustments,
    conservative: bool = False,
) -> float:
    """
    D* = max { D : CR(D) >= 1 }.

    Because V_liq is linear and increasing in D and L_stress is exogenous to the
    LlamaLend market size, CR is strictly decreasing in D, so D* is the unique
    root of CR(D) = 1. Solved in closed form; a bisection cross-check lives in
    the tests.
    """
    l_stress = stressed_liquidity(depth, adj)
    if conservative:
        frac = 1.0
    else:
        frac = min(1.0, stress.collateral_shock / market.soft_liq_band_drop)
    if frac <= 0.0:
        return float("inf")  # no liquidation pressure under this (degenerate) stress
    # V_liq(D) = (D / ltv) * frac ; set == l_stress and solve for D
    return l_stress * market.representative_ltv / frac


def coverage_curve(
    debt_grid: Sequence[float],
    depth: DepthCurve,
    market: MarketParams,
    stress: Stress,
    adj: LiquidityAdjustments,
    conservative: bool = False,
) -> np.ndarray:
    """Vectorised CR over a grid of debt ceilings (for plotting)."""
    return np.array(
        [coverage_ratio(d, depth, market, stress, adj, conservative) for d in debt_grid],
        dtype=float,
    )


def heuristic_depth_agnostic_ceiling(
    market: MarketParams,
    underlying_vol_annual: float,
    base_fraction: float = 0.5,
) -> float:
    """
    ILLUSTRATIVE depth-agnostic benchmark ceiling.

    Represents the kind of ceiling set from underlying volatility and maturity
    alone -- WITHOUT a stressed-execution constraint: a fraction of secondary
    TVL, scaled down for higher underlying volatility and longer maturity.
    Calibration is illustrative; the point of the model is the comparison of
    this number to D*, not its absolute level.
    """
    if underlying_vol_annual < 0.0:
        raise ValueError("underlying_vol_annual must be >= 0")
    vol_factor = max(0.1, 1.0 - underlying_vol_annual * (market.maturity_years ** 0.5))
    return market.pool_tvl_usd * base_fraction * vol_factor
