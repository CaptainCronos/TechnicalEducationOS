# TEOS application

This package contains the Phase 1 command-line workflow, validation, audits,
and document renderers. It reads authoritative records and writes only
generated outputs.

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

This writes one DOCX per daily lesson. The renderer uses only the Python
standard library, preserves the template package and header artwork, replaces
the template placeholders, and appends the curriculum-backed sections required
by the approved plans.

An audit returns a nonzero exit status when a valid record has objectives
without lecture, lab, or assessment alignment. Invalid or broken source
relationships return exit status 2.

Run the dependency-free test suite with:

```bash
python -m unittest discover -s tests -v
```
