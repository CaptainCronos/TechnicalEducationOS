#!/usr/bin/env bash
#
# expand_repository.sh
#
# Expand the TechnicalEducationOS repository structure.
# Safe to run multiple times.
#

set -euo pipefail

###############################################################################
# Locate repository root
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(realpath "$SCRIPT_DIR/../..")}"

echo
echo "==============================================="
echo "TechnicalEducationOS Repository Expansion"
echo "==============================================="
echo "Repository: $ROOT"
echo

###############################################################################
# KNOWLEDGE
###############################################################################

mkdir -p "$ROOT/knowledge/standards/ASE/T1"
mkdir -p "$ROOT/knowledge/standards/ASE/T2"
mkdir -p "$ROOT/knowledge/standards/ASE/T3"
mkdir -p "$ROOT/knowledge/standards/ASE/T4"
mkdir -p "$ROOT/knowledge/standards/ASE/T5"
mkdir -p "$ROOT/knowledge/standards/ASE/T6"
mkdir -p "$ROOT/knowledge/standards/ASE/T7"
mkdir -p "$ROOT/knowledge/standards/ASE/T8"

mkdir -p "$ROOT/knowledge/standards/FMCSA"
mkdir -p "$ROOT/knowledge/standards/OSHA"
mkdir -p "$ROOT/knowledge/standards/EPA"
mkdir -p "$ROOT/knowledge/standards/OEM"

mkdir -p "$ROOT/knowledge/instructional/cdx"
mkdir -p "$ROOT/knowledge/instructional/videos"
mkdir -p "$ROOT/knowledge/instructional/lab-manuals"
mkdir -p "$ROOT/knowledge/instructional/instructor-notes"
mkdir -p "$ROOT/knowledge/instructional/manufacturer-training"
mkdir -p "$ROOT/knowledge/instructional/service-information"

mkdir -p "$ROOT/knowledge/institutional/calendar"
mkdir -p "$ROOT/knowledge/institutional/grading"
mkdir -p "$ROOT/knowledge/institutional/policies"
mkdir -p "$ROOT/knowledge/institutional/program-requirements"

mkdir -p "$ROOT/knowledge/extracted/standards"
mkdir -p "$ROOT/knowledge/extracted/instructional"
mkdir -p "$ROOT/knowledge/extracted/institutional"

mkdir -p "$ROOT/knowledge/processed/standards"
mkdir -p "$ROOT/knowledge/processed/instructional"
mkdir -p "$ROOT/knowledge/processed/institutional"

###############################################################################
# CURRICULUM
###############################################################################

mkdir -p "$ROOT/curriculum/competencies"
mkdir -p "$ROOT/curriculum/objectives"
mkdir -p "$ROOT/curriculum/lessons"
mkdir -p "$ROOT/curriculum/activities"
mkdir -p "$ROOT/curriculum/assessments"
mkdir -p "$ROOT/curriculum/scope-sequence"

###############################################################################
# RENDERERS
###############################################################################

mkdir -p "$ROOT/renderers/lesson-plans"
mkdir -p "$ROOT/renderers/labs"
mkdir -p "$ROOT/renderers/assessments"
mkdir -p "$ROOT/renderers/student-guides"
mkdir -p "$ROOT/renderers/slides"
mkdir -p "$ROOT/renderers/lms"
mkdir -p "$ROOT/renderers/reports"
mkdir -p "$ROOT/renderers/exports"

###############################################################################
# TEMPLATES
###############################################################################

mkdir -p "$ROOT/templates/slides"
mkdir -p "$ROOT/templates/student-guides"
mkdir -p "$ROOT/templates/assessments"
mkdir -p "$ROOT/templates/labs"
mkdir -p "$ROOT/templates/reports"

###############################################################################
# SCHEMAS
###############################################################################

mkdir -p "$ROOT/schemas/knowledge"
mkdir -p "$ROOT/schemas/curriculum"
mkdir -p "$ROOT/schemas/artifacts"

###############################################################################
# OUTPUTS
###############################################################################

mkdir -p "$ROOT/outputs/curriculum"
mkdir -p "$ROOT/outputs/slides"
mkdir -p "$ROOT/outputs/student-guides"
mkdir -p "$ROOT/outputs/lms"

###############################################################################
# SCRIPTS
###############################################################################

mkdir -p "$ROOT/scripts/bootstrap"
mkdir -p "$ROOT/scripts/extractors"
mkdir -p "$ROOT/scripts/validators"
mkdir -p "$ROOT/scripts/utilities"

###############################################################################
# TESTS
###############################################################################

mkdir -p "$ROOT/tests/fixtures"
mkdir -p "$ROOT/tests/integration"
mkdir -p "$ROOT/tests/unit"

###############################################################################
# EXAMPLES
###############################################################################

mkdir -p "$ROOT/examples/knowledge"
mkdir -p "$ROOT/examples/courses"
mkdir -p "$ROOT/examples/blueprints"
mkdir -p "$ROOT/examples/outputs"

###############################################################################
# Create README placeholders where missing
###############################################################################

while IFS= read -r -d '' dir
do
    if [[ ! -f "$dir/README.md" ]]; then
        cat > "$dir/README.md" <<EOF
# $(basename "$dir")

Purpose:
Describe the purpose of this directory.

Status:
Placeholder
EOF
    fi
done < <(find "$ROOT" -type d -print0)

###############################################################################
# Finished
###############################################################################

echo
echo "Repository expansion complete."
echo
echo "Review the changes:"
echo "    git status"
echo "    lstree $ROOT"
echo
echo "Done."
