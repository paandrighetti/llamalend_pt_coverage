"""
discover_market.py
===================
List ACTIVE Pendle markets matching a name (e.g. "sUSDe") and, for each match,
print a ready-to-paste `pendle_depth.py` command plus the `run_analysis.py`
parameters (maturity-years, pool-tvl). This removes the need to read addresses
off the Pendle UI by hand.

Run (needs internet to the Pendle API):
    python discover_market.py --query sUSDe
    python discover_market.py --query sUSDe --raw   # dump raw JSON of first match

NOTES
-----
* The Pendle API field names can drift. This script extracts defensively and
  prints `None` where a field is missing -- use --raw to inspect the schema if
  so, or read the value from app.pendle.finance.
* For PT-sUSDe the accounting asset is USDe (1 PT = 1 USDe at maturity), so the
  emitted command uses the underlying (USDe) as the swap out-token.
* Verify routes against https://api-v2.pendle.finance/core/docs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from typing import Any

import requests

BASE = "https://api-v2.pendle.finance/core"


def get_json(url: str, params: dict[str, Any] | None = None, timeout: float = 30.0,
             soft: bool = False) -> Any:
    try:
        r = requests.get(url, params=params or {}, timeout=timeout)
    except requests.RequestException as e:
        if soft:
            return None
        sys.exit(f"[discover] request failed for {url}: {e}")
    if r.status_code != 200:
        if soft:
            return None
        sys.exit(f"[discover] HTTP {r.status_code} for {r.url}\n{r.text[:800]}")
    try:
        return r.json()
    except ValueError:
        if soft:
            return None
        sys.exit(f"[discover] non-JSON response for {r.url}:\n{r.text[:800]}")


def first(d: dict, *keys: str, default: Any = None) -> Any:
    """Return the first present key from a dict (schema-drift tolerant)."""
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default


def strip_chain(token_id: Any) -> Any:
    """Pendle token ids look like '1-0xabc...'; return the address part."""
    if isinstance(token_id, str) and "-" in token_id:
        return token_id.split("-", 1)[1]
    if isinstance(token_id, dict):
        return strip_chain(first(token_id, "address", "id"))
    return token_id


def years_until(expiry: Any) -> tuple[float | None, str]:
    if not isinstance(expiry, str):
        return None, str(expiry)
    try:
        exp = dt.datetime.fromisoformat(expiry.replace("Z", "+00:00"))
        days = (exp - dt.datetime.now(dt.timezone.utc)).days
        return max(0.0, round(days / 365.0, 4)), exp.date().isoformat()
    except ValueError:
        return None, expiry


def fetch_active(chain: int) -> list[dict]:
    data = get_json(f"{BASE}/v1/{chain}/markets/active")
    if isinstance(data, dict):
        markets = first(data, "markets", "results", default=None)
        if markets is None:
            # some responses nest under 'data'
            markets = first(data.get("data", {}), "markets", default=data)
    else:
        markets = data
    if not isinstance(markets, list):
        sys.exit("[discover] unexpected active-markets shape; rerun with --raw "
                 "and inspect, or read the market from app.pendle.finance.")
    return markets


def enrich(chain: int, addr: str) -> dict:
    """Per-market data (price / liquidity / implied APY). Tries v3 then v2."""
    for ver in ("v3", "v2"):
        data = get_json(f"{BASE}/{ver}/{chain}/markets/{addr}/data", soft=True)
        if isinstance(data, dict):
            return data
    return {}


def market_name(m: dict) -> str:
    return str(first(m, "name", "symbol", "proSymbol", default="")) or ""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--chain-id", type=int, default=1)
    p.add_argument("--query", default="sUSDe", help="substring to match in market name")
    p.add_argument("--receiver", required=True,
                   help="any valid EOA you control; only used to simulate quotes, never to execute"
                        "address; pass your own wallet ideally). NOT zero/precompile.")
    p.add_argument("--max-depth-fraction", type=float, default=0.25,
                   # note: the published sUSDe analysis probed beyond this default,
                   # up to the AMM proportion cap (~1.3x TVL); raise it to locate the cap
                   help="largest sell size to quote as a fraction of pool TVL")
    p.add_argument("--raw", action="store_true",
                   help="print raw JSON of the first match and exit")
    args = p.parse_args()

    markets = fetch_active(args.chain_id)
    q = args.query.lower()
    matches = [m for m in markets if q in market_name(m).lower()]

    if not matches:
        sys.exit(f"[discover] no active market name contains '{args.query}'. "
                 f"Try a broader --query, or --raw to inspect.")

    if args.raw:
        print(json.dumps(matches[0], indent=2)[:4000])
        return

    print(f"\nActive markets matching '{args.query}' on chain {args.chain_id}: "
          f"{len(matches)} found\n" + "=" * 78)

    for m in matches:
        addr = first(m, "address", "id")
        addr = strip_chain(addr)
        pt = strip_chain(first(m, "pt", "ptAddress"))
        sy = strip_chain(first(m, "sy", "syAddress"))
        underlying = strip_chain(first(m, "underlyingAsset", "asset", "accountingAsset"))
        yrs, exp_date = years_until(first(m, "expiry", "maturity"))

        md = enrich(args.chain_id, addr) if addr else {}
        liq = first(md, "liquidity", default={})
        tvl = first(liq, "usd", default=liq) if isinstance(liq, dict) else liq
        implied = first(md, "impliedApy")
        pt_obj = first(md, "pt", default={})
        # PT price in USD if exposed; otherwise None (read spot from UI)
        pt_price_usd = first(pt_obj, "price", default=None) if isinstance(pt_obj, dict) else None

        print(f"\n{market_name(m)}   (matures {exp_date}, ~{yrs} yr)")
        print(f"  market   : {addr}")
        print(f"  PT       : {pt}")
        print(f"  SY       : {sy}")
        print(f"  asset    : {underlying}   <- use as --out-token (USDe for sUSDe)")
        print(f"  TVL(usd) : {tvl}")
        print(f"  impliedAPY: {implied}")
        print(f"  PT price : {pt_price_usd}  (if None, read spot from the Pendle UI)")

        und_sym = None
        for key in ("underlyingAsset", "accountingAsset", "sy"):
            node = m.get(key) if isinstance(m, dict) else None
            if isinstance(node, dict) and node.get("symbol"):
                und_sym = node["symbol"]; break
        und_sym = und_sym or "<UNDERLYING_SYMBOL>"
        # emit the ready pendle_depth.py command
        max_size = None
        if isinstance(tvl, (int, float)) and pt_price_usd:
            max_size = round(args.max_depth_fraction * tvl / pt_price_usd)
        spot = pt_price_usd if pt_price_usd else "<SPOT_PT_PRICE>"
        out_tok = underlying if underlying else "<USDe_ADDRESS>"
        print("  --- pendle_depth.py command (fill <...> if needed) ---")
        print(
            f"  python pendle_depth.py --chain-id {args.chain_id} "
            f"--market {addr} --pt-address {pt} --out-token {out_tok} "
            f"--receiver {args.receiver} --spot-price {spot} "
            f"--min-size-pt 1000 --max-size-pt {max_size or '<MAX_SIZE_PT>'} "
            f"--steps 25 --out-csv pt_depth_curve.csv"
        )
        print(f"  --- then: run_analysis.py uses --maturity-years {yrs} "
              f"--pool-tvl {tvl} --underlying-symbol {und_sym} ---")

    print("\n" + "=" * 78)
    print("Pick the maturity with the deepest liquidity (largest TVL), run its "
          "pendle_depth.py command, then run_analysis.py with the printed "
          "--maturity-years / --pool-tvl.\n")


if __name__ == "__main__":
    main()
