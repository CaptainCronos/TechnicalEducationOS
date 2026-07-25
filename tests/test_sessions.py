from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from teos.cli import main
from teos.records import RecordError, load_curriculum, load_json
from teos.scheduler import resolve_session, schedule_sessions
from teos.session_render import render_administrative_session


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DSL204_DIRECTORY = REPOSITORY_ROOT / "curriculum" / "courses" / "dsl204"
FALL_2026 = (
    REPOSITORY_ROOT
    / "institutions"
    / "j-tech"
    / "calendars"
    / "dsl204-fall-2026.json"
)


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

    def test_holiday_shifts_session_without_mutating_curriculum(self):
        original = deepcopy(self.sessions)
        schedule = schedule_sessions(self.course, self.sessions, self.calendar)
        self.assertEqual(
            [item["date"] for item in schedule["assignments"]],
            ["2026-09-03", "2026-09-10"],
        )
        self.assertEqual(schedule["completion_date"], "2026-09-10")
        self.assertEqual(self.sessions, original)

    def test_week_day_alias_resolves_before_rendering(self):
        schedule = schedule_sessions(self.course, self.sessions, self.calendar)
        self.assertEqual(resolve_session(schedule, week=5, day=2), 2)

    def test_insufficient_slots_stop_scheduling(self):
        calendar = deepcopy(self.calendar)
        calendar["meeting_slots"] = calendar["meeting_slots"][:2]
        with self.assertRaisesRegex(RecordError, "available slots"):
            schedule_sessions(self.course, self.sessions, calendar)


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
                        "--calendar",
                        str(FALL_2026),
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
                        "5",
                        "--day",
                        "2",
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
