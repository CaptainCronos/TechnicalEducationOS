#!/usr/bin/env python3
"""Validate TEOS JSON Schemas and the repository records they govern."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIRECTORY = REPOSITORY_ROOT / "schemas"
SCHEMA_RECORDS = {
    "academic-calendar.schema.json": (
        "institutions/*/calendars/*.json",
    ),
    "canonical-lesson.schema.json": (
        "curriculum/courses/*/lessons/*.yaml",
    ),
    "course.schema.json": ("curriculum/courses/*/course.json",),
    "institution.schema.json": ("institutions/*/institution.json",),
    "instructional-unit.schema.json": (
        "curriculum/courses/*/units/*.json",
    ),
    "session-plan.schema.json": ("curriculum/courses/*/sessions.json",),
    "week.schema.json": ("curriculum/courses/*/weeks/*.json",),
}


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _load_record(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        if path.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(stream)
        return json.load(stream)


def _walk_ids(value: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            found.append((value["id"], f"{path}.id"))
        for key, child in value.items():
            found.extend(_walk_ids(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_walk_ids(child, f"{path}[{index}]"))
    return found


def _canonical_lesson_ids(record: dict[str, Any], section: str) -> set[str]:
    return {item["id"] for item in record[section]}


def _validate_canonical_lesson(record: dict[str, Any], path: Path) -> None:
    id_locations: dict[str, str] = {}
    for entity_id, location in _walk_ids(record):
        if entity_id in id_locations:
            raise ValidationError(
                f"{path}: duplicate ID {entity_id!r} at {location}; "
                f"first declared at {id_locations[entity_id]}"
            )
        id_locations[entity_id] = location

    target_ids = {
        "source_ref": _canonical_lesson_ids(record, "sources"),
        "source_refs": _canonical_lesson_ids(record, "sources"),
        "objective_ids": _canonical_lesson_ids(record, "objectives"),
        "standard_ids": _canonical_lesson_ids(record, "standards"),
        "material_ids": _canonical_lesson_ids(record, "materials"),
        "resource_ids": _canonical_lesson_ids(record, "resources"),
        "terminology_ids": _canonical_lesson_ids(record, "terminology"),
        "safety_requirement_ids": _canonical_lesson_ids(
            record, "safety_requirements"
        ),
        "activity_ids": _canonical_lesson_ids(record, "activities"),
        "warm_up_activity_id": _canonical_lesson_ids(record, "activities"),
        "essential_question_ids": _canonical_lesson_ids(
            record, "essential_questions"
        ),
        "closing_assessment_ids": _canonical_lesson_ids(record, "assessments"),
    }

    def check_references(value: Any, location: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in target_ids:
                    references = child if isinstance(child, list) else [child]
                    missing = sorted(set(references) - target_ids[key])
                    if missing:
                        raise ValidationError(
                            f"{path}: unresolved {key} at {location}.{key}: "
                            f"{', '.join(missing)}"
                        )
                check_references(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_references(child, f"{location}[{index}]")

    check_references(record)

    activities = {item["id"]: item for item in record["activities"]}
    scheduled_activity_ids: list[str] = []
    segment_total = 0
    for segment in record["scheduling"]["segments"]:
        activity_total = sum(
            activities[activity_id]["duration_minutes"]
            for activity_id in segment["activity_ids"]
        )
        if activity_total != segment["duration_minutes"]:
            raise ValidationError(
                f"{path}: segment {segment['id']} declares "
                f"{segment['duration_minutes']} minutes but its activities total "
                f"{activity_total}"
            )
        segment_total += segment["duration_minutes"]
        scheduled_activity_ids.extend(segment["activity_ids"])

    duration = record["scheduling"]["duration_minutes"]
    if segment_total != duration:
        raise ValidationError(
            f"{path}: lesson declares {duration} minutes but segments total "
            f"{segment_total}"
        )
    if len(scheduled_activity_ids) != len(set(scheduled_activity_ids)):
        raise ValidationError(f"{path}: an activity is scheduled more than once")
    missing_activities = sorted(set(activities) - set(scheduled_activity_ids))
    if missing_activities:
        raise ValidationError(
            f"{path}: unscheduled activities: {', '.join(missing_activities)}"
        )

    sequences = [activity["sequence"] for activity in record["activities"]]
    if sorted(sequences) != list(range(1, len(sequences) + 1)):
        raise ValidationError(
            f"{path}: activity sequence values must be contiguous and unique"
        )

    if record["lesson"]["lifecycle"]["status"] == "approved":
        unavailable = [
            source["id"]
            for source in record["sources"]
            if source["availability"] == "not_available"
        ]
        unresolved: list[str] = []
        for value, location in _walk_origins(record):
            if value.get("verification") != "verified":
                unresolved.append(location)
        if unavailable or unresolved:
            details = []
            if unavailable:
                details.append(f"unavailable sources: {', '.join(unavailable)}")
            if unresolved:
                details.append(
                    f"unverified origins: {', '.join(unresolved[:5])}"
                )
            raise ValidationError(
                f"{path}: approved lesson has unresolved review state "
                f"({'; '.join(details)})"
            )


def _walk_origins(value: Any, path: str = "$") -> list[tuple[dict[str, Any], str]]:
    found: list[tuple[dict[str, Any], str]] = []
    if isinstance(value, dict):
        origin = value.get("origin")
        if isinstance(origin, dict):
            found.append((origin, f"{path}.origin"))
        for key, child in value.items():
            found.extend(_walk_origins(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_walk_origins(child, f"{path}[{index}]"))
    return found


def validate_schemas() -> tuple[int, int]:
    schema_count = 0
    record_count = 0

    for schema_name, patterns in SCHEMA_RECORDS.items():
        schema_path = SCHEMA_DIRECTORY / schema_name
        schema = _load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        schema_count += 1

        record_paths = sorted(
            {
                path
                for pattern in patterns
                for path in REPOSITORY_ROOT.glob(pattern)
            }
        )
        if not record_paths:
            raise ValidationError(f"{schema_name} has no repository records")

        for record_path in record_paths:
            record = _load_record(record_path)
            validator.validate(record)
            if schema_name == "canonical-lesson.schema.json":
                _validate_canonical_lesson(record, record_path)
            record_count += 1

    return schema_count, record_count


def main() -> int:
    try:
        schema_count, record_count = validate_schemas()
    except (OSError, json.JSONDecodeError, SchemaError, ValidationError) as exc:
        print(f"Schema validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Schema validation passed: {schema_count} schemas and "
        f"{record_count} repository records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
