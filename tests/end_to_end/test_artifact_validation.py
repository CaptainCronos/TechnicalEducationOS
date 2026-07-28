from __future__ import annotations

import hashlib
import html.parser
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterator

import pytest

from teos import BuildConfig, build
from teos.generators import GENERATORS
from teos.records import load_curriculum
from teos.session_render import SESSION_RENDERERS


pytestmark = [pytest.mark.end_to_end, pytest.mark.regression]

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = REPOSITORY_ROOT / "examples" / "reference_curriculum"
SCHEMA_ROOT = REPOSITORY_ROOT / "schemas"
SNAPSHOT_PATH = (
    REPOSITORY_ROOT / "tests" / "snapshots" / "reference_artifacts.json"
)
ARTIFACT_TYPES = ("administrative", "instructor", "lab")
FORMATS = ("markdown", "html", "docx", "pdf")
EXPECTED_SECTIONS = {
    "administrative": (
        "Objectives",
        "Essential Question",
        "Materials",
        "Warm Up",
        "Academic Activities",
        "Shop Activities",
        "Exit",
        "Assessment",
    ),
    "instructor": (
        "Preparation",
        "Teaching Sequence",
        "Common Technician Errors",
        "Instructor Shop Tip",
        "Flex Activities",
    ),
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _config(output: Path, **changes: object) -> BuildConfig:
    values: dict[str, object] = {
        "repository": REFERENCE_ROOT,
        "schema_directory": SCHEMA_ROOT,
        "institution_id": "north-valley-community-college",
        "calendar_id": "fall-2026-semester",
        "meeting_pattern_id": "monday-wednesday-evening",
        "locale": "en-US",
        "theme": "institution-branded",
        "output_directory": output,
    }
    values.update(changes)
    return BuildConfig(**values)  # type: ignore[arg-type]


@pytest.fixture(scope="module")
def reference_output(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("artifact-validation") / "reference"
    build(_config(output))
    return output


@pytest.fixture(scope="module")
def curriculum() -> tuple[
    dict[str, object],
    dict[str, dict[str, object]],
    dict[str, dict[str, object]],
]:
    course, units, sessions = load_curriculum(REFERENCE_ROOT / "curriculum")
    return (
        course,
        {unit["id"]: unit for unit in units},
        {session["id"]: session for session in sessions},
    )


def _rendered_records(output: Path) -> Iterator[dict[str, object]]:
    for path in sorted((output / "rendered").glob("*.json")):
        yield _json(path)


def _normalize(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").splitlines()]
    return "\n".join(lines).strip() + "\n"


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", _normalize(text), flags=re.UNICODE)


class _BodyParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del attrs
        if tag == "body":
            self.in_body = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "body":
            self.in_body = False

    def handle_data(self, data: str) -> None:
        if self.in_body:
            self.parts.append(data)


def _pdf_text(content: bytes) -> str:
    strings = re.findall(rb"\(((?:\\.|[^\\)])*)\) Tj", content)
    lines = []
    for value in strings:
        value = value.replace(b"\\(", b"(").replace(b"\\)", b")")
        value = value.replace(b"\\\\", b"\\")
        lines.append(value.decode("cp1252"))
    return "\n".join(lines)


def _physical_text(path: Path, artifact_format: str) -> str:
    if artifact_format == "markdown":
        return path.read_text(encoding="utf-8")
    if artifact_format == "html":
        parser = _BodyParser()
        parser.feed(path.read_text(encoding="utf-8"))
        return "".join(parser.parts)
    if artifact_format == "docx":
        with zipfile.ZipFile(path) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
        namespace = (
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        )
        paragraphs = [
            "".join(node.text or "" for node in paragraph.iter(f"{namespace}t"))
            for paragraph in document.iter(f"{namespace}p")
        ]
        return "\n".join(paragraphs) + "\n"
    if artifact_format == "pdf":
        return _pdf_text(path.read_bytes())
    raise AssertionError(f"unexpected format: {artifact_format}")


def _headings(content: str, level: int = 2) -> list[str]:
    marker = "#" * level
    return [
        line[len(marker) + 1 :]
        for line in content.splitlines()
        if line.startswith(f"{marker} ") and not line.startswith(f"{marker}#")
    ]


def _section(content: str, heading: str, level: int = 2) -> list[str]:
    lines = content.splitlines()
    marker = f"{'#' * level} {heading}"
    start = lines.index(marker) + 1
    stop = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= level:
            stop = index
            break
    return [line for line in lines[start:stop] if line]


def _ordered(values: list[str]) -> list[str]:
    return [f"{index}. {value}" for index, value in enumerate(values, 1)]


def _unordered(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values] if values else ["None recorded."]


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def test_artifact_inventory_and_output_integrity(reference_output: Path) -> None:
    manifest = _json(reference_output / "manifest.json")
    entries = manifest["artifacts"]
    assert isinstance(entries, list)
    assert set(SESSION_RENDERERS) == set(ARTIFACT_TYPES)
    assert set(GENERATORS) == set(FORMATS)
    assert manifest["artifact_count"] == 96 == len(entries)
    assert Counter(entry["artifact_type"] for entry in entries) == {
        artifact_type: 32 for artifact_type in ARTIFACT_TYPES
    }
    assert Counter(entry["format"] for entry in entries) == {
        artifact_format: 24 for artifact_format in FORMATS
    }
    assert Counter(
        (entry["artifact_type"], entry["format"]) for entry in entries
    ) == {
        (artifact_type, artifact_format): 8
        for artifact_type in ARTIFACT_TYPES
        for artifact_format in FORMATS
    }
    assert len(list((reference_output / "rendered").glob("*.json"))) == 24

    expected_paths = {
        Path(entry["output_path"])
        for entry in entries
    }
    actual_paths = {
        path.relative_to(reference_output)
        for path in (reference_output / "artifacts").rglob("*")
        if path.is_file()
    }
    assert actual_paths == expected_paths
    filename = re.compile(
        r"^tec101-session-\d{3}-(administrative|instructor|lab)"
        r"\.(md|html|docx|pdf)$"
    )
    for entry in entries:
        path = reference_output / entry["output_path"]
        assert path.is_relative_to(reference_output / "artifacts")
        assert filename.fullmatch(path.name)
        assert path.suffix == GENERATORS[entry["generator"]][0]
        assert 20 < path.stat().st_size < 5_000_000
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["content_hash"]


def test_structural_and_content_validation(
    reference_output: Path,
    curriculum: tuple[
        dict[str, object],
        dict[str, dict[str, object]],
        dict[str, dict[str, object]],
    ],
) -> None:
    course, units, sessions = curriculum
    for record in _rendered_records(reference_output):
        artifact_type = record["artifact_type"]
        content = record["content"]
        assert isinstance(artifact_type, str)
        assert isinstance(content, str)
        session = sessions[record["session_id"]]
        unit = units[record["unit_id"]]
        instruction = session.get("instruction", {})
        assert isinstance(instruction, dict)

        headings = _headings(content)
        assert len(headings) == len(set(headings))
        if artifact_type in EXPECTED_SECTIONS:
            assert tuple(headings) == EXPECTED_SECTIONS[artifact_type]

        if artifact_type == "administrative":
            objectives = {
                objective["id"]: objective
                for objective in unit["objectives"]
            }
            expected_objectives = [
                f"- **{objective_id}** — {objectives[objective_id]['statement']}"
                for objective_id in session["objective_ids"]
            ]
            assert _section(content, "Objectives") == expected_objectives
            materials = instruction.get("materials", unit["required_resources"])
            assert _section(content, "Materials") == _unordered(materials)
            activities = instruction.get("activities", [])
            for heading, category in (
                ("Warm Up", "warm_up"),
                ("Academic Activities", "academic"),
                ("Shop Activities", "shop"),
                ("Exit", "exit"),
            ):
                expected = [
                    item["description"]
                    for item in activities
                    if item["category"] == category
                ]
                assert _section(content, heading) == (
                    _ordered(expected) if expected else ["None recorded."]
                )
            assessments = {
                assessment["id"]: assessment
                for assessment in unit["assessments"]
            }
            expected_assessments = [
                assessments[assessment_id].get(
                    "description", assessments[assessment_id]["title"]
                )
                for assessment_id in instruction.get("assessment_ids", [])
            ]
            assert _section(content, "Assessment") == _unordered(
                expected_assessments
            )

        elif artifact_type == "instructor":
            preparation = instruction.get(
                "preparation", unit.get("preparation", [])
            )
            assert _section(content, "Preparation") == _unordered(preparation)
            teaching = [
                item["description"]
                for item in instruction.get("activities", [])
                if item["category"] in {"academic", "shop"}
            ]
            assert _section(content, "Teaching Sequence") == (
                _ordered(teaching) if teaching else ["None recorded."]
            )
            assert _section(content, "Common Technician Errors") == _unordered(
                instruction.get("common_technician_errors", [])
            )
            assert _section(content, "Instructor Shop Tip") == [
                instruction.get("instructor_shop_tip", "None recorded.")
            ]
            assert _section(content, "Flex Activities") == [
                instruction.get("flex_activities", "None recorded.")
            ]

        else:
            objective_ids = set(session["objective_ids"])
            labs = [
                lab
                for lab in unit["labs"]
                if objective_ids.intersection(lab["objective_ids"])
            ]
            assert headings == [lab["title"] for lab in labs]
            if not labs:
                assert content.rstrip().endswith(
                    "No lab is assigned to this session."
                )
            for lab in labs:
                block = "\n".join(_section(content, lab["title"]))
                assert _headings(block, 3) == [
                    "Procedure",
                    "Deliverables",
                    "Safety",
                ]
                assert _section(block, "Procedure", 3) == _ordered(
                    lab["procedure"]
                )
                assert _section(block, "Deliverables", 3) == _unordered(
                    lab["deliverables"]
                )
                assert _section(block, "Safety", 3) == _unordered(
                    lab["safety_notes"]
                )

        assert record["course_id"] == course["course_id"]
        assert record["unit_id"] == session["unit_id"]


def test_cross_document_consistency(reference_output: Path) -> None:
    records = list(_rendered_records(reference_output))
    by_session: dict[str, list[dict[str, object]]] = {}
    for record in records:
        by_session.setdefault(record["session_id"], []).append(record)
    assert len(by_session) == 8
    for session_records in by_session.values():
        assert {record["artifact_type"] for record in session_records} == set(
            ARTIFACT_TYPES
        )
        shared_fields = (
            "build_id",
            "curriculum_revision",
            "curriculum_version",
            "course_id",
            "unit_id",
            "session_id",
            "session_number",
            "schedule_id",
            "institution_id",
            "locale",
            "theme",
        )
        for field in shared_fields:
            assert len({record[field] for record in session_records}) == 1
        contexts = []
        for record in session_records:
            content = str(record["content"])
            contexts.append(
                tuple(
                    line
                    for line in content.splitlines()
                    if line.startswith(
                        (
                            "- Course:",
                            "- Session:",
                            "- Instructional unit:",
                            "- Phase:",
                            "- Duration:",
                            "- Institution:",
                        )
                    )
                )
            )
        assert contexts[0] == contexts[1] == contexts[2]


def test_every_physical_format_preserves_rendered_content(
    reference_output: Path,
) -> None:
    manifest = _json(reference_output / "manifest.json")
    rendered = {
        (record["session_id"], record["artifact_type"]): record["content"]
        for record in _rendered_records(reference_output)
    }
    for entry in manifest["artifacts"]:
        expected = rendered[(entry["session_id"], entry["artifact_type"])]
        actual = _physical_text(
            reference_output / entry["output_path"], entry["format"]
        )
        if entry["format"] == "pdf":
            assert _tokens(actual) == _tokens(expected)
        else:
            assert _normalize(actual) == _normalize(expected)


def test_formatting_and_parser_contracts(reference_output: Path) -> None:
    manifest = _json(reference_output / "manifest.json")
    for entry in manifest["artifacts"]:
        path = reference_output / entry["output_path"]
        content = path.read_bytes()
        if entry["format"] == "markdown":
            text = content.decode("utf-8")
            assert text.startswith("# ")
            assert "\t" not in text
        elif entry["format"] == "html":
            text = content.decode("utf-8")
            assert text.startswith("<!doctype html>")
            assert '<meta charset="utf-8">' in text
            assert "white-space:pre-wrap" in text
            assert "font-family:Georgia, serif" in text
            assert "background:#ffffff" in text
            assert "color:#17324d" in text
        elif entry["format"] == "docx":
            with zipfile.ZipFile(path) as archive:
                assert archive.testzip() is None
                assert set(archive.namelist()) == {
                    "[Content_Types].xml",
                    "_rels/.rels",
                    "word/document.xml",
                }
                ET.fromstring(archive.read("[Content_Types].xml"))
                ET.fromstring(archive.read("_rels/.rels"))
                ET.fromstring(archive.read("word/document.xml"))
        else:
            assert content.startswith(b"%PDF-1.4")
            assert content.endswith(b"%%EOF\n")
            assert b"/MediaBox [0 0 612 792]" in content
            assert b"/BaseFont /Helvetica" in content
            assert re.search(rb"xref\n0 \d+\n", content)


def test_metadata_and_revision_traceability(
    reference_output: Path,
    curriculum: tuple[
        dict[str, object],
        dict[str, dict[str, object]],
        dict[str, dict[str, object]],
    ],
) -> None:
    course, units, sessions = curriculum
    manifest = _json(reference_output / "manifest.json")
    session_plan = _json(
        REFERENCE_ROOT / "curriculum" / "sessions.json"
    )
    unit_records = [
        _json(path)
        for path in sorted((REFERENCE_ROOT / "curriculum" / "units").glob("*.json"))
    ]
    revision = hashlib.sha256(
        _canonical_json([course, *unit_records, session_plan]).encode("utf-8")
    ).hexdigest()
    assert manifest["manifest_version"] == "1.0"
    assert manifest["curriculum_version"] == course["schema_version"] == "2.0"
    assert manifest["curriculum_revision"] == revision
    assert manifest["source_curriculum_id"] == course["course_id"] == "tec101"
    assert manifest["institution_id"] == "north-valley-community-college"
    assert manifest["locale"] == "en-US"
    assert manifest["theme"] == "institution-branded"
    assert re.fullmatch(r"[0-9a-f]{64}", manifest["build_id"])
    assert "generation_timestamp" not in manifest

    source_hashes = manifest["source_hashes"]
    for relative, expected_hash in source_hashes.items():
        source = REFERENCE_ROOT / relative
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash

    artifact_ids = set()
    for entry in manifest["artifacts"]:
        artifact_ids.add(entry["artifact_id"])
        session = sessions[entry["session_id"]]
        assert entry["course_id"] == course["course_id"]
        assert entry["unit_id"] == session["unit_id"]
        assert entry["curriculum_version"] == course["schema_version"]
        assert entry["curriculum_revision"] == revision
        assert entry["institution_id"] == manifest["institution_id"]
        assert entry["locale"] == manifest["locale"]
        assert entry["theme"] == manifest["theme"]
        assert entry["pipeline_result"] == "success"
    assert len(artifact_ids) == 96


def test_localized_interface_is_complete_and_source_meaning_is_preserved(
    tmp_path: Path,
    curriculum: tuple[
        dict[str, object],
        dict[str, dict[str, object]],
        dict[str, dict[str, object]],
    ],
) -> None:
    course, units, sessions = curriculum
    output = tmp_path / "spanish"
    build(_config(output, locale="es-US", generators=("markdown", "html")))
    english_catalog = _json(REFERENCE_ROOT / "locales" / "en-US.json")["strings"]
    spanish_catalog = _json(REFERENCE_ROOT / "locales" / "es-US.json")["strings"]
    assert set(english_catalog) == set(spanish_catalog)
    assert english_catalog.keys() >= {
        "label.objectives",
        "label.materials",
        "label.assessment",
        "label.procedure",
        "label.safety",
        "message.none_recorded",
    }
    for record in _rendered_records(output):
        content = record["content"]
        assert record["locale"] == "es-US"
        assert content.startswith(
            {
                "administrative": "# Plan de lección administrativo",
                "instructor": "# Guía del instructor",
                "lab": "# Hoja de laboratorio",
            }[record["artifact_type"]]
        )
        for english_heading in (
            "## Objectives",
            "## Materials",
            "## Assessment",
            "## Preparation",
            "## Teaching Sequence",
            "### Procedure",
            "### Deliverables",
            "### Safety",
        ):
            assert english_heading not in content
        session = sessions[record["session_id"]]
        unit = units[record["unit_id"]]
        assert course["title"] in content
        assert session["title"] in content
        assert unit["title"] in content
        if record["artifact_type"] == "administrative":
            objectives = {
                objective["id"]: objective["statement"]
                for objective in unit["objectives"]
            }
            for objective_id in session["objective_ids"]:
                assert objectives[objective_id] in content


def test_theme_changes_presentation_only(tmp_path: Path) -> None:
    default_output = tmp_path / "default"
    dark_output = tmp_path / "dark"
    build(_config(default_output, theme="default"))
    build(_config(dark_output, theme="dark"))
    default_records = {
        (record["session_id"], record["artifact_type"]): record["content"]
        for record in _rendered_records(default_output)
    }
    dark_records = {
        (record["session_id"], record["artifact_type"]): record["content"]
        for record in _rendered_records(dark_output)
    }
    assert default_records == dark_records

    for relative in sorted(
        path.relative_to(default_output / "artifacts")
        for path in (default_output / "artifacts").rglob("*")
        if path.is_file()
    ):
        default_path = default_output / "artifacts" / relative
        dark_path = dark_output / "artifacts" / relative
        artifact_format = relative.parts[0]
        assert _tokens(_physical_text(default_path, artifact_format)) == _tokens(
            _physical_text(dark_path, artifact_format)
        )
        if artifact_format != "html":
            assert default_path.read_bytes() == dark_path.read_bytes()

    default_html = next((default_output / "artifacts" / "html").glob("*.html"))
    dark_html = next((dark_output / "artifacts" / "html").glob("*.html"))
    assert "background:#ffffff" in default_html.read_text(encoding="utf-8")
    assert "font-family:system-ui, sans-serif" in default_html.read_text(
        encoding="utf-8"
    )
    assert "background:#111827" in dark_html.read_text(encoding="utf-8")
    assert "color:#f3f4f6" in dark_html.read_text(encoding="utf-8")


def test_normalized_reference_snapshot(reference_output: Path) -> None:
    expected = _json(SNAPSHOT_PATH)
    actual_hashes = {
        f"session-{record['session_number']:03d}-{record['artifact_type']}": (
            hashlib.sha256(_normalize(record["content"]).encode("utf-8")).hexdigest()
        )
        for record in _rendered_records(reference_output)
    }
    assert expected["snapshot_version"] == "1.0"
    assert expected["normalization"] == "LF line endings; trailing whitespace removed"
    assert expected["logical_artifact_count"] == 24
    assert expected["physical_artifact_count"] == 96
    assert expected["normalized_content_sha256"] == actual_hashes
