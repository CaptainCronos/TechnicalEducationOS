# Versioning and compatibility policy

## Semantic versions

TEOS release tags use Semantic Versioning as `vMAJOR.MINOR.PATCH` with optional
pre-release identifiers such as `-alpha1`, `-beta1`, or `-rc1`. Python package
versions express the same release using PEP 440, for example
`v1.2.0-alpha1` maps to `1.2.0a1`.

- **MAJOR** changes may break stable public contracts and require migration.
- **MINOR** changes add backward-compatible behavior and may deprecate public
  contracts.
- **PATCH** changes contain backward-compatible fixes, including security
  fixes.

Pre-release versions are ordered previews of the intended release. Alpha
contracts may change as evidence is collected. Beta releases freeze intended
stable contracts except where a defect, security issue, or unusable design
requires a documented change. The compatibility guarantees below begin with a
stable release unless a release note explicitly grants an earlier guarantee.

## Compatibility surfaces

| Surface | Public contract | Stable-release guarantee |
|---|---|---|
| Python API | Names re-exported by `teos` and documented in `docs/API.md` | Existing valid calls continue within a major version |
| CLI | Documented commands, options, exit behavior, and machine-readable output | Existing supported invocations continue within a major version |
| Data and schemas | Versioned schemas and documented record semantics | Readers accept supported prior minor formats or provide migration |
| Repository | Documented source-directory roles, manifests, and configuration lookup | Supported repositories remain buildable or receive a migration path |
| Curriculum | Stable IDs, required semantics, mappings, and ordering rules | Content meaning is not silently rewritten by a software update |
| Plugins/extensions | Explicitly documented extension contracts and capability IDs | Governed according to the contract maturity declared below |
| Generated artifacts | Manifest, trace metadata, and documented logical fields | Meaning is preserved; byte-for-byte layout is stable only where tested and documented |

Internal modules, undocumented command output, log wording, filesystem
temporary state, and presentation details are not public contracts. A behavior
does not become public merely because Python permits importing it.

Bug fixes may reject input that never satisfied the documented contract. Such a
change must include a test and release note when users could reasonably have
depended on the prior behavior.

## API compatibility

Public API additions are allowed in a minor release. Removing or changing the
meaning of a public name requires a major release after deprecation. Adding an
optional parameter is compatible; adding a required parameter, changing an
accepted value's meaning, or changing a documented exception is breaking.

CLI additions are compatible when they do not change an existing invocation.
Renaming or removing an option, changing a successful invocation to fail, or
changing documented machine-readable output is breaking.

## Repository and curriculum compatibility

Schema versions and TEOS package versions are separate. Every persisted source
record must identify its schema version where its contract requires one.
Converters must not overwrite the only copy of user data and should support a
dry run or explicit output path.

A stable minor release must either:

1. continue reading repositories accepted by the previous supported minor;
2. provide and test a deterministic migration; or
3. reject the repository with an actionable version diagnostic when the
   repository is outside the published support window.

Stable curriculum identifiers must not be reassigned to different meanings.
Renaming requires an explicit alias or mapping. A software upgrade must not
silently change objectives, durations, safety rules, assessments, sequencing,
or source authority. Reference Curriculum changes that alter expected meaning
require review, snapshot updates, traceability evidence, and release notes.

Generated presentation may evolve in compatible releases, but manifest fields,
trace links, and semantic content are contracts when documented or locked by
regression tests.

## Plugin compatibility

The alpha registry and internal renderer/generator Python interfaces are
**experimental** unless a document explicitly calls them public. Third-party
extensions must pin the TEOS versions they test. Themes, locale catalogs,
institution profiles, and other data extensions are compatible according to
their versioned schema, not merely the Python package version.

An extension contract becomes stable only when it is documented as public,
has conformance tests, and is listed in
[Plugin ecosystem governance](PLUGIN_GOVERNANCE.md). Stable plugin contracts
follow the same major-version rule as the API. Capability negotiation is
preferred to inferring support from implementation details.

## Deprecation

A deprecation must:

- identify the replacement or explain why none exists;
- produce an actionable warning where practical;
- appear in the API/CLI or schema documentation and `CHANGELOG.md`;
- include migration and compatibility tests; and
- state the earliest removal release.

After the first stable release, a public contract normally remains available
for at least one subsequent minor release and six months, whichever is longer,
and is removed only in a major release. A longer window may be assigned to
repository or curriculum formats because institutional migrations are costly.

Maintainers may accelerate removal when retaining behavior creates a material
security, privacy, legal, licensing, data-integrity, or learner-safety risk.
The release notes must explain the exception and provide mitigation when
possible. Pre-release incompatibilities do not require a major version, but
they still require release notes and migration guidance when practical.
