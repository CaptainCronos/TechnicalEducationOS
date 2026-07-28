# Request for Comments process

An RFC is the public design record for a consequential change before its
implementation is treated as decided. It complements an Architecture Decision
Record (ADR): the RFC captures the proposal and discussion; an ADR records an
accepted architectural decision in its lasting context.

## When an RFC is required

Use an RFC for:

- a new or breaking public API, CLI, schema, repository, curriculum, or plugin
  contract;
- a change to authority, ownership, data flow, privacy, or security boundaries;
- a new top-level subsystem or extension category;
- governance, compatibility, support, or release-policy changes; or
- major-version planning and removal of stable behavior.

Small fixes, compatible implementation details, documentation corrections, and
work already required by an accepted contract do not need an RFC.

## Lifecycle

1. **Discuss.** Open a feature/RFC issue describing the problem, users,
   constraints, and alternatives. A maintainer confirms whether an RFC is
   needed and assigns a sponsor.
2. **Draft.** Copy `docs/rfcs/0000-template.md` to a pull request using the next
   available four-digit number. Use status `Draft`; do not include the main
   implementation.
3. **Review.** The sponsor requests affected CODEOWNER, compatibility,
   curriculum, security, and documentation review. The normal comment period
   is at least 7 calendar days; governance, breaking, and major-version RFCs
   receive at least 14.
4. **Resolve.** Update the RFC with material alternatives and the disposition
   of objections. Lack of comments is not approval.
5. **Decide.** Maintainers mark the RFC `Accepted`, `Rejected`, or `Withdrawn`
   under [project governance](../GOVERNANCE.md). Accepted architecture changes
   also add or identify an ADR.
6. **Implement.** Linked pull requests deliver the change, tests, migration,
   documentation, and release notes. Material design changes return to RFC
   review.
7. **Finalize.** The RFC becomes `Implemented` when all acceptance criteria are
   present in a release, or `Superseded` when a later RFC replaces it.

Security-sensitive designs may begin in a private advisory. Maintainers publish
a redacted or complete RFC when disclosure is safe.

## Decision criteria

Reviewers consider mission fit, evidence of user need, compatibility and
migration cost, educational and learner safety, privacy, security,
accessibility, maintainability, testability, ecosystem impact, and a realistic
stewardship owner. Acceptance authorizes the design direction, not an
unreviewed merge or guaranteed delivery date.

RFC numbers are never reused. Rejected and withdrawn RFCs remain in the
repository because they preserve decision context.
