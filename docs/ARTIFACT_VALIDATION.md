# Document Verification and Artifact Validation

Status: Implemented validation baseline  
Reference curriculum: `tec101`  
Snapshot version: `1.0`

## Scope

This phase validates generated outputs from the maintained end-to-end reference
build. It does not add artifact types, change curriculum, or make a generated
document authoritative. The validation target is:

```text
8 scheduled sessions
× 3 registered document renderers
× 4 physical generators
= 24 logical documents and 96 physical artifacts
```

A logical document is one renderer result for one session. A physical artifact
is that result encoded as Markdown, HTML, DOCX, or PDF. The 24 rendered JSON
records are trace intermediates, not additional instructional documents.

## Artifact inventory

| Document type | Registered renderer | Logical count | Physical count | Notes |
|---|---:|---:|---:|---|
| Administrative lesson plan | `administrative` | 8 | 32 | One per scheduled session |
| Instructor lesson plan/guide | `instructor` | 8 | 32 | One per scheduled session |
| Lab sheet | `lab` | 8 | 32 | May state that no lab is assigned |
| Course outline | — | 0 | 0 | Not registered in the application build |
| Student guide | — | 0 | 0 | Not registered |
| Standalone assessment | — | 0 | 0 | Assessment descriptions appear in plans |
| Answer key/rubric key | — | 0 | 0 | No protected answer-key source exists |
| Standalone resource list | — | 0 | 0 | Resources appear within lesson plans |
| Attendance sheet | — | 0 | 0 | Not registered |
| Other supported document types | — | 0 | 0 | No other session renderer is registered |

Each format contains 24 files. Each renderer/format pairing contains eight
files. Inventory validation derives these expectations from the registered
renderer and generator sets and then compares them with the manifest and the
actual output tree. A specification-level artifact class is not counted as
supported until it is registered in the application pipeline.

## Structural validation

The permanent tests parse the Markdown source hierarchy and require exact,
unique, ordered level-two sections.

Administrative lesson plans require:

1. Objectives
2. Essential Question
3. Materials
4. Warm Up
5. Academic Activities
6. Shop Activities
7. Exit
8. Assessment

Instructor guides require:

1. Preparation
2. Teaching Sequence
3. Common Technician Errors
4. Instructor Shop Tip
5. Flex Activities

Lab sheets require one section per applicable source lab. Every lab section
requires Procedure, Deliverables, and Safety subsections. A session with no
applicable lab must explicitly say so. The document title and course, session,
unit, phase, duration, and institution context are also required.

Empty optional values are rendered as an explicit `None recorded.` statement.
A repeated lab subsection under a different lab is valid nesting, not a
duplicate document section.

Footers and revision metadata are not embedded in the current minimal document
bodies. Revision and build traceability are adjacent in `manifest.json` and the
rendered JSON record.

## Content and cross-document validation

Validation loads the authoritative course, units, and sessions independently
of the output. It compares:

- administrative objectives with the session objective selection and owning
  unit statements;
- administrative materials, categorized activities, and assessment
  descriptions with the session/unit source values;
- instructor preparation, teaching sequence, common errors, shop tip, and flex
  activities with the source values; and
- lab selection, procedures, deliverables, and safety notes with applicable
  source labs.

The comparisons are exact and ordered. Consequently, an invented, changed,
omitted, duplicated, or reordered value fails the suite.

For each session, the administrative, instructor, and lab records must have the
same build, curriculum revision/version, course, unit, session, schedule,
institution, locale, and theme values. Their visible context blocks must also
be identical. The validator does not require a value in a document whose
renderer contract does not expose that value; for example, competencies and
standards are validated in the source model but are not currently printed by
the three registered session renderers.

## Physical-format and formatting validation

Every physical artifact is opened using a format-appropriate parser:

- Markdown is decoded as UTF-8 and checked for its title hierarchy.
- HTML is parsed, checked for UTF-8 metadata and theme CSS, and reduced to its
  body text.
- DOCX is opened as ZIP, every member is integrity-checked, and its OOXML parts
  are parsed.
- PDF is checked for its header, trailer, cross-reference table, page media
  box, font resource, and extractable text commands.

Normalized physical text must equal the rendered source. PDF comparison uses
Unicode-aware tokens because deterministic visual line wrapping introduces
presentation-only whitespace. The PDF generator wraps long lines without
discarding text.

Filename pattern, extension, directory containment, size bounds, manifest
checksum, and exact manifest/output-tree agreement are required for every
file.

Renderer-independent validation covers semantic text, heading hierarchy,
lists, and paragraph order. HTML verifies configured colors and typography.
The minimal DOCX and PDF generators do not currently provide production print
layout features such as branded headers, footers, logos, explicit margins, or
page numbers; those are listed under limitations rather than inferred.

## Localization validation

The `en-US` and `es-US` catalogs must have identical key sets. The build
requires translations for every interface title, context label, heading,
empty-state message, phase, and duration unit used by the registered
renderers. Tests reject untranslated English interface headings in Spanish
artifacts.

Instructional source strings are preserved exactly in every locale. TEOS does
not machine-translate objectives or other curriculum prose, because doing so
would rewrite authoritative curriculum. Thus the current localization contract
localizes presentation/interface text while preserving source-language
instructional meaning.

## Theme validation

Equivalent builds using `default` and `dark` themes must have identical
rendered instructional content and identical normalized content in every
format. Markdown, DOCX, and PDF are byte-identical across those themes. HTML
must change only its configured background, foreground, accent, and font
family tokens.

The reference theme model has no logo, header, or footer tokens. Those features
cannot be validated until they exist in an approved presentation contract.

## Metadata validation

The package manifest is the adjacent metadata authority. Tests verify:

- manifest version, TEOS/compiler version, deterministic build identifier, and
  pipeline result;
- curriculum identifier, schema/model version, and curriculum revision digest;
- institution, calendar, meeting pattern, locale, and theme;
- exact hashes for all loaded curriculum, institutional, locale, theme, and
  template sources; and
- a unique artifact ID plus course, unit, session, schedule, revision, locale,
  theme, output path, format, and content checksum for every physical artifact.

`curriculum_revision` is SHA-256 over canonical course, ordered unit, and
session-plan records. `build_id` additionally identifies configuration and all
loaded source hashes.

No generation timestamp is emitted. Its omission is intentional: there is no
applicable nondeterministic metadata field, and equivalent builds remain
byte-for-byte reproducible.

## Snapshot and determinism strategy

The checked-in
`tests/snapshots/reference_artifacts.json` file contains one normalized SHA-256
digest per logical document. Normalization converts line endings to LF and
removes trailing whitespace. It does not remove, sort, or rewrite
instructional content.

Binary files are not checked into the repository. Their extracted normalized
content is compared with the rendered record, their containers are parsed, and
their manifest hashes are verified. The existing end-to-end determinism test
also performs an exact byte comparison of two complete build trees, including
DOCX and PDF.

There are no accepted nondeterministic fields. Snapshot changes require review
against authoritative source changes or an intentional renderer correction;
hashes must never be refreshed merely to make a failing test pass.

## Automated validation

Run the artifact phase:

```bash
python -m pytest -q tests/end_to_end/test_artifact_validation.py
```

Run the complete repository suite:

```bash
python -m pytest -q
```

The artifact suite permanently covers inventory, structure, exact content,
cross-document metadata/context, four-format semantic preservation, parser and
container integrity, filenames/checksums/sizes, revision metadata,
localization, theme isolation, and normalized snapshots. Builds use temporary
directories; generated instructional documents are never committed.

## Remaining limitations

- Only administrative lesson plans, instructor guides, and lab sheets are
  registered. Course outlines, student guides, standalone assessments, answer
  keys, resource lists, and attendance sheets are outside the current output
  inventory.
- Competencies and standards are source-validated but are not visible in every
  current document, so their cross-document presentation cannot be tested.
- Spanish localization covers interface text. Authoritative English
  instructional prose has no approved translated curriculum counterpart and
  remains English.
- HTML consumes the complete theme token set. The minimal DOCX and PDF outputs
  do not yet apply theme typography/colors or institution branding assets.
- Logos, branded headers/footers, page numbers, explicit print margins,
  accessibility tagging, and visual pixel/page regression are not supported by
  the current end-to-end generators.
- Parser validation proves structural opening and text preservation; it does
  not substitute for manual review in every office-suite or PDF viewer.
