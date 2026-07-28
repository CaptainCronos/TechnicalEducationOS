# Plugin ecosystem governance

“Plugin” is an ecosystem term for a separately maintained extension. It does
not imply that every extension is executable Python or that the current alpha
exposes a stable plugin-loading API.

## Extension categories

| Category | Owns | Must not do |
|---|---|---|
| Generator | Converts renderer records to a physical format | Invent or alter curriculum meaning |
| Renderer | Projects approved curriculum into an artifact-specific record | Read unregistered evidence directly or bypass validation |
| Theme/template | Presentation tokens, layout, and branding | Supply objectives, assessments, safety rules, or other curriculum facts |
| Institution profile | Institution identity, policy, scheduling, and presentation configuration | Redefine institution-independent curriculum |
| Localization pack | Translated labels and presentation strings | Reassign stable IDs or silently change instructional meaning |
| Future extension | A capability accepted through RFC review | Cross authority or security boundaries without an explicit contract |

## Contract maturity

Each extension must declare the TEOS versions, contract/schema versions,
capability IDs, and platforms it has tested. Maturity is one of:

- **experimental** — may change in pre-releases; consumers pin exact versions;
- **provisional** — documented and tested, but not yet covered by the full
  stable guarantee; or
- **stable** — explicitly listed as public and governed by
  `docs/COMPATIBILITY.md`.

The current third-party Python renderer and generator integration boundary is
experimental. Data extensions follow the maturity of their published schema.
Use capability negotiation or explicit metadata rather than implementation
inspection.

## Requirements for third-party extensions

An extension publisher should provide:

- a unique, non-misleading ID and clear statement that the extension is not
  official TEOS software;
- an OSI-approved code license and explicit licenses/provenance for data,
  fonts, media, templates, translations, and curriculum sources;
- a compatibility manifest, changelog, installation instructions, and support
  contact;
- isolated tests against supported TEOS versions plus representative invalid
  inputs;
- deterministic output where the same approved inputs are expected to produce
  the same result;
- actionable failure behavior without secrets, personal data, or proprietary
  content in logs; and
- security reporting and dependency-update practices appropriate to its risk.

Extensions must not claim TEOS certification, collect or transmit data without
clear consent, execute untrusted curriculum as code, bypass schema validation,
or present generated instructional content as automatically approved.
Institution profiles and localization packs require review by people authorized
to represent the institution or language community.

## Core listing and adoption

The project does not currently operate an official marketplace. A link or
discussion in project spaces is not endorsement. Maintainers may remove
ecosystem references for abandonment, incompatibility, deceptive naming,
license problems, security risk, or Code of Conduct violations.

Moving an extension or contract into the core repository requires an RFC,
identified long-term maintainer, compatible license and provenance, conformance
tests, documentation, security review, and evidence that central maintenance is
better than an independent package. Core adoption transfers maintenance
responsibility; popularity alone is insufficient.

## Compatibility and incident handling

Extension authors own compatibility with TEOS and should test upcoming
pre-releases. TEOS release notes call out known ecosystem breaks. Stable
extension contracts use normal deprecation periods; experimental contracts may
change with pre-release notice.

Suspected vulnerabilities in TEOS belong in the private process described by
`SECURITY.md`. Vulnerabilities confined to a third-party extension go to its
publisher. When impact crosses the boundary, both teams should coordinate
disclosure and mitigations without publishing exploitable details early.
