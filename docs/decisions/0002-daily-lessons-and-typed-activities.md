# ADR 0002: Daily lessons and typed activities

- Status: Accepted
- Date: 2026-07-25

## Context

The two approved DSL204 Week 5 administrative lesson plans are daily plans.
They contain classroom and shop activities, but they do not assign a duration
to each activity or define lab procedures, deliverables, assessment questions,
or rubrics. The initial weekly schema assumed those details. Filling its
lecture, lab, and question-bank structures would therefore invent curriculum.

The plans also contain reusable instructional knowledge that does not belong in
a document template: materials, terminology, industry applications, common
technician errors, shop tips, homework, and flex activities.

## Decision

Keep the course and week records as the source boundary and add these minimum
entities:

- course competencies or external-standard statements;
- weekly learning objectives linked to those competencies;
- daily lessons linked to objectives and assessments;
- typed activities (`warm_up`, `academic`, `shop`, and `exit`) linked to
  objectives; and
- assessments that may be described observationally without a question bank.

A daily lesson owns its approved duration, objective summary, essential
question, materials, terminology, teaching knowledge, and activity sequence.
Academic and shop activities satisfy the existing lecture and lab alignment
audit without requiring duplicate lecture or lab records.

The administrative renderer owns the section names, section order,
configuration-board table, numbering, time formatting, and blank instructor
reflection prompts. An optional institution overlay owns branding and
administrative fields. The DSL204 curriculum records do not contain `J-Tech`.

The existing lecture/lab representation remains supported for curriculum that
actually contains timed lectures and procedural labs. The daily lesson model is
an additive refinement, not a forced migration.

## Reference-plan classification

- Curriculum: objectives, standards, questions, activities, assessments,
  materials, terminology, applications, errors, tips, homework, and flex
  guidance.
- Presentation: headings, the two-column configuration board, list numbering,
  typography, page layout, section order, and blank reflection prompts.
- Institution-specific: institution name, program name, branding, and arbitrary
  administrative fields supplied by an overlay. The approved files contain no
  visible institution name or logo.
- Reusable source records: competencies, objectives, lessons, activities, and
  assessments. Other approved teaching knowledge remains nested in the lesson
  because neither reference plan demonstrates a need to share it independently.

## Consequences

- Both approved plans can be generated from one Week 5 record without copying
  objective or activity text into document-specific sources.
- The model records only details present in the approved curriculum.
- A week may generate multiple administrative plans, one per daily lesson.
- The model is independent of output format. ADR 0003 subsequently adds the
  production J-Tech Word presentation without changing curriculum ownership.
