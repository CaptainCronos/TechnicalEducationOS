# Release procedure

This checklist is the permanent TEOS release procedure. Perform it from a clean
checkout on a dedicated release branch. Replace the example version and tag for
later releases.

## 1. Prepare

- [ ] Confirm the intended semantic version and PEP 440 package equivalent
  (`v1.2.0-alpha1` / `1.2.0a1`).
- [ ] Review open issues, security reports, deprecations, and known limitations.
- [ ] Verify the GitHub description, homepage, topics, default branch, license
  detection, vulnerability reporting, and repository visibility.
- [ ] Update `pyproject.toml`, `teos.__version__`, `CHANGELOG.md`, documentation
  version references, and the release-notes draft.
- [ ] Confirm runtime and optional dependency ranges and review dependency
  licenses and advisories.
- [ ] Run `python scripts/check_markdown_links.py`.
- [ ] Confirm `git status --short` contains only intended release changes.

## 2. Verify quality

- [ ] Create a clean Python 3.11 environment and install `-e ".[dev]"`.
- [ ] Run `python scripts/validate_schemas.py`.
- [ ] Run `python -m ruff check .`.
- [ ] Run `python -m pytest -m "not performance" --cov=teos
  --cov-report=term-missing`.
- [ ] Run `python -m pytest -m performance -s` and review regressions.
- [ ] Repeat the standard suite on every supported Python version or confirm the
  protected CI matrix passed.
- [ ] Confirm all warnings are treated as errors and no unexpected warnings
  remain.

## 3. Build and inspect artifacts

- [ ] Remove prior `build/`, `dist/`, `*.egg-info/`, cache, and coverage output.
- [ ] Run `python scripts/build_release_artifacts.py`.
- [ ] Confirm exactly one wheel and one source distribution exist.
- [ ] Run `python -m twine check dist/*`.
- [ ] Inspect wheel and sdist contents; confirm required code, metadata,
  `README.md`, and `LICENSE`, and exclude caches, tests, generated output,
  proprietary source material, and local configuration.
- [ ] Record SHA-256 checksums for both artifacts.
- [ ] Repeat the release build from the same commit and confirm both artifact
  checksums are identical.

## 4. Verify installations

- [ ] Install the wheel into a new environment with no editable checkout or
  `PYTHONPATH`.
- [ ] Run `scripts/verify_installed_package.py` with that environment.
- [ ] Install the sdist into a separate new environment and repeat verification.
- [ ] Install the source checkout editable into a third new environment.
- [ ] Verify `teos --version`, `teos --help`, public API import, canonical
  curriculum compilation, and the complete reference build for each applicable
  path.
- [ ] Run documentation commands exactly as published.

## 5. Review and approve

- [ ] Review the final diff, repository audit, license notices, release notes,
  roadmap, and known limitations.
- [ ] Confirm protected CI checks pass on the exact release commit.
- [ ] Obtain maintainer approval before committing, tagging, or creating remote
  release state.

## 6. Create the release

- [ ] Commit the approved release changes.
- [ ] Push the release branch and merge through the protected workflow.
- [ ] Create the annotated protected tag from the verified commit:
  `git tag -a v1.2.0-alpha1 -m "TechnicalEducationOS v1.2.0-alpha1"`.
- [ ] Push only that tag.
- [ ] Confirm the release workflow builds and verifies fresh artifacts.
- [ ] Review the automatically created **draft** GitHub release, release notes,
  artifact names, checksums, and target commit.
- [ ] Publish the GitHub release only after explicit maintainer approval.
- [ ] Publish to the selected package index only if that publication is part of
  the approved release plan.

## 7. Post-release verification

- [ ] Install from the public release/package index into a clean environment.
- [ ] Verify the reported version, CLI, API, and reference build.
- [ ] Confirm GitHub identifies the license and displays the release assets.
- [ ] Confirm documentation links and badges resolve on the default branch.
- [ ] Open follow-up issues for deferred work and advance `CHANGELOG.md` to the
  next `Unreleased` cycle.
- [ ] Announce the release and document any rollback or yanking action.
