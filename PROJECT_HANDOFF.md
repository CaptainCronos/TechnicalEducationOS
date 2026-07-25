# TechnicalEducationOS Repository Constitution

Version: 2.0
Effective: 2026-07-25

## 1. Mission

TechnicalEducationOS (TEOS) is a curriculum compiler. It transforms registered
knowledge sources and institutional constraints into a reviewed, structured
curriculum model, then renders that model into educational artifacts.

Its purpose is to reduce instructor workload while preserving instructional
quality, source evidence, and the ability to explain why every instructional
element exists.

## 2. Governing principle

The structured curriculum model is the single authoritative source for
educational artifacts. A lesson plan is one compiled output, not the curriculum
itself.

```text
knowledge sources
      ↓
course blueprint
      ↓
structured curriculum model
      ↓
validated educational artifacts
```

PowerPoint files, manuals, standards, and calendars are evidence or constraints.
They do not render directly into lesson plans. Templates control presentation;
they do not provide curriculum content. Generated artifacts never become source
records.

## 3. Authority order

When records disagree, resolve the disagreement instead of silently choosing:

1. approved educational standards and regulatory requirements;
2. approved institutional requirements and calendar constraints;
3. reviewed course blueprints;
4. approved structured curriculum models;
5. instructional-resource evidence;
6. generated artifacts.

The order describes governance, not automatic truth. Conflicts MUST be recorded
and reviewed by an authorized curriculum owner.

## 4. Architectural boundaries

- `knowledge/` registers source evidence and provenance.
- `curriculum/blueprints/` defines course scope, sequence, and allocation.
- `curriculum/models/` contains renderer-ready curriculum models.
- `curriculum/mappings/` contains explicit cross-source mappings and migration
  work products.
- `schemas/` defines machine-readable contracts.
- `renderers/`, `teos/`, and institution presentation adapters compile approved
  models into artifacts.
- `templates/` owns presentation assets only.
- `outputs/` contains reproducible, disposable artifacts.
- `docs/` governs architecture and authoring practice.

The existing `curriculum/courses/` week records remain supported as legacy
authoritative records during migration. New compiler development MUST target
the blueprint and curriculum-model contracts rather than deepen a
week-document-first design.

## 5. Non-negotiable rules

1. Every generated educational claim MUST resolve to the approved curriculum
   model.
2. Every curriculum requirement MUST be traceable to a registered source,
   approved authoring decision, or documented exception.
3. Renderers MUST NOT invent objectives, durations, labs, assessment content,
   safety requirements, tools, or materials.
4. Generated files MUST NOT be edited as source.
5. Stable identifiers MUST connect records; wording MUST NOT be used as an
   identifier.
6. Source versions, schema versions, and generation metadata MUST be explicit.
7. Institution-specific policy and presentation MUST remain isolated from
   institution-independent curriculum.
8. A change to an upstream source MUST be detectable in downstream validation.
9. Human approval gates MUST remain visible; automation MUST NOT silently
   resolve ambiguous curriculum decisions.
10. Significant boundary changes MUST be recorded in `docs/decisions/`.

## 6. Instructor-facing workflow

TEOS preserves the familiar Week 1, Week 2, Week 3 presentation. Internally, a
week is a scheduled projection of competencies, objectives, activities,
resources, and assessments. The schedule may change without duplicating or
redefining those curriculum entities.

## 7. Delivery sequence

Development proceeds in this order:

1. architecture and repository foundation;
2. standards and knowledge-source ingestion;
3. course blueprint generation;
4. curriculum model generation;
5. artifact renderers;
6. validation and traceability;
7. LMS and external integrations.

Existing renderers may continue operating while upstream compiler capabilities
are added incrementally.

## 8. Definition of success

An authorized curriculum owner can register evidence, approve a course
blueprint, compile a validated curriculum model, generate all required
educational artifacts, and trace any artifact element back through the model to
its source or recorded authoring decision.

## 9. Governing documentation

The normative architecture begins at
[`docs/architecture/overview.md`](docs/architecture/overview.md). Detailed
contracts live in `docs/specifications/`. If an older document conflicts with
this constitution, this constitution and accepted architecture decisions take
precedence.
