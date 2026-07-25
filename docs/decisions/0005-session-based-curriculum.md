# ADR 0005: Session-Based Curriculum

Status: Accepted  
Date: 2026-07-25

## Decision

TEOS uses curriculum as its only instructional source of truth. The canonical
order is standards and knowledge, compilation, competencies, instructional
units, and sessions. Courses and units contain no week, semester, date, or
institution-calendar fields.

A session is the scheduling primitive and references one instructional unit. A
dedicated scheduler maps ordered sessions onto available slots in one academic
calendar. Closures shift assignments without changing session or unit records.
Week/day labels are aliases stored in the schedule projection and must resolve
to a session before rendering.

Lesson plans, instructor guides, student materials, labs, assessments, LMS
packages, calendars, attendance sheets, and gradebook entries are generated
views. None is an independent authoring surface.

## Consequences

- Curriculum can be reused across semester, accelerated, evening, weekend, and
  self-paced delivery patterns.
- Schedule changes regenerate mappings and affected artifacts, not curriculum.
- Renderers accept sessions and units, never weeks.
- Existing week records and commands are deprecated read-only compatibility
  mechanisms and cannot receive new curriculum.
