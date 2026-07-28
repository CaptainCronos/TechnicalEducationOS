#!/usr/bin/env python3
"""Validate TEOS JSON Schemas and the repository records they govern."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIRECTORY = REPOSITORY_ROOT / "schemas"
SCHEMA_RECORDS = {
    "academic-calendar.schema.json": (
        "institutions/*/calendars/*.json",
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
            validator.validate(_load_json(record_path))
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

