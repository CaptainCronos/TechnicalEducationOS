# Third-party notices

TEOS application source and project-authored templates are distributed under
the MIT License in [`LICENSE`](LICENSE).

## Runtime dependency

TEOS depends on `jsonschema`, which is distributed under the MIT License.
Installation tools may resolve its transitive dependencies (`attrs`,
`jsonschema-specifications`, `referencing`, and `rpds-py`); each is distributed
under an OSI-approved license. Exact resolved versions and license metadata must
be reviewed from the release verification environment because dependency
resolution varies by Python version and platform.

## Project assets

- `templates/jtech/admin_lesson_plan_template.docx` is a project-authored
  presentation template included under the repository MIT License.
- `examples/reference_curriculum/templates/` and
  `examples/reference_curriculum/themes/` are project-authored reference assets
  included under the repository MIT License.
- DOCX files under `tests/fixtures/` are regression fixtures authored or
  approved for this project. They are test-only and are excluded from built
  Python distributions.

No third-party standards manual, proprietary theme, font, or externally
licensed template is redistributed in the release. Users are responsible for
registering and licensing their own standards and instructional source
material.
