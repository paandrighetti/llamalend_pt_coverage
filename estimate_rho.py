"""
estimate_rho.py
===============
Empirically estimate the wrong-way contraction factor rho from a past USDe depeg.

rho = (stressed absorbable PT capacity) / (calm absorbable capacity), proxied by
the contraction of a USDe/sUSDe-linked liquidity series through the episode. Two
estimators are reported (cross-checking, falsifiable):

  1. Episode:    rho_ep  = (trough capacity during the episode) / (pre-episode median)
  2. Regression: log(capacity) ~ a + b*dev  ->  rho_reg(d*) = exp(b * d*)
                 evaluated at the model's stress depeg d* (relative to dev=0)

Both are clamped to (0, 1]: we never credit liquidity that *grew* under stress.

INPUT  rho_inputs.csv columns:
    date          ISO date
    usde_price    USDe price in USD (~1.0 at peg)        [or provide usde_dev]
    capacity_usd  liquidity proxy (pool TVL / reserve), USD

OUTPUT  rho_episode, rho_regression, a recommended rho, the worst observed depeg
        (to calibrate run_analysis --depeg), and a co-movement chart.

No network. Verify the logic with:  python estimate_rho.py --synthetic
"""
from __future__ import annotations

import argparse
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def synthetic() -> pd.DataFrame:
    """A 180-day series with a ~4.5% USDe depeg around day 92 and wrong-way
    liquidity contraction. Illustrative only."""
    n = 180
    t = np.arange(n)
    dev = 0.045 * np.exp(-((t - 92) ** 2) / (2 * 3.0 ** 2))      # transient depeg
    base = 60e6 + 2e6 * np.sin(t / 15.0)                         # slow TVL drift
    rng = np.random.RandomState(0)
    cap = base * (1.0 - 6.0 * dev) * (1.0 + 0.01 * rng.randn(n))  # contracts on depeg
    return pd.DataFrame({
        "date": pd.date_range("2024-06-01", periods=n),
        "usde_price": 1.0 - dev,
        "capacity_usd": cap,
    })


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    if "usde_dev" not in df.columns:
        if "usde_price" not in df.columns:
            sys.exit("[estimate_rho] CSV needs 'usde_price' or 'usde_dev'.")
        df["usde_dev"] = (1.0 - df["usde_price"]).clip(lower=0.0)
    df = df.dropna(subset=["capacity_usd"])
    df = df[df["capacity_usd"] > 0].reset_index(drop=True)
    if len(df) < 20:
        sys.exit("[estimate_rho] need >= 20 valid daily points.")
    return df


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--inputs-csv", help="rho_inputs.csv [date, usde_price, capacity_usd]")
    src.add_argument("--synthetic", action="store_true", help="illustrative demo")
    p.add_argument("--stress-depeg", type=float, default=0.03,
                   help="d* at which to evaluate the regression rho (match run_analysis --depeg)")
    p.add_argument("--baseline-days", type=int, default=30,
                   help="pre-episode window (days) for the calm baseline")
    p.add_argument("--lag-days", type=int, default=5,
                   help="days after the episode to keep (liquidity withdrawal lags)")
    p.add_argument("--chart", default="rho_wrongway.png")
    args = p.parse_args()

    df = synthetic() if args.synthetic else load(args.inputs_csv)
    if "usde_dev" not in df.columns:
        df["usde_dev"] = (1.0 - df["usde_price"]).clip(lower=0.0)
    dev = df["usde_dev"].to_numpy()
    cap = df["capacity_usd"].to_numpy()

    # --- worst USDe depeg in sample --------------------------------------- #
    imax = int(np.argmax(dev))
    d_max = float(dev[imax])
    has_episode = d_max >= 0.005

    # --- capacity max-drawdown (always available, even without a depeg) ---- #
    run_max = np.maximum.accumulate(cap)
    dd_frac = cap / run_max
    t_idx = int(np.argmin(dd_frac))
    rho_dd = float(dd_frac[t_idx])               # worst trough vs preceding peak
    peak_idx = int(np.argmax(cap[: t_idx + 1])) if t_idx > 0 else 0

    rho_ep = rho_reg = r2 = b1 = None
    start = end = None
    if has_episode:
        thr = max(0.005, 0.5 * d_max)
        in_ep = np.where(dev >= thr)[0]
        start = int(in_ep.min())
        end = min(len(df) - 1, int(in_ep.max()) + args.lag_days)
        base_slice = cap[max(0, start - args.baseline_days):start]
        c0 = float(np.median(base_slice)) if base_slice.size else float(np.median(cap[:start + 1]))
        c_trough = float(np.min(cap[start:end + 1]))
        rho_ep = min(1.0, c_trough / c0) if c0 > 0 else float("nan")
        if np.std(dev) > 1e-9:                   # guard: regression needs variance in dev
            y = np.log(cap)
            b1, b0 = np.polyfit(dev, y, 1)
            yhat = b0 + b1 * dev
            ss_res = float(((y - yhat) ** 2).sum())
            ss_tot = float(((y - y.mean()) ** 2).sum())
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
            rho_reg = min(1.0, float(np.exp(b1 * args.stress_depeg)))

    candidates = [v for v in (rho_ep, rho_reg) if isinstance(v, float)]
    rho_reco = min(candidates) if candidates else None

    # --- report ----------------------------------------------------------- #
    print("=" * 70)
    print("WRONG-WAY CONTRACTION FACTOR rho  (USDe depeg -> PT liquidity)")
    print("=" * 70)
    if args.synthetic:
        print("!! SYNTHETIC DATA -- illustrative only !!")
    print(f"Sample                         : {df['date'].iloc[0].date()} -> "
          f"{df['date'].iloc[-1].date()}  ({len(df)} days)")
    print(f"Worst observed USDe depeg d_max: {d_max:.2%}  on {df['date'].iloc[imax].date()}")
    print("-" * 70)
    print(f"Capacity max-drawdown          : {rho_dd:.3f}   "
          f"(${cap[peak_idx]/1e6:,.1f}M {df['date'].iloc[peak_idx].date()} -> "
          f"${cap[t_idx]/1e6:,.1f}M {df['date'].iloc[t_idx].date()})")
    print(f"  (trough / preceding peak)      NB: conflates organic outflows + stress")
    if has_episode:
        print("-" * 70)
        print(f"Depeg episode window           : {df['date'].iloc[start].date()} -> "
              f"{df['date'].iloc[end].date()}")
        print(f"  rho_episode (trough/baseline): {rho_ep:.3f}")
        if rho_reg is not None:
            print(f"  regression slope b           : {b1:+.2f}   R^2 = {r2:.2f}  (b<0 = wrong-way)")
            print(f"  rho_regression at d*={args.stress_depeg:.0%}    : {rho_reg:.3f}")
    print("=" * 70)
    if rho_reco is not None:
        print(f"RECOMMENDED rho (conservative) : {rho_reco:.3f}")
        print(f"  -> run_analysis.py --rho {rho_reco:.2f} --depeg "
              f"{max(args.stress_depeg, round(d_max,3)):.3f}")
    else:
        print("RECOMMENDED rho                : NOT CALIBRATABLE from a USDe depeg")
        print("  USDe held peg (<0.5%) across the sample, so the depeg-driven wrong-way")
        print("  channel is unobserved. Treat rho as a forward STRESS PARAMETER: present")
        print("  D* across rho (dstar_vs_rho) and pick a conservative rho in [0.3, 0.5].")
        print(f"  Context only: worst capacity drawdown was {rho_dd:.2f} (organic + stress mixed).")
    print("=" * 70)

    # --- chart ------------------------------------------------------------ #
    fig, ax1 = plt.subplots(figsize=(10, 5.2))
    ax1.plot(df["date"], cap / 1e6, color="tab:blue", lw=1.8, label="liquidity capacity ($M)")
    ax1.set_ylabel("liquidity capacity ($M)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(df["date"], dev * 100, color="tab:red", lw=1.4, label="USDe depeg (%)")
    ax2.set_ylabel("USDe downside deviation (%)", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    if has_episode:
        ax1.axvspan(df["date"].iloc[start], df["date"].iloc[end], color="tab:red", alpha=0.10)
        sub = (f"rho_episode={rho_ep:.2f}"
               + (f"  rho_reg={rho_reg:.2f}  (rec {rho_reco:.2f})" if rho_reg is not None else ""))
    else:
        ax1.axvline(df["date"].iloc[t_idx], color="tab:purple", ls=":", lw=1.2)
        sub = (f"USDe peg-stable (max dev {d_max:.2%}); rho not calibratable from a depeg. "
               f"Worst capacity drawdown {rho_dd:.2f}")
    ttl = "Wrong-way check: USDe deviation vs PT-linked liquidity"
    if args.synthetic:
        ttl += "  [SYNTHETIC]"
    ax1.set_title(f"{ttl}\n{sub}", fontsize=10)
    ax1.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(args.chart, dpi=140)
    print(f"[estimate_rho] chart written to {args.chart}")


if __name__ == "__main__":
    main()
