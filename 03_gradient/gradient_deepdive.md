# S5: The Gradient of Eligibility: What Would It Take?

**Version**: 1.0, 2026-05-11
**Status**: source material for Section 6 of article (target 600 words in final draft, full content here is ~2000 words)
**Focus**: BUIDL specifically as primary case study, with cross-references to OUSG and bIB01 where relevant.

## Framework reminder

The S3 verdict closed at L0: no tokenised RWA product currently qualifies as HQLA. The gradient describes the structural evolutions required to reach progressively higher levels of eligibility.

| Level | Description | Required structural change | Resulting potential |
|---|---|---|---|
| **L0** | Status quo | Today | Not HQLA, not ECB-eligible |
| **L1** | UCITS-compatible MMF wrapper | Restructure issuance as authorised UCITS MMF under MMFR (2017/1131) | Level 1 or 2A HQLA potential via DR 2015/61 Art. 15 look-through |
| **L2** | DLT-issued via authorised CSD | Token issuance via CSD using DLT-based services, T2S-reachable | ECB collateral eligibility (operational since 30 March 2026) |
| **L3** | Native sovereign DLT issuance | Sovereign treasury issues debt natively on DLT-SS | Candidate Level 1 HQLA + ECB eligibility, subject to the usual issuer/claim/currency/operational criteria |

The critical update for this version: **L2 has moved from prospective to operational on 30 March 2026** following the ECB Governing Council decision of 27 January 2026.

## L1: UCITS MMF restructuration

### The structural change required

Convert BUIDL from a §3(c)(7)-exempt BVI fund into an EU-authorised UCITS Money Market Fund under Regulation (EU) 2017/1131 (MMFR). The legal target structure:

- **Fund vehicle**: UCITS Public Debt Constant NAV MMF (Short-Term)
- **Authorisation**: CSSF (Luxembourg) or Central Bank of Ireland, these are the two jurisdictions where Public Debt CNAV is allowed; France only permits VNAV which adds complexity for the $1.00 stable-value design
- **Investment Manager**: BlackRock Asset Management Ireland Limited or BlackRock (Luxembourg) S.A. would act as ManCo, both are existing entities with UCITS infrastructure in place. BlackRock has the institutional capacity to execute this restructuring without external dependencies
- **Depositary**: EU credit institution under CRR Article 401 (BNY Mellon has Luxembourg/Ireland branches that qualify; alternatively State Street Bank International, J.P. Morgan SE)
- **Custodian**: same EU credit institution acting as depositary
- **Distribution**: UCITS passport into 30 EEA states

### Why this would unlock HQLA Level 1 or 2A potential

Under DR 2015/61 Article 15, holdings of UCITS units are HQLA-eligible **subject to look-through** to the underlying assets. The look-through means:
- If the UCITS holds 99.5%+ US Treasuries (Rule 2a-7-equivalent for EU), the holder gets approximately Level 1 treatment proportional to the Treasury exposure
- Combined cap per institution: 500 M€ across all UCITS HQLA holdings (Art. 15(2))

The Level 1 vs 2A determination depends on the specific MMFR sub-category and the look-through application, supervisory judgement may differ across NCAs.

### The Franklin BENJI precedent (and its limits)

Franklin Templeton's OnChain U.S. Government Money Fund (FOBXX, BENJI) is the leading existing precedent. It is a regulated 1940 Act fund that invests at least 99.5% of its total assets in government securities, cash and repurchase agreements collateralized fully by government securities or cash, structured as a Rule 2a-7 Government MMF.

Critical differences with BUIDL:
- BENJI is **US 1940 Act registered**, accessible to **US retail investors** via Benji Investments app
- BUIDL is **§3(c)(7) exempt**, restricted to US Qualified Purchasers ($5M minimum)
- BENJI uses **public blockchain as system of record** for share ownership, a fundamentally different architecture from BUIDL's permissioned token wrapping
- AUM: BENJI ~$700M (Jul 2025), BUIDL ~$2.4B (May 2026)

**The lesson**: BENJI demonstrates that a public-blockchain MMF can operate under a registered fund framework (US 1940 Act). The EU equivalent, a UCITS Public Debt CNAV MMF using public blockchain as system of record, **does not yet exist**.

This is the gap L1 proposes to fill. The MMFR regime since 2018 has been used for hundreds of traditional MMFs in Luxembourg and Ireland; the technical pathway is well-documented. What is missing is regulatory comfort with public blockchain as the system-of-record technology.

### Timeline and execution feasibility

- Optimistic case: 12-18 months from BlackRock filing to CSSF/CBI authorisation
- Realistic case: 18-30 months including IT integration, custodian onboarding, and audit
- Constraint: Public blockchain as system of record requires regulatory dialogue with NCA. FCA CP25/28 (October 2025) shows UK direction, EU pace likely slower

### Why bIB01 and OUSG cannot easily follow this path

- **bIB01**: legally a debt instrument under EU Prospectus Regulation. The UCITS path would require **abandoning the tracker certificate structure** and creating a new fund vehicle. Effectively a new product, not a restructuring. Backed Finance has no fund management infrastructure.
- **OUSG**: fund-of-funds structure compounds the problem. Either Ondo flattens to direct holdings (loses BlackRock partnership economics), or Ondo restructures the Delaware LP into a Luxembourg AIF (loses §3(c)(7) US accessibility). Neither is simple.

## L2: DLT-issued via authorised CSD

### What changed on 30 March 2026

On 27 January 2026, the ECB announced that the Eurosystem will accept marketable assets issued in CSDs using DLT-based services as eligible collateral for Eurosystem credit operations as of 30 March 2026. The eligibility criteria:

- Asset must be issued in an EU-authorised CSD
- CSD uses DLT-based services for issuance/settlement
- Asset is reachable via TARGET2-Securities (T2S)
- Asset complies with standard Eurosystem collateral eligibility criteria

This is *not* HQLA eligibility under Basel III, it is **central bank collateral eligibility**, a distinct regulatory concept. But practically, for a treasurer:
- ECB-eligible collateral can be repo'd at the ECB facility, generating monetary access at central bank rates
- This is the closest functional equivalent to HQLA Level 1 status (in the *liquidity* sense, not the *prudential* sense)
- Sub-divisions of LCR Level 1 are not affected, but the asset becomes meaningfully more useful in liquidity management

### Current state of DLT Pilot Regime authorisations

Six DLT market infrastructures had been authorised under the DLT Pilot Regime by March 2026. ESMA maintains the current list; the examples below are illustrative rather than exhaustive:
- **CSD Prague**: DLT-SS, authorised 11 October 2024
- **21X AG**: DLT-TSS, authorised 3 December 2024, operates on Polygon
- **360X AG**: DLT-MTF, authorised 29 April 2025

The European Commission's package proposed in December 2025 includes amendments to remove volume limits and increase flexibility, addressing the structural problems of the original regime (the €6 billion volume cap discouraged large players).

### What BUIDL would need to do for L2

Option A, Issue through an existing DLT-PR authorised infrastructure:
- BlackRock contracts with CSD Prague or 21X AG to issue a new share class of BUIDL via their DLT-SS or DLT-TSS
- The "BUIDL on Ethereum" model is preserved technically, but the *securities registration* moves under the EU CSD framework
- Existing US §3(c)(7) BUIDL holders remain on the legacy structure; EU institutional holders access through the new share class
- Timeline: 6-12 months once partnership signed

Option B, BlackRock applies for DLT-PR authorisation directly:
- Higher infrastructure investment
- Higher control over the stack
- Timeline: 18-24 months minimum

The L2 path is **significantly faster than L1 for HQLA** because it does not require restructuring the fund vehicle itself, only the issuance and settlement layer. **But it does not, by itself, deliver HQLA Level 1 status under Basel III LCR.** It delivers ECB collateral eligibility, which is materially valuable but legally distinct.

### What this means for the L1+L2 combination

A BUIDL UCITS MMF (L1) issued via 21X AG DLT-TSS (L2) would simultaneously hold:
- HQLA Level 1 or 2A potential under DR 2015/61 Art. 15
- ECB collateral eligibility from 30 March 2026 framework
- Settlement finality opposable under EU law via DLT Pilot Regime exemptions

This is the most credible 24-36 month target structure. It does not require sovereign issuance changes; it builds on existing regulatory infrastructure.

## L3: Native sovereign DLT issuance

### The Eurosystem dual-track strategy

The ECB Governing Council approved on 1 July 2025 a dual-track approach for settling DLT transactions in central bank money:

- **Pontes** (short-term track): pilot launching Q3 2026, linking DLT platforms with TARGET Services. It will offer a single Eurosystem DLT-based solution, linking DLT platforms and TARGET Services to settle transactions in central bank money
- **Appia** (long-term track): integrated ecosystem for euro DLT settlement, no fixed timeline yet

The 2024 exploratory work that informed this strategy involved 64 participants over 50 trials and experiments with three Eurosystem solutions:
- **DL3S** (Banque de France): full-DLT interoperability
- **TIPS Hash-Link** (Banca d'Italia)
- **Trigger Solution** (Bundesbank)

### The L3 hypothetical: native sovereign issuance

The ultimate state would be: the French Trésor, German Finanzagentur, or US Treasury issues debt directly on a DLT-SS, with no intermediate wrapper. Token holders are direct claimants on the sovereign.

Under DR 2015/61 Art. 10(1)(a)-(d), this would immediately qualify as **Level 1 HQLA**, no haircut, no operational restrictions specific to the wrapper. The DLT just becomes the issuance and settlement technology.

### Why this is 5-7 years out

A conservative timeline reflects:
- The Pontes pilot starts Q3 2026; observation period at least 12-18 months before scaled deployment
- Sovereign issuance under DLT requires national debt management agencies to adopt new infrastructure
- Treaty-level alignment between Eurosystem and individual national treasuries
- Political dimension: sovereigns are highly conservative about debt issuance technology changes (cf. the slow adoption of even electronic Treasury auctions; AFT moved to electronic-only in 2003, 25 years after first electronic trials)
- The 3-5 years window assumes near-perfect political execution. The 5-7 years window adds margin for the typical regulatory drift observed in European financial market infrastructure projects (cf. T2S which was originally targeted for 2013, went live 2015-2017)

Realistic conservative timeline (Eurozone):
- 2026 Q3, Pontes pilot launches
- 2027-2028, first non-sovereign issuances under Pontes
- 2028-2029, first experimental sovereign issuances (small tranches alongside traditional auctions)
- 2030-2032, mainstream sovereign DLT issuance as a meaningful share of primary issuance

### US Treasury L3: DTCC Canton Network and the absence of a Pontes equivalent

The US has no public sector equivalent to Pontes/Appia. The closest functional parallel is the private-sector DTCC-Digital Asset partnership announced December 2025 to tokenize DTC-custodied US Treasury securities on the Canton Network, with a minimum viable product targeted for H1 2026.

Critical distinctions with Pontes:
- **Operator**: DTCC is a private-sector clearing house (regulated, but not central bank). Pontes is run by the Eurosystem (ECB + NCBs).
- **Settlement asset**: DTCC initiative settles in commercial bank money or tokenised deposits, not central bank money. Pontes settles in central bank money.
- **HQLA implications**: DTCC tokenisation of existing book-entry Treasuries preserves their Level 1 HQLA status (per FRB/OCC/FDIC joint FAQ of 5 March 2026, which confirmed that the capital rule is technology neutral and tokenized representations of traditional financial instruments should receive the same risk weight as their non-tokenized counterparts). This is closer to L2 in the framework, same legal substance, new technology layer, than to genuine L3 native issuance.

For genuine L3 in the US sense, the relevant question is when the Treasury itself would issue T-bills natively as tokens on a DLT-SS. As of May 2026, no public roadmap exists. The October 2024 TBAC presentation explicitly cited concerns about the incumbent advantage of legacy infrastructure and the high transition costs.

A reasonable US L3 timeline is therefore:
- 2026 H1, DTCC-Canton MVP launches (tokenised representation of existing book-entry Treasuries)
- 2027-2029, possible Federal Reserve pilot for wholesale DLT settlement (no commitment publicly)
- 2030+, earliest realistic horizon for native Treasury issuance on DLT
- 2032-2035, meaningful share of primary issuance

The US is approximately 12-24 months behind the Eurozone on the native sovereign DLT path. This is partly structural (decentralized monetary system, sovereign autonomy of the Federal Reserve) and partly political (TBAC scepticism). The Trump administration's executive orders on crypto policy (January 2025) have not specifically addressed sovereign DLT issuance, the focus has been on private-sector innovation and stablecoin regulation, not government debt infrastructure.

### Summary of L3 prospects

| Jurisdiction | Track | Operational pilot | Native sovereign target | Realistic timeline |
|---|---|---|---|---|
| Eurozone | Pontes / Appia | Q3 2026 | 2028-2029 (experimental) | 5-7 years for mainstream |
| US | DTCC Canton (private) | H1 2026 MVP | No public plan | 6-9 years |
| UK | Digital Securities Sandbox | Active since 2024 | No public plan | 6-9 years |

## Roadmap visualisation

The four-level gradient is best visualised as a staircase showing structural distance to HQLA:

```
                           L3: Native sovereign DLT
                          /  • Direct Level 1 HQLA
                         /   • Full ECB collateral
                        /    • Timeline: 5-7 years
                       /
              L2: DLT-PR via authorised CSD
             /  • ECB collateral eligibility ←── operational since 30 Mar 2026
            /   • Settlement finality opposable
           /    • Timeline: 6-24 months
          /
   L1: UCITS MMF restructuration
  /  • HQLA Level 1/2A via look-through (Art. 15)
 /   • EU passport access
/    • Timeline: 12-30 months
L0: Status quo (current state June 2026)
 • Not HQLA
 • Not ECB collateral
 • All three products (BUIDL, OUSG, bIB01)
```

The path L0 → L1+L2 (combined, 24-36 months) → L3 (5-7 years) represents the most credible institutional roadmap, with BlackRock as the natural executor for L1 given its existing UCITS infrastructure in Luxembourg and Ireland.

## Implications for the three products

| Product | Most credible target | Estimated timeline | Main obstacle |
|---|---|---|---|
| BUIDL | L1+L2 (BlackRock UCITS MMF via 21X AG DLT-TSS) | 24-36 months | Regulatory dialogue with CSSF or CBI on public blockchain as system of record |
| OUSG | L1 indirect (via underlying UCITS MMFs) | Already partially possible if Ondo flattens fund-of-funds | Loss of BlackRock partnership economics |
| bIB01 | New product launch (not a restructuring) | Effectively N/A, would require Backed Finance to become a fund manager | Business model misalignment |

## What this means for the article narrative

Section 6 (Gradient) of the article should:

1. **Lead with the regulatory update**: the L2 path became operational on 30 March 2026. This is news for many readers and frames the gradient as practically actionable, not academic
2. **Use BUIDL as primary case**: the only product with a credible institutional pathway
3. **Frame the L1+L2 combination** as the next 24-36 month target. Single-level steps L0→L1 or L0→L2 alone are sub-optimal
4. **Note the asymmetry**: bIB01's debt-instrument structure makes the gradient inapplicable. OUSG's fund-of-funds creates economic obstacles. BUIDL is unique in having both a credible structure and an institutional shareholder (BlackRock) capable of executing the restructuring

## Editorial decisions for the article (validated 2026-05-11)

The following decisions have been validated for the article integration:

1. **L1+L2 combination**: presented as 24-36 months target, ambitious but credible, anchored on Pontes Q3 2026 and three active DLT-PR authorisations
2. **L3 timeline**: 5-7 years (conservative, accounts for political margin on sovereign debt issuance technology changes)
3. **L3 sovereign coverage**: Eurozone (detailed Pontes/Appia pathway) + US Treasury (DTCC Canton Network MVP + TBAC scepticism + FRB/OCC/FDIC technology-neutral capital guidance)
4. **BlackRock mention**: explicit reference as L1 executor for credibility and concreteness, supported by BlackRock's existing UCITS infrastructure (BlackRock Asset Management Ireland Limited, BlackRock Luxembourg S.A.)

## Sources

### Primary regulatory texts
- Regulation (EU) 2017/1131 (MMFR), Money Market Funds Regulation
- Regulation (EU) 2022/858, DLT Pilot Regime
- ECB Press Release 27 January 2026: "ECB paves way for acceptance of DLT-based assets as eligible Eurosystem collateral"
- ECB Press Release 1 July 2025: "ECB commits to distributed ledger technology settlement plans with dual-track strategy" (Pontes/Appia)
- FRB/OCC/FDIC Interagency FAQ 5 March 2026 on capital treatment of tokenized securities

### Operational documents
- ESMA Report on DLT Pilot Regime functioning (ESMA75-117376770-460, 25 June 2025)
- ECB Exploratory Work Report on DLT Settlement (November 2025 publication)
- European Commission package proposed amendments to DLT-PR (December 2025)
- TBAC Charge October 2024 Q4: "Digital Assets and the Treasury Market" presentation
- DTCC-Digital Asset announcement December 2025: tokenization of DTC-custodied US Treasury securities on Canton Network

### Precedent documents
- Franklin Onchain U.S. Government Money Fund Prospectus and SEC filings (SEC EDGAR CIK 0001786958)
- 21X AG DLT-TSS authorisation announcement (December 2024)
- DTCC-Digital Asset UST Collateral Network Pilot results (September 2024)
