# TechnicalEducationOS Roadmap

TEOS has completed its initial engineering implementation. This roadmap lists
post-alpha work only; it is not part of the `v1.2.0-alpha1` release-hardening
scope. Milestone contents may change through normal issue and architecture
review.

## v1.2.0-beta — operational validation

- collect installation and workflow feedback across supported platforms;
- resolve alpha defects without redesigning public APIs;
- exercise real institutional profiles and curriculum repositories;
- improve diagnostics where alpha users cannot act on an error;
- confirm packaging, documentation, accessibility, and upgrade guidance; and
- define the compatibility baseline required for a stable release.

Exit criterion: no known high-severity defects, successful external pilot
builds, stable schemas and public API, and a complete release-candidate audit.

## v1.2.0 — stable release

- complete beta remediation and security review;
- freeze supported CLI, public API, schema, and manifest contracts;
- publish stable installation and compatibility policy;
- validate reproducible signed release artifacts; and
- provide documented migration from the alpha and beta.

Exit criterion: supported production workflows pass on all supported Python
versions with no known release blockers.

## v1.3 — maintainability and interoperability

- prioritize roadmap items using adopter evidence;
- expand standards and LMS interoperability through reviewed adapters;
- improve authoring ergonomics and diagnostics without weakening model
  authority;
- evaluate additional supported Python versions and platforms; and
- retire compatibility paths only through a documented deprecation cycle.

Architecture, API, renderer, generator, and reference-curriculum expansions
require separate proposals and remain outside the alpha release phase.
