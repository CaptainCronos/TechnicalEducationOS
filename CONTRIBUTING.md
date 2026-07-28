# Contributing

Thank you for helping improve TEOS. By participating, you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Contributions of code, curriculum,
documentation, testing, translation, design review, and reproducible field
experience are all valuable.

## Before starting

Use Python 3.11 or 3.12 and follow the
[Developer Guide](docs/DEVELOPMENT.md). Read the
[project governance](GOVERNANCE.md), repository constitution, relevant
architecture/specification, and current roadmap before changing a contract.

Open an issue before investing in a large feature, new extension boundary,
architecture change, or breaking change. Maintainers will identify whether the
[RFC process](docs/RFC_PROCESS.md) applies. A discussion does not reserve a
feature or guarantee acceptance.

Do not include credentials, private student data, vulnerability details,
proprietary curriculum, or third-party material without documented
redistribution permission. Report vulnerabilities privately through
[SECURITY.md](SECURITY.md).

## Issue workflow

Search open and closed issues first, then use the closest issue form. A useful
issue states the supported TEOS/Python/platform versions, user impact, minimal
safe reproduction or use case, expected result, and relevant logs without
sensitive content.

Maintainers triage issues into:

- **needs information** — the reporter must provide a safe reproduction or
  decision input;
- **accepted/backlog** — valid work without a committed delivery date;
- **scheduled** — assigned to a current milestone and steward;
- **blocked** — waiting on a stated dependency or decision;
- **duplicate/declined** — closed with a link or rationale; or
- **completed** — verified by a merged change or documented resolution.

Priority follows user impact, security/data integrity, learner safety,
regression severity, reach, and availability of a safe workaround. It does not
follow comment volume. The full priority model is in [ROADMAP.md](ROADMAP.md).

## Pull request workflow

1. Create a focused branch from the current default branch.
2. Keep the pull request limited to one coherent outcome. Link the issue and
   accepted RFC/ADR when required.
3. Preserve the ownership and authority boundaries in
   `PROJECT_HANDOFF.md`; generated artifacts are not source records.
4. Add or update tests, documentation, examples, migration notes, and
   `CHANGELOG.md` in the same change when they are affected.
5. Complete the pull request template, including exact verification commands,
   compatibility analysis, and data/license review.
6. Resolve review conversations and rerun checks after substantive updates.
7. Allow a maintainer to merge through the protected workflow. Do not rewrite
   or force-push shared work without coordinating with reviewers.

Draft pull requests are welcome for early feedback but are not approval to merge
or a substitute for an RFC. Maintainers may close inactive pull requests after
summarizing what is needed to resume; useful commits remain attributable to
their authors.

## Review expectations

Reviewers evaluate correctness, contract compatibility, architecture,
traceability, deterministic behavior, failure safety, privacy, licensing,
accessibility, tests, and documentation. Reviews should identify whether a
comment is blocking or optional and explain the user or contract impact.

Authors should respond to each substantive comment with a change, evidence, or
reasoned alternative. Maintainers require all protected checks, conversation
resolution, CODEOWNER review for affected areas, and at least one approving
maintainer. Authors should not approve their own work when another maintainer is
available. Significant changes may require specialist curriculum,
institutional, localization, security, or accessibility review.

## Testing requirements

Run the narrowest relevant tests while developing and the standard gates before
requesting final review:

```bash
python scripts/validate_schemas.py
python -m pytest -m "not performance"
python -m ruff check .
python scripts/check_markdown_links.py
python -m build
python -m twine check dist/*
```

The last two commands are required for packaging, dependency, metadata, or
release changes. Performance tests are required when the change may affect
representative build time. Supported behavior needs positive, negative, and
regression coverage at the appropriate level. Schema and migration changes
need old/new fixtures and failure cases. Never replace a meaningful assertion
or snapshot merely to make a check pass; explain and review the intended
contract change.

## Documentation standards

Use plain language, repository-relative links, copyable commands, stable
terminology, and explicit version context. Update public API/CLI, architecture,
curriculum authoring, examples, support, compatibility, and migration material
whenever the corresponding behavior changes. Meaningful visuals require text
alternatives. Follow [Documentation governance](docs/DOCUMENTATION_GOVERNANCE.md).

Curriculum and institutional claims need provenance and qualified human review.
Examples must be safe, licensed, demonstrative rather than certified, and
executable under the documented support matrix.

## Commit messages

Use an imperative, focused subject no longer than 72 characters. TEOS uses
Conventional Commit prefixes:

```text
feat: add locale capability validation
fix(scheduler): reject overlapping meeting periods
docs: define stable repository compatibility
test(render): lock trace metadata regression
chore(deps): update supported jsonschema range
```

Allowed common types are `feat`, `fix`, `docs`, `test`, `refactor`, `perf`,
`build`, `ci`, and `chore`. Add `!` and a `BREAKING CHANGE:` footer only for a
breaking change approved through the RFC/versioning process. Reference issues
or RFCs in the body when context is not obvious. Merge commits and release
commits may use the repository's established generated format.

## Compatibility and release notes

Changes to public CLI behavior, exported API, schemas, repository records,
curriculum meaning, plugin contracts, or generated semantic formats require
compatibility analysis, tests, and release notes. Follow
[Versioning and compatibility](docs/COMPATIBILITY.md). Architecture and public
contract redesign begins with an RFC, not the implementation pull request.
