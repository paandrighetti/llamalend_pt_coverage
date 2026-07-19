import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from coverage_model import (DepthCurve, LiquidityAdjustments, MarketParams, Stress,
                            heuristic_depth_agnostic_ceiling, solve_debt_ceiling, coverage_ratio)

df = pd.read_csv("pt_depth_curve_2.csv")
depth = DepthCurve(df["size_usd"].to_numpy(), df["impact"].to_numpy())

market = MarketParams(pt_symbol="PT-wstETH", underlying_symbol="wstETH",
                      maturity_years=1.5288, max_ltv=0.80, representative_ltv=0.70,
                      pool_tvl_usd=2803190.0, soft_liq_band_drop=0.08)
stress = Stress(underlying_depeg=0.05, pt_discount_widen=0.05, horizon_days=2.0)
def adj_for(rho): return LiquidityAdjustments(sigma_max=0.02, maturity_haircut=0.25, wrongway_rho=rho)

dstar = solve_debt_ceiling(depth, market, stress, adj_for(0.40), conservative=False)
heur  = heuristic_depth_agnostic_ceiling(market, 0.30)
cr_h  = coverage_ratio(heur, depth, market, stress, adj_for(0.40))
print(f"check D*(rho=0.40) = ${dstar:,.0f}   heuristic = ${heur:,.0f}   CR@heur = {cr_h:.2f}")

# ---- Figure 1: gradual depth curve with D* and heuristic marked ----
fig, ax = plt.subplots(figsize=(9.2, 5.2))
ax.plot(df["size_usd"]/1e3, df["impact"]*100, color="tab:blue", lw=2.0, marker="o", ms=3)
for s, lbl in [(0.5,"0.5%"),(1.0,"1%"),(2.0,"2%")]:
    x = np.interp(s/100, df["impact"], df["size_usd"])/1e3
    ax.plot([x],[s], "o", color="tab:orange", ms=7, zorder=5)
    ax.annotate(f"{lbl} @ ${x:,.0f}k", (x,s), textcoords="offset points", xytext=(8,-2), fontsize=8)
ax.axvline(dstar/1e3, color="tab:green", ls="--", lw=1.6, label=f"D* (liquidity-aware) = ${dstar/1e3:,.0f}k")
ax.axvline(heur/1e3,  color="tab:red",   ls="--", lw=1.6, label=f"depth-agnostic heuristic = ${heur/1e3:,.0f}k  (CR={cr_h:.2f})")
ax.set_xlabel("PT sell size into Pendle secondary ($k)")
ax.set_ylabel("size-driven slippage (%)")
ax.set_title("PT-wstETH (Dec-2027, $2.80M pool): gradual depth — the heuristic ceiling sits deep in unsafe slippage")
ax.grid(True, alpha=0.25); ax.legend(fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig("/mnt/user-data/outputs/pt_depth_wsteth.png", dpi=140)

# ---- Figure 2: D* vs rho with conservative band ----
rhos = np.linspace(0.1, 1.0, 19)
ds = [solve_debt_ceiling(depth, market, stress, adj_for(r), conservative=False) for r in rhos]
fig2, ax2 = plt.subplots(figsize=(9.2, 5.2))
ax2.plot(rhos, np.array(ds)/1e3, color="tab:blue", lw=2.2, marker="o", ms=4)
ax2.axvspan(0.30, 0.50, color="tab:green", alpha=0.12, label="recommended conservative band rho in [0.3, 0.5]")
ax2.axhline(heur/1e3, color="tab:red", ls="--", lw=1.5, label=f"depth-agnostic heuristic = ${heur/1e3:,.0f}k")
d04 = solve_debt_ceiling(depth, market, stress, adj_for(0.40), conservative=False)
ax2.plot([0.40],[d04/1e3], "o", color="black", ms=8, zorder=6)
ax2.annotate(f"rho=0.40 -> ${d04/1e3:,.0f}k", (0.40, d04/1e3), textcoords="offset points", xytext=(8,8), fontsize=9)
ax2.set_xlabel("wrong-way contraction factor  rho  (forward stress parameter; not calibratable from USDe history)")
ax2.set_ylabel("safe debt ceiling  D*  ($k)")
ax2.set_title("PT-wstETH: safe ceiling D* vs rho — even at rho=1.0, D* stays far below the naive heuristic")
ax2.grid(True, alpha=0.25); ax2.legend(fontsize=8, loc="upper left")
fig2.tight_layout(); fig2.savefig("/mnt/user-data/outputs/dstar_vs_rho_wsteth.png", dpi=140)
print("wrote pt_depth_wsteth.png and dstar_vs_rho_wsteth.png")
print("D* range over rho[0.1..1.0]: ${:,.0f} .. ${:,.0f}".format(min(ds), max(ds)))
