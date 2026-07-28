# Tests

Tests own automated verification and synthetic fixtures. Inputs are schemas,
compiler and renderer behavior, and deliberately synthetic records. Outputs are
test results and diagnostics. Real curriculum remains solely under
`curriculum/`.

Run the suite from the repository root:

```bash
python -m pytest -q
```

The permanent generated-document checks live in
`end_to_end/test_artifact_validation.py`. They build into temporary
directories and validate inventory, required sections, source fidelity,
cross-document consistency, all physical formats, metadata, localization,
themes, and normalized snapshots. The snapshot digests are stored in
`snapshots/reference_artifacts.json`; generated documents are not fixtures and
must not be committed.

The Administrative Lesson Plan coverage verifies that the approved reference
content and populated official-template content both originate in the DSL204
course/week records. It also verifies removal of blank-template placeholders
and preservation of the official header artwork. Presentation-contract tests
compare the generated heading hierarchy, section set, two-column configuration
board, and list treatment with the approved FUN101 Week 7 documents without
using their instructional content as source data.
