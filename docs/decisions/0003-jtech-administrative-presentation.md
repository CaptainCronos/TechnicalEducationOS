# ADR 0003: J-Tech Administrative presentation adapter

- Status: Accepted
- Date: 2026-07-25

## Context

The official blank J-Tech form supplies institutional branding and a partial
layout. The approved FUN101 Week 7 plans demonstrate the finished production
standard: a two-page document with a heading hierarchy, two-column
configuration board, compact content sections, lists, and reflection prompts.

The original DOCX renderer populated the blank form and appended the remaining
content with the form's generic paragraph style. That kept curriculum
provenance intact but produced a three-page document whose hierarchy,
information density, and board layout did not match the approved plans.

## Decision

Keep curriculum records and relationship validation unchanged. Place all
J-Tech-specific DOCX presentation in `teos/institutions/jtech.py` and retain
`teos/docx.py` only as a compatibility facade.

Use the official blank form as the generated package and header-artwork base.
Rebuild its document body from validated curriculum values using the reusable
presentation contract demonstrated by the approved FUN101 plans. Section
labels, ordering, table layout, fonts, colors, spacing, list treatment, and
blank reflection prompts are institution presentation.

Do not read curriculum from an approved DOCX and do not make the approved
FUN101 files runtime curriculum dependencies.

## Consequences

- J-Tech presentation logic is isolated from curriculum records.
- The same renderer works for any course/week record satisfying the source
  contract; it contains no FUN101, DSL204, week, or day special cases.
- Generated plans preserve official branding and render at the approved
  two-page density for the current records.
- Future institutions require separate presentation adapters instead of
  conditionals in curriculum or the J-Tech renderer.
- The institution must still accept the generated files in its supported Word
  environment.
