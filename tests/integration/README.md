# Integration tests

These tests call production interfaces across subsystem boundaries. They avoid
mocking TEOS components and use temporary output directories for write paths.
Complete installed-application behavior belongs in `../end_to_end`; stable
canonical outcomes belong in `../regression`.
