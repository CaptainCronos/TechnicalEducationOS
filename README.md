# TechnicalEducationOS

[![Build Status](https://github.com/CaptainCronos/TechnicalEducationOS/actions/workflows/build.yml/badge.svg)](https://github.com/CaptainCronos/TechnicalEducationOS/actions/workflows/build.yml)
[![Test Status](https://github.com/CaptainCronos/TechnicalEducationOS/actions/workflows/tests.yml/badge.svg)](https://github.com/CaptainCronos/TechnicalEducationOS/actions/workflows/tests.yml)
![Coverage](https://img.shields.io/badge/coverage-report%20artifact-blue)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)

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
knowledge/                  curriculum/               operations/       outputs/
standards ──────────┐       competencies                               lesson plans
instructional ──────┼─────> units ──> sessions ─┐                     labs
                    │       modules             ├─> scheduler ───────> assessments
institution profile ┴─> academic calendar ──────┘                     reports/LMS
```

Every renderer consumes a validated curriculum model. No educational artifact
may be generated directly from a slide deck, source PDF, calendar, or template.

## Repository map

- `docs/` — governing architecture, specifications, decisions, and guidance.
- `knowledge/` — registered standards, institutional resources, and
  instructional resources with provenance.
- `curriculum/` — courses, modules, competencies, units, sessions, and mappings.
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

## Current model

Curriculum is authored as competencies, instructional units, and ordered
sessions. Institution Profiles define operating and presentation rules;
Academic Calendars define instructional availability. The Scheduler combines
them without transferring curriculum ownership. Week/day requests are resolved
through a generated schedule before rendering. Legacy week records remain
read-only inputs solely for reproducing approved documents.

See [ROADMAP.md](ROADMAP.md) for the current milestone sequence.

## Quality verification

GitHub Actions builds the wheel and source distribution, runs the full test
suite on Python 3.11 and 3.12, validates JSON Schema contracts, and tests the
installed wheel from a clean environment. JUnit, coverage, wheel, source
distribution, and build-log artifacts are retained for each applicable run.

Recommended default-branch and version-tag rules are documented in
[Repository protection recommendations](docs/branch-protection.md).

The complete wheel-installed reference pipeline, canonical command,
configuration matrix, output manifest, API example, determinism method, and
failure behavior are documented in the
[End-to-End Reference Build runbook](docs/END_TO_END_BUILD.md).

Test categories, regression snapshots, marker commands, performance baselines,
coverage review, and CI behavior are documented in
[Integration and Regression Testing](docs/TESTING.md).
