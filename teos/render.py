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


def render_lab(
    course: dict[str, Any],
    week: dict[str, Any],
    lab: dict[str, Any],
    institution: dict[str, Any] | None = None,
) -> str:
    lines = _header(f"Lab: {lab['title']}", course, week, institution)
    objective_statements = {
        objective["id"]: objective["statement"] for objective in week["objectives"]
    }
    lines.extend(
        [
            f"- Duration: {lab['duration_minutes']} minutes",
            "",
            "## Objectives",
            "",
            *(
                f"- **{objective_id}** — {objective_statements[objective_id]}"
                for objective_id in lab["objective_ids"]
            ),
        ]
    )
    if lab.get("safety_notes"):
        lines.extend(["", "## Safety", "", _bullets(lab["safety_notes"])])
    lines.extend(
        [
            "",
            "## Procedure",
            "",
            _numbered(lab["procedure"]),
            "",
            "## Deliverables",
            "",
            _bullets(lab["deliverables"]),
        ]
    )
    return "\n".join(lines) + "\n"


def assessment_batches(
    assessment: dict[str, Any], size: int = 10
) -> list[list[dict[str, Any]]]:
    questions = assessment["question_bank"]
    return [questions[index : index + size] for index in range(0, len(questions), size)]


def _question_text(question: dict[str, Any], number: int) -> list[str]:
    lines = [f"{number}. {question['prompt']}"]
    if question["type"] == "multiple_choice":
        lines.extend(
            f"   {chr(65 + index)}. {choice}"
            for index, choice in enumerate(question.get("choices", []))
        )
    return lines


def render_assessment_batch(
    course: dict[str, Any],
    week: dict[str, Any],
    assessment: dict[str, Any],
    questions: list[dict[str, Any]],
    batch_number: int,
    institution: dict[str, Any] | None = None,
) -> str:
    lines = _header(
        f"Assessment: {assessment['title']} — Batch {batch_number}",
        course,
        week,
        institution,
    )
    lines.extend(
        [
            f"- Type: {assessment['type']}",
            f"- Objectives: {', '.join(assessment['objective_ids'])}",
            "",
            "## Questions",
            "",
        ]
    )
    for number, question in enumerate(questions, 1):
        lines.extend(_question_text(question, number))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_assessment_key(
    course: dict[str, Any],
    week: dict[str, Any],
    assessment: dict[str, Any],
    questions: list[dict[str, Any]],
    batch_number: int,
    institution: dict[str, Any] | None = None,
) -> str:
    lines = _header(
        f"Assessment Key: {assessment['title']} — Batch {batch_number}",
        course,
        week,
        institution,
    )
    lines.extend(["", "## Answers and rubrics", ""])
    for number, question in enumerate(questions, 1):
        guidance = question.get("answer") or question.get("rubric") or "Not recorded."
        lines.append(f"{number}. **{question['id']}** — {guidance}")
    return "\n".join(lines) + "\n"


def render_audit(
    course: dict[str, Any], week: dict[str, Any], findings: list[str]
) -> str:
    lines = [
        "# Curriculum Relationship Audit",
        "",
        f"- Course: {course['title']} (`{course['course_id']}`)",
        f"- Week: {week['week_number']} — {week['title']}",
        f"- Result: {'PASS' if not findings else 'REVIEW'}",
        "",
        "## Findings",
        "",
        _bullets(findings, "No relationship gaps found."),
    ]
    return "\n".join(lines) + "\n"
