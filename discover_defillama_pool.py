"""
discover_defillama_pool.py
==========================
List DefiLlama yield pools matching a symbol (and optional project), printing the
pool UUID + current TVL so you can pick a capacity proxy for estimate_rho. Emits
the ready-to-paste fetch_rho_inputs.py command for each.

Run (needs internet to DefiLlama):
    python discover_defillama_pool.py --symbol USDe --project curve
    python discover_defillama_pool.py --symbol sUSDe --project pendle

Pick a pool with high TVL and (ideally) long history that spans a past USDe
depeg. Curve USDe pools are persistent (reliable long history); Pendle sUSDe
pools are the most apples-to-apples but may be young/short.
"""
from __future__ import annotations

import argparse
import sys

import requests

POOLS_URL = "https://yields.llama.fi/pools"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", required=True, help="substring to match in the pool symbol (e.g. USDe)")
    p.add_argument("--project", default="", help="optional substring to match in the project (e.g. curve, pendle)")
    p.add_argument("--chain", default="", help="optional substring to match in the chain (e.g. Ethereum)")
    p.add_argument("--min-tvl", type=float, default=1e6, help="ignore pools below this TVL (USD)")
    p.add_argument("--limit", type=int, default=15)
    p.add_argument("--days", type=int, default=500, help="passed through into the emitted fetch command")
    p.add_argument("--raw", action="store_true", help="print one raw pool record and exit")
    args = p.parse_args()

    try:
        r = requests.get(POOLS_URL, timeout=90)
    except requests.RequestException as e:
        sys.exit(f"[discover_dl] request failed: {e}")
    if r.status_code != 200:
        sys.exit(f"[discover_dl] HTTP {r.status_code}\n{r.text[:600]}")
    try:
        payload = r.json()
    except ValueError:
        sys.exit("[discover_dl] non-JSON response from DefiLlama.")

    pools = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(pools, list):
        sys.exit("[discover_dl] unexpected /pools shape; DefiLlama may have changed it.")

    if args.raw:
        print(str(pools[0])[:1500])
        return

    sym, proj, ch = args.symbol.lower(), args.project.lower(), args.chain.lower()
    matches = [
        x for x in pools
        if sym in str(x.get("symbol", "")).lower()
        and (not proj or proj in str(x.get("project", "")).lower())
        and (not ch or ch in str(x.get("chain", "")).lower())
        and (x.get("tvlUsd") or 0) >= args.min_tvl
    ]
    matches.sort(key=lambda x: x.get("tvlUsd") or 0, reverse=True)

    if not matches:
        sys.exit(f"[discover_dl] no pools match symbol~'{args.symbol}' "
                 f"project~'{args.project}' chain~'{args.chain}' tvl>={args.min_tvl:.0f}.")

    print(f"\n{len(matches)} pools match (showing top {min(args.limit, len(matches))}, by TVL):\n"
          + "=" * 86)
    for x in matches[:args.limit]:
        uuid = x.get("pool")
        print(f"\n{x.get('symbol')}  |  {x.get('project')}  |  {x.get('chain')}  "
              f"|  TVL ${ (x.get('tvlUsd') or 0)/1e6:,.2f}M  |  APY {x.get('apy')}")
        print(f"  pool UUID : {uuid}")
        print(f"  -> python fetch_rho_inputs.py --pool {uuid} --days {args.days}")
    print("\n" + "=" * 86)
    print("Prefer high TVL + long history (spans a past USDe depeg). Run the emitted "
          "command, then: python estimate_rho.py --inputs-csv rho_inputs.csv\n")


if __name__ == "__main__":
    main()
