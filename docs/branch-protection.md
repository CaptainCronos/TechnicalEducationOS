# Repository protection recommendations

These settings are recommendations for repository administrators. The CI phase
does not apply or modify GitHub repository settings.

## Default branch

Protect the default branch with a ruleset that:

- requires a pull request and at least one approving review before merge;
- dismisses stale approvals when new commits are pushed;
- requires conversation resolution before merge;
- requires the branch to be up to date before merge;
- requires successful `Build`, `Tests`, `Quality`, and `Release Validation`
  checks;
- blocks force pushes and branch deletion;
- requires linear history;
- applies to administrators unless an explicitly audited emergency bypass is
  necessary.

After the first workflow run, select the individual job checks exposed by the
four workflows. In particular, require both supported Python-version jobs from
`Tests` and `Release Validation`.

## Version tags

Protect tags matching `v*` with a repository ruleset that:

- restricts tag creation, update, and deletion to release maintainers;
- blocks force updates;
- allows bypass only for an explicitly named emergency role.

Release and deployment automation are intentionally outside the scope of this
phase.
