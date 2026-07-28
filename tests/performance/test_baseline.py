from __future__ import annotations

import statistics
from copy import deepcopy
from pathlib import Path
from time import perf_counter

import pytest

from teos import build
from teos.generators import GENERATORS
from teos.records import load_curriculum, load_json, validate_curriculum
from teos.scheduler import schedule_sessions
from teos.session_render import SESSION_RENDERERS

pytestmark = pytest.mark.performance


def _median_seconds(operation, repeats: int = 7) -> float:
    samples = []
    for _ in range(repeats):
        started = perf_counter()
        operation()
        samples.append(perf_counter() - started)
    return statistics.median(samples)


def test_representative_subsystem_timings(
    reference_root: Path,
    reference_curriculum: tuple[dict, list[dict], list[dict]],
    community_profile: dict,
    community_calendar: dict,
    request: pytest.FixtureRequest,
) -> None:
    course, units, sessions = reference_curriculum
    session = sessions[0]
    unit = next(item for item in units if item["id"] == session["unit_id"])
    rendered = SESSION_RENDERERS["administrative"](
        course, unit, session, community_profile
    )
    theme = load_json(reference_root / "themes/default.json")
    theme["_locale"] = "en-US"
    source_paths = [
        reference_root / "curriculum/course.json",
        *(reference_root / "curriculum/units").glob("*.json"),
        reference_root / "curriculum/sessions.json",
    ]
    measurements = {
        "loading": _median_seconds(
            lambda: [load_json(path) for path in source_paths]
        ),
        "validation": _median_seconds(
            lambda: validate_curriculum(
                deepcopy(course), deepcopy(units), deepcopy(sessions)
            )
        ),
        "compilation": _median_seconds(
            lambda: load_curriculum(reference_root / "curriculum")
        ),
        "scheduling": _median_seconds(
            lambda: schedule_sessions(
                course,
                sessions,
                community_profile,
                community_calendar,
                "monday-wednesday-evening",
            )
        ),
        "rendering": _median_seconds(
            lambda: [
                renderer(course, unit, session, community_profile)
                for renderer in SESSION_RENDERERS.values()
            ]
        ),
        "document_generation": _median_seconds(
            lambda: [
                generator(rendered, theme)
                for _, generator in GENERATORS.values()
            ]
        ),
    }
    for name, seconds in measurements.items():
        request.node.user_properties.append(
            (f"{name}_seconds", f"{seconds:.6f}")
        )
        print(f"{name}: {seconds:.6f} s")
        assert seconds < 1.0, f"{name} exceeded the 1 s regression guard"


def test_complete_reference_build_timing(
    tmp_path: Path,
    build_config,
    request: pytest.FixtureRequest,
) -> None:
    started = perf_counter()
    build(build_config(tmp_path / "performance-build"))
    seconds = perf_counter() - started
    request.node.user_properties.append(
        ("complete_build_seconds", f"{seconds:.6f}")
    )
    print(f"complete_build: {seconds:.6f} s")
    assert seconds < 5.0, "complete reference build exceeded the 5 s guard"
