from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from teos import BuildError, build
from teos.records import RecordError, validate_curriculum
from teos.scheduler import schedule_sessions


pytestmark = pytest.mark.regression


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_malformed_repository_reports_source_path_and_json_error(
    tmp_path: Path,
    build_config,
    mutable_reference,
) -> None:
    repository = mutable_reference("malformed")
    source = repository / "curriculum/course.json"
    source.write_text("{not valid JSON", encoding="utf-8")
    with pytest.raises(BuildError) as captured:
        build(build_config(tmp_path / "output", repository=repository))
    diagnostic = str(captured.value)
    assert "invalid JSON" in diagnostic
    assert str(source) in diagnostic


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    [
        ("duplicate_unit", "duplicate ID"),
        ("unresolved_objective", "unknown objectives"),
        ("invalid_schedule", "available slots"),
    ],
)
def test_invalid_curriculum_and_schedule_diagnostics(
    reference_curriculum: tuple[dict, list[dict], list[dict]],
    community_profile: dict,
    community_calendar: dict,
    mutation: str,
    diagnostic: str,
) -> None:
    course, units, sessions = deepcopy(reference_curriculum)
    with pytest.raises(RecordError, match=diagnostic):
        if mutation == "duplicate_unit":
            units.append(deepcopy(units[0]))
            validate_curriculum(course, units, sessions)
        elif mutation == "unresolved_objective":
            sessions[0]["objective_ids"] = ["objective.missing"]
            validate_curriculum(course, units, sessions)
        else:
            calendar = deepcopy(community_calendar)
            calendar["last_day"] = calendar["first_day"]
            schedule_sessions(
                course,
                sessions,
                community_profile,
                calendar,
                "monday-wednesday-evening",
            )


@pytest.mark.parametrize(
    ("relative_path", "mutation", "diagnostic"),
    [
        (
            "locales/en-US.json",
            lambda record: record["strings"].pop("label.objectives"),
            "missing required string",
        ),
        (
            "themes/default.json",
            lambda record: record["tokens"].pop("accent"),
            "must define exactly",
        ),
        (
            "institutions/community-college/institution.json",
            lambda record: record["lesson_plan_templates"].update(
                {"administrative": "templates/missing.md"}
            ),
            "template not found",
        ),
        (
            "templates/default/lesson-plan.md",
            lambda record: None,
            "missing required placeholder",
        ),
    ],
)
def test_corrupted_presentation_inputs_have_actionable_diagnostics(
    tmp_path: Path,
    build_config,
    mutable_reference,
    relative_path: str,
    mutation,
    diagnostic: str,
) -> None:
    repository = mutable_reference(relative_path.replace("/", "-"))
    path = repository / relative_path
    if path.suffix == ".json":
        record = json.loads(path.read_text(encoding="utf-8"))
        mutation(record)
        _write_json(path, record)
    else:
        path.write_text("# broken template\n", encoding="utf-8")
    config_changes: dict[str, object] = {"repository": repository}
    if relative_path.startswith("themes/"):
        config_changes["theme"] = "default"
    with pytest.raises(BuildError, match=diagnostic):
        build(build_config(tmp_path / "output", **config_changes))


def test_missing_renderer_and_generator_are_named(
    tmp_path: Path,
    build_config,
) -> None:
    with pytest.raises(BuildError, match=r"renderer\(s\) unavailable: missing"):
        build(build_config(tmp_path / "renderer", renderers=("missing",)))
    with pytest.raises(BuildError, match=r"generator\(s\) unavailable: missing"):
        build(build_config(tmp_path / "generator", generators=("missing",)))
