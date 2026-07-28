# Curriculum Authoring

Author curriculum in instructional order, never calendar order.

1. Define the course identity, standards, competencies, and modules in
   `course.json`.
2. Define each reusable instructional unit in `units/*.json`. A unit owns its
   objectives, lecture material, demonstrations, labs, assessments, resources,
   and estimated instructional time.
3. Divide units into the ordered meetings required to teach them in
   `sessions.json`. A session references exactly one unit and may select a phase
   and objective subset.
4. Validate the calendar-independent curriculum:

   ```bash
   python -m teos build --course curriculum/courses/COURSE_ID
   ```

5. Separately select an Institution Profile, term calendar, and meeting pattern,
   then generate a schedule:

   ```bash
   python -m teos schedule \
     --course curriculum/courses/COURSE_ID \
     --institution institutions/INSTITUTION_ID/institution.json \
     --calendar institutions/INSTITUTION_ID/calendars/TERM.json \
     --meeting-pattern MEETING_PATTERN_ID \
     --output outputs/COURSE_ID-TERM-schedule.json
   ```

6. Render a canonical session directly, or resolve a calendar alias first:

   ```bash
   python -m teos render --course curriculum/courses/COURSE_ID --session 12

   python -m teos render \
     --course curriculum/courses/COURSE_ID \
     --week 5 --day 2 \
     --schedule outputs/COURSE_ID-TERM-schedule.json
   ```

Never edit a generated lesson plan, guide, calendar, or LMS export as curriculum.
Change the unit or session and regenerate. The `weeks/` format and the
`generate --week` commands exist only to reproduce legacy approved artifacts.

## Canonical lesson authoring

When one session needs a governed, artifact-complete lesson source, author a
Canonical Lesson Model YAML record in `curriculum/courses/COURSE_ID/lessons/`.
The CLM binds session instruction, safety, activities, assessment, homework,
guidance, and reflection without adding presentation.

Validate it with:

```bash
python scripts/validate_schemas.py
```

Use stable IDs and references. In particular, the instructional brief
references canonical objective, standard, question, activity, and assessment
records rather than repeating their text. Classroom and shop instruction share
the same activity type and use `environment` for selection.

See the [Canonical Lesson Model
Specification](specifications/canonical-lesson-model.md) and [renderer
contract](../renderers/canonical-lesson-contract.md). A lesson with unavailable
sources or unverified content must remain `draft` or `in_review`; renderers
cannot fill its gaps.

Institution Profiles own operating rules and presentation configuration, not
course content. Academic calendars own term boundaries and events, not course
IDs or preassigned sessions. The Scheduler is the only component that combines
these records.
