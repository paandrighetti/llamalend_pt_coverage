# RWA HQLA Eligibility Matrix: v1.1

**Framework**: Basel III LCR HQLA eligibility scoring for tokenised Real-World Assets
**Version**: 1.1, 2026-06-17 (scoring unchanged from v1.0 of 2026-05-11; empirical layer refreshed with measured Dune data)
**Scope**: BUIDL (BlackRock), OUSG (Ondo Finance), bIB01 (Backed Finance)
**Regulatory basis**: BCBS 238 (Jan 2013); CRR (EU) 575/2013 art. 411-419; Commission Delegated Regulation (EU) 2015/61 art. 7-17; EU Prospectus Regulation (EU) 2017/1129; ESMA Guidelines on eligible assets for UCITS.

## Scoring methodology

Each criterion is rated against three products on a 4-level scale:
- **Pass**, Criterion fully satisfied as per primary regulatory text.
- **Conditional**, Criterion potentially satisfied subject to specific operational arrangements (e.g. custody choice, contractual modification).
- **Fail**, Criterion materially not satisfied.
- **N/A**, Criterion does not apply (e.g. equity criterion to fund-share product).

Block A (Eligibility Category) is **cascading** (a conservative gating convention of this framework, not statutory language): any Fail closes the cascade for that level, and the asset fails Block A in aggregate. Blocks B, C, D are independent. Overall HQLA verdict requires Pass in A + Pass in B + Pass in C; Block D collects wrapper-specific frictions that may downgrade Level under qualitative supervisory review.

## Block A: Eligibility Category Cascade

Reference: DR 2015/61 art. 10-15; BCBS 238 §49-54.

### A.1: Direct sovereign claim (Level 1 candidate)
Reference: DR 2015/61 art. 10(1)(a)-(d); BCBS 238 §49.

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Fail | Token = interest in BVI fund Ltd, not direct claim on US Treasury. Investment Company Act §3(c)(7) excludes from 1940 Act. | Form D EDGAR 0002014390-24-000001 |
| OUSG | Fail | Token = interest in Delaware LP holding fund interests (incl. BUIDL), two-layer wrapping. | Ondo Regulatory Compliance Docs |
| bIB01 | Fail | Token = debt instrument (CFI DEMMRM) issued by Backed Assets (JE) Limited, tracking ETF price. No direct sovereign exposure. | bIB01 Final Terms 11 Jul 2025, ISIN CH1173294260 |

### A.2: UCITS look-through (Level 1/2A via art. 15)
Reference: DR 2015/61 art. 15; ESMA UCITS Eligible Assets Directive 2007/16/EC.

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Fail | BVI exempted fund is not a UCITS. No EU recognition or passport. | BlackRock BUIDL press release 13 Nov 2024 |
| OUSG | Fail | Delaware LP is not a UCITS. Holds BUIDL (also non-UCITS), Franklin/WisdomTree/Fidelity US funds (mostly 1940 Act, not UCITS). | Ondo OUSG Overview docs |
| bIB01 | Fail | bIB01 itself is a debt instrument, NOT a part of a UCITS. Holding bIB01 = holding a contractual debt of Backed Assets (JE) Limited referenced to UCITS price. Underlying iShares IB01 (ISIN IE00BGSF1X88) is a UCITS, but the investor does not own it. | bIB01 Final Terms 11 Jul 2025, §I |

### A.3: Corporate debt rated ≥ CQS1 (Level 2A candidate)
Reference: DR 2015/61 art. 12(1)(b); CRR Annex VI Credit Quality Steps.

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | N/A | Equity-like fund interest, not corporate debt. | n/a |
| OUSG | N/A | Equity-like fund interest. | n/a |
| bIB01 | Fail | Backed Assets (JE) Limited is unrated. Treatment under CRR art. 122 as corporate debt unrated → 100% risk weight under Standardised Approach. Disqualifies Level 2A (requires 20% RW). | bIB01 Final Terms; CRR art. 122 |

### A.4: Level 2B equity major index
Reference: DR 2015/61 art. 14(b).

All three products are N/A, none are equity instruments part of major indices.

### Block A aggregate verdict
| Product | Verdict |
|---|---|
| BUIDL | Not eligible for any HQLA level |
| OUSG | Not eligible for any HQLA level |
| bIB01 | Not eligible for any HQLA level |

## Block B: Operational Requirements

Reference: DR 2015/61 art. 7-8; CRR art. 417; BCBS 238 §28-43.

### B.1: Unencumbered (free transferability within 30-day stress)
Reference: DR 2015/61 art. 7(2); BCBS 238 §31.

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Fail | Whitelist KYC enforced on-chain; freeze function present; transferable only between Securitize-onboarded accounts. | BlackRock BUIDL disclosures |
| OUSG | Fail | "OUSG tokens may be freely transferred between any investors that have already onboarded to our Qualified Access Funds", restriction to whitelisted subset. | Ondo OUSG Overview |
| bIB01 | Fail | Smart contract pause function present; sanctions blocking via Chainalysis oracle; freezing function reserved for future upgrade; Issuer Call Option unilateral with 30 BD notice "without providing for a specific reason". | bIB01 Final Terms §II, §VI.iii |

### B.2: Control by liquidity management function
Reference: DR 2015/61 art. 8(2).

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Conditional | Self-custody possible if whitelisted (Anchorage Digital, Fireblocks, Coinbase Custody, BitGo compatible). Institutional treasury control achievable. | BUIDL ecosystem documentation |
| OUSG | Conditional | Same logic as BUIDL, institutional custody compatible. | Ondo docs |
| bIB01 | Conditional | Custody via Maerki Baumann or InCore Bank; self-custody possible whitelisted. Less institutional-grade than BUIDL/OUSG. | bIB01 Final Terms §1.1 |

### B.3: Monetisation capacity within 30-day stress
Reference: DR 2015/61 art. 7(2); BCBS 238 §28.

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Pass | USDC instant redemption via Circle (since 2024) + USD T+1 traditional. Validated under non-stress conditions. | BUIDL press release |
| OUSG | Pass | USDC instant + USD T+1. Daily NAV update at Business Day end. JPMorgan/Mastercard/Ripple cross-border pilot 6 May 2026 validates redemption rails. | Ondo OUSG docs |
| bIB01 | Conditional | Settlement T+5 maximum per Terms and Conditions. Slower than money market standards but compatible with 30-day window. Underlying Illiquidity clause may further delay. | bIB01 Final Terms §VI.v, §VIII |

### B.4: Documented monetisation policy
Reference: DR 2015/61 art. 8(3); BCBS 238 §39.

| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Conditional | Subscription/redemption mechanics documented in PPM (private). Public press release confirms USDC + USD routes. | PPM (not public); press releases |
| OUSG | Conditional | Detailed mint/redeem documentation in Ondo docs; instant limits documented. | Ondo OUSG Instant Limits docs |
| bIB01 | Conditional | Issuance and Redemption processes fully documented in Base Prospectus §VI (3 options for issuance, T+5 redemption). | bIB01 Final Terms §VI |

### B.5: Diversification at portfolio level
Reference: DR 2015/61 art. 8(1)(c); CRR art. 417(e).

This criterion applies at the *holding institution* level, not at the product level. For all three products: an institution holding only one issuer's tokens would fail diversification. Concentration of issuer is therefore an *institutional* risk, not a product-level one.

### Block B aggregate verdict
| Product | Score |
|---|---|
| BUIDL | Conditional-Fail (B.1 fail) |
| OUSG | Conditional-Fail (B.1 fail) |
| bIB01 | Fail (B.1 fail + B.3 conditional) |

## Block C: Market Criteria

Reference: BCBS 238 §24(c)-(f).

### C.1: Listed on developed and recognised exchange
| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Fail | "Interests in BUIDL have not been registered with the Securities and Exchange Commission and will not be listed on any exchange." (BlackRock disclosure verbatim) | BUIDL press release 13 Nov 2024 |
| OUSG | Fail | Not listed on any exchange. Secondary trading via Uniswap/CowSwap permissionless AMM only. | Ondo docs |
| bIB01 | Fail | Final Terms: "Initial offer without admission to trading / listing". Issuer "intends to admit at INX Securities, LLC" (US ATS) but with NO market making, NO liquidity guarantee. | bIB01 Final Terms §3, §B |

### C.2: Active and sizable market with low concentration
| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Fail | Primary market = redemption with issuer ($2.5-2.9B AUM). Secondary market = AMMs with typical daily volume <$1M. Not "deep and active" in BCBS sense. | RWA.xyz, Messari |
| OUSG | Fail | ~$770M AUM, secondary volume minimal. | RWA.xyz |
| bIB01 | Fail | Secondary volume documented near zero on standard data providers. Reported $250M+ AUM across Backed product suite. | CoinDesk, Bybit |

### C.3: Committed market makers
| Product | Score | Justification | Source |
|---|---|---|---|
| BUIDL | Fail | No committed market makers; collateral on Binance/Crypto.com/Deribit is not market making. | n/a |
| OUSG | Fail | No committed market makers. | n/a |
| bIB01 | Fail | "Market Maker: Not applicable", verbatim in Final Terms. | bIB01 Final Terms §1.1 |

### C.4: Low bid-ask spread historical
N/A for all, insufficient secondary market depth to compute representative bid-ask.

### C.5: Proven liquidity in stress (max drawdown 10% over 30-day stress)
N/A for all, insufficient track record (BUIDL since Mar 2024, OUSG since Jan 2023, bIB01 since 2023). No stress event of sufficient magnitude tested.

### Block C aggregate verdict
| Product | Score |
|---|---|
| BUIDL | Fail |
| OUSG | Fail |
| bIB01 | Fail |

## Block D: Wrapper-Specific Friction Assessment

Frictions not directly addressed by current DR 2015/61. Qualitative risk overlay for supervisory judgement.

### D.1: Settlement finality (SFD 98/26/EC compliance)
| Product | Score | Justification |
|---|---|---|
| BUIDL | Fail | Ethereum/Solana/etc. not designated as "system" under SFD 98/26/EC. Not operating under DLT Pilot Regime. |
| OUSG | Fail | Same. |
| bIB01 | Fail | Same. Ledger-based securities under Swiss art. 973d CO grants Swiss legal certainty but not SFD coverage. |

### D.2: Custody chain layers (number of intermediaries between token and underlying Treasury)
| Product | Layers | Detail |
|---|---|---|
| BUIDL | 2 | BNY Mellon custodian → BVI fund Ltd → token holder |
| OUSG | 3 | Underlying MMF custodians → Coinbase → Ondo I LP → token holder |
| bIB01 | 3 | State Street Ireland (UCITS custodian) → Maerki Baumann/InCore Bank (Backed custodian) → JE Limited → token holder |

### D.3: Oracle dependency for valuation
| Product | Score | Detail |
|---|---|---|
| BUIDL | Conditional | NAV published by Securitize; on-chain via RedStone. Single point of failure on Securitize attestation. |
| OUSG | Conditional | NAV updated end of Business Day, on-chain via Ondo Price Oracle. |
| bIB01 | Conditional | Chainlink Price Feed + SIX Swiss Exchange + London Stock Exchange as reference sources. Best documented. |

### D.4: Smart contract upgradeability (admin keys risk)
| Product | Score | Justification |
|---|---|---|
| BUIDL | Fail | Proxy upgradeable contracts; admin multisig held by Securitize. |
| OUSG | Fail | Upgradeable contracts. |
| bIB01 | Fail | "updating: ability to update the smart contract code", explicit per Terms and Conditions §II. Tokenizer Backed Finance AG controls. |

### D.5: Pause / freeze function
| Product | Score | Justification |
|---|---|---|
| BUIDL | Fail | Compliance freeze function present. |
| OUSG | Fail | Same. |
| bIB01 | Fail | "pausing: ability to stop all transfers of tokens" (active) + "freezing function" (reserved for future upgrade per §II). |

### D.6: Issuer Call Option / forced redemption clauses
| Product | Score | Justification |
|---|---|---|
| BUIDL | Standard fund mechanics | Redemption per PPM; not specifically unilateral termination clause documented publicly. |
| OUSG | Standard fund mechanics | Per Ondo terms. |
| bIB01 | **Fail** | Article VI.iii: Issuer Call Option exercisable with 30 BD notice, "without providing for a specific reason"; in stress, "Redemption Amount may be considerably lower compared to the issue price or the last valuation". |

### D.7: Substitution of issuer without investor consent
| Product | Score | Justification |
|---|---|---|
| BUIDL | Standard fund mechanics | Not documented publicly as unilateral. |
| OUSG | Standard fund mechanics | Same. |
| bIB01 | **Fail** | Article XXIV: "Issuer is entitled at any time and without the additional consent of the Investors to have itself substituted as the debtor for the Products by a new issuer". |

### D.8: Liability cap / Extraordinary Event clauses
| Product | Score | Justification |
|---|---|---|
| BUIDL | Standard limitation | Fund-level liability limitation per BVI law and PPM. |
| OUSG | Standard limitation | Per Ondo terms. |
| bIB01 | **Fail** | Article XVII: liability exclusion for "fraud, theft, cyber-attacks, drastic changes in regulation"; Redemption Amount "may be as low as the smallest denomination of the Settlement Currency (i.e. USD 0.01...)" upon Extraordinary Event. |

### D.9: Realization Event creditor cascade before investors
| Product | Layers before investors | Detail |
|---|---|---|
| BUIDL | 0 | BVI fund assets bankruptcy-remote; investors are residual claimants on fund assets directly. |
| OUSG | 0 | Same logic for Delaware LP fund structure. |
| bIB01 | **3** | Per Article XXII.ii: (1) Security Agent fees; (2) Paying Account Providers; (3) Custodian + Broker (pari passu) → THEN investors pro-rata. Plus "any other third parties' claims in connection with any realization and distribution costs". |

### D.10: ECB collateral eligibility status
| Product | Score | Justification |
|---|---|---|
| BUIDL | Not assessed (no formal declaration either way) | Implicit non-eligibility given BVI domicile and absence of EU notification. |
| OUSG | Not assessed | Same logic. |
| bIB01 | **Fail (explicit)** | Section 6 verbatim: "ECB eligibility: The Product is not expected to be ECB eligible." |

### Block D aggregate (count of Fails)
| Product | Fails | Conditionals |
|---|---|---|
| BUIDL | 3 | 2 |
| OUSG | 3 | 2 |
| bIB01 | **8** | 1 |

## Final synthesis

| Product | Block A | Block B | Block C | Block D | Overall HQLA verdict |
|---|---|---|---|---|---|
| BUIDL | Fail | Conditional-Fail | Fail | 3 fails | **Not HQLA** |
| OUSG | Fail | Conditional-Fail | Fail | 3 fails | **Not HQLA** |
| bIB01 | Fail | Fail | Fail | **8 fails** | **Not HQLA, additional contractual disqualifiers** |

### Distance-to-HQLA hierarchy
1. **BUIDL**, closest to HQLA-compatible structure. Strong fund framework (BlackRock fiduciary, BNY custody, bankruptcy-remote BVI exempted fund). Main gaps: not UCITS-equivalent, not listed, whitelist restrictions, BVI domicile.
2. **OUSG**, intermediate. Fund-of-funds structure adds a wrapping layer; SEC RIA manager but Delaware LP structure not equivalent to MMF UCITS.
3. **bIB01**, furthest from HQLA. Debt-instrument legal nature triggers CRR art. 122 unrated treatment, plus contractual clauses (Extraordinary Event $0.01 floor, unilateral Issuer Call, substitution clause, 3-layer creditor cascade, explicit non-ECB eligibility) compound the structural ineligibility.

## Roadmap to HQLA: gradient of eligibility

### L0: Status quo (current state, June 2026)
All three products fail Block A categorically. Frictions in Blocks B-D compound. Verdict: not eligible for any HQLA level.

### L1: UCITS-compatible wrapper
**Required structural change**: re-structure issuance as a UCITS MMF (Money Market Fund) under Regulation (EU) 2017/1131 (MMF Regulation), domiciled in an EU jurisdiction (Luxembourg, Ireland, France).

- BUIDL → Luxembourg UCITS MMF version. Precedent: Franklin Templeton OnChain U.S. Government Money Fund (BENJI) registered under US 1940 Act.
- OUSG → harder pivot due to fund-of-funds structure; would require flattening to direct holdings + UCITS MMF wrapper.
- bIB01 → would require radical reformulation from debt instrument to fund unit. Backed Assets is currently a debt issuer, not a fund manager. Effectively, this is a new product.

**Timeline**: 12-18 months for issuer; subject to FMA/CSSF/CBI authorisation.

**Resulting HQLA potential**: Level 1 or 2A via DR 2015/61 art. 15 UCITS look-through.

### L2: DLT Pilot Regime compliance
**Required structural change**: issuance via authorised DLT-SS or DLT-TSS under Regulation (EU) 2022/858. By March 2026, six DLT market infrastructures had been authorised under the regime; ESMA maintains the current list. None of BUIDL, OUSG, or bIB01 is analysed here as operating through an authorised DLT market infrastructure.

**Timeline**: 18-24 months; dependent on issuer execution, authorisation capacity, and legislative follow-up to ESMA's 2025 review of the regime.

**Resulting HQLA potential**: stronger settlement-finality and legal-certainty arguments. ECB collateral eligibility remains conditional on the asset satisfying the standard Eurosystem eligibility and settlement requirements; DLT issuance alone is insufficient.

### L3: Native sovereign DLT issuance
**Required structural change**: tokens issued directly by sovereign treasury (US Treasury, German Finance Ministry, France AFT) via authorised DLT-SS.

**Timeline**: 3-5 years. Precedents in trial: ECB Eurosystem trials on wholesale CBDC settlement 2024-2026; Banque de France TARGET Instant Payment Settlement on DLT.

**Resulting HQLA potential**: direct Level 1 sovereign claim (DR Art. 10(1)(a)-(d)); full ECB collateral eligibility; bankruptcy remoteness equivalent to traditional book-entry sovereign debt.

## Limitations and caveats

1. This framework is based on **public documentation only**. Private Placement Memoranda (PPMs) for BUIDL and Ondo I LP are not public; analysis relies on Form D filings, regulatory compliance pages, and issuer press releases.
2. The bIB01 Securities Note dated 8 May 2025 expired on 7 May 2026 per Article 12 of the Prospectus Regulation, before the publication date of this framework. No Successor Base Prospectus was published on the issuer's website at snapshot date. the First Supplement to the Registration Document dated 30 January 2026 discloses a material ownership change: Backed Finance AG is now 100% owned by Payward Europe Limited (Ireland), itself 100% owned by Payward, Inc. (US), i.e. Kraken. This change is consequential for the gradient analysis: Kraken lacks the UCITS management infrastructure that would be required for an L1 pivot.
3. Scoring is qualitative judgement based on regulatory text interpretation. Final supervisory verdict (PRA, ACPR, BaFin, CSSF, etc.) may differ in specific cases. Framework is intended as analytical guide, not regulatory advice.
4. Product structures evolve. BlackRock filed new tokenised fund offerings on 9 May 2026; any post-publication structural change requires framework re-application.
5. Stress event track record is insufficient (longest = BUIDL since March 2024). No supervisory-relevant 30-day stress observed. C.5 scoring is N/A.

## Sources

### Primary regulatory texts
- BCBS 238 (January 2013): Basel III, The Liquidity Coverage Ratio and liquidity risk monitoring tools
- Regulation (EU) 575/2013 (CRR), Articles 411-419, 122, 132
- Commission Delegated Regulation (EU) 2015/61, Articles 7-17
- Regulation (EU) 2017/1129 (Prospectus Regulation)
- Regulation (EU) 2017/1131 (MMF Regulation)
- Regulation (EU) 2022/858 (DLT Pilot Regime)
- Directive 98/26/EC (Settlement Finality Directive)

### Product-specific primary documents
- BUIDL: Form D filed 18 March 2024 (SEC EDGAR CIK 0002013810, filing 0002014390-24-000001)
- BUIDL: BlackRock press release 13 November 2024 (PRNewswire)
- OUSG: Ondo Regulatory Compliance documentation (docs.ondo.finance)
- OUSG: Form D Ondo I LP (referenced via StreetInsider, CIK pending direct EDGAR fetch)
- bIB01: Final Terms Nr. 5 dated 11 July 2025 (Backed Assets JE Limited, FMA-ID 351548)
- bIB01: Base Prospectus dated 8 May 2025 (Backed Assets, Liechtenstein FMA-approved, EU passport notified)

### Supervisory commentary
- ESMA Report on DLT Pilot Regime functioning (ESMA75-117376770-460, 25 June 2025)
- EBA Report on tokenised deposits (12 December 2024)
- AFME submission on DLT Pilot Regime (April 2025)

---

*Framework v1.1, 2026-06-17. Methodology open for iteration. Comments and supervisory feedback welcome.*
