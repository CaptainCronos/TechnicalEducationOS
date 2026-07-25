# DSL204

DSL204 demonstrates the canonical session-based curriculum:

- `course.json` owns course metadata, standards, competencies, and modules.
- `units/` owns reusable instructional content.
- `sessions.json` divides units into ordered instructional meetings.
- `weeks/` is deprecated compatibility data for approved historical documents.

The J-Tech profile and Fall 2026 calendar are deliberately outside the
curriculum under `institutions/j-tech/`.

Build and schedule it with:

```bash
python -m teos build --course curriculum/courses/dsl204
python -m teos schedule \
  --course curriculum/courses/dsl204 \
  --institution institutions/j-tech/institution.json \
  --calendar institutions/j-tech/calendars/fall-2026.json \
  --meeting-pattern thursday-friday-am \
  --output outputs/dsl204-fall-2026-schedule.json
```
