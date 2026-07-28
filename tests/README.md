# Automated tests

TEOS tests verify observable contracts at the narrowest useful level. Shared
Reference Curriculum fixtures live in `conftest.py`; tests generate artifacts
only under pytest temporary directories.

The categories are:

- `unit/`: isolated validation and format contracts;
- `integration/`: direct interfaces between two or more subsystems;
- `end_to_end/`: complete CLI and public-API builds, including physical files;
- `regression/`: canonical invariants, known defects, negative inputs, and the
  Reference Curriculum dataset lock; and
- `performance/`: optional timing baselines with deliberately generous guards.

Run the standard suite with:

```bash
python -m pytest -m "not performance"
```

Run one category with:

```bash
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m end_to_end
python -m pytest -m regression
python -m pytest -m performance -s
```

Regression and end-to-end are intentionally overlapping properties: a
wheel-installed pipeline test is end-to-end in scope and also protects a
permanent behavior. Directory placement describes scope; markers describe the
suite memberships developers and CI need.

The permanent dataset is `examples/reference_curriculum`. Its reviewed file
digests are in `snapshots/reference_dataset.json`; artifact-level normalized
digests are in `snapshots/reference_artifacts.json`. Generated documents are
never fixtures and must not be committed.

See [Integration and Regression Testing](../docs/TESTING.md) for philosophy,
inventory, maintenance rules, expected duration, coverage, and CI behavior.
