"""Create a hash-bearing sidecar manifest for a publication depth curve."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROVENANCE_COLUMNS = {
    "ts_utc", "chain_id", "market", "pt_address", "out_token",
    "api_base", "aggregator_enabled", "spot_price_arg",
}


def canonical_file_sha256(path: Path) -> str:
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def unique_value(frame: pd.DataFrame, column: str) -> object:
    values = frame[column].dropna().unique()
    if len(values) != 1:
        raise ValueError(f"{column} must contain exactly one provenance value")
    value = values[0]
    return value.item() if hasattr(value, "item") else value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--publication-ready", action="store_true")
    parser.add_argument("--collector-version", required=True)
    args = parser.parse_args()

    frame = pd.read_csv(args.csv)
    missing = ({"size_usd", "impact"} | PROVENANCE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")

    sizes = frame["size_usd"].to_numpy(dtype=float)
    impacts = frame["impact"].to_numpy(dtype=float)
    if not np.all(np.isfinite(sizes)) or not np.all(np.isfinite(impacts)):
        raise ValueError("depth curve contains NaN or infinity")
    if np.any(sizes <= 0) or np.any(np.diff(sizes) <= 0):
        raise ValueError("publication sizes must be strictly increasing and positive")
    if np.any((impacts < 0) | (impacts >= 1)) or np.any(np.diff(impacts) < 0):
        raise ValueError("publication impacts must be non-decreasing and in [0, 1)")

    manifest = {
        "schema_version": 1,
        "publication_ready": args.publication_ready,
        "filename": args.csv.name,
        "sha256": canonical_file_sha256(args.csv),
        "rows": int(len(frame)),
        "size_usd_min": float(sizes.min()),
        "size_usd_max": float(sizes.max()),
        "impact_min": float(impacts.min()),
        "impact_max": float(impacts.max()),
        "observed_at": str(unique_value(frame, "ts_utc")),
        "chain_id": int(unique_value(frame, "chain_id")),
        "market": str(unique_value(frame, "market")),
        "pt_address": str(unique_value(frame, "pt_address")),
        "out_token": str(unique_value(frame, "out_token")),
        "api_base": str(unique_value(frame, "api_base")),
        "aggregator_enabled": bool(unique_value(frame, "aggregator_enabled")),
        "spot_price_arg": float(unique_value(frame, "spot_price_arg")),
        "collector_version": args.collector_version,
        "limitations": [
            "The CSV is a dated quote snapshot, not live liquidity.",
            "The quoted route and API schema may change after collection.",
            "Publication use requires the SHA-256 hash to match.",
        ],
    }
    output = args.csv.with_suffix(".manifest.json")
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
