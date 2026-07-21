# S6: Implications for Bank Treasurers: A Practical Framework

**Version**: 1.0, 2026-05-11
**Status**: source material for Section 7 of article (target 400 words in final draft, full content here is ~2200 words)
**Editorial voice**: analytical for framework sections, first-person for recommendations ("If I were the treasurer today...")
**NDA scope**: strictly limited to hypothetical analyst reasoning; no reference to specific institutional practices

## Why this section matters

Tokenised treasuries are not HQLA today. But they are not excluded from a European or US bank's balance sheet either. Treasurers and ALM teams need a working classification, valuation, and limits framework, *now*, pending the regulatory evolution described in Section 6 (gradient). The absence of an authoritative prudential treatment does not absolve treasurers of the need to make decisions.

This section proposes a practical framework, with explicit numerical proposals that should be re-calibrated by each institution's ALM committee.

## 7.1: Current prudential classification

### Where tokenised treasuries fit in the LCR

Under Regulation (EU) 575/2013 (CRR), the Liquidity Coverage Ratio is computed as: HQLA / Net Cash Outflows over 30-day stress. As established in Sections 4-5, tokenised treasuries (BUIDL, OUSG, bIB01) currently fail Block A and Block C tests for HQLA inclusion. The mechanical consequence:

- **Numerator (HQLA)**: zero contribution. Tokenised treasury holdings cannot be included as Level 1, 2A, or 2B HQLA. They are reported "outside" the LCR numerator.
- **Denominator (Net Cash Outflows)**: no direct impact. Holdings do not create outflow obligations.
- **COREP C72 (liquid assets template)**: non-eligible instruments simply do not enter the C72 liquid-asset rows; there is no catch-all "other assets" HQLA line for them. Any monitoring of the position happens outside the HQLA stack (internal reporting and, where applicable, additional monitoring metrics), which is precisely the operational consequence of ineligibility.

### ILAAP and internal liquidity reporting

Within the Internal Liquidity Adequacy Assessment Process, tokenised treasuries should be classified in a distinct category:

- *Not* cash and equivalents (insufficient settlement finality, restricted transferability)
- *Not* sovereign debt holdings (wrapper introduces issuer and operational risk)
- *Not* conventional corporate bonds for prudential bucketing: bIB01 is issuer debt (a tracker certificate), so the exposure class and risk weight must be confirmed under the applicable CRR provisions rather than assumed
- A new category: "Tokenised RWA" or "Digital Asset Backed Securities", with sub-classification by product type (fund share, debt instrument, structured note)

This classification choice has knock-on effects: internal stress testing, contingency funding plan, ICAAP/ILAAP risk categorisation (capital and operational aspects sit in ICAAP; liquidity, survival horizon and buffer policy sit in ILAAP). The treasury function should treat the establishment of this new category as a deliberate ALM committee decision, not a default operational classification.

### What this means in practice

A €50 million BUIDL holding by a European bank today:
- Contributes €0 to the LCR numerator
- Does not increase outflow obligations
- Should appear in internal liquidity reports under a "Tokenised RWA" line
- Requires a distinct ALM treatment justification documented in policy
- Is subject to operational risk monitoring per ICAAP

The €50 million is therefore a *yielding* asset (with returns aligned to short-term US Treasury yields) that contributes to balance sheet productivity but provides zero regulatory liquidity relief. This is the central trade-off treasurers face.

## 7.2: Internal haircut framework

### The valuation challenge

Since tokenised treasuries are not HQLA, the standard regulatory haircuts (0% Level 1, 15% Level 2A, 25-50% Level 2B) do not apply by reference. But treasurers nonetheless need a way to value the asset for internal liquidity buffer purposes, particularly if the holding is to be considered part of a *contingency* liquidity reserve (even if not LCR-eligible).

I propose an internal haircut framework composed of four risk premiums, each adjustable per product and per ALM committee judgement:

| Risk component | Haircut range | Rationale |
|---|---|---|
| Custody chain risk | 5-10% | Reflects intermediaries between token and underlying Treasury (BUIDL: 2 layers, OUSG: 3, bIB01: 3). More layers = higher haircut. |
| Settlement finality risk | 10-15% | No SFD coverage; settlement legally finalized at chain confirmation, vulnerable to reorganisation in extreme cases. |
| Contract upgradeability risk | 3-5% | Admin keys risk; pause/freeze functions could be triggered by issuer in stress |
| Issuer concentration risk | 5-10% | Single fund manager (BlackRock for BUIDL), single tokenisation provider (Securitize, Backed Finance), single chain dominance |
| **Cumulative range** | **23-40%** | Envelope across profiles, aggregation method (additive is the conservative bound) and stress overlay; the coded presets sit at roughly 27-32% multiplicative before overlay |

These are not regulatory haircuts. They are internal management adjustments to reflect wrapper-specific risks that the regulatory framework does not yet price.

### Reference points for calibration

For comparison:
- Level 2B HQLA receives a regulatory 25-50% haircut for fully eligible assets
- A typical bank's internal buffer haircut on a Money Market Fund unit (not HQLA-eligible) is 10-15%
- A typical bank's internal haircut on corporate bonds rated CQS2 (not HQLA-eligible) is 10-20%

A cumulative 20-30% internal haircut on tokenised treasuries places them somewhere between an MMF unit and a Level 2B HQLA asset, reflecting their structural distance to true sovereign exposure.

### Adjustment dynamics

The haircut should not be static. I would propose:
- **Quarterly recalibration** by the ALM committee
- **Stress event trigger**: if a smart contract bug, oracle failure, custody event, or pause function is exercised on the holding, an emergency haircut increase of 10-20 percentage points should be applied pending full reassessment
- **Regulatory evolution monitoring**: when a product reaches L1 status (UCITS MMF), the haircut should reduce by 10-15 percentage points
- **ECB collateral eligibility**: products that achieve L2 status (DLT-PR via authorised CSD, operational since 30 March 2026) should see a reduction of 5-10 percentage points

## 7.3: Internal limits matrix

### Why limits matter more than haircut

A 25% haircut on a €10 million holding means little. A 25% haircut on a €500 million holding means significant capital and liquidity impact. Concentration limits are the primary control mechanism for tokenised treasury exposure.

I propose the following limits structure as a starting point, chiffres à calibrer selon ALM committee:

| Limit | Proposed cap | Rationale |
|---|---|---|
| Single-product cap (e.g., BUIDL alone) | 5% of total liquid assets | Avoid material exposure to a single wrapper + issuer |
| Single-issuer cap (e.g., BlackRock-managed) | 10% of total liquid assets | Avoid management concentration |
| Single-chain cap (e.g., Ethereum-deployed) | 25% of total tokenised RWA | Diversify chain risk |
| Single-custodian cap (e.g., Anchorage, Fireblocks) | 33% of total tokenised RWA | Diversify operational custody risk |
| Total tokenised RWA cap | 1-2% of total liquid assets | Aggregate cap pending regulatory clarity |

### Calibration logic

The 1-2% aggregate cap reflects the analytical reality: until products reach L1 status, tokenised treasuries should be a yield-enhancement allocation, not a structural liquidity reserve. Even at 2% of liquid assets, a €100 billion bank would have €1-2 billion exposure, non-trivial in absolute terms, sufficient for treasury yield optimisation, but bounded in systemic terms.

The single-product cap of 5% is more permissive at the granular level because internal diversification within the tokenised RWA bucket is harder than diversification across the wider liquid asset universe.

### Caveat: to calibrate per institution

These numbers are starting points. They should be adjusted by ALM committee based on:
- Institution size and complexity
- Existing liquid asset diversification
- Risk appetite framework
- Regulatory dialogue with home supervisor (ACPR, BaFin, CSSF, etc.)
- Operational maturity (custody, monitoring, audit)

A G-SIB might tighten these caps further (e.g., 0.5% aggregate). A neo-bank with a different risk profile might find them appropriate as-is or might choose a different framework altogether. Fintechs operating without the LCR constraint can use this framework as inspiration but should adapt to their specific cash management context.

## 7.4: Regulatory monitoring checklist

Treasurers should establish a quarterly monitoring routine on the following indicators:

### EU supervisory developments
- EBA work programme on tokenised HQLA classification
- ECB collateral framework evolution post-30 March 2026 (which subsets of DLT-based assets become eligible next)
- ESMA review of UCITS Eligible Assets Directive (the review starts 2026, conclusion expected 2027)
- ESMA monitoring of MiCAR implementation impact on tokenised assets

### Global supervisory developments
- BCBS work programme on cryptoasset prudential treatment (BCBS 538 + follow-up consultations)
- FSB recommendations on tokenisation
- IOSCO standards on tokenised funds

### US supervisory developments
- FRB/OCC/FDIC interagency guidance evolution post-March 2026 joint FAQ
- SEC Division of Investment Management positions on tokenised funds
- FINRA expectations on broker-dealer activity in tokenised securities
- Federal Reserve Wholesale Settlement work programme

### Market evolution indicators
- New product launches (Superstate, Hashnote, OpenEden, etc.) and their structural choices
- Existing product restructurings (BUIDL share class additions, OUSG fund-of-funds composition changes)
- Cross-border settlement pilots (JPMorgan / Mastercard / Ripple type collaborations)
- DLT Pilot Regime authorisation pipeline (six infrastructures authorised by March 2026; current list maintained by ESMA)

## 7.5: ICAAP/ILAAP risk category mapping

The Internal Capital Adequacy Assessment Process should explicitly map tokenised RWA exposures to standard risk categories:

| ICAAP risk category | Specific risk for tokenised RWA | Mitigation / control |
|---|---|---|
| Liquidity risk | Settlement may delay beyond 30-day window under stress (T+1 BUIDL, T+5 bIB01); whitelist counterparty acceptance may freeze under stress | Internal haircut framework (7.2); single-product caps (7.3); monthly redemption stress testing |
| Market risk | Wrapper-specific basis risk between NAV and on-chain price; oracle valuation lag | Mark-to-NAV with daily reconciliation; oracle quality monitoring |
| Operational risk | Smart contract bug; oracle failure; custody key compromise; chain reorganisation | Custody chain diligence; bug bounty awareness; multi-signature governance; chain selection limited to mature L1 chains |
| Concentration risk | Single issuer / chain / custodian dominance | Internal limits matrix (7.3) |
| Legal risk | Non-bankruptcy-remote structure for some products (bIB01 creditor cascade); jurisdictional uncertainty (BVI for BUIDL, Jersey for bIB01) | Pre-investment legal opinion; documentation review per ALM committee |
| Reputation risk | Public chain transparency means all holdings are visible to competitors and journalists | Communication strategy; coordinated disclosure |

Liquidity-dimension items above belong to the ILAAP; the total ICAAP capital allocation for tokenised RWA exposures should reflect the cumulative materiality of these risks. For a typical European bank holding tokenised treasuries at 1-2% of liquid assets, this would translate to a marginal capital impact under Pillar 2.

## 7.6: "If I were the treasurer today"

As an analytical exercise, here is how I would approach tokenised treasury allocation as a hypothetical treasurer at a European bank in May 2026:

**Decision 1, Whether to allocate at all**. The opportunity cost of *not* allocating any treasury cash to tokenised products is the foregone yield enhancement, typically 25-50 basis points above traditional MMF returns once operational costs are factored in. For a bank with €100 billion liquid assets, even a small allocation generates meaningful incremental income. The decision to allocate should be based on: (a) operational maturity of custody and reporting infrastructure, (b) ALM committee comfort with the wrapper-specific risks documented in this framework, (c) strategic positioning for the regulatory evolution toward L1/L2 eligibility. I would allocate modestly (~1% of liquid assets) for the first 12-18 months, with capacity to scale to 2-3% as the framework matures.

**Decision 2, Which products**. I would choose BUIDL as the primary allocation (~70% of tokenised RWA bucket) because of its closest structural distance to HQLA, BlackRock fiduciary, BNY Mellon custody, and clear path to L1 via UCITS restructuring. OUSG would be a secondary allocation (~30%) for diversification. I would explicitly *avoid* bIB01 because of the five contractual disqualifiers documented in Section 4 (Block D fails), particularly the Article XVII Extraordinary Event $0.01 floor and the three-layer creditor cascade.

**Decision 3, Custody arrangement**. Self-custody via Anchorage Digital Bank (US OCC-chartered) or Fireblocks (with appropriate insurance) for institutional-grade key management. I would explicitly *avoid* exchange-based custody (Coinbase Custody is acceptable as second-tier but adds counterparty risk). The custody choice has direct implications for the operational risk haircut.

**Decision 4, Chain selection**. Ethereum mainnet only for the initial allocation. Multi-chain deployment (Solana, Polygon, Arbitrum) adds operational complexity without proportionate yield benefit. The single-chain concentration is acceptable at the modest aggregate allocation level (1-2% of liquid assets).

**Decision 5, Monitoring infrastructure**. I would build (or buy) an internal dashboard that tracks: real-time NAV vs on-chain price; daily transfer volume on the contract; holder concentration metrics; custody key health; regulatory news flow. The dashboard cost is justified by the operational risk exposure.

**Decision 6, Exit strategy**. Any of the following triggers would prompt immediate liquidation: smart contract pause beyond 24 hours; oracle failure; custody breach; product Extraordinary Event clause invocation; aggregate exposure exceeding 2.5% of liquid assets (10% over policy cap); regulatory enforcement action against the issuer.

This is the analytical exercise as it would be performed by a hypothetical treasurer. The actual decisions of any specific institution will depend on its risk appetite, ALM committee judgement, supervisor dialogue, and operational maturity.

## What this means for the article narrative

Section 7 (Implications) of the article should:

1. **Lead with the LCR mechanics**: tokenised RWA contributes zero to HQLA numerator today. State this clearly.
2. **Propose the haircut framework**: 20-30% cumulative internal haircut, with the four-component breakdown for analytical credibility
3. **Anchor with the limits matrix**: 5% single product, 10% single issuer, 25% single chain, 33% single custodian, 1-2% aggregate. Caveat: à calibrer per institution.
4. **Close with the "if I were the treasurer" exercise**: 6 decisions, brief justification each. This is the section that distinguishes the article from generic regulatory analysis.
5. **Avoid CASA-specific references**: the entire content is hypothetical analyst reasoning. No claim about any institution's actual practice.

## Caveats and limitations

1. This framework is one analyst's proposal. Other analysts may propose different cap percentages, haircut compositions, or product preferences with equally defensible rationales.
2. The framework reflects June 2026 product structures. Regulatory evolution toward L1/L2 will materially change the framework parameters (lower haircuts, possibly higher caps).
3. The framework focuses on European prudential context (CRR, DR 2015/61, ECB collateral framework). US bank treasurers operating under FRB/OCC/FDIC technology-neutral guidance (March 2026) have a different starting point and may calibrate differently.
4. Fintechs and neo-banks not subject to LCR have more operational flexibility but should still consider the haircut and limits framework for prudent treasury management.

## Sources

- Regulation (EU) 575/2013 (CRR), Articles 411-419
- Commission Delegated Regulation (EU) 2015/61, Articles 7-17
- EBA Guidelines on ILAAP
- BCBS 238 (January 2013): Basel III LCR
- BCBS 538: Prudential treatment of cryptoasset exposures (December 2022, updated 2025)
- ECB Press Release 27 January 2026: DLT-based collateral eligibility
- FRB/OCC/FDIC Joint FAQ 5 March 2026: Capital Treatment of Tokenized Securities
- ESMA Report on DLT Pilot Regime functioning (ESMA75-117376770-460, 25 June 2025)
