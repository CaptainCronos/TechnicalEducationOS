"""Populate the official Administrative Lesson Plan DOCX template."""

from __future__ import annotations

import copy
import io
import zipfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any

WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{WORD_NAMESPACE}}}"

ElementTree.register_namespace("w", WORD_NAMESPACE)
ElementTree.register_namespace(
    "r",
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
)


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(f"{W}t")).strip()


def _run(
    text: str,
    *,
    bold: bool = False,
    break_before: bool = False,
) -> ElementTree.Element:
    run = ElementTree.Element(f"{W}r")
    properties = ElementTree.SubElement(run, f"{W}rPr")
    fonts = ElementTree.SubElement(properties, f"{W}rFonts")
    fonts.set(f"{W}ascii", "Calibri Light")
    fonts.set(f"{W}hAnsi", "Calibri Light")
    fonts.set(f"{W}cs", "Calibri Light")
    if bold:
        ElementTree.SubElement(properties, f"{W}b")
        ElementTree.SubElement(properties, f"{W}bCs")
    size = ElementTree.SubElement(properties, f"{W}sz")
    size.set(f"{W}val", "22")
    complex_size = ElementTree.SubElement(properties, f"{W}szCs")
    complex_size.set(f"{W}val", "22")
    if break_before:
        ElementTree.SubElement(run, f"{W}br")
    text_node = ElementTree.SubElement(run, f"{W}t")
    text_node.text = text
    return run


def _replace_runs(
    paragraph: ElementTree.Element,
    values: list[tuple[str, bool, bool]],
) -> None:
    for child in list(paragraph):
        if child.tag != f"{W}pPr":
            paragraph.remove(child)
    for text, bold, break_before in values:
        paragraph.append(
            _run(text, bold=bold, break_before=break_before)
        )


def _new_paragraph(
    text: str = "",
    *,
    bold: bool = False,
    template: ElementTree.Element | None = None,
) -> ElementTree.Element:
    paragraph = ElementTree.Element(f"{W}p")
    if template is not None:
        properties = template.find(f"{W}pPr")
        if properties is not None:
            paragraph.append(copy.deepcopy(properties))
    if text:
        paragraph.append(_run(text, bold=bold))
    return paragraph


def _find_paragraph(
    paragraphs: list[ElementTree.Element],
    predicate,
    description: str,
) -> ElementTree.Element:
    for paragraph in paragraphs:
        if predicate(_paragraph_text(paragraph)):
            return paragraph
    raise ValueError(
        f"Administrative Lesson Plan template is missing {description}"
    )


def _hours(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    if remainder == 0:
        return f"{hours} Hr" if hours == 1 else f"{hours} Hrs"
    return f"{hours} Hrs {remainder} min" if hours else f"{remainder} min"


def _time_text(duration: dict[str, Any]) -> str:
    text = _hours(duration["total_minutes"])
    if duration["segments"]:
        segments = " / ".join(
            f"{_hours(segment['minutes'])} {segment['label']}"
            for segment in duration["segments"]
        )
        text += f" ({segments})"
    return text


def _sentence_list(values: list[str]) -> str:
    text = ", ".join(value.rstrip(".") for value in values)
    return f"{text}." if text else ""


def render_administrative_docx(
    template_path: Path,
    course: dict[str, Any],
    week: dict[str, Any],
    lesson: dict[str, Any],
) -> bytes:
    """Return a populated copy of the official administrative DOCX template."""

    try:
        template_bytes = template_path.read_bytes()
    except FileNotFoundError as exc:
        raise ValueError(
            f"Administrative Lesson Plan template not found: {template_path}"
        ) from exc

    with zipfile.ZipFile(io.BytesIO(template_bytes)) as template:
        try:
            document_xml = template.read("word/document.xml")
        except KeyError as exc:
            raise ValueError(
                "Administrative Lesson Plan template has no word/document.xml"
            ) from exc

        for _, namespace in ElementTree.iterparse(
            io.BytesIO(document_xml), events=("start-ns",)
        ):
            prefix, uri = namespace
            ElementTree.register_namespace(prefix, uri)
        document = ElementTree.fromstring(document_xml)
        body = document.find(f"{W}body")
        if body is None:
            raise ValueError("Administrative Lesson Plan template has no body")
        paragraphs = body.findall(f"{W}p")

        week_heading = _find_paragraph(
            paragraphs,
            lambda text: text == "Summer/Week 1",
            "week heading placeholder",
        )
        course_line = _find_paragraph(
            paragraphs,
            lambda text: text.startswith("Course:"),
            "course placeholder",
        )
        time_line = _find_paragraph(
            paragraphs,
            lambda text: text.startswith("Time:"),
            "time placeholder",
        )
        objective_heading = _find_paragraph(
            paragraphs,
            lambda text: text.startswith("Objective - Student will be able to:"),
            "student objective heading",
        )

        _replace_runs(
            week_heading,
            [(f"Week {week['week_number']} / Day {lesson['day_number']}", True, False)],
        )
        _replace_runs(
            course_line,
            [(f"Course: {course['title']}", True, False)],
        )
        _replace_runs(
            time_line,
            [
                ("Time: ", True, False),
                (_time_text(lesson["duration"]), False, False),
            ],
        )

        objective_index = paragraphs.index(objective_heading)
        if objective_index + 1 >= len(paragraphs):
            raise ValueError(
                "Administrative Lesson Plan template has no objective content area"
            )
        objective_content = paragraphs[objective_index + 1]
        _replace_runs(
            objective_content,
            [(lesson["objective_summary"], False, False)],
        )

        blank_after_week = paragraphs[paragraphs.index(week_heading) + 1]
        _replace_runs(
            blank_after_week,
            [(lesson["title"], False, False)],
        )

        objectives = {
            item["id"]: item for item in week["objectives"]
        }
        competencies = {
            item["id"]: item["statement"] for item in course["competencies"]
        }
        lesson_objectives = [
            objectives[objective_id] for objective_id in lesson["objective_ids"]
        ]
        objective_text = " ".join(
            item["statement"] for item in lesson_objectives
        )
        competency_ids = dict.fromkeys(
            competency_id
            for objective in lesson_objectives
            for competency_id in objective["competency_ids"]
        )
        standard_text = " ".join(
            competencies[competency_id] for competency_id in competency_ids
        )
        activities = {
            category: [
                item["description"]
                for item in lesson["activities"]
                if item["category"] == category
            ]
            for category in ("warm_up", "academic", "shop", "exit")
        }
        configuration = [
            ("Warm Up", activities["warm_up"][0]),
            ("Objective", objective_text),
            ("Standard", standard_text),
            ("Essential Question", lesson["essential_question"]),
            ("Exit", activities["exit"][0]),
        ]

        tables = body.findall(f"{W}tbl")
        if not tables:
            raise ValueError(
                "Administrative Lesson Plan template has no configuration table"
            )
        rows = tables[0].findall(f"{W}tr")
        if len(rows) != len(configuration):
            raise ValueError(
                "Administrative Lesson Plan template configuration table "
                "must contain five rows"
            )
        for row, (label, value) in zip(rows, configuration):
            paragraph = row.find(f".//{W}p")
            if paragraph is None:
                raise ValueError(
                    "Administrative Lesson Plan template has an empty "
                    "configuration row"
                )
            if not _paragraph_text(paragraph).startswith(label):
                raise ValueError(
                    "Administrative Lesson Plan template configuration rows "
                    "are not in the expected order"
                )
            _replace_runs(
                paragraph,
                [(label, True, False), (value, False, True)],
            )

        assessments = {
            item["id"]: item for item in week["assessments"]
        }
        section_content: list[tuple[str, list[str]]] = [
            ("Necessary Materials", [_sentence_list(lesson["materials"])]),
            ("Terminology", [_sentence_list(lesson["terminology"])]),
            ("Academic Activities", activities["academic"]),
            ("Shop Activities", activities["shop"]),
            ("Industry Applications", [lesson["industry_applications"]]),
            ("Common Technician Errors", lesson["common_technician_errors"]),
            ("Instructor's Shop Tip", [lesson["instructor_shop_tip"]]),
            (
                "Assessment",
                [
                    assessments[assessment_id]["description"]
                    for assessment_id in lesson["assessment_ids"]
                ],
            ),
            ("Homework", [lesson["homework"]]),
            ("Notes / Flex Activities", [lesson["flex_activities"]]),
        ]

        section_properties = body.find(f"{W}sectPr")
        if section_properties is None:
            raise ValueError(
                "Administrative Lesson Plan template has no section properties"
            )
        for heading, content in section_content:
            body.insert(
                list(body).index(section_properties),
                _new_paragraph(heading, bold=True, template=objective_heading),
            )
            for value in content:
                body.insert(
                    list(body).index(section_properties),
                    _new_paragraph(
                        value,
                        template=objective_content,
                    ),
                )
        body.insert(
            list(body).index(section_properties),
            _new_paragraph(
                "Instructor Reflection",
                bold=True,
                template=objective_heading,
            ),
        )
        for label in (
            "Student strengths:",
            "Student challenges:",
            "Concepts requiring additional review:",
        ):
            body.insert(
                list(body).index(section_properties),
                _new_paragraph(label, template=objective_content),
            )
            body.insert(
                list(body).index(section_properties),
                _new_paragraph(template=objective_content),
            )

        rendered_xml = ElementTree.tostring(
            document,
            encoding="utf-8",
            xml_declaration=True,
        )
        result = io.BytesIO()
        with zipfile.ZipFile(result, "w") as output:
            for item in template.infolist():
                content = (
                    rendered_xml
                    if item.filename == "word/document.xml"
                    else template.read(item.filename)
                )
                output.writestr(item, content)
    return result.getvalue()
