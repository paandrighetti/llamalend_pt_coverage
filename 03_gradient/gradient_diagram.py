"""
RWA HQLA Framework: Gradient L0 to L3 Visualisation
Staircase diagram for Section 6 of the publication article.

Output: 05_figures/gradient_staircase.png (high-res for article)
        05_figures/gradient_staircase.svg (vector for repo)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def draw_gradient_diagram(output_png: str = "./05_figures/gradient_staircase.png",
                          output_svg: str = "./05_figures/gradient_staircase.svg"):
    """
    Render a 4-level staircase showing the L0 to L3 gradient of HQLA eligibility
    for tokenised treasuries. Each level includes:
      - Title and timeline
      - Required structural change
      - Resulting eligibility
      - Operational status indicator (current / target / hypothetical)
    """
    fig, ax = plt.subplots(figsize=(15, 10))

    # Background
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Define levels with x_start, y_bottom, width, height
    levels = [
        {
            "id": "L0",
            "x": 0.5,
            "y": 0.3,
            "w": 3.5,
            "h": 2.2,
            "title": "L0: Status quo (May 2026)",
            "color": "#d62728",       # red
            "alpha": 0.20,
            "bullets": [
                "All three products fail Block A",
                "Not HQLA, not ECB collateral",
                "BUIDL, OUSG, bIB01 today",
            ],
            "status": "CURRENT STATE",
            "timeline": "Today"
        },
        {
            "id": "L1",
            "x": 4.0,
            "y": 2.5,
            "w": 3.8,
            "h": 2.6,
            "title": "L1: UCITS MMF restructuration",
            "color": "#ff7f0e",       # orange
            "alpha": 0.25,
            "bullets": [
                "Public Debt CNAV under MMFR 2017/1131",
                "Lux (CSSF) or Irl (CBI) authorisation",
                "HQLA Level 1/2A via Art. 15 look-through",
                "Precedent: Franklin BENJI (1940 Act US)",
            ],
            "status": "ACHIEVABLE",
            "timeline": "12-30 months"
        },
        {
            "id": "L2",
            "x": 7.8,
            "y": 5.1,
            "w": 4.0,
            "h": 2.8,
            "title": "L2: DLT via authorised CSD",
            "color": "#2ca02c",       # green
            "alpha": 0.25,
            "bullets": [
                "DLT-PR Regulation (EU) 2022/858",
                "Via CSD Prague, 21X AG, or 360X AG",
                "ECB collateral eligibility OPERATIONAL",
                "since 30 March 2026 (ECB decision 27 Jan)",
            ],
            "status": "OPERATIONAL FRAMEWORK",
            "timeline": "6-24 months for BUIDL"
        },
        {
            "id": "L3",
            "x": 11.8,
            "y": 7.9,
            "w": 4.0,
            "h": 2.8,
            "title": "L3: Native sovereign DLT",
            "color": "#1f77b4",       # blue
            "alpha": 0.25,
            "bullets": [
                "Treasury issues directly on DLT-SS",
                "ECB Pontes pilot Q3 2026",
                "ECB Appia long-term integrated",
                "Direct Level 1 HQLA",
            ],
            "status": "PROSPECTIVE",
            "timeline": "5-7 years"
        }
    ]

    # Draw level boxes
    for lev in levels:
        # Main filled box
        box = FancyBboxPatch(
            (lev["x"], lev["y"]),
            lev["w"], lev["h"],
            boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=lev["color"],
            alpha=lev["alpha"],
            edgecolor=lev["color"],
            linewidth=2.5
        )
        ax.add_patch(box)

        # Header bar (taller to accommodate title + timeline on separate lines)
        header_h = 0.65
        header = patches.Rectangle(
            (lev["x"], lev["y"] + lev["h"] - header_h),
            lev["w"], header_h,
            facecolor=lev["color"],
            alpha=0.6,
            edgecolor=lev["color"]
        )
        ax.add_patch(header)

        # Title (white on header: top line)
        ax.text(
            lev["x"] + 0.15, lev["y"] + lev["h"] - 0.22,
            lev["title"],
            fontsize=11, fontweight="bold",
            color="white", va="center", ha="left"
        )

        # Timeline (white on header: bottom line, smaller font)
        ax.text(
            lev["x"] + 0.15, lev["y"] + lev["h"] - 0.5,
            f"Timeline: {lev['timeline']}",
            fontsize=8.5, fontstyle="italic",
            color="white", va="center", ha="left"
        )

        # Bullets (start below the taller header)
        for i, bullet in enumerate(lev["bullets"]):
            ax.text(
                lev["x"] + 0.2,
                lev["y"] + lev["h"] - 0.95 - i * 0.32,
                f"• {bullet}",
                fontsize=9.5, color="#333",
                va="center", ha="left"
            )

        # Status indicator (bottom)
        ax.text(
            lev["x"] + lev["w"] / 2,
            lev["y"] + 0.15,
            lev["status"],
            fontsize=8.5, fontweight="bold",
            color=lev["color"],
            va="center", ha="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=lev["color"], linewidth=1)
        )

    # Draw connecting arrows between levels
    arrow_pairs = [
        (levels[0], levels[1]),
        (levels[1], levels[2]),
        (levels[2], levels[3])
    ]

    for src, dst in arrow_pairs:
        arrow = FancyArrowPatch(
            (src["x"] + src["w"], src["y"] + src["h"] / 2),
            (dst["x"], dst["y"] + dst["h"] / 2),
            arrowstyle="->,head_width=0.4,head_length=0.6",
            mutation_scale=20,
            color="#555",
            linewidth=2,
            linestyle="-"
        )
        ax.add_patch(arrow)

    # Y-axis label "HQLA eligibility distance"
    ax.annotate(
        "",
        xy=(-0.3, 11), xytext=(-0.3, 0.3),
        arrowprops=dict(arrowstyle="<-", color="#888", lw=1.5),
        annotation_clip=False
    )
    ax.text(
        -0.55, 5.65,
        "Distance to HQLA Level 1 eligibility",
        fontsize=10, fontstyle="italic", color="#666",
        rotation=90, ha="center", va="center"
    )

    # X-axis label "Time / Regulatory maturity"
    ax.annotate(
        "",
        xy=(15.7, -0.2), xytext=(0.5, -0.2),
        arrowprops=dict(arrowstyle="->", color="#888", lw=1.5),
        annotation_clip=False
    )
    ax.text(
        8, -0.55,
        "Regulatory and structural evolution →",
        fontsize=10, fontstyle="italic", color="#666",
        ha="center", va="center"
    )

    # Title
    fig.suptitle(
        "The Gradient of HQLA Eligibility for Tokenised Treasuries",
        fontsize=14, fontweight="bold", y=0.97
    )
    ax.text(
        8, 11.5,
        "From current state (L0) to native sovereign DLT issuance (L3), May 2026 snapshot",
        fontsize=10.5, style="italic", color="#666",
        ha="center", va="center"
    )

    # Footnote
    ax.text(
        0.5, -0.95,
        "Source: BCBS 238 ; DR 2015/61 ; Reg (EU) 2017/1131 (MMFR) ; Reg (EU) 2022/858 (DLT-PR) ; "
        "ECB Press Release 27 January 2026 ; ECB Pontes/Appia 1 July 2025.",
        fontsize=8, color="#888", ha="left", va="center",
        style="italic"
    )

    plt.tight_layout()
    plt.savefig(output_png, dpi=160, bbox_inches="tight", facecolor="white")
    plt.savefig(output_svg, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved : {output_png}")
    print(f"Saved : {output_svg}")


if __name__ == "__main__":
    import os as _os; _os.chdir(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    import os
    os.makedirs("./05_figures", exist_ok=True)
    draw_gradient_diagram()
