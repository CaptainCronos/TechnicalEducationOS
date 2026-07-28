# TEOS reference curriculum

## Purpose

This is the canonical compact regression dataset for the implemented TEOS v2
pipeline. It teaches **Introduction to Technical Electricity** from immutable
course, unit, and session records, then combines those records with two
institution profiles and two academic calendars.

The example is intentionally instructional enough to be believable, but it is
not a production course, a substitute for governing safety standards, or a
complete electrical program. Its stable IDs, dates, durations, and wording
should change only through an intentional regression-fixture update.

## Directory structure

```text
examples/reference_curriculum/
├── README.md
├── assessments/
│   └── README.md
├── competencies/
│   └── README.md
├── curriculum/
│   ├── course.json
│   ├── sessions.json
│   └── units/
│       ├── circuit-diagnosis.json
│       └── safe-measurement.json
├── institutions/
│   ├── community-college/
│   │   ├── calendars/fall-2026-semester.json
│   │   └── institution.json
│   └── trade-school/
│       ├── calendars/accelerated-8-week.json
│       └── institution.json
├── locales/
│   ├── en-US.json
│   └── es-US.json
├── resources/
│   └── README.md
├── standards/
│   └── README.md
├── templates/
│   ├── README.md
│   ├── dark/lesson-plan.md
│   └── default/lesson-plan.md
└── themes/
    ├── dark.json
    ├── default.json
    └── institution-branded.json
```

The shape follows the frozen v2 authoring convention. Standards and
competencies live in `course.json`; objectives, resources, lectures,
demonstrations, labs, and assessments live in their owning unit; ordered
sessions live in `sessions.json`. The explanatory directories do not duplicate
those canonical objects.

Generated schedules and artifacts are deliberately not stored here. They are
disposable results and should be written to a temporary or ignored output
directory.

## Curriculum summary

| Item | Count / value |
|---|---:|
| Contact time | 12 hours / 720 minutes |
| Modules | 2 |
| Instructional units | 2 |
| Competencies | 4 |
| Objectives | 6 |
| Sessions | 8 × 90 minutes |
| Lectures | 4 |
| Demonstrations | 4 |
| Labs | 4 |
| Assessments | 4 |
| Session phases | theory, demonstration, lab, assessment, integrated |

The first unit establishes electrical safety and digital multimeter use. The
second applies those skills to series/parallel analysis and fault isolation.
The ordered transition from session 4 to session 5 is the course's instructional
prerequisite. The current v2 model has no explicit prerequisite edge.

## Object relationships

```text
standards
  └── competencies
        └── units
              └── objectives
                    ├── lectures / demonstrations / labs / assessments
                    └── sessions

sessions + institution meeting pattern + academic calendar
  └── generated schedule
        └── resolved session + unit + optional institution
              └── rendered Markdown artifact
```

The example demonstrates:

- one standard mapped to multiple competencies;
- competencies mapped to multiple objectives;
- safety and measurement competencies reused across both units;
- objectives referenced by multiple component types and sessions;
- multiple objectives converging on a single assessment; and
- the same eight sessions scheduled without mutation in two institutions.

See [the standards notes](standards/README.md) and
[competency mapping](competencies/README.md) for the compact mapping tables.

## Institutions, calendars, and presentation resources

| Profile | Pattern | Calendar behavior | Presentation selection |
|---|---|---|---|
| North Valley Community College | Monday/Wednesday evenings at 18:00 | Semester; Labor Day and a faculty day remove meetings | branded theme, `en-US`, HTML preference |
| Metro Trade Institute | Tuesday 09:00/Thursday 13:00 | Accelerated 8-week term; certification day removes a meeting | dark theme, `es-US`, Markdown preference |

Calendar events also include holidays, breaks, closures, and an event explicitly
marked instructional. Only scheduling and presentation configuration vary; both
profiles consume the same curriculum records.

Three parallel theme token catalogs and two key-compatible locale catalogs show
presentation-only variants. English and Spanish translate artifact and field
labels, not curriculum statements. The current v2 renderers do not consume
theme tokens or locale catalogs; the regression test therefore verifies their
shape and curriculum isolation rather than claiming localized or themed output.

## Execute the supported pipeline

Run all commands from the repository root.

### Schema and runtime validation / compilation

The repository-wide schema gate validates production records:

```bash
python scripts/validate_schemas.py
```

The reference regression test validates all eight reference records against the
same frozen schemas. Runtime compilation is:

```bash
python -m teos build \
  --course examples/reference_curriculum/curriculum
```

Expected:

```text
Build passed: tec101 has 2 instructional unit(s) and 8 session(s).
```

`load_curriculum` validates IDs, ownership, objective and assessment
references, contiguous sessions, and exact unit/session time totals. A
successful build has no unresolved runtime references. The v2 records define no
dependency-edge field, so there is no dependency-cycle input to evaluate.

### Scheduling

Community college semester:

```bash
python -m teos schedule \
  --course examples/reference_curriculum/curriculum \
  --institution examples/reference_curriculum/institutions/community-college/institution.json \
  --calendar examples/reference_curriculum/institutions/community-college/calendars/fall-2026-semester.json \
  --meeting-pattern monday-wednesday-evening \
  --output /tmp/tec101-community-schedule.json
```

Expected meeting dates:

```text
2026-08-24, 2026-08-26, 2026-08-31, 2026-09-02,
2026-09-14, 2026-09-16, 2026-09-21, 2026-09-23
```

The Labor Day and faculty development events remove September 7 and 9.

Accelerated trade school:

```bash
python -m teos schedule \
  --course examples/reference_curriculum/curriculum \
  --institution examples/reference_curriculum/institutions/trade-school/institution.json \
  --calendar examples/reference_curriculum/institutions/trade-school/calendars/accelerated-8-week.json \
  --meeting-pattern tuesday-thursday-day \
  --output /tmp/tec101-trade-schedule.json
```

Expected meeting dates:

```text
2026-10-20, 2026-10-22, 2026-10-27, 2026-11-03,
2026-11-05, 2026-11-10, 2026-11-12, 2026-11-17
```

The instructor certification day removes October 29. Tuesday and Thursday
start times remain 09:00 and 13:00 respectively.

### Rendering

Render all implemented canonical session artifacts:

```bash
python -m teos render \
  --course examples/reference_curriculum/curriculum \
  --session 3 \
  --artifact all \
  --institution examples/reference_curriculum/institutions/community-college/institution.json \
  --output /tmp/tec101-rendered
```

Expected files:

```text
tec101-session-003-administrative.md
tec101-session-003-instructor.md
tec101-session-003-lab.md
```

Calendar aliases resolve before rendering:

```bash
python -m teos render \
  --course examples/reference_curriculum/curriculum \
  --week 5 --day 2 \
  --schedule /tmp/tec101-community-schedule.json \
  --artifact administrative \
  --output /tmp/tec101-rendered
```

Expected resolved artifact:

```text
tec101-session-008-administrative.md
```

The regression suite pins SHA-256 digests for all three session 3 intermediate
documents and produces each schedule twice to verify byte-for-byte determinism.

### Regression suite

```bash
python -m pytest tests/test_reference_curriculum.py -q
python -m pytest
```

The focused suite covers frozen schemas, complete compilation, every supported
component collection, cross-unit mapping, both schedules, holiday behavior,
session immutability, renderer hashes, CLI execution, and presentation-resource
isolation.

## CLI compatibility and document generation

The currently implemented canonical commands are `build`, `schedule`, and
`render`. There is no `validate` or `compile` subcommand; `build` performs the
canonical load and validation. The existing `generate` command is a deprecated
v1 week-record compatibility path and cannot consume this v2 reference course.

The canonical renderer currently emits Markdown only. HTML, DOCX, and PDF
generation from a shared rendered intermediate representation is not present in
the repository. The existing DOCX function is tied to the deprecated v1 daily
lesson record and therefore is not used here. Adding adapters or new CLI
commands would change implementation/API scope and is intentionally excluded
from this data-only reference phase.

## Known limitations

- Standard IDs are stored and exercised, but the runtime does not resolve them
  against a governed standard-record type.
- The v2 model has no explicit prerequisite or cross-reference edge and no
  dependency-graph API exposed by the current package.
- Canonical renderers cover administrative lesson plan, instructor guide, and
  lab sheet only. There are no canonical assessment, resource-list,
  student-guide, or course-outline renderers.
- Themes and locales are illustrative presentation resources but are not
  consumed by the current renderer.
- Canonical HTML, DOCX, and PDF document generators are not implemented.
- The course uses only current-limited low-voltage trainers and is not
  production electrical safety instruction.

These gaps are documented rather than bypassed with new domain objects or
public APIs, preserving the frozen architecture and making unsupported success
criteria visible to future phases.
