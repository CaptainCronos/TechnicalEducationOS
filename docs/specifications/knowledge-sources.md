# Knowledge Sources Specification

Status: Governing  
Version: 1.0

## Purpose

The knowledge-source framework makes external evidence identifiable,
versioned, addressable, and reviewable before it influences curriculum. It
preserves the distinction between what a source says and what TEOS decides to
do with it.

## Source layers

| Layer | Question answered | Examples |
|---|---|---|
| Educational standards | What must students learn or demonstrate? | ASE tasks, FMCSA rules, OSHA requirements, OEM requirements, institutional outcomes |
| Institutional resources | When and under what local constraints can teaching occur? | academic calendar, meeting pattern, holidays, policies, exam windows |
| Instructional resources | What approved content or method can support delivery? | CDX slides, instructor notes, lab manuals, service manuals, videos, demonstrations |

A source has one primary layer. Cross-layer relationships are expressed as
mappings rather than by duplicating the source.

## Source manifest

Every registered source MUST have a manifest containing at least:

- `source_id`: stable namespaced identifier;
- `source_type` and `layer`;
- title, issuer/author, and edition or version;
- publication/effective date when known;
- acquisition date and acquisition method;
- canonical URI or repository-relative locator;
- integrity checksum when a file is retained;
- media type and language;
- rights, license, access, and redistribution notes;
- supersession status;
- registration actor and review status; and
- schema version.

Unknown values are represented explicitly; they are not fabricated.

## Addressable records

Extraction MUST produce records that can cite a precise source location.
Depending on the media, a locator may identify:

- standard section, task code, table, or appendix;
- PDF page and bounding region;
- slide number and element;
- document heading and paragraph;
- video time range;
- manual chapter, page, figure, or procedure; or
- calendar date or policy section.

An extracted record includes its text or structured value, source ID, source
version, locator, extraction method, confidence/review state, and checksum or
content hash where practical.

## Source-specific requirements

### Standards

Standard records distinguish task/requirement text, classification or priority,
conditions, performance criteria, related safety requirements, and
supersession. TEOS preserves issuer identifiers rather than replacing them with
course-local IDs.

### Institutional resources

Calendar and schedule records use explicit dates, time zones, meeting patterns,
exceptions, instructional-minute rules, and approval status. Policies retain
effective dates and the population or program to which they apply.

### Instructional resources

Resources record applicable topics, intended audience, supported delivery
modes, prerequisites, safety constraints, and addressable media. Topic tagging
is descriptive until an authorized mapping links the resource to a curriculum
entity.

## Ingestion lifecycle

```text
discovered → registered → extracted → reviewed → active
                                  ↘ rejected/superseded
```

- **Registered** means provenance and identity are sufficient.
- **Extracted** means content is addressable but not necessarily verified.
- **Reviewed** means extraction fidelity has been checked.
- **Active** means the version may support new blueprint or model work.
- **Superseded** sources remain available for historical traceability.

## Conflict and interpretation

Ingestion does not reconcile conflicting sources. Conflicts are recorded with
both citations and routed to blueprint or curriculum review. Interpretive
statements MUST be stored as authoring decisions linked to the supporting
source; they MUST NOT be inserted into extracted source text.

## Inputs and outputs

Inputs are external authoritative documents, media, metadata, and reviewer
decisions. Outputs are versioned source packages, addressable extracted records,
diagnostics, and provenance links consumed by blueprints and curriculum models.

Knowledge ingestion MUST NOT output lesson plans, labs, assessment questions,
or other educational artifacts.
