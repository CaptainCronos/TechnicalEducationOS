# TEOS application

This package contains the Phase 1 command-line workflow, validation, audits,
and document renderers. It reads authoritative records and writes only
generated outputs.

From the repository root:

```bash
python -m teos audit --course curriculum/courses/COURSE_ID --week 8
python -m teos generate --course curriculum/courses/COURSE_ID --week 8
```

Add `--institution institutions/INSTITUTION_ID.json` to apply an optional
administrative overlay. Generated Markdown is written to `outputs/` by default.

An audit returns a nonzero exit status when a valid record has objectives
without lecture, lab, or assessment alignment. Invalid or broken source
relationships return exit status 2.

Run the dependency-free test suite with:

```bash
python -m unittest discover -s tests -v
```
