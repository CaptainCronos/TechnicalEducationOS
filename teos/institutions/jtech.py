"""J-Tech Administrative Lesson Plan DOCX presentation.

Curriculum values enter this module as validated source records. Everything
created here—headings, ordering, typography, tables, numbering, spacing, and
reflection prompts—is institution-owned presentation.
"""

from __future__ import annotations

import copy
import io
import zipfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any, Iterable

WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{WORD_NAMESPACE}}}"

ElementTree.register_namespace("w", WORD_NAMESPACE)
ElementTree.register_namespace(
    "r",
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
)

HEADING_COLOR = "2F5496"
BODY_FONT = "Times New Roman"
HEADING_FONT = "Calibri Light"
CONFIGURATION_LABELS = (
    "Warm Up",
    "Objective",
    "Standard",
    "Essential Question",
    "Exit",
)
REFLECTION_PROMPTS = (
    "Student strengths:",
    "Student challenges:",
    "Concepts requiring additional review:",
)


def _element(tag: str, **attributes: str) -> ElementTree.Element:
    element = ElementTree.Element(f"{W}{tag}")
    for name, value in attributes.items():
        element.set(f"{W}{name}", value)
    return element


def _append(parent: ElementTree.Element, tag: str, **attributes: str) -> ElementTree.Element:
    child = _element(tag, **attributes)
    parent.append(child)
    return child


def _run(
    text: str,
    *,
    bold: bool = False,
    font: str = BODY_FONT,
    size: int = 20,
    color: str | None = None,
) -> ElementTree.Element:
    run = _element("r")
    properties = _append(run, "rPr")
    _append(properties, "rFonts", ascii=font, hAnsi=font, cs=font)
    if bold:
        _append(properties, "b")
        _append(properties, "bCs")
    if color:
        _append(properties, "color", val=color)
    _append(properties, "sz", val=str(size))
    _append(properties, "szCs", val=str(size))
    text_node = _append(run, "t")
    if text[:1].isspace() or text[-1:].isspace():
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text
    return run


def _paragraph(
    text: str = "",
    *,
    style: str = "Normal",
    bold: bool = False,
    heading: bool = False,
    numbered: bool = False,
) -> ElementTree.Element:
    paragraph = _element("p")
    properties = _append(paragraph, "pPr")
    _append(properties, "pStyle", val=style)
    if numbered:
        _append(properties, "contextualSpacing", val="0")
    if heading:
        _append(properties, "keepNext")
        _append(properties, "keepLines")
    if text:
        if heading:
            paragraph.append(
                _run(
                    text,
                    font=HEADING_FONT,
                    size=32,
                    color=HEADING_COLOR,
                )
            )
        else:
            paragraph.append(_run(text, bold=bold))
    return paragraph


def _heading(text: str, level: int = 2) -> ElementTree.Element:
    return _paragraph(text, style=f"Heading{level}", heading=True)


def _list_items(values: Iterable[str]) -> list[ElementTree.Element]:
    return [
        _paragraph(
            f"• {value}",
            style="ListParagraph",
            numbered=True,
        )
        for value in values
    ]


def _hours(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    if not hours:
        return f"{remainder} min"
    hour_text = f"{hours} Hr" if hours == 1 else f"{hours} Hrs"
    return f"{hour_text} {remainder} min" if remainder else hour_text


def _time_text(duration: dict[str, Any]) -> str:
    text = _hours(duration["total_minutes"])
    segments = duration.get("segments", [])
    if segments:
        segment_text = " / ".join(
            f"{_hours(segment['minutes'])} {segment['label']}"
            for segment in segments
        )
        text += f" ({segment_text})"
    return text


def _sentence_list(values: list[str]) -> str:
    text = ", ".join(value.rstrip(".") for value in values)
    return f"{text}." if text else ""


def _border(parent: ElementTree.Element, edge: str) -> None:
    _append(parent, edge, val="single", sz="4", space="0", color="auto")


def _configuration_table(rows: list[tuple[str, str]]) -> ElementTree.Element:
    table = _element("tbl")
    properties = _append(table, "tblPr")
    _append(properties, "tblW", w="8640", type="dxa")
    borders = _append(properties, "tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        _border(borders, edge)
    margins = _append(properties, "tblCellMar")
    _append(margins, "top", w="35", type="dxa")
    _append(margins, "left", w="60", type="dxa")
    _append(margins, "bottom", w="35", type="dxa")
    _append(margins, "right", w="60", type="dxa")
    _append(
        properties,
        "tblLook",
        val="04A0",
        firstRow="1",
        lastRow="0",
        firstColumn="1",
        lastColumn="0",
        noHBand="0",
        noVBand="1",
    )
    grid = _append(table, "tblGrid")
    _append(grid, "gridCol", w="2160")
    _append(grid, "gridCol", w="6480")

    for label, value in rows:
        row = _append(table, "tr")
        for width, text, bold in (
            ("2160", label, True),
            ("6480", value, False),
        ):
            cell = _append(row, "tc")
            cell_properties = _append(cell, "tcPr")
            _append(cell_properties, "tcW", w=width, type="dxa")
            cell_borders = _append(cell_properties, "tcBorders")
            for edge in ("top", "left", "bottom", "right"):
                _border(cell_borders, edge)
            cell.append(_paragraph(text, bold=bold))
    return table


def _set_style(
    styles: ElementTree.Element,
    style_id: str,
    *,
    name: str,
    based_on: str | None = None,
    next_style: str | None = None,
    default: bool = False,
    heading_level: int | None = None,
    before: int = 0,
    after: int = 0,
    list_style: bool = False,
) -> None:
    for existing in styles.findall(f"{W}style"):
        if existing.get(f"{W}styleId") == style_id:
            styles.remove(existing)
            break
    attributes = {"type": "paragraph", "styleId": style_id}
    if default:
        attributes["default"] = "1"
    style = _element("style", **attributes)
    _append(style, "name", val=name)
    if based_on:
        _append(style, "basedOn", val=based_on)
    if next_style:
        _append(style, "next", val=next_style)
    _append(style, "qFormat")

    paragraph_properties = _append(style, "pPr")
    if heading_level is not None:
        _append(paragraph_properties, "keepNext")
        _append(paragraph_properties, "keepLines")
    _append(
        paragraph_properties,
        "spacing",
        before=str(before),
        after=str(after),
        line="240",
        lineRule="auto",
    )
    if heading_level is not None:
        _append(paragraph_properties, "outlineLvl", val=str(heading_level))
    if list_style:
        _append(paragraph_properties, "ind", left="720", hanging="360")
        _append(paragraph_properties, "contextualSpacing")

    run_properties = _append(style, "rPr")
    font = HEADING_FONT if heading_level is not None else BODY_FONT
    size = "32" if heading_level is not None else "20"
    _append(run_properties, "rFonts", ascii=font, hAnsi=font, cs=font)
    if heading_level is not None:
        _append(run_properties, "color", val=HEADING_COLOR)
    _append(run_properties, "sz", val=size)
    _append(run_properties, "szCs", val=size)
    styles.append(style)


def _presentation_styles(styles_xml: bytes) -> bytes:
    styles = ElementTree.fromstring(styles_xml)
    _set_style(styles, "Normal", name="Normal", default=True)
    _set_style(
        styles,
        "Heading1",
        name="heading 1",
        based_on="Normal",
        next_style="Normal",
        heading_level=0,
        before=240,
    )
    _set_style(
        styles,
        "Heading2",
        name="heading 2",
        based_on="Normal",
        next_style="Normal",
        heading_level=1,
        before=160,
        after=80,
    )
    _set_style(
        styles,
        "ListParagraph",
        name="List Paragraph",
        based_on="Normal",
        list_style=True,
    )
    return ElementTree.tostring(styles, encoding="utf-8", xml_declaration=True)


def _section(
    title: str,
    content: list[str],
    *,
    numbered: bool = False,
) -> list[ElementTree.Element]:
    if not content:
        return []
    elements = [_heading(title)]
    elements.extend(
        _list_items(content)
        if numbered
        else [_paragraph(value) for value in content]
    )
    return elements


def render_administrative_docx(
    template_path: Path,
    course: dict[str, Any],
    week: dict[str, Any],
    lesson: dict[str, Any],
) -> bytes:
    """Render one J-Tech plan using the official blank form as its package base."""

    try:
        template_bytes = template_path.read_bytes()
    except FileNotFoundError as exc:
        raise ValueError(
            f"Administrative Lesson Plan template not found: {template_path}"
        ) from exc

    with zipfile.ZipFile(io.BytesIO(template_bytes)) as template:
        required_parts = {
            "word/document.xml",
            "word/styles.xml",
        }
        missing = required_parts - set(template.namelist())
        if missing:
            raise ValueError(
                "Administrative Lesson Plan template is missing: "
                + ", ".join(sorted(missing))
            )

        document = ElementTree.fromstring(template.read("word/document.xml"))
        body = document.find(f"{W}body")
        if body is None:
            raise ValueError("Administrative Lesson Plan template has no body")
        section_properties = body.find(f"{W}sectPr")
        if section_properties is None:
            raise ValueError(
                "Administrative Lesson Plan template has no section properties"
            )
        section_properties = copy.deepcopy(section_properties)
        for child in list(body):
            body.remove(child)

        objectives = {item["id"]: item for item in week["objectives"]}
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
        assessments = {
            item["id"]: item for item in week["assessments"]
        }

        title = (
            f"{course['title']} – Week {week['week_number']} Day "
            f"{lesson['day_number']} Administrative Lesson Plan"
        )
        elements: list[ElementTree.Element] = [
            _heading(title, level=1),
            _paragraph(lesson["title"]),
        ]
        if lesson.get("duration"):
            elements.append(
                _paragraph(f"Time: {_time_text(lesson['duration'])}")
            )
        elements.extend(
            [
                _paragraph(),
                _heading("Configuration Board"),
                _configuration_table(
                    list(
                        zip(
                            CONFIGURATION_LABELS,
                            (
                                activities["warm_up"][0],
                                objective_text,
                                standard_text,
                                lesson["essential_question"],
                                activities["exit"][0],
                            ),
                        )
                    )
                ),
                _paragraph(),
            ]
        )

        sections = [
            ("Objectives", [lesson["objective_summary"]], False),
            (
                "Necessary Materials",
                [_sentence_list(lesson.get("materials", []))],
                False,
            ),
            (
                "Terminology",
                [_sentence_list(lesson.get("terminology", []))],
                False,
            ),
            ("Academic Activities", activities["academic"], True),
            ("Shop Activities", activities["shop"], True),
            (
                "Industry Applications",
                [lesson["industry_applications"]]
                if lesson.get("industry_applications")
                else [],
                False,
            ),
            (
                "Common Technician Errors",
                lesson.get("common_technician_errors", []),
                True,
            ),
            (
                "Captain Joe's Shop Tip",
                [lesson["instructor_shop_tip"]]
                if lesson.get("instructor_shop_tip")
                else [],
                False,
            ),
            (
                "Assessment",
                [
                    assessments[assessment_id]["description"]
                    for assessment_id in lesson["assessment_ids"]
                    if assessments[assessment_id].get("description")
                ],
                False,
            ),
            (
                "Homework",
                [lesson["homework"]] if lesson.get("homework") else [],
                False,
            ),
            (
                "Notes / Flex Activities",
                [lesson["flex_activities"]]
                if lesson.get("flex_activities")
                else [],
                False,
            ),
        ]
        for heading, content, numbered in sections:
            content = [value for value in content if value]
            elements.extend(_section(heading, content, numbered=numbered))

        elements.append(_heading("Instructor Reflection"))
        for index, prompt in enumerate(REFLECTION_PROMPTS):
            elements.append(_paragraph(prompt))
            if index < len(REFLECTION_PROMPTS) - 1:
                elements.append(_paragraph())

        for element in elements:
            body.append(element)

        section_type = section_properties.find(f"{W}type")
        if section_type is not None:
            section_properties.remove(section_type)
        margins = section_properties.find(f"{W}pgMar")
        if margins is None:
            margins = _append(section_properties, "pgMar")
        for edge in ("top", "right", "bottom", "left"):
            margins.set(f"{W}{edge}", "1440")
        margins.set(f"{W}header", "720")
        margins.set(f"{W}footer", "720")
        body.append(section_properties)

        rendered_xml = ElementTree.tostring(
            document,
            encoding="utf-8",
            xml_declaration=True,
        )
        rendered_styles = _presentation_styles(template.read("word/styles.xml"))

        result = io.BytesIO()
        with zipfile.ZipFile(result, "w") as output:
            for item in template.infolist():
                if item.filename == "word/document.xml":
                    content = rendered_xml
                elif item.filename == "word/styles.xml":
                    content = rendered_styles
                else:
                    content = template.read(item.filename)
                output.writestr(item, content)
    return result.getvalue()
