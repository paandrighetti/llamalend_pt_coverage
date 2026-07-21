"""
RWA HQLA Framework: Scoring Heatmap Generator
Version 1.1: 2026-06-17

Reads eligibility_matrix.json and produces the heatmap PNG used in
Section 4 (Block-by-block verdict) of the article.

v1.1 changes vs v1.0:
- bIB01 C.2 (Active and sizable market) downgraded from Fail to Conditional
  reflecting the measured 96% secondary share ratio (Dune M6 snapshot 2026-06-17).
- Justification: empirical ratio nuances binary Fail; absolute 0.43 tx/day still
  insufficient for HQLA but the ratio deserves explicit acknowledgement.

Output: 05_figures/scoring_heatmap.png
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import os


VERDICT_TO_VALUE = {"Pass": 3, "Conditional": 2, "Fail": 1, "N/A": 0}
VERDICT_TO_LABEL = {"Pass": "P", "Conditional": "C", "Fail": "F", "N/A": "-"}
COLORS = ["#e8e8e8", "#d62728", "#ff9933", "#2ca02c"]


def normalize_verdict(verdict_raw: str) -> str:
    """Map explicitly documented descriptive Block-D values to the scale.

    Unknown values raise instead of being silently converted to ``Fail``.
    """
    if verdict_raw in VERDICT_TO_VALUE:
        return verdict_raw
    aliases = {
        "0 layers": "Pass",
        "1 layer": "Pass",
        "2 layers": "Conditional",
        "3 layers": "Fail",
        "4 layers": "Fail",
        "5 layers": "Fail",
        "standard fund mechanics": "Pass",
        "standard limitation": "Conditional",
        "not assessed (implicit non-eligible)": "N/A",
        "fail (explicit)": "Fail",
        "yes": "Fail",
        "true": "Fail",
        "no": "Pass",
        "false": "Pass",
    }
    key = verdict_raw.lower().strip()
    if key in aliases:
        return aliases[key]
    raise ValueError(f"Unknown verdict value: {verdict_raw!r}")



def load_matrix(path):
    with open(path, "r") as f:
        return json.load(f)


def extract_scoring_data(matrix):
    products = matrix["framework"]["products_assessed"]
    rows, values, texts = [], [], []
    for block_key in ["block_A_eligibility_category", "block_B_operational_requirements",
                       "block_C_market_criteria", "block_D_wrapper_friction"]:
        block = matrix["scoring"][block_key]
        for criterion in block["criteria"]:
            crit_id = criterion["id"]
            crit_name = criterion["name"]
            short_name = crit_name if len(crit_name) <= 55 else crit_name[:52] + "..."
            rows.append(f"{crit_id}  {short_name}")
            value_row, text_row = [], []
            for product in products:
                raw_verdict = criterion["scoring"][product]["verdict"]
                normalized = normalize_verdict(raw_verdict)
                value_row.append(VERDICT_TO_VALUE[normalized])
                text_row.append(VERDICT_TO_LABEL[normalized])
            values.append(value_row)
            texts.append(text_row)
    return rows, products, np.array(values), np.array(texts)


def plot_heatmap(rows, cols, values, texts, output_path):
    n_rows, n_cols = len(rows), len(cols)
    fig_height = max(8, n_rows * 0.32)
    fig, ax = plt.subplots(figsize=(11, fig_height))
    cmap = ListedColormap(COLORS)
    ax.imshow(values, cmap=cmap, aspect="auto", vmin=0, vmax=3)

    for i in range(n_rows):
        for j in range(n_cols):
            text_color = "white" if values[i, j] in (1, 3) else "black"
            ax.text(j, i, texts[i, j], ha="center", va="center",
                    color=text_color, fontsize=11, fontweight="bold")

    ax.set_xticks(np.arange(n_cols))
    ax.set_xticklabels(cols, fontsize=11, fontweight="bold")
    ax.set_yticks(np.arange(n_rows))
    ax.set_yticklabels(rows, fontsize=9)
    ax.set_xticks(np.arange(n_cols + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n_rows + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=0)

    last_block, boundaries = None, []
    for idx, label in enumerate(rows):
        prefix = label.split(".")[0]
        if last_block is not None and prefix != last_block:
            boundaries.append(idx - 0.5)
        last_block = prefix
    for b in boundaries:
        ax.axhline(y=b, color="black", linewidth=1.5)

    legend_elements = [
        Patch(facecolor=COLORS[3], label="Pass"),
        Patch(facecolor=COLORS[2], label="Conditional"),
        Patch(facecolor=COLORS[1], label="Fail"),
        Patch(facecolor=COLORS[0], label="N/A"),
    ]
    ax.legend(handles=legend_elements, loc="upper center",
              bbox_to_anchor=(0.5, -0.04), ncol=4, frameon=False, fontsize=10)
    ax.set_title(
        "RWA HQLA Eligibility: Scoring Matrix\n"
        "24 criteria × 3 products (Basel III LCR, snapshot 2026-06-17)",
        fontsize=12, pad=15
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {output_path}")


def print_summary(rows, cols, texts):
    print("\n" + "=" * 70)
    print("Scoring summary by product (verdict counts):")
    print("=" * 70)
    for col_idx, product in enumerate(cols):
        counts = {"P": 0, "C": 0, "F": 0, "-": 0}
        for row_idx in range(len(rows)):
            counts[texts[row_idx, col_idx]] += 1
        print(f"  {product:8s} : Pass={counts['P']}, Conditional={counts['C']}, "
              f"Fail={counts['F']}, N/A={counts['-']}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    matrix_path = os.path.join(repo_dir, "01_framework", "eligibility_matrix.json")
    output_path = os.path.join(repo_dir, "05_figures", "scoring_heatmap.png")
    matrix = load_matrix(matrix_path)
    rows, cols, values, texts = extract_scoring_data(matrix)
    print_summary(rows, cols, texts)
    plot_heatmap(rows, cols, values, texts, output_path)
