from __future__ import annotations

import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

from teos import BuildConfig, BuildError, build
from teos.cli import main


pytestmark = [pytest.mark.end_to_end, pytest.mark.regression]

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = REPOSITORY_ROOT / "examples" / "reference_curriculum"
SCHEMA_ROOT = REPOSITORY_ROOT / "schemas"


def config(output: Path, **changes: object) -> BuildConfig:
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


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def assert_complete_output(output: Path) -> dict[str, object]:
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pipeline_result"] == "success"
    assert manifest["artifact_count"] == 96
    assert {item["format"] for item in manifest["artifacts"]} == {
        "markdown",
        "html",
        "docx",
        "pdf",
    }
    assert {item["artifact_type"] for item in manifest["artifacts"]} == {
        "administrative",
        "instructor",
        "lab",
    }
    for item in manifest["artifacts"]:
        path = output / item["output_path"]
        assert path.is_file()
        assert path.stat().st_size > 0
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["content_hash"]
        assert path.is_relative_to(output)
    sample_docx = next((output / "artifacts" / "docx").glob("*.docx"))
    with zipfile.ZipFile(sample_docx) as archive:
        assert archive.testzip() is None
        ET.fromstring(archive.read("word/document.xml"))
    sample_pdf = next((output / "artifacts" / "pdf").glob("*.pdf")).read_bytes()
    assert sample_pdf.startswith(b"%PDF-1.4")
    assert sample_pdf.endswith(b"%%EOF\n")
    sample_html = next((output / "artifacts" / "html").glob("*.html"))
    assert "<!doctype html>" in sample_html.read_text(encoding="utf-8")
    return manifest


def test_complete_successful_cli_build(tmp_path: Path) -> None:
    output = tmp_path / "cli"
    exit_code = main(
        [
            "build",
            "--repository",
            str(REFERENCE_ROOT),
            "--schemas",
            str(SCHEMA_ROOT),
            "--institution",
            "north-valley-community-college",
            "--calendar",
            "fall-2026-semester",
            "--meeting-pattern",
            "monday-wednesday-evening",
            "--locale",
            "en-US",
            "--theme",
            "institution-branded",
            "--renderers",
            "all",
            "--generators",
            "all",
            "--output",
            str(output),
        ]
    )
    assert exit_code == 0
    manifest = assert_complete_output(output)
    schedule = json.loads((output / "schedule.json").read_text(encoding="utf-8"))
    assert [item["session_number"] for item in schedule["assignments"]] == list(
        range(1, 9)
    )
    assert manifest["institution_id"] == "north-valley-community-college"


def test_complete_successful_api_build(tmp_path: Path) -> None:
    result = build(config(tmp_path / "api"))
    assert result.build_id
    assert result.manifest_path.is_file()
    assert len(result.artifact_paths) == 96
    assert result.compilation_summary == {
        "course_id": "tec101",
        "schema_version": "2.0",
        "unit_ids": ["unit.safe-measurement", "unit.circuit-diagnosis"],
        "session_ids": [f"session.{number}" for number in range(1, 9)],
        "session_count": 8,
        "total_minutes": 720,
        "dependency_edges": [],
        "dependency_graph_acyclic": True,
    }
    assert_complete_output(tmp_path / "api")


def test_alternate_institution_calendar_locale_and_theme(tmp_path: Path) -> None:
    output = tmp_path / "alternate"
    result = build(
        config(
            output,
            institution_id="metro-trade-institute",
            calendar_id="accelerated-8-week",
            meeting_pattern_id="tuesday-thursday-day",
            locale="es-US",
            theme="dark",
        )
    )
    assert [item["date"] for item in result.schedule["assignments"]] == [
        "2026-10-20",
        "2026-10-22",
        "2026-10-27",
        "2026-11-03",
        "2026-11-05",
        "2026-11-10",
        "2026-11-12",
        "2026-11-17",
    ]
    rendered = json.loads(
        (output / "rendered/session-001-administrative.json").read_text(
            encoding="utf-8"
        )
    )
    assert rendered["locale"] == "es-US"
    assert rendered["theme"] == "dark"
    assert rendered["content"].startswith("# Plan de lección administrativo\n")
    html = next((output / "artifacts/html").glob("*.html")).read_text(
        encoding="utf-8"
    )
    assert '<html lang="es-US">' in html
    assert "background:#111827" in html


def test_repeated_builds_are_byte_deterministic_and_cli_api_equivalent(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    api_result = build(config(first))
    assert (
        main(
            [
                "build",
                "--repository",
                str(REFERENCE_ROOT),
                "--schemas",
                str(SCHEMA_ROOT),
                "--institution",
                "north-valley-community-college",
                "--calendar",
                "fall-2026-semester",
                "--meeting-pattern",
                "monday-wednesday-evening",
                "--locale",
                "en-US",
                "--theme",
                "institution-branded",
                "--output",
                str(second),
            ]
        )
        == 0
    )
    assert api_result.build_id == json.loads(
        (second / "manifest.json").read_text(encoding="utf-8")
    )["build_id"]
    first_files = {
        path.relative_to(first): path.read_bytes()
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        path.relative_to(second): path.read_bytes()
        for path in second.rglob("*")
        if path.is_file()
    }
    assert first_files == second_files


@pytest.mark.parametrize(
    ("change", "diagnostic"),
    [
        ({"repository": Path("/definitely/missing/teos-reference")}, "not found"),
        ({"institution_id": "missing-institution"}, "institution"),
        ({"calendar_id": "missing-calendar"}, "calendar"),
        ({"locale": "xx-XX"}, "locale"),
        ({"theme": "missing-theme"}, "theme"),
        ({"renderers": ("missing-renderer",)}, "renderer"),
        ({"generators": ("missing-generator",)}, "generator"),
    ],
)
def test_controlled_configuration_failures(
    tmp_path: Path,
    change: dict[str, object],
    diagnostic: str,
) -> None:
    output = tmp_path / "failed"
    with pytest.raises(BuildError, match=diagnostic):
        build(config(output, **change))
    assert not output.exists()


def test_malformed_source_and_unresolved_reference_fail_without_outputs(
    tmp_path: Path,
) -> None:
    malformed_repository = tmp_path / "malformed-reference"
    shutil.copytree(REFERENCE_ROOT, malformed_repository)
    course_path = malformed_repository / "curriculum/course.json"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    del course["title"]
    course_path.write_text(json.dumps(course), encoding="utf-8")
    malformed_output = tmp_path / "malformed-output"
    with pytest.raises(BuildError, match="schema validation failed"):
        build(
            config(
                malformed_output,
                repository=malformed_repository,
            )
        )
    assert not malformed_output.exists()

    unresolved_repository = tmp_path / "unresolved-reference"
    shutil.copytree(REFERENCE_ROOT, unresolved_repository)
    unit_path = (
        unresolved_repository
        / "curriculum/units/safe-measurement.json"
    )
    unit = json.loads(unit_path.read_text(encoding="utf-8"))
    unit["competency_ids"].append("comp.missing")
    unit_path.write_text(json.dumps(unit), encoding="utf-8")
    unresolved_output = tmp_path / "unresolved-output"
    with pytest.raises(BuildError, match="unknown competencies"):
        build(
            config(
                unresolved_output,
                repository=unresolved_repository,
            )
        )
    assert not unresolved_output.exists()


def test_unwritable_output_target_is_controlled(tmp_path: Path) -> None:
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("file", encoding="utf-8")
    with pytest.raises(BuildError, match="cannot create output directory"):
        build(config(blocked_parent / "output"))


def test_cli_failure_is_nonzero_useful_and_has_no_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "failed-cli"
    assert (
        main(
            [
                "build",
                "--repository",
                str(tmp_path / "missing"),
                "--schemas",
                str(SCHEMA_ROOT),
                "--institution",
                "north-valley-community-college",
                "--calendar",
                "fall-2026-semester",
                "--meeting-pattern",
                "monday-wednesday-evening",
                "--locale",
                "en-US",
                "--theme",
                "institution-branded",
                "--output",
                str(output),
            ]
        )
        == 2
    )
    captured = capsys.readouterr()
    assert captured.err.startswith("Error:")
    assert "Traceback" not in captured.err
    assert not output.exists()


def test_source_tree_is_unchanged_and_outputs_are_isolated(tmp_path: Path) -> None:
    before = tree_hash(REFERENCE_ROOT)
    successful = tmp_path / "successful"
    build(config(successful))
    with pytest.raises(BuildError):
        build(config(successful))
    failed = tmp_path / "failed"
    with pytest.raises(BuildError):
        build(config(failed, locale="unsupported"))
    assert tree_hash(REFERENCE_ROOT) == before
    assert (successful / "manifest.json").is_file()
    assert not failed.exists()
