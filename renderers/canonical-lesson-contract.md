# Canonical Lesson Renderer Contract

Status: Proposed  
Version: 1.0

## Common input

Every lesson renderer consumes the same validated Canonical Lesson Model (CLM)
defined by the [Canonical Lesson Model
Specification](../docs/specifications/canonical-lesson-model.md).

A renderer invocation may also receive separately governed inputs:

- a resolved schedule projection for date and clock-time display;
- an Institution Profile for approved identity and operating metadata;
- renderer configuration for audience, locale, and artifact options; and
- a template or theme for presentation.

Those inputs do not modify the CLM. A renderer must identify them independently
in its generation manifest.

## Renderer responsibilities

A renderer **MUST**:

- validate the CLM and reject an unsupported schema version;
- reject release generation for a lesson that is not `approved`;
- declare its artifact type, audience, version, required fields, selection
  rules, ordering rules, and failure behavior;
- resolve IDs only within the validated object;
- select content appropriate for its declared audience and security policy;
- preserve instructional wording and trace generated content to canonical IDs;
- treat absent optional content according to a declared policy;
- keep source diagnostics visible to authorized reviewers;
- satisfy format-specific accessibility requirements; and
- produce a generation manifest identifying every input and output version.

A renderer **MUST NOT**:

- invent, paraphrase, summarize, correct, or complete instructional content;
- create objectives, standards, definitions, procedures, safety controls,
  assessment criteria, feedback, homework, or instructor guidance;
- infer a duration, sequence, or service specification;
- retrieve a manual, slide deck, task sheet, or website as a parallel source of
  instructional truth;
- convert a template placeholder into curriculum content;
- add institution-specific instructional claims;
- expose instructor or restricted assessment content to learners; or
- write changes back to the CLM.

## Permitted transformations

A renderer may:

- filter by audience, environment, activity method, or security classification;
- order records by canonical sequence;
- resolve references and aggregate related entities;
- label, number, group, and paginate canonical content;
- repeat one safety requirement at multiple points of use;
- calculate display-only totals from canonical durations;
- turn canonical relationships into tables, lists, timelines, diagrams, or
  package structures;
- apply locale-aware presentation without changing instructional meaning; and
- add clearly non-instructional static interface text.

Any repeated output remains traceable to one canonical ID.

## Artifact-specific contracts

| Renderer | Required projection | Exclusions and special rules |
|---|---|---|
| Administrative Lesson Plan | Lesson metadata, resolved schedule if supplied, instructional brief, duration summary, objective and standard coverage, activity overview, assessment overview, homework | May use a board or table; may not copy a second source of objective/standard text into configuration data |
| Instructor Lesson Plan | All authorized lesson content, ordered activities, teaching actions, safety, materials, resources, assessment criteria, guidance, reflection prompts, review notes | Must visibly distinguish unresolved diagnostics in preview output; restricted content follows explicit authorization |
| Student Lesson | Student-relevant objectives, questions, terminology, learner actions, resources, safety, deliverables, assessments, homework | Excludes instructor actions, instructor guidance, reflection, reviewer notes, protected feedback, and restricted assessment content |
| Lab Guide | Shop/field activities, referenced objectives, procedures, materials, resources, safety requirements, outputs, and permitted criteria | Must preserve activity order and show safety at point of use; cannot add procedural steps from a manual |
| PowerPoint Outline | Canonical title, objectives, essential questions, terminology, selected activity concepts, assessment prompts, and source-approved media references | Owns slide grouping and titles only; cannot invent explanatory bullets, examples, speaker notes, or media |
| Assessment | Selected assessment purpose, learner directions derived from canonical evidence, criteria, and objective alignment | Answer/rubric and feedback visibility follows `security`; missing items or criteria cause failure rather than generation |
| LMS Export | Canonical identities, sequence, activities, resources, assessments, homework, and objective/standard mappings encoded in a supported package | Owns package identifiers and interoperability mappings; cannot synthesize course settings, due dates, grades, or question items |

An artifact-specific implementation must document any smaller required field
set and its optional-section behavior. It may require more data than this table,
but may never introduce a second instructional source.

## Configuration-board behavior

The administrative and instructor renderers resolve `instructional_brief`
references at render time. The board label, layout, ordering, and visual style
belong to the renderer. The referenced activity, objective, standard,
essential-question, and assessment entities remain the only content source.

## Schedule behavior

The CLM supplies intended durations and source aliases. A resolved schedule may
add an institution date, meeting label, and clock times to an artifact. If no
schedule projection is supplied, the renderer may display instructional
durations but must not infer dates or clock times.

## Missing content and failure

For release generation, a renderer fails when:

- schema or semantic validation fails;
- lifecycle status is not `approved`;
- a required section or reference is missing;
- its required security authorization is absent;
- a required resource cannot be identified; or
- its artifact contract requires instructional content not present in the CLM.

Preview rendering of an `in_review` lesson is permitted only when the output is
clearly identified as a preview and includes unresolved diagnostics. A blank
template section is not evidence that content exists.

## Output manifest

Each artifact manifest records:

- lesson ID, lesson version, CLM schema version, and lifecycle status;
- canonical IDs included and intentionally excluded;
- schedule, Institution Profile, renderer, template, locale, and theme
  versions, when supplied;
- artifact type, audience, format, security classification, and generation
  time;
- validation result and unresolved preview diagnostics;
- content checksum and output identity; and
- compiler and renderer versions.

The manifest supports reproducibility and traceability; it does not become an
instructional source.
