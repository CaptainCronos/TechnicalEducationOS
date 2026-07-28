from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.regression


def test_reference_dataset_matches_reviewed_fingerprints(
    reference_root: Path,
) -> None:
    snapshot_path = (
        Path(__file__).resolve().parents[1]
        / "snapshots"
        / "reference_dataset.json"
    )
    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    actual = {
        path.relative_to(reference_root).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(reference_root.rglob("*"))
        if path.is_file() and path.name != "README.md"
    }
    assert actual == expected, (
        "reference curriculum changed; review the semantic change and update "
        "tests/snapshots/reference_dataset.json intentionally"
    )

