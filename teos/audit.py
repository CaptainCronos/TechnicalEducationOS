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
    for lesson in week.get("lessons", []):
        for activity in lesson["activities"]:
            if activity["category"] == "academic":
                coverage["lectures"].update(activity["objective_ids"])
            elif activity["category"] == "shop":
                coverage["labs"].update(activity["objective_ids"])
        referenced_assessments = set(lesson["assessment_ids"])
        coverage["assessments"].update(
            objective_id
            for assessment in week["assessments"]
            if assessment["id"] in referenced_assessments
            for objective_id in assessment["objective_ids"]
        )
    findings: list[str] = []
    for objective in week["objectives"]:
        objective_id = objective["id"]
        if objective_id not in coverage["lectures"]:
            findings.append(f"{objective_id}: no lecture alignment")
        if objective_id not in coverage["labs"]:
            findings.append(f"{objective_id}: no lab alignment")
        if objective_id not in coverage["assessments"]:
            findings.append(f"{objective_id}: no assessment alignment")
    for assessment in week["assessments"]:
        if "question_bank" in assessment and not assessment["question_bank"]:
            findings.append(f"{assessment['id']}: question bank is empty")
    return findings
