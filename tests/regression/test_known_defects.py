from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from teos import BuildError, build

pytestmark = pytest.mark.regression


def test_complete_interface_localization_not_only_document_title(
    tmp_path: Path,
    build_config,
) -> None:
    output = tmp_path / "localized"
    build(
        build_config(
            output,
            locale="es-US",
            renderers=("administrative",),
            generators=("markdown",),
        )
    )
    content = next((output / "artifacts/markdown").glob("*.md")).read_text(
        encoding="utf-8"
    )
    assert "## Objetivos" in content
    assert "- Curso:" in content
    assert "- Duración:" in content
    assert "## Objectives" not in content


def test_long_pdf_lines_are_wrapped_without_truncating_tail(
    tmp_path: Path,
    build_config,
) -> None:
    output = tmp_path / "pdf"
    build(
        build_config(
            output,
            renderers=("administrative",),
            generators=("pdf",),
        )
    )
    content = (
        output
        / "artifacts/pdf/tec101-session-001-administrative.pdf"
    ).read_bytes()
    strings = re.findall(rb"\(((?:\\.|[^\\)])*)\) Tj", content)
    extracted = b" ".join(strings).decode("cp1252")
    assert "connection method." in extracted


def test_artifact_traceability_metadata_survives_every_boundary(
    tmp_path: Path,
    build_config,
) -> None:
    output = tmp_path / "traceability"
    result = build(
        build_config(
            output,
            renderers=("lab",),
            generators=("markdown",),
        )
    )
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    rendered = json.loads(
        (output / "rendered/session-001-lab.json").read_text(encoding="utf-8")
    )
    artifact = manifest["artifacts"][0]
    for key in (
        "build_id",
        "curriculum_revision",
        "course_id",
        "curriculum_version",
        "session_id",
        "session_number",
        "schedule_id",
        "institution_id",
        "locale",
        "theme",
    ):
        expected = manifest[key] if key in manifest else artifact[key]
        assert rendered[key] == expected
        if key in artifact:
            assert artifact[key] == expected


def test_failed_generation_leaves_no_partial_output(
    tmp_path: Path,
    build_config,
) -> None:
    output = tmp_path / "missing-generator"
    with pytest.raises(BuildError, match="generator"):
        build(build_config(output, generators=("not-installed",)))
    assert not output.exists()
