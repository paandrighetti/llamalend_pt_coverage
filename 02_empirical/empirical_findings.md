# RWA HQLA Framework: Empirical Findings

**Version**: 1.1.1 (data snapshot 2026-06-17) (initial extraction 2026-05-11)
**Source data**: Dune Analytics (snapshot 17 June 2026), Etherscan, CoinGecko, RWA.xyz, ESMA filings, Messari, BlackRock/Ondo press releases
**Methodology**: on-chain extraction via the SQL queries in `dune_queries.sql`, concentration metrics via Python (`lorenz_real_data.py`).

## Executive summary

The on-chain empirical analysis **strongly confirms and extends the scoring matrix verdict**. Block C (Market Criteria), which scored Fail across all three products on the regulatory text alone, is now validated by directly measured data (Dune Analytics, snapshot 17 June 2026):

- BUIDL Ethereum mainnet: **76 holders** for ~$181M, of which 25 hold dust balances below $2 (effective holder count 51). The multi-chain global figure of $2.28B means Ethereum now represents only about 8% of total AUM, the bulk having migrated to Solana and other chains.
- **Near-zero secondary trading volume** on the only public price aggregator (CoinGecko)
- Cumulative concentration measured from the per-holder export (query M2-bis): Top-3 = 55.2%, Top-10 = 83.0%, Top-25 = 99.5%. Scalar Gini = **0.863** on a reconstruction under these measured constraints; exact LP bounds show every consistent distribution has Gini in **[0.850, 0.885]**
- Top-3 holders: 55% of supply; Top-10: 83%; Top-25: 99.5%
- 14,046 cumulative transfers, of which 3,151 secondary, approximately 4 secondary transfers per day averaged over the fund's 26-month history

The market microstructure is closer to a **bilateral institutional product** (around 50 effective counterparties transacting with BlackRock and Securitize) than to a "deep and active market with committed market makers" as required by BCBS 238 §24(d).

## Detailed findings by product

### BUIDL: empirical snapshot

| Metric | Value | Source |
|---|---|---|
| Contract Ethereum | `0x7712c34205737192402172409a8F7ccef8aA2AEc` | Etherscan |
| AUM global (multi-chain) | $2,282,555,237 | CoinGecko 2026-05-06 |
| AUM Ethereum mainnet | $181,293,772 | Dune 2026-06-17 |
| Holders Ethereum mainnet | 76 (≈50 effective) | Dune 2026-06-17 |
| Cumulative transfers Ethereum | 14,046 (3,151 secondary) | Dune 2026-06-17 |
| Secondary transfer rate | ~4/day | Computed |
| Number of chains deployed | 8 | RWA.xyz |
| Time since launch | ~826 days (2.26 years) | Computed |

**Concentration (Dune per-holder export, query M2-bis):**
- Gini = 0.863 on the constrained reconstruction (exact feasible range [0.850, 0.885]; see `lorenz_real_data.py`)
- Top-3 holders = 55% of supply
- Top-10 holders = 83% of supply
- Top-25 holders = 99.5% of supply

**Interpretation**: BUIDL is structurally a wholesale institutional money market product accessed through a fund-share token wrapper. The "blockchain" property adds 24/7 transferability and USDC settlement rails but **does not create a secondary market in any meaningful sense**.

### OUSG: empirical snapshot

| Metric | Value | Source |
|---|---|---|
| AUM global (Apr 2026) | ~$770M | RWA.xyz |
| Holders Ethereum mainnet | ~80 | Dune 2026-06-17 |
| Cumulative transfers Ethereum | 2,119 (851 secondary) | Dune 2026-06-17 |
| Secondary transfer rate | ~0.7/day | Computed |
| 24h secondary volume | Low five-digit USD range (estimate) | CoinGecko / aggregators |
| Major position | Ripple (post-XRPL pilot 6 May 2026) | Press release |

Recent cross-border settlement pilot with Kinexys (JPMorgan), Mastercard MTN, and Ripple validates operational rails, but is an **institutional B2B integration**, not a public secondary market.

### bIB01: empirical snapshot

| Metric | Value | Source |
|---|---|---|
| Contract Ethereum | `0xCA30c93B02514f86d5C86a6e375E3A330B435Fb5` | bIB01 Final Terms |
| AUM (Backed product suite, not bIB01-specific) | ~$250M+ | CV5 Capital |
| Max issue volume per Final Terms | CHF 100,000,000 | FMA filing |
| Holders Ethereum mainnet | ~35 | Dune 2026-06-17 |
| Cumulative transfers Ethereum | 510 (492 secondary, 96%) | Dune 2026-06-17 |
| Secondary transfer rate | ~0.43/day | Computed |
| INX ATS listing | Yes, no market making | Final Terms §3 |

**Particularity 1**: structural cap of CHF 100M per Final Terms limits scale by design. Smaller AUM is therefore not a market failure but a **deliberate issuance limit by the issuer**.

**Particularity 2**: the 96% secondary transfer ratio is the highest of the three products, a mechanical consequence of bIB01 being a freely transferable debt instrument rather than a whitelisted fund share. In absolute terms, however, 492 secondary transfers over three years (roughly one every two days) remains structurally indistinguishable from no market. The ratio is high because the denominator is tiny; the scoring matrix records this as a Conditional rather than a Fail on criterion C.2.

## Block C scoring: empirical validation

| Criterion | Framework verdict (regulatory text) | Empirical verdict (measured) | Strengthens or weakens? |
|---|---|---|---|
| C.1 Listed on developed exchange | Fail | Fail (BUIDL/OUSG: not listed; bIB01: ATS without market making) | **Strengthens** |
| C.2 Active and sizable market, volume dimension | Fail | Fail (BUIDL: $0 24h volume) | **Strengthens decisively** |
| C.2 Active and sizable market, concentration dimension | Fail (qualitative) | Fail (Gini 0.863, Top-3 = 55%) | **Strengthens** |
| C.3 Committed market makers | Fail | Fail (no on-chain MMs identified; AMM presence minimal due to whitelist) | **Strengthens** |

The empirical layer does not change the framework verdict. It strengthens the market-liquidity evidence, while the final classification remains subject to supervisory interpretation and the limitations stated in the article.

## Comparison with traditional HQLA proxies

Reference points, indicative orders of magnitude only (heterogeneous bases: onchain addresses vs beneficial owners, venue-reported vs interdealer volumes):

| Asset | Holders worldwide | Daily volume USD | Gini equivalent |
|---|---|---|---|
| 1-year US Treasury Bill | 100,000+ (via primary + secondary) | $500B+ | ~0.5 (illustrative) |
| Money market mutual fund (typical) | 1,000-50,000 | $50M-$1B | ~0.65 |
| iShares IB01 UCITS ETF | n/a (intra-exchange) | $1-10M | ~0.40 (ETF wrapper) |
| **BUIDL global** | ~150-200 | **$0 secondary** | **0.863** (reconstr.) |
| **OUSG** | ~80-100 | ~$50K | ~0.70 (est.) |
| **bIB01** | ~35-50 | ~$5K | ~0.65 (est.) |

The gap with traditional HQLA assets is two-to-four orders of magnitude on volume and holders count. **This is the structural disqualifier that the framework captures empirically.**

## How the article uses this layer

Section 5 of `../article/article.md` builds directly on these measurements: the $0 24h volume statistic for BUIDL leads the empirical argument, the Lorenz curve (Gini = 0.863, reconstruction) serves as the visual centerpiece against traditional HQLA benchmarks (Gini 0.40-0.65), and the secondary transfer rates (~4/day BUIDL, ~0.7/day OUSG, ~0.43/day bIB01) quantify the "trading metabolism" gap against assets that trade thousands of times per day across hundreds of venues.

## Limitations and roadmap

- **Concentration: measured constraints, reconstructed scalar** (v1.1). The per-holder export (query M2-bis) measures the cumulative shares directly (Top-3 = 55.2%, Top-10 = 83.0%, Top-25 = 99.5%) and the 25 smallest balances verbatim; the Gini of 0.863 is computed on a reconstruction under those constraints, and exact LP bounds give [0.850, 0.885] across all consistent distributions. The v1.0 Pareto estimate (anchored on the July 2024 Ondo OUSG ~35% observation) landed in the same region.

- **AUM time-series now plotted** (v1.1). See `../05_figures/aum_timeseries.png` and Figure 0 of the article. Anchor data points: Mar 2024 launch $0 → Apr 2024 $245M → Jul 2024 $502M → Aug 2025 $2.4B → May 2026 $2.28B (recent outflow phase noted).

- **Multi-chain aggregation not yet performed**. BUIDL is deployed on 8 chains; OUSG on 5; bIB01 on 5. Cross-chain holder de-duplication (same entity holding on multiple chains) requires entity-resolution heuristics. The Dune queries in `dune_queries.sql` cover Ethereum primarily; multi-chain extension is straightforward but increases complexity.

- **Settlement time distribution (query M5) requires Circle treasury wallet address mapping** to match BUIDL burns with USDC payouts. Not in public Securitize/Circle disclosures with sufficient precision; would require API integration.

## Files in this section

| File | Purpose |
|---|---|
| `dune_queries.sql` | SQL queries ready to execute on Dune Analytics |
| `lorenz_real_data.py` | Lorenz curve and Gini computation from the per-holder export |
| `market_comparison.py` | Four-panel Block C comparison figure |
| `aum_timeseries.py` | AUM trajectory figure |
| `DUNE_SETUP_GUIDE.md` | Step-by-step guide to reproduce the live dashboard |
| `../05_figures/lorenz_buidl.png` | Lorenz curve BUIDL with Gini = 0.863 (reconstruction) |
| `../05_figures/market_comparison.png` | 4-panel comparison BUIDL/OUSG/bIB01 on Block C metrics |
| `../05_figures/scoring_heatmap.png` | Final verdict heatmap, 24 criteria × 3 products |
| `empirical_findings.md` | This document |

## Next steps

The gradient analysis (what each product would need to change structurally to reach progressively higher HQLA eligibility, L0 → L3) is developed in `../03_gradient/gradient_deepdive.md`, including the BUIDL Level 1 hypothetical pathway under DR 2015/61 art. 10. Open empirical extensions are the two items above: multi-chain holder de-duplication and the M5 settlement time distribution.
