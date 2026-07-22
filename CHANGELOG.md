# Changelog

## v0.2.2 (2026-07-22)

- Distinguished explicit empty-route responses from technical API failures.
- Abort measurements on rate limits, HTTP errors, timeouts and schema errors
  rather than interpreting them as liquidity-depth observations.
- Sort successful quotes by PT size before selecting the marginal reference.
- Raised the default Hosted SDK timeout to 120 seconds.
- Expanded CI to Python 3.10-3.13 and the complete pytest suite.

## v0.2.1 (2026-07-22)

- Migrated fresh quote retrieval to Pendle's recommended v3 Convert POST endpoint.
- Corrected the slippage parameter to `0.01` for a one-percent tolerance and added an explicit `--use-limit-order` opt-in.
- Preserved the two governance-anchor CSVs as dated historical snapshots rather than rewriting them after an API migration.
- Added tests for the v3 request payload, response normalisation, complete quote failure, output-token USD conversion and published CSV presence.
- Expanded continuous integration to Python 3.10-3.13 and the full pytest suite.
- Removed the stale README note that the reUSD CSV still needed to be added.

## v0.2 (2026-07-19/20)

- Measured-provenance CSVs: timestamp, chain, market, addresses, API
  base and routing mode written with every pull.
- Spot sanity check on the smallest execution (3% tolerance, explicit
  override flag).
- Aggregator routing off by default (`--enable-aggregator` to opt in);
  `--receiver` required (third-party default address removed).
- Signature fix on the retrieval path (`fetch_swap_quote` declares
  `enable_aggregator`; keyword-only internal call).
- Governance post published under `governance/` with two Pendle-only
  anchor curves (near-maturity PT-sUSDe, far-maturity PT-reUSD);
  README quickstart reproduces both calibrations.
- Test suite (11 tests) and continuous integration.

## v0.1 (2026-06-08)

- Initial toolkit: `pendle_depth.py` grid quoting, `discover_market.py`,
  `coverage_model.py` closed-form ceiling, `run_analysis.py`,
  Dune queries; June PT-sUSDe pull (aggregator-routed, pre-provenance,
  retained as `pt_depth_curve.csv`).
