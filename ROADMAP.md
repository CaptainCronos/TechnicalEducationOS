# TechnicalEducationOS Roadmap

The sequence follows the compiler dependency chain. Downstream features do not
define upstream curriculum.

## Milestone 0 — Curriculum architecture foundation

- Establish the repository constitution and governing specifications.
- Separate knowledge sources, blueprints, models, mappings, renderers, and
  outputs.
- Define ownership, inputs, outputs, data flow, and traceability requirements.
- Preserve existing week-based records and renderers during transition.

Exit criterion: every major subsystem has a documented boundary and future
implementation has one unambiguous compiler pipeline.

## Milestone 1 — Standards ingestion

- Register ASE and other standards with source identity, version, provenance,
  and rights metadata.
- Extract addressable standard and task records without losing page or section
  citations.
- Validate stable identifiers and source integrity.

Exit criterion: standards can be cited and versioned as structured knowledge.

## Milestone 2 — Knowledge-source ingestion

- Register institutional calendars, policies, and requirements.
- Register CDX materials, manuals, presentations, notes, videos, and
  demonstrations.
- Preserve source locations and distinguish extracted facts from interpretation.

Exit criterion: all three knowledge layers use a common provenance contract.

## Milestone 3 — Course blueprint generation

- Define course constraints, meetings, instructional hours, holidays, exams,
  scope and sequence, and competency allocation.
- Detect scheduling and coverage conflicts.
- Add explicit human review and approval.

Exit criterion: an approved blueprint accounts for requirements and available
instructional time before lesson authoring.

## Milestone 4 — Curriculum model generation

- Compile blueprints and knowledge references into structured instructional
  units, objectives, activities, labs, assessments, and resource requirements.
- Validate references, time budgets, safety coverage, and renderer readiness.
- Migrate existing course/week records without breaking current outputs.

Exit criterion: a versioned model is the complete educational input to
renderers.

## Milestone 5 — Educational artifact renderers

- Adapt existing lesson-plan renderers to the curriculum-model contract.
- Add student notes, labs, quizzes, exams, question banks, reports, and LMS
  exports.
- Emit generation manifests and trace metadata with every artifact.

Exit criterion: renderers contain presentation logic only and never invent
curriculum.

## Milestone 6 — Validation and traceability

- Produce coverage, gap, conflict, and impact analysis.
- Trace standards through objectives, schedule, instruction, and assessment.
- Generate accreditation evidence and change-impact reports.

Exit criterion: required paths are machine-verifiable and gaps are actionable.

## Milestone 7 — Integrations

- Add LMS and approved external-system adapters.
- Keep external formats downstream of the curriculum model.

Exit criterion: integrations exchange versioned model projections without
becoming curriculum authorities.
