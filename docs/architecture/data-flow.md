# Data Flow Specification

Status: Governing  
Version: 1.0

## Permitted pipeline

```text
external sources
    │
    ▼
1. register ──> knowledge source packages
    │
    ▼
2. extract/normalize ──> addressable knowledge records
    │
    ▼
3. design ──> draft course blueprint
    │              │ human review
    │              ▼
    │         approved blueprint
    ▼
4. compile ──> draft structured curriculum model
                   │ human review + validation
                   ▼
              approved curriculum model
                   │
          ┌────────┴────────┐
          ▼                 ▼
5. render artifacts   6. audit/trace reports
```

## Stage contracts

| Stage | Inputs | Outputs | Required checks |
|---|---|---|---|
| Register | external file, URL, or authoritative record | source manifest and preserved/referenceable original | identity, version, rights, checksum, provenance |
| Extract | registered source package | structured, addressable records and citations | fidelity, locator validity, extraction method |
| Design | standards, institutional constraints, course requirements | course blueprint | time feasibility, required coverage, conflicts |
| Compile | approved blueprint and reviewed knowledge references | structured curriculum model and trace graph | schema, references, coverage, safety, time |
| Render | approved curriculum model, renderer configuration, optional template | artifact and generation manifest | model approval, renderer prerequisites, deterministic identity |
| Audit | versioned sources, blueprint, model, and manifests | coverage, gap, impact, and accreditation reports | graph integrity and freshness |

## Prohibited flows

The following paths are invalid:

```text
slides ───────────────X──> lesson plan
standard PDF ─────────X──> assessment
template placeholder ─X──> curriculum fact
generated artifact ───X──> curriculum model
institution overlay ──X──> replacement objective
```

Source files may be shown or cited inside an artifact only through an approved
model reference. A renderer may retrieve a referenced media asset, but the
model determines that the asset is used and why.

## Transformation records

Each stage MUST record:

- input IDs and immutable versions or checksums;
- output IDs and schema versions;
- tool/compiler version;
- timestamp;
- actor or automation identity;
- approval state where applicable; and
- diagnostics and explicit exception dispositions.

## Change propagation

An upstream change MUST NOT mutate approved downstream records in place.
Instead TEOS:

1. registers a new source or record version;
2. identifies affected trace paths;
3. marks dependent blueprints, models, and artifacts stale;
4. recompiles drafts;
5. presents semantic changes for review; and
6. generates new artifacts only after required approval.

## Failure behavior

- Missing required evidence, broken references, impossible schedules, or
  unapproved model content stop affected builds.
- Optional missing content is handled only when the renderer contract declares
  it optional.
- Partial builds identify omitted targets and their diagnostics.
- Failed builds never overwrite the last approved artifact set.

## Legacy bridge

Until blueprint and model schemas are executable, existing validated course/week
records may flow through current renderers. That compatibility path is
explicitly transitional and MUST NOT be used to justify new direct
instructional-resource-to-renderer dependencies.
