"""
RWA HQLA Framework: Internal Haircut Calculator
Version 1.0: 2026-05-11

Implements the internal haircut framework proposed in 04_implications/bank_implications.md.
Computes a cumulative internal management haircut for tokenised RWA exposures,
decomposed into four risk components, with product-specific parameters.

This is an analytical tool, not regulatory guidance. All parameters should be
re-calibrated by each institution's ALM committee.

Usage:
    python haircut_calculator.py
    # or import as module:
    from haircut_calculator import compute_haircut, PRODUCT_PROFILES
"""

from dataclasses import dataclass, field
from typing import Literal


# ============================================================================
# Risk component definitions
# ============================================================================

@dataclass
class HaircutComponents:
    """
    Four risk components of the internal haircut framework.
    Each value is a fraction (e.g. 0.10 = 10%).
    """
    custody_chain: float        # 5-10%: intermediaries between token and Treasury
    settlement_finality: float  # 10-15%: no SFD coverage under current chains
    contract_upgradeability: float  # 3-5%: admin keys / pause function exposure
    issuer_concentration: float     # 5-10%: single issuer / chain dominance

    def total_additive(self) -> float:
        """Simple additive aggregation of haircut components."""
        return (self.custody_chain + self.settlement_finality
                + self.contract_upgradeability + self.issuer_concentration)

    def total_multiplicative(self) -> float:
        """
        Multiplicative aggregation: 1 - product of (1 - component).
        NOTE: for non-negative components this is LOWER than (or equal to) the
        additive sum, i.e. LESS conservative: 1 - prod(1-h_i) <= sum(h_i).
        It is used as the base because it models compounding of residual value
        and cannot exceed 100%. The additive sum is reported alongside as the
        conservative upper bound.
        """
        residual = 1.0
        for c in (self.custody_chain, self.settlement_finality,
                  self.contract_upgradeability, self.issuer_concentration):
            residual *= (1 - c)
        return 1 - residual


# ============================================================================
# Product-specific risk profiles
# ============================================================================
# Parameters derived from the eligibility matrix (01_framework).
# Custody chain layers: BUIDL=2, OUSG=3, bIB01=3
# All three fail settlement finality (no SFD), have upgradeable contracts,
# and exhibit issuer/chain concentration.
# ============================================================================

PRODUCT_PROFILES: dict[str, HaircutComponents] = {
    "BUIDL": HaircutComponents(
        custody_chain=0.06,           # 2 custody layers (BNY Mellon -> BVI fund)
        settlement_finality=0.12,     # Ethereum-dominant, no SFD/DLT-PR
        contract_upgradeability=0.04, # Securitize admin multisig
        issuer_concentration=0.08,    # BlackRock single manager, 95% Ethereum
    ),
    "OUSG": HaircutComponents(
        custody_chain=0.09,           # 3 custody layers (fund-of-funds)
        settlement_finality=0.12,     # same chain risk profile
        contract_upgradeability=0.04, # upgradeable contracts
        issuer_concentration=0.07,    # Ondo manager + indirect BlackRock via BUIDL
    ),
    "bIB01": HaircutComponents(
        custody_chain=0.09,           # 3 custody layers (State Street -> Maerki/InCore -> JE Ltd)
        settlement_finality=0.13,     # same + Swiss DLT but no SFD
        contract_upgradeability=0.05, # explicit updating function in T&C
        issuer_concentration=0.10,    # unrated Jersey SPV + Kraken parent + creditor cascade
    ),
}


# ============================================================================
# Haircut computation
# ============================================================================

def compute_haircut(
    product: str,
    method: Literal["additive", "multiplicative"] = "multiplicative",
    stress_overlay: float = 0.0,
) -> dict:
    """
    Compute the internal haircut for a given product.

    Args:
        product: one of PRODUCT_PROFILES keys (BUIDL, OUSG, bIB01)
        method: aggregation method for components
        stress_overlay: additional emergency haircut (e.g. 0.15 if a smart
                        contract pause or oracle failure is observed)

    Returns:
        dict with component breakdown, base haircut, stress overlay, and
        effective haircut applied to book value.
    """
    if product not in PRODUCT_PROFILES:
        raise ValueError(f"Unknown product: {product}. "
                         f"Available: {list(PRODUCT_PROFILES.keys())}")

    components = PRODUCT_PROFILES[product]
    base = (components.total_multiplicative() if method == "multiplicative"
            else components.total_additive())

    # Stress overlay is additive on top of base, capped at 100%
    effective = min(base + stress_overlay, 1.0)

    return {
        "product": product,
        "haircut_additive_pct": round(components.total_additive() * 100, 1),
        "method": method,
        "components": {
            "custody_chain": components.custody_chain,
            "settlement_finality": components.settlement_finality,
            "contract_upgradeability": components.contract_upgradeability,
            "issuer_concentration": components.issuer_concentration,
        },
        "base_haircut": round(base, 4),
        "stress_overlay": stress_overlay,
        "effective_haircut": round(effective, 4),
        "value_retained_per_100": round((1 - effective) * 100, 2),
    }


def apply_haircut_to_position(
    product: str,
    book_value_usd: float,
    method: Literal["additive", "multiplicative"] = "multiplicative",
    stress_overlay: float = 0.0,
) -> dict:
    """
    Apply the computed haircut to a specific position size.

    Args:
        product: product identifier
        book_value_usd: position book value in USD
        method: aggregation method
        stress_overlay: emergency overlay

    Returns:
        dict with book value, haircut, and internal liquidity value.
    """
    hc = compute_haircut(product, method, stress_overlay)
    internal_value = book_value_usd * (1 - hc["effective_haircut"])
    return {
        **hc,
        "book_value_usd": book_value_usd,
        "internal_liquidity_value_usd": round(internal_value, 2),
        "haircut_amount_usd": round(book_value_usd - internal_value, 2),
    }


# ============================================================================
# Demonstration
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RWA HQLA Framework: Internal Haircut Calculator")
    print("=" * 70)
    print("\nBase haircuts by product (multiplicative aggregation):\n")

    for product in PRODUCT_PROFILES:
        hc = compute_haircut(product, method="multiplicative")
        print(f"  {product:8s} : {hc['base_haircut']*100:5.1f}% haircut "
              f"-> ${hc['value_retained_per_100']:.2f} retained per $100")

    print("\nComponent breakdown:\n")
    for product in PRODUCT_PROFILES:
        c = PRODUCT_PROFILES[product]
        print(f"  {product}:")
        print(f"    Custody chain         : {c.custody_chain*100:4.1f}%")
        print(f"    Settlement finality   : {c.settlement_finality*100:4.1f}%")
        print(f"    Contract upgradeability: {c.contract_upgradeability*100:4.1f}%")
        print(f"    Issuer concentration  : {c.issuer_concentration*100:4.1f}%")
        print()

    print("Example: $50M BUIDL position under normal conditions:\n")
    result = apply_haircut_to_position("BUIDL", 50_000_000)
    print(f"  Book value          : ${result['book_value_usd']:,.0f}")
    print(f"  Effective haircut   : {result['effective_haircut']*100:.1f}%")
    print(f"  Internal liq. value : ${result['internal_liquidity_value_usd']:,.0f}")
    print(f"  Haircut amount      : ${result['haircut_amount_usd']:,.0f}")

    print("\nExample: same position with smart-contract-pause stress overlay (+15%):\n")
    result_stress = apply_haircut_to_position("BUIDL", 50_000_000, stress_overlay=0.15)
    print(f"  Effective haircut   : {result_stress['effective_haircut']*100:.1f}%")
    print(f"  Internal liq. value : ${result_stress['internal_liquidity_value_usd']:,.0f}")

    print("\n" + "=" * 70)
    print("These are analytical parameters, not regulatory haircuts.")
    print("Re-calibrate per institution ALM committee judgement.")
    print("=" * 70)
