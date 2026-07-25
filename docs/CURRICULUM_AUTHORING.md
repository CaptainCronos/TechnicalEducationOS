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

5. Separately define an institution-specific calendar and generate a schedule:

   ```bash
   python -m teos schedule \
     --course curriculum/courses/COURSE_ID \
     --calendar institutions/INSTITUTION_ID/calendars/COURSE_ID-TERM.json \
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
