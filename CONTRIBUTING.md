# Contributing

Thank you for helping improve TEOS. By participating, you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Setup

Use Python 3.11 or 3.12 and follow the
[developer guide](docs/DEVELOPMENT.md). It contains the authoritative
environment, test, lint, package, and reference-build commands.

## Standard workflow

1. Read `PROJECT_HANDOFF.md`, the architecture overview, and the relevant
   subsystem specification.
2. Review the current repository status.
3. Keep knowledge evidence, curriculum decisions, and generated artifacts in
   their documented ownership boundaries.
4. Record changes to authority, ownership, or data flow in
   `docs/decisions/`.
5. Test implementation and documentation links before committing.
6. Run the standard quality gates:

   ```bash
   python -m pytest -m "not performance"
   python -m ruff check .
   python scripts/check_markdown_links.py
   python -m build
   python -m twine check dist/*
   ```

7. Use a focused branch, clear commit messages, and a pull request that
   explains the reason for the change and its verification.

Do not commit generated artifacts, local environments, caches, credentials, or
third-party source material without documented redistribution permission.

## Compatibility

Changes to public CLI behavior, imports, schemas, record contracts, or generated
formats require tests and release notes. Architecture and public API redesigns
must be proposed before implementation.

## Security

Do not open a public issue for a suspected vulnerability. Follow
[SECURITY.md](SECURITY.md).
