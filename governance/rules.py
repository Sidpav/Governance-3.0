from copy import deepcopy

DIMENSIONS = (
    "ai_suitability", "economic_viability", "data_readiness",
    "workflow_maturity", "change_management", "risk_compliance",
)


class GovernanceValidationError(ValueError):
    pass


def validate_feasibility_result(raw: dict, problem: dict) -> dict:
    """Validate scores and calculate the authoritative verdict in Python."""
    if not isinstance(raw, dict):
        raise GovernanceValidationError("Assessment output must be an object.")
    result = deepcopy(raw)
    scores = result.get("scores")
    if not isinstance(scores, dict):
        raise GovernanceValidationError("Assessment output is missing scores.")
    clean = {}
    for key in DIMENSIONS:
        try:
            value = round(float(scores[key]), 1)
        except (KeyError, TypeError, ValueError):
            raise GovernanceValidationError(f"Invalid or missing score: {key}")
        if not 1.0 <= value <= 5.0:
            raise GovernanceValidationError(f"Score outside 1–5 range: {key}")
        clean[key] = value

    overall = sum(clean.values()) / len(clean)
    risk_level = str(problem.get("iso_risk_category") or "").strip().lower()
    hard_reasons = []
    if risk_level == "unacceptable":
        hard_reasons.append("Use case is classified as Unacceptable risk.")
    if clean["risk_compliance"] <= 2.0:
        hard_reasons.append("Risk & Compliance readiness is at or below 2.0.")
    if clean["data_readiness"] <= 2.0 and str(problem.get("data_sensitivity") or "").lower() in {
        "restricted", "highly restricted", "personal data (pii)"
    }:
        hard_reasons.append("Sensitive data is proposed without sufficient data readiness.")

    if risk_level == "high":
        overall -= 0.3
    overall = round(max(0.0, min(5.0, overall)), 2)
    verdict = "Not Feasible" if hard_reasons or overall < 2.5 else (
        "Conditional" if overall < 3.5 else "Feasible"
    )
    result["scores"] = clean
    result["overall"] = overall
    result["verdict"] = verdict
    result["hard_gate_triggered"] = bool(hard_reasons)
    result["hard_gate_reason"] = " ".join(hard_reasons)
    result.setdefault("dimension_reasoning", {})
    result.setdefault("dimension_improvement", {})
    result.setdefault("strengths", [])
    result.setdefault("risks", [])
    result.setdefault("recommendations", [])
    result.setdefault("overall_summary", "")
    result.setdefault("planning_context", {})
    return result


def validate_gain_pain_result(raw: dict) -> dict:
    result = deepcopy(raw)
    gains = result.get("gains", {})
    pains = result.get("pains", {})
    gain_keys = ("business_value_gain", "strategic_alignment", "efficiency_gain", "innovation_potential")
    pain_keys = ("implementation_cost", "operational_risk", "adoption_resistance", "compliance_burden")
    for group, keys in ((gains, gain_keys), (pains, pain_keys)):
        for key in keys:
            try: group[key] = round(float(group[key]), 1)
            except (KeyError, TypeError, ValueError): raise GovernanceValidationError(f"Invalid score: {key}")
            if not 1.0 <= group[key] <= 5.0: raise GovernanceValidationError(f"Score outside 1–5 range: {key}")
    avg_gains = round(sum(gains[k] for k in gain_keys) / 4, 2)
    avg_pains = round(sum(pains[k] for k in pain_keys) / 4, 2)
    priority = round(avg_gains * 0.6 - avg_pains * 0.4, 2)
    scaled = round(max(0, min(10, ((priority + 2) / 5) * 10)), 2)
    band = "High Priority" if scaled >= 7 else ("Medium Priority" if scaled >= 4 else "Low Priority")
    result.update({"gains": gains, "pains": pains, "avg_gains": avg_gains,
                   "avg_pains": avg_pains, "priority_score": priority,
                   "priority_score_scaled": scaled, "priority_band": band})
    return result
