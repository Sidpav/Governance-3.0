# database/feasibility_repository.py
# ─────────────────────────────────────────────────────────────────────────
# Adapter exposing Friend's original feasibility_repository contract over
# the canonical `feasibility_assessments` table (written by Module 2's
# AI feasibility logic, preserved from My Project).
#
# Friend's original positional contract for a "feasibility" row used a
# 13-column table (id, problem_id, ai_suitability, economic_viability,
# data_readiness, technology_readiness, workflow_maturity, ...). My
# Project's six dimensions don't split "data" and "technology" readiness,
# so [4] and [5] both surface `data_readiness_score` — the dimension that,
# in My Project's framework, explicitly covers Data & Technology Readiness.
# ─────────────────────────────────────────────────────────────────────────

from database.db import db_load_assessments
from database.problem_repository import get_problems, get_problem_by_id  # noqa: F401 (re-exported — Friend's Module 4 page imports these from here)


def get_feasibility_by_problem(problem_id):
    rows = db_load_assessments(problem_id)
    if not rows:
        return None
    a = rows[0]  # most recent
    fmt = lambda v: f"{float(v or 0):.1f}/5"
    return (
        a["id"],
        problem_id,
        fmt(a.get("ai_suitability_score")),
        fmt(a.get("economic_viability_score")),
        fmt(a.get("data_readiness_score")),
        fmt(a.get("data_readiness_score")),   # "Technology" column — see note above
        fmt(a.get("workflow_maturity_score")),
        fmt(a.get("change_management_score")),
        fmt(a.get("risk_compliance_score")),
        a.get("overall_score"),
        a.get("verdict"),
        a.get("ai_recommendation"),
    )
