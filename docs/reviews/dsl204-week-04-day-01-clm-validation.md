# DSL204 Week 4 Day 1 CLM Validation

Status: In review  
Review date: 2026-07-28  
Canonical record:
[`week-04-day-01.yaml`](../../curriculum/courses/dsl204/lessons/week-04-day-01.yaml)

## Executive finding

The Canonical Lesson Model can represent every instructional category required
by the named lesson without depending on a document format. The reference YAML
passes structural and repository semantic validation and demonstrates
normalized relationships among objectives, standards, resources, safety,
activities, assessments, homework, guidance, reflection, and notes.

Fidelity to the approved DSL204 Week 4 Day 1 lesson is **not yet proven**. The
named approved lesson document was absent from both the repository and the
connected DSL204 source folder during this review. The only facts verified
directly for the target lesson are:

- course: DSL204;
- source alias: Week 4 Day 1;
- title: Foundation Brake Preparation, Preliminary Inspection, and Drum/Shoe
  Service; and
- course-framework placement: Chapter 36, Foundation and Parking Brake
  Systems.

Supporting task sheets and a drum-brake maintenance resource were available.
They support the model's safety and workflow capabilities, but they are not a
substitute for the approved lesson. Consequently, the canonical record is
`in_review`, source-derived and author-designed content is distinguished, and
all unconfirmed content is approval-gated.

## Source inventory

| Source | Availability | Use in validation |
|---|---|---|
| Approved DSL204 Week 4 Day 1 lesson | Not available | Required for final section-by-section fidelity and approval |
| CLM assignment brief | Available | Course, source alias, title, required sections, and design principles |
| DSL204 Curriculum Framework draft | Available | Week 4 to Chapter 36 mapping |
| CDX MHT3A002 task sheet | Available | Preparation, system identification, safety, documentation, cleanup |
| CDX MHT3C001 task sheet | Available | Foundation-brake shop safety, inspection practice, needed action, employability criteria |
| Drum Brake Maintenance Manual L974 Rev E | Available | Candidate drum-brake service reference; vehicle applicability unconfirmed |
| Selected vehicle service information | Restricted/selected at delivery | Vehicle-specific warnings, procedures, measurements, and limits |

## Normalization review

| Source concept | Classification | Canonical owner | Normalization decision |
|---|---|---|---|
| Course code, lesson ID, title, language, lifecycle | Metadata | `lesson` | Stored once; institution name is not part of lesson identity |
| Week/day label | Metadata/operational alias | `scheduling.source_aliases` | Retained for source traceability, not treated as a date or canonical sequence authority |
| Total and classroom/shop duration | Instructional scheduling | `scheduling` | Segment durations reference activities; validator reconciles every total |
| Configuration Board | Presentation plus instructional references | `instructional_brief` | Board layout removed; references resolve to the one canonical copy of each item |
| Academic/course/chapter/task references | Metadata/resources | `academic_references` and `sources` | Locators separated from objective and activity prose |
| Objectives | Instruction | `objectives` | One measurable statement per ID; activities and assessments reference it |
| Standards | Instructional requirement | `standards` | Exact statement represented once; unverified code is visibly approval-gated |
| Essential question | Instruction | `essential_questions` | Stored once and referenced by the brief |
| Materials/tools/PPE | Resources for performance | `materials` | Physical items separated from informational resources and referenced by activities/safety |
| Manuals, task sheets, presentations, diagrams, videos | Resources | `resources` | Purpose and source locator stored without output-format assumptions |
| Terminology | Instruction | `terminology` | Definition stored once; activities reference term IDs |
| Safety statements | Instruction | `safety_requirements` | Hazard/control entities replace repeated safety paragraphs |
| Classroom and shop activities | Instruction | `activities` | One activity type; `environment` enables renderer selection without parallel schemas |
| Procedure and demonstration | Instruction | `activities.procedure_steps` | Steps belong to the activity; a renderer cannot import extra steps from a manual |
| Exit ticket, observation, practical evaluation | Assessment | `assessments` | Evidence and criteria stored separately from the activity producing them |
| Homework | Instruction/assessment | `homework` | Separate cross-session assignment with objective/resource references |
| Common errors, tips, flex work | Instruction | `instructor_guidance` | Typed guidance; not copied into lab safety or activity prose |
| Instructor reflection | Instructional improvement | `reflection` | Meaningful prompts only; response boxes and blank lines belong to renderers |
| Notes | Metadata/instruction/review | `notes` | Only notes with meaning are canonical; blank note areas are presentation |
| Headings, numbering, tables, spacing, logos, headers/footers | Presentation | Renderer/template | Excluded from CLM |

### Duplication removed

- The configuration board contains IDs, not duplicate objective, standard,
  question, warm-up, or closing-assessment text.
- Classroom and shop records share the same activity schema.
- Segment activity lists reference activities; they do not restate activity
  content.
- Materials, resources, terminology, and safety requirements are declared once
  and referenced from activities.
- Assessments reference the activities that produce evidence instead of
  embedding a second activity description.
- Safety can be repeated in rendered output at point of use while retaining one
  canonical hazard/control record.
- The Week 4 Day 1 label is a source alias, not a duplicate calendar record.

## Lesson mapping

The following mapping demonstrates coverage of every requested section. The
status column distinguishes model capability from verified source fidelity.

| Requested lesson section | CLM path | Representation | Status |
|---|---|---|---|
| Lesson Metadata | `lesson` | Stable lesson/course ID, title, summary, language, lifecycle; optional unit/session linkage | Title/course verified; unit/session IDs omitted until course records define them |
| Scheduling | `scheduling` | Sequence, 240-minute intent, source alias, two segments, ordered activity references | Model complete; durations require source confirmation |
| Academic References | `academic_references` | Course, Chapter 36, source task, target task locator | Chapter verified; exact target task code missing |
| Configuration Board | `instructional_brief` | Warm-up, objective, standard, question, closing-assessment references | Fully modeled; wording requires source comparison |
| Learning Objectives | `objectives` | Preparation, preliminary inspection, drum/shoe inspection, documentation | Fully modeled; author decisions in review |
| Standards | `standards` | CDX chapter plus approval-gated ASE semantic mapping | Exact ASE edition/code/wording not modeled because unavailable |
| Materials | `materials` | Vehicle, chocks, lifting equipment, tools, dust control, PPE, record | Fully modeled; exact quantities/specifications need confirmation |
| Resources | `resources` | Vehicle service information, L974, supporting task sheet | Fully modeled; approved lesson resource list not verified |
| Terminology | `terminology` | Foundation brake, drum, shoe, lining, service limit, needed action | Fully modeled; approved term list not verified |
| Safety Requirements | `safety_requirements` | Vehicle movement, stored energy, lifting, brake dust, PPE/tools | Fully modeled; qualified safety review required |
| Classroom Activities | `activities[environment=classroom]` | Warm-up, preparation, inspection concepts, readiness check | Fully modeled; source sequence/wording not verified |
| Shop Activities | `activities[environment=shop]` | Demonstration, preliminary inspection, drum/shoe inspection, restore/close | Fully modeled; vehicle-specific scope remains external selection |
| Assessments | `assessments` | Readiness, practical observation, exit explanation with criteria | Fully modeled; approved scoring/criteria not verified |
| Homework | `homework` | Evidence and service-information review | Fully modeled; approved assignment not verified |
| Instructor Guidance | `instructor_guidance` | Emphasis, shop tip, misconception, flex alternative | Fully modeled; approved guidance not verified |
| Reflection | `reflection` | Objective, safety, pacing, and revision prompts | Fully modeled; prompts are author decisions |
| Notes | `notes` | Provenance gap and renderer-independence review | Fully modeled; blank note space intentionally excluded |

## Information not currently modeled

No known instructional category is outside the schema. The following target
lesson information cannot yet be populated or verified:

- the exact approved lesson wording and section order;
- approved class duration and segment durations;
- exact CDX/ASE framework edition, task codes, and verbatim statements;
- canonical Chapter 36 unit and session IDs in the DSL204 course records;
- approved learning outcomes, essential question, terminology, resources,
  procedures, assessment criteria, homework, and instructor guidance;
- selected lab vehicle and applicable manufacturer service procedure;
- institution-approved shop safety procedure and local regulatory controls;
- assessment answer content, scoring weights, mastery threshold, and retest
  policy, if the approved lesson contains them; and
- any accommodation, differentiation, prerequisite, or learner-support content
  present in the unavailable source.

These are content/provenance gaps, not representation gaps. They must be
resolved from approved evidence rather than inferred by a renderer.

## Renderer-independence review

The schema and example were reviewed for output-format assumptions.

| Concern | Finding |
|---|---|
| Microsoft Word | No field or behavior |
| PDF | No field or behavior |
| HTML | No field or behavior |
| PowerPoint | No slide or speaker-note structure |
| LMS | No package, course-setting, due-date, or gradebook structure |
| Printed forms | No page, response-box, line, checkbox, or form-field geometry |
| Institution branding | No institution name, logo, color, or department field |
| Clock schedule | No date or clock time; only intended durations and a source alias |

File extensions appear only in source locators, where they identify evidence;
they do not affect lesson structure or renderer behavior.

## Automated validation findings

The repository validator confirms:

- the JSON Schema itself is valid Draft 2020-12;
- the YAML conforms to the complete CLM structure;
- entity IDs are globally unique;
- all typed references resolve;
- all eight activities are scheduled exactly once;
- activity sequence is contiguous;
- classroom activities total 120 minutes;
- shop activities total 120 minutes;
- segments and lesson duration reconcile to 240 minutes; and
- an unavailable approved source or unverified origin prevents an `approved`
  lifecycle state.

The schema deliberately rejects unknown fields, limiting accidental insertion
of renderer-specific data.

## Success-criteria assessment

| Criterion | Finding |
|---|---|
| Single object represents all required instructional elements | Pass for model capability |
| No instructional duplication | Pass structurally; human wording review still required |
| Instruction separated from presentation | Pass |
| Renderer independent | Pass |
| Institution and curriculum independence | Pass; source-specific values use references and aliases |
| Human- and machine-readable | Pass |
| Versionable and extensible | Pass |
| Fully faithful to approved DSL204 lesson | Blocked pending approved source |
| Authoritative approved YAML | Not yet; authoritative candidate is `in_review` |

## Recommendations

Before approval:

1. Add the approved lesson as a governed source with immutable version or
   checksum.
2. Compare every source section against the mapping table and update canonical
   wording without copying presentation.
3. Replace the pending standard code and statement with the exact approved
   framework citation.
4. Confirm duration, materials, resources, terminology, safety, activities,
   assessments, homework, guidance, and reflection.
5. Validate vehicle-specific procedures and safety controls with qualified
   reviewers.
6. Record reviewers, approval identity, approval date, and change summary.
7. Change lifecycle status to `approved` only after all origins are `verified`
   and the source is available.

For future CLM versions:

- add prerequisite and prerequisite-evidence entities;
- add protected assessment-item and rubric banks;
- add accommodations and differentiated pathways without document mechanics;
- add station/team/resource-capacity constraints;
- add media accessibility and translation provenance;
- add course-level trace edges and revision impact analysis; and
- build renderer contract tests proving that every artifact traces to canonical
  IDs and never supplies fallback instructional prose.
