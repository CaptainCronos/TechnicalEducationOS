# DSL204

DSL204 demonstrates the canonical session-based curriculum:

- `course.json` owns course metadata, standards, competencies, and modules.
- `units/` owns reusable instructional content.
- `sessions.json` divides units into ordered instructional meetings.
- `weeks/` is deprecated compatibility data for approved historical documents.

The J-Tech example calendar is deliberately outside the curriculum at
`institutions/j-tech/calendars/dsl204-fall-2026.json`.

Build and schedule it with:

```bash
python -m teos build --course curriculum/courses/dsl204
python -m teos schedule \
  --course curriculum/courses/dsl204 \
  --calendar institutions/j-tech/calendars/dsl204-fall-2026.json \
  --output outputs/dsl204-fall-2026-schedule.json
```
