# Developer guide

## Onboarding

Prerequisites are Git and CPython 3.11 or 3.12.

```bash
git clone https://github.com/CaptainCronos/TechnicalEducationOS.git
cd TechnicalEducationOS
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

Confirm the environment:

```bash
.venv/bin/teos --version
.venv/bin/python scripts/validate_schemas.py
.venv/bin/python -m pytest -m "not performance"
.venv/bin/python -m ruff check .
.venv/bin/python scripts/check_markdown_links.py
```

## Build and package

```bash
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
```

Release artifacts use `python scripts/build_release_artifacts.py`, which fixes
archive timestamps and ownership to the release commit for reproducibility.

To test the installed package outside the checkout, create a new environment,
install one artifact, and run `scripts/verify_installed_package.py` from that
environment. The permanent process is documented in
[Release procedure](RELEASING.md).

## Generate documents and run examples

The shortest canonical check is:

```bash
.venv/bin/teos build --course examples/reference_curriculum/curriculum
```

The full document command is in the
[End-to-End Reference Build runbook](END_TO_END_BUILD.md). It generates
Markdown, HTML, DOCX, and PDF only under the selected output directory.

## Test organization

Use the standard suite for every change:

```bash
.venv/bin/python -m pytest -m "not performance"
```

Use marker-specific commands during development:

```bash
.venv/bin/python -m pytest -m unit
.venv/bin/python -m pytest -m integration
.venv/bin/python -m pytest -m end_to_end
.venv/bin/python -m pytest -m regression
.venv/bin/python -m pytest -m performance -s
```

Coverage is enforced at 85 percent when `pytest-cov` is enabled. CI runs the
supported Python matrix, canonical regression suite, installed-wheel
end-to-end suite, schema validation, lint, link checks, package metadata
checks, and both distribution installation paths.

## Repository rules

Read [PROJECT_HANDOFF.md](../PROJECT_HANDOFF.md) before changing model
ownership or data flow. Keep generated output out of Git, preserve deterministic
fixtures, add an ADR for significant boundary changes, and update tests and
release notes for observable compatibility changes.

Use the complete [contribution workflow](../CONTRIBUTING.md) for issues, pull
requests, review, tests, documentation, and commit messages. Public contracts,
governance, and architectural boundaries may also require an
[RFC](RFC_PROCESS.md). The [support matrix](SUPPORT.md) defines the environments
that release validation must cover.
