"""Public application service for the complete TEOS build pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from teos import __version__
from teos.generators import GENERATORS
from teos.records import RecordError, load_curriculum, load_json, validate_institution
from teos.scheduler import schedule_sessions, validate_calendar
from teos.session_render import SESSION_RENDERERS


class BuildError(RecordError):
    """A controlled end-to-end build failure."""


@dataclass(frozen=True)
class BuildConfig:
    repository: Path
    schema_directory: Path
    institution_id: str
    calendar_id: str
    meeting_pattern_id: str
    locale: str
    theme: str
    output_directory: Path
    renderers: tuple[str, ...] = tuple(SESSION_RENDERERS)
    generators: tuple[str, ...] = tuple(GENERATORS)


@dataclass(frozen=True)
class BuildResult:
    build_id: str
    manifest_path: Path
    artifact_paths: tuple[Path, ...]
    compilation_summary: dict[str, Any]
    schedule: dict[str, Any]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _hash_file(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _select_record(
    paths: Iterable[Path],
    field: str,
    expected: str,
    label: str,
) -> tuple[Path, dict[str, Any]]:
    for path in sorted(paths):
        record = load_json(path)
        if record.get(field) == expected:
            return path, record
    raise BuildError(f"{label} {expected!r} is not available")


def _validate_schema(record: Any, schema_path: Path, source_path: Path) -> None:
    schema = load_json(schema_path)
    try:
        Draft202012Validator(
            schema,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        ).validate(record)
    except ValidationError as exc:
        location = ".".join(str(item) for item in exc.absolute_path) or "<root>"
        raise BuildError(
            f"schema validation failed for {source_path}: {location}: {exc.message}"
        ) from exc


def _validate_catalog(
    record: dict[str, Any],
    *,
    identifier_field: str,
    identifier: str,
    content_field: str,
) -> None:
    if record.get(identifier_field) != identifier:
        raise BuildError(f"{identifier_field} does not match requested {identifier!r}")
    content = record.get(content_field)
    if not isinstance(content, dict) or not content:
        raise BuildError(f"{identifier_field} {identifier!r} has no {content_field}")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in content.items()):
        raise BuildError(f"{identifier_field} {identifier!r} has invalid {content_field}")


def _validate_template(path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise BuildError(f"template is not valid UTF-8: {path}") from exc
    required = {
        "{{ artifact_title }}",
        "{{ context }}",
        "{{ content }}",
        "{{ footer }}",
    }
    missing = sorted(
        placeholder for placeholder in required if placeholder not in content
    )
    if missing:
        raise BuildError(
            f"template {path} is missing required placeholder(s): "
            f"{', '.join(missing)}"
        )


def _localized_content(
    content: str,
    artifact_type: str,
    locale: dict[str, Any],
) -> str:
    title_keys = {
        "administrative": "artifact.administrative.title",
        "instructor": "artifact.instructor.title",
        "lab": "artifact.lab.title",
    }
    strings = locale["strings"]
    replacements = {
        "# Administrative Lesson Plan": title_keys["administrative"],
        "# Instructor Guide": title_keys["instructor"],
        "# Lab Sheet": title_keys["lab"],
        "## Objectives": "label.objectives",
        "## Essential Question": "label.essential_question",
        "## Materials": "label.materials",
        "## Warm Up": "label.warm_up",
        "## Academic Activities": "label.academic_activities",
        "## Shop Activities": "label.shop_activities",
        "## Exit": "label.exit",
        "## Assessment": "label.assessment",
        "## Preparation": "label.preparation",
        "## Teaching Sequence": "label.teaching_sequence",
        "## Common Technician Errors": "label.common_technician_errors",
        "## Instructor Shop Tip": "label.instructor_shop_tip",
        "## Flex Activities": "label.flex_activities",
        "### Procedure": "label.procedure",
        "### Deliverables": "label.deliverables",
        "### Safety": "label.safety",
        "No lab is assigned to this session.": "message.no_lab",
        "None recorded.": "message.none_recorded",
    }
    prefix_replacements = {
        "- Course: ": "label.course",
        "- Session: ": "label.session",
        "- Instructional unit: ": "label.instructional_unit",
        "- Phase: ": "label.phase",
        "- Duration: ": "label.duration",
        "- Institution: ": "label.institution",
    }
    required_keys = {
        *replacements.values(),
        *prefix_replacements.values(),
        *(
            f"phase.{phase}"
            for phase in (
                "theory",
                "demonstration",
                "lab",
                "assessment",
                "integrated",
            )
        ),
        "label.minutes",
    }
    missing = sorted(key for key in required_keys if not strings.get(key))
    if missing:
        raise BuildError(
            f"locale {locale['locale']!r} is missing required string(s): "
            f"{', '.join(missing)}"
        )
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line in replacements:
            marker = f"{line.split(' ', 1)[0]} " if line.startswith("#") else ""
            lines[index] = f"{marker}{strings[replacements[line]]}"
            continue
        for prefix, key in prefix_replacements.items():
            if not line.startswith(prefix):
                continue
            value = line[len(prefix) :]
            if key == "label.phase":
                value = strings[f"phase.{value.lower()}"]
            elif key == "label.duration" and value.endswith(" minutes"):
                value = f"{value[:-8]} {strings['label.minutes']}"
            lines[index] = f"- {strings[key]}: {value}"
            break
    return "\n".join(lines) + "\n"


def _validate_requested(config: BuildConfig) -> None:
    if not config.renderers:
        raise BuildError("at least one renderer is required")
    if not config.generators:
        raise BuildError("at least one generator is required")
    unavailable_renderers = sorted(set(config.renderers) - SESSION_RENDERERS.keys())
    if unavailable_renderers:
        raise BuildError(f"renderer(s) unavailable: {', '.join(unavailable_renderers)}")
    unavailable_generators = sorted(set(config.generators) - GENERATORS.keys())
    if unavailable_generators:
        raise BuildError(f"generator(s) unavailable: {', '.join(unavailable_generators)}")
    if len(set(config.renderers)) != len(config.renderers):
        raise BuildError("renderer selections must be unique")
    if len(set(config.generators)) != len(config.generators):
        raise BuildError("generator selections must be unique")


def _build(config: BuildConfig) -> BuildResult:
    """Execute Load → Validate → Compile → Schedule → Render → Generate."""
    _validate_requested(config)
    repository = Path(config.repository).resolve()
    schemas = Path(config.schema_directory).resolve()
    output = Path(config.output_directory).resolve()
    if not repository.is_dir():
        raise BuildError(f"reference repository not found: {repository}")
    if not schemas.is_dir():
        raise BuildError(f"schema directory not found: {schemas}")
    if output.exists():
        raise BuildError(f"output directory already exists: {output}")

    course_directory = repository / "curriculum"
    institution_path, institution = _select_record(
        (repository / "institutions").glob("*/institution.json"),
        "institution_id",
        config.institution_id,
        "institution",
    )
    calendar_path, calendar = _select_record(
        (repository / "institutions").glob("*/calendars/*.json"),
        "calendar_id",
        config.calendar_id,
        "calendar",
    )
    locale_path, locale = _select_record(
        (repository / "locales").glob("*.json"),
        "locale",
        config.locale,
        "locale",
    )
    theme_path, theme = _select_record(
        (repository / "themes").glob("*.json"),
        "theme_id",
        config.theme,
        "theme",
    )
    template_value = institution.get("lesson_plan_templates", {}).get("administrative")
    if not isinstance(template_value, str) or not template_value:
        raise BuildError("institution has no administrative template selection")
    marker = "reference_curriculum/"
    template_relative = template_value.split(marker, 1)[-1]
    template_path = repository / template_relative
    if not template_path.is_file():
        raise BuildError(f"template not found: {template_path}")
    _validate_template(template_path)

    course_path = course_directory / "course.json"
    sessions_path = course_directory / "sessions.json"
    course_record = load_json(course_path)
    session_record = load_json(sessions_path)
    unit_paths = sorted((course_directory / "units").glob("*.json"))
    if not unit_paths:
        raise BuildError(f"no instructional units found: {course_directory / 'units'}")
    unit_records = [load_json(path) for path in unit_paths]

    _validate_schema(course_record, schemas / "course.schema.json", course_path)
    _validate_schema(
        session_record,
        schemas / "session-plan.schema.json",
        sessions_path,
    )
    for path, record in zip(unit_paths, unit_records):
        _validate_schema(
            record,
            schemas / "instructional-unit.schema.json",
            path,
        )
    _validate_schema(
        institution,
        schemas / "institution.schema.json",
        institution_path,
    )
    _validate_schema(
        calendar,
        schemas / "academic-calendar.schema.json",
        calendar_path,
    )
    validate_institution(institution)
    validate_calendar(calendar)
    _validate_catalog(
        locale,
        identifier_field="locale",
        identifier=config.locale,
        content_field="strings",
    )
    _validate_catalog(
        theme,
        identifier_field="theme_id",
        identifier=config.theme,
        content_field="tokens",
    )
    required_theme_tokens = {"background", "foreground", "accent", "font_family"}
    if set(theme["tokens"]) != required_theme_tokens:
        raise BuildError(
            f"theme {config.theme!r} must define exactly: "
            f"{', '.join(sorted(required_theme_tokens))}"
        )

    source_snapshot = _canonical_json(
        [course_record, *unit_records, session_record, institution, calendar]
    )
    curriculum_revision = _hash_bytes(
        _canonical_json([course_record, *unit_records, session_record]).encode("utf-8")
    )
    course, units, sessions = load_curriculum(course_directory)
    unit_order = [
        unit_id
        for module in course["modules"]
        for unit_id in module["unit_ids"]
    ]
    ordered_units = sorted(units, key=lambda item: unit_order.index(item["id"]))
    ordered_sessions = sorted(sessions, key=lambda item: item["session_number"])
    compilation_summary = {
        "course_id": course["course_id"],
        "schema_version": course["schema_version"],
        "unit_ids": [item["id"] for item in ordered_units],
        "session_ids": [item["id"] for item in ordered_sessions],
        "session_count": len(ordered_sessions),
        "total_minutes": sum(item["duration_minutes"] for item in ordered_sessions),
        "dependency_edges": [],
        "dependency_graph_acyclic": True,
    }
    schedule = schedule_sessions(
        course,
        ordered_sessions,
        institution,
        calendar,
        config.meeting_pattern_id,
    )
    assigned = [item["session_number"] for item in schedule["assignments"]]
    expected = [item["session_number"] for item in ordered_sessions]
    if assigned != expected or len(set(assigned)) != len(assigned):
        raise BuildError("scheduler omitted, duplicated, or reordered sessions")

    source_files = [
        course_path,
        *unit_paths,
        sessions_path,
        institution_path,
        calendar_path,
        locale_path,
        theme_path,
        template_path,
    ]
    source_hashes = {
        str(path.relative_to(repository)): _hash_file(path)
        for path in sorted(source_files)
    }
    identity = {
        "teos_version": __version__,
        "source_curriculum_id": course["course_id"],
        "institution_id": config.institution_id,
        "calendar_id": config.calendar_id,
        "meeting_pattern_id": config.meeting_pattern_id,
        "locale": config.locale,
        "theme": config.theme,
        "renderers": list(config.renderers),
        "generators": list(config.generators),
        "source_hashes": source_hashes,
    }
    build_id = _hash_bytes(_canonical_json(identity).encode("utf-8"))

    output_parent = output.parent
    try:
        output_parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix=f".{output.name}.", dir=output_parent)
        )
    except OSError as exc:
        raise BuildError(f"cannot create output directory {output}: {exc}") from exc

    artifact_entries: list[dict[str, Any]] = []
    try:
        _write_json(staging / "compiled-curriculum.json", compilation_summary)
        _write_json(staging / "schedule.json", schedule)
        units_by_id = {item["id"]: item for item in ordered_units}
        sessions_by_number = {
            item["session_number"]: item for item in ordered_sessions
        }
        presentation = {**theme, "_locale": config.locale}
        for assignment in schedule["assignments"]:
            session = sessions_by_number[assignment["session_number"]]
            unit = units_by_id[session["unit_id"]]
            for renderer_id in config.renderers:
                rendered = SESSION_RENDERERS[renderer_id](
                    course,
                    unit,
                    session,
                    institution,
                )
                rendered = _localized_content(rendered, renderer_id, locale)
                rendered_record = {
                    "renderer": renderer_id,
                    "artifact_type": renderer_id,
                    "build_id": build_id,
                    "curriculum_revision": curriculum_revision,
                    "course_id": course["course_id"],
                    "curriculum_version": course["schema_version"],
                    "unit_id": unit["id"],
                    "session_id": session["id"],
                    "session_number": session["session_number"],
                    "schedule_id": schedule["schedule_id"],
                    "institution_id": config.institution_id,
                    "locale": config.locale,
                    "theme": config.theme,
                    "content": rendered,
                }
                rendered_relative = (
                    Path("rendered")
                    / f"session-{session['session_number']:03d}-{renderer_id}.json"
                )
                _write_json(staging / rendered_relative, rendered_record)
                for generator_id in config.generators:
                    extension, generator = GENERATORS[generator_id]
                    content = generator(rendered, presentation)
                    relative = (
                        Path("artifacts")
                        / generator_id
                        / (
                            f"{course['course_id']}-session-"
                            f"{session['session_number']:03d}-{renderer_id}{extension}"
                        )
                    )
                    path = staging / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                    artifact_entries.append(
                        {
                            "artifact_id": (
                                f"{course['course_id']}:{session['id']}:"
                                f"{renderer_id}:{generator_id}"
                            ),
                            "artifact_type": renderer_id,
                            "renderer": renderer_id,
                            "generator": generator_id,
                            "format": generator_id,
                            "course_id": course["course_id"],
                            "curriculum_version": course["schema_version"],
                            "curriculum_revision": curriculum_revision,
                            "unit_id": unit["id"],
                            "session_id": session["id"],
                            "session_number": session["session_number"],
                            "schedule_id": schedule["schedule_id"],
                            "institution_id": config.institution_id,
                            "locale": config.locale,
                            "theme": config.theme,
                            "output_path": relative.as_posix(),
                            "content_hash": _hash_bytes(content),
                            "pipeline_result": "success",
                        }
                    )
        manifest = {
            "manifest_version": "1.0",
            "build_id": build_id,
            "curriculum_revision": curriculum_revision,
            "curriculum_version": course["schema_version"],
            **identity,
            "artifact_count": len(artifact_entries),
            "artifacts": artifact_entries,
            "pipeline_result": "success",
        }
        _write_json(staging / "manifest.json", manifest)
        current_snapshot = _canonical_json(
            [
                load_json(course_path),
                *(load_json(path) for path in unit_paths),
                load_json(sessions_path),
                load_json(institution_path),
                load_json(calendar_path),
            ]
        )
        if current_snapshot != source_snapshot:
            raise BuildError("source records changed during the build")
        os.replace(staging, output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        shutil.rmtree(staging, ignore_errors=True)
        if isinstance(exc, BuildError):
            raise
        raise BuildError(f"build generation failed: {exc}") from exc

    paths = tuple(output / item["output_path"] for item in artifact_entries)
    return BuildResult(
        build_id=build_id,
        manifest_path=output / "manifest.json",
        artifact_paths=paths,
        compilation_summary=deepcopy(compilation_summary),
        schedule=deepcopy(schedule),
    )


def build(config: BuildConfig) -> BuildResult:
    """Run the public build service and normalize record failures by API type."""
    try:
        return _build(config)
    except BuildError:
        raise
    except RecordError as exc:
        raise BuildError(str(exc)) from exc
