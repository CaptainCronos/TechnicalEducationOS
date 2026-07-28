from __future__ import annotations

import hashlib
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from teos.cli import main
from teos.records import load_curriculum, load_json, validate_institution
from teos.scheduler import schedule_sessions
from teos.session_render import SESSION_RENDERERS

pytestmark = pytest.mark.regression

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = REPOSITORY_ROOT / "examples" / "reference_curriculum"
COURSE_DIRECTORY = REFERENCE_ROOT / "curriculum"
SCHEMA_DIRECTORY = REPOSITORY_ROOT / "schemas"
COMMUNITY_PROFILE = (
    REFERENCE_ROOT / "institutions" / "community-college" / "institution.json"
)
COMMUNITY_CALENDAR = (
    REFERENCE_ROOT
    / "institutions"
    / "community-college"
    / "calendars"
    / "fall-2026-semester.json"
)
TRADE_PROFILE = (
    REFERENCE_ROOT / "institutions" / "trade-school" / "institution.json"
)
TRADE_CALENDAR = (
    REFERENCE_ROOT
    / "institutions"
    / "trade-school"
    / "calendars"
    / "accelerated-8-week.json"
)


class ReferenceCurriculumSchemaTests(unittest.TestCase):
    def test_every_governed_record_matches_its_frozen_schema(self):
        records = (
            ("course.schema.json", COURSE_DIRECTORY / "course.json"),
            *(
                ("instructional-unit.schema.json", path)
                for path in sorted((COURSE_DIRECTORY / "units").glob("*.json"))
            ),
            ("session-plan.schema.json", COURSE_DIRECTORY / "sessions.json"),
            ("institution.schema.json", COMMUNITY_PROFILE),
            ("institution.schema.json", TRADE_PROFILE),
            ("academic-calendar.schema.json", COMMUNITY_CALENDAR),
            ("academic-calendar.schema.json", TRADE_CALENDAR),
        )
        for schema_name, record_path in records:
            with self.subTest(record=record_path.relative_to(REFERENCE_ROOT)):
                schema = load_json(SCHEMA_DIRECTORY / schema_name)
                validator = Draft202012Validator(
                    schema,
                    format_checker=Draft202012Validator.FORMAT_CHECKER,
                )
                validator.validate(load_json(record_path))


class ReferenceCurriculumCompilationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course, cls.units, cls.sessions = load_curriculum(COURSE_DIRECTORY)

    def test_complete_curriculum_compiles_with_exact_time_and_all_phases(self):
        self.assertEqual(self.course["course_id"], "tec101")
        self.assertEqual(len(self.units), 2)
        self.assertEqual(len(self.sessions), 8)
        self.assertEqual(sum(unit["estimated_minutes"] for unit in self.units), 720)
        self.assertEqual(sum(item["duration_minutes"] for item in self.sessions), 720)
        self.assertEqual(
            {item["phase"] for item in self.sessions},
            {"theory", "demonstration", "lab", "assessment", "integrated"},
        )

    def test_all_supported_repository_component_types_are_populated(self):
        for unit in self.units:
            with self.subTest(unit=unit["id"]):
                self.assertTrue(unit["objectives"])
                self.assertTrue(unit["lectures"])
                self.assertTrue(unit["demonstrations"])
                self.assertTrue(unit["labs"])
                self.assertTrue(unit["assessments"])
                self.assertTrue(unit["required_resources"])
        self.assertEqual(
            {item["type"] for unit in self.units for item in unit["assessments"]},
            {"formative", "summative"},
        )

    def test_standard_competency_unit_objective_session_trace_is_resolved(self):
        standard_ids = {
            standard_id
            for competency in self.course["competencies"]
            for standard_id in competency["standard_ids"]
        }
        self.assertIn("OSHA.1910.334.c.1", standard_ids)
        self.assertIn("NFPA70E.ESWP", standard_ids)

        competencies = {item["id"] for item in self.course["competencies"]}
        units = {item["id"]: item for item in self.units}
        for unit in self.units:
            self.assertLessEqual(set(unit["competency_ids"]), competencies)
            objectives = {item["id"] for item in unit["objectives"]}
            for component_name in (
                "lectures",
                "demonstrations",
                "labs",
                "assessments",
            ):
                for component in unit[component_name]:
                    self.assertLessEqual(set(component["objective_ids"]), objectives)
        for session in self.sessions:
            self.assertIn(session["unit_id"], units)
            self.assertLessEqual(
                set(session["objective_ids"]),
                {item["id"] for item in units[session["unit_id"]]["objectives"]},
            )

    def test_safety_and_measurement_competencies_are_reused_across_units(self):
        mappings = {
            competency_id: {
                unit["id"]
                for unit in self.units
                if competency_id in unit["competency_ids"]
            }
            for competency_id in (
                "comp.electrical-safety",
                "comp.measurement",
            )
        }
        self.assertEqual(
            mappings,
            {
                "comp.electrical-safety": {
                    "unit.safe-measurement",
                    "unit.circuit-diagnosis",
                },
                "comp.measurement": {
                    "unit.safe-measurement",
                    "unit.circuit-diagnosis",
                },
            },
        )

    def test_cli_build_executes_against_reference_directory(self):
        self.assertEqual(
            main(["build", "--course", str(COURSE_DIRECTORY)]),
            0,
        )


class ReferenceCurriculumScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course, _, cls.sessions = load_curriculum(COURSE_DIRECTORY)
        cls.community = load_json(COMMUNITY_PROFILE)
        cls.community_calendar = load_json(COMMUNITY_CALENDAR)
        cls.trade = load_json(TRADE_PROFILE)
        cls.trade_calendar = load_json(TRADE_CALENDAR)

    def test_both_profiles_validate_and_keep_curriculum_outside_overlays(self):
        for profile in (self.community, self.trade):
            validate_institution(profile)
            self.assertNotIn("course_id", profile)
            self.assertNotIn("competencies", profile)
            self.assertNotIn("sessions", profile)

    def test_semester_schedule_skips_holiday_and_faculty_day(self):
        original = deepcopy(self.sessions)
        schedule = schedule_sessions(
            self.course,
            self.sessions,
            self.community,
            self.community_calendar,
            "monday-wednesday-evening",
        )
        self.assertEqual(
            [item["date"] for item in schedule["assignments"]],
            [
                "2026-08-24",
                "2026-08-26",
                "2026-08-31",
                "2026-09-02",
                "2026-09-14",
                "2026-09-16",
                "2026-09-21",
                "2026-09-23",
            ],
        )
        self.assertEqual(schedule["completion_date"], "2026-09-23")
        self.assertEqual(self.sessions, original)

    def test_accelerated_schedule_uses_its_own_pattern_and_closure(self):
        schedule = schedule_sessions(
            self.course,
            self.sessions,
            self.trade,
            self.trade_calendar,
            "tuesday-thursday-day",
        )
        self.assertEqual(
            [item["date"] for item in schedule["assignments"]],
            [
                "2026-10-20",
                "2026-10-22",
                "2026-10-27",
                "2026-11-03",
                "2026-11-05",
                "2026-11-10",
                "2026-11-12",
                "2026-11-17",
            ],
        )
        self.assertEqual(
            {item["start_time"] for item in schedule["assignments"]},
            {"09:00", "13:00"},
        )
        self.assertEqual(schedule["completion_date"], "2026-11-17")

    def test_cli_generates_both_schedule_records_deterministically(self):
        cases = (
            (
                COMMUNITY_PROFILE,
                COMMUNITY_CALENDAR,
                "monday-wednesday-evening",
            ),
            (TRADE_PROFILE, TRADE_CALENDAR, "tuesday-thursday-day"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, (profile, calendar, pattern) in enumerate(cases):
                first = root / f"schedule-{index}-first.json"
                second = root / f"schedule-{index}-second.json"
                arguments = [
                    "schedule",
                    "--course",
                    str(COURSE_DIRECTORY),
                    "--institution",
                    str(profile),
                    "--calendar",
                    str(calendar),
                    "--meeting-pattern",
                    pattern,
                ]
                self.assertEqual(main([*arguments, "--output", str(first)]), 0)
                self.assertEqual(main([*arguments, "--output", str(second)]), 0)
                self.assertEqual(first.read_bytes(), second.read_bytes())


class ReferenceCurriculumPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course, cls.units, cls.sessions = load_curriculum(COURSE_DIRECTORY)
        cls.units_by_id = {unit["id"]: unit for unit in cls.units}
        cls.community = load_json(COMMUNITY_PROFILE)
        cls.trade = load_json(TRADE_PROFILE)

    def test_all_canonical_session_renderers_are_deterministic(self):
        session = self.sessions[2]
        unit = self.units_by_id[session["unit_id"]]
        expected_hashes = {
            "administrative": (
                "8a495a6b0c72639c549ffa304152208957defded4c5ee946465035c1ec84982f"
            ),
            "instructor": (
                "e4352809325f43053e30bb0d97237bbc54333a747f8d708fa35d68891ec84117"
            ),
            "lab": (
                "b990a62269c233cdc7dc2a0b8a6c1c64939e026a94d84572075de4ffaebf5244"
            ),
        }
        for name, renderer in SESSION_RENDERERS.items():
            with self.subTest(renderer=name):
                first = renderer(self.course, unit, session, self.community)
                second = renderer(self.course, unit, session, self.community)
                self.assertEqual(first, second)
                self.assertEqual(
                    hashlib.sha256(first.encode("utf-8")).hexdigest(),
                    expected_hashes[name],
                )
                self.assertIn(session["title"], first)
                self.assertIn(unit["title"], first)

    def test_institution_changes_presentation_context_not_curriculum(self):
        session = self.sessions[0]
        unit = self.units_by_id[session["unit_id"]]
        community = SESSION_RENDERERS["administrative"](
            self.course,
            unit,
            session,
            self.community,
        )
        trade = SESSION_RENDERERS["administrative"](
            self.course,
            unit,
            session,
            self.trade,
        )
        for objective in unit["objectives"][:2]:
            self.assertIn(objective["statement"], community)
            self.assertIn(objective["statement"], trade)
        self.assertIn(self.community["institution_name"], community)
        self.assertNotIn(self.trade["institution_name"], community)
        self.assertIn(self.trade["institution_name"], trade)
        self.assertNotIn(self.community["institution_name"], trade)

    def test_cli_renders_every_supported_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            self.assertEqual(
                main(
                    [
                        "render",
                        "--course",
                        str(COURSE_DIRECTORY),
                        "--session",
                        "3",
                        "--artifact",
                        "all",
                        "--institution",
                        str(COMMUNITY_PROFILE),
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertEqual(
                {path.name for path in output.glob("*.md")},
                {
                    "tec101-session-003-administrative.md",
                    "tec101-session-003-instructor.md",
                    "tec101-session-003-lab.md",
                },
            )

    def test_themes_and_locales_have_parallel_presentation_contracts(self):
        themes = [
            load_json(path)
            for path in sorted((REFERENCE_ROOT / "themes").glob("*.json"))
        ]
        locales = [
            load_json(path)
            for path in sorted((REFERENCE_ROOT / "locales").glob("*.json"))
        ]
        self.assertEqual(
            {theme["theme_id"] for theme in themes},
            {"default", "dark", "institution-branded"},
        )
        self.assertTrue(
            all(
                set(theme["tokens"]) == set(themes[0]["tokens"])
                for theme in themes
            )
        )
        self.assertEqual(
            {locale["locale"] for locale in locales},
            {"en-US", "es-US"},
        )
        self.assertEqual(
            set(locales[0]["strings"]),
            set(locales[1]["strings"]),
        )
        theme_ids = {theme["theme_id"] for theme in themes}
        locale_ids = {locale["locale"] for locale in locales}
        for profile in (self.community, self.trade):
            self.assertIn(profile["branding"]["theme_id"], theme_ids)
            self.assertIn(profile["branding"]["locale"], locale_ids)
            self.assertTrue(
                (
                    REPOSITORY_ROOT
                    / profile["lesson_plan_templates"]["administrative"]
                ).is_file()
            )
        self.assertEqual(
            load_json(COURSE_DIRECTORY / "course.json"),
            self.course,
        )
