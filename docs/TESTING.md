# Integration and Regression Testing

## Philosophy and organization

Tests protect public behavior and subsystem contracts. A test should live at
the narrowest level that can expose the failure:

| Category | Purpose | Typical dependency |
|---|---|---|
| Unit | Small validation or format contract | One production module |
| Integration | Interface interoperability | Two or more subsystems |
| End-to-end | Complete installed CLI/API workflow | Built package and filesystem |
| Regression | Permanent reviewed behavior | Canonical data, defect, or invariant |
| Performance | Representative timing comparison | Stable local/CI environment |

Tests do not mock TEOS subsystems when deterministic real implementations are
fast enough. Shared fixtures load the maintained Reference Curriculum once,
deep-copy only when mutation is needed, and write all build output under
pytest's temporary directories. Assertions target identifiers, diagnostics,
manifests, content, and format contracts rather than private call sequences.

## Integration inventory

The integration suite covers these production boundaries:

| Boundary | Evidence |
|---|---|
| Repository loading → runtime validation | Canonical course, units, and sessions load and validate together |
| Validation → compilation | Unit ownership, references, session order, and time reconciliation survive loading |
| Compilation → scheduling | Compiled sessions map to institution/calendar slots without source mutation |
| Scheduling → rendering | Assignment session/unit identifiers select the correct renderer inputs |
| Rendering → generation | Rendered text becomes Markdown, HTML, DOCX, and PDF through registered generators |
| Localization → rendering | Both locale catalogs translate titles, sections, labels, phases, units, and empty messages |
| Theme → generation | Theme tokens and locale reach HTML presentation without changing curriculum |
| Institution Profile → scheduling/rendering | Profile meeting rules schedule sessions and branding supplies presentation context |
| CLI → services | Legacy and canonical CLI commands exercise the same loaders, scheduler, renderers, and generators |
| Public API → manifest/files | `build()` returns detached results that agree with persisted output |

The end-to-end suite owns complete 96-artifact builds, CLI/API equivalence,
isolation, byte determinism, artifact parsing, and cross-document fidelity.
Those assertions are not duplicated in lower-level integration tests.

## Regression strategy and inventory

`examples/reference_curriculum` is the only permanent regression dataset. The
dataset lock records SHA-256 for each governed source and presentation asset in
`tests/snapshots/reference_dataset.json`. README changes are excluded because
they do not affect compilation. `reference_artifacts.json` separately locks
normalized generated outcomes.

The permanent suite protects:

- schema validity and canonical source fingerprints;
- exact curriculum size, time, phases, trace mappings, and reused standards;
- both institutional schedules, locales, and themes;
- renderer determinism and complete artifact inventory;
- CLI/API equivalence, build identity, source isolation, and failure cleanup;
- document structure, content fidelity, metadata, and cross-format parsing;
- the historical full-interface localization correction;
- the historical PDF long-line wrapping correction;
- the historical artifact/build traceability metadata correction; and
- unavailable extension diagnostics with no partial output.

When a source change is intentional, review its semantic effect, update focused
expectations first, recompute only the affected snapshot, and explain the
reason in the pull request. Never update a snapshot merely to make CI green.

## Edge and negative coverage

Valid edge cases include empty lecture/demonstration/lab/assessment component
lists, sessions with no assessment selection, no-lab rendering, both locales,
all themes, alternate calendars, large competency-to-standard mappings, reused
standards, empty rendered documents, holidays, insufficient calendar capacity,
and source immutability.

Negative cases include malformed JSON, schema-invalid repositories, duplicate
IDs, unresolved competency/objective/unit/assessment references, noncontiguous
sessions, schedule capacity and selector errors, missing or incomplete locale
catalogs, missing theme tokens, unknown locale/theme/profile/calendar,
corrupted or missing templates, unavailable renderers/generators, unwritable
outputs, and existing output directories. API failures raise `BuildError`;
CLI failures return 2 with an `Error:` diagnostic and no traceback.

The v2 source schema has no prerequisite/dependency-edge field, so it cannot
express a cyclic dependency input. The compilation result permanently asserts
an empty edge set and an acyclic flag. Adding cycle tests must wait for an
accepted model/API change; tests must not invent curriculum semantics.

The current model also has no instructor-assignment collection. Institution
profiles require the administrative `instructor` field, but a multiple-
instructor workflow cannot be expressed until that capability exists.

## Performance baseline

Run:

```bash
python -m pytest -m performance -s
```

Representative local measurements on Python 3.14 on 2026-07-28 were:

| Operation | Median |
|---|---:|
| Loading governed curriculum JSON | 0.000154 s |
| Runtime validation | 0.000351 s |
| Complete load/compile operation | 0.000428 s |
| Scheduling | 0.000113 s |
| Three renderers for one session | 0.000020 s |
| Four document generators for one render | 0.000388 s |
| Complete 96-artifact reference build | 0.025426 s |

Subsystem medians use seven repetitions. The guards are 1 second per
representative subsystem operation and 5 seconds for the complete build. These
large margins detect order-of-magnitude regressions without treating noisy CI
timing as a microbenchmark. Optimize only after repeatable profiling identifies
a bottleneck.

## Coverage review

Coverage is a production-path review tool, not a target by itself. CI publishes
branch coverage and XML for every supported Python version. The phase added
meaningful paths around catalog/template failures, format edge behavior, public
API result isolation, subsystem handoffs, large mappings, and canonical
negative inputs.

The measured non-performance suite on Python 3.14 reports 86% total branch
coverage (1,267 of 1,418 statements exercised). Generators and session
renderers are at 100%; the public application service is at 91%; CLI is at 85%;
records validation is at 79%; and scheduling is at 75%. The lower records and
scheduler figures are mostly individual defensive shape/date branches. Their
important production workflows, ownership/reference failures, calendar
linkage, closures, capacity, and selector diagnostics are covered.

Legacy weekly curriculum and DOCX-template rendering remain covered because
they reproduce approved documents. The primary risk areas are error branches
that require operating-system races or permission behavior, and the model
limits described above. Numeric coverage should not be increased with brittle
tests or mocks that cannot detect production integration failures.

To run the same review locally after installing the `dev` extra:

```bash
python -m pytest -m "not performance" \
  --cov=teos --cov-branch --cov-report=term-missing
```

## Marker and developer commands

Markers are registered under strict marker checking in `pyproject.toml`.

```bash
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m end_to_end
python -m pytest -m regression
python -m pytest -m "not performance"
```

Use `-x` for a first-failure loop and `--durations=10` for slow-test
diagnostics. A new defect fix should include the smallest reproducer under
`regression`, a diagnostic assertion for invalid input, and a positive
assertion for the corrected behavior. Reuse `conftest.py` factories rather than
copying the Reference Curriculum or build configuration.

## CI behavior

The test workflow:

- runs every non-performance test with coverage on Python 3.11 and 3.12;
- runs the source-level canonical regression suite explicitly on Python 3.11;
- builds and tests the installed wheel end-to-end outside the source import
  path;
- fails when any regression, artifact, or checkout-cleanliness check fails;
- retains JUnit and coverage evidence for 14 days; and
- runs timing baselines only for manual `workflow_dispatch`, retaining their
  JUnit properties for comparison.

The explicit source regression job excludes `tests/end_to_end` because the
installed-wheel job owns that environment. `pytest -m regression` locally
includes both permanent source and end-to-end regressions.
