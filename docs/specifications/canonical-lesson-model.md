# Canonical Lesson Model Specification

Status: Proposed  
Version: 1.0

## Purpose

The Canonical Lesson Model (CLM) is the authoritative, renderer-independent
representation of instructional meaning for one lesson. Every lesson-related
artifact is a projection of the same validated lesson object.

The CLM is not a document model. It does not describe pages, slides, tables,
forms, fonts, package structures, or any other presentation concern. It is also
not a substitute for course-level scope and sequence. Course, unit, competency,
and session records continue to own reusable course design; a CLM binds the
instruction selected for one session into a reviewable lesson source.

## Authority and boundaries

For a lesson:

- the CLM owns instructional content, instructional sequence, intended
  duration, evidence expectations, safety controls, and teaching guidance;
- course and unit records own reusable course-level meaning referenced by the
  lesson;
- a Scheduler owns dates, clock times, meeting patterns, closures, and
  institution-specific week/day projections;
- an Institution Profile owns institution identity and operating constraints;
- renderer configuration and templates own audience selection, labels, layout,
  branding, accessibility presentation, file naming, and packaging; and
- generated artifacts own no instructional truth.

The historical `Week 4 Day 1` label may be retained in `source_aliases` for
traceability. It is not a date or an authoritative scheduling assignment.

## Design rules

A canonical lesson **MUST** be:

- independent of renderer, institution, curriculum vendor, and file format;
- human-readable YAML and machine-validatable against
  [`canonical-lesson.schema.json`](../../schemas/canonical-lesson.schema.json);
- normalized through stable IDs and references;
- explicit about provenance and review status;
- complete enough that a renderer never invents instructional content; and
- versioned independently of its generated artifacts.

A canonical lesson **MUST NOT** contain:

- page, paragraph, table, slide, worksheet-cell, or form-field instructions;
- fonts, colors, spacing, logos, headers, footers, or pagination;
- Word, PDF, HTML, PowerPoint, LMS, or print implementation details;
- blank response-space dimensions or other capture mechanics;
- a second copy of text merely because two artifacts display it; or
- calendar dates and clock times supplied by an institution schedule.

## Object structure

| Property | Owns |
|---|---|
| `schema_version` | CLM contract version |
| `lesson` | Stable identity, course/unit/session linkage, summary, language, and lifecycle |
| `sources` | Addressable evidence and its availability |
| `scheduling` | Instructional sequence, intended duration, segments, and non-authoritative source aliases |
| `academic_references` | Course, chapter, learning-outcome, task, and standard-set locators |
| `instructional_brief` | References used for the warm-up/objective/standard/question/closing snapshot |
| `essential_questions` | Questions that organize inquiry |
| `objectives` | Measurable lesson outcomes and standard alignment |
| `standards` | Exact external requirements represented once |
| `materials` | Physical tools, equipment, vehicles, components, consumables, PPE, and facilities |
| `resources` | Instructional or technical information used for teaching and performance |
| `terminology` | Terms, definitions, and aliases |
| `safety_requirements` | Hazard, control, severity, applicability, prerequisites, and verification |
| `activities` | Ordered classroom, shop, field, online, independent, or environment-neutral instruction |
| `assessments` | Purpose, coverage, evidence, criteria, feedback, and security |
| `homework` | Out-of-session learning assignment and deliverable |
| `instructor_guidance` | Content emphasis, misconceptions, pacing, shop tips, differentiation, flex, and remediation |
| `reflection` | Questions used to evaluate and improve the lesson |
| `notes` | Instructionally meaningful review or provenance notes |

### Configuration board normalization

`instructional_brief` is the semantic source for what an administrative
artifact may call a configuration board. It contains references only:

- `warm_up_activity_id`;
- `objective_ids`;
- `standard_ids`;
- `essential_question_ids`; and
- `closing_assessment_ids`.

The objective, standard, question, activity, and assessment text exists once in
its owning entity. A renderer chooses whether to present these references as a
board, list, table, dashboard, or another accessible view.

### Classroom and shop activity normalization

All activities use one entity type. The `environment` property distinguishes
`classroom`, `shop`, `field`, `online`, `independent`, and portable `any`
activities. This avoids separate schemas and duplicate activities while still
allowing classroom and shop renderers to select the correct records.

An activity owns:

- sequence and intended duration;
- method and instructional purpose;
- objective, material, resource, terminology, and safety references;
- distinct instructor and learner actions;
- procedural steps when the activity is procedural; and
- learner outputs.

The description explains why the activity exists. Procedure steps describe
what is done. They should not restate each other.

### Materials and resources

Materials are physical requirements. Resources carry information. A service
manual is a resource; a measurement tool is a material. A task sheet is a
resource even if a renderer later prints it.

Materials and resources exist once and are linked to every applicable activity.
A renderer may aggregate those references for a lesson-wide list without
copying them into the source.

### Safety

Safety requirements are first-class instructional entities, not notes embedded
in a lab paragraph. Each requirement identifies:

- the hazard;
- the control;
- severity;
- applicable activities;
- required materials or PPE;
- any prerequisite; and
- how the control is verified.

Activities reference applicable safety IDs. Renderers may repeat a safety
warning at the point of use for risk communication, but the repeated output is
generated from one canonical requirement.

### Assessment

Assessments separately own purpose, objective coverage, evidence, criteria,
feedback, and security classification. An activity may produce assessment
evidence, but the activity does not duplicate the rubric. The assessment points
back to the activity through `activity_ids`.

Homework has its own entity because it crosses the lesson boundary and requires
a distinct deliverable. It still references the same objectives and resources.

### Reflection and notes

Reflection stores meaningful questions, never blank lines or text-box
dimensions. Notes contain actual instructional, safety, provenance, or review
meaning. A renderer decides how responses are captured and whether a permitted
audience sees a note.

## Provenance

Every instructional entity has an `origin`:

| Classification | Meaning |
|---|---|
| `source_derived` | Supported directly by the referenced source |
| `author_decision` | Designed by an authorized curriculum author |
| `institution_required` | Required by an institution record without becoming general curriculum |
| `computed` | Deterministically derived from other versioned data |

`source_refs` link the assertion to top-level source records. `verification`
distinguishes verified content from content requiring source confirmation or
curriculum review. An author decision should include a rationale when its
reason is not self-evident.

Unavailable evidence is represented as an unavailable source. It is not
silently replaced by generated prose.

## Lifecycle

The lifecycle is:

```text
draft -> in_review -> approved -> superseded
```

Only `approved` lessons may produce released artifacts. Approval requires:

- the named approved source to be available;
- every instructional assertion to be verified;
- all schema and semantic checks to pass;
- curriculum and safety review by qualified reviewers; and
- reviewer and approval metadata to be recorded.

A new lesson version is created when instructional meaning changes. Renderer or
template changes do not change the lesson version unless they expose a model
defect that requires a curriculum change.

## Validation

Structural validation enforces the JSON Schema contract. Repository semantic
validation additionally enforces:

- global uniqueness of entity IDs;
- resolution of source, objective, standard, material, resource, terminology,
  safety, activity, question, and assessment references;
- contiguous and unique activity sequence;
- exactly one scheduling placement for every activity;
- equality of activity, segment, and lesson durations; and
- approval gating for unavailable sources and unverified origins.

Human review remains required for:

- fidelity to the approved lesson;
- accuracy of standards and source wording;
- appropriateness of objectives, teaching sequence, assessment criteria, and
  homework;
- applicability and sufficiency of safety controls; and
- alignment of vehicle-specific procedures and service information.

## Empty and missing content

An empty array means that the reviewed lesson has no entries for that optional
entity type. Missing required properties are invalid. Unknown or unavailable
content must not be encoded as an empty string, placeholder prose presented as
fact, or a renderer default.

If a required instructional element is unavailable, the lesson remains
`in_review`, its source availability and verification gap are recorded, and
release rendering stops.

## Extension policy

Compatible extensions should add entities or optional fields rather than
embedding output-specific structures. Likely future extensions include:

- prerequisites and prerequisite-evidence checks;
- accessibility and accommodation intent that remains independent of artifact
  mechanics;
- multilingual instructional equivalents with reviewed translation
  provenance;
- assessment-item banks and protected answer/rubric records;
- team roles, station rotations, and resource-capacity constraints;
- differentiated pathways and remediation branches;
- media accessibility descriptions and transcript references;
- competency and trace-graph edges to course-level records; and
- revision-impact metadata for regenerated artifacts.

Any extension must identify the owner of the meaning, its provenance, and the
renderer behavior it enables. A field must not be added solely because one
template contains a placeholder.
