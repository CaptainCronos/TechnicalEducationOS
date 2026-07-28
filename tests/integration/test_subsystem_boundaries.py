from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from teos import BuildResult, build
from teos.generators import GENERATORS
from teos.records import load_curriculum, validate_curriculum
from teos.scheduler import schedule_sessions
from teos.session_render import SESSION_RENDERERS


pytestmark = pytest.mark.integration


def test_load_validate_compile_schedule_render_generate_boundary(
    reference_root: Path,
    reference_curriculum: tuple[dict, list[dict], list[dict]],
    community_profile: dict,
    community_calendar: dict,
) -> None:
    loaded = load_curriculum(reference_root / "curriculum")
    assert loaded == reference_curriculum
    course, units, sessions = loaded
    validate_curriculum(course, units, sessions)
    schedule = schedule_sessions(
        course,
        sessions,
        community_profile,
        community_calendar,
        "monday-wednesday-evening",
    )
    assignment = schedule["assignments"][0]
    session = next(
        item for item in sessions if item["id"] == assignment["session_id"]
    )
    unit = next(item for item in units if item["id"] == assignment["unit_id"])
    rendered = SESSION_RENDERERS["administrative"](
        course, unit, session, community_profile
    )
    extension, generator = GENERATORS["html"]
    physical = generator(
        rendered,
        {
            "tokens": {
                "background": "#fff",
                "foreground": "#000",
                "accent": "#06c",
                "font_family": "sans-serif",
            },
            "_locale": "en-US",
        },
    )
    assert extension == ".html"
    assert session["title"] in rendered
    assert community_profile["institution_name"] in rendered
    assert rendered.encode("utf-8").replace(b"&", b"&amp;")[:30] in physical


def test_public_api_returns_detached_summary_and_complete_manifest(
    tmp_path: Path,
    build_config,
) -> None:
    result = build(
        build_config(
            tmp_path / "api-boundary",
            renderers=("administrative",),
            generators=("markdown",),
        )
    )
    assert isinstance(result, BuildResult)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_count"] == 8
    assert len(result.artifact_paths) == manifest["artifact_count"]
    result.compilation_summary["session_ids"].clear()
    persisted = json.loads(
        (tmp_path / "api-boundary" / "compiled-curriculum.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(persisted["session_ids"]) == 8


@pytest.mark.parametrize(
    ("locale", "theme", "expected_title", "expected_background"),
    [
        ("en-US", "default", "# Administrative Lesson Plan", "#ffffff"),
        ("es-US", "dark", "# Plan de lección administrativo", "#111827"),
    ],
)
def test_localization_theme_and_generator_interoperate(
    tmp_path: Path,
    build_config,
    locale: str,
    theme: str,
    expected_title: str,
    expected_background: str,
) -> None:
    output = tmp_path / f"{locale}-{theme}"
    build(
        build_config(
            output,
            locale=locale,
            theme=theme,
            renderers=("administrative",),
            generators=("html",),
        )
    )
    rendered = json.loads(
        (output / "rendered/session-001-administrative.json").read_text(
            encoding="utf-8"
        )
    )
    html = next((output / "artifacts/html").glob("*.html")).read_text(
        encoding="utf-8"
    )
    assert rendered["content"].startswith(expected_title)
    assert f'<html lang="{locale}">' in html
    assert f"background:{expected_background}" in html


def test_empty_components_and_optional_assessments_cross_validation_rendering(
    reference_curriculum: tuple[dict, list[dict], list[dict]],
    community_profile: dict,
) -> None:
    course, units, sessions = deepcopy(reference_curriculum)
    unit = units[0]
    unit["lectures"] = []
    unit["demonstrations"] = []
    unit["labs"] = []
    unit["assessments"] = []
    for session in sessions:
        if session["unit_id"] == unit["id"]:
            session.setdefault("instruction", {})["assessment_ids"] = []
    validate_curriculum(course, units, sessions)
    session = next(item for item in sessions if item["unit_id"] == unit["id"])
    administrative = SESSION_RENDERERS["administrative"](
        course, unit, session, community_profile
    )
    lab = SESSION_RENDERERS["lab"](course, unit, session, community_profile)
    assert "None recorded." in administrative
    assert "No lab is assigned to this session." in lab


def test_scheduler_accepts_alternate_calendar_without_mutating_curriculum(
    reference_curriculum: tuple[dict, list[dict], list[dict]],
    reference_root: Path,
) -> None:
    course, _, sessions = reference_curriculum
    original = deepcopy(sessions)
    profile = json.loads(
        (
            reference_root / "institutions/trade-school/institution.json"
        ).read_text(encoding="utf-8")
    )
    calendar = json.loads(
        (
            reference_root
            / "institutions/trade-school/calendars/accelerated-8-week.json"
        ).read_text(encoding="utf-8")
    )
    schedule = schedule_sessions(
        course, sessions, profile, calendar, "tuesday-thursday-day"
    )
    assert schedule["completion_date"] == "2026-11-17"
    assert sessions == original

