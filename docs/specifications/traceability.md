# Traceability Specification

Status: Governing  
Version: 1.0

## Purpose

Traceability explains why curriculum content exists, where it is scheduled, how
it is taught and assessed, and which artifacts present it. It enables coverage
verification, accreditation evidence, gap analysis, revision, and reliable
regeneration.

## Trace model

Traceability is a directed graph of versioned nodes and typed edges. A typical
path is:

```text
standard requirement
  ─satisfied_by→ competency
  ─developed_by→ learning objective
  ─scheduled_in→ meeting
  ─taught_by→ activity/resource
  ─practiced_by→ lab
  ─assessed_by→ assessment item
  ─rendered_in→ artifact
```

Week 4 and Day 2 are schedule projections associated with the meeting node, not
substitutes for traceable entity IDs.

## Node classes

- source and source version;
- source locator or extracted record;
- standard requirement/task;
- institutional constraint;
- authoring decision;
- blueprint and blueprint allocation;
- competency and objective;
- unit, meeting, activity, demonstration, and lab;
- assessment and assessment item;
- resource, safety requirement, tool, and material;
- curriculum model version;
- artifact and generation manifest.

## Edge requirements

Each edge MUST contain:

- stable edge ID;
- typed source and target node IDs with immutable versions;
- relationship type;
- provenance (`declared`, `reviewed`, or `computed`);
- creator and creation time;
- review/approval state;
- optional rationale, strength, or coverage classification; and
- schema version.

Computed edges identify the rule and compiler version that produced them.

## Coverage policy

For each required standard, TEOS MUST record one of:

- covered through an approved competency, objective, instruction/practice, and
  assessment path;
- introduced or reinforced with an approved reason that assessment is not
  required in this course;
- deferred to an identified course or program component; or
- excepted with authority, rationale, and review date.

“No mapping found” is a gap, not an implicit exception.

## Cardinality and integrity

- One standard may map to multiple competencies and objectives.
- One objective may support multiple standards.
- Many-to-many relationships are explicit mapping edges, never comma-separated
  text pretending to be references.
- Every edge endpoint MUST resolve.
- Historical edges remain resolvable after supersession.
- A released artifact's `rendered_in` edges MUST resolve to the exact model and
  renderer build used.

## Required analyses

The trace graph supports:

- forward trace: requirement to artifact;
- backward trace: artifact element to source or authoring decision;
- coverage: requirements with complete or incomplete paths;
- gaps and orphans: unaddressed requirements or unsupported curriculum;
- impact: downstream records affected by a changed source;
- duplication: suspicious parallel entities or repeated coverage;
- freshness: downstream approvals or artifacts based on superseded inputs; and
- accreditation evidence: selected paths with source and approval metadata.

## Traceability matrix

A matrix is a generated view of the graph, not a separately maintained source.
At minimum it can show:

| Standard | Competency | Objective | Unit/meeting | Instruction/lab | Assessment | Artifact |
|---|---|---|---|---|---|---|

Blank cells represent diagnostics or approved dispositions; they are never
silently filled by renderer logic.

## Review

Mapping assertions that require subject-matter judgment remain draft until
reviewed by an authorized owner. Automated similarity or AI suggestions MAY
propose edges but MUST record their method and MUST NOT approve themselves.
