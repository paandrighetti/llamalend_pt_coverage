"""
Retrieve a REAL PT secondary-liquidity depth curve from the Pendle Hosted SDK.

WHY AN API AND NOT A HAND-ROLLED AMM
------------------------------------
Pendle's AMM math (a Notional-style logit curve scaled by time-to-maturity) is
non-trivial and battle-tested. Re-implementing it blindly is a correctness risk.
Instead we treat Pendle as the quoting authority: we ask it for a swap quote at a
grid of sell sizes and read the resulting price impact. This yields the true
on-venue depth curve with zero AMM-math risk. (A heavier alternative is
to read the market's on-chain MarketState and price it with Pendle's own SDK;
see README.)

IMPORTANT
---------
* This script needs outbound internet access to the Pendle API. It will NOT run
  inside a restricted sandbox.
* Pendle API routes/params drift. VERIFY the current schema against
  https://api-v2.pendle.finance/core/docs before trusting output. The script
  fails loudly (prints the raw response) if the schema does not match.
* A built-in sanity check verifies that the smallest-size execution price matches
  the quoted spot/asset price within tolerance; if it fails, do not use the curve.

Output: a CSV with columns [size_usd, impact] consumable by run_analysis.py.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from typing import Any

import requests

DEFAULT_BASE_URL = "https://api-v2.pendle.finance/core"


def _get(url: str, params: dict[str, Any], timeout: float,
         soft: bool = False, max_retries: int = 5) -> dict[str, Any] | None:
    delay = 2.0
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
        except requests.RequestException as e:
            if soft:
                return {"__error__": f"request failed: {e}"}
            sys.exit(f"[pendle_depth] request failed for {url}: {e}")
        # rate limited: back off and retry rather than dropping the size
        if resp.status_code == 429 and attempt < max_retries:
            time.sleep(delay)
            delay = min(delay * 2, 30.0)
            continue
        if resp.status_code != 200:
            payload = {"__error__": resp.text[:300], "__status__": resp.status_code}
            if soft:
                return payload
            sys.exit(
                f"[pendle_depth] HTTP {resp.status_code} for {resp.url}\n"
                f"Response: {resp.text[:1000]}"
            )
        try:
            return resp.json()
        except ValueError:
            if soft:
                return {"__error__": "non-JSON response"}
            sys.exit(f"[pendle_depth] non-JSON response for {resp.url}:\n{resp.text[:1000]}")
    if soft:
        return {"__error__": "rate-limited (429) after retries", "__status__": 429}
    sys.exit("[pendle_depth] rate-limited (429) after retries; raise --pause-s and rerun")


def _extract(d: dict[str, Any], *path: str) -> Any:
    """Walk a nested dict by keys, raising a clear error if a key is missing."""
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            sys.exit(
                f"[pendle_depth] expected key path {'/'.join(path)} not found in response.\n"
                f"Got keys at failure: {list(cur.keys()) if isinstance(cur, dict) else type(cur)}\n"
                f"Verify the Pendle API schema (see module docstring)."
            )
        cur = cur[key]
    return cur


def fetch_swap_quote(
    base_url: str,
    chain_id: int,
    market: str,
    token_in: str,
    token_out: str,
    amount_in_wei: int,
    receiver: str,
    enable_aggregator: bool,
    timeout: float,
    soft: bool = False,
) -> dict[str, Any] | None:
    """
    Single swap quote (exact-in: sell `amount_in_wei` of token_in for token_out).

    Endpoint shape (verify against current docs):
        GET {base}/v2/sdk/{chainId}/markets/{market}/swap
            ?tokenIn=&tokenOut=&amountIn=&receiver=&slippage=
    """
    url = f"{base_url}/v2/sdk/{chain_id}/markets/{market}/swap"
    params = {
        "tokenIn": token_in,
        "tokenOut": token_out,
        "amountIn": str(amount_in_wei),
        "receiver": receiver,
        "slippage": "0.99",          # permissive; we read the quote, not execute
        # Off by default: with the aggregator enabled a quote may route through
        # external venues, so the curve would measure ecosystem-executable depth
        # rather than Pendle-only routing. Enable explicitly if that is what you
        # want to measure, and say so wherever you publish the curve.
        "enableAggregator": "true" if enable_aggregator else "false",
    }
    return _get(url, params, timeout, soft=soft)


def build_depth_curve(
    base_url: str,
    chain_id: int,
    market: str,
    pt_address: str,
    out_token: str,
    receiver: str,
    pt_decimals: int,
    out_decimals: int,
    usd_mark_per_pt: float,
    sizes_pt: list[float],
    timeout: float,
    pause_s: float,
    enable_aggregator: bool = False,
) -> tuple[list[tuple], float | None]:
    """
    Quote token_out for each PT sell size and build a size-driven slippage curve.

    Slippage is REBASED to the smallest-size execution price (the marginal
    price). This isolates the price impact caused by order SIZE and is robust to
    the absolute price level, the routing baseline, and token-unit conventions.
    The absolute mark of PT is a valuation question (the oracle's job), not a
    depth question.

    Returns (rows, smallest_exec_price) where rows are
    (size_usd, impact, api_price_impact), size_usd = size_pt * usd_mark_per_pt,
    impact is in [0,1), and smallest_exec_price is the out-token execution
    price of the smallest filled size (used by the spot sanity check).
    """
    raw: list[tuple] = []  # (size_pt, exec_price_out_per_pt, api_price_impact)
    for size_pt in sizes_pt:
        amount_in_wei = int(round(size_pt * (10 ** pt_decimals)))
        data = fetch_swap_quote(
            base_url=base_url, chain_id=chain_id, market=market,
            token_in=pt_address, token_out=out_token,
            amount_in_wei=amount_in_wei, receiver=receiver,
            enable_aggregator=enable_aggregator, timeout=timeout, soft=True,
        ) or {}
        block = data.get("data") or {}
        amount_out_wei = block.get("amountOut")
        if amount_out_wei is None:
            why = str(data.get("__error__") or data.get("message") or "no quote")
            reason = ("rate-limited after retries (raise --pause-s and rerun)"
                      if "429" in why or "too many requests" in why.lower()
                      else "no/insufficient route at this size (depth limit)")
            print(f"[pendle_depth] skip size {size_pt:g} PT: {reason} -- {why}",
                  file=sys.stderr)
        else:
            exec_price = float(amount_out_wei) / (10 ** out_decimals) / size_pt
            raw.append((size_pt, exec_price, block.get("priceImpact")))
        if pause_s:
            time.sleep(pause_s)

    if not raw:
        return []

    # Rebase to the SMALLEST-size execution price (the marginal price), isolating
    # size-driven slippage. Robust to price level / routing baseline / units.
    ref_exec = raw[0][1]
    rows: list[tuple] = []
    for size_pt, exec_price, api_pi in raw:
        impact = max(0.0, (ref_exec - exec_price) / ref_exec)
        size_usd = size_pt * usd_mark_per_pt        # notional in USD at PT mark
        rows.append((size_usd, impact, api_pi))

    max_impact = max(r[1] for r in rows)
    if max_impact < 0.005:
        print(f"[pendle_depth] NOTE: max size-driven slippage is only {max_impact:.3%} "
              f"at the largest size quoted -- the pool is deep at these sizes. Increase "
              f"--max-size-pt to reach the region where slippage climbs.",
              file=sys.stderr)
    smallest_exec = raw[0][1] if raw else None
    return rows, smallest_exec


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--chain-id", type=int, default=1)
    p.add_argument("--market", required=True, help="Pendle market (AMM) address")
    p.add_argument("--pt-address", required=True)
    p.add_argument("--out-token", required=True,
                   help="token to receive (the SY/underlying/accounting asset)")
    p.add_argument("--receiver", required=True,
                   help="a VALID checksummed EOA used only for quoting (NOT the "
                        "zero address or a precompile like 0x..0001); your wallet works")
    p.add_argument("--pt-decimals", type=int, default=18)
    p.add_argument("--out-decimals", type=int, default=18)
    p.add_argument("--spot-price", type=float, required=True,
                   help="USD mark per PT, used only to scale the USD axis "
                        "(~PT price, e.g. 0.99 near maturity). Slippage is rebased "
                        "to the marginal quote, so this does NOT affect impact.")
    p.add_argument("--min-size-pt", type=float, required=True,
                   help="smallest PT sell size to quote")
    p.add_argument("--max-size-pt", type=float, required=True,
                   help="largest PT sell size to quote")
    p.add_argument("--steps", type=int, default=25)
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument("--pause-s", type=float, default=1.0,
                   help="delay between calls to respect rate limits "
                        "(429s are also retried with exponential back-off)")
    p.add_argument("--out-csv", default="pt_depth_curve.csv")
    p.add_argument("--enable-aggregator", action="store_true",
                   help="allow routing through external aggregators; default off "
                        "so the curve measures Pendle-only routing")
    p.add_argument("--spot-tolerance", type=float, default=0.03,
                   help="max relative gap between smallest exec price and --spot-price")
    p.add_argument("--allow-spot-mismatch", action="store_true",
                   help="downgrade the spot sanity check from fatal to warning")
    args = p.parse_args()

    if args.steps < 2:
        sys.exit("[pendle_depth] --steps must be >= 2")
    if not (0 < args.min_size_pt < args.max_size_pt):
        sys.exit("[pendle_depth] require 0 < --min-size-pt < --max-size-pt")
    if args.spot_price <= 0:
        sys.exit("[pendle_depth] --spot-price must be > 0")

    sizes = [
        args.min_size_pt + (args.max_size_pt - args.min_size_pt) * k / (args.steps - 1)
        for k in range(args.steps)
    ]
    rows, smallest_exec = build_depth_curve(
        args.base_url, args.chain_id, args.market, args.pt_address, args.out_token,
        args.receiver, args.pt_decimals, args.out_decimals, args.spot_price,
        sizes, args.timeout, args.pause_s, args.enable_aggregator,
    )
    if not rows:
        sys.exit(
            "[pendle_depth] no sizes returned a quote. Check: (1) --receiver is a "
            "valid checksummed EOA, (2) --out-token is correct (USDe for sUSDe), "
            "(3) the market address is current, (4) the Pendle API schema "
            "(https://api-v2.pendle.finance/core/docs)."
        )
    # Spot sanity check promised in the module docstring: the smallest filled
    # execution price should sit near the supplied spot mark. A large gap means
    # a wrong unit, a wrong route, or a stale --spot-price; the curve would be
    # rebased on a bad anchor.
    if smallest_exec is not None:
        gap = abs(smallest_exec - args.spot_price) / args.spot_price
        if gap > args.spot_tolerance:
            msg = (f"[pendle_depth] smallest-size exec price {smallest_exec:.6f} "
                   f"deviates {gap:.1%} from --spot-price {args.spot_price:.6f} "
                   f"(tolerance {args.spot_tolerance:.0%}).")
            if args.allow_spot_mismatch:
                print(msg + " Proceeding (--allow-spot-mismatch).", file=sys.stderr)
            else:
                sys.exit(msg + " Fix inputs or pass --allow-spot-mismatch.")

    import datetime as _dt
    prov = [_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            args.chain_id, args.market, args.pt_address, args.out_token,
            args.base_url, str(args.enable_aggregator).lower(), args.spot_price]
    with open(args.out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["size_usd", "impact", "api_price_impact",
                    "ts_utc", "chain_id", "market", "pt_address", "out_token",
                    "api_base", "aggregator_enabled", "spot_price_arg"])
        w.writerows([list(r) + prov for r in rows])
    print(f"[pendle_depth] wrote {len(rows)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
