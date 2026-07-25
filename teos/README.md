# TEOS application

This package contains the command-line workflow, validation, audits, and
document renderers. It reads authoritative records and writes only generated
outputs. Active Phase 1 development and acceptance are limited to the J-Tech
Administrative Lesson Plan DOCX pipeline; the older general generators remain
available but are not being expanded in this phase.

From the repository root:

```bash
python -m teos audit --course curriculum/courses/COURSE_ID --week 8
python -m teos generate --course curriculum/courses/COURSE_ID --week 8
```

Add `--institution institutions/INSTITUTION_ID/institution.json` to apply an
optional administrative overlay. Generated Markdown is written to `outputs/`
by default. One generation run creates:

- One administrative plan per daily lesson (or one weekly plan for the original
  lecture/lab representation) and an instructor lesson plan.
- A guide for each lab.
- Learner assessments in batches of at most ten questions.
- Separate answer keys for each assessment batch.
- A curriculum relationship audit.

The approved DSL204 Week 5 proof can be regenerated with:

```bash
python -m teos generate \
  --course curriculum/courses/dsl204 \
  --week 5 \
  --institution institutions/j-tech/institution.json
```

To populate the official blank J-Tech Administrative Lesson Plan template
directly, run the administrative-only command:

```bash
python -m teos generate-administrative \
  --course curriculum/courses/dsl204 \
  --week 5 \
  --template templates/jtech/admin_lesson_plan_template.docx
```

This writes one DOCX per daily lesson. The J-Tech presentation adapter uses
only the Python standard library, preserves the official template package and
header artwork, and constructs the finished two-page presentation demonstrated
by the approved FUN101 Week 7 plans. Every populated instructional value still
comes from the validated course/week records.

An audit returns a nonzero exit status when a valid record has objectives
without lecture, lab, or assessment alignment. Invalid or broken source
relationships return exit status 2.

Run the dependency-free test suite with:

```bash
python -m unittest discover -s tests -v
```
