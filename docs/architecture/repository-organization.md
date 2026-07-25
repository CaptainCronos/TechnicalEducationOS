# Repository Organization Standard

Status: Governing  
Version: 2.0

## Ownership rule

Each directory owns one class of information. A file belongs where its
authoritative meaning is maintained, not where a consumer happens to use it.
Every new top-level directory MUST document its purpose, accepted inputs,
produced outputs, and prohibited content.

## Directory contract

| Path | Owns | Inputs | Outputs / consumers |
|---|---|---|---|
| `docs/` | governing prose, decisions, and authoring guidance | approved architectural decisions | people and implementation work |
| `knowledge/standards/` | registered educational and regulatory requirements | ASE, FMCSA, OSHA, OEM, and institutional outcomes | blueprint and model references |
| `knowledge/institutional/` | calendars, schedules, policies, and delivery constraints | approved institutional records | Scheduler inputs |
| `knowledge/instructional/` | teaching resources and source locators | presentations, notes, manuals, labs, videos | reviewed model references |
| `curriculum/blueprints/` | reusable design inputs without calendar ownership | knowledge records and course requirements | curriculum compiler |
| `curriculum/models/` | approved renderer-ready curriculum meaning | approved blueprint and reviewed evidence | validators, renderers, audits |
| `curriculum/mappings/` | explicit crosswalks and migration maps | stable IDs from two or more authorities | compilation and impact analysis |
| `curriculum/courses/` | courses, modules, competencies, units, and sessions | compiled/reviewed curriculum | validators, Scheduler, renderers |
| `schemas/` | machine-readable contracts | governing specifications | validators, editors, automation |
| `renderers/` | artifact projection contracts and implementations | approved model plus presentation configuration | generated artifacts |
| `teos/` | validation, Scheduler, alias resolver, renderers, and compatibility pipeline | validated source records and configuration | schedules, audits, and artifacts |
| `templates/` | layout, styles, labels, and branding assets | approved presentation designs | renderers |
| `institutions/` | institution configuration, academic calendars, and administrative overlays | approved institution data | Scheduler and presentation adapters |
| `outputs/` | generated artifacts and build manifests | renderer results | instructors, students, reviewers, integrations |
| `tests/` | synthetic fixtures and automated verification | schemas, compiler, and renderer behavior | validation evidence |
| `scripts/` | thin repeatable workflow entry points | supported commands | developer/operator workflows |

## Repository tree

```text
docs/
  architecture/
  blueprints/
  decisions/
  specifications/
  standards/
knowledge/
  standards/
  institutional/
  instructional/
curriculum/
  blueprints/
  models/
  mappings/
  courses/
    <course-id>/
      course.json
      units/
      sessions.json
renderers/
outputs/
schemas/
templates/
institutions/
teos/
tests/
scripts/
```

## Source-package organization

Knowledge packages SHOULD use:

```text
knowledge/<layer>/<source-id>/
  manifest.json
  original/             # when storage and licensing permit
  extracted/            # normalized, addressable representations
  reviews/              # extraction or interpretation dispositions
```

Course data SHOULD be grouped by stable course ID beneath each curriculum
area. Exact filenames are defined by future schemas, not inferred from display
titles.

## Generated and derived data

- `outputs/` is disposable and ignored except for its documentation.
- Blueprints and curriculum models are derived but governed. Approved versions
  are first-class project assets and are not disposable build output.
- Extracted knowledge records are derived from originals but retain provenance
  and may be reviewed independently.
- Mapping files are explicit reviewed decisions; they are not caches.

## Prohibited placement

- No curriculum facts in templates or renderer source.
- No generated documents under `curriculum/` or `knowledge/`.
- No unregistered standards or instructional source files under `curriculum/`.
- No institution-specific branding in institution-independent curriculum
  models.
- No production student records, credentials, or secrets anywhere in the
  repository.

## Naming and versioning

- Directory and record IDs use lowercase ASCII letters, digits, dots, hyphens,
  or underscores according to their schemas.
- Display titles may use normal capitalization and punctuation.
- Schema version and record version are separate concepts.
- Replacing a source file without changing its manifest version is prohibited.
- Generated filenames are presentation concerns and MUST NOT serve as record
  identifiers.
