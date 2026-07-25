"""Map canonical instructional sessions onto institution-specific meeting slots."""

from __future__ import annotations

from datetime import date
from typing import Any

from teos.records import CURRICULUM_SCHEMA_VERSION, RecordError


def validate_calendar(calendar: dict[str, Any]) -> None:
    required = ("schema_version", "calendar_id", "course_id", "meeting_slots")
    missing = [field for field in required if field not in calendar]
    if missing:
        raise RecordError(f"academic calendar is missing: {', '.join(missing)}")
    if calendar["schema_version"] != CURRICULUM_SCHEMA_VERSION:
        raise RecordError("unsupported academic calendar schema")
    if not isinstance(calendar["meeting_slots"], list):
        raise RecordError("academic calendar meeting_slots must be a list")

    seen_dates: set[str] = set()
    seen_aliases: set[tuple[int, int]] = set()
    for index, slot in enumerate(calendar["meeting_slots"]):
        context = f"academic calendar meeting_slots[{index}]"
        if not isinstance(slot, dict) or "date" not in slot:
            raise RecordError(f"{context} must contain a date")
        try:
            date.fromisoformat(slot["date"])
        except (TypeError, ValueError) as exc:
            raise RecordError(f"{context}.date must be ISO YYYY-MM-DD") from exc
        if slot["date"] in seen_dates:
            raise RecordError(f"duplicate meeting date {slot['date']}")
        seen_dates.add(slot["date"])
        if "available" in slot and not isinstance(slot["available"], bool):
            raise RecordError(f"{context}.available must be boolean")
        aliases = slot.get("aliases", {})
        if not isinstance(aliases, dict):
            raise RecordError(f"{context}.aliases must be an object")
        if aliases:
            week = aliases.get("week")
            day = aliases.get("day")
            if (
                not isinstance(week, int)
                or week < 1
                or not isinstance(day, int)
                or day < 1
            ):
                raise RecordError(
                    f"{context}.aliases must contain positive week and day integers"
                )
            alias = (week, day)
            if alias in seen_aliases:
                raise RecordError(f"duplicate calendar alias week {week} day {day}")
            seen_aliases.add(alias)


def schedule_sessions(
    course: dict[str, Any],
    sessions: list[dict[str, Any]],
    calendar: dict[str, Any],
) -> dict[str, Any]:
    """Assign sessions in sequence without mutating curriculum records."""
    validate_calendar(calendar)
    if calendar["course_id"] != course["course_id"]:
        raise RecordError("academic calendar course_id does not match course.course_id")
    available = [
        slot for slot in calendar["meeting_slots"] if slot.get("available", True)
    ]
    if len(available) < len(sessions):
        raise RecordError(
            f"academic calendar has {len(available)} available slots for "
            f"{len(sessions)} sessions"
        )
    for session, slot in zip(
        sorted(sessions, key=lambda item: item["session_number"]),
        available,
    ):
        capacity = slot.get("duration_minutes")
        if capacity is not None and (
            not isinstance(capacity, int)
            or capacity < session["duration_minutes"]
        ):
            raise RecordError(
                f"meeting {slot['date']} cannot hold session "
                f"{session['session_number']} ({session['duration_minutes']} minutes)"
            )
    assignments = [
        {
            "session_number": session["session_number"],
            "session_id": session["id"],
            "unit_id": session["unit_id"],
            "date": slot["date"],
            "aliases": slot.get("aliases", {}),
        }
        for session, slot in zip(
            sorted(sessions, key=lambda item: item["session_number"]),
            available,
        )
    ]
    return {
        "schema_version": CURRICULUM_SCHEMA_VERSION,
        "schedule_id": f"{calendar['calendar_id']}.{course['course_id']}",
        "calendar_id": calendar["calendar_id"],
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
        if session_number is not None and assignment["session_number"] == session_number:
            return session_number
        if meeting_date is not None and assignment["date"] == meeting_date:
            return assignment["session_number"]
        aliases = assignment.get("aliases", {})
        if week is not None and aliases.get("week") == week and aliases.get("day") == day:
            return assignment["session_number"]
    raise RecordError("calendar selector does not resolve to a scheduled session")
