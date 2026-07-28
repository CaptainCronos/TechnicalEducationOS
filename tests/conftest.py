"""Shared deterministic fixtures for TEOS system tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Callable

import pytest

from teos import BuildConfig
from teos.records import load_curriculum, load_json

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = REPOSITORY_ROOT / "examples" / "reference_curriculum"
SCHEMA_ROOT = REPOSITORY_ROOT / "schemas"
COMMUNITY_PROFILE = (
    REFERENCE_ROOT / "institutions" / "community-college" / "institution.json"
)
COMMUNITY_CALENDAR = (
    REFERENCE_ROOT
    / "institutions"
    / "community-college"
    / "calendars"
    / "fall-2026-semester.json"
)


@pytest.fixture(scope="session")
def reference_root() -> Path:
    return REFERENCE_ROOT


@pytest.fixture(scope="session")
def schema_root() -> Path:
    return SCHEMA_ROOT


@pytest.fixture(scope="session")
def reference_curriculum() -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]
]:
    return load_curriculum(REFERENCE_ROOT / "curriculum")


@pytest.fixture(scope="session")
def community_profile() -> dict[str, Any]:
    return load_json(COMMUNITY_PROFILE)


@pytest.fixture(scope="session")
def community_calendar() -> dict[str, Any]:
    return load_json(COMMUNITY_CALENDAR)


@pytest.fixture
def build_config() -> Callable[..., BuildConfig]:
    def factory(output: Path, **changes: object) -> BuildConfig:
        values: dict[str, object] = {
            "repository": REFERENCE_ROOT,
            "schema_directory": SCHEMA_ROOT,
            "institution_id": "north-valley-community-college",
            "calendar_id": "fall-2026-semester",
            "meeting_pattern_id": "monday-wednesday-evening",
            "locale": "en-US",
            "theme": "institution-branded",
            "output_directory": output,
        }
        values.update(changes)
        return BuildConfig(**values)  # type: ignore[arg-type]

    return factory


@pytest.fixture
def mutable_reference(
    tmp_path: Path,
) -> Callable[[str], Path]:
    def factory(name: str = "reference") -> Path:
        destination = tmp_path / name
        shutil.copytree(REFERENCE_ROOT, destination)
        return destination

    return factory


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

