# ADR 0004: Curriculum compiler architecture

- Status: Accepted
- Date: 2026-07-25

## Context

The initial TEOS architecture began with existing course/week records and
generated lesson plans. That work proved deterministic document generation and
single-source relationships, but architectural review showed that lesson plans
begin too late in curriculum design. Standards define required outcomes,
institutional resources constrain available time, and instructional resources
support delivery. A lesson-plan-first model cannot fully govern scope,
sequence, competency allocation, or end-to-end traceability.

## Decision

Define TEOS as a curriculum compiler with this authoritative flow:

```text
registered knowledge sources
  → approved course blueprint
  → approved structured curriculum model
  → educational artifact renderers
```

Create separate repository boundaries for knowledge-source layers, course
blueprints, curriculum models, mappings, renderer contracts, and disposable
outputs. Preserve the school's week-based workflow as a schedule projection
over stable curriculum entities.

Renderers receive educational content only from an approved curriculum model.
Templates and institution presentation adapters supply presentation, not
curriculum. Traceability is compiled with the model and connects sources,
requirements, objectives, scheduled instruction, practice, assessment, and
artifacts.

Keep the existing `curriculum/courses/` records and `teos/` renderers working as
a compatibility pipeline while executable blueprint and model contracts are
implemented and validated.

## Consequences

- Architecture development precedes additional artifact features.
- Standards and resource ingestion require provenance and addressable
  citations.
- Course scheduling becomes a governed blueprint concern.
- Existing week records require an explicit, tested migration rather than an
  abrupt rewrite.
- Artifact generation can expand without making any artifact the curriculum
  authority.
- Changes to upstream sources can drive impact analysis and controlled
  regeneration.
