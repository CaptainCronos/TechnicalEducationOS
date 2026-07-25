"""Map canonical sessions through an institution profile onto a calendar."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from teos.records import (
    CURRICULUM_SCHEMA_VERSION,
    RecordError,
    validate_institution,
)

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
CALENDAR_SCHEMA_VERSION = "2.0"


def _iso_date(value: Any, context: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RecordError(f"{context} must be ISO YYYY-MM-DD") from exc


def validate_calendar(calendar: dict[str, Any]) -> None:
    """Validate a curriculum-free calendar of term boundaries and events."""
    required = (
        "schema_version",
        "calendar_id",
        "institution_id",
        "term_id",
        "name",
        "first_day",
        "last_day",
        "events",
    )
    missing = [field for field in required if field not in calendar]
    if missing:
        raise RecordError(f"academic calendar is missing: {', '.join(missing)}")
    if calendar["schema_version"] != CALENDAR_SCHEMA_VERSION:
        raise RecordError("unsupported academic calendar schema")
    for field in ("calendar_id", "institution_id", "term_id", "name"):
        if not isinstance(calendar[field], str) or not calendar[field].strip():
            raise RecordError(f"academic calendar {field} must be non-empty text")
    first_day = _iso_date(calendar["first_day"], "academic calendar first_day")
    last_day = _iso_date(calendar["last_day"], "academic calendar last_day")
    if last_day < first_day:
        raise RecordError("academic calendar last_day precedes first_day")
    events = calendar["events"]
    if not isinstance(events, list):
        raise RecordError("academic calendar events must be a list")
    valid_types = {
        "holiday",
        "break",
        "faculty_work_day",
        "graduation",
        "institutional_closure",
    }
    for index, event in enumerate(events):
        context = f"academic calendar events[{index}]"
        if not isinstance(event, dict):
            raise RecordError(f"{context} must be an object")
        missing = [
            field
            for field in ("name", "type", "start_date", "end_date")
            if field not in event
        ]
        if missing:
            raise RecordError(f"{context} is missing: {', '.join(missing)}")
        if not isinstance(event["name"], str) or not event["name"].strip():
            raise RecordError(f"{context}.name must be non-empty text")
        if event["type"] not in valid_types:
            raise RecordError(f"{context}.type is invalid")
        event_start = _iso_date(event["start_date"], f"{context}.start_date")
        event_end = _iso_date(event["end_date"], f"{context}.end_date")
        if event_end < event_start:
            raise RecordError(f"{context} ends before it starts")
        if "instructional" in event and not isinstance(event["instructional"], bool):
            raise RecordError(f"{context}.instructional must be boolean")


def _meeting_pattern(
    institution: dict[str, Any],
    pattern_id: str,
) -> dict[str, Any]:
    for pattern in institution["meeting_patterns"]:
        if pattern["pattern_id"] == pattern_id:
            return pattern
    raise RecordError(
        f"meeting pattern {pattern_id!r} not found in institution profile"
    )


def available_meeting_slots(
    institution: dict[str, Any],
    calendar: dict[str, Any],
    meeting_pattern_id: str,
) -> list[dict[str, Any]]:
    """Resolve an institution's meeting rule against a term calendar."""
    validate_institution(institution)
    validate_calendar(calendar)
    if calendar["institution_id"] != institution["institution_id"]:
        raise RecordError(
            "academic calendar institution_id does not match institution profile"
        )
    term = next(
        (
            item
            for item in institution["academic_year"]["terms"]
            if item["term_id"] == calendar["term_id"]
        ),
        None,
    )
    if term is None or term["calendar_id"] != calendar["calendar_id"]:
        raise RecordError("academic calendar is not registered to the profile term")

    pattern = _meeting_pattern(institution, meeting_pattern_id)
    calendar_start = _iso_date(calendar["first_day"], "academic calendar first_day")
    calendar_end = _iso_date(calendar["last_day"], "academic calendar last_day")
    pattern_start = _iso_date(pattern["starts_on"], "meeting pattern starts_on")
    pattern_end = (
        _iso_date(pattern["ends_on"], "meeting pattern ends_on")
        if pattern.get("ends_on")
        else calendar_end
    )
    start = max(calendar_start, pattern_start)
    end = min(calendar_end, pattern_end)
    if end < start:
        return []

    unavailable: dict[date, str] = {}
    for event in calendar["events"]:
        if event.get("instructional", False):
            continue
        event_day = _iso_date(event["start_date"], "calendar event start_date")
        event_end = _iso_date(event["end_date"], "calendar event end_date")
        while event_day <= event_end:
            unavailable[event_day] = event["name"]
            event_day += timedelta(days=1)

    meetings_by_weekday = {
        WEEKDAYS[item["weekday"]]: item for item in pattern["meetings"]
    }
    first_week = pattern.get("first_week_number", 1)
    pattern_week_start = pattern_start - timedelta(days=pattern_start.weekday())
    slots: list[dict[str, Any]] = []
    current = start
    while current <= end:
        meeting = meetings_by_weekday.get(current.weekday())
        if meeting is not None and current not in unavailable:
            week = first_week + ((current - pattern_week_start).days // 7)
            slots.append(
                {
                    "date": current.isoformat(),
                    "start_time": meeting["start_time"],
                    "duration_minutes": meeting["duration_minutes"],
                    "aliases": {"week": week, "day": meeting["day"]},
                }
            )
        current += timedelta(days=1)
    return slots


def schedule_sessions(
    course: dict[str, Any],
    sessions: list[dict[str, Any]],
    institution: dict[str, Any],
    calendar: dict[str, Any],
    meeting_pattern_id: str,
) -> dict[str, Any]:
    """Assign sessions in sequence without mutating curriculum records."""
    available = available_meeting_slots(
        institution,
        calendar,
        meeting_pattern_id,
    )
    if len(available) < len(sessions):
        raise RecordError(
            f"academic calendar has {len(available)} available slots for "
            f"{len(sessions)} sessions"
        )
    ordered_sessions = sorted(sessions, key=lambda item: item["session_number"])
    for session, slot in zip(ordered_sessions, available):
        if slot["duration_minutes"] < session["duration_minutes"]:
            raise RecordError(
                f"meeting {slot['date']} cannot hold session "
                f"{session['session_number']} ({session['duration_minutes']} minutes)"
            )
    assignments = [
        {
            "session_number": session["session_number"],
            "session_id": session["id"],
            "unit_id": session["unit_id"],
            **slot,
        }
        for session, slot in zip(ordered_sessions, available)
    ]
    return {
        "schema_version": CURRICULUM_SCHEMA_VERSION,
        "schedule_id": (
            f"{institution['institution_id']}.{calendar['calendar_id']}."
            f"{meeting_pattern_id}.{course['course_id']}"
        ),
        "institution_id": institution["institution_id"],
        "calendar_id": calendar["calendar_id"],
        "meeting_pattern_id": meeting_pattern_id,
        "course_id": course["course_id"],
        "assignments": assignments,
        "completion_date": assignments[-1]["date"] if assignments else None,
    }


def resolve_session(
    schedule: dict[str, Any],
    *,
    session_number: int | None = None,
    week: int | None = None,
    day: int | None = None,
    meeting_date: str | None = None,
) -> int:
    """Resolve a direct session selector or a calendar alias to a session number."""
    selectors = sum(
        (
            session_number is not None,
            meeting_date is not None,
            week is not None or day is not None,
        )
    )
    if selectors != 1 or ((week is None) != (day is None)):
        raise RecordError(
            "select exactly one of session number, meeting date, or week and day"
        )
    for assignment in schedule["assignments"]:
        if (
            session_number is not None
            and assignment["session_number"] == session_number
        ):
            return session_number
        if meeting_date is not None and assignment["date"] == meeting_date:
            return assignment["session_number"]
        aliases = assignment.get("aliases", {})
        if (
            week is not None
            and aliases.get("week") == week
            and aliases.get("day") == day
        ):
            return assignment["session_number"]
    raise RecordError("calendar selector does not resolve to a scheduled session")
