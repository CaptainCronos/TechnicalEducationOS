# TechnicalEducationOS

TechnicalEducationOS organizes an existing technical curriculum into one
authoritative set of source records. Administrative lesson plans, instructor
lesson plans, assessments, labs, audits, and reports are generated from those
records; generated files are never curriculum sources.

The governing document is [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md). Read it
before proposing architectural changes.

## Phase 1

The active Phase 1 work is intentionally limited to one production-quality
pipeline: J-Tech Administrative Lesson Plans.

1. Record existing course and weekly curriculum without rewriting it.
2. Validate the structured relationships used by each daily plan.
3. Generate a finished J-Tech Administrative Lesson Plan for each lesson.
4. Verify curriculum provenance and presentation quality against approved
   plans.

See [ROADMAP.md](ROADMAP.md) for the prioritized implementation plan and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for repository boundaries. Use
[docs/CURRICULUM_AUTHORING.md](docs/CURRICULUM_AUTHORING.md) when loading the
existing curriculum.

Instructor Lesson Plans, quizzes, labs, PowerPoint outlines, and other output
pipelines remain out of active Phase 1 scope.

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
