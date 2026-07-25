# Structured Curriculum Model Specification

Status: Governing  
Version: 1.0

## Purpose

The structured curriculum model is TEOS's intermediate representation and the
single source of educational truth for artifact generation. It combines an
approved blueprint with reviewed curriculum decisions and source references.

## Model envelope

Every model MUST declare:

- model ID, course ID, model version, and schema version;
- source blueprint ID and immutable version;
- status (`draft`, `in_review`, `approved`, `superseded`);
- authorship, review, approval, and revision metadata;
- source and decision dependencies; and
- compiler/tool version when machine-produced.

Only an approved model may produce release artifacts.

## Core entities

| Entity | Owns |
|---|---|
| Competency | demonstrable course capability and required-standard references |
| Learning objective | measurable instructional outcome and competency links |
| Unit | coherent scope, sequence, prerequisites, and time estimate |
| Meeting assignment | placement of model entities into a blueprint meeting |
| Instructional activity | delivery method, objective links, time, and resources |
| Demonstration | instructor performance, conditions, safety, tools, and observation points |
| Lab | student performance, procedure, safety, tools, materials, deliverables, and criteria |
| Assessment | type, objective/competency coverage, conditions, scoring, and item references |
| Assessment item | prompt/task, response or rubric, objective links, provenance, and security classification |
| Resource reference | approved use of an addressable knowledge-source location |
| Safety requirement | hazard, control, PPE, prerequisite, and applicable activity links |
| Tool/material | identity, quantity or availability constraints, and applicable activity links |
| Authoring decision | human interpretation or design choice with rationale and evidence |

Entities use stable IDs and references. Shared content is not copied into each
meeting or artifact.

## Minimum unit completeness

An instructional unit MUST define:

- competencies and measurable objectives;
- required standard references;
- estimated instructional time;
- instructional strategy or activities;
- assessment strategy;
- source/resource references;
- safety requirements or an explicit reviewed `not_applicable` disposition;
- required tools and materials or an explicit reviewed disposition; and
- placement or placement constraints from the blueprint.

Labs, demonstrations, and assessment items are required only when called for by
the blueprint, standards, or approved curriculum design. Their absence MUST
never be filled by renderer inference.

## Provenance rules

Each educational assertion is classified as one of:

- `source_derived`: supported by one or more exact source citations;
- `author_decision`: created by an authorized curriculum designer with
  rationale and supporting references where applicable;
- `institution_required`: linked to an approved institutional record; or
- `computed`: deterministically derived from versioned model data.

Generated prose is not automatically authoritative. AI-assisted or automated
draft content remains an `author_decision` in draft state until human approval.

## Scheduling separation

Educational entities own meaning; blueprint meetings own available time;
meeting assignments connect the two. The model MAY expose a week-based
projection, but that projection references stable entities and MUST NOT become
a second authoritative copy.

## Validation classes

### Structural

Schema validity, unique IDs, allowed values, and required fields.

### Referential

All blueprint, source, standard, objective, activity, assessment, and resource
references resolve to permitted versions.

### Semantic

Objectives are measurable, assessment criteria align to objectives, labs
contain necessary safety controls, and entity classifications are coherent.
Some semantic checks require human review and recorded disposition.

### Coverage

Required standards reach objectives, instruction, and assessments according to
the traceability policy.

### Temporal

Assigned time fits blueprint meetings, prerequisites are respected, and totals
reconcile.

### Renderer readiness

Every requested artifact contract has the model fields it requires.

## Outputs

The model emits a versioned renderer-ready package, trace graph, validation
report, change summary, and dependency manifest. A model is never reconstructed
from its generated documents.

## Legacy migration

Existing course/week records map as follows:

- course competencies → competency entities;
- week objectives → learning objectives;
- lectures and typed activities → instructional activities;
- labs → lab entities;
- assessments and question banks → assessment entities and items;
- lessons → meeting assignments plus week projection;
- teaching and safety notes → source-derived or author-decision records.

Migration MUST retain existing stable IDs where valid and compare current
artifacts before changing the compatibility pipeline.
