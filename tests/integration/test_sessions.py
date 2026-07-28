from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import pytest

from teos.cli import main
from teos.records import (
    RecordError,
    load_curriculum,
    load_json,
    validate_institution,
)
from teos.scheduler import (
    available_meeting_slots,
    resolve_session,
    schedule_sessions,
)
from teos.session_render import render_administrative_session

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DSL204_DIRECTORY = REPOSITORY_ROOT / "curriculum" / "courses" / "dsl204"
FALL_2026 = (
    REPOSITORY_ROOT
    / "institutions"
    / "j-tech"
    / "calendars"
    / "fall-2026.json"
)
J_TECH_PROFILE = REPOSITORY_ROOT / "institutions" / "j-tech" / "institution.json"
MEETING_PATTERN = "thursday-friday-am"


class CanonicalCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course, cls.units, cls.sessions = load_curriculum(DSL204_DIRECTORY)

    def test_dsl204_builds_without_calendar_knowledge(self):
        self.assertNotIn("week", self.course)
        self.assertNotIn("calendar", self.course)
        self.assertEqual(self.units[0]["estimated_minutes"], 480)
        self.assertEqual([item["session_number"] for item in self.sessions], [1, 2])

    def test_session_renderer_uses_unit_and_session_content(self):
        rendered = render_administrative_session(
            self.course,
            self.units[0],
            self.sessions[0],
        )
        self.assertIn("Session: 1", rendered)
        self.assertIn(self.units[0]["title"], rendered)
        self.assertIn(
            self.sessions[0]["instruction"]["essential_question"],
            rendered,
        )
        self.assertNotIn("Week 5", rendered)

    def test_noncontiguous_sessions_are_rejected(self):
        sessions = deepcopy(self.sessions)
        sessions[1]["session_number"] = 3
        from teos.records import validate_curriculum

        with self.assertRaisesRegex(RecordError, "contiguous"):
            validate_curriculum(self.course, self.units, sessions)


class SchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course, _, cls.sessions = load_curriculum(DSL204_DIRECTORY)
        cls.calendar = load_json(FALL_2026)
        cls.institution = load_json(J_TECH_PROFILE)

    def test_profile_contains_operations_but_no_curriculum(self):
        validate_institution(self.institution)
        self.assertNotIn("course_id", self.institution)
        self.assertNotIn("curriculum", self.institution)
        self.assertEqual(
            self.institution["meeting_patterns"][0]["pattern_id"],
            MEETING_PATTERN,
        )

    def test_calendar_contains_availability_but_no_course(self):
        self.assertNotIn("course_id", self.calendar)
        self.assertNotIn("meeting_slots", self.calendar)
        slots = available_meeting_slots(
            self.institution,
            self.calendar,
            MEETING_PATTERN,
        )
        self.assertEqual(
            [item["date"] for item in slots[:2]],
            ["2026-09-03", "2026-09-10"],
        )

    def test_holiday_shifts_session_without_mutating_curriculum(self):
        original = deepcopy(self.sessions)
        schedule = schedule_sessions(
            self.course,
            self.sessions,
            self.institution,
            self.calendar,
            MEETING_PATTERN,
        )
        self.assertEqual(
            [item["date"] for item in schedule["assignments"]],
            ["2026-09-03", "2026-09-10"],
        )
        self.assertEqual(schedule["completion_date"], "2026-09-10")
        self.assertEqual(self.sessions, original)

    def test_week_day_alias_resolves_before_rendering(self):
        schedule = schedule_sessions(
            self.course,
            self.sessions,
            self.institution,
            self.calendar,
            MEETING_PATTERN,
        )
        self.assertEqual(resolve_session(schedule, week=6, day=1), 2)

    def test_insufficient_slots_stop_scheduling(self):
        calendar = deepcopy(self.calendar)
        calendar["last_day"] = "2026-09-04"
        with self.assertRaisesRegex(RecordError, "available slots"):
            schedule_sessions(
                self.course,
                self.sessions,
                self.institution,
                calendar,
                MEETING_PATTERN,
            )


class SessionCliTests(unittest.TestCase):
    def test_schedule_then_render_calendar_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            schedule_path = root / "schedule.json"
            output = root / "outputs"
            self.assertEqual(
                main(
                    [
                        "schedule",
                        "--course",
                        str(DSL204_DIRECTORY),
                        "--institution",
                        str(J_TECH_PROFILE),
                        "--calendar",
                        str(FALL_2026),
                        "--meeting-pattern",
                        MEETING_PATTERN,
                        "--output",
                        str(schedule_path),
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "render",
                        "--course",
                        str(DSL204_DIRECTORY),
                        "--week",
                        "6",
                        "--day",
                        "1",
                        "--schedule",
                        str(schedule_path),
                        "--artifact",
                        "administrative",
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            document = output / "dsl204-session-002-administrative.md"
            self.assertTrue(document.is_file())
            self.assertIn("Session: 2", document.read_text(encoding="utf-8"))
            schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
            self.assertEqual(schedule["assignments"][1]["session_number"], 2)
