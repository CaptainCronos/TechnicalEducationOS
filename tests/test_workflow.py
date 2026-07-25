from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from teos.audit import coverage_findings
from teos.cli import main
from teos.records import RecordError, validate_course, validate_week
from teos.render import (
    assessment_batches,
    render_administrative,
    render_assessment_key,
    render_instructor,
    render_lab,
)


COURSE = {
    "schema_version": "1.0",
    "course_id": "synthetic-101",
    "title": "Synthetic Systems",
    "competencies": [
        {"id": "comp.safe", "statement": "Perform work safely."},
    ],
}

WEEK = {
    "schema_version": "1.0",
    "course_id": "synthetic-101",
    "week_number": 8,
    "title": "Synthetic Components",
    "preparation": ["Prepare the synthetic training component."],
    "objectives": [
        {
            "id": "obj.identify",
            "statement": "Identify the synthetic component.",
            "competency_ids": ["comp.safe"],
        }
    ],
    "lectures": [
        {
            "id": "lec.components",
            "title": "Component overview",
            "objective_ids": ["obj.identify"],
            "duration_minutes": 30,
            "topics": ["Component identification"],
            "instructor_notes": ["Show the safe example first."],
        }
    ],
    "labs": [
        {
            "id": "lab.identify",
            "title": "Identify components",
            "objective_ids": ["obj.identify"],
            "duration_minutes": 45,
            "procedure": ["Inspect the training component."],
            "deliverables": ["Completed identification record."],
            "safety_notes": ["Use only the inert training component."],
        }
    ],
    "assessments": [
        {
            "id": "assess.check",
            "title": "Identification check",
            "type": "formative",
            "objective_ids": ["obj.identify"],
            "question_bank": [
                {
                    "id": "q.identify.01",
                    "prompt": "Identify the marked component.",
                    "type": "short_answer",
                    "objective_ids": ["obj.identify"],
                    "answer": "The synthetic component.",
                }
            ],
        }
    ],
    "teaching_notes": ["Retain the inert example for future offerings."],
}


class RecordTests(unittest.TestCase):
    def test_valid_connected_records(self):
        validate_course(COURSE)
        validate_week(COURSE, WEEK)

    def test_unknown_objective_reference_is_rejected(self):
        week = deepcopy(WEEK)
        week["labs"][0]["objective_ids"] = ["obj.missing"]
        with self.assertRaisesRegex(RecordError, "unknown objectives"):
            validate_week(COURSE, week)

    def test_unknown_competency_reference_is_rejected(self):
        week = deepcopy(WEEK)
        week["objectives"][0]["competency_ids"] = ["comp.missing"]
        with self.assertRaisesRegex(RecordError, "unknown competencies"):
            validate_week(COURSE, week)


class AuditAndRenderTests(unittest.TestCase):
    def test_complete_coverage_has_no_findings(self):
        self.assertEqual(coverage_findings(WEEK), [])

    def test_missing_lab_alignment_is_reported(self):
        week = deepcopy(WEEK)
        week["labs"] = []
        self.assertEqual(
            coverage_findings(week),
            ["obj.identify: no lab alignment"],
        )

    def test_both_lesson_plans_derive_from_same_objective(self):
        administrative = render_administrative(COURSE, WEEK)
        instructor = render_instructor(COURSE, WEEK)
        statement = WEEK["objectives"][0]["statement"]
        self.assertIn(statement, administrative)
        self.assertIn(statement, instructor)
        self.assertIn("Completed identification record.", instructor)

    def test_lab_and_assessment_key_derive_from_week(self):
        lab = render_lab(COURSE, WEEK, WEEK["labs"][0])
        key = render_assessment_key(
            COURSE,
            WEEK,
            WEEK["assessments"][0],
            WEEK["assessments"][0]["question_bank"],
            1,
        )
        self.assertIn("Inspect the training component.", lab)
        self.assertIn("The synthetic component.", key)

    def test_question_bank_is_split_in_batches_of_ten(self):
        assessment = deepcopy(WEEK["assessments"][0])
        assessment["question_bank"] = [
            {**assessment["question_bank"][0], "id": f"q.identify.{index:02d}"}
            for index in range(1, 24)
        ]
        self.assertEqual(
            [len(batch) for batch in assessment_batches(assessment)],
            [10, 10, 3],
        )


class CliTests(unittest.TestCase):
    def test_generate_writes_all_weekly_documents(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            course_directory = root / "synthetic-101"
            weeks_directory = course_directory / "weeks"
            weeks_directory.mkdir(parents=True)
            (course_directory / "course.json").write_text(
                json.dumps(COURSE), encoding="utf-8"
            )
            (weeks_directory / "08.json").write_text(
                json.dumps(WEEK), encoding="utf-8"
            )
            output_directory = root / "outputs"

            result = main(
                [
                    "generate",
                    "--course",
                    str(course_directory),
                    "--week",
                    "8",
                    "--output",
                    str(output_directory),
                ]
            )

            self.assertEqual(result, 0)
            self.assertTrue(
                (output_directory / "synthetic-101-week-08-administrative.md").is_file()
            )
            self.assertTrue(
                (output_directory / "synthetic-101-week-08-instructor.md").is_file()
            )
            self.assertTrue(
                (
                    output_directory
                    / "synthetic-101-week-08-lab-lab.identify.md"
                ).is_file()
            )
            self.assertTrue(
                (
                    output_directory
                    / "synthetic-101-week-08-assessment-assess.check-batch-01.md"
                ).is_file()
            )
            self.assertTrue(
                (
                    output_directory
                    / "synthetic-101-week-08-assessment-assess.check-batch-01-key.md"
                ).is_file()
            )
            self.assertTrue(
                (output_directory / "synthetic-101-week-08-audit.md").is_file()
            )


if __name__ == "__main__":
    unittest.main()
