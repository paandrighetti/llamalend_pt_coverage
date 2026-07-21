# RWA HQLA Framework

**A regulatory and empirical framework for assessing the High-Quality Liquid Asset (HQLA) eligibility of tokenised Real-World Assets under Basel III.**

[![Framework Version](https://img.shields.io/badge/version-1.1.1-blue)]() [![Snapshot](https://img.shields.io/badge/snapshot-2026--06--17-green)]() [![Methodology](https://img.shields.io/badge/methodology-open-orange)]()

---

## TL;DR

Three widely cited tokenised treasury products, BlackRock BUIDL, Ondo OUSG, and Backed bIB01, are evaluated against a 24-criteria HQLA eligibility framework derived from BCBS 238, CRR (EU) 575/2013, and Commission Delegated Regulation (EU) 2015/61.

**Verdict**: None of the three qualifies as HQLA Level 1, 2A, or 2B under Basel III LCR. The framework identifies the structural changes required to reach progressively higher eligibility levels (L0 → L3).

**Scope note**: independent analytical assessment under the stated framework and public documentation as of the snapshot date. This is not legal, regulatory, accounting, or investment advice; no affiliation with or endorsement by any issuer is implied; supervisory conclusions may differ in specific cases.

**Empirical layer**: On-chain analysis (snapshot 17 June 2026) shows that BUIDL has 76 holders on Ethereum mainnet (25 of them dust wallets, leaving 51 effective), a Gini coefficient of 0.863 (constrained reconstruction), bounded by linear programming to [0.850, 0.885] across all distributions consistent with the measured concentration constraints (Top-3 = 55% of supply, Top-25 = 99.5%), and approximately 4 secondary transfers per day averaged over 26 months. The market microstructure is materially more concentrated than that of traditional HQLA reference assets.

---

## What's in this repo

```
.
├── 01_framework/
│   ├── eligibility_matrix.md       # 24-criteria scoring matrix (Markdown)
│   ├── eligibility_matrix.json     # Structured scoring (JSON)
│   ├── methodology.md              # Framework methodology
│   └── scoring_heatmap.py          # Heatmap figure generator
│
├── 02_empirical/
│   ├── dune_queries.sql            # SQL queries for Dune Analytics
│   ├── lorenz_real_data.py         # Lorenz curve + Gini from holder export
│   ├── market_comparison.py        # Block C four-panel comparison figure
│   ├── aum_timeseries.py           # AUM trajectory visualisation
│   ├── DUNE_SETUP_GUIDE.md         # Reproduce the live Dune dashboard
│   └── empirical_findings.md       # Synthesis of empirical findings
├── data/
│   └── snapshot_metrics.json       # Canonical measured and estimated snapshot inputs
│
├── 03_gradient/
│   ├── gradient_deepdive.md        # L0 → L3 roadmap analysis
│   └── gradient_diagram.py         # Roadmap visualisation script
│
├── 04_implications/
│   ├── bank_implications.md        # Practical framework for treasurers
│   ├── haircut_calculator.py       # Internal haircut framework code
│   └── limits_matrix.json          # Default limits configuration
│
├── 05_figures/
│   ├── aum_timeseries.png/svg      # Reported AUM milestones; Backed line is product-suite, not bIB01-specific
│   ├── scoring_heatmap.png         # 24 criteria across 3 products heatmap
│   ├── lorenz_buidl.png (+_wide)   # BUIDL concentration Lorenz curve
│   ├── market_comparison.png       # Block C empirical validation
│   └── gradient_staircase.png/svg  # L0 → L3 roadmap visualisation
│
├── article/
│   └── article.md                  # Final publication article (~6600 words)
│
├── CHANGELOG.md                     # v1.0 → v1.1 measured-data refresh
├── LICENSE-CONTENT.md               # CC-BY-4.0 for content
├── LICENSE-CODE.md                  # MIT for code
└── README.md                        # This file
```

---

## Methodology

The framework operates on a **4-block cascade**:

| Block | Criteria | Reference |
|---|---|---|
| **A. Eligibility category** | Direct sovereign claim, UCITS look-through, Corporate debt CQS1, Level 2B equity | DR 2015/61 art. 10-15; BCBS 238 §49-54 |
| **B. Operational requirements** | Unencumbered, control, monetisation, documentation, diversification | DR 2015/61 art. 7-8; BCBS 238 §28-43 |
| **C. Market criteria** | Listed exchange, sizable market, committed MMs, low spreads, stress liquidity | BCBS 238 §24(c)-(f) |
| **D. Wrapper-specific friction** | Settlement finality, custody layers, oracle, upgradeability, pause function, issuer call, substitution, extraordinary event, creditor cascade, ECB eligibility | Framework v1.1 contribution |

Each criterion is rated per product on a Pass / Conditional / Fail / N/A scale, with primary legal reference and source documentation.

---

## Key findings

### Three products, three failure modes

| Product | Block A | Block B | Block C | Block D | Verdict |
|---|---|---|---|---|---|
| BlackRock BUIDL | Fail (cascade) | Conditional-Fail | Fail | 3 fails | **Not HQLA** |
| Ondo OUSG | Fail (cascade) | Conditional-Fail | Fail | 3 fails | **Not HQLA** |
| Backed bIB01 | Fail (cascade) | Fail | Fail | **8 fails** | **Not HQLA, additional contractual disqualifiers** |

### bIB01 as structural outlier

bIB01 fails five contractual disqualifiers that BUIDL and OUSG do not:
- Article XVII Extraordinary Event: redemption can fall to $0.01
- Article VI.iii unilateral Issuer Call with 30 BD notice
- Article XXIV substitution of issuer without investor consent
- Article XXII three-layer creditor cascade before investors
- Section 6 explicit "Product not expected to be ECB eligible"

### Empirical validation of Block C

BUIDL on Ethereum mainnet, snapshot 17 June 2026:
- 76 holders (roughly 25 dust wallets, ~51 effective)
- $181M onchain AUM (approximately 8% of $2.28B multi-chain global; the bulk has migrated to Solana and other chains)
- 14,046 cumulative transfers, of which 3,151 secondary (~4 secondary transfers per day)
- Gini coefficient: **0.863** (constrained reconstruction; exact bounds [0.850, 0.885]; Top-3 = 55%, Top-10 = 83%, Top-25 = 99.5%)

Direct comparison with traditional securities is not like-for-like: blockchain addresses are not equivalent to beneficial owners or brokerage accounts. The on-chain metrics are therefore used as product-level evidence, not as a harmonised cross-market Gini benchmark.

---

## The gradient L0 → L3

| Level | Description | Timeline | Resulting eligibility |
|---|---|---|---|
| **L0** | Status quo (June 2026) | Today | Not HQLA |
| **L1** | UCITS MMF restructuration | 12-30 months | HQLA Level 1/2A via Art. 15 look-through |
| **L2** | DLT-issued via authorised CSD | 6-24 months | Potential ECB collateral route for assets that also satisfy the standard eligibility and settlement criteria |
| **L3** | Native sovereign DLT | 5-7 years | Direct Level 1 HQLA |

The L1+L2 combination (24-36 months) is the most credible institutional roadmap for BUIDL, with BlackRock as the natural executor given its existing UCITS infrastructure in Luxembourg and Ireland.

---

## Practical framework for treasurers

For bank treasurers needing to handle tokenised RWA exposures today (not HQLA but not excluded):

**Internal haircut framework** (cumulative 23-40% over book value):
- Custody chain risk: 5-10%
- Settlement finality risk: 10-15%
- Contract upgradeability risk: 3-5%
- Issuer concentration risk: 5-10%

**Internal limits matrix** (to calibrate per ALM committee):
- Single-product cap: 5% of total liquid assets
- Single-issuer cap: 10% of total liquid assets
- Single-chain cap: 25% of tokenised RWA
- Single-custodian cap: 33% of tokenised RWA
- Total tokenised RWA cap: 1-2% of total liquid assets

---

## Limitations and caveats

1. Framework is based on publicly available documentation. Private Placement Memoranda for BUIDL and Ondo I LP are not public.
2. bIB01 Securities Note dated 8 May 2025 expired 7 May 2026; no successor base prospectus was published at the snapshot date, and the issuer (Backed Finance AG) was acquired by Kraken in January 2026. Verify the current prospectus status before relying on the Block D analysis.
3. Empirical snapshot is 17 June 2026; products evolve fast.
4. The framework is one analyst's contribution. Final supervisory verdict may differ in specific cases.
5. The "if I were the treasurer" section reflects analytical reasoning, not the operational practice of any specific institution.

---

## How to use this repo

### For regulatory analysts
- Read `01_framework/eligibility_matrix.md` for the verdict and reasoning
- Cite primary sources from each cell of the matrix
- Apply the framework to new products by re-running the 24-criteria assessment

### For DeFi risk analysts
- Use `02_empirical/dune_queries.sql` to run real-time concentration metrics
- Adapt `02_empirical/lorenz_real_data.py` and the Dune queries for new products
- Track AUM, holder concentration, and transfer activity quarterly

### For bank treasurers
- Use `04_implications/bank_implications.md` as a working framework
- Calibrate the haircut and limits per your ALM committee judgement
- Monitor the regulatory checklist quarterly

### For students and researchers
- The matrix encodes the BCBS/CRR HQLA framework in machine-readable JSON
- `02_empirical/lorenz_real_data.py` demonstrates Gini, exact LP bounds, and Lorenz curve computation
- The gradient diagram shows the regulatory evolution path

---

## Reproducibility

To reproduce the empirical analysis:

```bash
pip install -r requirements.txt

python 01_framework/scoring_heatmap.py       # verdict heatmap from the JSON matrix
python 02_empirical/lorenz_real_data.py      # prints Gini 0.863 and recomputes the exact LP bounds [0.850, 0.885]
python 02_empirical/market_comparison.py
python 02_empirical/aum_timeseries.py
python 03_gradient/gradient_diagram.py
```

All five scripts embed their measured inputs and run offline; figures are written to `05_figures/`.

To extract live on-chain data:
1. Open a Dune Analytics account
2. Copy queries from `02_empirical/dune_queries.sql`
3. Adjust contract addresses if needed (verify via Etherscan)
4. Compare the exported values against the constants embedded in the scripts

---

## Dune dashboard

A live dashboard tracking the metrics in this framework is available at: https://dune.com/bandulf/rwa-hqla-framework-live-metrics.

The dashboard tracks:
- AUM time-series for BUIDL, OUSG, bIB01
- Holders concentration (Gini coefficient, Top-10 share)
- Daily transfer activity
- Primary vs secondary volume ratio
- Cross-chain distribution

---

## Citing this work

If this framework informs your research or analysis, please cite:

> Pierre-Antoine Andrighetti. (2026). *RWA HQLA Framework v1.1: A regulatory and empirical assessment of tokenised treasury HQLA eligibility.* https://github.com/paandrighetti/RWA_analysis

---

## Contributing

This framework is intended as a first version, an opening contribution to an analytical debate. Constructive challenges and methodological improvements are welcome via GitHub issues or pull requests.

Topics where peer feedback would be particularly valuable:
- Block A.2 UCITS look-through interpretation (especially for OUSG fund-of-funds structure)
- Block C empirical thresholds (what would qualify as "sizable market" quantitatively)
- Block D weighting scheme (currently all fails are equal; some may deserve higher weight)
- ICAAP capital allocation methodology for tokenised RWA exposures

---

## License

- **Content** (Markdown documents, framework methodology): Creative Commons Attribution 4.0 (CC-BY-4.0)
- **Code** (Python scripts, SQL queries): MIT License

---

## Acknowledgements

This framework synthesises primary regulatory texts from:
- Basel Committee on Banking Supervision (BCBS)
- European Banking Authority (EBA)
- European Securities and Markets Authority (ESMA)
- European Central Bank (ECB)
- US Federal Reserve / OCC / FDIC

The empirical layer relies on data from:
- Etherscan
- CoinGecko
- RWA.xyz
- Dune Analytics
- 21co Tokenization Government Securities dashboard

---

## Contact

https://www.linkedin.com/in/pierre-antoine-andrighetti
https://x.com/bandulf
p.a.andrighetti@gmail.com
