# Support policy

## Support matrix

The matrix describes the `v1.2.0-alpha1` line. A release note may narrow or
expand it after its release validation completes.

| Component | Level | Policy |
|---|---|---|
| CPython 3.11 | Supported | Full automated test and distribution-install validation |
| CPython 3.12 | Supported | Full automated test and distribution-install validation |
| Linux on the current GitHub-hosted Ubuntu runner | Tier 1 | CI-verified CLI, API, package, and reference build |
| Other maintained Linux distributions | Tier 2 | Expected to work on supported CPython; fixes are best effort unless reproduced in Tier 1 |
| macOS and Windows | Community-supported | Portable behavior is intended, but releases are not yet CI-certified on these systems |
| PyPy and other Python implementations | Unsupported | Reports and contributions are welcome; no release guarantee |

“Supported” means maintainers accept reproducible defects, test fixes on the
published matrix, and include the surface in release decisions. It does not
guarantee a response time or certify generated curriculum for instructional
use. Native applications used to inspect or convert generated files are
outside the TEOS support matrix.

Adding a Tier 1 platform requires repeatable CI coverage for installation, the
public CLI/API, and the Reference Curriculum. Removing one is a compatibility
change announced before the affected release when practical.

## Python lifecycle

TEOS supports at least two adjacent CPython minor versions when feasible. A new
Python version is added only after dependencies and the release validation
matrix pass. A Python version may be removed in a minor release after its
upstream security support ends, with at least one minor release of notice when
practical. The `requires-python` package metadata, CI, README, installation
guide, and this matrix must agree.

## Release support windows

- Alpha and beta releases are supported until superseded by the next release
  in the same intended series, with critical security handling as described in
  `SECURITY.md`.
- After stable release, the latest minor in a major series receives bug and
  security fixes. The immediately preceding minor receives critical security
  and data-integrity fixes for six months after supersession.
- Patch releases supersede earlier patches in the same minor line.
- Major lines outside an announced window are unsupported.

TEOS has no designated Long-Term Support release today. An LTS designation must
be announced in advance with a named maintenance owner, supported platform and
dependency matrix, minimum security window, and funding or capacity plan. LTS
is never inferred from adoption or version number.

## Dependencies

Runtime dependencies use bounded compatible ranges. Maintainers:

- review automated dependency and workflow-action updates at least monthly;
- perform a broader dependency, license, and stale-package review quarterly;
- test minimum and selected current dependency versions before widening or
  narrowing a public range;
- avoid speculative major upgrades in patch releases; and
- record user-visible dependency constraints in release notes.

Security updates are assessed as soon as practical. A vulnerable dependency
that is reachable in supported use is upgraded, constrained, patched, or
documented with mitigation according to the security process. Lock files, if
introduced for developer or release tooling, do not replace the declared
package compatibility ranges.

## Requests and escalation

Use the issue tracker for reproducible support questions and defects that
contain no private data. Maintainers prioritize by the
[roadmap process](../ROADMAP.md), not by organization size or repeated
requests. Vulnerabilities and sensitive reports use
[the private security process](../SECURITY.md).
