"""Load and validate authoritative TechnicalEducationOS source records."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SCHEMA_VERSION = "1.0"
CURRICULUM_SCHEMA_VERSION = "2.0"


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
    """Load a deprecated calendar-first record."""
    week = load_json(course_directory / "weeks" / f"{week_number:02d}.json")
    return week


def load_units(course_directory: Path) -> list[dict[str, Any]]:
    units_directory = course_directory / "units"
    if not units_directory.is_dir():
        raise RecordError(f"units directory not found: {units_directory}")
    units = [load_json(path) for path in sorted(units_directory.glob("*.json"))]
    if not units:
        raise RecordError(f"no instructional units found: {units_directory}")
    return units


def load_sessions(
    course_directory: Path,
    expected_course_id: str | None = None,
) -> list[dict[str, Any]]:
    record = load_json(course_directory / "sessions.json")
    _required(record, ("schema_version", "course_id", "sessions"), "session plan")
    if record["schema_version"] != CURRICULUM_SCHEMA_VERSION:
        raise RecordError(
            f"unsupported session plan schema: {record['schema_version']!r}"
        )
    if expected_course_id is not None and record["course_id"] != expected_course_id:
        raise RecordError("session plan course_id does not match course.course_id")
    return _list(record["sessions"], "session plan.sessions", allow_empty=False)


def load_curriculum(
    course_directory: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    course = load_course(course_directory)
    units = load_units(course_directory)
    sessions = load_sessions(course_directory, course["course_id"])
    validate_curriculum(course, units, sessions)
    return course, units, sessions


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


def _validate_objective_id_list(
    values: Any, valid_objectives: set[str], context: str
) -> None:
    references = _list(values, context, allow_empty=False)
    unknown = {
        _identifier(value, context) for value in references
    } - valid_objectives
    if unknown:
        raise RecordError(
            f"{context} references unknown objectives: "
            f"{', '.join(sorted(unknown))}"
        )


def validate_course(course: dict[str, Any]) -> None:
    if course.get("schema_version") == CURRICULUM_SCHEMA_VERSION:
        _validate_canonical_course(course)
        return
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


def _validate_canonical_course(course: dict[str, Any]) -> None:
    _required(
        course,
        (
            "schema_version",
            "course_id",
            "title",
            "description",
            "contact_hours",
            "standards",
            "competencies",
            "modules",
        ),
        "course",
    )
    _identifier(course["course_id"], "course.course_id")
    _text(course["title"], "course.title")
    _text(course["description"], "course.description")
    if not isinstance(course["contact_hours"], (int, float)) or course["contact_hours"] <= 0:
        raise RecordError("course.contact_hours must be a positive number")
    standards = _list(course["standards"], "course.standards")
    for index, standard in enumerate(standards):
        _text(standard, f"course.standards[{index}]")
    competencies = _list(course["competencies"], "course.competencies", allow_empty=False)
    _unique_ids(competencies, "course.competencies")
    for index, competency in enumerate(competencies):
        _text(competency.get("statement"), f"course.competencies[{index}].statement")
        mappings = _list(
            competency.get("standard_ids", []),
            f"course.competencies[{index}].standard_ids",
        )
        for mapping_index, mapping in enumerate(mappings):
            _text(
                mapping,
                f"course.competencies[{index}].standard_ids[{mapping_index}]",
            )
    modules = _list(course["modules"], "course.modules", allow_empty=False)
    _unique_ids(modules, "course.modules")
    for index, module in enumerate(modules):
        _text(module.get("title"), f"course.modules[{index}].title")
        unit_ids = _list(
            module.get("unit_ids"),
            f"course.modules[{index}].unit_ids",
            allow_empty=False,
        )
        for unit_index, unit_id in enumerate(unit_ids):
            _identifier(unit_id, f"course.modules[{index}].unit_ids[{unit_index}]")


def validate_curriculum(
    course: dict[str, Any],
    units: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
) -> None:
    """Validate the calendar-independent instructional source of truth."""
    validate_course(course)
    if course["schema_version"] != CURRICULUM_SCHEMA_VERSION:
        raise RecordError("canonical curriculum requires course schema version '2.0'")

    competency_ids = {item["id"] for item in course["competencies"]}
    unit_ids = _unique_ids(units, "units")
    declared_unit_ids = {
        unit_id for module in course["modules"] for unit_id in module["unit_ids"]
    }
    if declared_unit_ids != unit_ids:
        missing = unit_ids - declared_unit_ids
        unknown = declared_unit_ids - unit_ids
        details = []
        if missing:
            details.append(f"unassigned units: {', '.join(sorted(missing))}")
        if unknown:
            details.append(f"unknown module unit IDs: {', '.join(sorted(unknown))}")
        raise RecordError("; ".join(details))

    objectives_by_unit: dict[str, set[str]] = {}
    assessments_by_unit: dict[str, dict[str, dict[str, Any]]] = {}
    for index, unit in enumerate(units):
        context = f"units[{index}]"
        _required(
            unit,
            (
                "schema_version",
                "id",
                "course_id",
                "title",
                "competency_ids",
                "objectives",
                "lectures",
                "demonstrations",
                "labs",
                "assessments",
                "required_resources",
                "estimated_minutes",
            ),
            context,
        )
        if unit["schema_version"] != CURRICULUM_SCHEMA_VERSION:
            raise RecordError(f"{context} has unsupported schema version")
        if unit["course_id"] != course["course_id"]:
            raise RecordError(f"{context}.course_id does not match course.course_id")
        _text(unit["title"], f"{context}.title")
        unit_competencies = {
            _identifier(value, f"{context}.competency_ids")
            for value in _list(
                unit["competency_ids"],
                f"{context}.competency_ids",
                allow_empty=False,
            )
        }
        unknown_competencies = unit_competencies - competency_ids
        if unknown_competencies:
            raise RecordError(
                f"unit {unit['id']!r} references unknown competencies: "
                f"{', '.join(sorted(unknown_competencies))}"
            )
        objectives = _list(unit["objectives"], f"{context}.objectives", allow_empty=False)
        objective_ids = _unique_ids(objectives, f"{context}.objectives")
        objectives_by_unit[unit["id"]] = objective_ids
        for objective_index, objective in enumerate(objectives):
            _text(
                objective.get("statement"),
                f"{context}.objectives[{objective_index}].statement",
            )
            references = set(
                _list(
                    objective.get("competency_ids"),
                    f"{context}.objectives[{objective_index}].competency_ids",
                    allow_empty=False,
                )
            )
            if references - unit_competencies:
                raise RecordError(
                    f"{context}.objectives[{objective_index}] references competencies "
                    "outside its unit"
                )
        for field in ("lectures", "demonstrations", "labs", "assessments"):
            items = _list(unit[field], f"{context}.{field}")
            _unique_ids(items, f"{context}.{field}")
            _validate_references(items, objective_ids, f"{context}.{field}")
        assessments_by_unit[unit["id"]] = {
            assessment["id"]: assessment for assessment in unit["assessments"]
        }
        resources = _list(
            unit["required_resources"],
            f"{context}.required_resources",
            allow_empty=False,
        )
        for resource_index, resource in enumerate(resources):
            _text(resource, f"{context}.required_resources[{resource_index}]")
        if (
            not isinstance(unit["estimated_minutes"], int)
            or unit["estimated_minutes"] < 1
        ):
            raise RecordError(f"{context}.estimated_minutes must be positive")

    session_ids: set[int] = set()
    for index, session in enumerate(sessions):
        context = f"sessions[{index}]"
        _required(
            session,
            (
                "id",
                "session_number",
                "unit_id",
                "title",
                "phase",
                "duration_minutes",
                "objective_ids",
            ),
            context,
        )
        _identifier(session["id"], f"{context}.id")
        number = session["session_number"]
        if not isinstance(number, int) or number < 1:
            raise RecordError(f"{context}.session_number must be positive")
        if number in session_ids:
            raise RecordError(f"duplicate session_number {number}")
        session_ids.add(number)
        unit_id = _identifier(session["unit_id"], f"{context}.unit_id")
        if unit_id not in unit_ids:
            raise RecordError(f"{context} references unknown unit {unit_id!r}")
        _text(session["title"], f"{context}.title")
        if session["phase"] not in {
            "theory",
            "demonstration",
            "lab",
            "assessment",
            "integrated",
        }:
            raise RecordError(f"{context}.phase is invalid")
        if not isinstance(session["duration_minutes"], int) or session["duration_minutes"] < 1:
            raise RecordError(f"{context}.duration_minutes must be positive")
        _validate_objective_id_list(
            session["objective_ids"],
            objectives_by_unit[unit_id],
            f"{context}.objective_ids",
        )
        session_objective_ids = set(session["objective_ids"])
        instruction = session.get("instruction", {})
        if not isinstance(instruction, dict):
            raise RecordError(f"{context}.instruction must be an object")
        activities = _list(
            instruction.get("activities", []),
            f"{context}.instruction.activities",
        )
        _unique_ids(activities, f"{context}.instruction.activities")
        for activity_index, activity in enumerate(activities):
            _text(
                activity.get("description"),
                f"{context}.instruction.activities[{activity_index}].description",
            )
            references = set(
                _list(
                    activity.get("objective_ids"),
                    f"{context}.instruction.activities[{activity_index}].objective_ids",
                    allow_empty=False,
                )
            )
            if references - session_objective_ids:
                raise RecordError(
                    f"{context}.instruction.activities[{activity_index}] references "
                    "objectives outside its session"
                )
        assessment_ids = {
            _identifier(value, f"{context}.instruction.assessment_ids")
            for value in _list(
                instruction.get("assessment_ids", []),
                f"{context}.instruction.assessment_ids",
            )
        }
        unknown_assessments = assessment_ids - assessments_by_unit[unit_id].keys()
        if unknown_assessments:
            raise RecordError(
                f"{context} references unknown unit assessments: "
                f"{', '.join(sorted(unknown_assessments))}"
            )
        for assessment_id in assessment_ids:
            if (
                set(assessments_by_unit[unit_id][assessment_id]["objective_ids"])
                - session_objective_ids
            ):
                raise RecordError(
                    f"{context} references assessment {assessment_id!r} aligned "
                    "outside its session"
                )

    expected = list(range(1, len(sessions) + 1))
    if sorted(session_ids) != expected:
        raise RecordError("session numbers must be contiguous and start at 1")
    session_minutes_by_unit = {
        unit_id: sum(
            session["duration_minutes"]
            for session in sessions
            if session["unit_id"] == unit_id
        )
        for unit_id in unit_ids
    }
    for unit in units:
        if session_minutes_by_unit[unit["id"]] != unit["estimated_minutes"]:
            raise RecordError(
                f"unit {unit['id']!r} estimates {unit['estimated_minutes']} minutes "
                f"but its sessions total {session_minutes_by_unit[unit['id']]}"
            )


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
            allow_empty=True,
        )
        _unique_ids(items, f"week.{field}")
        _validate_references(items, objective_ids, f"week.{field}")
    lessons = _list(week.get("lessons", []), "week.lessons")
    if not week["lectures"] and not lessons:
        raise RecordError("week must contain at least one lecture or daily lesson")

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
            assessment.get("question_bank", []),
            f"week.assessments[{index}].question_bank",
        )
        if not questions and not assessment.get("description"):
            raise RecordError(
                f"week.assessments[{index}] must contain a description or questions"
            )
        if assessment.get("description") is not None:
            _text(
                assessment["description"],
                f"week.assessments[{index}].description",
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

    assessments_by_id = {
        item["id"]: item for item in week["assessments"]
    }
    _unique_ids(lessons, "week.lessons")
    day_numbers: set[int] = set()
    for index, lesson in enumerate(lessons):
        context = f"week.lessons[{index}]"
        _required(
            lesson,
            (
                "id",
                "day_number",
                "title",
                "objective_ids",
                "duration",
                "objective_summary",
                "essential_question",
                "materials",
                "terminology",
                "activities",
                "assessment_ids",
                "industry_applications",
                "common_technician_errors",
                "instructor_shop_tip",
                "homework",
                "flex_activities",
            ),
            context,
        )
        day_number = lesson["day_number"]
        if not isinstance(day_number, int) or day_number < 1:
            raise RecordError(f"{context}.day_number must be a positive integer")
        if day_number in day_numbers:
            raise RecordError(f"duplicate day_number {day_number} in week.lessons")
        day_numbers.add(day_number)
        _text(lesson["title"], f"{context}.title")
        for field in ("objective_summary", "essential_question"):
            _text(lesson[field], f"{context}.{field}")
        _validate_objective_id_list(
            lesson["objective_ids"], objective_ids, f"{context}.objective_ids"
        )

        duration = lesson["duration"]
        if not isinstance(duration, dict):
            raise RecordError(f"{context}.duration must be an object")
        total = duration.get("total_minutes")
        if not isinstance(total, int) or total < 1:
            raise RecordError(
                f"{context}.duration.total_minutes must be a positive integer"
            )
        segments = _list(
            duration.get("segments"), f"{context}.duration.segments"
        )
        segment_total = 0
        for segment_index, segment in enumerate(segments):
            if not isinstance(segment, dict):
                raise RecordError(
                    f"{context}.duration.segments[{segment_index}] must be an object"
                )
            _text(
                segment.get("label"),
                f"{context}.duration.segments[{segment_index}].label",
            )
            minutes = segment.get("minutes")
            if not isinstance(minutes, int) or minutes < 1:
                raise RecordError(
                    f"{context}.duration.segments[{segment_index}].minutes "
                    "must be a positive integer"
                )
            segment_total += minutes
        if segments and segment_total != total:
            raise RecordError(
                f"{context}.duration segments must total {total} minutes"
            )

        for field in ("materials", "terminology"):
            values = _list(
                lesson[field], f"{context}.{field}", allow_empty=False
            )
            for value_index, value in enumerate(values):
                _text(value, f"{context}.{field}[{value_index}]")

        activities = _list(
            lesson["activities"], f"{context}.activities", allow_empty=False
        )
        _unique_ids(activities, f"{context}.activities")
        _validate_references(
            activities,
            objective_ids,
            f"{context}.activities",
            label_field="description",
        )
        lesson_objective_ids = set(lesson["objective_ids"])
        categories = {"warm_up", "academic", "shop", "exit"}
        for activity_index, activity in enumerate(activities):
            if activity.get("category") not in categories:
                raise RecordError(
                    f"{context}.activities[{activity_index}].category is invalid"
                )
            unrelated = set(activity["objective_ids"]) - lesson_objective_ids
            if unrelated:
                raise RecordError(
                    f"{context}.activities[{activity_index}] references objectives "
                    f"outside its lesson: {', '.join(sorted(unrelated))}"
                )
        for required_category in ("warm_up", "exit"):
            count = sum(
                activity["category"] == required_category for activity in activities
            )
            if count != 1:
                raise RecordError(
                    f"{context}.activities must contain exactly one "
                    f"{required_category} activity"
                )

        referenced_assessments = {
            _identifier(value, f"{context}.assessment_ids")
            for value in _list(
                lesson["assessment_ids"],
                f"{context}.assessment_ids",
                allow_empty=False,
            )
        }
        unknown_assessments = referenced_assessments - assessments_by_id.keys()
        if unknown_assessments:
            raise RecordError(
                f"lesson {lesson['id']!r} references unknown assessments: "
                f"{', '.join(sorted(unknown_assessments))}"
            )
        for assessment_id in referenced_assessments:
            unrelated = (
                set(assessments_by_id[assessment_id]["objective_ids"])
                - lesson_objective_ids
            )
            if unrelated:
                raise RecordError(
                    f"lesson {lesson['id']!r} references assessment "
                    f"{assessment_id!r} aligned outside the lesson"
                )
        for field in (
            "industry_applications",
            "instructor_shop_tip",
            "homework",
            "flex_activities",
        ):
            if lesson.get(field) is not None:
                _text(lesson[field], f"{context}.{field}")
        errors = _list(
            lesson["common_technician_errors"],
            f"{context}.common_technician_errors",
            allow_empty=False,
        )
        for error_index, error in enumerate(errors):
            _text(error, f"{context}.common_technician_errors[{error_index}]")


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
