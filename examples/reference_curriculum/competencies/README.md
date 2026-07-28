# Competency mapping

Competencies are canonical objects embedded in `curriculum/course.json`.
Objectives are owned by instructional units, and sessions select objectives
from exactly one unit.

| Competency | Standards | Units |
|---|---|---|
| `comp.electrical-safety` | `OSHA.1910.334.c.1`, `NFPA70E.ESWP` | Both units |
| `comp.measurement` | `OSHA.1910.334.c.1`, `TEOS.EF-2` | Both units |
| `comp.circuit-analysis` | `TEOS.EF-1`, `TEOS.EF-2` | Circuit diagnosis |
| `comp.troubleshooting` | `NFPA70E.ESWP`, `TEOS.EF-2`, `TEOS.EF-3` | Circuit diagnosis |

This provides one-to-many standard mappings, many-to-one objective mappings,
and cross-unit reuse of safety and measurement competencies.
