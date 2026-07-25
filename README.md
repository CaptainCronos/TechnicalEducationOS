# TechnicalEducationOS

TechnicalEducationOS (TEOS) is a curriculum compiler. It turns educational
standards, institutional constraints, and instructional resources into a
reviewed course blueprint and structured curriculum model, then renders lesson
plans, labs, assessments, student guides, reports, and other artifacts.

The curriculum model is authoritative. Slides and manuals are evidence,
templates are presentation assets, and generated documents are disposable
outputs.

Read the [repository constitution](PROJECT_HANDOFF.md), then the
[architecture overview](docs/architecture/overview.md).

## Compiler pipeline

```text
knowledge/                  curriculum/                 outputs/
standards ──────────┐       blueprints                  lesson plans
institutional ──────┼─────> models ─────> renderers ──> labs
instructional ──────┘       mappings                    assessments
                                                       reports
```

Every renderer consumes a validated curriculum model. No educational artifact
may be generated directly from a slide deck, source PDF, calendar, or template.

## Repository map

- `docs/` — governing architecture, specifications, decisions, and guidance.
- `knowledge/` — registered standards, institutional resources, and
  instructional resources with provenance.
- `curriculum/` — course blueprints, curriculum models, mappings, and legacy
  course/week records.
- `schemas/` — machine-readable data contracts.
- `renderers/` — renderer contracts and artifact-specific implementations.
- `teos/` — current Python validation, audit, and generation application.
- `templates/` — presentation assets; never curriculum sources.
- `institutions/` — institution-specific configuration and overlays.
- `outputs/` — generated, reproducible artifacts.
- `tests/` — automated contract and behavior verification.
- `scripts/` — thin workflow wrappers.

The full ownership and input/output rules are defined in the
[Repository Organization Standard](docs/architecture/repository-organization.md).

## Current transition

The existing DSL204 week records and lesson-plan renderers remain working
assets. They are not being discarded. They represent an earlier source model
that will migrate behind the blueprint and curriculum-model boundary as those
contracts become executable.

See [ROADMAP.md](ROADMAP.md) for the current milestone sequence.
