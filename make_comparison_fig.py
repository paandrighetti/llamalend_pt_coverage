import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# values from the locked analysis (sUSDe: prior-session validated; wstETH: this session)
markets   = ["PT-sUSDe\n(66d, $9.49M, peg-stable)", "PT-wstETH\n(1.53y, $2.80M, ETH-corr.)"]
heuristic = [4.50e6, 0.8817e6]      # depth-agnostic heuristic ceiling
dstar     = [6.41e6, 0.0949e6]      # coverage-safe D* at rho=0.40 (central)

x = np.arange(len(markets)); w = 0.36
fig, ax = plt.subplots(figsize=(9.0, 5.4))
b1 = ax.bar(x - w/2, heuristic, w, label="depth-agnostic heuristic", color="tab:red", alpha=0.85)
b2 = ax.bar(x + w/2, dstar,     w, label="coverage-safe D* (rho=0.40)", color="tab:green", alpha=0.85)
ax.set_yscale("log")
ax.set_ylabel("debt ceiling ($, log scale)")
ax.set_xticks(x); ax.set_xticklabels(markets)
ax.set_title("Depth-agnostic heuristic vs liquidity-coverage D*\nthe naive rule is mildly tight on the deep pool and ~9x too loose on the thin long-dated one")
for b in list(b1)+list(b2):
    h = b.get_height()
    ax.annotate(f"${h/1e6:,.2f}M" if h>=1e6 else f"${h/1e3:,.0f}k",
                (b.get_x()+b.get_width()/2, h), textcoords="offset points",
                xytext=(0,3), ha="center", fontsize=9)
# ratio annotations
ax.annotate("D* / heuristic = 1.4x\n(corrects UP: mildly tight)", (0, max(heuristic[0],dstar[0])*1.7),
            ha="center", fontsize=8, color="dimgray")
ax.annotate("D* / heuristic = 0.11x\n(corrects DOWN: ~9x too loose,\nCR=0.11 at heuristic)", (1, heuristic[1]*1.7),
            ha="center", fontsize=8, color="dimgray")
ax.legend(loc="upper right", fontsize=9); ax.grid(True, axis="y", alpha=0.25)
ax.set_ylim(5e4, 2e7)
fig.tight_layout(); fig.savefig("/mnt/user-data/outputs/two_market_comparison.png", dpi=140)
print("wrote two_market_comparison.png")
