# Phase 1 Administrative Lesson Plan Status (Historical)

This document records the lesson-plan compatibility milestone that preceded the
curriculum compiler architecture. It remains useful implementation history but
is not the current roadmap. See [`ROADMAP.md`](../ROADMAP.md) and the
[architecture overview](architecture/overview.md).

Date reviewed: 2026-07-25

## Result

The repository can now generate production-quality J-Tech Administrative
Lesson Plans from the current DSL204 Week 5 curriculum records. Both generated
plans render as two-page, letter-size documents and follow the organization,
information density, typography, branded header, configuration board, and
reflection treatment established by the approved FUN101 Week 7 plans.

The architecture preserves the required ownership boundaries:

```text
curriculum records -> validation/reference resolution
                   -> J-Tech presentation renderer
                   -> disposable DOCX output
```

Phase 1 is technically ready for institution review. It should be declared
complete only after the generated files are accepted in J-Tech's supported
Microsoft Word environment. The repository does not contain structured FUN101
Week 7 curriculum, so the approved FUN101 documents can define presentation
but cannot themselves be regenerated or used as curriculum sources.

## Completed work

- Read the repository constitution, architecture, source contracts, validators,
  renderers, tests, and documentation.
- Inspected the official blank J-Tech Administrative Lesson Plan template and
  both approved FUN101 Week 7 Administrative Lesson Plans at the DOCX/XML and
  rendered-page levels.
- Classified every visible element by ownership:
  - curriculum owns teaching content and relationships;
  - the J-Tech layer owns branding, document hierarchy, labels, layout,
    typography, list treatment, and blank reflection prompts;
  - DOCX files in `outputs/` remain disposable generated artifacts.
- Moved J-Tech DOCX presentation into
  `teos/institutions/jtech.py`. `teos/docx.py` is now only a compatibility
  facade.
- Rebuilt the renderer around the approved finished-document standard while
  continuing to use the official blank form as the package and branding base.
- Added the approved production presentation features:
  - J-Tech header artwork;
  - blue heading hierarchy;
  - compact Times New Roman body typography;
  - one-inch letter page geometry;
  - a true two-column configuration board;
  - bulleted activity and error lists;
  - content-driven optional sections;
  - compact blank instructor-reflection fields.
- Removed the blank form's forced section transition, which could create an
  empty trailing branded page.
- Generated the current source records as:
  - `outputs/dsl204-week-05-day-01-administrative.docx`
  - `outputs/dsl204-week-05-day-02-administrative.docx`
- Verified both generated DOCX packages with ZIP integrity checks and
  LibreOffice conversion.
- Expanded automated coverage from 21 to 22 tests. The suite now checks the
  FUN101 presentation contract as well as field provenance, reference
  integrity, placeholder removal, header-artwork preservation, and CLI output.

## Ownership and renderer responsibilities

### Curriculum content

- course and lesson identity;
- duration and classroom/shop segments;
- objectives and competency/standard relationships;
- essential question and student objective summary;
- materials and terminology;
- warm-up, academic, shop, and exit activities;
- industry applications and common technician errors;
- shop tip, assessment, homework, and flex guidance.

### J-Tech presentation

- logo and branded header;
- document title construction;
- section names and ordering;
- “Captain Joe's Shop Tip” label;
- configuration-board labels and column layout;
- heading color, fonts, sizes, margins, and spacing;
- bullet treatment;
- blank instructor-reflection prompts.

### Renderer

The renderer resolves source IDs, projects the selected lesson into the
institution presentation, formats durations, joins source lists for display,
omits sections with no source content, and writes the DOCX package. It does not
author, infer, or duplicate instructional content.

## Field provenance

Every populated instructional value in the generated plans has a structured
source:

| Generated field | Authoritative source |
|---|---|
| Course | `course.title` |
| Week and day | `week.week_number`, `lesson.day_number` |
| Lesson title | `lesson.title` |
| Time | `lesson.duration` |
| Warm Up and Exit | typed `lesson.activities` |
| Objective | statements referenced by `lesson.objective_ids` |
| Standard | competencies referenced by those objectives |
| Essential Question | `lesson.essential_question` |
| Objectives | `lesson.objective_summary` |
| Materials and terminology | `lesson.materials`, `lesson.terminology` |
| Academic and shop activities | typed `lesson.activities` |
| Industry applications | `lesson.industry_applications` |
| Common technician errors | `lesson.common_technician_errors` |
| Shop tip | `lesson.instructor_shop_tip` |
| Assessment | assessments referenced by `lesson.assessment_ids` |
| Homework and flex activities | `lesson.homework`, `lesson.flex_activities` |

The title syntax, labels, configuration board, bullets, and empty reflection
areas contain no instructional claims and are presentation-owned.

## Schema assessment

No curriculum-schema change was necessary. The current course/week contracts
already model every populated field required by the available DSL204 source
records, including stable objective, competency, activity, and assessment
relationships.

The approved FUN101 files omit some sections used by DSL204, but no structured
FUN101 record is available to prove whether those values are absent curriculum
or merely omitted presentation. Relaxing or redesigning the curriculum
contract on that evidence would violate the project's source-of-truth rule.
The renderer therefore treats supported presentation sections as
content-driven without changing the authoritative records.

## Presentation comparison

| Area | Generated DSL204 plans | Approved FUN101 Week 7 plans |
|---|---|---|
| Page size | Letter | Letter |
| Page count | 2 pages each | 2 pages each |
| Margins | 1 inch | 1 inch |
| Branding | Official J-Tech header/logo | Official J-Tech header/logo |
| Title hierarchy | Blue Heading 1 plus lesson subtitle | Same |
| Section hierarchy | Blue Heading 2 | Same |
| Body typography | Compact Times New Roman | Compact Times New Roman |
| Configuration board | 2 columns, narrow label/wide content | 2 columns, equal-width cells |
| Activities/errors | Bulleted lists | Bulleted lists |
| Reflection | Blank prompts at document end | Same |
| Extra source-backed sections | Time, terminology, and flex guidance | Not populated in the approved FUN101 files |

The narrower label column is an intentional usability refinement within the
same two-column organization: it reduces label whitespace and gives the
instructional value more readable line length. Section presence varies only
when the current curriculum record contains additional structured content.

## Remaining architectural and acceptance gaps

- The approved FUN101 Week 7 documents have no corresponding structured
  FUN101 curriculum records. Their presentation can be tested, but their
  instructional provenance and exact regeneration cannot be verified without
  adding curriculum that the repository does not currently contain.
- Final behavior has been inspected through LibreOffice. Acceptance in the
  institution's supported Microsoft Word version remains outstanding.
- The blank J-Tech form contains only the header, top fields, configuration
  board, and objective area. The institution renderer must construct the
  remaining finished-plan body; those elements are not available as named
  placeholders in the base form.
- Institution approval is still needed for the 25/75 configuration-board
  column split. The approved plans use equal-width cells, while the generated
  split is denser and more readable for long instructional values.

## Recommendations before declaring Phase 1 complete

1. Open both generated DSL204 plans in the supported Microsoft Word version
   and obtain instructor/administrative acceptance.
2. Confirm the configuration-board column proportion during that review.
3. If FUN101 Week 7 regeneration is required, transcribe its existing
   curriculum into authoritative structured records as a separate,
   instructor-reviewed curriculum-loading task; do not parse the approved DOCX
   output back into curriculum automatically.
4. Keep all non-Administrative output types deferred until this one pipeline is
   accepted.

Instructor Lesson Plans, quizzes, labs, PowerPoint outlines, and other output
types were not extended during this work.
