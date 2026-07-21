"""
RWA HQLA Framework: Real BUIDL Holder Distribution Lorenz Curve
Data extracted from Dune M2-bis query on 17 June 2026.
Replaces the previously estimated Pareto-based distribution.
"""

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy.optimize import linprog


# ============================================================================
# Real distribution from Dune M2-bis snapshot 2026-06-17
# ============================================================================
# Tail (smallest 25 holders) extracted verbatim from query output
# Top 51 holders: we know n=76 total, total_supply = 181,293,771.96
# Top-3 share = 55.22%, Top-10 = 83.02%, Top-25 = 99.54%
# We reconstruct the top using these constraints + power-law for middle range
# ============================================================================

# Verbatim from Dune (smallest 25 holders, ascending balance)
SMALLEST_25 = [
    7.105427357601002e-15,
    3.4907545604090373e-12,
    3.0325963962241076e-11,
    4.5080383870299556e-11,
    3.346940502524376e-10,
    7.421476766467094e-10,
    7.457856554538012e-10,
    8.75443273429255e-10,
    2.160668088890816e-9,
    2.9979787541378755e-9,
    3.2741809263825417e-9,
    3.490185918053612e-9,
    3.725290298461914e-9,
    7.450580596923828e-9,
    9.313225746154785e-9,
    9.778887033462524e-9,
    5.848705768585205e-7,
    0.00004500150680541992,
    0.0400000012396049,
    0.049999990052015164,
    0.0799999973551877,
    0.4399309754371643,
    1.0,
    1.17,
    1.5,
]

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "snapshot_metrics.json"
with DATA_PATH.open("r", encoding="utf-8") as fh:
    _SNAPSHOT = json.load(fh)["BUIDL"]

TOTAL_SUPPLY = _SNAPSHOT["aum_ethereum_usd"]
TOP3_SHARE = _SNAPSHOT["top3_share"]
TOP10_SHARE = _SNAPSHOT["top10_share"]
TOP25_SHARE = _SNAPSHOT["top25_share"]
N_HOLDERS = _SNAPSHOT["holders_raw"]


def _tilted_flat_split(total: float, n: int, upper: float, lower: float) -> list[float]:
    """Descending split of `total` across `n` holders: each value sits at the
    block mean plus a small linear tilt, with the largest value kept below
    `upper` (the previous block's minimum) and the smallest above `lower`
    (the next block's maximum). All Top-k constraints then hold exactly on
    the sorted result, because blocks never interleave."""
    m = total / n
    if not (lower < m < upper):
        raise ValueError(f"infeasible block: mean {m} outside ({lower}, {upper})")
    if n == 1:
        return [total]
    half = (n - 1) / 2.0
    tilt = 0.5 * min(upper - m, m - lower) / half
    vals = [m + tilt * (half - k) for k in range(n)]
    vals[-1] += total - sum(vals)   # exact total; adjustment is O(1e-9)
    return vals


def reconstruct_distribution():
    """
    Reconstruct the full 76-holder distribution using:
      - the 25 smallest balances (measured verbatim)
      - the Top-3, Top-10, Top-25 cumulative share constraints
      - near-flat descending blocks between the constrained ranks, with
        block boundaries pinned so the global ordering is monotone

    The Top-3/10/25 cumulative shares and the 25 smallest balances are
    MEASURED; the scalar Gini is computed on this constrained
    reconstruction, and every Top-k constraint holds exactly on the sorted
    result. Feasible extremes consistent with the same constraints span
    Gini in [0.850, 0.885] (recomputed by compute_gini_bounds below), so
    the conclusions do not depend on the reconstruction assumptions.
    """
    top3_total = TOP3_SHARE * TOTAL_SUPPLY
    # Split of the measured Top-3 aggregate (55.22%) across ranks 1-3.
    # The 25/18/12 pattern is an assumption; renormalised so the three
    # balances sum EXACTLY to the measured Top-3 share.
    top3 = [top3_total * w / 0.55 for w in (0.25, 0.18, 0.12)]

    tail = sorted(SMALLEST_25, reverse=True)
    ranks_4_10 = _tilted_flat_split(
        (TOP10_SHARE - TOP3_SHARE) * TOTAL_SUPPLY, 7,
        upper=0.95 * min(top3), lower=0.0)
    ranks_11_25 = _tilted_flat_split(
        (TOP25_SHARE - TOP10_SHARE) * TOTAL_SUPPLY, 15,
        upper=0.95 * min(ranks_4_10), lower=0.0)
    remaining_total = (TOTAL_SUPPLY - sum(top3) - sum(ranks_4_10)
                       - sum(ranks_11_25) - sum(SMALLEST_25))
    middle = _tilted_flat_split(
        remaining_total, N_HOLDERS - 25 - 25,
        upper=0.95 * min(ranks_11_25), lower=1.05 * max(tail))

    all_balances = top3 + ranks_4_10 + ranks_11_25 + middle + tail
    assert all(all_balances[i] >= all_balances[i + 1] - 1e-9
               for i in range(len(all_balances) - 1)), "ordering violated"
    return np.array(all_balances)


def compute_gini_bounds():
    """Exact Gini bounds over ALL descending 76-holder distributions
    consistent with the measured constraints (linear programme, HiGHS).

    The Gini coefficient is linear in the balances once the total is fixed:
    with descending balances b_1 >= ... >= b_n summing to T,
        G = (2 / (n T)) * sum_k (n + 1 - k) * b_k  -  (n + 1) / n.
    Free variables: ranks 1..51 (the 25 smallest balances are measured
    verbatim and fixed). Constraints: total supply; Top-3, Top-10, Top-25
    cumulative shares; monotonic descending ordering; continuity with the
    fixed tail (b_51 >= max of the measured smallest balances); b >= 0.
    Minimising and maximising the linear objective yields the exact bounds.
    """
    n = N_HOLDERS
    tail = sorted(SMALLEST_25, reverse=True)          # b_52..b_76 descending
    n_free = n - len(tail)                            # 51
    T = TOTAL_SUPPLY
    s_free = T - sum(tail)

    # objective coefficients for free ranks k = 1..51
    c = np.array([(n + 1 - k) for k in range(1, n_free + 1)], dtype=float)
    fixed_term = sum((n + 1 - k) * b for k, b in
                     zip(range(n_free + 1, n + 1), tail))

    A_eq = [np.ones(n_free)]
    b_eq = [s_free]
    for top_k, share in ((3, TOP3_SHARE), (10, TOP10_SHARE), (25, TOP25_SHARE)):
        row = np.zeros(n_free); row[:top_k] = 1.0
        A_eq.append(row); b_eq.append(share * T)

    # monotonic descending: x_{k+1} - x_k <= 0 ; and tail continuity -x_51 <= -max(tail)
    A_ub, b_ub = [], []
    for k in range(n_free - 1):
        row = np.zeros(n_free); row[k] = -1.0; row[k + 1] = 1.0
        A_ub.append(row); b_ub.append(0.0)
    row = np.zeros(n_free); row[-1] = -1.0
    A_ub.append(row); b_ub.append(-max(tail))

    bounds = []
    for sense in (1.0, -1.0):
        res = linprog(sense * c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                      A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                      bounds=[(0, None)] * n_free, method="highs")
        if not res.success:
            raise RuntimeError(f"LP failed: {res.message}")
        obj = sense * res.fun
        bounds.append((2.0 * (obj + fixed_term)) / (n * T) - (n + 1) / n)
    return min(bounds), max(bounds)


def gini_coefficient(balances):
    """Standard Gini coefficient formula."""
    balances = np.sort(balances)
    n = len(balances)
    cum = np.cumsum(balances)
    return (2 * np.sum(np.arange(1, n + 1) * balances)) / (n * cum[-1]) - (n + 1) / n


def lorenz_curve(balances):
    sorted_b = np.sort(balances)
    cum = np.cumsum(sorted_b) / sorted_b.sum()
    pop = np.arange(1, len(sorted_b) + 1) / len(sorted_b)
    return np.insert(pop, 0, 0), np.insert(cum, 0, 0)


def plot_lorenz(output_path="05_figures/lorenz_buidl.png",
                wide=True):
    balances = reconstruct_distribution()
    pop, cum = lorenz_curve(balances)
    g = gini_coefficient(balances)

    print(f"Reconstructed distribution:")
    print(f"  Holder count        : {len(balances)}")
    print(f"  Total supply        : {balances.sum():,.0f}")
    print(f"  Top-3 share         : {balances[:3].sum() / balances.sum():.3f}")
    print(f"  Top-10 share        : {balances[:10].sum() / balances.sum():.3f}")
    print(f"  Top-25 share        : {balances[:25].sum() / balances.sum():.3f}")
    print(f"  Computed Gini       : {g:.3f}")
    lo, hi = compute_gini_bounds()
    print(f"  Exact LP bounds     : [{lo:.3f}, {hi:.3f}] over all descending"
          f" distributions matching the measured constraints")
    if abs(lo - 0.850) > 0.0015 or abs(hi - 0.885) > 0.0015:
        print("  WARNING: recomputed bounds drift from the documented"
              " [0.850, 0.885]; investigate before publishing")

    # Wide landscape format (2.6:1) for dashboard embedding; square for standalone
    figsize = (13, 5) if wide else (8, 7)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5,
            label="Perfect equality (Gini = 0)")
    ax.plot(pop, cum, "C0-", linewidth=2.5, label=f"BUIDL, reconstructed under measured constraints (Gini = {g:.3f})")
    ax.fill_between(pop, cum, pop, alpha=0.15, color="C0")

    ax.set_xlabel("Cumulative share of holders (sorted ascending)", fontsize=11)
    ax.set_ylabel("Cumulative share of balance", fontsize=11)
    ax.set_title(
        "Lorenz curve: BUIDL holder distribution (Ethereum mainnet)\n"
        f"Snapshot 2026-06-17, 76 holders (≈25 dust), $181M AUM",
        fontsize=12
    )
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=10)
    # No set_aspect('equal') in wide mode: let it fill the rectangle
    if not wide:
        ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved : {output_path}")


if __name__ == "__main__":
    import os as _os; _os.chdir(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    import os
    os.makedirs("05_figures", exist_ok=True)
    plot_lorenz()
