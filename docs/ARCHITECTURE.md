# Architecture

## Governing constraint

`PROJECT_HANDOFF.md` is the repository constitution. The architecture exists to
reduce lesson-planning work for existing curriculum; it does not redesign that
curriculum.

## Data flow

```text
curriculum source records ─┐
                           ├─> validate/audit ─> generators ─> outputs/
institution overlay ───────┘
```

Only files under `curriculum/` are authoritative curriculum. Institution
overlays may supply names, headings, or administrative fields, but may not
replace objectives or instructional content. Files under `outputs/` are
reproducible artifacts and must not be edited as sources.

## Source boundaries

- A course record owns course identity and competencies.
- A week record owns that week's objectives, lectures, labs, assessments, and
  teaching notes. When the existing curriculum is organized as daily plans, the
  week also owns daily lessons and their typed activities.
- Stable IDs connect records. Content is written once and referenced by ID.
- Schema versions make future migrations explicit.
- Institution overlays are optional and isolated under `institutions/`.

JSON is used in Phase 1 because it is supported by the Python standard library,
has an unambiguous data model, and avoids a package-management dependency.

## Application boundaries

- Validation checks record shape and broken references before generation.
- Audits report instructional coverage gaps without changing curriculum.
- Generators are deterministic: identical inputs produce identical content.
- Renderers contain document presentation; curriculum records contain teaching
  knowledge.
- Institution presentation adapters contain institution-specific labels,
  typography, layout, and template integration. The J-Tech Administrative
  adapter lives in `teos/institutions/jtech.py`; generic validation and source
  records do not depend on it.
- Daily administrative plans are generated once per lesson. Academic and shop
  activity links participate in the same objective-coverage audit as explicit
  lecture and lab records.
- The command-line interface is the first workflow surface. A UI is not needed
  to prove Phase 1 value.

## Change rule

Add a field only when a real existing curriculum item or required output needs
it. Add a new generator without copying curriculum into a document-specific
source. Record significant boundary changes in `docs/decisions/`.
