# TEOS v2 Strategic Roadmap and Architecture Evolution

Status: Planning proposal  
Date: 2026-07-28  
Planning horizon: v1.2 beta through v2.0 and later

## Purpose and scope

This document evaluates TechnicalEducationOS after `v1.2.0-alpha1` and proposes
a multi-release direction. It is a planning artifact, not an accepted RFC,
delivery commitment, compatibility guarantee, or authorization to implement a
feature. Dates and staffing are intentionally omitted. Work enters a milestone
only through the governance, issue-intake, RFC, and release processes.

The roadmap preserves the repository constitution: governed knowledge informs
an approved curriculum model, and only that model supplies educational meaning
to generated artifacts. A web interface, API, plugin, optimization service, or
external integration must not bypass that authority chain.

The following labels distinguish the nature of proposed work:

- **Maintenance** preserves or hardens current supported behavior.
- **Evolution** adds backward-compatible foundations or improves an existing
  contract.
- **Capability** introduces a material new user or platform capability.
- **Breaking** requires a v2 contract change or removal.

## 1. Current platform assessment

### Assessment basis

The assessment covers the governing architecture and specifications, public
API and CLI, schemas, canonical Reference Curriculum, runtime modules, release
and maintenance policies, and the unit, integration, end-to-end, regression,
negative, artifact, and performance suites. It reflects repository evidence at
the date above, not production telemetry or adopter interviews that do not yet
exist.

### Strengths

| Area | Current strength | Strategic value |
|---|---|---|
| Authority model | Knowledge, curriculum, scheduling, presentation, and output ownership are explicitly separated. | New interfaces can reuse one governed compiler rather than invent competing sources of truth. |
| Determinism | Equivalent inputs produce stable build identities, manifests, and byte-reproducible artifacts. Failed builds do not replace successful output. | Enables caching, auditability, remote execution, and trustworthy comparisons. |
| Contracts | JSON Schemas, runtime validation, stable identifiers, schema versions, and compatibility policy establish explicit boundaries. | Provides a base for repository tooling and future service contracts. |
| Application surface | `BuildConfig`, `BuildResult`, `BuildError`, and `build()` form a deliberately small public Python API; CLI and API share the pipeline. | Limits compatibility burden while the alpha is validated. |
| Testing | The suite covers subsystem boundaries, a complete 96-artifact build, installed-wheel behavior, negative inputs, snapshots, deterministic output, and performance guards. | Makes incremental refactoring safer and provides candidate conformance fixtures. |
| Extensibility seams | Renderer, generator, theme, locale, institution, and calendar concepts already exist, with ecosystem governance and maturity language. | Supplies bounded starting points without prematurely promising a general plugin API. |
| Governance | RFCs, ADRs, contribution rules, security handling, support policy, release audit, documentation governance, and stewardship expectations are documented. | Supports long-lived architectural decisions and responsible ecosystem growth. |
| Operational simplicity | The runtime has one required dependency, local file inputs, no server, and no mandatory database or broker. | Keeps installation, recovery, and offline use straightforward. |

### Limitations

| Limitation | Evidence and consequence | Planning implication |
|---|---|---|
| Repository shape is narrow | The complete build expects one `curriculum/course.json`, one `sessions.json`, unit files, and fixed institution/locale/theme directories. | A registry or multi-course service first needs an explicit repository/package manifest and discovery contract. |
| The runtime is a synchronous local pipeline | Builds run in one process against a filesystem and return only after all artifacts are generated. | Web and cloud use need job semantics, cancellation, progress, quotas, and durable result metadata. |
| No persistence or collaboration model | There is no database, user identity, authorization, edit history, locking, comments, or approval workflow engine. | Collaborative authoring cannot be layered safely onto mutable JSON files without a separate domain design. |
| Extension loading is internal | Renderer and generator registries are in-process dictionaries; third-party Python integration is experimental. | Do not expose arbitrary package execution through a service or marketplace before isolation and conformance decisions. |
| Scheduling is intentionally basic | Sessions are assigned sequentially to available slots and must fit a single meeting duration. | Optimization, resource constraints, split sessions, cohorts, rooms, and instructor assignments require new model semantics. |
| Output inventory is limited | Only administrative, instructor, and lab documents are registered. DOCX/PDF presentation is deliberately minimal. | Output quality and missing core artifacts should be validated before broad interface expansion. |
| Traceability is stronger in specification than runtime | Manifests and curriculum references exist, but the full versioned trace graph, stale propagation, approval lifecycle, and impact analysis are not implemented as services. | This is a prerequisite for safe authoring, synchronization, analytics, and automated regeneration. |
| Configuration is fragmented | `BuildConfig`, repository conventions, institution profiles, calendars, locale catalogs, themes, and templates jointly configure a build without one declarative project file. | Define configuration precedence, validation, secrets boundaries, and portable profiles before remote execution. |
| Localization is presentation-only | Interface labels are localized while authoritative instructional prose remains in its source language. | Full curriculum translation needs reviewed parallel curriculum records and approval, not automatic text substitution. |
| No service security model | The local tool has no tenant, identity, access, network, or sensitive-data boundary because it does not need one yet. | A REST service or cloud deployment requires a threat model and data classification before implementation. |

### Scalability concerns

Current reference performance is excellent because the dataset is small and
local. The relevant future risks are workload shape and state management, not
the present millisecond baseline.

1. The application loads curriculum and configuration into memory and scans
   directories for selection. Large registries need indexed discovery and
   bounded loading.
2. A complete build renders the Cartesian product of sessions, renderers, and
   generators synchronously. Artifact counts grow linearly with each dimension
   and can create CPU, memory, temporary-storage, and file-count pressure.
3. Builds have no concurrency policy. Simultaneous writes, duplicate work,
   tenant quotas, cancellation, and resource exhaustion are undefined.
4. The output directory must not already exist. This is safe locally but is not
   a versioned artifact-retention or concurrent-publication strategy.
5. The scheduler uses a greedy sequence and materializes all available slots.
   Constraint optimization can become combinatorial and must be bounded,
   explainable, and independently budgeted.
6. Content-addressed build identity exists, but no cache uses it. Remote
   execution without deduplication would regenerate identical outputs.
7. Filesystem paths are part of operational configuration. Distributed workers
   will require immutable packages or object references instead of shared-path
   assumptions.

### Maintainability observations

- The modular-monolith deployment is appropriate for the current scale and
  should remain the default through v1.3. Service decomposition now would add
  operations and distributed-failure cost before domain boundaries are proven.
- `records.py`, `application.py`, and `cli.py` hold broad responsibilities.
  The application also owns discovery, validation, localization, theme checks,
  compilation summary, generation, and publication. Internal boundary
  extraction can improve ownership without changing deployment.
- JSON Schema validation and detailed Python validation are both valuable, but
  their responsibilities and error aggregation are not formally divided.
  Drift could make one layer accept what the other rejects.
- Compatibility code is intentionally retained and well tested, but its
  removal release and migration evidence need to be decided before v2.
- Locale substitution currently depends on renderer text and prefix matching.
  Typed message identifiers would be less fragile while preserving curriculum
  prose.
- Institution-specific legacy presentation code is substantial. Its long-term
  place should be an adapter with an explicit support owner, not an accidental
  parallel rendering architecture.
- Current documentation accurately distinguishes implemented output from
  specification, an important discipline to preserve as the roadmap grows.

### Extensibility opportunities

The safest early extension points are declarative: schemas, institution
profiles, calendars, locales, themes, templates, and versioned curriculum
packages. Executable renderers and generators can follow once public contracts,
capability negotiation, conformance tests, lifecycle hooks, failure budgets,
and isolation are established.

The deterministic build ID and source hashes are natural keys for an artifact
cache. Rendered records are also a useful boundary between semantic rendering
and physical generation. The public application service can become the single
in-process façade behind future CLI, REST, and job-worker adapters.

## 2. Technical debt review

### Priority model

- **TD0 — release blocker:** could invalidate data, compatibility, security, or
  the stable-release promise.
- **TD1 — high:** materially limits safe evolution or frequently raises change
  cost.
- **TD2 — medium:** should be addressed when its subsystem changes.
- **TD3 — accepted:** low-cost or deliberate debt that may remain until
  evidence changes.

### Debt inventory

| ID | Priority | Type | Finding | Recommended disposition |
|---|---|---|---|---|
| TD-01 | TD0 | Contract | Beta has not yet produced an explicit freeze inventory for CLI, API, schemas, manifests, repositories, and extensions. | Record each intended stable surface and its compatibility tests before v1.2 stable. |
| TD-02 | TD0 | Migration | Legacy week-based paths are deprecated, but the earliest removal release and tested migration/reproduction strategy are not finalized. | Decide through RFC; publish support and rehearsal evidence before v2 preview. |
| TD-03 | TD1 | Architecture | Full trace graph, approval lifecycle, stale propagation, and impact analysis are governing concepts but not complete runtime capabilities. | Define the minimum persisted trace/approval domain before collaborative or synchronization features. |
| TD-04 | TD1 | Refactoring | Build orchestration combines discovery, validation, compilation, rendering, generation, and publication. | Extract internal ports/services behind unchanged public behavior; retain a modular monolith. |
| TD-05 | TD1 | Contract | Schema validation and Python semantic validation lack a documented ownership matrix and unified diagnostic format. | Assign invariants to layers, add diagnostic codes/paths, and test parity. |
| TD-06 | TD1 | Configuration | There is no versioned repository/project manifest or documented precedence across API, CLI, repository, institution, and presentation settings. | Design a portable declarative manifest and migration path for v1.3; avoid implicit environment configuration. |
| TD-07 | TD1 | Security | No service threat model, tenant isolation model, data classification, retention policy, or plugin execution policy exists. | Required planning gate before network, cloud, marketplace, or collaborative pilots. |
| TD-08 | TD1 | Testing | Records and scheduling have lower branch coverage than other core modules, especially defensive date/shape paths. | Add risk-based table/property tests; do not chase coverage with implementation-coupled mocks. |
| TD-09 | TD1 | Quality | Minimal DOCX/PDF output lacks production layout, accessibility tagging, and representative viewer validation. | Treat accessibility and core artifact usability as product quality, with manual and automated acceptance evidence. |
| TD-10 | TD2 | Refactoring | Localization is coupled to rendered English headings and prefixes. | Introduce typed presentation/message records before adding more renderers or locales. |
| TD-11 | TD2 | Refactoring | Registry entries are callable implementation objects without a public descriptor/capability contract. | Separate discovery metadata from execution and create a conformance fixture set. |
| TD-12 | TD2 | Testing | Performance guards use generous absolute thresholds and one small reference corpus. | Add opt-in small/medium/large workload fixtures and trend reporting before server capacity claims. |
| TD-13 | TD2 | Documentation | No operator runbook covers a future database, queue, object store, backup/restore, or disaster recovery. | Write these only when an accepted deployment RFC chooses those components. |
| TD-14 | TD2 | Documentation | Accessibility, curriculum translation governance, privacy, analytics interpretation, and synchronization conflicts need dedicated contracts. | Add focused RFCs/specifications before related capability implementation. |
| TD-15 | TD3 | Accepted | The application is synchronous and filesystem-based. | Retain for local/offline v1.x; add an adapter rather than weakening the simple path. |
| TD-16 | TD3 | Accepted | There is one required runtime dependency and no general dependency-injection framework. | Preserve until concrete substitution/testing needs justify additional machinery. |
| TD-17 | TD3 | Accepted | Performance tests are manual rather than required for every pull request. | Keep manual to avoid noisy gates; run on releases and architecture changes. |
| TD-18 | TD3 | Accepted | Some defensive OS race and permission branches are difficult to cover portably. | Accept with integration tests around observable atomic-publication behavior. |

TD0 and TD1 items should be visible in milestone planning. TD2 items should not
trigger broad rewrites by themselves. TD3 items are deliberate constraints,
not defects.

### Documentation gaps

The current user, developer, release, governance, and architecture
documentation is comprehensive for a local compiler. Future work needs
documentation only as its scope becomes accepted:

- repository/package manifest and schema migration handbook;
- stable extension author guide and conformance protocol;
- service API semantics, error model, pagination, idempotency, and versioning;
- identity, roles, institutional tenancy, approval delegation, and audit log;
- data classification, privacy, retention, deletion, export, and telemetry;
- asynchronous job lifecycle, cancellation, retry, and recovery;
- synchronization ownership and conflict-resolution rules;
- analytics definitions, limitations, and protection against misleading
  educational conclusions; and
- production deployment, observability, backup, restore, and incident
  runbooks.

### Testing improvements

Before v1.2 stable, emphasize compatibility matrices, migrations, supported
platform installation, artifact accessibility review, and real institutional
pilots. For v1.3, add repository-package conformance, schema migration,
diagnostic-code, extension-fixture, and larger-corpus tests. Before v2, add
contract tests for REST and jobs, authorization and tenant isolation, failure
injection, concurrent build publication, cache correctness, backup/restore,
upgrade/rollback, load/soak, and plugin sandbox escape boundaries as applicable.

## 3. Future capability inventory

Priority reflects user value and architectural leverage, not a delivery
promise.

| Capability | Value | Dependencies and constraints | Earliest sensible horizon | Priority |
|---|---|---|---|---|
| Curriculum repository manifest and local registry | Discover, validate, pin, and build multiple versioned curriculum packages. | Package identity, semantic/content versioning, dependency/provenance metadata, signing decision, migration tooling. | v1.3 foundation | Highest |
| Read-only REST API | Makes validation, build submission, status, manifests, and artifact retrieval available to other systems. | Stable application façade, job model, API versioning, auth/threat model, idempotency, quotas. | v2 preview | Highest |
| Web review interface | Lowers barriers for repository selection, validation, build review, schedule inspection, and artifact retrieval. | REST/job foundation, accessible design system, identity/roles, no direct model bypass. | v2 | High |
| Traceability and impact workspace | Shows source-to-model-to-artifact links, gaps, staleness, and proposed semantic changes. | Persisted trace graph, versioned approvals, diff semantics. | v1.3 foundation; v2 UX | Highest |
| Improved artifact portfolio | Adds course outlines, student guides, assessments, resource lists, and accessible production layouts. | Approved renderer contracts, answer-key protection, accessibility and content validation. | v1.3 incrementally | High |
| Scheduling optimization | Handles constraints such as rooms, equipment, cohorts, instructors, split durations, and preferences with explanations. | New scheduling domain schema, solver evaluation, deterministic tie-breaking, infeasibility diagnostics, human approval. | v2 or later | Medium-high |
| Collaborative authoring | Enables drafts, comments, proposals, review, approval, history, and conflict handling. | Identity/roles, immutable versions, transactions, trace/stale propagation, audit log, export and offline strategy. | After v2 foundation | High, high cost |
| Institutional synchronization | Exchanges calendars, rosters/configuration, LMS records, and approved curriculum with institutional systems. | Adapter contracts, field authority matrix, privacy, credentials, idempotency, reconciliation, vendor sandboxes. | v2 pilots or later | Medium-high |
| Analytics | Measures builds, curriculum coverage, gaps, review state, schedule utilization, and artifact use. | Canonical event/metric definitions, privacy, consent, retention, bias review; avoid learner-outcome claims without valid evidence. | v2 operational analytics; later educational analytics | Medium |
| Cloud deployment reference | Offers a repeatable supported deployment for the service and workers. | Container/runtime decision, state stores, secrets, observability, backups, scaling, cost model, SLOs. | v2 | High only when service demand is validated |
| Plugin catalog | Publishes signed/verified metadata, compatibility, health, provenance, and installation guidance. | Stable extension contracts, namespace policy, conformance automation, moderation, revocation, incident response. | v2 or later | Medium |
| Executable plugin marketplace | Adds discovery and installation of third-party code. | Everything in catalog plus strong isolation, supply-chain controls, permissions, review capacity, safe updates/rollback. | Later; separate go/no-go RFC | Low until ecosystem demand exists |
| Visual curriculum designer | Provides schema-aware editing, sequencing, trace mapping, validation, preview, and accessible review. | Collaborative/version domain, form contracts, semantic diffs, undo, approvals, large-model UX research. | After core web review workflows | Medium-high, very high cost |
| CLI/offline synchronization | Preserves local authoring and deterministic builds while exchanging immutable versions with a service. | Package manifest, remote protocol, conflict policy, authentication, resumable transfer. | v2 | High if cloud is adopted |

### Capability sequencing

```text
repository manifest + diagnostic contracts + trace foundations
                              │
                    stable application façade
                              │
             versioned REST API + asynchronous jobs
                    ┌─────────┴─────────┐
                    │                   │
             web review UI       cloud deployment
                    │                   │
          collaborative domain   institutional adapters
                    └─────────┬─────────┘
                              │
              visual authoring and governed analytics

extension descriptors + conformance + isolation
                              │
                       plugin catalog
                              │
              optional executable marketplace
```

A marketplace and visual designer are not prerequisites for v2.0. A narrow,
reliable review/build platform has more architectural value than a broad
interface that embeds unresolved ownership and security decisions.

## 4. Architecture evolution recommendations

### Recommended target shape

Evolve as a **modular monolith with ports and adapters** through v1.3. Preserve
the local library and CLI. In v2, add a service façade and independently
scalable build workers only where workload evidence requires them.

```text
CLI / Python API          Web UI / external clients
       │                           │
       └──── application ports ────┘
                    │
      repository │ validation │ compilation │ trace
      scheduling │ rendering  │ generation  │ publication
                    │
       filesystem adapters / service adapters
                    │
        package store │ metadata store │ job queue
```

Domain code must not import HTTP, queue, database, cloud-vendor, or UI
frameworks. Adapters translate those concerns into versioned application
commands and results. The local path remains supported unless an RFC explicitly
changes that promise.

### Service decomposition

Do not begin with microservices. Establish internal modules and measure
contention first. The first justified process boundary is likely an
unprivileged build worker because document generation is resource-consuming
and may eventually execute reviewed extensions. Metadata/approval and artifact
storage have different durability and security needs, but can initially remain
behind one service.

Extract a separate service only when at least one condition is demonstrated:

- it needs independent scaling or resource limits;
- it has a materially different trust boundary;
- it requires an independent availability or deployment lifecycle;
- it is owned by a stable separate team; or
- operational evidence shows the modular monolith cannot meet an agreed SLO.

Never split along nouns alone. Distributed calls must not replace in-process
calls without idempotency, versioned messages, trace correlation, timeouts,
retry policy, and failure recovery.

### Caching

Use content-addressed, immutable caching keyed by compiler version, schema
versions, normalized input hashes, extension versions, and relevant
configuration. Cache only derived results: validated package summaries,
compiled models, schedules, rendered records, and generated artifacts.

Do not cache approval decisions, mutable drafts, credentials, or unresolved
external lookups. A cache hit must reproduce the same manifest and must be
subject to authorization. Add size bounds, retention, integrity verification,
stampede prevention, and metrics. Start with build-level deduplication; add
stage-level caching only after profiling shows value.

### Asynchronous processing

Keep local builds synchronous. A service should represent remote builds as
durable jobs with states such as `accepted`, `validating`, `compiling`,
`rendering`, `publishing`, `succeeded`, `failed`, and `cancelled`. Define:

- idempotency and duplicate submission behavior;
- immutable input snapshot and requested capability versions;
- progress that does not become a compatibility trap;
- cancellation checkpoints and cleanup;
- bounded retry rules for transient infrastructure failures only;
- terminal diagnostic and partial-output policy;
- retention, authorization, and audit semantics; and
- recovery after worker or control-plane restart.

Curriculum or validation errors are deterministic user outcomes, not retryable
infrastructure failures.

### Configuration improvements

Introduce a versioned project/repository manifest that declares package
identity, curriculum roots, compatible schema/compiler ranges, institutions,
locales, themes, templates, extensions, and default build profiles. Establish
precedence explicitly:

```text
schema defaults < repository profile < institution profile
                < named build profile < explicit CLI/API request
```

The exact order requires RFC review; no layer may override curriculum meaning
through presentation configuration. Secrets must be references supplied by the
runtime, never manifest values. Provide an effective-configuration inspection
command/result and redact sensitive adapter settings.

### Plugin isolation

Prefer declarative data extensions. Treat executable plugins as untrusted until
proven otherwise. A public extension descriptor should identify capability,
contract version, permissions, resources, deterministic behavior, provenance,
and compatibility. Conformance tests are necessary but not a sandbox.

For a network service, do not import arbitrary third-party code into the API
process. Run executable extensions in a restricted worker process or stronger
isolation appropriate to the threat model, with no ambient credentials,
read-only immutable inputs, a dedicated output directory, resource/time limits,
network disabled by default, structured diagnostics, and verified output
manifests. Define revocation and emergency-disable behavior before any official
catalog.

### Repository versioning

Separate and record:

1. repository/package format version;
2. schema version for each record type;
3. curriculum content revision/version;
4. extension contract and implementation versions;
5. TEOS compiler version; and
6. generated manifest/artifact format version.

Use immutable releases plus content hashes. A package lock records exact
dependencies and provenance. Migrations write to a new destination, preserve
the source, support inspection/dry run, emit a machine-readable report, and are
tested both forward and, when promised, for rollback. Do not assume SemVer alone
can describe changes to regulated or institution-approved curriculum content.

### Data and persistence

Do not choose a database before the collaborative domain is defined. Immutable
curriculum packages and artifacts can begin in content-addressed object
storage; searchable metadata, job state, roles, approvals, and audit events
need transactional persistence. The authoritative boundary between repository
files and service records must be explicit. Every mutation should create a new
version or auditable proposal rather than silently rewriting an approved
record.

### Observability and reliability

Adopt structured diagnostic codes and correlation IDs before a REST API.
Measure stage duration, queue time, cache behavior, failure class, artifact
volume, and dependency health without collecting curriculum or personal data
by default. Logs must not contain credentials, proprietary source content,
student data, or protected answer keys. Define service SLOs only after pilot
traffic establishes useful baselines.

## 5. Multi-release roadmap

The sequence below distinguishes stabilization from capability work. Minor
release additions remain backward compatible. Any proposed item can be
deferred if evidence, stewardship, security, or quality gates are missing.

### v1.2 beta — operational validation and contract candidate

**Release character: Maintenance. No major new platform capability.**

Objectives:

- run external installation and complete-build pilots on supported Python and
  operating-system combinations;
- exercise multiple real, rights-cleared institutional profiles and curriculum
  repositories without expanding the public contract casually;
- resolve P0/P1 alpha defects and improve actionable diagnostics;
- inventory the exact API, CLI, schema, repository, manifest, artifact, and
  extension surfaces proposed for stability;
- complete accessibility and representative office/PDF viewer review for
  supported artifacts, documenting remaining limits;
- rehearse alpha-to-beta repository and configuration changes;
- publish known limitations and collect structured adopter feedback; and
- keep new REST, web, collaboration, marketplace, optimization, and cloud work
  out of the release branch.

Exit evidence:

- no known high-severity defect or unresolved data-integrity concern;
- successful clean installs and canonical builds across the Tier 1 matrix;
- at least two external pilot contexts or an explicit governance-approved
  explanation of insufficient evidence;
- compatibility-candidate inventory with tests and owners;
- release-candidate audit, migration notes, and documented manual artifact
  review; and
- stable test runs with no unresolved flaky required check.

### v1.2 stable — compatibility baseline

**Release character: Maintenance and release hardening. No major new platform
capability.**

Objectives:

- remediate beta findings and complete security, license, provenance,
  packaging, and dependency review;
- freeze and document the supported public surfaces;
- verify deterministic release artifacts and installed-wheel behavior;
- publish final installation, compatibility, support, and upgrade matrices;
- assign maturity to each extension surface and keep unsupported internals
  explicitly experimental; and
- establish patch-release ownership and operational response expectations.

Exit evidence:

- all supported workflows pass on every Tier 1 combination;
- zero known release blockers and a disposition for every material audit
  finding;
- tested beta-to-stable upgrade/migration guidance;
- signed-off compatibility tests and release audit; and
- published support start/end policy for the v1.2 line.

### v1.3 — backward-compatible foundations and usability

**Release character: Maintenance plus bounded Evolution. Selected
backward-compatible capabilities may ship only behind mature contracts.**

Candidate objectives, ordered:

1. introduce stable diagnostic codes and validation reports;
2. define and pilot a versioned repository/project manifest with safe migration
   tooling;
3. extract internal application boundaries without changing public behavior;
4. strengthen trace/coverage/impact outputs and approval metadata;
5. publish extension descriptors and a conformance harness while executable
   loading remains experimental;
6. improve core accessible artifact quality and add only evidence-backed
   renderer types;
7. add larger-corpus performance characterization and cache-key design, but no
   mandatory distributed cache; and
8. publish the accepted v2 umbrella RFC, threat model, migration plan, and
   preview criteria.

v1.3 should not introduce a public production REST service, multi-user editing,
an executable marketplace, or breaking schema cleanup. Experimental discovery
or read-only prototypes may inform RFCs but are not stable product promises.

Exit evidence:

- all additions are backward compatible with v1.2 or have an allowed
  opt-in/new-version path;
- repository migration is non-destructive and tested on representative data;
- new diagnostics and trace records have machine-readable schemas;
- extension conformance cannot imply security certification; and
- v2 proposed breaks and compatible alternatives are publicly inventoried.

### v2.0 — governed platform service foundation

**Release character: Breaking where justified, plus major Capability.**

Recommended objective: turn the trusted local compiler into a platform that can
run locally or behind a secure, versioned job service while consolidating
necessary contract migrations once.

Candidate in-scope outcomes:

- versioned curriculum/repository packages with locks, provenance, migration,
  and registry discovery;
- durable trace, approval, stale-state, and semantic-diff foundations;
- a versioned read-only/build-oriented REST API and asynchronous job contract;
- accessible web workflows for repository validation, build submission,
  schedule/artifact review, diagnostics, and trace inspection;
- isolated build workers, content-addressed artifact storage/cache, and a
  supported deployment reference if pilot demand justifies operations;
- explicit identity, institutional tenancy, roles, audit, retention, export,
  and recovery contracts;
- an offline/local path with clear synchronization boundaries;
- versioned extension descriptors, capability negotiation, conformance
  fixtures, and safe execution policy; and
- removal or migration of legacy contracts approved by the umbrella RFC.

Potentially out of scope for v2.0 stable:

- unrestricted collaborative curriculum editing;
- full visual curriculum design;
- an official executable plugin marketplace;
- general-purpose constraint optimization;
- broad vendor synchronization;
- learner-level or outcome analytics; and
- automatic translation of authoritative curriculum.

Those capabilities can build on v2 foundations, but including all of them would
make compatibility, security, and validation unreviewable in one release.

v2 exit evidence:

- at least one preview and one release-candidate cycle;
- completed migration rehearsal using preserved v1.2/v1.3 repositories;
- local and service builds agree on normalized semantic outputs;
- authorization, tenant isolation, job recovery, cache integrity,
  backup/restore, load, and upgrade/rollback tests pass;
- threat model and privacy review have no unresolved release blocker;
- operators can deploy, observe, back up, restore, and upgrade solely from
  maintained documentation; and
- the prior stable line remains supported according to published policy.

## 6. Risk assessment

| ID | Category | Risk | Likelihood / impact | Mitigation and trigger |
|---|---|---|---|---|
| R-01 | Scaling | Artifact fan-out exhausts worker memory, CPU, temporary storage, or file limits. | Medium / High | Per-job quotas, streaming/bounded stages, resource limits, workload benchmarks; trigger at representative large-corpus pilot. |
| R-02 | Scaling | Optimization workloads become unbounded or nondeterministic. | Medium / High | Explicit constraint scope, time budgets, deterministic tie-breaks, feasible/infeasible explanations, human approval. |
| R-03 | Scaling | Duplicate remote builds waste capacity. | High / Medium | Content-addressed idempotency and build-level cache with authorization-aware retrieval. |
| R-04 | Compatibility | Stable API/schema/repository promises freeze accidental alpha shapes. | Medium / High | Beta surface inventory, adopter evidence, explicit maturity, defer uncertain contracts. |
| R-05 | Compatibility | v2 migration changes approved curriculum meaning or stable IDs. | Low / Critical | Semantic diff, preserved source, migration reports, authorized review, rehearsal and rollback. |
| R-06 | Compatibility | Plugin and core versions drift across independent releases. | High / High | Capability negotiation, tested ranges, lock files, pre-release ecosystem testing, revocation policy. |
| R-07 | Maintenance | Too many platform surfaces exceed maintainer capacity. | High / High | Narrow v2 scope, named steward per capability, support-cost review, archive/retire unsupported experiments. |
| R-08 | Maintenance | Specification and runtime claims diverge. | Medium / High | Implemented/planned status labels, conformance tests, release documentation audit. |
| R-09 | Maintenance | Legacy paths consume disproportionate test and support effort. | Medium / Medium | Usage evidence, explicit retirement RFC, migration tooling, time-bounded support. |
| R-10 | Dependency | New web, database, queue, solver, and document dependencies expand vulnerabilities and upgrade burden. | High / High | Architecture decision per dependency class, minimum set, lock/review, SBOM/provenance, replacement/exit plan. |
| R-11 | Dependency | A solver or document library is abandoned or changes license. | Medium / High | Health/license review, adapter boundary, reproducible fixtures, evaluated fallback. |
| R-12 | Security | Executable plugins access tenant data, credentials, or the network. | Medium / Critical | No in-process untrusted plugins, least-privilege isolation, permissions, egress default-deny, security tests and revocation. |
| R-13 | Security/privacy | Institutional synchronization or analytics ingests student or protected data outside TEOS's present scope. | Medium / Critical | Data minimization, classification, privacy review, separate stores/roles, consent and retention; reject fields without authority. |
| R-14 | Community | A marketplace implies endorsement or overwhelms moderation. | Medium / High | Begin with metadata catalog, clear non-endorsement, objective listing/removal policy, sustainable moderation staffing. |
| R-15 | Community | Roadmap breadth creates expectations the maintainer base cannot meet. | High / Medium | Horizons, no-date commitments, quarterly revalidation, owner required for acceptance. |
| R-16 | Community | Institutional or language overlays are accepted without authorized reviewers. | Medium / High | Authority verification, review records, provenance and appeal path. |
| R-17 | Product | Web convenience bypasses approval and curriculum authority. | Medium / Critical | Application commands enforce lifecycle invariants; UI is never an authority layer. |
| R-18 | Reliability | Queue/database/object-store partial failure publishes incomplete or mismatched artifacts. | Medium / High | Immutable staging, transactional metadata, checksum verification, idempotent publication, recovery tests. |
| R-19 | Analytics | Operational data is misrepresented as evidence of teaching or learner effectiveness. | Medium / High | Metric definitions and disclaimers, governance review, no causal claims without validated research design. |

Critical-impact risks are design gates even when likelihood is low. Accepted
RFCs should link their risks to owners, verification, and release criteria.

## 7. Success metrics

Metrics are release gates and trend signals, not incentives to hide difficult
work. Baselines should be recorded during v1.2 beta and targets reviewed at
each release.

| Dimension | Indicator | Proposed target | Measurement |
|---|---|---|---|
| Build reliability | Canonical deterministic build success | 100% in required CI; at least 99% for valid pilot submissions, excluding user validation failures | CI and privacy-preserving classified pilot telemetry/support log |
| Build reliability | Reproducibility | 100% normalized semantic equivalence for repeated supported builds; byte identity where the contract promises it | Determinism suite |
| Installation success | Clean Tier 1 install and first build | 100% in automated matrix; at least 90% of documented external pilot attempts without maintainer intervention | Release validation and structured pilot checklist |
| Installation success | Time to first successful reference build | Median under 15 minutes for a new contributor following only maintained docs | Quarterly usability sample |
| Documentation quality | Tested commands/links | 100% required documentation commands represented by smoke tests where practical; zero broken internal links | CI link and doc-command checks |
| Documentation quality | Task completion | At least 90% of sampled users complete install/build/diagnose tasks without undocumented steps | Beta documentation study |
| Contributor onboarding | First-time PR readiness | Median under 60 minutes from checkout to required local checks on a supported environment | Opt-in contributor survey/issue template |
| Contributor onboarding | Review latency | Median first human response within 5 business days when maintainer capacity permits | Repository reports, with pauses disclosed |
| Regression stability | Required-check flake rate | Below 0.5% over a rolling 30-day window; zero accepted quarantined release blockers | CI rerun classification |
| Regression stability | Escaped high-severity regressions | Zero known at stable release; target zero per supported minor line | Issue/release audit |
| Compatibility | Migration success | 100% of maintained representative prior-version repositories migrate or receive the documented actionable rejection | Migration fixture suite |
| Accessibility | Supported artifact/interface review | 100% of supported artifact types and web release-critical flows pass the declared automated and manual checklist | Release audit |
| Release cadence | Maintenance predictability | Security and critical fixes follow published response policy; roadmap reviewed quarterly; no release solely to meet a date | Maintenance log and release audit |
| Release cadence | Stable readiness | 100% of release checklist evidence present before tag; no retroactive required evidence | Release audit |
| Service readiness | Job completion and recovery | Target defined after pilot baseline; zero lost terminal results in recovery tests | Load, failure-injection, and pilot metrics |
| Ecosystem health | Extension compatibility | 100% of listed extensions publish tested version ranges; conformance status is current for each supported core release | Catalog automation |

Do not collect personal or curriculum content merely to calculate a metric.
Publish denominators and exclusions so a small sample is not presented as broad
adoption evidence.

## 8. Prioritized backlog

Items are ordered within priority. “Target” is a planning recommendation.

| Rank | ID | Class | Backlog item | Target | Dependency / acceptance evidence |
|---:|---|---|---|---|---|
| 1 | B-01 | Maintenance | Complete external install/build pilots and classify failures. | v1.2 beta | Tier 1 matrix and pilot reports |
| 2 | B-02 | Maintenance | Inventory and test every intended stable compatibility surface. | v1.2 beta | Public-surface register with owner |
| 3 | B-03 | Maintenance | Resolve release-blocking defects, flaky checks, accessibility blockers, and audit findings. | v1.2 beta/stable | Zero open blockers |
| 4 | B-04 | Maintenance | Publish alpha/beta migration, limitations, and final support matrix. | v1.2 stable | Rehearsed clean upgrade |
| 5 | B-05 | Evolution | Define stable diagnostic codes, locations, severity, and machine-readable reports. | v1.3 | Schema and CLI/API parity tests |
| 6 | B-06 | Evolution | RFC a versioned repository/project manifest and configuration precedence. | v1.3 | Non-destructive migration prototype and accepted ADR |
| 7 | B-07 | Evolution | Document schema-versus-semantic validation ownership and close high-risk test gaps. | v1.3 | Invariant matrix and negative tests |
| 8 | B-08 | Evolution | Extract repository, compiler, renderer, generator, and publisher application ports. | v1.3 | No public behavior or snapshot change |
| 9 | B-09 | Evolution | Implement the minimum trace, approval metadata, stale-state, and semantic-diff contracts selected by RFC. | v1.3/v2 | Governed lifecycle fixtures |
| 10 | B-10 | Maintenance | Improve accessible DOCX/PDF presentation and evidence-backed core artifact coverage. | v1.3 | Manual/automated artifact acceptance |
| 11 | B-11 | Evolution | Define extension descriptors, capability negotiation, and conformance fixtures. | v1.3 | No claim of executable-plugin safety |
| 12 | B-12 | Planning | Accept a v2 umbrella RFC covering breaks, migration, support, threat model, and staffing. | Before v2 implementation | Public review and named owners |
| 13 | B-13 | Capability | Add immutable package registry discovery and lock/provenance records. | v2 | Manifest and migration mature |
| 14 | B-14 | Capability | Define durable build jobs, idempotency, cancellation, retry, retention, and recovery. | v2 preview | State-machine and failure tests |
| 15 | B-15 | Capability | Publish a versioned build/validation REST API. | v2 preview | Auth, quotas, errors, contract suite |
| 16 | B-16 | Capability | Provide accessible web review/build/trace workflows. | v2 | User research and API stability |
| 17 | B-17 | Capability | Add isolated workers and content-addressed artifact storage/cache. | v2 | Threat model, integrity and load tests |
| 18 | B-18 | Capability | Publish a supported cloud deployment reference only if pilots justify it. | v2 | SLO, cost, backup/restore, runbooks |
| 19 | B-19 | Breaking | Migrate or remove approved legacy contracts as one reviewed v2 change set. | v2 | Usage evidence and migration rehearsal |
| 20 | B-20 | Planning | Model collaborative drafts, proposals, reviews, approvals, conflicts, and offline export. | Post-v2 candidate | Domain RFC before UI |
| 21 | B-21 | Planning | Model scheduling resources and constraints; evaluate solvers and explainability. | v2/later candidate | Representative institutional cases |
| 22 | B-22 | Planning | Define institutional adapter authority, privacy, reconciliation, and credential contracts. | v2/later candidate | Vendor sandbox and data review |
| 23 | B-23 | Capability | Launch a metadata-only extension catalog with moderation and revocation. | Later | Stable contracts and sustained reviewers |
| 24 | B-24 | Planning | Research visual curriculum design on top of version/review semantics. | Later | Accessible workflow evidence |
| 25 | B-25 | Planning | Define privacy-preserving analytics and prohibit unsupported outcome claims. | Later | Metric governance and data inventory |
| 26 | B-26 | Capability | Consider executable marketplace only after a separate security and sustainability go/no-go review. | Later | Isolation validation and moderation capacity |

Backlog items B-01 through B-04 are the only recommended v1.2 work. B-05
through B-12 establish a safe bridge to v2. B-20 and later should not compete
with the service foundation unless adopter evidence changes priorities.

## 9. Remaining architectural questions

These questions require evidence and, where indicated, RFC decisions:

1. What is the smallest stable v1.2 contract surface, and which alpha
   registries must remain explicitly experimental?
2. Is a TEOS repository one curriculum package, a workspace containing many
   packages, or both? How are package IDs globally namespaced?
3. Which versions represent educational approval, content revision, package
   release, schema format, and compiler compatibility?
4. Where is the authoritative approved record when a local repository and a
   hosted service both exist?
5. What semantic diff is sufficient for an authorized reviewer to confirm that
   migration or regeneration did not change curriculum meaning?
6. Which approval roles are universal, and which are delegated by an
   institution? Can approval be revoked, and what becomes stale?
7. Must TEOS remain fully offline-capable for all core workflows? If so, which
   hosted features must have export/import equivalents?
8. Does the first REST API expose only immutable build commands and results, or
   also mutable authoring resources?
9. What are the tenant, institution, course, and package isolation boundaries?
   Can one user act for multiple institutions?
10. What data is explicitly prohibited from TEOS? Are student rosters,
    submissions, grades, protected answer keys, and proprietary sources in
    separate security domains?
11. Which job stages are safe to retry, and what publication transaction makes
    metadata and artifacts visible atomically?
12. Is object storage plus relational metadata the preferred persistence
    model, and how are backups proven restorable?
13. What workload sizes and SLOs justify asynchronous workers, caching, or
    service separation?
14. Should a cache be shared across tenants when hashes match, or does
    authorization/provenance require tenant-scoped storage?
15. Are executable third-party plugins a product requirement? Would declarative
    extensions or separately operated integration services meet the need with
    less risk?
16. What isolation boundary is strong enough for document generators that
    process proprietary inputs?
17. Who can list, delist, revoke, or declare compatibility for an extension,
    and who handles ecosystem security incidents?
18. Which scheduling constraints are common enough to standardize, and which
    remain institution-specific? Must results be globally optimal or simply
    valid and explainable?
19. Which external system owns each synchronized field, and how are concurrent
    edits, deletions, and offline changes reconciled?
20. Which analytics are operational, curricular, institutional, or
    learner-level, and what evidence supports each interpretation?
21. What exact accessibility standards and representative viewers are part of
    the artifact and web support promise?
22. When may legacy weekly records and institution-specific adapters be
    removed, and which maintained repositories prove migration?
23. What prior stable line support window can the maintainer community
    realistically sustain during and after v2?
24. Which capabilities have named long-term stewards? Any capability without
    one should remain in research or backlog.

## Review and change control

Review this strategy at least quarterly and after each release. Update it when
adopter evidence, maintainer capacity, risks, or accepted RFCs materially
change. Accepted RFCs and ADRs override this planning proposal where they are
more specific. Deferral is the correct outcome when a capability lacks an
owner, evidence, migration, security boundary, or measurable exit criteria.
