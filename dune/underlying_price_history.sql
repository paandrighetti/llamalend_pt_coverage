-- underlying_price_history.sql
-- PURPOSE: historical price of the PT's UNDERLYING asset (e.g. USDe), used to
--   (1) calibrate the stress depeg magnitude `d` (worst observed deviation), and
--   (2) calibrate the wrong-way factor `rho` (co-movement of depeg vs PT depth).
--
-- DuneSQL / Trino. This is a TEMPLATE: confirm the price source for your asset.
-- `prices.usd` covers many assets by contract; if your underlying is missing,
-- fall back to a DEX VWAP (second query below).
--
-- Replace <UNDERLYING_CONTRACT> and <CHAIN> ('ethereum', etc.).

-- Option A: catalog price feed (preferred when available)
SELECT
    date_trunc('hour', minute) AS hour,
    approx_percentile(price, 0.5) AS price_median,
    min(price)                  AS price_min,        -- captures intra-hour depeg
    max(price)                  AS price_max
FROM prices.usd
WHERE blockchain = '<CHAIN>'
  AND contract_address = <UNDERLYING_CONTRACT>
  AND minute > now() - interval '365' day
GROUP BY 1
ORDER BY 1;

-- Option B (fallback): DEX VWAP if the asset is not in prices.usd
-- SELECT
--     date_trunc('hour', block_time) AS hour,
--     sum(amount_usd) / sum(token_bought_amount) AS vwap_usd,
--     count(*) AS n_trades
-- FROM dex.trades
-- WHERE blockchain = '<CHAIN>'
--   AND token_bought_address = <UNDERLYING_CONTRACT>
--   AND block_time > now() - interval '365' day
--   AND amount_usd > 0
-- GROUP BY 1
-- ORDER BY 1;
