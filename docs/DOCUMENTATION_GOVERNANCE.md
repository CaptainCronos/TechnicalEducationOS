# Documentation governance

Documentation is part of the product. A change is incomplete when users cannot
discover, operate, validate, migrate, or safely evaluate it from the maintained
documentation.

## Authority and status

The authority order is:

1. `PROJECT_HANDOFF.md` and accepted governance policy;
2. accepted ADRs and normative architecture/specifications;
3. public API, CLI, compatibility, support, security, and release policy;
4. task guides, curriculum authoring guidance, and examples;
5. release notes and historical records.

When documents conflict, fix the lower-authority document; do not leave both
interpretations in place. Normative documents use **MUST**, **MUST NOT**,
**SHOULD**, and **MAY** deliberately. Historical files under `docs/archive/`
must not be linked as current instructions.

## Maintained sets

| Set | Maintenance expectation | Review trigger |
|---|---|---|
| README | Accurate purpose, warning, install, quick start, support, and navigation | Every release and public workflow change |
| Developer Guide | Reproducible setup, quality gates, repository rules, and contribution links | Tooling, dependency, CI, or workflow change |
| Architecture and ADRs | Current boundaries, authority, data flow, and rationale | Architectural/RFC change |
| API and CLI reference | Exact public surface, errors, examples, and compatibility status | Any observable API/CLI change |
| Reference Curriculum | Small, licensed, traceable, valid, and executable regression corpus | Schema, compiler, renderer, or curriculum change |
| Examples | Copyable, safe, supported, and clearly distinguished from normative contracts | Feature or documentation release |
| Release and migration docs | Version-specific behavior, known limits, checksums/process, and upgrade path | Every release |

CODEOWNERS route review to maintainers. Curriculum meaning, translations, and
institutional claims also require an appropriately qualified reviewer; a prose
edit cannot silently change approved educational content.

## Change standards

Documentation changes must:

- use repository-relative links and terms consistent with governing documents;
- identify version-specific commands and outputs;
- avoid private learner data, credentials, proprietary content, and claims of
  certification;
- include alt text or an equivalent text explanation for meaningful visuals;
- keep examples minimal, deterministic, and validated where tooling exists;
- update all affected navigation and cross-references; and
- add release notes when behavior, compatibility, support, or migration changes.

Pull requests run `python scripts/check_markdown_links.py`. Code examples should
also be exercised by an automated test or by the documented verification
command when practical. A snapshot update must explain why expected meaning or
format changed.

## Review schedule

Maintainers perform:

- a link and command check continuously in CI;
- a release-readiness review of README, API/CLI, support, compatibility,
  installation, and migration guidance for every release;
- a quarterly rotating review of architecture, developer, curriculum,
  reference, and example documentation; and
- an annual authority, accessibility, licensing/provenance, and archive audit.

Issues discovered in review enter the normal roadmap. Incorrect safety,
security, compatibility, or data-loss instructions are release blockers until
corrected or prominently mitigated.
