"""Deterministic Markdown renderers for Phase 1 lesson plans."""

from __future__ import annotations

from typing import Any


def _bullets(values: list[str], empty: str = "None recorded.") -> str:
    return "\n".join(f"- {value}" for value in values) if values else empty


def _numbered(values: list[str]) -> str:
    return "\n".join(f"{index}. {value}" for index, value in enumerate(values, 1))


def _header(
    document_title: str,
    course: dict[str, Any],
    week: dict[str, Any],
    institution: dict[str, Any] | None,
) -> list[str]:
    lines = [
        f"# {document_title}",
        "",
        f"- Course: {course['title']} (`{course['course_id']}`)",
        f"- Week: {week['week_number']} — {week['title']}",
    ]
    if institution:
        lines.append(f"- Institution: {institution['institution_name']}")
        if institution.get("program_name"):
            lines.append(f"- Program: {institution['program_name']}")
        lines.extend(
            f"- {label}: {value}"
            for label, value in institution.get("administrative_fields", {}).items()
        )
    return lines


def render_administrative(
    course: dict[str, Any],
    week: dict[str, Any],
    institution: dict[str, Any] | None = None,
) -> str:
    lines = _header("Administrative Lesson Plan", course, week, institution)
    lines.extend(["", "## Objectives", "", "| ID | Objective | Competencies |", "|---|---|---|"])
    lines.extend(
        f"| {item['id']} | {item['statement']} | {', '.join(item['competency_ids'])} |"
        for item in week["objectives"]
    )
    lines.extend(["", "## Instructional schedule", "", "| Activity | Minutes | Objectives |", "|---|---:|---|"])
    for kind in ("lectures", "labs"):
        label = kind[:-1].title()
        lines.extend(
            f"| {label}: {item['title']} | {item['duration_minutes']} | "
            f"{', '.join(item['objective_ids'])} |"
            for item in week[kind]
        )
    lines.extend(["", "## Assessment alignment", ""])
    if week["assessments"]:
        lines.extend(
            f"- {item['title']} ({item['type']}): "
            f"{', '.join(item['objective_ids'])}"
            for item in week["assessments"]
        )
    else:
        lines.append("None recorded.")
    return "\n".join(lines) + "\n"


def render_instructor(
    course: dict[str, Any],
    week: dict[str, Any],
    institution: dict[str, Any] | None = None,
) -> str:
    lines = _header("Instructor Lesson Plan", course, week, institution)
    lines.extend(["", "## Preparation", "", _bullets(week.get("preparation", []))])
    lines.extend(["", "## Objectives", ""])
    lines.extend(f"- **{item['id']}** — {item['statement']}" for item in week["objectives"])

    lines.extend(["", "## Lectures"])
    for item in week["lectures"]:
        lines.extend(
            [
                "",
                f"### {item['title']} ({item['duration_minutes']} minutes)",
                "",
                f"Objectives: {', '.join(item['objective_ids'])}",
                "",
                _bullets(item["topics"]),
            ]
        )
        if item.get("instructor_notes"):
            lines.extend(["", "Instructor notes:", "", _bullets(item["instructor_notes"])])

    lines.extend(["", "## Labs"])
    if not week["labs"]:
        lines.extend(["", "None recorded."])
    for item in week["labs"]:
        lines.extend(
            [
                "",
                f"### {item['title']} ({item['duration_minutes']} minutes)",
                "",
                f"Objectives: {', '.join(item['objective_ids'])}",
                "",
                "Procedure:",
                "",
                _numbered(item["procedure"]),
                "",
                "Deliverables:",
                "",
                _bullets(item["deliverables"]),
            ]
        )
        if item.get("safety_notes"):
            lines.extend(["", "Safety notes:", "", _bullets(item["safety_notes"])])

    lines.extend(["", "## Assessment checkpoints", ""])
    if week["assessments"]:
        lines.extend(
            f"- {item['title']} ({item['type']}): "
            f"{', '.join(item['objective_ids'])}"
            for item in week["assessments"]
        )
    else:
        lines.append("None recorded.")
    lines.extend(["", "## Preserved teaching notes", "", _bullets(week.get("teaching_notes", []))])
    return "\n".join(lines) + "\n"
