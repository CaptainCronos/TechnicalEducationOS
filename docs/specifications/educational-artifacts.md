# Educational Artifact Specification

Status: Governing  
Version: 1.0

## Purpose

Educational artifacts are compiled projections of an approved curriculum model
for a defined audience, use, and format. They are not curriculum authorities.

## Artifact classes

- administrative and instructor lesson plans;
- student guides and notes;
- demonstrations and lab instructions;
- quizzes, exams, practical evaluations, and answer/rubric keys;
- question-bank packages;
- scope-and-sequence and pacing views;
- accreditation, coverage, gap, and audit reports;
- LMS and external-system exports.

## Renderer contract

Every renderer MUST declare:

- renderer ID and version;
- supported artifact type, audience, and formats;
- required and optional model fields;
- selection and ordering rules;
- template/configuration dependencies;
- handling for approved `not_applicable` and optional values;
- security rules, including separation of student and answer-key content;
- output naming and packaging rules; and
- validation and failure behavior.

## Allowed renderer behavior

A renderer may:

- select model content for an audience;
- order, group, label, number, and paginate it;
- transform approved values into tables, prose, media references, or supported
  export structures;
- calculate display-only values such as totals from model data; and
- apply branding and accessibility-aware presentation.

A renderer MUST NOT:

- create or rewrite objectives, standards, explanations, procedures, questions,
  answers, rubrics, safety controls, durations, tools, or materials;
- infer missing curriculum from a template placeholder;
- read a slide deck or manual as a parallel content source;
- conceal unresolved compiler diagnostics; or
- write changes back into a blueprint or curriculum model.

## Templates

Templates own styles, static labels, layout, logos, headers, footers, and blank
response areas. Any template text that makes an educational claim MUST instead
be modeled and supplied by the curriculum model.

Template and institution configuration are independent inputs to presentation.
They cannot override model content.

## Generation manifest

Each released artifact or artifact package MUST be accompanied by metadata
containing:

- artifact ID, type, audience, format, and generation time;
- course, offering, blueprint, and model IDs/versions;
- renderer and template IDs/versions;
- compiler/build version;
- relevant trace-edge or trace-bundle ID;
- content checksum;
- validation result;
- confidentiality/security classification; and
- stale/superseded status when known.

The manifest may be embedded, adjacent, or included in an output-package
manifest as appropriate to the format.

## Quality requirements

- Identical approved inputs SHOULD yield semantically identical outputs.
- Artifact accessibility requirements belong to the renderer contract.
- Student-facing artifacts MUST exclude protected keys, rubrics, or instructor
  notes unless explicitly authorized.
- A partial artifact clearly identifies missing optional sections; it never
  disguises missing required curriculum.
- Output filenames are convenient labels, not stable identity.

## Lifecycle

```text
requested → validated → rendered → quality checked → released → superseded
```

Artifacts in `outputs/` are reproducible and may be deleted. Release or
distribution systems may preserve approved packages according to institutional
records policy, but those packages still do not become curriculum sources.
