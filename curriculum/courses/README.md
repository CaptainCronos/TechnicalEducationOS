# Canonical courses

Each course directory owns calendar-independent curriculum:

```text
course.json
units/*.json
sessions.json
weeks/*.json         # deprecated compatibility records, when present
```

Units and sessions are authoritative. Institution calendars live below
`institutions/`, map sessions to dates, and do not own instructional content.
Generated schedules and documents belong in `outputs/`.
