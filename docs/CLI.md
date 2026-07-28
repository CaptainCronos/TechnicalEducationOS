# Command-line interface

The `teos` console command and `python -m teos` expose the same interface.

```bash
teos --version
teos --help
teos COMMAND --help
```

## Canonical commands

`teos build --course COURSE_DIRECTORY` loads, validates, and compiles a
canonical course.

`teos build --repository REPOSITORY --schemas SCHEMAS ...` runs the complete
load, validate, compile, schedule, render, and generate pipeline. Institution,
calendar, meeting pattern, locale, theme, renderer, generator, and output
options are required for this form. See the
[reference-build runbook](END_TO_END_BUILD.md) for a complete command.

`teos schedule` maps ordered sessions to an Institution Profile and Academic
Calendar:

```bash
teos schedule \
  --course examples/reference_curriculum/curriculum \
  --institution examples/reference_curriculum/institutions/community-college/institution.json \
  --calendar examples/reference_curriculum/institutions/community-college/calendars/fall-2026-semester.json \
  --meeting-pattern monday-wednesday-evening \
  --output /tmp/teos-schedule.json
```

`teos render` renders administrative, instructor, or lab Markdown for a
canonical session. A session number can be supplied directly; date or week/day
aliases require a generated schedule.

```bash
teos render \
  --course examples/reference_curriculum/curriculum \
  --session 3 \
  --artifact all \
  --output /tmp/teos-rendered
```

## Compatibility commands

`generate`, `audit`, and `generate-administrative` reproduce the deprecated
week-record workflow. They remain available for approved historical documents
but are not the authoring path for new curricula. Run `teos COMMAND --help` for
their arguments.

## Exit behavior

- `0`: success;
- `1`: completed audit with curriculum coverage findings;
- `2`: command usage or controlled input/build error.

Controlled errors are written to standard error, begin with `Error:`, and do
not expose a Python traceback.
