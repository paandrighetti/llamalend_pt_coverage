"""
Synthetic PT depth-curve generator.

Used ONLY to exercise the analysis pipeline end-to-end without network access.
The shape (convex, increasing price impact with size) is qualitatively realistic
for a concentrated-liquidity AMM, but the NUMBERS ARE NOT REAL. Never use a
synthetic curve in the published analysis -- replace it with a real curve from
pendle_depth.py.
"""
from __future__ import annotations

import numpy as np

from coverage_model import DepthCurve


def synthetic_depth_curve(
    pool_tvl_usd: float,
    depth_scale_usd: float | None = None,
    exponent: float = 1.5,
    n: int = 60,
    max_fraction_of_tvl: float = 0.5,
) -> DepthCurve:
    """
    Build a synthetic price-impact curve: impact(size) = (size / depth_scale)^exponent.

    depth_scale_usd controls how deep the book is. If omitted it defaults to
    ~0.68 * pool_tvl_usd, which makes a sell of ~7.4% of TVL cost ~2% slippage --
    a deliberately illustrative calibration.
    """
    if depth_scale_usd is None:
        depth_scale_usd = 0.68 * pool_tvl_usd
    sizes = np.linspace(
        pool_tvl_usd * max_fraction_of_tvl / n,
        pool_tvl_usd * max_fraction_of_tvl,
        n,
    )
    impacts = (sizes / depth_scale_usd) ** exponent
    return DepthCurve(sizes=sizes, impacts=impacts)
