# End-to-End Reference Build

This runbook verifies the authoritative TEOS application pipeline:

```text
Load → Validate → Compile → Schedule → Render → Generate
```

It uses only maintained reference sources. Generated files are disposable and
must be written to a new, isolated output directory.

## Prerequisites and clean installation

- Python 3.11 or newer
- a clean repository checkout
- network or package-cache access for declared build/runtime dependencies
- no `PYTHONPATH`, editable installation, shell alias, home-directory
  configuration, or pre-existing output

From the repository root:

```bash
python -m venv /tmp/teos-build-venv
/tmp/teos-build-venv/bin/python -m pip install build
/tmp/teos-build-venv/bin/python -m build
python -m venv /tmp/teos-wheel-venv
/tmp/teos-wheel-venv/bin/python -m pip install dist/*.whl
```

Run the installed command from a directory outside the checkout, with
`PYTHONPATH` unset.

## Canonical build command

```bash
env -u PYTHONPATH /tmp/teos-wheel-venv/bin/teos build \
  --repository /path/to/TechnicalEducationOS/examples/reference_curriculum \
  --schemas /path/to/TechnicalEducationOS/schemas \
  --institution north-valley-community-college \
  --calendar fall-2026-semester \
  --meeting-pattern monday-wednesday-evening \
  --locale en-US \
  --theme institution-branded \
  --renderers all \
  --generators all \
  --output /tmp/teos-reference-build
```

`--repository` and `--schemas` are explicit so execution never depends on the
current directory or on developer-specific package data. The output path must
not already exist. A successful run prints the manifest path, artifact count,
and reproducible build identifier.

## Reference configuration matrix

| Institution | Calendar | Meeting pattern | Locale | Theme |
|---|---|---|---|---|
| `north-valley-community-college` | `fall-2026-semester` | `monday-wednesday-evening` | `en-US` | `institution-branded` |
| `metro-trade-institute` | `accelerated-8-week` | `tuesday-thursday-day` | `es-US` | `dark` |

To exercise the alternate combination, replace the five corresponding values
in the canonical command. Profile, calendar, locale, theme, and template
selection are validated before compilation or generation.

## Loaded and validated sources

The build loads:

- the canonical course, its embedded standards and competencies;
- all instructional units, including objectives, lectures, demonstrations,
  labs, assessments, and resource requirements;
- the ordered session plan;
- the selected institution profile and academic calendar;
- the selected locale and theme catalogs; and
- the institution-selected administrative template.

Course, unit, session-plan, institution, and calendar records are checked
against the frozen JSON Schemas. Runtime validation then checks identifiers,
uniqueness, ownership, references, domain invariants, cross-object mappings,
instructional time, institution/calendar linkage, meeting capacity, locale
keys, and theme tokens. Invalid objects never reach compilation.

## Output structure and expected artifacts

```text
teos-reference-build/
├── compiled-curriculum.json
├── schedule.json
├── manifest.json
├── rendered/
│   └── session-NNN-{administrative,instructor,lab}.json
└── artifacts/
    ├── markdown/*.md
    ├── html/*.html
    ├── docx/*.docx
    └── pdf/*.pdf
```

The reference build schedules eight authoritative sessions. Each resolved
session is passed with its owning unit to the three currently registered
renderers: administrative lesson plan, instructor guide, and lab sheet.
Renderers produce deterministic intermediate records and never write files.
The four generators consume only rendered text and presentation configuration,
producing 96 physical artifacts in total.

Automated verification checks non-empty files, extensions and containment,
UTF-8 Markdown/HTML, DOCX ZIP/XML structure, and PDF header/trailer structure.
DOCX ZIP member timestamps are fixed; PDF objects contain no timestamps.
The complete structural, content, cross-document, localization, theme,
metadata, parser, and snapshot strategy is defined in
[Document Verification and Artifact Validation](ARTIFACT_VALIDATION.md).

## Manifest

`manifest.json` contains:

- manifest and TEOS versions;
- reproducible `build_id`;
- deterministic curriculum revision and schema/model version;
- source curriculum, institution, calendar, meeting pattern, locale, and theme;
- renderer and generator selections;
- hashes for every loaded source;
- one record per artifact with type, renderer, generator, session, relative
  output path, curriculum/institution/locale/theme trace metadata, SHA-256
  content hash, and pipeline result; and
- overall artifact count and pipeline result.

The build identifier is a SHA-256 digest of canonical configuration and source
hashes. No operational timestamp is embedded, so two equivalent builds produce
byte-identical manifests and artifacts.

## Determinism verification

Run the canonical command twice with two new output directories:

```bash
diff -ru /tmp/teos-reference-build-1 /tmp/teos-reference-build-2
```

The permanent test compares every byte, including compilation summaries,
schedules, rendered intermediates, manifests, Markdown, HTML, DOCX, and PDF.
There are no known nondeterministic fields in these generated reference
artifacts.

## Public API

The CLI is a thin adapter over the same application service:

```python
from pathlib import Path
from teos import BuildConfig, build

result = build(
    BuildConfig(
        repository=Path("/path/to/examples/reference_curriculum"),
        schema_directory=Path("/path/to/schemas"),
        institution_id="north-valley-community-college",
        calendar_id="fall-2026-semester",
        meeting_pattern_id="monday-wednesday-evening",
        locale="en-US",
        theme="institution-branded",
        output_directory=Path("/tmp/teos-reference-api-build"),
    )
)
print(result.build_id, result.manifest_path)
```

Equivalent CLI and API configurations produce the same logical artifact set,
byte-identical content, and the same build identifier.

## Failure diagnostics and isolation

Normal CLI errors return status 2, begin with `Error:`, and do not show a
traceback. The API raises `teos.BuildError`. Controlled diagnostics cover a
missing repository, malformed/schema-invalid records, unresolved references,
unknown institution/calendar/locale/theme selections, unavailable
renderer/generator selections, schedule impossibility, and output creation
errors.

Generation uses a staging directory adjacent to the requested output and moves
it into place only after all artifacts and the manifest succeed. A failed build
does not report success, expose partial output, overwrite an existing build, or
modify reference sources.

## Model limits

The frozen v2 source model has no explicit prerequisite/dependency-edge field.
The build therefore records an empty acyclic dependency edge set and preserves
the authoritative session order; it does not manufacture a cycle scenario.

The currently registered session renderers are administrative lesson plan,
instructor guide, and lab sheet. The reference model contains assessment
descriptions but no protected answer-key content. The end-to-end build does not
invent answer keys or add artifact types merely to enlarge the regression
inventory.
