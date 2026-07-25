# Schemas

These JSON Schemas document source-record contracts. Runtime validation also
checks cross-record ID relationships that JSON Schema cannot conveniently
express.

`course.schema.json`, `week.schema.json`, and `institution.schema.json` are the
machine-readable source contracts. The week contract supports both explicit
lecture/lab records and approved daily lesson plans with typed activities.

Daily lessons include the populated sections required by the Administrative
Lesson Plan template: materials, terminology, assessment alignment, industry
applications, common technician errors, shop tip, homework, and flex
activities. Required presentation labels and blank reflection prompts remain
renderer-owned.

Schema changes must be driven by real curriculum or required outputs and
recorded in `docs/decisions/`.
