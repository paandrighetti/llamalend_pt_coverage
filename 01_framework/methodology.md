# Framework Methodology

**Version**: 1.0, 2026-05-11

This document explains the methodology underlying the RWA HQLA Eligibility Framework. It is intended to be read alongside the scoring matrix (`eligibility_matrix.md` / `.json`).

## Purpose

The framework provides a structured, auditable, and reproducible method for assessing whether a tokenised Real-World Asset qualifies as a High-Quality Liquid Asset (HQLA) under the Basel III Liquidity Coverage Ratio (LCR) framework, as transposed into EU law via the Capital Requirements Regulation (CRR) and Commission Delegated Regulation (EU) 2015/61.

The method is designed to be applied to any tokenised product, not only the three studied here (BUIDL, OUSG, bIB01).

## Regulatory basis

The framework derives its criteria from primary regulatory texts:

- **BCBS 238** (January 2013): Basel III, The Liquidity Coverage Ratio and liquidity risk monitoring tools. The foundational standard defining HQLA characteristics.
- **Regulation (EU) 575/2013 (CRR)**, Articles 411-419: the EU transposition of the LCR, including the definition of liquid assets and the operational requirements.
- **Commission Delegated Regulation (EU) 2015/61**, Articles 7-17: the detailed EU rules on HQLA eligibility, levels, haircuts, and operational requirements.
- **Regulation (EU) 2017/1129** (Prospectus Regulation): relevant for the legal characterisation of debt-instrument wrappers.
- **Regulation (EU) 2017/1131** (MMFR): relevant for the UCITS Money Market Fund pathway in the gradient analysis.
- **Regulation (EU) 2022/858** (DLT Pilot Regime): relevant for the settlement finality and DLT-issuance pathways.
- **Directive 98/26/EC** (Settlement Finality Directive): relevant for the settlement finality friction assessment.

## The four-block cascade

HQLA eligibility is assessed through four blocks, applied as a cascade for Block A and independently for Blocks B, C, and D.

### Block A: Eligibility category (cascading)

An asset must fall into a recognised HQLA category. The block tests, in order:
- A.1 Direct sovereign claim (Level 1 candidate), DR 2015/61 Art. 10(1)(a)-(d)
- A.2 UCITS look-through (Level 1/2A via Art. 15), DR 2015/61 Art. 15
- A.3 Corporate debt rated CQS1 (Level 2A candidate), DR 2015/61 Art. 12(1)(b)
- A.4 Level 2B equity in major index, DR 2015/61 Art. 14(b)

The cascade is closed by the first Fail at each level: if an asset is not a direct sovereign claim, it falls through to the UCITS test, then the corporate debt test, etc. If it fails all applicable tests, it fails Block A in aggregate and cannot qualify for any HQLA level.

### Block B: Operational requirements (independent)

- B.1 Unencumbered, DR 2015/61 Art. 7(2)
- B.2 Control by liquidity management function, DR 2015/61 Art. 8(2)
- B.3 Monetisation capacity within 30-day stress, DR 2015/61 Art. 7(2)
- B.4 Documented monetisation policy, DR 2015/61 Art. 8(3)
- B.5 Diversification at portfolio level, DR 2015/61 Art. 8(1)(c)

These are largely remediable through institutional arrangements (custody, policy, limits) and do not by themselves defeat eligibility.

### Block C: Market criteria (independent)

- C.1 Listed on developed and recognised exchange, BCBS 238 §24(c)
- C.2 Active and sizable market with low concentration, BCBS 238 §24(d)
- C.3 Committed market makers, BCBS 238 §24(d)
- C.4 Low bid-ask spread historical, BCBS 238 §24(e)
- C.5 Proven liquidity in stress, BCBS 238 §24(f)

Block C is validated empirically through the on-chain analysis (see `02_empirical/`).

### Block D: Wrapper-specific friction (framework contribution)

This block is the framework's contribution beyond the literal regulatory text, which predates tokenised wrappers. It identifies ten frictions:
- D.1 Settlement finality (SFD 98/26/EC compliance)
- D.2 Custody chain layers
- D.3 Oracle dependency for valuation
- D.4 Smart contract upgradeability
- D.5 Pause / freeze function
- D.6 Issuer Call Option / forced redemption
- D.7 Substitution of issuer without consent
- D.8 Liability cap / Extraordinary Event clauses
- D.9 Realization Event creditor cascade
- D.10 ECB collateral eligibility status

## Scoring scale

Each criterion is rated per product on a four-level scale:

- **Pass**, Criterion fully satisfied per primary regulatory text.
- **Conditional**, Potentially satisfied subject to specific operational arrangements (custody choice, contractual modification).
- **Fail**, Materially not satisfied.
- **N/A**, Criterion does not apply (e.g. equity criterion to a fund-share product).

## Verdict logic

The overall HQLA verdict requires:
- Pass in Block A (eligibility category), AND
- Pass in Block C (market criteria)

Block B Fails are typically remediable and do not alone defeat eligibility. Block D Fails are qualitative red flags for supervisory review and contribute to the distance-to-HQLA assessment.

## Auditability principle

Every cell in the matrix is anchored to either:
- A specific statutory provision (e.g. DR 2015/61 Art. 10(1)(a) for direct sovereign claim, CRR Art. 122 for unrated corporate treatment), OR
- A specific contractual clause from the product's primary documentation (Final Terms, Form D filing, Private Placement Memorandum, press release).

The methodology is designed to be auditable: each verdict should be traceable to a cited source and an explicit interpretation. The scoring still involves legal and supervisory judgement; the matrix makes that judgement inspectable rather than eliminating it.

## Reproducibility

To apply the framework to a new product:
1. Gather the product's primary documentation (prospectus, Final Terms, fund formation documents).
2. Assess each of the 24 criteria, citing the relevant source per cell.
3. Run the empirical analysis using the Dune queries (`02_empirical/dune_queries.sql`) adjusted for the new contract address.
4. Compute concentration metrics with `02_empirical/lorenz_real_data.py` and the measured constraints from the Dune queries.
5. Apply the verdict logic.

The matrix in JSON format (`eligibility_matrix.json`) is designed for programmatic re-application.

## Limitations

The framework is qualitative judgement based on regulatory text interpretation. Final supervisory verdicts (PRA, ACPR, BaFin, CSSF, etc.) may differ in specific cases. The framework is intended as an analytical guide, not regulatory advice. See the limitations section of `eligibility_matrix.md` for the full list of caveats.
