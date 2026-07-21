# database/gain_pain_repository.py
# ─────────────────────────────────────────────────────────────────────────
# Adapter exposing Friend's original gain_pain_repository contract over the
# canonical `gainpain_analyses` table (written by Module 3's AI gain-pain
# logic, preserved from My Project — and, after a Save in the new Expert
# Review panel, by the expert-override recompute path).
#
# Friend's original positional contract:
#   [12]=gain_score [13]=pain_score [14]=priority_score
# ─────────────────────────────────────────────────────────────────────────

from database.db import db_load_gainpain


def get_gain_pain_by_problem(problem_id):
    rows = db_load_gainpain(problem_id)
    if not rows:
        return None
    g = rows[0]  # most recent
    return (
        g["id"], problem_id,
        g.get("business_value_gain"), g.get("strategic_alignment"),
        g.get("efficiency_gain"), g.get("innovation_potential"),
        g.get("implementation_cost"), g.get("operational_risk"),
        g.get("adoption_resistance"), g.get("compliance_burden"),
        None, None,                                   # unused legacy slots
        round(g.get("avg_gains") or 0, 2),             # [12] Gain Score
        round(g.get("avg_pains") or 0, 2),             # [13] Pain Score
        round(g.get("priority_score_scaled") or 0, 2), # [14] Priority Score
    )


def get_top_opportunities():
    rows = db_load_gainpain()
    rows = sorted(rows, key=lambda g: g.get("priority_score_scaled") or 0, reverse=True)[:5]
    return [
        (g["id"], g["problem_id"], round(g.get("priority_score_scaled") or 0, 2), g.get("priority_band"))
        for g in rows
    ]
