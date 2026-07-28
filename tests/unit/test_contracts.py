from __future__ import annotations

import zipfile
from copy import deepcopy
from io import BytesIO

import pytest

from teos.generators import GENERATORS
from teos.records import RecordError, validate_course, validate_curriculum
from teos.session_render import SESSION_RENDERERS

pytestmark = pytest.mark.unit


def test_registered_renderers_and_generators_are_stable_contracts() -> None:
    assert tuple(SESSION_RENDERERS) == ("administrative", "instructor", "lab")
    assert tuple(GENERATORS) == ("markdown", "html", "docx", "pdf")


def test_generators_accept_empty_rendered_content() -> None:
    theme = {
        "tokens": {
            "background": "#fff",
            "foreground": "#000",
            "accent": "#00f",
            "font_family": "sans-serif",
        },
        "_locale": "en-US",
    }
    generated = {
        name: generator("", theme)
        for name, (_, generator) in GENERATORS.items()
    }
    assert generated["markdown"] == b""
    assert b"<html lang=\"en-US\">" in generated["html"]
    with zipfile.ZipFile(BytesIO(generated["docx"])) as archive:
        assert archive.testzip() is None
    assert generated["pdf"].endswith(b"%%EOF\n")


def test_large_competency_mapping_and_reused_standards_are_valid(
    reference_curriculum: tuple[dict, list[dict], list[dict]],
) -> None:
    course, _, _ = deepcopy(reference_curriculum)
    shared = [f"STANDARD.{index:04d}" for index in range(1_000)]
    course["standards"] = shared
    for competency in course["competencies"]:
        competency["standard_ids"] = list(shared)
    validate_course(course)
    assert course["competencies"][0]["standard_ids"] is not course["competencies"][1][
        "standard_ids"
    ]


def test_duplicate_identifier_has_contextual_diagnostic(
    reference_curriculum: tuple[dict, list[dict], list[dict]],
) -> None:
    course, units, sessions = deepcopy(reference_curriculum)
    units[0]["objectives"].append(deepcopy(units[0]["objectives"][0]))
    with pytest.raises(
        RecordError,
        match=r"duplicate ID .* in units\[0\]\.objectives",
    ):
        validate_curriculum(course, units, sessions)
