# Changelog

Notable project changes are recorded here. TEOS follows semantic versioning;
Python distribution versions use PEP 440 pre-release notation.

## [Unreleased]

### Added

- project governance, RFC, compatibility, support, plugin ecosystem,
  documentation, and long-term maintenance policies;
- community-driven roadmap intake, prioritization, and major-version planning;
  and
- feature/RFC issue and expanded pull request review guidance.

### Changed

- contribution, release, security, conduct, and community templates now share
  explicit triage, review, cadence, disclosure, and compatibility standards.

## [1.2.0-alpha1] - 2026-07-28

First public alpha release.

### Added

- immutable curriculum records, validation, compilation, scheduling, rendering,
  and deterministic physical document generation;
- public `BuildConfig`, `BuildResult`, `BuildError`, and `build()` application
  API;
- `teos` CLI for canonical builds, scheduling, rendering, and maintained legacy
  reproduction commands;
- Institution Profiles, Academic Calendars, locale catalogs, themes, templates,
  and renderer/generator registries;
- canonical Reference Curriculum and permanent regression snapshots;
- wheel-installed end-to-end, artifact-validation, integration, regression,
  performance, and negative-input test suites; and
- packaging, installation, release, security, contributing, and community
  documentation.

### Changed

- package version advanced from the internal `0.1.0` snapshot to PEP 440
  `1.2.0a1`, corresponding to release `v1.2.0-alpha1`;
- generated and golden documents were removed from source/output locations or
  isolated as test fixtures;
- licensing metadata and repository license now consistently use MIT; and
- repository scaffolding and historical phase material were separated from
  current developer guidance.

### Compatibility

- week-record `generate`, `audit`, and `generate-administrative` commands remain
  deprecated compatibility paths;
- `v1.2.0-alpha1` does not promise stable schemas or public behavior until the
  beta compatibility review; and
- there is no supported in-place migration from unpublished `0.1.0`
  development snapshots.

[Unreleased]: https://github.com/CaptainCronos/TechnicalEducationOS/compare/v1.2.0-alpha1...HEAD
[1.2.0-alpha1]: https://github.com/CaptainCronos/TechnicalEducationOS/releases/tag/v1.2.0-alpha1
