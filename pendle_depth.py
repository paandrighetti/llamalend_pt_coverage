"""
Retrieve an observed PT secondary-liquidity depth curve from the Pendle Hosted SDK.

WHY AN API AND NOT A HAND-ROLLED AMM
------------------------------------
Pendle's AMM math (a Notional-style logit curve scaled by time-to-maturity) is
non-trivial and battle-tested. Re-implementing it blindly is a correctness risk.
Instead we treat Pendle as the quoting authority: we ask it for a swap quote at a
grid of sell sizes and read the resulting price impact. This avoids
re-implementing Pendle AMM mathematics, while retaining API-schema, routing,
unit-conversion, and data-availability risks. A heavier alternative is to read
the market's on-chain MarketState and price it with Pendle's own SDK; see README.

IMPORTANT
---------
* This script needs outbound internet access to the Pendle API. It will NOT run
  inside a restricted sandbox.
* Pendle API routes and schemas can change. Verify the current Hosted SDK
  documentation before a fresh pull. The script prints a clear error if the
  expected response shape is not present.
* A built-in sanity check verifies that the smallest-size execution price matches
  the quoted spot/asset price within tolerance; if it fails, do not use the curve.

Output: a provenance-bearing CSV consumable by run_analysis.py.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from typing import Any

import requests

DEFAULT_BASE_URL = "https://api-v2.pendle.finance/core"


class QuoteCollectionError(SystemExit):
    """Abort a depth measurement that is invalid for technical reasons."""




def _post(
    url: str,
    payload: dict[str, Any],
    timeout: float,
    soft: bool = False,
    max_retries: int = 5,
) -> dict[str, Any] | None:
    """POST JSON and preserve the distinction between routing and API failures."""

    delay = 2.0

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)

        except requests.Timeout as exc:
            result = {
                "__error__": f"request timed out: {exc}",
                "__kind__": "timeout",
            }

            if soft:
                return result

            raise QuoteCollectionError(
                f"[pendle_depth] request timed out for {url}: {exc}"
            ) from exc

        except requests.RequestException as exc:
            result = {
                "__error__": f"request failed: {exc}",
                "__kind__": "request_error",
            }

            if soft:
                return result

            raise QuoteCollectionError(
                f"[pendle_depth] request failed for {url}: {exc}"
            ) from exc

        if resp.status_code == 429 and attempt < max_retries:
            time.sleep(delay)
            delay = min(delay * 2, 30.0)
            continue

        if resp.status_code != 200:
            status = resp.status_code

            if status == 429:
                kind = "rate_limited"
            elif status in {400, 401, 403, 404, 409, 422}:
                kind = "client_error"
            elif status >= 500:
                kind = "server_error"
            else:
                kind = "http_error"

            result = {
                "__error__": resp.text[:300],
                "__status__": status,
                "__kind__": kind,
            }

            if soft:
                return result

            raise QuoteCollectionError(
                f"[pendle_depth] HTTP {status} for {url}\n"
                f"Response: {resp.text[:1000]}"
            )

        try:
            decoded = resp.json()

        except ValueError as exc:
            result = {
                "__error__": "non-JSON response",
                "__status__": resp.status_code,
                "__kind__": "schema_error",
            }

            if soft:
                return result

            raise QuoteCollectionError(
                f"[pendle_depth] non-JSON response for {url}:\n"
                f"{resp.text[:1000]}"
            ) from exc

        if not isinstance(decoded, dict):
            result = {
                "__error__": (
                    f"unexpected JSON type: {type(decoded).__name__}"
                ),
                "__status__": resp.status_code,
                "__kind__": "schema_error",
            }

            if soft:
                return result

            raise QuoteCollectionError(
                f"[pendle_depth] expected a JSON object from {url}, "
                f"got {type(decoded).__name__}"
            )

        return decoded

    result = {
        "__error__": "rate-limited (429) after retries",
        "__status__": 429,
        "__kind__": "rate_limited",
    }

    if soft:
        return result

    raise QuoteCollectionError(
        "[pendle_depth] rate-limited (429) after retries; "
        "raise --pause-s and rerun"
    )


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
    use_limit_order: bool = False,
) -> dict[str, Any] | None:
    """
    Request an exact-input quote through Pendle's recommended v3 Convert API.

    The Convert API identifies the action from the input and output token
    addresses. ``market`` is retained in this function signature for provenance
    and backwards-compatible callers; the universal endpoint does not accept a
    market parameter. ``use_limit_order`` defaults to false so the published
    curve measures AMM/router capacity rather than order-book liquidity.
    """
    del market
    url = f"{base_url}/v3/sdk/{chain_id}/convert"
    payload: dict[str, Any] = {
        "receiver": receiver,
        "slippage": 0.01,
        "enableAggregator": enable_aggregator,
        "inputs": [{"token": token_in, "amount": str(amount_in_wei)}],
        "outputs": [token_out],
        "useLimitOrder": use_limit_order,
    }
    return _post(url, payload, timeout, soft=soft)


def _normalise_quote(
    response: dict[str, Any], expected_token_out: str
) -> tuple[str | None, float | None]:
    """Return ``(amount_out_wei, api_price_impact)`` from Convert or legacy data."""
    routes = response.get("routes")
    if isinstance(routes, list) and routes:
        route = routes[0] if isinstance(routes[0], dict) else {}
        outputs = route.get("outputs") or []
        selected: dict[str, Any] | None = None
        for output in outputs:
            if not isinstance(output, dict):
                continue
            if str(output.get("token", "")).lower() == expected_token_out.lower():
                selected = output
                break
        if selected is None and len(outputs) == 1 and isinstance(outputs[0], dict):
            selected = outputs[0]
        amount = None if selected is None else selected.get("amount")
        data = route.get("data") if isinstance(route.get("data"), dict) else {}
        return (None if amount is None else str(amount), data.get("priceImpact"))

    # Backwards-compatible parser for archived fixtures and earlier API responses.
    block = response.get("data") if isinstance(response.get("data"), dict) else {}
    amount = block.get("amountOut")
    return (None if amount is None else str(amount), block.get("priceImpact"))


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
    out_token_usd_price: float = 1.0,
    use_limit_order: bool = False,
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
    impact is in [0,1), and smallest_exec_price is the USD execution
    price of the smallest filled size after applying ``out_token_usd_price``.
    Set that conversion explicitly when the output token is not worth exactly
    one US dollar.
    """
    raw: list[tuple] = []  # (size_pt, exec_price_out_per_pt, api_price_impact)
    for size_pt in sizes_pt:
        amount_in_wei = int(round(size_pt * (10 ** pt_decimals)))
        data = fetch_swap_quote(
            base_url=base_url, chain_id=chain_id, market=market,
            token_in=pt_address, token_out=out_token,
            amount_in_wei=amount_in_wei, receiver=receiver,
            enable_aggregator=enable_aggregator, timeout=timeout, soft=True,
            use_limit_order=use_limit_order,
        ) or {}
        amount_out_wei, api_price_impact = _normalise_quote(data, out_token)
        if amount_out_wei is None:
            routes = data.get("routes")

            # Convert v3 explicitly returning an empty route list is treated as
            # a genuine absence of executable liquidity at this size.
            explicit_no_route = (
                isinstance(routes, list)
                and len(routes) == 0
                and "__error__" not in data
            )

            if explicit_no_route:
                print(
                    f"[pendle_depth] skip size {size_pt:g} PT: "
                    "no executable route at this size (depth limit)",
                    file=sys.stderr,
                )
            else:
                kind = str(data.get("__kind__") or "schema_error")
                status = data.get("__status__")
                why = str(
                    data.get("__error__")
                    or data.get("message")
                    or "response contained no usable output amount"
                )

                status_text = "" if status is None else f" HTTP {status}"

                raise QuoteCollectionError(
                    f"[pendle_depth] quote collection aborted at "
                    f"{size_pt:g} PT: {kind}{status_text}: {why}. "
                    "This is a technical measurement failure, not a "
                    "liquidity-depth observation."
                )
        else:
            exec_price = float(amount_out_wei) / (10 ** out_decimals) / size_pt
            raw.append((size_pt, exec_price, api_price_impact))
        if pause_s:
            time.sleep(pause_s)

    raw.sort(key=lambda item: item[0])

    if not raw:
        return [], None

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
    smallest_exec_usd = raw[0][1] * out_token_usd_price if raw else None
    return rows, smallest_exec_usd


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
                   help="USD mark per PT, used to scale the USD axis and check "
                        "the smallest execution after output-token conversion "
                        "(~PT price, e.g. 0.99 near maturity). Slippage is rebased "
                        "to the marginal quote, so this does NOT affect impact.")
    p.add_argument("--out-token-usd-price", type=float, default=1.0,
                   help="USD price of one output-token unit for the spot sanity "
                        "check. Default 1.0 is an explicit par assumption; set "
                        "the observed value for depegged or non-USD output tokens.")
    p.add_argument("--min-size-pt", type=float, required=True,
                   help="smallest PT sell size to quote")
    p.add_argument("--max-size-pt", type=float, required=True,
                   help="largest PT sell size to quote")
    p.add_argument("--steps", type=int, default=25)
    p.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds; default 120 for Hosted SDK routing",
    )
    p.add_argument("--pause-s", type=float, default=1.0,
                   help="delay between calls to respect rate limits "
                        "(429s are also retried with exponential back-off)")
    p.add_argument("--out-csv", default="pt_depth_curve.csv")
    p.add_argument("--enable-aggregator", action="store_true",
                   help="allow routing through external aggregators; default off "
                        "so the curve measures Pendle-native routing")
    p.add_argument("--use-limit-order", action="store_true",
                   help="include Pendle limit-order liquidity; default off so the "
                        "curve isolates AMM/router capacity")
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
    if args.out_token_usd_price <= 0:
        sys.exit("[pendle_depth] --out-token-usd-price must be > 0")

    sizes = [
        args.min_size_pt + (args.max_size_pt - args.min_size_pt) * k / (args.steps - 1)
        for k in range(args.steps)
    ]
    rows, smallest_exec = build_depth_curve(
        args.base_url, args.chain_id, args.market, args.pt_address, args.out_token,
        args.receiver, args.pt_decimals, args.out_decimals, args.spot_price,
        sizes, args.timeout, args.pause_s, args.enable_aggregator,
        out_token_usd_price=args.out_token_usd_price,
        use_limit_order=args.use_limit_order,
    )
    if not rows:
        sys.exit(
            "[pendle_depth] no sizes returned a quote. Check: (1) --receiver is a "
            "valid checksummed EOA, (2) --out-token is correct (USDe for sUSDe), "
            "(3) the market address is current, (4) the Pendle API schema "
            "(https://api-v2.pendle.finance/core/docs)."
        )
    # Spot sanity check promised in the module docstring: the smallest filled
    # USD execution price should sit near the supplied USD spot mark. A
    # large gap means a wrong unit, conversion, route, or stale --spot-price;
    # the curve would be rebased on a bad anchor.
    if smallest_exec is not None:
        gap = abs(smallest_exec - args.spot_price) / args.spot_price
        if gap > args.spot_tolerance:
            msg = (f"[pendle_depth] smallest-size USD exec price {smallest_exec:.6f} "
                   f"deviates {gap:.1%} from --spot-price {args.spot_price:.6f} "
                   f"(tolerance {args.spot_tolerance:.0%}).")
            if args.allow_spot_mismatch:
                print(msg + " Proceeding (--allow-spot-mismatch).", file=sys.stderr)
            else:
                sys.exit(msg + " Fix inputs or pass --allow-spot-mismatch.")

    import datetime as _dt
    prov = [_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            args.chain_id, args.market, args.pt_address, args.out_token,
            args.base_url, "v3_convert_post",
            str(args.enable_aggregator).lower(),
            str(args.use_limit_order).lower(), 0.01, args.spot_price,
            args.out_token_usd_price]
    with open(args.out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["size_usd", "impact", "api_price_impact",
                    "ts_utc", "chain_id", "market", "pt_address", "out_token",
                    "api_base", "api_route", "aggregator_enabled",
                    "limit_order_enabled", "slippage_tolerance",
                    "spot_price_arg", "out_token_usd_price_arg"])
        w.writerows([list(r) + prov for r in rows])
    print(f"[pendle_depth] wrote {len(rows)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
