"""Command-line entry point for TechnicalEducationOS."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from teos.audit import coverage_findings
from teos.records import (
    RecordError,
    load_course,
    load_json,
    load_week,
    validate_institution,
    validate_week,
)
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
        output_directory / f"{stem}-administrative.md": render_administrative(
            course, week, institution
        ),
        output_directory / f"{stem}-instructor.md": render_instructor(
            course, week, institution
        ),
    }
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teos",
        description="Validate, audit, and generate documents from curriculum records.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except RecordError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
