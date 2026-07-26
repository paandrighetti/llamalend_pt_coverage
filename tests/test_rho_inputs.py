from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from estimate_rho import load
from fetch_rho_inputs import USDE


def test_fetcher_uses_unstaked_usde_contract() -> None:
    assert USDE.lower() == "0x4c9edd5852cd905f086c759e8383e09bff1e68b3"


def test_rho_loader_rejects_yield_accreting_share_price(tmp_path: Path) -> None:
    path = tmp_path / "bad_series.csv"
    pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=30, freq="D"),
            "usde_price": [1.20] * 30,
            "capacity_usd": [10_000_000.0] * 30,
        }
    ).to_csv(path, index=False)

    with pytest.raises(SystemExit, match="unstaked USDe spot"):
        load(str(path))
