import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

markets = [
    {"name": "PT-sUSDe\n(deep, 66d, peg-stable USDe)",
     "heuristic": 4.54e6, "dstar": 6.36e6, "dstar_lo": 3.52e6, "dstar_hi": 6.36e6},
    {"name": "PT-wstETH 2027\n(thin, 1.5y, ETH-correlated)",
     "heuristic": 0.8817e6, "dstar": 0.0949e6, "dstar_lo": 0.0949e6, "dstar_hi": 0.0949e6},
]

fig, ax = plt.subplots(figsize=(11, 5.2))
y = np.arange(len(markets))
h = 0.34
c_heur, c_dstar = "#b0772d", "#1f6f6f"

for i, m in enumerate(markets):
    ax.barh(y[i] + h/2, m["heuristic"], height=h, color=c_heur,
            label="Depth-agnostic heuristic" if i == 0 else None, zorder=3)
    ax.barh(y[i] - h/2, m["dstar"], height=h, color=c_dstar,
            label="Coverage-safe D* (rho=0.40)" if i == 0 else None, zorder=3)
    if m["dstar_hi"] > m["dstar_lo"]:
        ax.plot([m["dstar_lo"], m["dstar_hi"]], [y[i]-h/2, y[i]-h/2], color="#0b3b3b", lw=2.2, zorder=4)
        for xb in (m["dstar_lo"], m["dstar_hi"]):
            ax.plot([xb, xb], [y[i]-h/2-0.05, y[i]-h/2+0.05], color="#0b3b3b", lw=2.2, zorder=4)
    ax.text(m["heuristic"]*1.06, y[i]+h/2, f"${m['heuristic']/1e6:,.2f}M",
            va="center", ha="left", fontsize=9, color=c_heur)
    dstar_txt = (f"${m['dstar']/1e6:,.2f}M" if m["dstar_hi"]==m["dstar_lo"]
                 else f"${m['dstar_lo']/1e6:,.1f}-{m['dstar_hi']/1e6:,.1f}M")
    ax.text(m["dstar"]*0.90, y[i]-h/2, dstar_txt, va="center", ha="right",
            fontsize=9, color="white", fontweight="bold", zorder=5)
    # ratio note: to the RIGHT of the longer bar, at group center
    ratio = m["dstar"]/m["heuristic"]
    note = (f"D* ≈ {ratio:.2f}× heuristic" if ratio >= 1
            else f"D* = {ratio:.2f}× heuristic\n(heuristic oversizes ×{1/ratio:.0f})")
    xmax = max(m["heuristic"], m["dstar"])
    ax.text(xmax*1.9, y[i], note, va="center", ha="left", fontsize=9.5, style="italic",
            color=("#0b3b3b" if ratio < 1 else "#666"))

ax.set_xscale("log")
ax.set_yticks(y); ax.set_yticklabels([m["name"] for m in markets], fontsize=9.5)
ax.set_xlabel("Per-market debt ceiling (USD, log scale)")
ax.set_xlim(4e4, 3.0e7)
ax.set_ylim(-0.6, 1.6)
ax.set_title("Depth-agnostic heuristic vs liquidity-coverage $D^*$   (rho = 0.40, per-underlying stress)",
             fontsize=11, pad=10)
ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
ax.grid(True, axis="x", alpha=0.25, which="both")
ax.invert_yaxis()
fig.text(0.5, 0.905, "The coverage constraint corrects in both directions: slack on a deep peg-stable pool, "
         "binding ~9× on a thin long-dated pool", ha="center", fontsize=9.3, color="#444")
fig.subplots_adjust(top=0.84, left=0.20, right=0.97, bottom=0.12)
fig.savefig("/mnt/user-data/outputs/two_market_comparison.png", dpi=150)
print("wrote two_market_comparison.png")
