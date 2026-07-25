# Tests

Tests use synthetic curriculum fixtures. Real curriculum remains solely under
`curriculum/`.

Run the suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

The Administrative Lesson Plan coverage verifies that the approved reference
content and populated official-template content both originate in the DSL204
course/week records. It also verifies removal of blank-template placeholders
and preservation of the official header artwork. Presentation-contract tests
compare the generated heading hierarchy, section set, two-column configuration
board, and list treatment with the approved FUN101 Week 7 documents without
using their instructional content as source data.
