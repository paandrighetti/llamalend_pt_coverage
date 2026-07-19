"""
fetch_rho_inputs.py
===================
Convenience fetcher (DefiLlama) that builds rho_inputs.csv for estimate_rho.py:
USDe price history + a chosen liquidity pool's historical TVL, merged by date.

Run in your environment (needs internet to DefiLlama):
    python fetch_rho_inputs.py --pool <DEFILLAMA_POOL_UUID> --days 400

Finding the pool UUID: on DefiLlama, open the pool's page (URL ends with the
UUID), or query https://yields.llama.fi/pools and grep for the symbol. Prefer a
PAST Pendle sUSDe / eUSDe PT pool that existed through a USDe stress episode
(most apples-to-apples); a large Curve USDe pool is a good robustness cross-check.

DefiLlama routes can change -- the script fails loudly on a schema mismatch.
Use --raw to inspect responses.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

import pandas as pd
import requests

USDE = "0x9d39a5de30e57443bff2a8307a4256c8797a3497"  # Ethena USDe (Ethereum)
COINS_BASE = "https://coins.llama.fi"
YIELDS_BASE = "https://yields.llama.fi"


def get_json(url: str, params: dict | None = None, timeout: float = 40.0):
    try:
        r = requests.get(url, params=params or {}, timeout=timeout)
    except requests.RequestException as e:
        sys.exit(f"[fetch_rho] request failed for {url}: {e}")
    if r.status_code != 200:
        sys.exit(f"[fetch_rho] HTTP {r.status_code} for {r.url}\n{r.text[:800]}")
    try:
        return r.json()
    except ValueError:
        sys.exit(f"[fetch_rho] non-JSON for {r.url}\n{r.text[:800]}")


def fetch_price(token: str, days: int, raw: bool) -> pd.DataFrame:
    """USDe daily price history. DefiLlama caps /chart at 500 points per call, so
    we page backwards in <=500-day windows and dedupe by date."""
    coins = f"ethereum:{token}"
    max_span = 500
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    remaining = max(1, days)
    chunk_end = now
    by_date: dict = {}
    first = True
    while remaining > 0:
        span = min(max_span, remaining)
        start = chunk_end - span * 86400
        data = get_json(f"{COINS_BASE}/chart/{coins}",
                        {"start": start, "span": span, "period": "1d", "searchWidth": "6h"})
        if raw and first:
            print(str(data)[:2000]); sys.exit(0)
        try:
            prices = data["coins"][coins]["prices"]
        except (KeyError, TypeError):
            sys.exit(f"[fetch_rho] unexpected price schema; "
                     f"keys={list(data) if isinstance(data, dict) else type(data)}. "
                     f"Use --raw to inspect.")
        for p in prices:
            d = dt.datetime.fromtimestamp(p["timestamp"], dt.timezone.utc).date()
            by_date[d] = p["price"]
        remaining -= span
        chunk_end = start
        first = False
    return pd.DataFrame(sorted(by_date.items()), columns=["date", "usde_price"])


def fetch_pool_tvl(pool: str, raw: bool) -> pd.DataFrame:
    data = get_json(f"{YIELDS_BASE}/chart/{pool}")
    if raw:
        print(str(data)[:2000]); sys.exit(0)
    series = data.get("data") if isinstance(data, dict) else None
    if not isinstance(series, list) or not series:
        sys.exit(f"[fetch_rho] unexpected pool schema; got {type(data)}. Use --raw to inspect.")
    rows = []
    for d in series:
        ts = d.get("timestamp")
        tvl = d.get("tvlUsd", d.get("tvl"))
        if ts is None or tvl is None:
            continue
        try:
            day = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).date()
        except ValueError:
            day = dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).date()
        rows.append((day, float(tvl)))
    return pd.DataFrame(rows, columns=["date", "capacity_usd"])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool", required=True, help="DefiLlama pool UUID for the capacity proxy")
    p.add_argument("--token", default=USDE, help="USDe contract (Ethereum) for the price series")
    p.add_argument("--days", type=int, default=400)
    p.add_argument("--out-csv", default="rho_inputs.csv")
    p.add_argument("--raw", action="store_true", help="print first raw response and exit")
    args = p.parse_args()

    price = fetch_price(args.token, args.days, args.raw)
    tvl = fetch_pool_tvl(args.pool, args.raw)
    merged = pd.merge(price, tvl, on="date", how="inner").sort_values("date")
    merged = merged[merged["capacity_usd"] > 0].dropna()
    if len(merged) < 20:
        sys.exit(f"[fetch_rho] only {len(merged)} overlapping days -- check the pool UUID "
                 f"covers the price window, or increase --days.")
    merged.to_csv(args.out_csv, index=False)
    print(f"[fetch_rho] wrote {len(merged)} rows to {args.out_csv} "
          f"({merged['date'].min()} -> {merged['date'].max()})")
    print(f"[fetch_rho] next: python estimate_rho.py --inputs-csv {args.out_csv}")


if __name__ == "__main__":
    main()
