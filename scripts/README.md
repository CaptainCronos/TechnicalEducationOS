# Scripts

Purpose: own thin, repeatable workflow entry points that compose supported TEOS
commands.

Inputs are explicit command arguments and repository records. Outputs are the
documented results of the commands they invoke. Scripts must not become hidden
curriculum sources, embed credentials, or duplicate compiler business logic.

- `build_release_artifacts.py` builds reproducible wheel and source archives.
- `check_markdown_links.py` validates repository-local documentation targets.
- `validate_schemas.py` validates schemas and governed repository records.
- `verify_installed_package.py` smoke-tests an installed distribution outside
  the source import path.
