# TechnicalEducationOS roadmap

TEOS has transitioned from implementation-led construction to
community-driven evolution. The roadmap communicates intent, not a promise of
scope or date. Accepted work still requires an available steward, review,
tests, documentation, and release approval.

## Planning horizons

- **Now** — accepted work for the active milestone with an owner and exit
  evidence.
- **Next** — validated problems likely to enter one of the next two milestones.
- **Later** — worthwhile ideas that need evidence, design, capacity, or a
  maintainer.

Maintainers review horizons at least quarterly and after every release.
Unstaffed work moves back rather than remaining indefinitely “in progress.”

## Now: v1.2.0-beta — operational validation

- collect installation and workflow feedback across the support matrix;
- resolve alpha defects without unnecessary public-contract redesign;
- exercise real institutional profiles and curriculum repositories;
- improve diagnostics where alpha users cannot act on an error;
- confirm packaging, documentation, accessibility, and upgrade guidance; and
- define the compatibility baseline required for stable release.

Exit criterion: no known high-severity defects, successful external pilot
builds, stable intended schemas and public API, and a complete
release-candidate audit.

## Next: v1.2.0 — stable release

- complete beta remediation and security review;
- freeze supported CLI, public API, schema, manifest, and extension contracts;
- publish final installation, support, and compatibility matrices;
- validate reproducible release artifacts; and
- provide documented migration from alpha and beta.

Exit criterion: supported production workflows pass on all Tier 1 Python and OS
combinations with no known release blockers.

## Later: v1.3 and beyond

- prioritize maintainability and authoring ergonomics using adopter evidence;
- expand standards and LMS interoperability through reviewed adapters;
- mature selected generator, renderer, theme, locale, and institution extension
  contracts;
- evaluate additional Tier 1 Python versions and platforms; and
- retire compatibility paths only through the deprecation policy.

No item enters a release solely because it appears in this section.

## Intake and prioritization

Feature requests start with the feature/RFC issue form. They should describe
the user problem, evidence, alternatives, compatibility impact, and a possible
steward rather than only a proposed implementation. Maintainers may request a
small experiment before accepting a lasting contract.

Bugs are prioritized as:

| Priority | Meaning | Planning response |
|---|---|---|
| P0 critical | Active security compromise, likely data loss/corruption, or severe learner-safety risk with no mitigation | Private/emergency handling; interrupt normal release work |
| P1 high | Supported workflow unusable, major regression, or broad incorrect output without a practical workaround | Target current patch/beta milestone |
| P2 normal | Material defect with a workaround or limited affected surface | Prioritize against current/next capacity |
| P3 low | Cosmetic, narrow edge case, or low-impact improvement | Backlog or contributor-ready work |

Severity, reach, reproducibility, safety, and workaround quality determine
priority. Security issues are reported privately and may use a different public
label after coordinated disclosure.

## RFCs and architectural changes

Public contract, governance, boundary, and major architectural proposals use
the [RFC process](docs/RFC_PROCESS.md). Accepted architecture also receives an
ADR under `docs/decisions/`. An RFC must identify a long-term owner,
compatibility and migration, tests, documentation, and retirement conditions;
acceptance does not guarantee scheduling.

## Major-version planning

A major version begins with a public umbrella RFC that inventories proposed
breaks, user evidence, rejected compatible alternatives, migration tooling,
ecosystem impact, and a support timeline. Maintainers group changes so users do
not face repeated avoidable migrations. At least one preview release and a
documented migration rehearsal precede stable release. Stable prior lines
remain supported according to [the support policy](docs/SUPPORT.md).

Milestone changes and deferrals are recorded in issues and summarized in
release notes. Emergency security work may remain private until disclosure is
safe.
