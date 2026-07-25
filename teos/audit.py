"""Audit curriculum relationships without modifying source records."""

from __future__ import annotations

from typing import Any


def coverage_findings(week: dict[str, Any]) -> list[str]:
    coverage = {
        field: {
            objective_id
            for item in week[field]
            for objective_id in item["objective_ids"]
        }
        for field in ("lectures", "labs", "assessments")
    }
    findings: list[str] = []
    for objective in week["objectives"]:
        objective_id = objective["id"]
        if objective_id not in coverage["lectures"]:
            findings.append(f"{objective_id}: no lecture alignment")
        if objective_id not in coverage["labs"]:
            findings.append(f"{objective_id}: no lab alignment")
        if objective_id not in coverage["assessments"]:
            findings.append(f"{objective_id}: no assessment alignment")
    return findings
