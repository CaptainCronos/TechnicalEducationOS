# TEOS Architecture Overview

Status: Governing  
Version: 1.0  
Date: 2026-07-25

## Purpose

TEOS compiles governed knowledge into a structured curriculum and projects that
curriculum into educational artifacts. The architecture separates evidence,
curriculum decisions, scheduling, presentation, and generated files so each can
change without silently redefining the others.

## System model

```text
┌──────────────────── Knowledge plane ────────────────────┐
│ standards │ institutional constraints │ teaching media │
└──────────────────────────┬───────────────────────────────┘
                           │ register, extract, cite
                           ▼
                  ┌──────────────────┐
                  │ Course Blueprint │
                  │ scope + schedule │
                  └────────┬─────────┘
                           │ compile + review
                           ▼
             ┌───────────────────────────┐
             │ Structured Curriculum     │
             │ Model                     │
             │ objectives, instruction,  │
             │ labs, assessments, safety │
             └─────────────┬─────────────┘
                           │ validate + render
             ┌─────────────┴──────────────────┐
             ▼                                ▼
     Educational artifacts          Trace and audit products
```

## Major subsystems

### Knowledge-source registry

Registers source identity, version, provenance, rights, integrity, extraction
state, and addressable locations. It contains three layers:

1. educational standards define required learning;
2. institutional resources constrain delivery time and policy;
3. instructional resources provide evidence for delivery methods and content.

Registration does not make extracted content an approved curriculum decision.

### Course blueprint

Defines a course before individual artifacts exist. It reconciles course
requirements with the academic calendar and available instructional time,
producing scope and sequence, competency allocation, assessment windows, and a
week-based schedule projection.

### Structured curriculum model

Owns approved instructional meaning: competencies, objectives, units,
meetings, activities, demonstrations, labs, assessments, safety requirements,
tools, materials, time estimates, and source references. It is the sole
educational-content input to artifact renderers.

### Traceability service

Maintains typed relationships across standards, decisions, schedule entities,
instruction, assessment, and outputs. It supports coverage verification, gap
analysis, impact analysis, accreditation evidence, and regeneration.

### Validation and compilation

Validates schemas, references, time budgets, coverage, provenance, approval
state, and renderer prerequisites. Compilation is deterministic for the same
versioned inputs and compiler version. Validation errors stop dependent
outputs; warnings require an explicit disposition.

### Artifact renderers

Project an approved curriculum model into audience- and format-specific
documents. Renderers may select, order, format, paginate, and label model
content. They may not add educational claims or requirements.

## Authority and lifecycle

Records progress through explicit states:

```text
registered source → reviewed extraction → draft blueprint → approved blueprint
→ draft curriculum model → approved model → generated artifact
```

Approval is version-specific. Changing an approved upstream record makes
affected approvals and outputs stale; it does not rewrite them silently.

## Cross-cutting requirements

- IDs are stable, unique within a declared namespace, and never derived solely
  from display wording.
- Every stored record declares its schema version.
- Every source-derived assertion carries a citation or explicit authoring
  decision.
- Institution-specific overlays cannot replace standards or curriculum facts.
- Calendars schedule curriculum entities; weeks do not own duplicate copies of
  them.
- Generated artifacts carry a manifest identifying model, renderer, template,
  and generation versions.
- Original source files and generated outputs are not committed when licensing,
  privacy, or repository policy forbids it; their metadata remains addressable.

## Compatibility strategy

The current `curriculum/courses/<course>/weeks/` records combine curriculum and
schedule concerns but already enforce valuable relationships. They remain valid
inputs to the existing renderers. Migration will map them into blueprint and
model entities, compare generated output, and only then retire direct legacy
paths.

## Related specifications

- [Knowledge Sources](../specifications/knowledge-sources.md)
- [Course Blueprint](../specifications/course-blueprint.md)
- [Curriculum Model](../specifications/curriculum-model.md)
- [Traceability](../specifications/traceability.md)
- [Educational Artifacts](../specifications/educational-artifacts.md)
