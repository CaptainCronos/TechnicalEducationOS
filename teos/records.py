"""Load and validate authoritative TechnicalEducationOS source records."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SCHEMA_VERSION = "1.0"


class RecordError(ValueError):
    """Raised when a source record is invalid or internally inconsistent."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RecordError(f"record not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RecordError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RecordError(f"record must be a JSON object: {path}")
    return data


def load_course(course_directory: Path) -> dict[str, Any]:
    course = load_json(course_directory / "course.json")
    validate_course(course)
    return course


def load_week(course_directory: Path, week_number: int) -> dict[str, Any]:
    week = load_json(course_directory / "weeks" / f"{week_number:02d}.json")
    return week


def _required(record: dict[str, Any], fields: tuple[str, ...], context: str) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise RecordError(f"{context} is missing: {', '.join(missing)}")


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordError(f"{context} must be a non-empty string")
    return value


def _identifier(value: Any, context: str) -> str:
    identifier = _text(value, context)
    if not ID_PATTERN.fullmatch(identifier):
        raise RecordError(f"{context} has invalid ID {identifier!r}")
    return identifier


def _list(value: Any, context: str, *, allow_empty: bool = True) -> list[Any]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "non-empty " if not allow_empty else ""
        raise RecordError(f"{context} must be a {qualifier}list")
    return value


def _unique_ids(items: list[Any], context: str) -> set[str]:
    identifiers: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise RecordError(f"{context}[{index}] must be an object")
        identifier = _identifier(item.get("id"), f"{context}[{index}].id")
        if identifier in identifiers:
            raise RecordError(f"duplicate ID {identifier!r} in {context}")
        identifiers.add(identifier)
    return identifiers


def _validate_references(
    items: list[Any],
    valid_objectives: set[str],
    context: str,
    *,
    label_field: str = "title",
) -> None:
    for index, item in enumerate(items):
        _required(item, ("id", label_field, "objective_ids"), f"{context}[{index}]")
        _text(item[label_field], f"{context}[{index}].{label_field}")
        references = _list(
            item["objective_ids"],
            f"{context}[{index}].objective_ids",
            allow_empty=False,
        )
        unknown = {
            _identifier(value, f"{context}[{index}].objective_ids")
            for value in references
        } - valid_objectives
        if unknown:
            raise RecordError(
                f"{context} {item['id']!r} references unknown objectives: "
                f"{', '.join(sorted(unknown))}"
            )


def validate_course(course: dict[str, Any]) -> None:
    _required(
        course,
        ("schema_version", "course_id", "title", "competencies"),
        "course",
    )
    if course["schema_version"] != SCHEMA_VERSION:
        raise RecordError(f"unsupported course schema: {course['schema_version']!r}")
    _identifier(course["course_id"], "course.course_id")
    _text(course["title"], "course.title")
    competencies = _list(course["competencies"], "course.competencies", allow_empty=False)
    _unique_ids(competencies, "course.competencies")
    for index, competency in enumerate(competencies):
        _text(competency.get("statement"), f"course.competencies[{index}].statement")


def validate_week(course: dict[str, Any], week: dict[str, Any]) -> None:
    _required(
        week,
        (
            "schema_version",
            "course_id",
            "week_number",
            "title",
            "objectives",
            "lectures",
            "labs",
            "assessments",
        ),
        "week",
    )
    if week["schema_version"] != SCHEMA_VERSION:
        raise RecordError(f"unsupported week schema: {week['schema_version']!r}")
    if week["course_id"] != course["course_id"]:
        raise RecordError("week.course_id does not match course.course_id")
    if not isinstance(week["week_number"], int) or not 1 <= week["week_number"] <= 99:
        raise RecordError("week.week_number must be an integer from 1 through 99")
    _text(week["title"], "week.title")

    objectives = _list(week["objectives"], "week.objectives", allow_empty=False)
    objective_ids = _unique_ids(objectives, "week.objectives")
    competency_ids = {item["id"] for item in course["competencies"]}
    for index, objective in enumerate(objectives):
        _text(objective.get("statement"), f"week.objectives[{index}].statement")
        references = _list(
            objective.get("competency_ids"),
            f"week.objectives[{index}].competency_ids",
            allow_empty=False,
        )
        unknown = {
            _identifier(value, f"week.objectives[{index}].competency_ids")
            for value in references
        } - competency_ids
        if unknown:
            raise RecordError(
                f"objective {objective['id']!r} references unknown competencies: "
                f"{', '.join(sorted(unknown))}"
            )

    for field in ("lectures", "labs", "assessments"):
        items = _list(
            week[field],
            f"week.{field}",
            allow_empty=field != "lectures",
        )
        _unique_ids(items, f"week.{field}")
        _validate_references(items, objective_ids, f"week.{field}")

    for index, lecture in enumerate(week["lectures"]):
        if (
            not isinstance(lecture.get("duration_minutes"), int)
            or lecture["duration_minutes"] < 1
        ):
            raise RecordError(
                f"week.lectures[{index}].duration_minutes must be a positive integer"
            )
        topics = _list(
            lecture.get("topics"),
            f"week.lectures[{index}].topics",
            allow_empty=False,
        )
        for topic_index, topic in enumerate(topics):
            _text(topic, f"week.lectures[{index}].topics[{topic_index}]")

    for index, lab in enumerate(week["labs"]):
        if not isinstance(lab.get("duration_minutes"), int) or lab["duration_minutes"] < 1:
            raise RecordError(
                f"week.labs[{index}].duration_minutes must be a positive integer"
            )
        for field in ("procedure", "deliverables"):
            values = _list(
                lab.get(field),
                f"week.labs[{index}].{field}",
                allow_empty=False,
            )
            for value_index, value in enumerate(values):
                _text(value, f"week.labs[{index}].{field}[{value_index}]")

    for index, assessment in enumerate(week["assessments"]):
        if assessment.get("type") not in {"diagnostic", "formative", "summative"}:
            raise RecordError(
                f"week.assessments[{index}].type must be diagnostic, formative, "
                "or summative"
            )
        questions = _list(
            assessment.get("question_bank"),
            f"week.assessments[{index}].question_bank",
        )
        _unique_ids(questions, f"week.assessments[{index}].question_bank")
        _validate_references(
            questions,
            objective_ids,
            f"week.assessments[{index}].question_bank",
            label_field="prompt",
        )
        for question_index, question in enumerate(questions):
            if question.get("type") not in {
                "multiple_choice",
                "short_answer",
                "performance",
            }:
                raise RecordError(
                    f"week.assessments[{index}].question_bank[{question_index}].type "
                    "is invalid"
                )


def validate_institution(institution: dict[str, Any]) -> None:
    _required(
        institution,
        ("schema_version", "institution_id", "institution_name"),
        "institution",
    )
    if institution["schema_version"] != SCHEMA_VERSION:
        raise RecordError(
            f"unsupported institution schema: {institution['schema_version']!r}"
        )
    _identifier(institution["institution_id"], "institution.institution_id")
    _text(institution["institution_name"], "institution.institution_name")
    fields = institution.get("administrative_fields", {})
    if not isinstance(fields, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in fields.items()
    ):
        raise RecordError("institution.administrative_fields must contain text values")
