# Sizing Pendle PT Debt Ceilings in LlamaLend v2 from Soft-Liquidation Capacity: A Liquidity-Horizon Framework under Correlated Stress

*For gov.curve.finance, Research / Risk. Independent contribution. All figures measured 19 July 2026 with the published toolkit, Pendle-only routing, provenance columns in the repository CSVs.*

---

## 1. Context and scope

LlamaRisk has done substantial public work preparing Principal Token (PT) collateral for LlamaLend v2: price-discovery analysis, liquidity characterisation, a maturity-aware debt-ceiling notion, and a dedicated time-decay oracle. On pricing specifically, the question is largely settled — the Exponential Lower Bound (ELB) curve LlamaRisk proposed on Aave, alongside Chaos Labs' PT Risk Oracle and RedStone's Dynamic PT Oracle, gives a conservative, manipulation-resistant mark for PTs as collateral.

This post does **not** revisit valuation. It addresses a complementary, downstream question that LLAMMA's mechanism makes distinct from the Aave/Morpho/Euler context where most PT risk analysis currently lives:

> Given a conservative PT mark, can LlamaLend's soft-liquidation actually **unwind** PT collateral within the relevant liquidation horizon, under a *correlated* stress, without slippage breaching the soft-liquidation buffer and minting bad debt?

In bank-risk terms: existing frameworks set the **mark-to-model** value of PT collateral. This proposal sizes the **liquidation value under a time-to-liquidate constraint**, and derives a debt ceiling from it. The two are not the same number, and under LLAMMA the gap matters.

## 2. The gap: executability, not valuation

Three points motivate a Curve-specific treatment.

**(a) PT liquidation parameters do not transfer cleanly from Aave-style systems.** Aave, Morpho and Euler liquidate via a health-factor / liquidation-bonus mechanism: a discrete swap of collateral for debt repayment, executed by liquidators against external venues. LlamaLend does not. LLAMMA converts collateral into crvUSD *continuously and reversibly* across concentrated-liquidity bands (soft-liquidation), with hard liquidation only as a backstop. The realised outcome therefore depends on the *path* of conversion and on the depth of PT secondary liquidity encountered along that path — not on a single liquidation price. A debt ceiling calibrated to a hard-liquidation system implicitly assumes a liquidation mechanism LlamaLend doesn't use.

**(b) PT secondary liquidity is wrong-way / procyclical.** A PT's most material risk is the underlying it wraps; Pendle does not backstop the underlying. PT secondary liquidity is also thin in less-deep pools, and large pre-maturity exits incur significant slippage. Crucially, the event that *triggers* liquidation of a PT position — an underlying depeg (e.g. USDe), or an implied-yield spike widening the PT discount — is the *same* event that drains PT secondary liquidity. Liquidation need and liquidation capacity are negatively correlated. This is textbook wrong-way risk, and a debt ceiling keyed only to time-to-maturity × underlying volatility does not capture it: it sizes the *asset's* price risk, not the *market's* capacity to absorb a stressed unwind.

**(c) The sDOLA-long2 incident is the relevant precedent.** The March 2026 sDOLA exploit demonstrated, on LlamaLend specifically, how oracle-derived valuations of non-spot-liquid, yield-bearing collateral interact dangerously with soft-liquidation: positions were forced into soft-liquidation and then made unhealthy via manipulation of a price-per-share-derived oracle. PTs sit in the same structural family — model-derived price, thin spot market, yield-bearing, underlying-correlated. The lesson generalises: for this collateral family, the binding risk is not the steady-state mark but the *interaction of valuation and liquidation execution under stress*. PT onboarding is the next instance of exactly the surface that incident exposed.

## 3. Framework: a liquidity-coverage constraint for PT debt ceilings

The proposal transposes the Basel III Liquidity Coverage Ratio (LCR, BCBS 238) logic — *high-quality liquid assets must cover net outflows over a defined stress horizon* — to the soft-liquidation setting:

> *Available stressed PT secondary liquidity must cover the collateral that must be liquidated under a correlated stress, over the liquidation horizon.*

Define, for a candidate PT market:

- **V_liq(D, S, H)** — the volume of PT collateral that enters liquidation (soft → hard) over horizon **H** under stress scenario **S**, as a function of the market debt ceiling **D**. This depends on the LLAMMA band distribution of outstanding loans and on the price path implied by **S**.
- **L_stress(σ_max, h(τ), ρ)** — the PT secondary liquidity realisable within an acceptable slippage bound **σ_max**, after:
  - a **maturity-bucketed haircut h(τ)** on realisable value (PT liquidity and price behaviour are a function of time-to-maturity τ — analogous to maturity-bucketed haircuts in the Basel collateral framework / FRTB liquidity horizons);
  - a **wrong-way factor ρ ∈ (0,1]** contracting available depth in the stressed state, calibrated to the historical co-movement of underlying deviation and PT pool depth.

The debt-ceiling constraint:

```
Coverage Ratio:  CR = L_stress(σ_max, h(τ), ρ) / V_liq(D, S, H)  ≥  1

Debt ceiling:    D* = max { D :  V_liq(D, S, H) ≤ L_stress(σ_max, h(τ), ρ) }
```

This is deliberately complementary to LlamaRisk's existing debt-ceiling methodology, which already monitors liquidity depth and borrower behaviour. The addition is to (i) make the constraint *forward and stress-conditioned* rather than a depth observation, (ii) condition it on maturity via h(τ), (iii) embed the wrong-way correlation ρ explicitly, and (iv) tie V_liq to LLAMMA's band mechanics rather than to a hard-liquidation assumption.

**The punchline (§4): execution capacity is regime-dependent in maturity.** Near maturity, Pendle's AMM concentrates liquidity around redemption value and exposes a hard proportion cap: capacity is a binary cliff, cheap below it and unavailable above it. Far from maturity, slippage is genuinely gradual and the sigma_max bound binds well before any cap. A ceiling keyed to calm depth mis-sizes both regimes; once capacity is stress-contracted (rho), D* sits well below both the pool's cap and what porting Aave-style hard-liquidation parameters would suggest, and the gap widens with maturity and thinness.

## 4. Empirical results: two maturities, two regimes (Ethereum, 19 July 2026)

Both curves are Pendle-only (aggregator routing disabled), quoted PT to underlying across a size grid, slippage rebased to the marginal (smallest-trade) price; CSVs with full provenance (timestamp, addresses, routing mode) are in the repository.

### 4.1 Near maturity: PT-sUSDe, matures 13-Aug-2026 (25 days, tau = 0.066 yr)

Pool TVL $8.32M, implied yield 4.3%, spot 0.8042 sUSDe per PT. Across every size the AMM serves, slippage stays below 0.45%; a 2% threshold is never approached. The pool then refuses outright: quotes at 7.81M PT and above return `MarketProportionTooHigh`, with the largest served size at 7.29M PT (about $5.9M at spot). Execution capacity is a cliff, not a curve. Notably, in the June draft of this analysis the same market (then 66 days out, TVL $9.5M, aggregator routing enabled) showed the wall near $12.4M: part of that difference is routing, part is the pool's decline into maturity. Both readings make the same governance point: the cap moves with the pool, so it must be monitored, not assumed.

### 4.2 Away from maturity: PT-reUSD, matures 10-Dec-2026 (tau = 0.389 yr)

Pool TVL $7.57M, implied yield 10.4%. Here the regime inverts: slippage climbs progressively with size from the smallest quotes onward, the sigma_max = 2% bound binds within the quotable range, and the proportion cap is not the operative constraint. This is the general regime the framework targets, and the one where a calm-depth or maturity-only rule mis-sizes most: measured, executable depth within the slippage bound is a strict subset of displayed TVL.

### 4.3 Ceilings under the coverage constraint

Running the identical stress calibration on both curves (3% underlying depeg, 1.5% discount widening, 8% band drop, representative LTV 0.80, two-day horizon, maturity haircuts 0.05 and 0.15 respectively), with the wrong-way factor rho as the sensitivity axis:

| rho (stressed depth retention) | D* PT-sUSDe, central (conservative) | D* PT-reUSD, central (conservative) |
|---|---:|---:|
| 0.5 | $[SUSDE_C_05]M ($[SUSDE_K_05]M) | $[REUSD_C_05]M ($[REUSD_K_05]M) |
| 0.3 | $[SUSDE_C_03]M ($[SUSDE_K_03]M) | $[REUSD_C_03]M ($[REUSD_K_03]M) |

Recommended anchoring rho in [0.3, 0.5], consistent with liquidity contractions observed in past stablecoin-depeg episodes; the full sensitivity is in the repository charts.

Three structural readings survive any rho choice. First, both ceilings land well below pool TVL once stress contraction applies: displayed depth is not usable depth. Second, the near-maturity anchor's ceiling is governed by the proportion cap times rho; the far anchor's by the slippage curve times rho: same formula, different binding term, which is exactly why a single ported parameter set cannot serve both. Third, the depth-agnostic heuristic lands near the conservative band on one anchor and away from it on the other, for the wrong reasons in both cases: it captures neither the cap structure nor the contraction.

## 5. Recommendation

For PT collateral in LlamaLend v2, set the per-market debt ceiling as **min( maturity-/volatility-based ceiling, D\* from the soft-liquidation coverage constraint )**, with:

- **σ_max** (acceptable liquidation slippage) and **ρ** (wrong-way factor) published per underlying family;
- **h(τ)** tightening as a function of remaining maturity;
- **monitoring triggers**: in production, track distance-to-cap (the pool's proportion relative to its `MarketProportionTooHigh` bound), not just spot depth. The two dated measurements above show why: on the same sUSDe market, the wall moved materially in six weeks as the pool declined into maturity. Alert when underlying deviation crosses the band that historically coincides with capacity contraction: monitor stressed coverage continuously, not only at onboarding.

## 6. Limitations and open questions

- PT secondary-depth data is the load-bearing input; where pool data is sparse the result should be stated as bounds plus sensitivity, not a false point estimate.
- Stressed depth is treated as instantaneous capacity with no replenishment term over the horizon: no LP re-entry, no arbitrage refill. Conservative for multi-day horizons.
- Every unit unwound by LLAMMA is assumed to hit Pendle secondary liquidity one for one: no OTC absorption, no holder of last resort. Conservative.
- Routing: resolved since the June draft. All published figures are Pendle-only quotes (aggregator routing disabled, provenance columns in the CSVs). Aggregator routing would add external depth and raise measured capacity; excluding it is the conservative and governance-relevant choice, since a forced unwind under stress cannot assume third-party routing.
- rho calibration requires a sufficiently long joint history of underlying deviation and PT depth, which young pools may lack; until estimated per family, it is a published sensitivity input, and D* should be read as an indicative band, not a point.
- The framework assumes LLAMMA band parameters are known and stable per market; v2 design changes would shift V_liq.

Questions for LlamaRisk and the community: does the v2 PT design already constrain executability implicitly (e.g. via oracle/band choices), making this redundant — or is an explicit coverage constraint additive? And is the wrong-way factor better handled at the debt-ceiling level (as proposed here) or at the oracle level on top of the ELB?

---

*Independent analysis, not investment advice. Methodology, code, measured curves and provenance: https://github.com/paandrighetti/llamalend_pt_coverage*
