-- pendle_pt_liquidity_context.sql
-- PURPOSE: time series of the Pendle market's secondary-liquidity context
--   (token balances held by the market AMM, as a TVL/depth proxy). Used to (a)
--   provide the `pool_tvl_usd` context input and (b) measure how depth contracts
--   during underlying-depeg episodes -> calibrates the wrong-way factor `rho`.
--
-- NOTE ON DEPTH: the *exact* slippage curve (L_raw) is best taken from the Pendle
-- API (see pendle_depth.py) because it reflects the live AMM math. This query
-- gives the slower-moving LIQUIDITY CONTEXT, not the precise price-impact curve.
--
-- DuneSQL / Trino. TEMPLATE: Pendle's decoded tables vary; the robust, source-
-- agnostic approach below reconstructs the market's PT and SY balances from ERC-20
-- transfers in/out of the market contract. Replace <MARKET>, <PT>, <SY>, <CHAIN>.

WITH flows AS (
    SELECT date_trunc('day', evt_block_time) AS day,
           contract_address                  AS token,
           CASE WHEN "to"   = <MARKET> THEN  CAST(value AS double)
                WHEN "from" = <MARKET> THEN -CAST(value AS double)
                ELSE 0 END                    AS signed_amount
    FROM erc20_<CHAIN>.evt_Transfer
    WHERE contract_address IN (<PT>, <SY>)
      AND (<MARKET> IN ("to", "from"))
      AND evt_block_time > now() - interval '365' day
),
balances AS (
    SELECT day, token,
           sum(sum(signed_amount)) OVER (PARTITION BY token ORDER BY day) AS bal_raw
    FROM flows
    GROUP BY 1, 2
)
SELECT day,
       max(CASE WHEN token = <PT> THEN bal_raw END) / 1e18 AS pt_balance,
       max(CASE WHEN token = <SY> THEN bal_raw END) / 1e18 AS sy_balance
FROM balances
GROUP BY 1
ORDER BY 1;
