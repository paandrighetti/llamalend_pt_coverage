# LlamaLend PT Debt Ceilings: a Liquidity-Coverage Toolkit

Sizing Pendle Principal Token (PT) debt ceilings in Curve LlamaLend from **soft-liquidation capacity** under correlated stress. Companion code to a governance research contribution on gov.curve.finance (empirical anchor: the PT-sUSDe market maturing 13 August 2026).

## The idea in one paragraph

LlamaLend lends crvUSD against PT collateral. A PT is economically a zero-coupon
claim that redeems 1:1 for an underlying at a fixed date. If collateral value
falls, LLAMMA (Curve's soft-liquidation AMM) must progressively convert that PT
into crvUSD, which ultimately means **selling the PT into its secondary market
(Pendle)**. The more you must sell, the worse the price (slippage). The trap:
the event that *forces* the sale (an underlying depeg / a widening PT discount)
is the same event that *drains* PT liquidity. That is a fire-sale exactly when you can
least afford one, producing bad debt for lenders. So the binding question is not
"what is the PT worth" (oracles solved that) but **"can the market absorb the
forced unwind without a fire-sale?"** This toolkit answers it by transposing the
Basel III Liquidity Coverage Ratio (BCBS 238) survival-horizon logic onchain:

```
Coverage ratio:  CR(D) = L_stress / V_liq(D)
Safe ceiling:    D* = max { D : CR(D) >= 1 }
```

* `V_liq(D)`: PT collateral the market is forced to unwind under stress, given debt ceiling D
* `L_stress`: PT secondary liquidity absorbable within an acceptable slippage bound, after a maturity haircut and a wrong-way (procyclical) depth-contraction factor

If `V_liq(D) > L_stress`, the market is over-sized; `D*` is the largest safe size.

## Files

| File | Role | Needs internet? |
|---|---|---|
| `coverage_model.py` | Core math: V_liq, L_stress, CR, D*, benchmark. Pure, typed, tested. | No |
| `run_analysis.py` | CLI: load depth curve, produce report + chart. | No |
| `synthetic.py` | Synthetic depth curve to demo the pipeline. **Illustrative only.** | No |
| `discover_market.py` | Lists active Pendle markets matching a name and prints a ready-to-paste `pendle_depth.py` command with the correct addresses. | **Yes (Pendle API)** |
| `pendle_depth.py` | Retrieval: builds the REAL PT price-impact curve from Pendle API swap quotes. | **Yes (Pendle API)** |
| `dune/underlying_price_history.sql` | Underlying price history: stress depeg + rho calibration. | Run on Dune |
| `dune/pendle_pt_liquidity_context.sql` | Pendle market liquidity context over time: rho. | Run on Dune |
| `tests/test_coverage_model.py` | Unit tests (run: `python tests/test_coverage_model.py`). | No |
| `pt_depth_curve.csv` | Measured PT-sUSDe depth curve (Pendle API quotes) used in the forum analysis. | n/a |
| `example_depth_curve.csv` | Minimal CSV schema example. | n/a |
| `coverage_chart.png`, `dstar_vs_rho.png` | Output figures. | n/a |

## Quick start

```bash
pip install -r requirements.txt

# 1) Verify the engine and run an illustrative demo (no network):
python tests/test_coverage_model.py
python run_analysis.py --synthetic          # writes coverage_chart.png

# 2) Find a market and pull a REAL depth curve (needs Pendle API access).
#    discover_market.py prints a ready-to-paste pendle_depth.py command
#    with the correct market, PT, and out-token addresses:
python discover_market.py --query sUSDe

# 3) Run the analysis on a measured curve. Parameter values below are
#    illustrative; the exact PT-sUSDe calibration used in the forum post
#    is documented in the post itself:
python run_analysis.py --depth-csv pt_depth_curve.csv \
    --maturity-years 0.5 --max-ltv 0.90 --representative-ltv 0.80 \
    --pool-tvl 100e6 --band-drop 0.08 \
    --depeg 0.03 --discount-widen 0.04 --horizon-days 2 \
    --sigma-max 0.02 --maturity-haircut 0.15 --rho 0.5 --underlying-vol 0.10
```

## The three real inputs (and where to get them)

1. **Depth / slippage curve**: `pendle_depth.py` (Pendle Hosted SDK swap quotes
   over a grid of sizes). This is the load-bearing input.
2. **Stress calibration** (`--depeg`, `--discount-widen`): from the underlying's
   worst historical deviation and the PT discount history (`dune/underlying_price_history.sql`).
3. **Wrong-way factor** (`--rho`): from the co-movement of underlying deviation
   and PT depth (both Dune queries). Until estimated, treat `rho` as a sensitivity input.

## Model scope and assumptions (v0.1)

The ceiling D* is an indicative figure under stated assumptions, not a guarantee. Read these before quoting any number:

* Static coverage constraint, not a simulation: no dynamic model of LLAMMA band traversal, oracle path, arbitrage or de-liquidation. The soft-liquidated fraction is a linear proxy in the collateral shock.
* The horizon H parameterises the calibration of the stress inputs (depeg, discount widening, withdrawal fraction are H-horizon stressed moves); stressed depth is treated as instantaneous capacity with no replenishment term, which is conservative for multi-day horizons.
* The maturity effect enters through the exogenous haircut h(tau) supplied per maturity family; `maturity_years` feeds the depth-agnostic benchmark, not the coverage formula.
* A single representative LTV stands in for the borrower distribution; `max_ltv` is a validation bound.
* Every unit unwound by LLAMMA is assumed to hit Pendle secondary liquidity one for one (no OTC absorption, no holders of last resort): conservative.

## Limitations

* **`synthetic.py` is illustrative only.** No number in the accompanying
  analysis derives from it; every published figure comes from real retrieval
  (`pt_depth_curve.csv`).
* **The AMM is treated as source of truth, not re-implemented.** `pendle_depth.py`
  asks Pendle for quotes rather than re-deriving its (Notional-style) AMM math,
  to avoid correctness risk. A fully trustless alternative is to read the
  onchain `MarketState` and price with Pendle's own SDK: heavier, same result.
* **`V_liq` is modeled, not measured.** Where LlamaLend v2 PT markets are not
  live, the unwound-volume side uses a parametric soft-liquidation model
  (`soft_liq_band_drop`, `representative_ltv`). It is the most assumption-heavy
  piece; report it with sensitivity, not as a point estimate.
* **The benchmark ceiling is illustrative.** `heuristic_depth_agnostic_ceiling`
  is a depth-agnostic stand-in to make the comparison concrete; the contribution
  is the *method* and the *relative* result (does execution bind tighter?), not
  that specific number.
* **API drift.** Pendle and Dune routes change; `pendle_depth.py` fails loudly on
  a schema mismatch. Verify against current Pendle API docs.

---

## Citing this work

If this toolkit informs your research or analysis, please cite:

> Pierre-Antoine Andrighetti. (2026). *LlamaLend PT debt ceilings: a liquidity-coverage toolkit for Pendle principal-token collateral under correlated stress.* https://github.com/paandrighetti/llamalend_pt_coverage

---

## Contact

https://www.linkedin.com/in/pierre-antoine-andrighetti
https://x.com/bandulf
p.a.andrighetti@gmail.com

---

## Depth measurement notes

`pendle_depth.py` v0.2 quotes with aggregator routing disabled by default (`--enable-aggregator` to opt in), enforces a spot sanity check on the smallest execution, and writes provenance columns (timestamp, chain, market, addresses, API base, routing mode) into the CSV. The committed `pt_depth_curve.csv` was pulled with the pre-v0.2 script (aggregator enabled, no provenance columns); re-pull with the current script to reproduce the curve under Pendle-only routing.

## License

MIT. See [LICENSE](./LICENSE).

## Disclaimer

This work is independent and exploratory. It is not investment advice, not a
recommendation to borrow from or provide liquidity to any Curve LlamaLend or
Pendle market, and not a substitute for a security audit or formal risk
assessment. The author has no affiliation with Curve, LlamaRisk, or Pendle
beyond public usage.
