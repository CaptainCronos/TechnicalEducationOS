"""Deterministic Markdown renderers for legacy week-based lesson plans."""

from __future__ import annotations

from typing import Any


def _bullets(values: list[str], empty: str = "None recorded.") -> str:
    return "\n".join(f"- {value}" for value in values) if values else empty


def _numbered(values: list[str]) -> str:
    return "\n".join(f"{index}. {value}" for index, value in enumerate(values, 1))


def _hours(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    if remainder == 0:
        return f"{hours} Hr" if hours == 1 else f"{hours} Hrs"
    return f"{minutes} minutes"


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
    lesson: dict[str, Any] | None = None,
) -> str:
    if lesson is not None:
        return _render_daily_administrative(course, week, lesson, institution)
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


def _render_daily_administrative(
    course: dict[str, Any],
    week: dict[str, Any],
    lesson: dict[str, Any],
    institution: dict[str, Any] | None,
) -> str:
    duration = lesson["duration"]
    segment_text = " / ".join(
        f"{_hours(segment['minutes'])} {segment['label']}"
        for segment in duration["segments"]
    )
    time_text = _hours(duration["total_minutes"])
    if segment_text:
        time_text += f" ({segment_text})"

    objectives = {
        objective["id"]: objective for objective in week["objectives"]
    }
    competencies = {
        competency["id"]: competency["statement"]
        for competency in course["competencies"]
    }
    lesson_objectives = [
        objectives[objective_id] for objective_id in lesson["objective_ids"]
    ]
    objective_text = " ".join(
        objective["statement"] for objective in lesson_objectives
    )
    competency_ids = dict.fromkeys(
        competency_id
        for objective in lesson_objectives
        for competency_id in objective["competency_ids"]
    )
    standard_text = " ".join(
        competencies[competency_id] for competency_id in competency_ids
    )
    activities_by_category = {
        category: [
            activity["description"]
            for activity in lesson["activities"]
            if activity["category"] == category
        ]
        for category in ("warm_up", "academic", "shop", "exit")
    }
    assessments = {
        assessment["id"]: assessment for assessment in week["assessments"]
    }
    assessment_text = [
        assessments[assessment_id]["description"]
        for assessment_id in lesson["assessment_ids"]
        if assessments[assessment_id].get("description")
    ]

    lines = [
        f"# {course['title']} – Week {week['week_number']} "
        f"Day {lesson['day_number']} Administrative Lesson Plan",
        "",
        lesson["title"],
        "",
        f"*Time: {time_text}*",
    ]
    if institution:
        lines.extend(["", f"Institution: {institution['institution_name']}"])
        if institution.get("program_name"):
            lines.append(f"Program: {institution['program_name']}")
        lines.extend(
            f"{label}: {value}"
            for label, value in institution.get("administrative_fields", {}).items()
        )
    lines.extend(
        [
            "",
            "## Configuration Board",
            "",
            "| Element | Plan |",
            "|---|---|",
            f"| Warm Up | {activities_by_category['warm_up'][0]} |",
            f"| Objective | {objective_text} |",
            f"| Standard | {standard_text} |",
            f"| Essential Question | {lesson['essential_question']} |",
            f"| Exit | {activities_by_category['exit'][0]} |",
            "",
            "## Student Objectives",
            "",
            lesson["objective_summary"],
            "",
            "## Necessary Materials",
            "",
            ", ".join(lesson["materials"]),
            "",
            "## Terminology",
            "",
            ", ".join(lesson["terminology"]),
            "",
            "## Academic Activities",
            "",
            _numbered(activities_by_category["academic"]),
            "",
            "## Shop Activities",
            "",
            _numbered(activities_by_category["shop"]),
            "",
            "## Industry Applications",
            "",
            lesson.get("industry_applications", "None recorded."),
            "",
            "## Common Technician Errors",
            "",
            _numbered(lesson.get("common_technician_errors", [])),
            "",
            "## Instructor's Shop Tip",
            "",
            lesson.get("instructor_shop_tip", "None recorded."),
            "",
            "## Assessment",
            "",
            "\n\n".join(assessment_text) if assessment_text else "None recorded.",
            "",
            "## Homework",
            "",
            lesson.get("homework", "None recorded."),
            "",
            "## Notes / Flex Activities",
            "",
            lesson.get("flex_activities", "None recorded."),
            "",
            "## Instructor Reflection",
            "",
            "Student strengths:",
            "",
            "Student challenges:",
            "",
            "Concepts requiring additional review:",
        ]
    )
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
    questions = assessment.get("question_bank", [])
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
