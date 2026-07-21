-- ============================================================================
-- RWA HQLA Framework — Dune SQL Queries v1.2
-- Updated 2026-05-27
-- ============================================================================
--
-- DESIGN PRINCIPLE FOR v1.2:
-- All queries below depend on a SINGLE confirmed table: tokens.transfers
-- Schema confirmed at https://docs.dune.com/data-catalog/curated/token-transfers/overview
-- Columns used : block_date, block_time, blockchain, contract_address, "from", "to", amount, amount_usd, symbol
-- Partition keys : blockchain, block_date (always filter on these)
--
-- Why no balances.erc20_latest in v1.2? Because the exact column names of
-- that table are not in the public docs and I refuse to guess again.
-- Computing balances by aggregating tokens.transfers is slower but
-- guaranteed to work.
--
-- Contract addresses (lowercase for Trino safety):
--   BUIDL Ethereum  : 0x7712c34205737192402172409a8f7ccef8aa2aec
--   OUSG  Ethereum  : 0x1b19c19393e2d034d8ff31ff34c81252fcbbee92
--   bIB01 Ethereum  : 0xca30c93b02514f86d5c86a6e375e3a330b435fb5
--
-- ZERO ADDRESS (mint/burn marker):
--   0x0000000000000000000000000000000000000000
-- ============================================================================


-- ============================================================================
-- STEP 0 — Sanity check before running any other query
-- ============================================================================
-- Run this FIRST on Dune (DuneSQL engine).
-- If it returns rows : table and contract address are correct, proceed.
-- If "table not found" : switch to DuneSQL engine (top-left dropdown).
-- If 0 rows : contract_address or date filter is wrong.
-- Expected : ~5 rows from the first weeks after BUIDL launch (March 2024).
-- ============================================================================

SELECT
    block_time,
    "from",
    "to",
    amount,
    amount_usd
FROM tokens.transfers
WHERE blockchain = 'ethereum'
  AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
  AND block_date >= DATE '2024-03-01'
  AND block_date <= DATE '2024-03-31'
ORDER BY block_time
LIMIT 10;


-- ============================================================================
-- M1 — AUM time-series (daily)
-- ============================================================================

WITH supply_changes AS (
    SELECT
        block_date AS day,
        SUM(
            CASE
                WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount
                WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN -amount
                ELSE 0
            END
        ) AS net_supply_change
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'
      AND (
          "from" = 0x0000000000000000000000000000000000000000
          OR "to" = 0x0000000000000000000000000000000000000000
      )
    GROUP BY 1
)
SELECT
    day,
    SUM(net_supply_change) OVER (ORDER BY day) AS aum_tokens
FROM supply_changes
ORDER BY day;


-- ============================================================================
-- M2 — Holders count + Top concentration shares
-- ============================================================================

WITH movements AS (
    SELECT
        "to" AS address,
        amount AS amt
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'

    UNION ALL

    SELECT
        "from" AS address,
        -amount AS amt
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'
),
balances AS (
    SELECT
        address,
        SUM(amt) AS balance
    FROM movements
    WHERE address != 0x0000000000000000000000000000000000000000
    GROUP BY address
    HAVING SUM(amt) > 0
),
ranked AS (
    SELECT
        address,
        balance,
        ROW_NUMBER() OVER (ORDER BY balance DESC) AS rank_desc,
        SUM(balance) OVER () AS total_supply,
        COUNT(*) OVER () AS n_holders
    FROM balances
)
SELECT
    MAX(n_holders) AS holder_count,
    SUM(CASE WHEN rank_desc <=  3 THEN balance ELSE 0 END) / MAX(total_supply) AS top3_share,
    SUM(CASE WHEN rank_desc <= 10 THEN balance ELSE 0 END) / MAX(total_supply) AS top10_share,
    SUM(CASE WHEN rank_desc <= 25 THEN balance ELSE 0 END) / MAX(total_supply) AS top25_share,
    MAX(total_supply) AS total_supply_tokens
FROM ranked;


-- ============================================================================
-- M2-bis — Per-holder balance export (CSV for Python Lorenz plot)
-- ============================================================================

WITH movements AS (
    SELECT "to" AS address, amount AS amt
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'
    UNION ALL
    SELECT "from" AS address, -amount AS amt
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'
)
SELECT
    address,
    SUM(amt) AS balance
FROM movements
WHERE address != 0x0000000000000000000000000000000000000000
GROUP BY address
HAVING SUM(amt) > 0
ORDER BY balance ASC;


-- ============================================================================
-- M3 — Transfer activity (daily, excluding mint/burn)
-- ============================================================================

SELECT
    block_date AS day,
    COUNT(*) AS n_transfers,
    SUM(amount) AS volume_tokens,
    COUNT(DISTINCT "from") AS unique_senders,
    COUNT(DISTINCT "to")   AS unique_recipients
FROM tokens.transfers
WHERE blockchain = 'ethereum'
  AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
  AND "from" != 0x0000000000000000000000000000000000000000
  AND "to"   != 0x0000000000000000000000000000000000000000
  AND block_date >= DATE '2024-03-01'
GROUP BY 1
ORDER BY 1;


-- ============================================================================
-- M4 — Primary (mint/burn) vs Secondary classification
-- ============================================================================

WITH classified AS (
    SELECT
        block_date AS day,
        CASE
            WHEN "from" = 0x0000000000000000000000000000000000000000
              OR "to"   = 0x0000000000000000000000000000000000000000
                THEN 'primary'
                ELSE 'secondary'
        END AS flow_type,
        amount
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'
)
SELECT
    day,
    flow_type,
    COUNT(*)    AS n_transfers,
    SUM(amount) AS volume_tokens
FROM classified
GROUP BY 1, 2
ORDER BY 1, 2;


-- ============================================================================
-- M5 — Burn pattern analysis
-- ============================================================================

SELECT
    "from" AS burner_address,
    COUNT(*) AS n_burns,
    SUM(amount) AS total_burned,
    AVG(amount) AS avg_burn,
    MAX(amount) AS max_burn,
    MIN(block_date) AS first_burn,
    MAX(block_date) AS last_burn
FROM tokens.transfers
WHERE blockchain = 'ethereum'
  AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
  AND "to" = 0x0000000000000000000000000000000000000000
  AND block_date >= DATE '2024-03-01'
GROUP BY "from"
ORDER BY total_burned DESC
LIMIT 50;


-- ============================================================================
-- M6 — Cross-product comparison (BUIDL / OUSG / bIB01 in one query)
-- ============================================================================

WITH all_transfers AS (
    SELECT 'BUIDL' AS product, "from", "to", amount
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'

    UNION ALL

    SELECT 'OUSG' AS product, "from", "to", amount
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x1b19c19393e2d034d8ff31ff34c81252fcbbee92
      AND block_date >= DATE '2023-01-01'

    UNION ALL

    SELECT 'bIB01' AS product, "from", "to", amount
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0xca30c93b02514f86d5c86a6e375e3a330b435fb5
      AND block_date >= DATE '2023-04-01'
)
SELECT
    product,
    COUNT(*) AS total_transfers,
    COUNT(*) FILTER (
        WHERE "from" != 0x0000000000000000000000000000000000000000
          AND "to"   != 0x0000000000000000000000000000000000000000
    ) AS secondary_transfers,
    SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount ELSE 0 END) AS total_minted,
    SUM(CASE WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN amount ELSE 0 END) AS total_burned,
    SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount ELSE 0 END)
        - SUM(CASE WHEN "to" = 0x0000000000000000000000000000000000000000 THEN amount ELSE 0 END) AS current_supply,
    COUNT(DISTINCT "from") AS unique_senders,
    COUNT(DISTINCT "to") AS unique_recipients
FROM all_transfers
GROUP BY product
ORDER BY current_supply DESC;


-- ============================================================================
-- DEBUGGING — if Step 0 fails
-- ============================================================================
--
-- 1. "Table 'tokens.transfers' not found":
--    -> Engine is not DuneSQL. Change engine in the top-left dropdown.
--    -> If still failing, run this discovery query in DuneSQL:
--         SELECT table_schema, table_name
--         FROM information_schema.tables
--         WHERE table_name LIKE '%transfer%'
--         LIMIT 50;
--
-- 2. "Column 'amount' not found":
--    -> Schema may differ. Run :
--         SELECT * FROM tokens.transfers
--         WHERE blockchain = 'ethereum'
--           AND block_date = CURRENT_DATE - INTERVAL '1' DAY
--         LIMIT 1;
--       Inspect actual column names returned.
--
-- 3. "Cannot resolve operator for varbinary = varchar":
--    -> Engine mismatch. Confirm DuneSQL is selected.
--    -> If still failing, cast explicitly:
--         contract_address = CAST(0x7712... AS varbinary)
--
-- 4. Returns 0 rows on Step 0:
--    -> Try without contract_address filter:
--         SELECT contract_address, symbol, COUNT(*)
--         FROM tokens.transfers
--         WHERE blockchain = 'ethereum'
--           AND block_date BETWEEN DATE '2024-03-15' AND DATE '2024-03-22'
--           AND symbol = 'BUIDL'
--         GROUP BY 1, 2
--         LIMIT 10;
--       The contract_address returned tells you the canonical form to use.
--
-- 5. Query times out (30s free tier):
--    -> M2 with full history scan can hit the limit on BUIDL (~1500 transfers
--       total is small, but the UNION ALL doubles the scan).
--    -> Tighten date range: block_date BETWEEN DATE '2025-01-01' AND CURRENT_DATE
--    -> Or use materialized view : Dune can save expensive CTEs as materialized
--       views, refreshed periodically. See dune.com/docs.
--
-- IF YOU HAVE A SPECIFIC ERROR :
-- send me the exact error string and the SQL that triggered it.
-- I will stop guessing and target the actual issue.
-- ============================================================================


-- ============================================================================
-- M7 — Unified AUM time-series (3 products in one chart)
-- ============================================================================
-- Added in v1.1 (2026-06-17). Produces a single result set with three series
-- (one per product) for plotting BUIDL, OUSG, bIB01 on a single chart in
-- Dune. Use a log-scale Y-axis given the three orders of magnitude difference
-- (BUIDL ~$181M vs OUSG ~$1.9M vs bIB01 ~$40K on Ethereum mainnet).
-- Save on Dune as: RWA_HQLA_M7_AUM_unified_3products
-- ============================================================================

WITH all_supply_changes AS (
    SELECT
        block_date AS day,
        'BUIDL' AS product,
        SUM(CASE
            WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount
            WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN -amount
            ELSE 0
        END) AS net_change
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x7712c34205737192402172409a8f7ccef8aa2aec
      AND block_date >= DATE '2024-03-01'
      AND ("from" = 0x0000000000000000000000000000000000000000
           OR "to" = 0x0000000000000000000000000000000000000000)
    GROUP BY 1

    UNION ALL

    SELECT
        block_date AS day,
        'OUSG' AS product,
        SUM(CASE
            WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount
            WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN -amount
            ELSE 0
        END) AS net_change
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0x1b19c19393e2d034d8ff31ff34c81252fcbbee92
      AND block_date >= DATE '2023-01-01'
      AND ("from" = 0x0000000000000000000000000000000000000000
           OR "to" = 0x0000000000000000000000000000000000000000)
    GROUP BY 1

    UNION ALL

    SELECT
        block_date AS day,
        'bIB01' AS product,
        SUM(CASE
            WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount
            WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN -amount
            ELSE 0
        END) AS net_change
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND contract_address = 0xca30c93b02514f86d5c86a6e375e3a330b435fb5
      AND block_date >= DATE '2023-04-01'
      AND ("from" = 0x0000000000000000000000000000000000000000
           OR "to" = 0x0000000000000000000000000000000000000000)
    GROUP BY 1
)
SELECT
    day,
    product,
    SUM(net_change) OVER (PARTITION BY product ORDER BY day) AS aum_tokens
FROM all_supply_changes
ORDER BY product, day;

-- Visualization tip on Dune:
--   Chart type : Line chart
--   X-axis     : day
--   Y-axis     : aum_tokens (LOG SCALE — critical, otherwise BUIDL drowns OUSG and bIB01)
--   Group by   : product
