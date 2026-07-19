# Sizing Pendle PT Debt Ceilings in LlamaLend v2 from Soft-Liquidation Capacity: A Liquidity-Horizon Framework under Correlated Stress

*Draft for gov.curve.finance — Research / Risk. Independent contribution; figures in §4 are placeholders pending the on-chain data pull specified inline.*

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

**The punchline (refined by the data in §4):** the binding execution constraint is not gradual slippage but the pool's *hard proportion cap*, and calm-market capacity badly *overstates* what is available under stress. Once that capacity is stress-contracted (ρ), D* sits well below both the pool's cap and what porting Aave-style, hard-liquidation parameters would suggest — and the gap is quantifiable, not rhetorical. It widens with maturity and thinness.

## 4. Empirical result — PT-sUSDe (matures 13-Aug-2026), Ethereum

Anchor: the sole active sUSDe PT market, ≈66 days to maturity (τ≈0.18 yr), Pendle pool TVL ≈ $9.49M, implied yield ≈ 4.5%. Depth measured by quoting PT→SY swaps across a size grid, with slippage rebased to the marginal (smallest-trade) price; reproducible via the published toolkit.

**Finding 1 — calm-market slippage is not the binding constraint.** Across the entire quotable range the pool absorbs PT sales with negligible size-driven slippage (<0.2% up to ≈$12.4M, i.e. ≈1.3× pool TVL). A 2% slippage threshold is never reached. Instead the AMM exposes a hard capacity wall: beyond ≈$12.4M it returns `MarketProportionTooHigh` and refuses to quote. Execution capacity is therefore a near-binary cliff — cheap below the cap, *unavailable* above it — not a gradual slippage curve. This is characteristic of Pendle's near-maturity AMM, which concentrates liquidity around redemption value.

**Finding 2 — the binding lever is stress contraction (ρ), not calm depth.** Because calm capacity (≈$12.4M) exceeds the pool's own TVL, sizing a ceiling off calm depth would *overstate* available liquidity: the premise of wrong-way risk is precisely that this capacity contracts when liquidation is triggered (a USDe depeg both forces the unwind and pushes the pool toward its proportion cap / pulls LPs). Capturing this with the contraction factor ρ, the safe ceiling is

D* = ( cap · (1 − h(τ)) · ρ ) · LTV_repr / f(stress),

with measured cap ≈ $12.4M, h(τ)=0.10 (small, justified by the 66-day horizon), LTV_repr=0.80, and f(stress)=55.7% of collateral entering liquidation under a combined 3% USDe depeg + 1.5% discount-widening shock.

**D\* is governed almost entirely by ρ** (all other inputs measured or near-certain):

| ρ (stressed depth retention) | D* central | D* conservative |
|---|---:|---:|
| 1.0 (no contraction) | $15.9M | $8.8M |
| 0.7 | $11.1M | $6.2M |
| 0.5 | $8.0M | $4.4M |
| 0.3 | $4.8M | $2.7M |
| 0.2 | $3.2M | $1.8M |

*(figure: D\* vs ρ, with pool TVL, the $12.4M proportion cap, and a depth-agnostic heuristic marked.)*

Since ρ cannot be estimated reliably from a 66-day-old pool's own history, we anchor it conservatively to liquidity contractions observed in past stablecoin-depeg episodes, ρ∈[0.3,0.5], giving a safe ceiling of roughly **$2.7–4.4M (conservative) / ≈30–45% of pool TVL**. A depth-agnostic heuristic (~$4.5M here) happens to land in this band — but for the wrong reasons: it captures neither the proportion-cap structure nor the stress contraction, and would mis-size badly at a different maturity or pool depth.

**Scope.** This framework discriminates *most* for longer-dated PTs, whose pools are thinner and whose slippage is genuinely gradual; for a near-maturity PT like this one the proportion cap and ρ dominate. As LlamaLend v2 onboards longer-dated and lower-liquidity PT collateral, the calm-vs-stressed gap widens and the constraint becomes materially tighter than valuation- or maturity-based ceilings.

## 5. Recommendation

For PT collateral in LlamaLend v2, set the per-market debt ceiling as **min( maturity-/volatility-based ceiling, D\* from the soft-liquidation coverage constraint )**, with:

- **σ_max** (acceptable liquidation slippage) and **ρ** (wrong-way factor) published per underlying family;
- **h(τ)** tightening as a function of remaining maturity;
- **monitoring triggers**: in production, track the pool's proportion relative to its `MarketProportionTooHigh` bound (distance-to-cap), not just spot depth, and alert when underlying deviation crosses the band that historically coincides with capacity contraction — i.e. monitor stressed coverage continuously, not only at onboarding.

## 6. Limitations and open questions

- PT secondary-depth data is the load-bearing input; where pool data is sparse the result should be stated as bounds + sensitivity, not a false point estimate.
- ρ calibration requires a sufficiently long joint history of underlying deviation and PT depth, which young pools may lack.
- The framework assumes LLAMMA band parameters are known and stable per market; v2 design changes would shift V_liq.

Questions for LlamaRisk and the community: does the v2 PT design already constrain executability implicitly (e.g. via oracle/band choices), making this redundant — or is an explicit coverage constraint additive? And is the wrong-way factor better handled at the debt-ceiling level (as proposed here) or at the oracle level on top of the ELB?

---

*Independent analysis. Methodology and code intended to be published openly as a reusable resource for prospective LlamaLend integrators.*
