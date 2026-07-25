from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
import zipfile
from copy import deepcopy
from pathlib import Path

from teos.audit import coverage_findings
from teos.cli import main
from teos.records import (
    RecordError,
    load_course,
    load_json,
    load_week,
    validate_course,
    validate_institution,
    validate_week,
)
from teos.render import (
    assessment_batches,
    render_administrative,
    render_assessment_key,
    render_instructor,
    render_lab,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DSL204_DIRECTORY = REPOSITORY_ROOT / "curriculum" / "courses" / "dsl204"
J_TECH_OVERLAY = REPOSITORY_ROOT / "institutions" / "j-tech" / "institution.json"
WORD_NAMESPACE = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
}


def reference_document_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        document = ElementTree.fromstring(archive.read("word/document.xml"))
    return "\n".join(
        node.text or "" for node in document.findall(".//w:t", WORD_NAMESPACE)
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


class ApprovedLessonPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course = load_course(DSL204_DIRECTORY)
        cls.week = load_week(DSL204_DIRECTORY, 5)
        cls.institution = load_json(J_TECH_OVERLAY)

    def test_reference_source_records_validate_and_audit(self):
        validate_week(self.course, self.week)
        validate_institution(self.institution)
        self.assertEqual(len(self.week["lessons"]), 2)
        self.assertEqual(coverage_findings(self.week), [])

    def test_unknown_daily_lesson_assessment_is_rejected(self):
        week = deepcopy(self.week)
        week["lessons"][0]["assessment_ids"] = ["assess.missing"]
        with self.assertRaisesRegex(RecordError, "unknown assessments"):
            validate_week(self.course, week)

    def test_daily_lesson_duration_segments_must_match_total(self):
        week = deepcopy(self.week)
        week["lessons"][0]["duration"]["segments"][0]["minutes"] = 60
        with self.assertRaisesRegex(RecordError, "segments must total"):
            validate_week(self.course, week)

    def test_each_daily_plan_is_derived_from_its_source_record(self):
        objectives = {
            item["id"]: item["statement"] for item in self.week["objectives"]
        }
        assessments = {
            item["id"]: item["description"] for item in self.week["assessments"]
        }
        for lesson in self.week["lessons"]:
            rendered = render_administrative(
                self.course, self.week, lesson=lesson
            )
            self.assertIn(lesson["title"], rendered)
            self.assertIn(lesson["objective_summary"], rendered)
            self.assertIn(lesson["essential_question"], rendered)
            self.assertIn(lesson["industry_applications"], rendered)
            self.assertIn(lesson["instructor_shop_tip"], rendered)
            self.assertIn(lesson["homework"], rendered)
            self.assertIn(lesson["flex_activities"], rendered)
            for objective_id in lesson["objective_ids"]:
                self.assertIn(objectives[objective_id], rendered)
            for activity in lesson["activities"]:
                self.assertIn(activity["description"], rendered)
            for assessment_id in lesson["assessment_ids"]:
                self.assertIn(assessments[assessment_id], rendered)
            for value in (
                lesson["materials"]
                + lesson["terminology"]
                + lesson["common_technician_errors"]
            ):
                self.assertIn(value, rendered)

    def test_source_records_preserve_approved_document_content(self):
        competencies = {
            item["id"]: item["statement"] for item in self.course["competencies"]
        }
        objectives = {
            item["id"]: item for item in self.week["objectives"]
        }
        assessments = {
            item["id"]: item["description"] for item in self.week["assessments"]
        }
        for lesson in self.week["lessons"]:
            day_number = lesson["day_number"]
            reference = reference_document_text(
                REPOSITORY_ROOT
                / f"DSL204_Week5_Admin_LessonPlan_Day{day_number}_v1.0.docx"
            )
            expected_curriculum = [
                lesson["title"],
                lesson["objective_summary"],
                lesson["essential_question"],
                lesson["industry_applications"],
                lesson["instructor_shop_tip"],
                lesson["homework"],
                lesson["flex_activities"],
                *lesson["materials"],
                *lesson["terminology"],
                *lesson["common_technician_errors"],
                *(
                    activity["description"]
                    for activity in lesson["activities"]
                ),
                *(
                    assessments[assessment_id]
                    for assessment_id in lesson["assessment_ids"]
                ),
            ]
            for objective_id in lesson["objective_ids"]:
                objective = objectives[objective_id]
                expected_curriculum.append(objective["statement"])
                expected_curriculum.extend(
                    competencies[competency_id]
                    for competency_id in objective["competency_ids"]
                )
            for value in expected_curriculum:
                self.assertIn(value, reference)

    def test_institution_branding_is_an_optional_overlay(self):
        curriculum_text = json.dumps(
            {"course": self.course, "week": self.week}
        )
        unbranded = render_administrative(
            self.course, self.week, lesson=self.week["lessons"][0]
        )
        branded = render_administrative(
            self.course,
            self.week,
            self.institution,
            self.week["lessons"][0],
        )
        self.assertNotIn("J-Tech", curriculum_text)
        self.assertNotIn("Configuration Board", curriculum_text)
        self.assertNotIn("Instructor Reflection", curriculum_text)
        self.assertNotIn("Institution:", unbranded)
        self.assertIn("Institution: J-Tech", branded)

    def test_cli_generates_one_administrative_plan_per_lesson(self):
        with tempfile.TemporaryDirectory() as temporary:
            output_directory = Path(temporary)
            result = main(
                [
                    "generate",
                    "--course",
                    str(DSL204_DIRECTORY),
                    "--week",
                    "5",
                    "--institution",
                    str(J_TECH_OVERLAY),
                    "--output",
                    str(output_directory),
                ]
            )
            self.assertEqual(result, 0)
            for day_number in (1, 2):
                path = (
                    output_directory
                    / f"dsl204-week-05-day-{day_number:02d}-administrative.md"
                )
                self.assertTrue(path.is_file())
                self.assertIn("Institution: J-Tech", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
