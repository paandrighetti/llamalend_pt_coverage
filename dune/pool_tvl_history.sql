-- pool_tvl_history.sql
-- PURPOSE: daily USD TVL of a liquidity pool used as the capacity proxy for rho
--   estimation (its contraction through a past USDe depeg = wrong-way factor).
--   Pair this with usde price history; merge on day into rho_inputs.csv with
--   columns [date, usde_price, capacity_usd] for estimate_rho.py.
--
-- DuneSQL / Trino. TEMPLATE: replace <POOL>, the two pool tokens <TOKEN_A>/<TOKEN_B>
-- (and their decimals), and <CHAIN>. For a Pendle sUSDe pool the tokens are PT and
-- SY; for a Curve USDe pool they are USDe and the paired stable.
--
-- DefiLlama (fetch_rho_inputs.py) is the easier route for a clean TVL series;
-- use this when you want a fully on-chain, auditable capacity series.

WITH flows AS (
    SELECT date_trunc('day', evt_block_time) AS day,
           contract_address                  AS token,
           CASE WHEN "to"   = <POOL> THEN  CAST(value AS double)
                WHEN "from" = <POOL> THEN -CAST(value AS double)
                ELSE 0 END                    AS signed
    FROM erc20_<CHAIN>.evt_Transfer
    WHERE contract_address IN (<TOKEN_A>, <TOKEN_B>)
      AND (<POOL> IN ("to", "from"))
      AND evt_block_time > now() - interval '450' day
),
bal AS (  -- running on-chain balance of each pool token
    SELECT day, token,
           sum(sum(signed)) OVER (PARTITION BY token ORDER BY day) AS bal_raw
    FROM flows GROUP BY 1, 2
),
px AS (   -- daily USD price per token from the catalog
    SELECT date_trunc('day', minute) AS day, contract_address AS token,
           approx_percentile(price, 0.5) AS price
    FROM prices.usd
    WHERE blockchain = '<CHAIN>'
      AND contract_address IN (<TOKEN_A>, <TOKEN_B>)
      AND minute > now() - interval '450' day
    GROUP BY 1, 2
)
SELECT b.day AS date,
       sum( (b.bal_raw / 1e18) * p.price ) AS capacity_usd   -- adjust 1e18 per token decimals
FROM bal b
JOIN px p ON p.day = b.day AND p.token = b.token
GROUP BY 1
ORDER BY 1;
