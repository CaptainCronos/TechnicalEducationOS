# Legacy course records

This area owns the current course/week JSON records used by the working
validation and rendering pipeline.

Inputs: faithfully transcribed, approved existing curriculum.
Outputs: validated legacy records consumed by the current `teos/` application
and by future migration mappings.

The `dsl204/` records are the first real single-source proof. Their approved
DOCX files remain reference documents, not generator inputs.

These records remain authoritative for the compatibility pipeline, but new
compiler architecture targets `curriculum/blueprints/` and
`curriculum/models/`. Do not add direct slide-to-week automation or copy
generated documents back into these records.
