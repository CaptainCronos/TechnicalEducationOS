"""Render administrative views from canonical units and sessions."""

from __future__ import annotations

from typing import Any


def _bullets(values: list[str], empty: str = "None recorded.") -> str:
    return "\n".join(f"- {value}" for value in values) if values else empty


def _numbered(values: list[str], empty: str = "None recorded.") -> str:
    return (
        "\n".join(f"{index}. {value}" for index, value in enumerate(values, 1))
        if values
        else empty
    )


def _context(
    course: dict[str, Any],
    unit: dict[str, Any],
    session: dict[str, Any],
    institution: dict[str, Any] | None,
) -> list[str]:
    lines = [
        f"- Course: {course['title']} (`{course['course_id']}`)",
        f"- Session: {session['session_number']} — {session['title']}",
        f"- Instructional unit: {unit['title']} (`{unit['id']}`)",
        f"- Phase: {session['phase'].title()}",
        f"- Duration: {session['duration_minutes']} minutes",
    ]
    if institution:
        lines.append(f"- Institution: {institution['institution_name']}")
    return lines


def _session_objectives(
    unit: dict[str, Any], session: dict[str, Any]
) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in unit["objectives"]}
    return [by_id[objective_id] for objective_id in session["objective_ids"]]


def render_administrative_session(
    course: dict[str, Any],
    unit: dict[str, Any],
    session: dict[str, Any],
    institution: dict[str, Any] | None = None,
) -> str:
    """Render a lesson-plan view; the document itself is never a source record."""
    detail = session.get("instruction", {})
    objectives = _session_objectives(unit, session)
    activities = detail.get("activities", [])
    assessments_by_id = {
        assessment["id"]: assessment for assessment in unit["assessments"]
    }
    by_category = {
        category: [
            item["description"]
            for item in activities
            if item.get("category") == category
        ]
        for category in ("warm_up", "academic", "shop", "exit")
    }
    lines = [
        "# Administrative Lesson Plan",
        "",
        *_context(course, unit, session, institution),
        "",
        "## Objectives",
        "",
        *(
            f"- **{objective['id']}** — {objective['statement']}"
            for objective in objectives
        ),
        "",
        "## Essential Question",
        "",
        detail.get("essential_question", "None recorded."),
        "",
        "## Materials",
        "",
        _bullets(detail.get("materials", unit["required_resources"])),
        "",
        "## Warm Up",
        "",
        _numbered(by_category["warm_up"]),
        "",
        "## Academic Activities",
        "",
        _numbered(by_category["academic"]),
        "",
        "## Shop Activities",
        "",
        _numbered(by_category["shop"]),
        "",
        "## Exit",
        "",
        _numbered(by_category["exit"]),
        "",
        "## Assessment",
        "",
        _bullets(
            [
                assessments_by_id[assessment_id].get(
                    "description",
                    assessments_by_id[assessment_id]["title"],
                )
                for assessment_id in detail.get("assessment_ids", [])
            ]
        ),
    ]
    return "\n".join(lines) + "\n"


def render_instructor_session(
    course: dict[str, Any],
    unit: dict[str, Any],
    session: dict[str, Any],
    institution: dict[str, Any] | None = None,
) -> str:
    detail = session.get("instruction", {})
    lines = [
        "# Instructor Guide",
        "",
        *_context(course, unit, session, institution),
        "",
        "## Preparation",
        "",
        _bullets(detail.get("preparation", unit.get("preparation", []))),
        "",
        "## Teaching Sequence",
        "",
        _numbered(
            [
                item["description"]
                for item in detail.get("activities", [])
                if item.get("category") in {"academic", "shop"}
            ]
        ),
        "",
        "## Common Technician Errors",
        "",
        _bullets(detail.get("common_technician_errors", [])),
        "",
        "## Instructor Shop Tip",
        "",
        detail.get("instructor_shop_tip", "None recorded."),
        "",
        "## Flex Activities",
        "",
        detail.get("flex_activities", "None recorded."),
    ]
    return "\n".join(lines) + "\n"


def render_lab_session(
    course: dict[str, Any],
    unit: dict[str, Any],
    session: dict[str, Any],
    institution: dict[str, Any] | None = None,
) -> str:
    objective_ids = set(session["objective_ids"])
    labs = [
        lab
        for lab in unit["labs"]
        if objective_ids.intersection(lab["objective_ids"])
    ]
    lines = [
        "# Lab Sheet",
        "",
        *_context(course, unit, session, institution),
    ]
    if not labs:
        lines.extend(["", "No lab is assigned to this session."])
    for lab in labs:
        lines.extend(
            [
                "",
                f"## {lab['title']}",
                "",
                "### Procedure",
                "",
                _numbered(lab.get("procedure", [])),
                "",
                "### Deliverables",
                "",
                _bullets(lab.get("deliverables", [])),
                "",
                "### Safety",
                "",
                _bullets(lab.get("safety_notes", [])),
            ]
        )
    return "\n".join(lines) + "\n"


SESSION_RENDERERS = {
    "administrative": render_administrative_session,
    "instructor": render_instructor_session,
    "lab": render_lab_session,
}
