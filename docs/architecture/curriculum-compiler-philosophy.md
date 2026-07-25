# Curriculum Compiler Philosophy

Status: Governing  
Version: 1.0

## Curriculum as source code

TEOS treats curriculum engineering as compilation:

| Compiler concept | TEOS equivalent |
|---|---|
| source files | registered standards, policies, calendars, and resources |
| build configuration | course blueprint |
| intermediate representation | structured curriculum model |
| compiler checks | schema, reference, coverage, time, and provenance validation |
| executable/output | lesson plans, labs, assessments, guides, and exports |
| debug symbols | trace links and generation manifests |

The analogy establishes separation of concerns; it does not imply curriculum
decisions are mechanical. Educators approve interpretations, priorities,
sequencing, and pedagogy.

## Governing principles

### Compile, do not copy

A fact is authored once in its authoritative record and referenced elsewhere by
stable ID. Artifact-specific copies are generated.

### Evidence is not curriculum

A standard says what is required. A calendar says when instruction can occur.
A slide deck or manual offers content and delivery evidence. None alone is a
course. The blueprint and reviewed curriculum model record the educational
decisions that reconcile them.

### No invention at render time

Missing instructional content is a compiler diagnostic, not a prompt for a
renderer to improvise. A renderer MUST fail, omit an explicitly optional
section, or render an approved “not applicable” value according to its contract.

### Weeks are a view

Instructors continue to plan and teach in weeks and meetings. Internally, weeks
schedule independently identified curriculum entities. This preserves the
school workflow while enabling rescheduling, reuse, and traceability.

### Traceability is part of compilation

Trace edges are emitted and validated with the model, not reconstructed after
documents exist. A successful build can state which requirements are covered,
where they are taught, how they are assessed, and which artifacts expose them.

### Determinism and review

Given identical approved inputs, compiler version, renderer version, and
template version, TEOS SHOULD produce semantically identical outputs. Human
review decisions are explicit versioned inputs rather than hidden state.

### Diagnostics over silent repair

The compiler reports:

- **errors** for invalid, conflicting, unapproved, or missing required data;
- **warnings** for risks that require recorded review;
- **information** for coverage, provenance, and build summaries.

Automation MUST NOT silently reinterpret standards, manufacture citations, or
resolve scheduling conflicts.

## Definition of a valid build

A build is valid only when:

1. all inputs satisfy their schemas;
2. required references resolve to approved versions;
3. blueprint time and calendar constraints reconcile;
4. required standards have an approved coverage disposition;
5. renderer-required model fields exist;
6. prohibited direct source-to-artifact paths are absent; and
7. a generation and trace manifest can be emitted.
