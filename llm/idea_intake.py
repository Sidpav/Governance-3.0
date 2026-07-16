# llm/idea_intake.py
# ─────────────────────────────────────────────────────────────────────────
# AI logic for the new document-aware Idea Submission flow. Each function
# takes plain Python inputs and returns a plain dict — no Streamlit imports
# here, so this module is testable independent of the UI layer (pages/
# 1_Idea_Submission.py owns all st.* calls and session_state).
# ─────────────────────────────────────────────────────────────────────────

import json

from utils.helpers import call_ai
from config.prompts import (
    IDEA_AUTOCAPTURE_PROMPT,
    IDEA_SOLUTION_PROPOSAL_PROMPT,
    IDEA_CLARIFICATION_QUESTIONS_PROMPT,
    IDEA_CONTRADICTION_PROMPT,
    IDEA_SIMILAR_PROJECT_PROMPT,
    IDEA_GAPS_PROMPT,
    IDEA_BUSINESS_VALUE_QUESTION_PROMPT,
    IDEA_DECISION_ENGINES_PROMPT,
)


def _clean_json(content: str) -> dict:
    content = content.replace("```json", "").replace("```", "").strip()
    if not content:
        raise ValueError("Model returned an empty response.")
    return json.loads(content)


def autocapture_fields(unified_context: str) -> dict:
    """
    Spec §6 — Auto-Capture Initial Fields.
    Identifies problem_statement + business_objective from the unified
    context (user text + extracted documents) before any questions are asked.
    """
    if not unified_context.strip():
        return {"problem_statement": "", "business_objective": "",
                "confidence": "low", "grounded_in": "No input provided."}

    prompt = f"{IDEA_AUTOCAPTURE_PROMPT}\n\n=== CONTEXT ===\n{unified_context}"
    raw = call_ai(prompt)
    try:
        return _clean_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {"problem_statement": "", "business_objective": "",
                "confidence": "low", "grounded_in": "Auto-capture failed; please fill in manually."}


def propose_solution(problem_context: dict, clarification_qa: list | None = None) -> dict:
    """
    Spec §10 — AI Proposed Solution Generation.
    `problem_context` must contain: problem_statement, business_objective,
    business_value, workflow_location, decision_support.
    `clarification_qa` (optional): [{"question": "...", "answer": "..."}]
    from a previous rejected round (Spec §11 validation loop).
    """
    ctx_lines = [
        f"Problem Statement: {problem_context.get('problem_statement', '')}",
        f"Business Objective: {problem_context.get('business_objective', '')}",
        f"Business Value (user-provided): {problem_context.get('business_value', '')}",
        f"Workflow Location: {problem_context.get('workflow_location', '')}",
        f"Decision Support Needed: {problem_context.get('decision_support', '')}",
    ]
    if clarification_qa:
        ctx_lines.append("\nPrior clarification round (previous proposal was rejected):")
        for qa in clarification_qa:
            ctx_lines.append(f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}")

    prompt = f"{IDEA_SOLUTION_PROPOSAL_PROMPT}\n\n=== PROBLEM CONTEXT ===\n" + "\n".join(ctx_lines)
    raw = call_ai(prompt)
    try:
        return _clean_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {
            "solution_name": "Unable to generate",
            "solution_type": "",
            "solution_description": "The AI could not generate a proposal. Please try again.",
            "expected_benefits": [],
            "key_assumptions": [],
        }


def generate_clarification_questions(problem_context: dict, rejected_solution: dict) -> dict:
    """Spec §11 — If NO: generate targeted clarification questions."""
    ctx = (
        f"Problem Statement: {problem_context.get('problem_statement', '')}\n"
        f"Business Objective: {problem_context.get('business_objective', '')}\n"
        f"Business Value: {problem_context.get('business_value', '')}\n"
        f"Workflow Location: {problem_context.get('workflow_location', '')}\n"
        f"Decision Support: {problem_context.get('decision_support', '')}\n\n"
        f"Rejected Solution: {rejected_solution.get('solution_name', '')} "
        f"({rejected_solution.get('solution_type', '')})\n"
        f"Description: {rejected_solution.get('solution_description', '')}"
    )
    prompt = f"{IDEA_CLARIFICATION_QUESTIONS_PROMPT}\n\n=== CONTEXT ===\n{ctx}"
    raw = call_ai(prompt)
    try:
        return _clean_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {"questions": [
            {"id": "q1", "question": "What constraints (budget, timeline, technical) should shape the solution?"},
            {"id": "q2", "question": "Which systems must this integrate with?"},
            {"id": "q3", "question": "Which decisions must remain human-controlled?"},
        ]}


def detect_contradictions(user_claims: dict, unified_document_context: str) -> dict:
    """
    Spec §12/§13 — Contradiction Detection with reference-based evidence.
    `user_claims` should be the directly-entered fields most likely to
    contain checkable numbers/scope (business_value, problem_statement,
    business_objective, workflow_location, decision_support).
    `unified_document_context` must be the document-only portion of the
    unified context (NOT including the user's own text) so the model has
    something independent to check against.
    """
    if not unified_document_context.strip():
        return {"contradictions": [], "has_contradictions": False}

    claims_text = "\n".join(f"{k}: {v}" for k, v in user_claims.items() if v)
    prompt = (
        f"{IDEA_CONTRADICTION_PROMPT}\n\n"
        f"=== USER-PROVIDED CLAIMS ===\n{claims_text}\n\n"
        f"=== DOCUMENT CONTENT (with source tags) ===\n{unified_document_context}"
    )
    raw = call_ai(prompt)
    try:
        result = _clean_json(raw)
        result.setdefault("contradictions", [])
        result.setdefault("has_contradictions", bool(result["contradictions"]))
        return result
    except (ValueError, json.JSONDecodeError):
        return {"contradictions": [], "has_contradictions": False, "_error": "Contradiction check failed."}


# ── Module 1 rework (Figma "Cortexa" flow) ──────────────────────────────────

def find_similar_problem(unified_context: str, existing_problems: list) -> dict:
    """
    Figma "Similar Project Found" step. Compares the new idea against a
    catalogue of already-saved problems and returns the closest match if
    the model is confident it's the same underlying problem.
    `existing_problems`: list of dicts with id/status/problem_statement/
    workflow_location (the shape returned by database.db.db_load_all()).
    """
    if not unified_context.strip() or not existing_problems:
        return {"found": False}

    catalogue_lines = []
    for p in existing_problems[:30]:
        catalogue_lines.append(
            f"- ID: {p.get('id','')} | Status: {p.get('status','') or 'Unknown'} | "
            f"Problem: {(p.get('problem_statement','') or '')[:220]} | "
            f"Business Unit: {p.get('workflow_location','') or 'Unspecified'}"
        )
    prompt = (
        f"{IDEA_SIMILAR_PROJECT_PROMPT}\n\n=== NEW IDEA ===\n{unified_context[:3000]}\n\n"
        f"=== EXISTING PROJECTS ===\n" + "\n".join(catalogue_lines)
    )
    raw = call_ai(prompt)
    try:
        result = _clean_json(raw)
        result.setdefault("found", False)
        return result
    except (ValueError, json.JSONDecodeError):
        return {"found": False}


def detect_gaps(unified_doc_context: str) -> dict:
    """
    Figma "Gaps / Discrepancies Found" step. Unlike detect_contradictions()
    (which checks user claims against documents), this looks for places
    where the uploaded DOCUMENTS disagree with EACH OTHER, and proposes an
    editable resolution for each.
    """
    if not unified_doc_context.strip():
        return {"gaps": []}
    prompt = f"{IDEA_GAPS_PROMPT}\n\n=== DOCUMENT CONTENT ===\n{unified_doc_context}"
    raw = call_ai(prompt)
    try:
        result = _clean_json(raw)
        result.setdefault("gaps", [])
        return result
    except (ValueError, json.JSONDecodeError):
        return {"gaps": []}


def generate_business_value_question(fields: dict) -> str:
    """Figma "Business Value Clarification" step — one tailored, quantifiable
    question (plain text, not JSON)."""
    ctx = (
        f"Problem Statement: {fields.get('problem_statement', '')}\n"
        f"Business Objective: {fields.get('business_objective', '')}"
    )
    prompt = f"{IDEA_BUSINESS_VALUE_QUESTION_PROMPT}\n\n=== CONTEXT ===\n{ctx}"
    raw = (call_ai(prompt) or "").strip().strip('"').strip()
    return raw or "What measurable business value would solving this problem create over the next 12 months?"


def propose_decision_engines(fields: dict) -> dict:
    """Figma "Decision Support Systems Required" step — 4-5 discrete AI
    decision-support engines that together solve the problem end-to-end."""
    ctx_lines = [
        f"Problem Statement: {fields.get('problem_statement', '')}",
        f"Business Objective: {fields.get('business_objective', '')}",
        f"Business Value: {fields.get('business_value', '')}",
    ]
    prompt = f"{IDEA_DECISION_ENGINES_PROMPT}\n\n=== CONTEXT ===\n" + "\n".join(ctx_lines)
    raw = call_ai(prompt)
    try:
        result = _clean_json(raw)
        result.setdefault("engines", [])
        return result
    except (ValueError, json.JSONDecodeError):
        return {"engines": []}
