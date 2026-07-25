# Schemas

Purpose: own machine-readable contracts for knowledge records, blueprints,
curriculum models, mappings, institution overlays, and compatibility records.

Inputs are governing subsystem specifications and accepted architecture
decisions. Outputs are versioned schemas consumed by validators, authoring
tools, compilers, renderers, and tests.

Current executable schemas:

- `course.schema.json` — legacy course record;
- `week.schema.json` — legacy weekly curriculum record;
- `institution.schema.json` — institution overlay.

Blueprint, knowledge-source, curriculum-model, traceability, and artifact
manifest schemas will be added with their implementation milestones. A schema
MUST follow the governing prose specification and MUST NOT be invented merely
to satisfy one renderer.

Runtime validation also checks cross-record and semantic relationships that
JSON Schema cannot conveniently express.
