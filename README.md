# LlamaLend PT Debt Ceilings: a Liquidity-Coverage Toolkit

Sizing Pendle Principal Token (PT) debt ceilings in Curve LlamaLend from **soft-liquidation capacity** under correlated stress. Companion code to a governance research contribution on gov.curve.finance (empirical anchors, measured 19 July 2026: PT-sUSDe maturing 13 August 2026 and PT-reUSD maturing 10 December 2026).

## The idea in one paragraph

LlamaLend lends crvUSD against PT collateral. A PT is economically a zero-coupon
claim that redeems 1:1 for an underlying at a fixed date. If collateral value
falls, LLAMMA (Curve's soft-liquidation AMM) must progressively convert that PT
into crvUSD, which ultimately means **selling the PT into its secondary market
(Pendle)**. The more you must sell, the worse the price (slippage). The trap:
the event that *forces* the sale (an underlying depeg / a widening PT discount)
is the same event that *drains* PT liquidity. That is a fire-sale exactly when you can
least afford one, producing bad debt for lenders. So the binding question is not
"what is the PT worth" but **"can the market absorb the
forced unwind without a fire-sale?"** This toolkit answers it by transposing the
Basel III Liquidity Coverage Ratio (BCBS 238) survival-horizon logic onchain:

```
Coverage ratio:  CR(D) = L_stress / V_liq(D)
Scenario ceiling: D* = max { D : CR(D) >= 1 }
```

* `V_liq(D)`: PT collateral the market is forced to unwind under stress, given debt ceiling D
* `L_stress`: PT secondary liquidity absorbable within an acceptable slippage bound, after a maturity haircut and a wrong-way (procyclical) depth-contraction factor

If `V_liq(D) > L_stress`, the market is over-sized under the stated assumptions; `D*` is the largest ceiling supported by that scenario.

## Files

| File | Role | Needs internet? |
|---|---|---|
| `coverage_model.py` | Core math: V_liq, L_stress, CR, D*, benchmark. Pure, typed, tested. | No |
| `run_analysis.py` | CLI: load depth curve, produce report + chart. | No |
| `synthetic.py` | Synthetic depth curve to demo the pipeline. **Illustrative only.** | No |
| `discover_market.py` | Lists active Pendle markets matching a name and prints a ready-to-paste `pendle_depth.py` command with the correct addresses. | **Yes (Pendle API)** |
| `pendle_depth.py` | Retrieval: builds an observed PT price-impact curve from Pendle Hosted SDK quotes. | **Yes (Pendle API)** |
| `dune/underlying_price_history.sql` | Underlying price history: stress depeg + rho calibration. | Run on Dune |
| `dune/pendle_pt_liquidity_context.sql` | Pendle market liquidity context over time: rho. | Run on Dune |
| `tests/` | Unit and publication-data tests (run: `python -m pytest -q`). | No |
| `governance/ForumPost_LlamaLend_PT.md` | The governance research post published on gov.curve.finance. | n/a |
| `pt_susde_aug13_depth.csv` | Near-maturity anchor curve, Pendle-only, v0.2 provenance columns. | n/a |
| `pt_reusd_dec10_depth.csv` | Far-maturity anchor curve, Pendle-only, v0.2 provenance columns. | n/a |
| `data/legacy/pt_depth_curve.csv` | Legacy June pull (pre-v0.2, aggregator-routed): kept for history, superseded by the two curves above. | n/a |
| `estimate_rho.py` | Wrong-way factor estimation: episode and regression estimators on underlying-deviation vs pool-capacity co-movement, honest not-calibratable branch. | `python estimate_rho.py --synthetic` |
| `fetch_rho_inputs.py` | DefiLlama-fed builder for the rho input series (daily underlying price + pool TVL). | see `--help` |
| `dune/*.sql` | Three queries: underlying price history, pool TVL history, Pendle market liquidity context (rho protocol and monitoring inputs). | n/a |
| `rho_inputs.csv`, `rho_inputs_dola.csv`, `rho_wrongway_*.png` | Corrected USDe-series inputs and co-movement charts for the two sampled pools. | n/a |
| `data/exploratory/pt_depth_curve_2.csv`, `make_market2_figs.py`, `coverage_chart_2.png` | **Exploratory** third-regime study (PT-wstETH, long-dated volatile underlying); pre-provenance pull, re-measurement with the v0.2 script planned before any published use. | n/a |
| `examples/example_depth_curve.csv` | Minimal CSV schema example. | n/a |
| `coverage_chart.png`, `coverage_chart_reusd.png` | Canonical output figures for the two publication anchors. | n/a |

Publication curves require adjacent `.manifest.json` files. `run_analysis.py` verifies the SHA-256 hash and rejects unmanifested data unless `--allow-nonpublication-data` is passed explicitly for legacy or exploratory work.

## Quick start

```bash
python -m pip install -e ".[dev]"

# 1) Verify the engine and run an illustrative demo (no network):
python -m pytest -q
python run_analysis.py --synthetic          # writes coverage_chart.png

# 2) Find a market and pull an observed depth curve (needs Pendle API access).
#    discover_market.py prints a ready-to-paste pendle_depth.py command
#    with the correct market, PT, and out-token addresses:
python discover_market.py --query sUSDe --receiver 0xYourEOA

# 3) Reproduce the two governance-post anchors (section 4.3 calibrations):
python run_analysis.py --depth-csv pt_susde_aug13_depth.csv \
    --pt-symbol PT-sUSDe --underlying-symbol sUSDe \
    --maturity-years 0.0658 --max-ltv 0.90 --representative-ltv 0.80 \
    --pool-tvl 8321683 --band-drop 0.08 --depeg 0.03 --discount-widen 0.015 \
    --horizon-days 2 --sigma-max 0.02 --maturity-haircut 0.05 --rho 0.5 --underlying-vol 0.10
python estimate_rho.py --inputs-csv rho_inputs.csv --stress-depeg 0.03   # wrong-way factor report
python run_analysis.py --depth-csv pt_reusd_dec10_depth.csv \
    --pt-symbol PT-reUSD --underlying-symbol reUSD \
    --maturity-years 0.389 --max-ltv 0.90 --representative-ltv 0.80 \
    --pool-tvl 7568508 --band-drop 0.08 --depeg 0.03 --discount-widen 0.015 \
    --horizon-days 2 --sigma-max 0.02 --maturity-haircut 0.15 --rho 0.5 --underlying-vol 0.10
# Legacy June curve (pre-v0.2, aggregator-routed), illustrative only:
python run_analysis.py --depth-csv data/legacy/pt_depth_curve.csv \
    --allow-nonpublication-data --maturity-years 0.5 --max-ltv 0.90 \
    --representative-ltv 0.80 --pool-tvl 100e6 --band-drop 0.08 \
    --depeg 0.03 --discount-widen 0.04 --horizon-days 2 \
    --sigma-max 0.02 --maturity-haircut 0.15 --rho 0.5 --underlying-vol 0.10
```

## The three empirical inputs (and where to get them)

1. **Depth / slippage curve**: `pendle_depth.py` (Pendle Hosted SDK swap quotes
   over a grid of sizes). This is the load-bearing input.
2. **Stress calibration** (`--depeg`, `--discount-widen`): from the underlying's
   worst historical deviation and the PT discount history (`dune/underlying_price_history.sql`).
3. **Wrong-way factor** (`--rho`): from the co-movement of underlying deviation
   and PT depth (both Dune queries). Until estimated, treat `rho` as a sensitivity input.

## Model scope and assumptions (v0.2)

The ceiling D* is an indicative figure under stated assumptions, not a guarantee. Read these before quoting any number:

* Static coverage constraint, not a simulation: no dynamic model of LLAMMA band traversal, oracle path, arbitrage or de-liquidation. The soft-liquidated fraction is a linear proxy in the collateral shock.
* The horizon H parameterises the calibration of the stress inputs (depeg, discount widening, withdrawal fraction are H-horizon stressed moves); stressed depth is treated as instantaneous capacity with no replenishment term, which is conservative for multi-day horizons.
* The maturity effect enters through the exogenous haircut h(tau) supplied per maturity family; `maturity_years` feeds the depth-agnostic benchmark, not the coverage formula.
* A single representative LTV stands in for the borrower distribution; `max_ltv` is a validation bound.
* Every unit unwound by LLAMMA is assumed to hit Pendle secondary liquidity one for one (no OTC absorption, no holders of last resort): conservative.

## Limitations

* **`synthetic.py` is illustrative only.** No number in the accompanying
  analysis derives from it; every published figure comes from an empirical retrieval
  (the governance curves `pt_susde_aug13_depth.csv` and
  `pt_reusd_dec10_depth.csv`; the legacy June curve `data/legacy/pt_depth_curve.csv` is
  retained for history only).
* **The AMM is treated as the quoting authority, not re-implemented.** `pendle_depth.py`
  asks Pendle for quotes rather than re-deriving its (Notional-style) AMM math,
  to avoid reimplementation risk. A heavier alternative is to read the
  onchain `MarketState` and price with Pendle's own SDK; the two approaches
  should be compared rather than assumed identical.
* **`V_liq` is modeled, not measured.** Where LlamaLend v2 PT markets are not
  live, the unwound-volume side uses a parametric soft-liquidation model
  (`soft_liq_band_drop`, `representative_ltv`). It is the most assumption-heavy
  piece; report it with sensitivity, not as a point estimate.
* **The benchmark ceiling is illustrative.** `heuristic_depth_agnostic_ceiling`
  is a depth-agnostic stand-in to make the comparison concrete; the contribution
  is the *method* and the *relative* result (does execution bind tighter?), not
  that specific number.
* **API drift.** The current collector uses Pendle's recommended v3 Convert
  endpoint and validates its response shape. The two governance-anchor CSVs are
  retained snapshots collected through the earlier market-specific swap endpoint;
  their quote values are not silently rewritten when the collector changes. Verify
  current routes against Pendle's official API documentation before a fresh pull.

---

## Citing this work

If this toolkit informs your research or analysis, please cite:

> Pierre-Antoine Andrighetti. (2026). *LlamaLend PT debt ceilings: a liquidity-coverage toolkit for Pendle principal-token collateral under correlated stress.* https://github.com/paandrighetti/llamalend_pt_coverage

---

## Contact

https://www.linkedin.com/in/pierre-antoine-andrighetti
p.a.andrighetti@gmail.com

---

## License

MIT. See [LICENSE](./LICENSE).

## Disclaimer

This work is independent and exploratory. It is not investment advice, not a
recommendation to borrow from or provide liquidity to any Curve LlamaLend or
Pendle market, and not a substitute for a security audit or formal risk
assessment. The author has no affiliation with Curve, LlamaRisk, or Pendle
beyond public usage.
