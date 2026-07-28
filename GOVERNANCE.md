# Project governance

## Mission and vision

TechnicalEducationOS (TEOS) is a curriculum compiler. Its mission is to reduce
the effort required to create and maintain technical-education curricula while
preserving instructional quality, source evidence, institutional control, and
human review.

The project's vision is an open, trustworthy foundation on which educators,
institutions, and tool builders can collaborate without coupling curriculum
meaning to one institution, presentation format, or vendor.

The architectural constitution in [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md)
governs the meaning and authority of project records. This document governs the
people and process used to evolve them.

## Scope

TEOS maintains:

- contracts for knowledge sources, blueprints, curriculum, institutions, and
  schedules;
- deterministic validation, compilation, rendering, and generation tools;
- a small public CLI and Python application API;
- reference schemas, examples, curriculum, profiles, themes, locales, and
  templates that exercise supported contracts; and
- documentation, tests, release tooling, and migration guidance needed to use
  those capabilities safely.

The project may add integrations when they preserve source authority,
traceability, reproducibility, privacy, accessibility, and human approval.

## Non-goals

TEOS is not:

- an LMS, student information system, content marketplace, or student-record
  store;
- an authority that certifies curriculum, regulatory compliance, instructor
  judgment, or learner safety;
- a mechanism for deriving curriculum facts from templates or generated files;
- a guarantee that one curriculum or institutional profile fits every
  jurisdiction; or
- a reason to embed proprietary, personal, or unlicensed source material in
  the public repository.

## Roles

Anyone may participate as a **contributor** by opening issues, reviewing work,
or proposing changes. A **maintainer** is a contributor with repository
authority and an established record of sound technical and community judgment.
A **release maintainer** is a maintainer explicitly trusted to manage protected
tags and releases. Maintainers may delegate triage or subsystem ownership
without delegating final repository accountability.

The current maintainers and path ownership are represented by
[CODEOWNERS](.github/CODEOWNERS). That file routes review; it does not override
this policy or make a path owner the sole source of ideas.

Maintainers are responsible for:

- applying this governance and the Code of Conduct consistently;
- triaging issues and security reports without exposing private information;
- reviewing compatibility, architecture, educational safety, licensing, and
  operational risk;
- keeping protected branches, required checks, releases, and documentation
  healthy;
- recording significant decisions and disclosing relevant conflicts of
  interest; and
- recruiting, mentoring, and offboarding maintainers so the project is not
  dependent on one person's undocumented knowledge.

## Decision process

TEOS uses public, evidence-based discussion and **lazy consensus**: a proposal
may proceed when relevant checks pass, affected reviewers have had a reasonable
opportunity to respond, and no unresolved, reasoned objection remains.
Silence never overrides a required approval.

| Change | Required record | Approval |
|---|---|---|
| Small fix, documentation correction, test, or internal refactor | Issue or pull request | One maintainer |
| User-visible compatible feature | Issue and pull request | One maintainer and affected CODEOWNERS |
| Public contract, schema, repository boundary, or governance change | Accepted RFC; ADR when architecture is affected | Two maintainers when available; otherwise the sole maintainer documents the decision and review period |
| Breaking change or major release | Accepted RFC, migration plan, and release plan | Maintainer consensus |
| Security response | Private advisory until disclosure is safe | Security/release maintainer |

A maintainer merges only after required checks, review, and conversations are
complete. The author should not be the only approver when another maintainer is
available. Maintainers must recuse themselves from a final decision when a
financial, employment, institutional, or personal conflict could reasonably
undermine trust. If consensus cannot be reached, the deciding maintainer must
document the alternatives, evidence, and disposition; postponing a change is
preferred to making an irreversible decision without adequate review.

The [RFC process](docs/RFC_PROCESS.md) provides review periods and escalation
for consequential proposals. Accepted architectural decisions are recorded in
`docs/decisions/`.

## Maintainer lifecycle

Existing maintainers nominate new maintainers based on sustained contribution,
review quality, community conduct, and demonstrated care for compatibility.
The nomination and decision are public unless privacy or safety requires
otherwise. Access is granted at the least privilege needed.

A maintainer may step down at any time. Maintainers who expect to be inactive
for three months should announce it and transfer active responsibilities.
After six months without project activity or response, the remaining
maintainers may move the person to emeritus status and remove privileged
access. Access may be suspended immediately for account compromise, security
risk, or a Code of Conduct enforcement action.

When only one maintainer is active, major and governance proposals remain open
for public review for at least 14 calendar days unless a security or service
emergency makes delay unsafe. The sole maintainer records the final rationale.

## Amendments

Governance changes use the RFC process and a pull request. They require the same
review as a public contract change. Emergency security or conduct procedures
may be applied immediately, but the permanent policy change must be reviewed
after the emergency.
