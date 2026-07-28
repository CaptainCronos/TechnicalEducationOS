# Installation

TEOS supports CPython 3.11 and 3.12. A virtual environment is strongly
recommended. The commands below use POSIX paths; on Windows, replace
`.venv/bin/python` with `.venv\Scripts\python.exe`.

## Install a release

After the alpha is published to the configured package index:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install technicaleducationos==1.2.0a1
.venv/bin/teos --version
```

Python package versions use the PEP 440 form `1.2.0a1`; the Git tag and release
name use `v1.2.0-alpha1`.

## Install a release artifact

Download either distribution from the GitHub release, then install exactly one:

```bash
python -m venv .venv
.venv/bin/python -m pip install technicaleducationos-1.2.0a1-py3-none-any.whl
```

```bash
python -m venv .venv
.venv/bin/python -m pip install technicaleducationos-1.2.0a1.tar.gz
```

Confirm the CLI and public API:

```bash
.venv/bin/teos --version
.venv/bin/teos --help
.venv/bin/python -c "import teos; print(teos.__version__)"
```

## Install a source checkout

```bash
git clone https://github.com/CaptainCronos/TechnicalEducationOS.git
cd TechnicalEducationOS
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/teos --version
```

The distribution installs application code and its runtime dependency. Schemas,
curriculum records, institution profiles, locale catalogs, theme catalogs, and
templates are explicit inputs and remain in the source repository. Use the
checkout when running the maintained reference curriculum.

## Verify the reference curriculum

From an editable checkout:

```bash
.venv/bin/teos build --course examples/reference_curriculum/curriculum
.venv/bin/teos build \
  --repository examples/reference_curriculum \
  --schemas schemas \
  --institution north-valley-community-college \
  --calendar fall-2026-semester \
  --meeting-pattern monday-wednesday-evening \
  --locale en-US \
  --theme institution-branded \
  --renderers all \
  --generators all \
  --output /tmp/teos-reference-build
```

The first command validates and compiles the canonical records. The second
produces 96 artifacts and a deterministic manifest. The output directory must
not already exist.

## Troubleshooting

- `No module named teos`: invoke the Python executable from the environment
  where TEOS was installed.
- `output directory already exists`: select a new empty output path; TEOS will
  not overwrite an existing build.
- `Error:` from the CLI: correct the indicated input or configuration. Expected
  user errors return status 2 without a traceback.
- Dependency download failure: confirm package-index and proxy configuration,
  then retry installation. TEOS has no runtime network requirement after its
  dependencies and inputs are installed.
