# ADR 0001: Source records and generated outputs

- Status: Accepted
- Date: 2026-07-25

## Context

The existing curriculum must generate several document types without requiring
instructors to maintain duplicate copies. Phase 1 must remain simple and
institution-independent where practical.

## Decision

Store institution-independent curriculum in versioned JSON course and week
records. Connect objectives, lectures, labs, assessments, and competencies with
stable IDs. Keep institution-specific presentation data in separate overlays.
Generate disposable documents into an ignored `outputs/` directory.

Use the Python standard library for the initial validator, auditor, CLI, and
Markdown renderers.

## Consequences

- Curriculum content has one authoritative location.
- Broken relationships can stop generation before inconsistent documents are
  produced.
- Outputs can be deleted and regenerated.
- JSON is more punctuation-heavy than authoring formats such as YAML, but it
  avoids an early dependency and is easy to validate and automate.
- A later authoring interface can sit above the same record contracts without
  changing source ownership.
