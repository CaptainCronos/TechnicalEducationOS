# Security policy

## Supported versions

Security fixes are produced only for versions inside the
[published support window](docs/SUPPORT.md).

| Version | Security support |
|---|---|
| `1.2.0-alpha1` | Yes, until superseded by the next `1.2.0` pre-release or stable release |
| Earlier development snapshots | No |

This table is updated as part of every release. Users should run the latest
patch or pre-release in a supported line because earlier patches are
superseded.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/CaptainCronos/TechnicalEducationOS/security/advisories/new).
If that feature is unavailable, contact the maintainer privately through the
address published on the maintainer's GitHub profile. Do not open a public
issue, pull request, discussion, or test containing exploitable details,
credentials, private learner data, or proprietary curriculum.

Include, when safely available:

- affected TEOS/package, Python, OS, and dependency versions;
- the affected API, CLI, input, artifact, or extension boundary;
- minimal reproduction steps or a private proof of concept;
- likely confidentiality, integrity, availability, privacy, or learner-safety
  impact;
- whether exploitation is known in the wild; and
- suggested mitigation or disclosure constraints.

Maintainers aim to acknowledge a complete report within seven calendar days.
Acknowledgment is not a promise of a fix date. The reporter and maintainer
should agree on a safe channel and coordinated disclosure plan.

## Response process

Security maintainers will:

1. preserve the report privately and remove unnecessary sensitive data;
2. validate scope, severity, affected supported versions, and extension impact;
3. prepare the narrowest safe fix and regression evidence in private when
   necessary;
4. coordinate fixes with dependency or extension maintainers without exposing
   the reporter or exploit;
5. build and verify artifacts through the security release path; and
6. publish an advisory, affected versions, credits if desired, mitigations, and
   fixed versions when disclosure is safe.

Critical active exploitation, likely data loss, credential exposure, or severe
learner-safety impact interrupts normal roadmap work. Lower-severity issues are
scheduled by exploitability, reach, impact, available mitigation, and release
risk. A release may be delayed, functionality disabled, or a package yanked
when that is safer than shipping an incomplete fix.

No one is asked to conceal a vulnerability indefinitely. If coordination
stalls, participants should provide reasonable notice before disclosure and
avoid publishing secrets, private data, or unnecessary exploit detail.

## Scope

In scope are vulnerabilities in supported TEOS code, release artifacts,
workflows, schemas, and official repository data that cross a security,
privacy, integrity, or trust boundary. Examples include path traversal,
arbitrary code execution, unsafe parsing, secret leakage, dependency
compromise, release tampering, and generation that silently violates validated
authority or traceability.

Content-quality bugs without a security or learner-safety impact belong in the
public issue tracker. Vulnerabilities confined to third-party extensions should
be reported to their publisher; cross-boundary issues should be coordinated
with both projects under [plugin governance](docs/PLUGIN_GOVERNANCE.md).

Never commit secrets, passwords, private keys, tokens, production student
records, or environment files. Generated curriculum must be reviewed by
authorized people before instructional use. The project does not offer a bug
bounty and cannot authorize testing against systems or data it does not own.
