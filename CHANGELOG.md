# Changelog

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
