# Long-term maintenance

## Operating rhythm

| Frequency | Maintenance work |
|---|---|
| Continuous | Triage new issues/PRs, protect secrets and private data, keep required checks passing |
| Monthly | Review dependencies and workflow actions, stale issues, flaky tests, security alerts, and support trends |
| Quarterly | Audit licenses, dependency health, supported platforms, performance baselines, roadmap, and one rotating documentation set |
| Each release | Apply `docs/RELEASING.md`, review compatibility/deprecations, test migrations, update support and release notes |
| Annually | Review governance, maintainer access, branch/tag protection, threat model, documentation authority, archival policy, and stewardship risks |

Maintenance is issue-driven and capacity-aware. Automation may open or prepare
updates, but a maintainer remains accountable for provenance, compatibility,
tests, and merge decisions.

## Repository health

Maintainers should keep the default branch releasable, use protected pull
requests, minimize privileged automation, pin or review third-party workflow
actions, preserve deterministic fixtures, and keep generated artifacts out of
source control. Temporary bypasses and emergency actions must be documented and
reviewed afterward.

Stale issues are closed only after checking whether the underlying need still
exists. Accepted roadmap work without an active steward returns to the backlog;
an issue assignment is not a permanent claim on the design.

## Audits

Periodic audits cover:

- public contract and documentation drift;
- dependency vulnerabilities, licenses, abandonment, and minimum versions;
- secret scanning, release permissions, artifact provenance, and recovery
  procedures;
- schema migrations, regression snapshots, deterministic builds, and backup of
  irreplaceable governance records;
- accessibility, localization, institutional authority, and curriculum source
  provenance; and
- maintainer concentration, inactive access, and succession readiness.

Findings receive an owner, severity, target milestone, and verification method.
Material unresolved risks appear in release notes rather than being hidden by
schedule pressure.

## Stewardship and continuity

At least two maintainers should understand releases, security handling, and
repository recovery whenever the contributor base permits. Privileged accounts
should use strong authentication and least privilege. Release and security
procedures must remain executable from repository documentation rather than
personal memory.

If maintainers can no longer sustain the project, they should announce the
status, stop promising unsupported releases, seek new qualified stewards, and
archive the repository only after documenting support and security
consequences. Project name, package indexes, signing identity, and private
security reports must transfer through an auditable process; they must not be
silently handed to an unknown party.

Funding or institutional sponsorship may support work but does not buy a merge,
security priority, certification claim, or exemption from governance.
