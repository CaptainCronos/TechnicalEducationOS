# TechnicalEducationOS

TechnicalEducationOS organizes an existing technical curriculum into one
authoritative set of source records. Administrative lesson plans, instructor
lesson plans, assessments, labs, audits, and reports are generated from those
records; generated files are never curriculum sources.

The governing document is [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md). Read it
before proposing architectural changes.

## Phase 1

Phase 1 supports the immediate Weeks 8–11 lesson-planning workflow:

1. Record existing course and weekly curriculum without rewriting it.
2. Validate relationships between objectives, instruction, labs, assessments,
   and competencies.
3. Generate consistent instructional documents.
4. Measure whether the workflow reduces weekly planning time toward one hour.

See [ROADMAP.md](ROADMAP.md) for the prioritized implementation plan and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for repository boundaries. Use
[docs/CURRICULUM_AUTHORING.md](docs/CURRICULUM_AUTHORING.md) when loading the
existing curriculum.

## Repository map

- `curriculum/` — authoritative, institution-independent curriculum records.
- `institutions/` — optional institution-specific presentation and
  administrative overlays.
- `schemas/` — machine-readable contracts for source records.
- `teos/` — validation, audit, and generation code.
- `tests/` — automated behavior checks using synthetic fixtures.
- `outputs/` — generated, disposable documents (ignored by Git).
- `docs/decisions/` — significant architectural decision records.
- `scripts/` — thin command wrappers only when they improve the workflow.

Do not manually edit generated files in `outputs/`.
