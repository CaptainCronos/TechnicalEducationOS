from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from jsonschema.exceptions import ValidationError

from scripts.validate_schemas import _validate_canonical_lesson, validate_schemas

pytestmark = pytest.mark.unit

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LESSON_PATH = (
    REPOSITORY_ROOT
    / "curriculum"
    / "courses"
    / "dsl204"
    / "lessons"
    / "week-04-day-01.yaml"
)


@pytest.fixture
def canonical_lesson() -> dict:
    with LESSON_PATH.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def test_repository_canonical_lesson_passes_schema_and_semantic_validation() -> None:
    schema_count, record_count = validate_schemas()
    assert schema_count >= 7
    assert record_count >= 7


def test_canonical_lesson_cannot_be_approved_with_review_gaps(
    canonical_lesson: dict,
) -> None:
    record = deepcopy(canonical_lesson)
    record["lesson"]["lifecycle"]["status"] = "approved"

    with pytest.raises(ValidationError, match="approved lesson has unresolved"):
        _validate_canonical_lesson(record, LESSON_PATH)


def test_canonical_lesson_rejects_unresolved_references(
    canonical_lesson: dict,
) -> None:
    record = deepcopy(canonical_lesson)
    record["instructional_brief"]["warm_up_activity_id"] = "activity.missing"

    with pytest.raises(ValidationError, match="unresolved warm_up_activity_id"):
        _validate_canonical_lesson(record, LESSON_PATH)


def test_canonical_lesson_reconciles_activity_segment_and_lesson_time(
    canonical_lesson: dict,
) -> None:
    record = deepcopy(canonical_lesson)
    record["activities"][0]["duration_minutes"] += 1

    with pytest.raises(ValidationError, match="its activities total"):
        _validate_canonical_lesson(record, LESSON_PATH)
