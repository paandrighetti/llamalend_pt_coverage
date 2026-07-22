"""
Run the PT debt-ceiling coverage analysis and produce a chart.

Examples
--------
# Demo on a synthetic depth curve (no network needed; numbers are illustrative):
python run_analysis.py --synthetic

# Real analysis once you have a curve from pendle_depth.py:
python run_analysis.py --depth-csv pt_depth_curve.csv \
    --maturity-years 0.5 --max-ltv 0.90 --representative-ltv 0.80 \
    --pool-tvl 100e6 --band-drop 0.08 \
    --depeg 0.03 --discount-widen 0.04 --horizon-days 2 \
    --sigma-max 0.02 --maturity-haircut 0.15 --rho 0.5 \
    --underlying-vol 0.10
"""
from __future__ import annotations

import argparse

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from coverage_model import (
    DepthCurve,
    LiquidityAdjustments,
    MarketParams,
    Stress,
    coverage_curve,
    coverage_ratio,
    heuristic_depth_agnostic_ceiling,
    liquidatable_volume,
    solve_debt_ceiling,
    stressed_liquidity,
)
from synthetic import synthetic_depth_curve


def _fmt(x: float) -> str:
    return f"${x/1e6:,.2f}M" if abs(x) >= 1e6 else f"${x:,.0f}"


def load_depth(args: argparse.Namespace) -> tuple[DepthCurve, bool]:
    if args.synthetic:
        return synthetic_depth_curve(args.pool_tvl), True
    df = pd.read_csv(args.depth_csv).sort_values("size_usd")
    df = df[df["size_usd"] > 0].drop_duplicates(subset="size_usd")
    # enforce a monotone, non-decreasing slippage curve (conservative) against
    # small non-monotonicities from quote noise
    df["impact"] = df["impact"].cummax()
    return DepthCurve(df["size_usd"].to_numpy(), df["impact"].to_numpy()), False


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--synthetic", action="store_true",
                     help="use a synthetic depth curve (illustrative only)")
    src.add_argument("--depth-csv", help="CSV from pendle_depth.py [size_usd,impact]")

    p.add_argument("--pt-symbol", default="PT-sUSDe")
    p.add_argument("--underlying-symbol", default="sUSDe")
    p.add_argument("--maturity-years", type=float, default=0.5)
    p.add_argument("--max-ltv", type=float, default=0.90)
    p.add_argument("--representative-ltv", type=float, default=0.80)
    p.add_argument("--pool-tvl", type=float, default=100e6)
    p.add_argument("--band-drop", type=float, default=0.08)

    p.add_argument("--depeg", type=float, default=0.03)
    p.add_argument("--discount-widen", type=float, default=0.04)
    p.add_argument("--horizon-days", type=float, default=2.0)

    p.add_argument("--sigma-max", type=float, default=0.02)
    p.add_argument("--maturity-haircut", type=float, default=0.15)
    p.add_argument("--rho", type=float, default=0.5)
    p.add_argument("--underlying-vol", type=float, default=0.10)

    p.add_argument("--chart", default="coverage_chart.png")
    args = p.parse_args()

    market = MarketParams(
        pt_symbol=args.pt_symbol,
        underlying_symbol=args.underlying_symbol,
        maturity_years=args.maturity_years,
        max_ltv=args.max_ltv,
        representative_ltv=args.representative_ltv,
        pool_tvl_usd=args.pool_tvl,
        soft_liq_band_drop=args.band_drop,
    )
    stress = Stress(
        underlying_depeg=args.depeg,
        pt_discount_widen=args.discount_widen,
        horizon_days=args.horizon_days,
    )
    adj = LiquidityAdjustments(
        sigma_max=args.sigma_max,
        maturity_haircut=args.maturity_haircut,
        wrongway_rho=args.rho,
    )

    depth, is_synth = load_depth(args)

    l_stress = stressed_liquidity(depth, adj)
    l_raw = depth.max_volume_at_slippage(adj.sigma_max)
    d_star = solve_debt_ceiling(depth, market, stress, adj, conservative=False)
    d_star_cons = solve_debt_ceiling(depth, market, stress, adj, conservative=True)
    benchmark = heuristic_depth_agnostic_ceiling(market, args.underlying_vol)
    cr_at_benchmark = coverage_ratio(benchmark, depth, market, stress, adj)
    frac = min(1.0, stress.collateral_shock / market.soft_liq_band_drop)

    # ----- report -------------------------------------------------------- #
    print("=" * 72)
    print("PT DEBT-CEILING LIQUIDITY-COVERAGE ANALYSIS  (LlamaLend / LLAMMA)")
    print("=" * 72)
    if is_synth:
        print("!! SYNTHETIC DEPTH CURVE -- numbers below are ILLUSTRATIVE ONLY !!")
    print(f"Market            : {market.pt_symbol}  (underlying {market.underlying_symbol})")
    print(f"Maturity (yrs)    : {market.maturity_years}")
    print(f"Max / repr. LTV   : {market.max_ltv:.0%} / {market.representative_ltv:.0%}")
    print(f"Secondary TVL     : {_fmt(market.pool_tvl_usd)}")
    print(f"Soft-liq band drop: {market.soft_liq_band_drop:.0%}")
    print("-" * 72)
    print(f"Stress            : depeg {stress.underlying_depeg:.0%} + discount widen "
          f"{stress.pt_discount_widen:.0%}  over {stress.horizon_days:g}d")
    print(f"Combined collateral shock m         : {stress.collateral_shock:.2%}")
    print(f"Liquidatable fraction (central)     : {frac:.2%}")
    print("-" * 72)
    print(f"sigma_max / maturity haircut / rho  : {adj.sigma_max:.0%} / "
          f"{adj.maturity_haircut:.0%} / {adj.wrongway_rho:.2f}")
    print(f"Absorbable @ sigma_max (calm)  L_raw : {_fmt(l_raw)}")
    print(f"Stressed absorbable          L_stress: {_fmt(l_stress)}")
    print("=" * 72)
    print(f"SCENARIO-IMPLIED CEILING D* (central)     : {_fmt(d_star)}")
    print(f"SCENARIO-IMPLIED CEILING D* (conservative): {_fmt(d_star_cons)}")
    print(f"Depth-agnostic heuristic ceiling     : {_fmt(benchmark)}  (illustrative)")
    print(f"  -> coverage ratio AT that ceiling  : {cr_at_benchmark:.2f}  "
          f"({'CR<1 under scenario' if cr_at_benchmark < 1 else 'CR>=1'})")
    if benchmark > 0:
        print(f"  -> D* (central) is {d_star/benchmark:.1%} of the heuristic ceiling")
    print("=" * 72)

    # ----- chart --------------------------------------------------------- #
    hi = max(d_star, d_star_cons, benchmark) * 1.4
    lo = max(hi / 1e4, 1e4)
    grid = np.geomspace(lo, hi, 240)
    cr = coverage_curve(grid, depth, market, stress, adj, conservative=False)
    cr_cons = coverage_curve(grid, depth, market, stress, adj, conservative=True)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(grid, cr, label="Coverage ratio CR(D), central", lw=2)
    ax.plot(grid, cr_cons, label="CR(D), conservative (whole market unwinds)",
            lw=1.6, ls="--")
    ax.axhline(1.0, color="black", lw=1, label="CR = 1 (coverage threshold)")
    ax.axvline(d_star, color="tab:green", lw=1.4, ls=":",
               label=f"D* central = {_fmt(d_star)}")
    ax.axvline(d_star_cons, color="tab:olive", lw=1.4, ls=":",
               label=f"D* conservative = {_fmt(d_star_cons)}")
    ax.axvline(benchmark, color="tab:red", lw=1.4, ls=":",
               label=f"depth-agnostic ceiling = {_fmt(benchmark)}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Market debt ceiling  D  (USD, log)")
    ax.set_ylabel("Coverage ratio  CR  (log)")
    title = "PT debt ceiling: liquidity-coverage constraint vs depth-agnostic heuristic"
    if is_synth:
        title += "\n[SYNTHETIC DATA, ILLUSTRATIVE]"
    ax.set_title(title, fontsize=11)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(args.chart, dpi=140)
    print(f"[run_analysis] chart written to {args.chart}")


if __name__ == "__main__":
    main()
