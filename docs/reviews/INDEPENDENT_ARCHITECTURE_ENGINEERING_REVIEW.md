# Independent Architecture and Engineering Review

**Project:** Technical Education OS (TEOS)  
**Review date:** 2026-07-28  
**Reviewed revision:** `aea5145` (`main`)  
**Release posture reviewed:** `1.2.0a1` / `v1.2.0-alpha1` documentation  
**Decision:** Conditionally ready for public alpha evaluation; not yet ready for
an unqualified stable-release or broad-production recommendation.

## 1. Executive summary

TEOS is a thoughtfully governed, compact curriculum compiler with unusually
strong documentation, deterministic artifact generation, explicit authority
boundaries, and a credible automated regression suite for its size. The
project's central architectural rule—educational artifacts consume validated
curriculum rather than source documents, calendars, or templates—is stated
consistently and is enforced in the implemented canonical session pipeline.
The public Python API is deliberately small, complete builds are staged before
publication, generated artifacts carry trace metadata and hashes, and the
reference curriculum exercises meaningful institution, calendar, locale, and
theme variation.

The primary concern is not basic correctness. It is the distance between the
scope implied by the governing v2 architecture and the smaller alpha runtime
that actually exists. Knowledge registration/extraction, blueprint
compilation, approval/staleness lifecycle, and a durable traceability service
are designed in detail but are not implemented application subsystems. The
current compiler is principally a schema/semantic validator, scheduler,
renderer, and file generator. This is acceptable for an alpha if every
architecture document clearly distinguishes implemented, compatibility, and
target-state capabilities. It would be misleading as a stable platform claim.

The codebase is readable but concentrated. Three semantic validators contain
hundreds of imperative checks, the complete application pipeline is one
290-line function, and the institution-specific DOCX renderer is another
202-line function. Untyped `dict[str, Any]` records, schema/runtime validation
duplication, text-replacement localization, and parallel legacy/canonical
rendering paths will increase change risk as formats and curriculum models
grow. These are maintainability risks, not present correctness failures.

Testing is a project strength. The review executed 93 required tests and two
performance tests successfully on Python 3.14.4, including byte-deterministic
CLI/API builds, negative inputs, regression snapshots, physical artifact
parsing, localization, scheduling, and output atomicity. The repository
declares branch coverage of at least 85 percent in CI. The review environment
did not have `pytest-cov`, `ruff`, or `build`, so it could not independently
reproduce coverage, lint, or package-build results locally. The repository's
schema and Markdown-link checks both passed.

Documentation and governance are substantially above the normal alpha
baseline. A new contributor has a coherent path from installation through
architecture, authoring, testing, and release. Remaining onboarding friction
comes from the split distribution model: the wheel contains application code,
while schemas and reference inputs must come from a repository checkout.

Operationally, CI is broad for a small project, but stable-release evidence is
not complete. CI tests only Linux, third-party actions and Python dependencies
are version-ranged rather than commit/hash locked, release artifacts have
checksums but no attestation/signing/SBOM evidence, and branch protection is
documented as a recommendation rather than verified configuration. The
repository has one named owner across all CODEOWNERS paths, creating a
material continuity and review-independence risk.

One local repository-integrity issue requires immediate attention:
`.git/refs/**/README.md` and `.git/objects/*/README.md` placeholder files cause
`git fsck --full` to report invalid refs and bad object files. These files are
not tracked project content and normally would not propagate through a fresh
clone, but this checkout should not be used to create or validate releases
until it is repaired or replaced with a verified clean clone.

No Critical application defect was identified. Six High risks and eight
Medium risks should be dispositioned before stable release. Broad public alpha
adoption is reasonable with the project's existing warnings and with the
repository-integrity issue isolated.

## 2. Review scope, method, and evidence

This was a read-only engineering assessment of tracked source, tests, schemas,
documentation, examples, governance, workflows, packaging metadata, recent
history, and local Git integrity. No functionality was added and no project
contract was changed.

Evidence reviewed includes:

- all tracked files under `teos/`, `tests/`, `schemas/`, `scripts/`, `docs/`,
  `.github/`, `examples/reference_curriculum/`, and the top-level project
  guides;
- the public API and CLI, canonical and compatibility pipelines, record
  validation, scheduler, renderers, generators, and J-Tech adapter;
- five CI/release workflow files, package metadata, compatibility policy,
  release runbooks, governance, security, and maintenance guidance;
- approximately 4,500 lines of application Python and 2,700 lines of tests;
- the reference curriculum and its dataset/artifact snapshots; and
- the current worktree, recent commits, tags, ignored build products, and Git
  object/ref integrity.

Commands executed:

```text
python -m pytest -m "not performance"
python -m pytest -m performance -s
python scripts/validate_schemas.py
python scripts/check_markdown_links.py
git fsck --full
```

Observed results:

- required suite: **93 passed, 2 deselected**, 0.61 seconds;
- performance suite: **2 passed, 93 deselected**, 0.07 seconds;
- complete reference build median: **0.025714 seconds** in this environment;
- schema gate: **6 schemas and 6 repository records passed**;
- Markdown links: **passed**; and
- Git integrity: **failed with invalid `README.md` refs and bad
  `.git/objects/*/README.md` files**.

Review limitations:

- Remote GitHub branch/ruleset configuration and historical workflow results
  were not independently queried. Workflow definitions were assessed as code.
- The active environment lacked the optional `ruff`, `pytest-cov`, and
  `build` packages. Lint, coverage, wheel/sdist construction, and `twine`
  checks were therefore assessed from configuration, tests, scripts, and
  documented release evidence rather than rerun locally.
- No external contributor usability study, production-size curriculum corpus,
  accessibility audit in assistive technology, or Windows/macOS execution was
  performed.
- The conceptual benchmark uses established practices common to mature
  open-source Python projects; it is not a feature-by-feature competitive
  analysis.

## 3. Architecture assessment

### 3.1 Architectural model

The architecture is coherent and teachable. The repository defines distinct
knowledge, curriculum, institution/calendar, scheduling, rendering, and output
concerns. Authority rules are explicit:

```text
registered evidence
      ↓
reviewed curriculum decisions
      ↓
canonical course → units → sessions
      ↓                  ↑
institution + calendar → scheduler
      ↓
resolved session → renderer → generator → disposable artifact
```

The implemented canonical path respects the most important boundaries:

- calendar data affects scheduling, not curriculum ownership;
- rendering receives a course, unit, resolved session, and optional
  institution—not a source document or calendar;
- presentation themes and locale catalogs are applied after canonical content
  is selected;
- source inputs are hashed and outputs include build, curriculum, schedule,
  institution, renderer, generator, locale, and theme identity;
- a complete build stages outputs and publishes the directory only after
  success; and
- legacy week records are isolated behind compatibility commands and
  documentation.

The architectural decision records, specifications, data-flow document, and
repository-organization standard reinforce one another. This is a strong base
for governance and future review.

### 3.2 Adherence and gaps

The runtime does not yet implement the full governing architecture:

| Governing concept | Implemented state | Assessment |
|---|---|---|
| Knowledge-source registry and extraction | Directory guidance and specifications; no runtime registry/extractor service | Target state |
| Blueprint compiler and approval | Specifications and repository placeholders; canonical records are loaded/validated directly | Target state |
| Structured course/unit/session model | JSON schemas plus semantic validation | Implemented |
| Institution profile and academic calendar | Schemas, semantic validation, examples, scheduling | Implemented |
| Scheduler | Deterministic sequential assignment with closures and aliases | Implemented, intentionally bounded |
| Traceability service | Manifest fields, source hashes, mappings, and audits; no durable graph/service | Partial |
| Approval/staleness lifecycle | Documented lifecycle; no executable state transition or invalidation model | Target state |
| Artifact renderers/generators | Three canonical renderers and four deterministic generators | Implemented |
| Extension governance | Policy and in-process registries; public executable extension contract deferred | Experimental |

The phrase “governing architecture” therefore currently mixes invariant
architecture with future platform architecture. The roadmap recognizes this
gap, but an adopter can still infer that the registry, compiler, trace service,
and approval lifecycle are operational. Documents should mark each subsystem
as Implemented, Partial, Compatibility, or Target without weakening the
long-term design.

### 3.3 Module organization and dependency boundaries

The dependency direction is mostly sound:

- `teos.application` orchestrates records, scheduler, session renderers, and
  generators;
- record validation does not depend on presentation;
- the scheduler depends only on record contracts;
- canonical renderers are pure text projections;
- physical generators operate on rendered text plus presentation tokens; and
- the public package re-exports only `BuildConfig`, `BuildResult`,
  `BuildError`, `build`, and `__version__`.

The main boundary weakness is representation, not imports. Most subsystem
interfaces pass mutable, structurally implicit dictionaries. Consumers rely on
specific nested keys and catch `KeyError`/`TypeError` at the orchestration
boundary. This keeps the alpha small, but it makes refactoring, static
analysis, and third-party extension conformance difficult.

`application._build` owns discovery, schema validation, semantic validation,
compilation summary construction, scheduling, localization, generation,
manifest construction, source-race detection, staging, and publication. It is
a useful transaction boundary but too broad as an implementation unit. The
roadmap's proposed repository/compiler/renderer/generator/publisher ports are
the right decomposition, provided behavior stays unchanged during extraction.

### 3.4 Extensibility and public interfaces

The intentionally small public API is a strength. `BuildConfig` is immutable,
`BuildResult` returns detached summaries, controlled failures use
`BuildError`, and CLI/API logical equivalence is tested.

Extensibility is currently internal. `SESSION_RENDERERS` and `GENERATORS` are
module dictionaries with implicit callable signatures, and the compatibility
policy correctly labels them experimental. Mature extension support will
require versioned descriptors, typed input/output contracts, capability
negotiation, collision rules, failure isolation, and conformance fixtures.
Those should not be promised before the v1.3/v2 governance work already
identified by the project.

### 3.5 Scalability

The present architecture is appropriate for a local alpha and the eight-session
reference dataset. It is not yet characterized for institution-scale or
multi-course corpora:

- all source records are loaded eagerly;
- every rendered intermediate and manifest artifact entry is retained in
  process;
- work is single-process and serial across sessions, renderers, and formats;
- validation repeatedly traverses nested dictionaries and sometimes uses
  linear lookup/index operations;
- all outputs are staged on one filesystem before atomic directory
  publication; and
- the performance suite measures only the compact reference corpus with
  generous upper bounds.

None of these choices is wrong for the current scope. Before making scale
claims, TEOS needs corpus-size definitions, memory/disk/fan-out measurements,
and complexity targets. Distributed execution would be premature; bounded
streaming and explicit stage interfaces should come first.

### 3.6 Architecture conclusion

**Rating: 7.5/10 — Strong conceptual architecture, good core-boundary
enforcement, partial runtime realization.**

The design quality is above average for an alpha. The score is limited by
target/implemented ambiguity, dictionary-shaped subsystem contracts, the
concentrated application service, and the absence of executable lifecycle and
trace services described by the governing model.

## 4. Code quality assessment

### 4.1 Strengths

- Naming is generally direct and domain-oriented.
- Functions use controlled exceptions with contextual diagnostics.
- Deterministic serialization, stable ZIP timestamps, normalized release
  archives, and source/artifact hashes demonstrate disciplined reproducibility.
- Output staging and cleanup prevent partial successful-looking builds.
- Pure renderer/generator functions are easy to exercise.
- Public dataclasses are frozen, and returned mutable structures are deep
  copied.
- Source records are re-read before publication to detect changes during a
  build.
- HTML instructional content is escaped before insertion.
- No broad `except Exception`, bare `except`, TODO stubs, or silent `pass`
  statements were found in production code.

### 4.2 Complexity and concentration

A simple AST-based review found the following hotspots:

| Function | Approx. lines | Approx. branch/decision complexity | Concern |
|---|---:|---:|---|
| `records.validate_week` | 276 | 58 | Large compatibility validator |
| `records.validate_curriculum` | 214 | 40 | Canonical semantic rules mixed together |
| `institutions.jtech.render_administrative_docx` | 202 | 35 | Presentation construction and template mutation |
| `application._build` | 290 | 32 | Entire transaction and all pipeline stages |
| `records.validate_institution` | 143 | 32 | Deep operational-record validation |
| `render._render_daily_administrative` | 136 | 18 | Legacy presentation path |
| `audit.coverage_findings` | 35 | 17 | Many policy branches in one expression-oriented function |

The numeric values are heuristic rather than tool-certified cyclomatic
complexity, but the structural concentration is evident from inspection.
Refactoring should extract named rule groups and stage boundaries while
preserving current diagnostics and snapshots.

### 4.3 Duplication and consistency

Validation exists in both JSON Schema and imperative Python. Some duplication
is necessary for cross-record semantics, but ownership is not formally mapped:
future contributors may add a constraint to one layer and omit the other.
Canonical and legacy rendering also repeat bullet/number formatting, context
assembly, and artifact concepts. The duplication is currently manageable but
should be monitored as legacy support ages.

`render.py` and `session_render.py` represent two domain generations. Their
separation is helpful, yet similarly named functions can be selected
incorrectly during maintenance. Compatibility modules or namespaces should be
made unmistakable when the next internal reorganization occurs.

### 4.4 Error handling and defensive programming

Normal missing-file and malformed-JSON cases become `RecordError`, and the CLI
converts those to exit code 2 without tracebacks. Negative tests cover many
important paths. Remaining weaknesses include:

- `load_json` does not normalize `UnicodeDecodeError`, permission errors, or
  general read failures, so some ordinary input failures can escape the public
  controlled-error contract;
- generation catches a selected tuple of exception types, so unexpected
  renderer/generator failures can escape without API normalization;
- localization operates by exact English heading/prefix replacement, coupling
  locale behavior to renderer wording and Markdown layout;
- locale and theme catalogs lack dedicated repository schemas and are checked
  by ad hoc application rules;
- theme token values are inserted into an HTML `<style>` element without
  contextual sanitization, allowing an untrusted theme value to alter generated
  HTML beyond presentation;
- the application derives a template-relative path by splitting on the
  literal string `reference_curriculum/`, which couples generic builds to the
  sample repository's path convention;
- locale, theme, and template files are hashed but omitted from the final
  source-change comparison; and
- caught `KeyError`/`TypeError` failures become generic “build generation
  failed” messages rather than stable, located diagnostics.

These are Medium risks in the current trusted-local alpha model. They become
High if arbitrary third-party repositories are processed or generated HTML is
served in a privileged browser context.

### 4.5 Simplification opportunities

Without adding functionality:

1. define a validation-ownership table mapping every invariant to schema,
   semantic validator, or cross-record compiler;
2. split `_build` into private load, validate, compile, render/generate, and
   publish stages behind the same public transaction;
3. introduce internal typed records/protocols at subsystem boundaries while
   keeping JSON and public API compatibility;
4. replace exact rendered-text localization with structured renderer fields;
5. isolate compatibility code under explicit legacy modules;
6. share small formatting primitives only where semantics are identical; and
7. replace sample-name path parsing with a documented repository-relative path
   contract and containment check.

### 4.6 Code quality conclusion

**Rating: 7.0/10 — Clear and disciplined, with material complexity hotspots.**

The code is easy to follow at repository scale and defensively written around
the primary happy and failure paths. The score reflects concentrated functions,
weakly typed boundaries, brittle localization/path conventions, and growing
legacy/canonical duplication.

## 5. Testing assessment

### 5.1 Test portfolio

The suite has five explicit categories:

| Category | Evidence | Assessment |
|---|---|---|
| Unit | Four focused contract/generator/validation tests | Small; useful but not the primary philosophy |
| Integration | Canonical subsystem boundaries, session scheduling/rendering, legacy workflow | Strong |
| Regression | Dataset locks, artifact snapshots, known defects, negative inputs, reference curriculum | Strong |
| End-to-end | CLI and public API complete builds; physical artifact validation | Very strong for alpha |
| Performance | Stage timings and one complete compact build | Baseline only |

The suite intentionally favors observable contracts over isolated
implementation mocking. That is appropriate for a compiler whose major risks
are cross-record semantics and generated artifacts. Tests use temporary
directories and do not modify authoritative inputs.

### 5.2 Determinism and fixture quality

Determinism is exceptionally well covered:

- CLI and API builds are compared byte for byte;
- source trees are hashed before/after builds;
- reference datasets and normalized artifacts have reviewed snapshots;
- ZIP timestamps and archive metadata are controlled;
- schedules are regenerated and compared;
- artifacts carry content hashes checked against physical files; and
- failed builds are asserted not to leave output directories.

The reference curriculum is compact, understandable, and includes meaningful
variation rather than arbitrary fixture noise. It explicitly documents known
model and artifact limitations. Legacy binary fixtures are separated from
source templates.

### 5.3 Gaps

1. **Unit isolation:** complex semantic validators, localization, path
   resolution, and publication logic have fewer narrow tests than their branch
   count warrants.
2. **Error normalization:** invalid UTF-8, permissions, disappearing files,
   concurrent mutation of presentation inputs, and unexpected plugin callable
   failures are not demonstrated as controlled public failures.
3. **Security-oriented artifacts:** adversarial locale/theme/template content,
   path traversal/containment, oversized input, and HTML active-content
   boundaries need explicit tests before untrusted repository processing.
4. **Scale:** the eight-session corpus cannot support claims about hundreds of
   courses, large source catalogs, or high artifact fan-out.
5. **Platform matrix:** CI covers Python 3.11/3.12 on Ubuntu only despite the
   “OS Independent” classifier. Filesystem, locale, ZIP, and office-document
   behavior should be sampled on Windows and macOS before stable release.
6. **Static contracts:** Ruff checks imports/basic errors, but CI has no type
   checker despite extensive nested dictionary contracts.
7. **Schema examples:** the repository schema gate validates six production
   records; the reference records are covered in tests, but locale, theme,
   manifest, rendered-record, and compiled-summary contracts do not all have
   formal schemas.
8. **Accessibility/viewers:** parser and text preservation tests do not prove
   accessible PDF/DOCX structure or behavior in representative viewers.
9. **Coverage reproducibility:** CI declares branch coverage and an 85 percent
   floor, but the review could not rerun it because `pytest-cov` was absent
   locally. Documentation reports lower module-level coverage in records and
   scheduling and correctly explains those residual branches.

### 5.4 Testing conclusion

**Rating: 8.5/10 — Excellent integration/regression discipline; targeted edge
and scale gaps remain.**

The suite provides high confidence in the supported compact pipeline. It
should not yet be interpreted as evidence for broad platform scale, untrusted
input security, cross-platform compatibility, or artifact accessibility.

## 6. Documentation assessment

### 6.1 Coverage and quality

The repository provides:

- a concise top-level README with installation, quick start, architecture,
  repository map, quality posture, and documentation index;
- `README_FIRST.md` and `PROJECT_HANDOFF.md` as contributor orientation and
  constitutional constraints;
- maintained architecture overview, data-flow, repository-organization,
  specifications, and six ADRs;
- installation, developer, testing, release, compatibility, maintenance,
  support, security, contribution, governance, RFC, and plugin-governance
  guides;
- separate CLI and public API documentation;
- a complete end-to-end runbook with expected artifacts and failure behavior;
- a detailed reference curriculum walkthrough; and
- documentation authority and review expectations.

The internal Markdown-link checker passes. Commands are generally concrete,
copyable, and aligned with CI. Known limitations are disclosed rather than
hidden.

### 6.2 Contributor onboarding

A technically experienced Python contributor should be able to:

1. identify the supported Python versions;
2. create an editable environment;
3. understand architecture and authority boundaries;
4. run schema, test, lint, and link gates;
5. exercise the reference pipeline;
6. locate public compatibility promises; and
7. prepare a governed pull request.

Likely onboarding friction:

- the PyPI-style package install alone does not include the schemas/reference
  repository needed for the main complete-build example;
- “architecture v2” can be confused with “runtime v2” and package version
  `1.2.0a1`;
- the top-level tree has many conceptual directories whose executable
  implementation is deferred;
- generated documentation is not published as a searchable/versioned site;
- there is no short “first contribution” path that identifies a safe,
  representative change and its minimum checks; and
- externally measured time-to-first-build evidence is still a roadmap item.

### 6.3 API and reference documentation

The public API documentation is proportionate to the deliberately small API
and states output-path behavior and exceptions. The CLI guide describes
canonical versus compatibility commands and exit codes. It does not attempt to
stabilize internal registries.

As stable release approaches, API/CLI documentation should add:

- a formal stability annotation per command/field;
- machine-readable manifest and schedule schemas;
- diagnostic categories/codes;
- resource/size constraints;
- trust expectations for repository inputs and generated HTML; and
- migration examples from compatibility records.

### 6.4 Documentation conclusion

**Rating: 8.5/10 — Comprehensive, principled, and navigable, with state-model
ambiguity.**

Documentation is a major project strength. The key correction is to label
implemented versus target-state architecture consistently and validate
onboarding with people who did not help design the repository.

## 7. Operational readiness assessment

### 7.1 Installation and configuration

Strengths:

- standard PEP 517/setuptools packaging;
- explicit Python 3.11/3.12 support;
- one small runtime dependency with an upper major bound;
- editable and artifact-install instructions;
- wheel and sdist validation workflows;
- isolated installed-package verification outside the source import path; and
- explicit configuration through `BuildConfig`/CLI arguments rather than
  hidden global state.

Concerns:

- wheel users still need a compatible external repository and schema
  directory;
- there is no single project/repository manifest defining schema location,
  package compatibility, defaults, or configuration precedence;
- dependency installation is not lock/hash reproducible;
- only Linux is in the automated platform matrix; and
- the review environment's missing optional tools shows that the developer
  guide assumes successful extra installation but has no bootstrap
  verification command.

### 7.2 CI and developer workflow

The five workflows separate build, quality, tests, release validation, and
tagged release. They apply read-only default permissions, concurrency
cancellation, timeouts, isolated installation, JUnit/coverage artifacts,
checkout-cleanliness checks, and a manual performance baseline.

Improvement areas:

- duplicated environment/build setup increases maintenance and version-drift
  risk;
- GitHub Actions are pinned to moving major tags, not immutable commit SHAs;
- pip dependencies are ranges rather than a reviewed CI/release lock;
- no Windows/macOS job validates the portability claim;
- no dependency/security scan, SBOM, artifact attestation, or signature is
  produced;
- release notes are filename-coupled to tags and should be preflight checked
  before a tag triggers the release job; and
- recommended branch/tag protection cannot be proven from repository files.

### 7.3 Release, packaging, and versioning

The release procedure is disciplined: clean-tree checks, deterministic build
script, wheel/sdist verification, metadata validation, checksum creation,
draft release creation, compatibility review, and explicit human publication.
Semantic Versioning and PEP 440 mapping are documented.

Current evidence remains pre-release:

- package metadata reports `1.2.0a1`;
- only `v0.1.0` is present as a valid local Git tag;
- ignored `dist/` artifacts exist locally but are not authoritative release
  evidence;
- no signed tag/artifact provenance or package-index publication evidence was
  reviewed; and
- external installation pilots and stable migration/support evidence remain
  roadmap gates.

### 7.4 Repository integrity

`git fsck --full` reports invalid refs:

```text
refs/README.md
refs/heads/README.md
refs/remotes/README.md
refs/remotes/origin/README.md
refs/tags/README.md
```

It also reports `bad sha1 file` for placeholder files named
`.git/objects/<prefix>/README.md`. These are local Git-administration files,
not tracked source files. Ordinary Git status, log, and tracked object access
still work, but ref enumeration emits warnings and full integrity verification
fails. A release must not be cut from a repository that fails Git integrity
checks. The safe remediation is to preserve any unique work, compare with the
remote, and use a verified clean clone or remove only confirmed placeholder
files under a documented recovery procedure.

### 7.5 Operational conclusion

**Release readiness rating: 6.5/10 — Well-prepared alpha automation, incomplete
stable evidence and a local Git-integrity blocker.**

The application can be evaluated and integrated as alpha software. Stable
release should wait for clean repository integrity, successful full release
rehearsal, cross-platform decision/evidence, supply-chain improvements,
external install pilots, and verified repository protection.

## 8. Engineering risk register

Severity represents residual risk at the reviewed revision. “Owner” names the
responsible role, not a specific person.

### Critical

No Critical defect was identified in the implemented supported alpha
pipeline. Any future failure that can silently change approved curriculum
meaning, cross institutional authorization boundaries, or publish mismatched
artifacts should be treated as Critical.

### High

| ID | Risk | Likelihood / impact | Evidence | Mitigation and verification | Owner |
|---|---|---|---|---|---|
| H-01 | Governing architecture is read as implemented platform capability | Medium / High | Registry, extraction, approval/staleness, and durable trace services are specified but absent from runtime | Add implementation-state labels and a conformance matrix; test every “implemented” claim | Architecture steward |
| H-02 | Core change risk from concentrated, weakly typed pipeline and validators | High / High | `_build` 290 lines; canonical validator 214; legacy validator 276; dictionary contracts | Extract private stage/rule boundaries without behavior change; add typed internal contracts and characterization tests | Core maintainer |
| H-03 | Local Git metadata corruption invalidates release provenance checks | High / High | `git fsck --full` reports invalid refs and bad object files | Preserve unique work; repair from known-good remote or reclone; require clean `git fsck` in release rehearsal | Release maintainer |
| H-04 | Maintainer and review authority are concentrated in one account | High / High | All CODEOWNERS paths name one owner; governance recommends two maintainers when possible | Recruit/authorize a second release/security steward; document recovery and succession drill | Governance |
| H-05 | Stable release supply-chain evidence is incomplete | Medium / High | Moving action tags, ranged dependencies, checksums only, no SBOM/attestation/signature reviewed | Pin privileged automation immutably; add dependency review, SBOM, provenance/attestation and signing decision | Release/security |
| H-06 | Broad adoption exceeds validated workload/platform envelope | Medium / High | Eight-session benchmark, Linux-only CI, eager serial fan-out | Define supported corpus/platform envelope; add representative large-corpus and selected cross-platform gates before claims | Product/core |

### Medium

| ID | Risk | Likelihood / impact | Evidence | Mitigation and verification | Owner |
|---|---|---|---|---|---|
| M-01 | Ordinary malformed input escapes controlled error contract | Medium / Medium | UTF-8/permission/general I/O errors are not uniformly normalized | Add negative tests and normalize user-caused I/O/decode errors with stable locations | Core maintainer |
| M-02 | Localization breaks when renderer wording changes | High / Medium | Exact English heading and prefix replacement after rendering | Move toward structured localized labels; lock renderer/locale conformance in unit tests | Presentation maintainer |
| M-03 | Untrusted theme values can alter generated HTML beyond presentation | Medium / High | Theme tokens inserted directly in `<style>`; no theme schema | Publish trust model; schema/constrain tokens; add adversarial artifact tests; sandbox served artifacts | Security/presentation |
| M-04 | Generic builds depend on sample repository path wording | Medium / Medium | Template path split on literal `reference_curriculum/` | Define repository-relative path semantics and containment; test renamed repositories | Core maintainer |
| M-05 | Source mutation detection is incomplete | Low / High | Final snapshot excludes locale, theme, and template files | Rehash every declared source immediately before publication and compare full identity | Core maintainer |
| M-06 | Wheel installation does not provide a self-contained first build | High / Medium | Application-only distribution requires external schemas and inputs | Make split model unmistakable; provide verified acquisition/version compatibility workflow in a future release | Developer experience |
| M-07 | Schema and semantic validation drift | Medium / Medium | Constraints duplicated without an invariant ownership table | Maintain schema/semantic/cross-record matrix and paired tests | Schema steward |
| M-08 | Legacy support consumes disproportionate complexity | Medium / Medium | Large weekly validator/renderer plus fixtures alongside canonical pipeline | Collect usage evidence; isolate compatibility package; publish retirement/migration decision per policy | Compatibility steward |

### Low

| ID | Risk | Likelihood / impact | Evidence | Mitigation and verification | Owner |
|---|---|---|---|---|---|
| L-01 | Documentation navigation becomes harder as governance grows | Medium / Low | Large document set and overlapping entry points | Maintain authority/index metadata and quarterly link/task audit | Documentation steward |
| L-02 | CI workflow duplication causes small inconsistencies | Medium / Low | Repeated install/build sequences across five workflows | Use reviewed reusable workflow/action after release behavior is stable | CI maintainer |
| L-03 | Internal renderer/generator dictionaries are mistaken for stable plugins | Low / Medium | Importable registries but policy labels experimental | Keep warnings prominent; add internal naming/docs until conformance contract exists | Plugin steward |
| L-04 | Performance guardrails produce false confidence | Medium / Low | Very small, fast reference corpus with generous limits | Label as regression smoke baseline and publish workload classes | Performance steward |

## 9. Benchmark against mature open-source projects

The comparison is conceptual and uses practices commonly seen in mature Python
libraries, compilers, documentation systems, and data-processing projects.

| Dimension | TEOS position | Mature-project norm | Practice worth adopting |
|---|---|---|---|
| Repository organization | Clear domain directories and ownership rules; some target-state placeholders | Executable packages and maintained assets clearly separated from proposals/examples | Add implementation-status metadata; consider `src/` layout only if import/build ambiguity appears |
| Architecture governance | Strong specifications, ADRs, RFC process, compatibility and authority rules | Explicit decision history and stable/experimental surface inventory | Add automated architecture/conformance matrix linking claims to tests |
| Public API | Small and intentionally exported | Minimal documented surface with deprecation tests | Preserve small surface; add stability annotations and typed protocols |
| Internal model | Nested dictionaries validated at runtime | Typed domain objects at internal boundaries with serialization adapters | Incrementally type stage boundaries without breaking JSON contracts |
| Testing philosophy | Strong integration/E2E/regression, deterministic snapshots | Layered pyramid/diamond plus property, fuzz, platform, security, and compatibility suites | Add invariant/property tests and adversarial inputs where they outperform example tests |
| Fixtures | Compact, governed reference corpus and separated legacy binaries | Multiple workload classes and versioned compatibility corpora | Add medium/large synthetic or redistributable corpora and prior-version repositories |
| Documentation | Excellent repository docs and runbooks | Versioned searchable site, doctested snippets, external usability feedback | Publish versioned docs and test critical commands/examples |
| CI | Good job separation and installed-package testing | Immutable actions, dependency review, OS matrix, reusable workflows, required-rule verification | Add supply-chain controls and a justified platform matrix |
| Releases | Deterministic artifacts, checksum, draft/human gate | Signed/attested artifacts, SBOM, reproducible build evidence, rollback/yank rehearsal | Add provenance and a release-candidate rehearsal report |
| Security | Clear policy and narrow local architecture | Threat model, dependency scanning, hardened untrusted-input boundary | Publish trust-boundary model before service/plugin use |
| Maintainership | One universal CODEOWNER | Multiple reviewers, documented succession, distributed release/security knowledge | Establish a second qualified steward and periodic recovery exercise |
| Observability | Deterministic manifest and controlled CLI errors | Stable diagnostic codes, structured reports, supportable telemetry boundaries | Adopt the roadmap's diagnostic/report contracts before service operation |

TEOS exceeds many alpha projects in governance, deterministic fixtures, and
end-to-end verification. It trails mature projects primarily in maintainer
depth, typed internal boundaries, platform/workload breadth, published
documentation infrastructure, and artifact supply-chain assurance.

## 10. Prioritized recommendations

Recommendations intentionally avoid new end-user functionality. They focus on
truthful scope, reliability, maintainability, and evidence.

### Immediate — before the next release artifact

1. **Restore Git integrity.** Do not tag or release from this checkout until a
   clean clone or documented repair passes `git fsck --full`, current revision
   and remote identity are verified, and the worktree is clean.
2. **Publish this review's disposition.** Assign an owner and target milestone
   to every High risk; explicitly accept, mitigate, transfer, or defer each.
3. **Label architecture state.** Mark each major subsystem Implemented,
   Partial, Compatibility, or Target in the governing overview and README.
4. **Rehearse the full declared release gate in a clean supported Python
   environment.** Capture tests with branch coverage, Ruff, schema/link checks,
   deterministic wheel/sdist build, `twine`, isolated installs, and reference
   build hashes.
5. **Verify GitHub protections.** Confirm required checks, review/conversation
   requirements, force-push restrictions, administrator coverage, and `v*`
   tag rules match `docs/branch-protection.md`.
6. **Close controlled-error gaps.** Characterize invalid UTF-8, unreadable and
   disappearing input files, and presentation-input mutation; ensure CLI/API
   failures remain actionable and leave no output.
7. **Clarify input trust.** State whether repositories, themes, locales, and
   templates are trusted author inputs; warn that generated HTML must not be
   served as trusted active content until token constraints are hardened.

### Near-term — before stable v1.2

1. Run external install/first-build pilots on the documented split package and
   repository model; publish observed failure classes and resolutions.
2. Add Windows and macOS smoke coverage or narrow the platform claim with a
   documented rationale.
3. Define a validation-ownership matrix and add focused tests for high-branch
   semantic rules, localization, containment, and publication.
4. Remove literal sample-directory coupling from template resolution while
   keeping existing repository behavior compatible.
5. Include every input file in final pre-publication mutation verification.
6. Pin/review release-sensitive workflow actions and dependencies; decide and
   document SBOM, provenance attestation, artifact signing, and package-index
   credential strategy.
7. Have an independent accessibility specialist inspect representative HTML,
   DOCX, and PDF artifacts; align support claims with the result.
8. Establish a second qualified release/security steward or formally document
   the residual single-maintainer risk and recovery escrow.
9. Publish the intended stable API/CLI/schema/manifest surface inventory and
   test at least one prior-repository compatibility or migration scenario.

### Long-term — v1.3 and sustained maintenance

1. Decompose the application service into internal repository, compiler,
   scheduler, renderer, generator, and publisher boundaries with
   characterization tests and no public behavior change.
2. Introduce typed immutable internal domain records or protocols at those
   boundaries, retaining JSON adapters at repository edges.
3. Replace text-replacement localization with structured render models and
   explicit locale keys.
4. Separate canonical and compatibility implementations into unmistakable
   namespaces; use measured legacy adoption to drive a governed retirement
   decision.
5. Add machine-readable diagnostic codes, source locations, severities, and
   validation reports as already proposed by the strategic roadmap.
6. Formalize schemas for locale, theme, build manifest, schedule, rendered
   record, and compilation summary where they are intended compatibility
   surfaces.
7. Add representative workload classes and publish time, memory, temporary
   storage, and artifact-fan-out envelopes.
8. Publish versioned, searchable documentation and test critical command
   snippets in CI.
9. Reduce CI duplication through a reviewed reusable workflow only after the
   current release gates are stable and observable.

### Future major versions

1. Do not implement a hosted service, multi-tenant operation, executable
   plugins, or collaborative editing until an accepted threat model defines
   trust, authorization, isolation, retention, recovery, and audit boundaries.
2. Consolidate justified breaking changes into a migration-rehearsed v2
   package/repository contract rather than accumulating minor-version
   exceptions.
3. Make approval, stale-state propagation, semantic diff, and traceability
   executable domain contracts before a web interface can mutate curriculum.
4. Preserve normalized semantic equivalence between local and any future
   service build path.
5. Require content-addressed identities, idempotent jobs, bounded resources,
   transactional publication, recovery tests, and authorization-aware cache
   policy before distributed scale.
6. Keep declarative extensions preferable to executable in-process plugins;
   require descriptors, capability negotiation, conformance fixtures,
   isolation, revocation, and sustainable governance before any marketplace.
7. Maintain an offline/exportable core unless adopter evidence and an accepted
   governance decision explicitly change that product promise.

## 11. Overall engineering scorecard

| Dimension | Rating | Justification |
|---|---:|---|
| Architecture | **7.5/10** | Excellent governing principles and enforced canonical boundaries; several named subsystems remain target state and runtime contracts are dictionary-shaped |
| Maintainability | **7.0/10** | Readable, compact, deterministic code with good naming; large validators/orchestrator, duplication, and one-owner concentration increase change cost |
| Documentation | **8.5/10** | Broad, coherent, linked, and candid; implementation-state ambiguity and split-install onboarding remain |
| Testing | **8.5/10** | Strong E2E, regression, negative, artifact, and determinism evidence; limited platform, scale, adversarial, accessibility, and narrow unit evidence |
| Developer Experience | **7.5/10** | Clear guides and commands, small dependency set, good PR templates; external assets, many governing documents, and optional-tool bootstrap add friction |
| Release Readiness | **6.5/10** | Strong workflow design and deterministic packaging intent; alpha status, incomplete stable evidence, supply-chain gaps, and local Git corruption prevent unconditional release approval |
| Long-Term Sustainability | **6.5/10** | Thoughtful governance and roadmap; single maintainer/reviewer, legacy burden, target breadth, and missing implementation owners are material risks |

**Weighted overall assessment: 7.4/10 — Good engineering foundation, approved
for continued alpha evaluation with conditions.**

### Review-board conclusion

TEOS has earned confidence as a deterministic local curriculum validation,
scheduling, and artifact-generation alpha. Its engineering discipline is most
visible in architecture governance, traceable outputs, regression fixtures,
and documentation. The project should preserve those strengths while resisting
premature platform claims.

Approval for broad stable adoption should be conditional on:

1. verified Git and release provenance integrity;
2. explicit implemented-versus-target architecture labeling;
3. disposition of all High risks;
4. external install and representative workload evidence;
5. a justified platform/support matrix;
6. hardened input/error boundaries;
7. release supply-chain controls; and
8. reduced maintainer concentration or formally accepted continuity risk.

This assessment introduces no functionality and makes no claim that planned v2
capabilities are required for a successful v1.2 stable release. The stable
release bar is truthful scope, reliable supported behavior, reproducible
evidence, and sustainable ownership.
