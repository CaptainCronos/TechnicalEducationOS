# Test fixtures

Binary fixtures in this directory protect the approved legacy DOCX presentation
contract. They are test inputs or golden comparisons, not generated release
artifacts, runtime package data, templates, or curriculum sources.

- `jtech/` contains approved presentation examples.
- `legacy/` contains reviewed DSL204 output goldens.

Tests may read these files but must write all generated output under pytest
temporary directories.
