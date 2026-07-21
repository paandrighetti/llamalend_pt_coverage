"""
RWA HQLA Framework: Block C Market Criteria Comparison (v1.1)
Regenerated 2026-06-17 with real Dune M6 + M2 measured data.

Replaces the v1.0 figure which had estimated/placeholder values.
All values below are measured on Ethereum mainnet via Dune queries M2 and M6,
snapshot 17 June 2026. Product-specific bIB01 USD AUM is not established
from the included public data package and is shown as unavailable.

Output: 05_figures/market_comparison.png
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# Canonical snapshot inputs
# ============================================================================
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "snapshot_metrics.json"
with DATA_PATH.open("r", encoding="utf-8") as fh:
    SNAPSHOT = json.load(fh)

PRODUCTS = ["BUIDL", "OUSG", "bIB01"]
COLORS = ["#4c8fc9", "#e8893c", "#5aa469"]

HOLDERS = [SNAPSHOT[p]["holders_raw"] for p in PRODUCTS]
AUM_ETH_M = [
    SNAPSHOT["BUIDL"]["aum_ethereum_usd"] / 1e6,
    SNAPSHOT["OUSG"]["aum_ethereum_usd"] / 1e6,
    None,
]
SECONDARY_TRANSFERS = [SNAPSHOT[p]["secondary_transfers"] for p in PRODUCTS]
SECONDARY_SHARE = [SNAPSHOT[p]["secondary_share_pct"] for p in PRODUCTS]



def plot_comparison(output_path="05_figures/market_comparison.png"):
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle(
        "Block C: Market Criteria Empirical Validation\n"
        "Snapshot 2026-06-17, Ethereum mainnet; bIB01 product AUM unavailable",
        fontsize=13
    )

    # Panel 1: AUM on Ethereum mainnet (log scale, 3 orders of magnitude)
    ax = axes[0, 0]
    known_idx = [i for i, value in enumerate(AUM_ETH_M) if value is not None]
    known_vals = [AUM_ETH_M[i] for i in known_idx]
    bars = ax.bar(known_idx, known_vals, color=[COLORS[i] for i in known_idx],
                  edgecolor="black", linewidth=0.5)
    ax.set_yscale("log")
    ax.set_xticks(range(len(PRODUCTS)), PRODUCTS)
    ax.set_title("AUM on Ethereum mainnet ($M, log scale)")
    ax.set_ylabel("$M (log)")
    for bar, val in zip(bars, known_vals):
        label = f"${val:.0f}M" if val >= 1 else f"${val*1000:.0f}K"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                label, ha="center", va="bottom", fontsize=9)
    ax.text(2, min(known_vals), "AUM not established\nfrom included data",
            ha="center", va="center", fontsize=8, style="italic", color="#555")

    # Panel 2: Holders
    ax = axes[0, 1]
    bars = ax.bar(PRODUCTS, HOLDERS, color=COLORS, edgecolor="black", linewidth=0.5)
    ax.set_title("Holders on Ethereum mainnet (raw count)")
    ax.set_ylabel("Count")
    for bar, val in zip(bars, HOLDERS):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                str(val), ha="center", va="bottom", fontsize=9)
    ax.text(0.5, -0.18,
            "Note: includes dust wallets. BUIDL effective holders ~51 after filtering sub-$2 balances.",
            transform=ax.transAxes, ha="center", fontsize=7, style="italic", color="#666")

    # Panel 3: Cumulative secondary transfers
    ax = axes[1, 0]
    bars = ax.bar(PRODUCTS, SECONDARY_TRANSFERS, color=COLORS, edgecolor="black", linewidth=0.5)
    ax.set_title("Cumulative secondary transfers (full history)")
    ax.set_ylabel("Transfers")
    for bar, val in zip(bars, SECONDARY_TRANSFERS):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f"{val:,}", ha="center", va="bottom", fontsize=9)

    # Panel 4: Secondary share %
    ax = axes[1, 1]
    bars = ax.bar(PRODUCTS, SECONDARY_SHARE, color=COLORS, edgecolor="black", linewidth=0.5)
    ax.set_title("Secondary share of transfers (%)")
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    for bar, val in zip(bars, SECONDARY_SHARE):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f"{val:.0f}%", ha="center", va="bottom", fontsize=9)
    ax.text(0.5, -0.18,
            "bIB01's 96% ratio reflects free transferability as a debt instrument,\nbut only 0.43 transfers/day in absolute terms.",
            transform=ax.transAxes, ha="center", fontsize=7, style="italic", color="#666")

    fig.text(0.5, 0.005,
             "BCBS 238 §24(d): 'active and sizable market with committed market makers, low concentration'. All three fall short under this framework; address counts are not beneficial-owner counts.",
             ha="center", fontsize=9, style="italic", color="#555")

    plt.tight_layout(rect=(0, 0.03, 1, 0.96))
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    import os as _os; _os.chdir(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    import os
    os.makedirs("05_figures", exist_ok=True)
    plot_comparison()
