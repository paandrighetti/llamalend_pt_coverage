from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from coverage_model import DepthCurve
from run_analysis import validate_and_prepare_depth_frame, validate_publication_manifest


@pytest.mark.parametrize(
    ("sizes", "impacts"),
    [
        ([1.0, np.nan], [0.0, 0.1]),
        ([1.0, np.inf], [0.0, 0.1]),
        ([1.0, 2.0], [0.0, np.nan]),
        ([1.0, 2.0], [0.0, np.inf]),
        ([1.0, -2.0], [0.0, 0.1]),
        ([1.0, 2.0], [0.0, -0.1]),
        ([1.0, 2.0], [0.0, 1.0]),
    ],
)
def test_depth_curve_rejects_invalid_numbers(sizes, impacts) -> None:
    with pytest.raises(ValueError):
        DepthCurve(sizes, impacts)


def test_small_monotonic_adjustment_is_reported() -> None:
    frame = pd.DataFrame({
        "size_usd": [1.0, 2.0, 3.0],
        "impact": [0.0010, 0.0009, 0.0012],
    })
    corrected, adjustment = validate_and_prepare_depth_frame(frame, 2.0)
    assert adjustment == pytest.approx(0.0001)
    assert np.all(np.diff(corrected["impact"]) >= 0)


def test_large_monotonic_adjustment_is_rejected() -> None:
    frame = pd.DataFrame({
        "size_usd": [1.0, 2.0, 3.0],
        "impact": [0.0100, 0.0010, 0.0120],
    })
    with pytest.raises(ValueError):
        validate_and_prepare_depth_frame(frame, 5.0)


def test_publication_manifest_hash_is_verified(tmp_path: Path) -> None:
    csv_path = tmp_path / "curve.csv"
    csv_path.write_text("size_usd,impact\n1,0\n2,0.01\n", encoding="utf-8")
    manifest = {
        "publication_ready": True,
        "sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    }
    csv_path.with_suffix(".manifest.json").write_text(json.dumps(manifest))
    assert validate_publication_manifest(csv_path, False) is not None
