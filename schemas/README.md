# Schemas

Purpose: own machine-readable contracts for knowledge records, blueprints,
curriculum models, mappings, Institution Profiles, and compatibility records.

Inputs are governing subsystem specifications and accepted architecture
decisions. Outputs are versioned schemas consumed by validators, authoring
tools, compilers, renderers, and tests.

Current executable schemas:

- `course.schema.json` — calendar-independent course, competency, and module record;
- `instructional-unit.schema.json` — reusable instructional unit;
- `session-plan.schema.json` — ordered canonical sessions;
- `academic-calendar.schema.json` — institution-specific term dates and events;
- `week.schema.json` — deprecated read-only compatibility record;
- `institution.schema.json` — operational Institution Profile, meeting rules,
  and presentation configuration.

Any future schema MUST follow the governing prose specification and MUST NOT be
invented merely to satisfy one renderer.

Runtime validation also checks cross-record and semantic relationships that
JSON Schema cannot conveniently express.
