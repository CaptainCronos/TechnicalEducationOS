# Course Blueprint Specification

Status: Governing  
Version: 1.0

## Purpose

A course blueprint is the approved design contract between requirements,
available time, and the curriculum model. It answers what the course will
cover, in what sequence, and within which scheduling constraints before daily
instructional artifacts are generated.

It is not a lesson plan and does not contain document layout.

## Required inputs

- course catalog identity, credit/contact-hour requirements, and prerequisites;
- active educational-standard records and required competencies;
- institutional calendar, meeting pattern, holidays, policies, and exam rules;
- program-specific constraints and approved exceptions; and
- optional prior blueprint or offering data for comparison.

Instructional resources may inform feasibility and allocation, but a blueprint
does not copy slide content into the schedule.

## Required blueprint sections

### Identity and governance

- stable blueprint and course IDs;
- schema and blueprint versions;
- owning institution/program;
- academic term or reusable scheduling profile;
- status, authors, reviewers, approval, and revision history;
- input source IDs and immutable versions.

### Course envelope

- semester start/end or duration;
- required and available instructional minutes;
- meeting pattern and meeting count;
- classroom, lab/shop, online, and other delivery-hour categories;
- holidays, closures, and non-instructional exceptions;
- midterm, final, practical, and other fixed windows.

### Scope and sequence

- required competencies and standard references;
- ordered units or modules;
- prerequisite and dependency relationships;
- inclusion, exclusion, and approved deferral decisions;
- estimated instructional time by unit and delivery mode.

### Allocation

- competency-to-unit allocation;
- unit-to-week/meeting allocation;
- assessment and practical-evaluation windows;
- contingency/flex allocation;
- total-time reconciliation.

### Diagnostics and approval

- uncovered, duplicated, or deferred requirements;
- overallocated or unallocated time;
- scheduling conflicts;
- explicit exception dispositions;
- approval state and signatures/identities.

## Schedule model

A schedule contains stable meeting IDs with dates or sequence positions,
available minutes, delivery mode, and exception state. Weeks group meetings for
the instructor-facing view. Curriculum entities are assigned to meetings by ID;
they are not re-authored inside a week.

Blueprints SHOULD support a reusable course design plus an offering-specific
calendar binding so a new term can be scheduled without redefining course
scope.

## Invariants

- Available instructional minutes equal the sum of valid meeting minutes after
  exceptions.
- Allocated minutes plus explicitly reserved minutes do not exceed available
  minutes.
- Every required competency has a coverage disposition.
- Every fixed exam or practical window resolves to valid meetings.
- Prerequisites precede dependent units unless an approved exception exists.
- A blueprint cannot be approved while blocking diagnostics are unresolved.

## Outputs

An approved blueprint produces:

- scope and sequence;
- weekly and meeting allocation;
- competency schedule;
- course time-budget report;
- assessment windows;
- unresolved-risk and exception report; and
- input and approval manifest.

These outputs are compiler inputs to the structured curriculum model. They are
not educational artifacts for direct instruction.

## Change behavior

Calendar-only changes SHOULD reschedule stable curriculum entities without
changing their educational meaning. Scope, standard, or allocation changes
produce a new blueprint version and trigger model impact analysis.
