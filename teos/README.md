# TEOS application

The application validates canonical course/unit/session records, schedules
sessions onto institution calendars, resolves calendar aliases, and renders
artifacts from the resolved session.

```bash
python -m teos build --course curriculum/courses/dsl204

python -m teos schedule \
  --course curriculum/courses/dsl204 \
  --calendar institutions/j-tech/calendars/dsl204-fall-2026.json \
  --output outputs/dsl204-fall-2026-schedule.json

python -m teos render \
  --course curriculum/courses/dsl204 \
  --session 2 \
  --artifact all

python -m teos render \
  --course curriculum/courses/dsl204 \
  --week 5 --day 2 \
  --schedule outputs/dsl204-fall-2026-schedule.json
```

The scheduler skips unavailable slots without changing curriculum. Renderers
receive only a resolved session and its instructional unit; they never consume
weeks or calendar dates.

`generate`, `audit`, and `generate-administrative` are deprecated compatibility
commands for reproducing approved week-based artifacts. Do not use them for new
curriculum.

Run the dependency-free test suite with:

```bash
python -m unittest discover -s tests -v
```
