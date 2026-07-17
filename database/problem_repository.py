# database/problem_repository.py
# ─────────────────────────────────────────────────────────────────────────
# Thin adapter so Friend's page code (app.py / pages/4_Governance_Review.py)
# can keep using the exact function names + positional-tuple access patterns
# it was written against, while the data actually lives in the canonical
# (My Project) `problem_statements` table. No UI/flow code in Friend's pages
# had to change — only this data-access layer was written to bridge schemas.
#
# Friend's original positional contract for a "problem" row:
#   [0]=id [1]=problem_statement [2]=business_objective [3]=proposed_solution
#   [4]=timeline [5]=owner [6]=workflow_location [7]=decision_support
#   [8]=business_value [9]=stakeholders [10]=why_ai [11]=data_sensitivity
# ─────────────────────────────────────────────────────────────────────────

from datetime import datetime

from database.db import (
    db_insert_record,
    db_load_all,
    db_get_problem,
    db_update_problem_planning_context,
)

def new_draft_id() -> str:
    """Generate a draft record id up front, before the problem is finally
    saved, so uploaded documents / contradiction flags / solution proposals
    captured during the new Idea Submission v2 flow can all be linked to
    the same id from the very first step."""
    return f"GRP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def save_problem_v2(data: dict, record_id: str = None):
    """
    Idea Submission v2 (document-aware flow) save path. Functionally the
    same shape as save_problem() below, but accepts a pre-generated
    record_id (from new_draft_id()) so it matches whatever id was already
    used to tag uploaded_documents / contradiction_flags / solution_proposals
    rows during the multi-step flow, and additionally persists the accepted
    proposed_solution fields. The original save_problem() is left untouched
    so Friend's Module 1 (app.py-as-was) keeps working unmodified elsewhere
    if ever needed.
    """
    record_id = record_id or new_draft_id()
    db_insert_record({
        "id":                   record_id,
        "submitted_at":         datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status":               "Submitted",
        "problem_statement":    data.get("problem_statement", ""),
        "business_objective":   data.get("business_objective", ""),
        "solution_approach":    data.get("proposed_solution", ""),
        "timeline":             data.get("timeline", ""),
        "action_owner":         data.get("owner", ""),
        "workflow_location":    data.get("workflow_location", ""),
        "decision_support":     data.get("decision_support", ""),
        "business_value":       data.get("business_value", ""),
        "stakeholders":         data.get("stakeholders", ""),
        "why_ai":               data.get("why_ai", ""),
        "data_sensitivity":     data.get("data_sensitivity", ""),
        "iso_risk_category":     data.get("iso_risk_category", ""),
        "affected_stakeholders": data.get("affected_stakeholders", data.get("stakeholders", "")),
        "human_override":        data.get("human_override", ""),
        "data_sources":          data.get("data_sources", ""),
        "success_criteria":      data.get("success_criteria", ""),
    })
    return record_id


def save_problem(data: dict):
    """Used by Friend's Module 1 (app.py) intake form."""
    record_id = f"GRP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    db_insert_record({
        "id":                   record_id,
        "submitted_at":         datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status":               "Submitted",
        "problem_statement":    data.get("problem_statement", ""),
        "business_objective":   data.get("business_objective", ""),
        "solution_approach":    data.get("proposed_solution", ""),
        "timeline":             data.get("timeline", ""),
        "action_owner":         data.get("owner", ""),
        "workflow_location":    data.get("workflow_location", ""),
        "decision_support":     data.get("decision_support", ""),
        "business_value":       data.get("business_value", ""),
        "stakeholders":         data.get("stakeholders", ""),
        "why_ai":               data.get("why_ai", ""),
        "data_sensitivity":     data.get("data_sensitivity", ""),
        # ISO 42001 fields (My Project) — left blank when a problem is
        # captured through Friend's intake form; Module 2's AI feasibility
        # logic treats missing ISO fields as "Not specified" and continues.
        "iso_risk_category":     data.get("iso_risk_category", ""),
        "affected_stakeholders": data.get("affected_stakeholders", data.get("stakeholders", "")),
        "human_override":        data.get("human_override", ""),
        "data_sources":          data.get("data_sources", ""),
        "success_criteria":      data.get("success_criteria", ""),
    })
    return record_id


def get_problems():
    """Returns [(id, problem_statement), ...] — same shape Friend's pages expect."""
    return [(r["id"], r["problem_statement"]) for r in db_load_all()]


def get_problem_by_id(problem_id):
    """Returns a positional tuple matching Friend's original column order."""
    r = db_get_problem(problem_id)
    if not r:
        return None
    return (
        r["id"],
        r.get("problem_statement", ""),
        r.get("business_objective", ""),
        r.get("solution_approach", ""),
        r.get("timeline", ""),
        r.get("action_owner", ""),
        r.get("workflow_location", ""),
        r.get("decision_support", ""),
        r.get("business_value", ""),
        r.get("stakeholders", "") or r.get("affected_stakeholders", ""),
        r.get("why_ai", ""),
        r.get("data_sensitivity", ""),
    )

def update_problem_planning_context(problem_id, timeline, owner):
    db_update_problem_planning_context(
        problem_id,
        timeline,
        owner
    )