"""Command-line entry point for TechnicalEducationOS."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from teos.audit import coverage_findings
from teos.docx import render_administrative_docx
from teos.records import (
    RecordError,
    load_course,
    load_curriculum,
    load_json,
    load_week,
    validate_institution,
    validate_week,
)
from teos.scheduler import resolve_session, schedule_sessions
from teos.session_render import SESSION_RENDERERS
from teos.render import (
    assessment_batches,
    render_administrative,
    render_assessment_batch,
    render_assessment_key,
    render_audit,
    render_instructor,
    render_lab,
)


def _load(args: argparse.Namespace):
    course_directory = Path(args.course)
    course = load_course(course_directory)
    week = load_week(course_directory, args.week)
    validate_week(course, week)
    institution = None
    if args.institution:
        institution = load_json(Path(args.institution))
        validate_institution(institution)
    return course, week, institution


def _generate(args: argparse.Namespace) -> int:
    course, week, institution = _load(args)
    output_directory = Path(args.output)
    output_directory.mkdir(parents=True, exist_ok=True)
    stem = f"{course['course_id']}-week-{week['week_number']:02d}"
    documents = {
        output_directory / f"{stem}-instructor.md": render_instructor(
            course, week, institution
        ),
    }
    if week.get("lessons"):
        documents.update(
            {
                (
                    output_directory
                    / f"{stem}-day-{lesson['day_number']:02d}-administrative.md"
                ): render_administrative(course, week, institution, lesson)
                for lesson in week["lessons"]
            }
        )
    else:
        documents[
            output_directory / f"{stem}-administrative.md"
        ] = render_administrative(course, week, institution)
    documents.update(
        {
            output_directory / f"{stem}-lab-{lab['id']}.md": render_lab(
                course, week, lab, institution
            )
            for lab in week["labs"]
        }
    )
    for assessment in week["assessments"]:
        for batch_number, questions in enumerate(
            assessment_batches(assessment), start=1
        ):
            batch_stem = (
                output_directory
                / f"{stem}-assessment-{assessment['id']}-batch-{batch_number:02d}"
            )
            documents[Path(f"{batch_stem}.md")] = render_assessment_batch(
                course,
                week,
                assessment,
                questions,
                batch_number,
                institution,
            )
            documents[
                batch_stem.with_name(f"{batch_stem.name}-key.md")
            ] = render_assessment_key(
                course,
                week,
                assessment,
                questions,
                batch_number,
                institution,
            )
    findings = coverage_findings(week)
    documents[output_directory / f"{stem}-audit.md"] = render_audit(
        course, week, findings
    )
    for path, content in documents.items():
        path.write_text(content, encoding="utf-8")
        print(path)
    if findings:
        print(f"Audit: {len(findings)} coverage finding(s); run 'audit' for details.")
    return 0


def _audit(args: argparse.Namespace) -> int:
    course, week, _ = _load(args)
    findings = coverage_findings(week)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_audit(course, week, findings), encoding="utf-8")
        print(output_path)
    if not findings:
        print("Audit passed: every objective aligns to a lecture, lab, and assessment.")
        return 0
    print("Audit findings:")
    for finding in findings:
        print(f"- {finding}")
    return 1


def _generate_administrative(args: argparse.Namespace) -> int:
    course, week, _ = _load(args)
    lessons = week.get("lessons", [])
    if not lessons:
        raise RecordError(
            "Administrative DOCX generation requires daily lessons"
        )
    template = Path(args.template)
    output_directory = Path(args.output)
    output_directory.mkdir(parents=True, exist_ok=True)
    stem = f"{course['course_id']}-week-{week['week_number']:02d}"
    try:
        documents = {
            (
                output_directory
                / f"{stem}-day-{lesson['day_number']:02d}-administrative.docx"
            ): render_administrative_docx(
                template,
                course,
                week,
                lesson,
            )
            for lesson in lessons
        }
    except ValueError as exc:
        raise RecordError(str(exc)) from exc
    for path, content in documents.items():
        path.write_bytes(content)
        print(path)
    return 0


def _build_curriculum(args: argparse.Namespace) -> int:
    course, units, sessions = load_curriculum(Path(args.course))
    print(
        f"Build passed: {course['course_id']} has {len(units)} instructional "
        f"unit(s) and {len(sessions)} session(s)."
    )
    return 0


def _schedule(args: argparse.Namespace) -> int:
    course, _, sessions = load_curriculum(Path(args.course))
    calendar = load_json(Path(args.calendar))
    schedule = schedule_sessions(course, sessions, calendar)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(schedule, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)
    return 0


def _render_session(args: argparse.Namespace) -> int:
    course, units, sessions = load_curriculum(Path(args.course))
    if args.day is not None and args.week is None:
        raise RecordError("--day may only be used with --week")
    session_number = args.session
    if args.week is not None or args.date is not None:
        if not args.schedule:
            raise RecordError(
                "calendar aliases require --schedule; renderers never interpret "
                "weeks or dates directly"
            )
        schedule = load_json(Path(args.schedule))
        session_number = resolve_session(
            schedule,
            week=args.week,
            day=args.day,
            meeting_date=args.date,
        )
    elif session_number is None:
        raise RecordError("render requires --session, --date, or --week with --day")

    session = next(
        (
            item
            for item in sessions
            if item["session_number"] == session_number
        ),
        None,
    )
    if session is None:
        raise RecordError(f"session {session_number} not found")
    unit = next(item for item in units if item["id"] == session["unit_id"])
    institution = None
    if args.institution:
        institution = load_json(Path(args.institution))
        validate_institution(institution)

    artifact_names = (
        list(SESSION_RENDERERS) if args.artifact == "all" else [args.artifact]
    )
    output_directory = Path(args.output)
    output_directory.mkdir(parents=True, exist_ok=True)
    for artifact_name in artifact_names:
        content = SESSION_RENDERERS[artifact_name](
            course,
            unit,
            session,
            institution,
        )
        path = (
            output_directory
            / f"{course['course_id']}-session-{session_number:03d}-{artifact_name}.md"
        )
        path.write_text(content, encoding="utf-8")
        print(path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teos",
        description="Validate, audit, and generate documents from curriculum records.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser(
        "build",
        help="Validate the canonical course, units, and sessions",
    )
    build.add_argument("--course", required=True, help="Course record directory")
    build.set_defaults(handler=_build_curriculum)

    schedule = subparsers.add_parser(
        "schedule",
        help="Map canonical sessions onto an academic calendar",
    )
    schedule.add_argument("--course", required=True, help="Course record directory")
    schedule.add_argument("--calendar", required=True, help="Academic calendar JSON")
    schedule.add_argument("--output", required=True, help="Generated schedule JSON")
    schedule.set_defaults(handler=_schedule)

    render = subparsers.add_parser(
        "render",
        help="Render artifacts from a session or resolved calendar alias",
    )
    render.add_argument("--course", required=True, help="Course record directory")
    selectors = render.add_mutually_exclusive_group(required=False)
    selectors.add_argument("--session", type=int, help="Canonical session number")
    selectors.add_argument("--date", help="Scheduled meeting date (YYYY-MM-DD)")
    selectors.add_argument("--week", type=int, help="Calendar week alias")
    render.add_argument("--day", type=int, help="Day alias used with --week")
    render.add_argument("--schedule", help="Generated schedule for alias resolution")
    render.add_argument(
        "--artifact",
        choices=["all", *SESSION_RENDERERS],
        default="all",
    )
    render.add_argument("--institution", help="Optional institution overlay JSON")
    render.add_argument("--output", default="outputs", help="Output directory")
    render.set_defaults(handler=_render_session)

    # Deprecated commands remain temporarily available for reproducibility of
    # approved artifacts. New authoring and renderer work uses the commands above.
    for name, handler in (("generate", _generate), ("audit", _audit)):
        command = subparsers.add_parser(name)
        command.add_argument("--course", required=True, help="Course record directory")
        command.add_argument("--week", required=True, type=int, help="Week number")
        command.add_argument("--institution", help="Optional institution overlay JSON")
        if name == "generate":
            command.add_argument("--output", default="outputs", help="Output directory")
        else:
            command.add_argument("--output", help="Optional Markdown audit report path")
        command.set_defaults(handler=handler)
    administrative = subparsers.add_parser(
        "generate-administrative",
        help="Populate the official Administrative Lesson Plan DOCX template",
    )
    administrative.add_argument(
        "--course", required=True, help="Course record directory"
    )
    administrative.add_argument(
        "--week", required=True, type=int, help="Week number"
    )
    administrative.add_argument(
        "--template", required=True, help="Official blank DOCX template"
    )
    administrative.add_argument(
        "--output", default="outputs", help="Output directory"
    )
    administrative.set_defaults(
        handler=_generate_administrative,
        institution=None,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except RecordError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
