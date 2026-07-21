# Dune Dashboard: Step-by-Step Setup Guide

This guide walks through running the six SQL queries from `dune_queries.sql` on Dune Analytics and assembling them into a public dashboard.

**Estimated time**: ~30 minutes.
**Cost**: free tier sufficient.

---

## Step 1: Sign in to Dune

1. Go to https://dune.com
2. Click "Sign in" (top-right). GitHub or email both work.
3. Choose a username (this appears in your dashboard URL: `dune.com/<username>/...`).
4. Confirm email if asked.

You are now in the free tier. Limits: 30 seconds per query, 250 query executions per month. Sufficient for this setup.

---

## Step 2: Run query M1 (AUM time-series)

1. Click "+ New" → "New query" in the top-right.
2. Make sure the engine is **DuneSQL** (top-left dropdown above the editor). Not Spark, not Postgres.
3. Copy-paste the M1 block from `02_empirical/dune_queries.sql` (lines marked between the `M1` headers).
4. Click "Run" (or Ctrl+Enter).
5. **Expected result**: a table with one row per day from 2024-03-15 to today, showing `day`, `aum_tokens`, `aum_usd`. Should be ~785 rows by May 2026.

**If it fails**:
- Error "table not found": Click "Data" tab in the left sidebar, search for `tokens.transfers`. If absent, replace with `erc20_ethereum.evt_Transfer` and adjust the query per the troubleshooting cheatsheet at the bottom of `dune_queries.sql`.
- Error about hex literal: ensure you have no extra spaces in `0x7712c34205737192402172409a8F7ccef8aA2AEc`.

6. Click "Save" (top-right). Name: `RWA_M1_AUM_timeseries_BUIDL`. Make it public.
7. Note the query URL (it'll be `dune.com/queries/<id>`). You'll need it for the dashboard.

8. **Duplicate for OUSG and bIB01**:
   - Click "Fork" on the query
   - Change `contract_address` to OUSG (`0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92`) and `block_date >= DATE '2023-01-01'`
   - Save as `RWA_M1_AUM_timeseries_OUSG`
   - Repeat for bIB01 (`0xCA30c93B02514f86d5C86a6e375E3A330B435Fb5`, `block_date >= DATE '2023-04-01'`)

---

## Step 3: Run query M2 (Holders concentration)

1. New query, DuneSQL engine.
2. Copy-paste the M2 block.
3. Run. **Expected result**: a single row with `holder_count`, `top3_share`, `top10_share`, `top25_share`, `total_supply_tokens`.

For BUIDL in May 2026, expected approximate values:
- `holder_count`: 50-60
- `top3_share`: ~0.60-0.70
- `top10_share`: ~0.80-0.90
- `top25_share`: ~0.95+
- `total_supply_tokens`: ~$147M

If your numbers differ materially from the article, that's expected, the snapshot was 2026-05-06 and the on-chain state evolves. Note your run date in the dashboard description.

4. Save as `RWA_M2_holders_concentration_BUIDL`. Fork for OUSG and bIB01.

5. **Optional: Lorenz curve data**. Create a second query using the commented-out block in `dune_queries.sql` (the "Companion query" section). Save as `RWA_M2_lorenz_data_BUIDL`. Export the holder-level result or record the Top-3/Top-10/Top-25 constraints and smallest balances. `lorenz_real_data.py` uses those inputs to recompute the constrained reconstruction, exact LP bounds, and Figure 2.

---

## Step 4: Run queries M3, M4, M5

Same pattern: new query → paste → run → save → fork per product.

- **M3** (transfer activity): expect very low daily counts. For BUIDL, ~1-3 transfers/day on average.
- **M4** (primary vs secondary): expect primary to dominate. Secondary share should be near zero for BUIDL.
- **M5** (burn pattern): expect a small number of large burns from issuer/redeemer addresses.

---

## Step 5: Run query M6 (cross-product comparison)

This is the single most useful query for the dashboard headline.

1. New query, paste M6, run.
2. **Expected result**: a table with 3 rows (one per product), columns `product_name`, `holder_count`, `total_supply`, `total_transfers`, `secondary_transfers`, `secondary_share`.
3. Save as `RWA_M6_cross_product_summary`.

This will be the headline table of your dashboard.

---

## Step 6: Build the dashboard

1. Click "+ New" → "New dashboard" in the top-right.
2. Name it: `RWA HQLA Framework, Live Metrics`. Make it public.
3. Layout suggestion:

```
Row 1 (full width): M6 cross-product summary table
Row 2 (split 1/2 + 1/2): M1 AUM time-series for BUIDL + M1 for OUSG
Row 3 (full width): M1 for bIB01 (or combined chart)
Row 4 (1/3 + 1/3 + 1/3): M2 holders (BUIDL, OUSG, bIB01): show as Counter visualisations
Row 5 (full width): M3 transfer activity (BUIDL primary chart)
Row 6 (split 1/2 + 1/2): M4 primary vs secondary (BUIDL) + M5 burn pattern (BUIDL)
```

To add a query to the dashboard:
- Click "Add visualization"
- Select your saved query
- Choose chart type (line for time-series, counter for single number, table for M6)
- Configure axes / colors
- Save the visualization

Markdown text widgets are useful for explaining each metric. Recommend adding a short header for each row referencing the article section.

---

## Step 7: Polish

1. Add a description to the dashboard: link back to the GitHub repo, brief explanation of the framework, snapshot date.
2. Set up email alerts (optional) on the M1 queries, Dune can email you when AUM crosses a threshold.
3. Copy the dashboard URL.

---

## Step 8: Wire it back to the article

Replace the placeholder in `article/article.md`:

```
*Live dashboard: https://dune.com/bandulf/rwa-hqla-framework-live-metrics*
```

with:

```
*Live dashboard: https://dune.com/bandulf/rwa-hqla-framework-live-metrics*
```

Same in `README.md`:

```
A live dashboard tracking the metrics in this framework is available at: https://dune.com/bandulf/rwa-hqla-framework-live-metrics.
```

Replace with the actual URL.

---

## Troubleshooting common issues

| Symptom | Cause | Fix |
|---|---|---|
| "Table not found" | DuneSQL engine has different schema | Use `erc20_ethereum.evt_Transfer` instead of `tokens.transfers`; see cheatsheet in SQL file |
| "Operator does not exist" on hex compare | Engine type mismatch | Verify DuneSQL engine selected, not legacy |
| Query timeout (30s+) | Too much data scanned | Tighten date range, add `LIMIT 1000` for testing |
| Zero rows returned | Wrong contract address or date | Verify address case-sensitive; check block_date filter |
| `amount` looks huge | Used raw event table instead of `tokens.transfers` | Either switch to `tokens.transfers`, or divide by `10^decimals` (6 for BUIDL, 18 for OUSG/bIB01) |
| Holders count seems off | `balances.erc20_latest` may have different freshness | Cross-check with Etherscan token holders page |

---

## What to do next

Once the dashboard is live and the article references point to it:

1. Tweet a screenshot of the cross-product summary with the dashboard link
2. Add a "fork this query" call-to-action, anyone applying the framework to a new product (Superstate, Hashnote, OpenEden) can fork your queries and just change the contract address

The dashboard is the operational complement to the article. The article makes the analytical case; the dashboard lets readers verify the empirical claims in real time.
