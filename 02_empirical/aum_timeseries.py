"""
RWA HQLA Framework: AUM Time-Series Visualisation
Version 1.0: 2026-05-11

Produces the AUM trajectory chart for Section 3 of the article.
Data points are anchored on publicly reported milestones; intermediate
values are interpolated for visualisation. Replace with Dune query output
(M1 in 02_empirical/dune_queries.sql) for production accuracy.

Output: 05_figures/aum_timeseries.png / .svg
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from datetime import datetime
import numpy as np


# ============================================================================
# Anchored data points from public reporting
# ============================================================================
# BUIDL: launched March 2024, milestones from press releases / RWA.xyz
# OUSG: launched Jan 2023, ~$770M by April 2026
# Backed product suite: public platform-level milestones. These values are
# not a bIB01-specific AUM series and must not be interpreted as such.
# ============================================================================

BUIDL_ANCHORS = [
    ("2024-03-15", 0),
    ("2024-04-30", 245_000_000),
    ("2024-07-31", 502_000_000),
    ("2024-12-31", 640_000_000),
    ("2025-08-31", 2_400_000_000),
    ("2026-05-06", 2_282_555_237),
]

OUSG_ANCHORS = [
    ("2023-01-31", 0),
    ("2023-12-31", 130_000_000),
    ("2024-07-31", 220_000_000),
    ("2025-06-30", 600_000_000),
    ("2026-04-30", 770_000_000),
]

BACKED_SUITE_ANCHORS = [
    ("2023-04-15", 0),
    ("2023-10-31", 37_000_000),
    ("2024-12-31", 110_000_000),
    ("2026-04-30", 250_000_000),
]


def to_dates_values(anchors):
    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in anchors]
    values = [v for _, v in anchors]
    return dates, values


def plot_aum_timeseries(output_png="05_figures/aum_timeseries.png",
                        output_svg="05_figures/aum_timeseries.svg"):
    fig, ax = plt.subplots(figsize=(13, 7))

    series = [
        ("BUIDL (BlackRock)", BUIDL_ANCHORS, "#1f77b4"),
        ("OUSG (Ondo)", OUSG_ANCHORS, "#ff7f0e"),
        ("Backed product suite (not bIB01-specific)", BACKED_SUITE_ANCHORS, "#2ca02c"),
    ]

    for label, anchors, color in series:
        dates, values = to_dates_values(anchors)
        values_bn = [v / 1e9 for v in values]
        ax.plot(dates, values_bn, "o-", color=color, linewidth=2.5,
                markersize=6, label=label)
        # annotate final value
        ax.annotate(f"${values_bn[-1]:.2f}B",
                    xy=(dates[-1], values_bn[-1]),
                    xytext=(8, 0), textcoords="offset points",
                    fontsize=9, color=color, fontweight="bold",
                    va="center")

    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Assets Under Management (USD billions)", fontsize=11)
    ax.set_title(
        "Reported Tokenised-Treasury AUM Milestones (2024-2026)\n"
        "Anchored on public reporting milestones, snapshot 2026-06-17",
        fontsize=13, pad=12
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("$%.1fB"))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=11)
    plt.xticks(rotation=45)

    # Annotation for the empirical paradox
    ax.annotate(
        "BUIDL: $2.28B AUM\nbut $0 secondary 24h volume",
        xy=(datetime.strptime("2026-05-06", "%Y-%m-%d"), 2.28),
        xytext=(datetime.strptime("2025-01-15", "%Y-%m-%d"), 1.9),
        fontsize=9, color="#1f77b4",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f0fe",
                  edgecolor="#1f77b4", linewidth=1),
        arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=1.2)
    )

    fig.text(
        0.5, 0.005,
        "Source: BlackRock press releases, Ondo Finance reporting, Backed Assets Final Terms, RWA.xyz, CoinGecko. "
        "Intermediate values interpolated for visualisation. The Backed line is product-suite AUM, not bIB01-specific.",
        ha="center", fontsize=8, style="italic", color="#888"
    )

    plt.tight_layout(rect=(0, 0.02, 1, 1))
    plt.savefig(output_png, dpi=160, bbox_inches="tight", facecolor="white")
    plt.savefig(output_svg, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {output_png}")
    print(f"Saved: {output_svg}")


if __name__ == "__main__":
    import os as _os; _os.chdir(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    import os
    os.makedirs("05_figures", exist_ok=True)
    plot_aum_timeseries()
