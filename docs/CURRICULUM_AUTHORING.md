# Recording Existing Curriculum (Legacy Compatibility)

This guide applies to the existing course/week pipeline while TEOS migrates to
course blueprints and structured curriculum models. New architecture work must
follow the governing specifications in `docs/specifications/`.

This workflow transcribes existing curriculum into authoritative compatibility
records. It does not invite curriculum redesign or direct extraction from
slides into generated artifacts.

## Create a course

1. Create `curriculum/courses/COURSE_ID/course.json`.
2. Record the course identity and its existing competencies using
   `schemas/course.schema.json`.
3. Create a `weeks/` directory beneath the course.

Use stable lowercase IDs. IDs are references, not display text, so they should
not change when wording is corrected.

## Record a week

Create `weeks/08.json`, `weeks/09.json`, and so on using
`schemas/week.schema.json`.

- Write each objective statement once in `objectives`.
- Reference objective IDs from lectures, labs, assessments, and questions.
- Reference course competency IDs from objectives.
- Preserve practical instructor knowledge in `instructor_notes`,
  `safety_notes`, and `teaching_notes`.
- Preserve existing assessment answers or rubrics in the question bank; they
  are emitted only into separate key documents.
- If an approved plan is organized by instructional day, record it in
  `lessons`. Use typed activities for its warm-up, academic, shop, and exit
  work. Do not invent lecture durations, lab procedures, deliverables, or
  assessment questions that are absent from the source.
- An observational or performance assessment may use `description` without a
  `question_bank`.

Do not copy document headings, institution names, or formatting into curriculum
fields.

## Check before generating

```bash
python -m teos audit --course curriculum/courses/COURSE_ID --week 8
```

Validation errors indicate broken or malformed source relationships. Audit
findings indicate valid records that need instructional review, such as an
objective without a lab or assessment. An audit finding should be resolved from
the existing curriculum or explicitly reviewed by the instructor—never filled
with invented content just to make the audit pass.

## Generate

```bash
python -m teos generate --course curriculum/courses/COURSE_ID --week 8
```

Review changes in the source record and regenerate. Do not correct generated
files directly.
