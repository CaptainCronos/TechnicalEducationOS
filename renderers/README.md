# Educational artifact renderers

Purpose: document artifact projection ownership. Current renderer
implementations live in `teos/`.

Inputs are approved structured curriculum models, renderer configuration,
institution presentation configuration, and optional templates. Outputs are
generated artifacts and generation manifests written to the caller-selected
output directory.

Renderers may select and format model content. They must not invent curriculum
or consume instructional source files as a parallel source. The current Python
implementations remain under `teos/` until migration is justified.

The [Canonical Lesson Renderer Contract](canonical-lesson-contract.md) defines
the common input and non-invention rules for administrative, instructor,
student, lab, presentation-outline, assessment, and LMS lesson artifacts.

See the [Educational Artifact
Specification](../docs/specifications/educational-artifacts.md).
