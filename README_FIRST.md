# Read This First

Every TEOS development session begins with:

1. [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) — repository constitution;
2. [`docs/architecture/overview.md`](docs/architecture/overview.md) — governing
   system boundaries;
3. [`ROADMAP.md`](ROADMAP.md) — milestone order; and
4. the relevant subsystem specification in `docs/specifications/`.

The current architecture foundation separates registered knowledge sources,
course blueprints, structured curriculum models, and generated artifacts.
Preserve the working legacy course/week pipeline, but do not extend it with
direct source-document-to-artifact dependencies.

Significant changes to ownership, authority, or data flow require an
architecture decision record.
