# Public application API

TEOS intentionally exposes a small public API from the `teos` package:

- `BuildConfig`: immutable build configuration;
- `BuildResult`: immutable build result;
- `BuildError`: controlled application failure;
- `build(config)`: complete application pipeline; and
- `__version__`: installed application version.

```python
from pathlib import Path

from teos import BuildConfig, BuildError, build

try:
    result = build(
        BuildConfig(
            repository=Path("examples/reference_curriculum"),
            schema_directory=Path("schemas"),
            institution_id="north-valley-community-college",
            calendar_id="fall-2026-semester",
            meeting_pattern_id="monday-wednesday-evening",
            locale="en-US",
            theme="institution-branded",
            output_directory=Path("/tmp/teos-api-build"),
        )
    )
except BuildError as exc:
    raise SystemExit(f"TEOS build failed: {exc}") from exc

print(result.build_id)
print(result.manifest_path)
print(len(result.artifact_paths))
```

`BuildConfig` also accepts explicit `renderers` and `generators` tuples.
Available renderer IDs are `administrative`, `instructor`, and `lab`; available
generator IDs are `markdown`, `html`, `docx`, and `pdf`.

The configured output path must not exist. TEOS stages results and moves them
into place only after a complete successful build. Equivalent CLI and API
configurations produce the same logical artifacts and build identifier.

Internal modules are importable for implementation and testing but are not part
of the compatibility promise unless re-exported by `teos`. See
[Versioning and compatibility](COMPATIBILITY.md) for the permanent API,
deprecation, and pre-release guarantees.
