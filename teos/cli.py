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
from teos.render import render_administrative, render_instructor


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
    for path, content in documents.items():
        path.write_text(content, encoding="utf-8")
        print(path)
    findings = coverage_findings(week)
    if findings:
        print(f"Audit: {len(findings)} coverage finding(s); run 'audit' for details.")
    return 0


def _audit(args: argparse.Namespace) -> int:
    _, week, _ = _load(args)
    findings = coverage_findings(week)
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
