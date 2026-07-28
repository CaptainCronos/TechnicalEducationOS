# DSL204

DSL204 demonstrates the canonical session-based curriculum:

- `course.json` owns course metadata, standards, competencies, and modules.
- `units/` owns reusable instructional content.
- `sessions.json` divides units into ordered instructional meetings.
- `lessons/` contains renderer-independent Canonical Lesson Model validation
  records. The Week 4 Day 1 record remains `in_review` until it is reconciled
  with the approved source lesson.
- `weeks/` is deprecated compatibility data for approved historical documents.

The J-Tech profile and Fall 2026 calendar are deliberately outside the
curriculum under `institutions/j-tech/`.

The initial CLM validation dataset is
[`lessons/week-04-day-01.yaml`](lessons/week-04-day-01.yaml). Its mapping and
validation findings are documented in
[`docs/reviews/dsl204-week-04-day-01-clm-validation.md`](../../../docs/reviews/dsl204-week-04-day-01-clm-validation.md).

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
