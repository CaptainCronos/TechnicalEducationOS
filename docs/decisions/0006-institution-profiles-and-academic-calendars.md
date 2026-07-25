# ADR 0006: Institution Profiles and Academic Calendars

Status: Accepted  
Date: 2026-07-25

## Decision

TEOS separates instructional meaning, scheduling, and presentation.

The curriculum owns all instructional content through courses, competencies,
instructional units, and ordered sessions. An Institution Profile owns
replaceable operating and presentation configuration. An Academic Calendar
owns term boundaries and availability events. Neither institutional record may
own curriculum or preassign sessions.

The Scheduler combines:

1. canonical ordered sessions;
2. one meeting pattern from an Institution Profile; and
3. one Academic Calendar registered to that profile.

It derives meeting slots, skips non-instructional dates, assigns sessions in
order, and emits a disposable schedule. Week/day labels are aliases on those
generated assignments and resolve to canonical sessions before rendering.

Renderers consume the resolved session and its instructional unit. Institution
configuration may control template, branding, required fields, LMS packaging,
and report format, but it may not introduce instructional claims.

## Consequences

- The same curriculum can be scheduled and rendered for multiple institutions.
- Calendars are term-wide and contain no `course_id`.
- Meeting rules live in the Institution Profile rather than being copied into
  course calendars.
- A closure changes only the generated mapping; sessions and units stay intact.
- Lesson plans and other outputs remain generated views, never curriculum
  authoring surfaces.
