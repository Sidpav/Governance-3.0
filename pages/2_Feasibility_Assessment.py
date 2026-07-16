# pages/2_Feasibility_Assessment.py
#
# MODULE 2 — Feasibility Assessment.
#   Part 1 (problem selection: dropdown, cards, header, layout) — Friend's
#           Project, unchanged.
#   Part 2 (AI feasibility logic, scoring, verdict, ISO/NIST mappings,
#           recommendations) — My Project, unchanged formulas/prompts.
#
# New flow per merge spec: everything happens on ONE scrollable page, in
# this order — Problem Selection -> Assessment Running -> Dimension Scores
# -> Reasoning -> Verdict -> Recommendations. No extra buttons, no second
# page: selecting a problem from the dropdown is the only action needed:
# the AI assessment runs automatically and the rest of the page renders
# sequentially below it.

import streamlit as st
import json
import pandas as pd
from datetime import datetime

from database.problem_repository import get_problems
from database.db import db_get_problem, db_save_assessment, db_update_status, db_load_assessments
from config.constants import ASSESSMENT_DIMENSIONS, VERDICT_CONFIG, M2_SCORING_BASIS, M2_OVERALL_FORMULA_HTML
from utils.helpers import get_completeness_color, call_m2_assessment, sanitize_ai_text
from database.problem_repository import update_problem_planning_context

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb, render_subtabs
from ui.auth import require_login, require_access

st.set_page_config(page_title="AI Governance Platform", page_icon="🤖",
                    layout="wide", initial_sidebar_state="expanded")

require_login()

apply_theme()
render_sidebar("m2")
render_navbar("m2")
require_access("m2")
render_breadcrumb("AI Use-Case Portfolio", "Use-case Scoring & Prioritization")
render_subtabs(
    [("📊 Use-case Scoring & Prioritization", "pages/2_Feasibility_Assessment.py"),
     ("⚖️ Value-Risk Assessment", "pages/3_Gain_Pain_Analysis.py")],
    active_target="pages/2_Feasibility_Assessment.py",
)

# ==========================
# PAGE TITLE  (Friend's — Part 1)
# ==========================

st.title("Use-case Scoring & Prioritization")
st.caption("Evaluate AI readiness and feasibility of submitted business problems.")

# ==========================================
# PROBLEM SELECTION  (Friend's — Part 1)
# ==========================================

problems = get_problems()

if not problems:
    st.warning("No problems found. Please submit a problem in Module 1 first.")
    st.stop()

problem_dict = {row[1]: row[0] for row in problems}
problem_options = ["-- Select a Problem --"] + list(problem_dict.keys())

selected_problem = st.selectbox("Select AI Opportunity", problem_options)

if selected_problem == "-- Select a Problem --":
    st.info("Please select a problem to begin analysis.")
    st.stop()

problem_id = problem_dict[selected_problem]
problem = db_get_problem(problem_id)

with st.container(border=True):
    st.markdown('<span class="card-title"></span>', unsafe_allow_html=True)
    st.subheader("Problem Summary")
    st.info(problem.get("problem_statement", ""))
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Business Objective**")
        st.write(problem.get("business_objective", "") or "—")
        st.write("**Proposed Solution**")
        st.write(problem.get("solution_approach", "") or "—")

    with c2:

        st.write("**Workflow Location**")
        st.write(problem.get("workflow_location", "") or "—")

        st.write("**Decision Support**")
        st.write(problem.get("decision_support", "") or "—")

        st.write("**Business Value**")
        st.write(problem.get("business_value", "") or "—")

st.divider()

# ==========================================
# PART 2 — AI FEASIBILITY LOGIC (My Project)
# ==========================================

st.markdown("### 🤖 AI Analysis")
st.caption("AI is evaluating feasibility across 6 dimensions — "
           "AI Suitability, Economic Viability, Data & Technology Readiness, "
           "Workflow Maturity, Change Management, Risk & Compliance.")

if "m2_result_cache" not in st.session_state:
    st.session_state["m2_result_cache"] = {}

cache = st.session_state["m2_result_cache"]

if problem_id not in cache:
    with st.spinner("AI is evaluating feasibility…"):
        result = call_m2_assessment(problem)
    if not result:
        st.error("Assessment failed. Please check your AI Settings (provider, model, API key) and try again.")
        st.stop()

    # Sanitize every free-text field the AI returned — models occasionally
    # echo markup from the prompt back into their text output, which would
    # otherwise render as broken layout or literal tags (e.g. "</div>")
    # wherever that field is later displayed.
    result["hard_gate_reason"] = sanitize_ai_text(result.get("hard_gate_reason", ""))
    result["overall_summary"] = sanitize_ai_text(result.get("overall_summary", ""))
    result["dimension_reasoning"] = {
        k: sanitize_ai_text(v) for k, v in result.get("dimension_reasoning", {}).items()
    }
    result["dimension_improvement"] = {
        k: sanitize_ai_text(v) for k, v in result.get("dimension_improvement", {}).items()
    }
    result["strengths"] = [sanitize_ai_text(s) for s in result.get("strengths", [])]
    result["risks"] = [sanitize_ai_text(r) for r in result.get("risks", [])]
    result["recommendations"] = [sanitize_ai_text(r) for r in result.get("recommendations", [])]

    cache[problem_id] = result
    # Persist — same scoring/verdict/hard-gate logic as My Project's Module 2
    scores = result.get("scores", {})
    overall = result.get("overall", 0.0)
    verdict = result.get("verdict", "Conditional")

    strengths = "\n".join(f"- {s}" for s in result.get("strengths", []))
    risks = "\n".join(f"- {r}" for r in result.get("risks", []))
    recommendations = "\n".join(f"- {r}" for r in result.get("recommendations", []))
    dim_reasoning = result.get("dimension_reasoning", {})
    reasoning_md = "\n".join(
        f"**{dim['label']}** ({scores.get(dim['id'], 0):.1f}/5): {dim_reasoning.get(dim['id'], '')}"
        for dim in ASSESSMENT_DIMENSIONS
    )

result = cache[problem_id]
planning = result.get("planning_context", {})

timeline = planning.get(
    "timeline",
    ""
)

owner = planning.get(
    "owner",
    ""
)

why_ai = planning.get(
    "why_ai",
    ""
)

data_sensitivity = planning.get(
    "data_sensitivity",
    "Internal"
)
scores = result.get("scores", {})
dim_reasoning = result.get("dimension_reasoning", {})
overall = result.get("overall", 0.0)
verdict = result.get("verdict", "Conditional")
vc = VERDICT_CONFIG.get(verdict, VERDICT_CONFIG["Conditional"])
hard_gate = result.get("hard_gate_triggered")
hard_gate_reason = result.get("hard_gate_reason", "")

st.success("Assessment complete.")

st.markdown("### 🧠 AI Generated Context")

st.caption(
    "The following implementation details have been generated by the AI. "
    "Review and edit them before saving."
)

left, right = st.columns(2)

with left:

    timeline = st.text_input(
        "Estimated Timeline",
        value=timeline
    )

    owner = st.text_input(
        "Business Owner",
        value=owner
    )

with right:

    why_ai = st.text_area(

        "Why AI?",

        value=why_ai,

        height=140

    )

    options = [

        "Public",

        "Internal",

        "Confidential",

        "Restricted",

        "Highly Restricted"

    ]

    predicted = data_sensitivity

    if predicted not in options:
        predicted = "Internal"

    data_sensitivity = st.selectbox(

        "Data Sensitivity",

        options,

        index=options.index(predicted)

    )

st.divider()

# ── Dimension Scores ─────────────────────────────────────────────────────
st.markdown("### 📊 Dimension Scores")
for dim in ASSESSMENT_DIMENSIONS:
    s = scores.get(dim["id"], 0)
    pct = int(s / 5 * 100)
    col = get_completeness_color(pct)
    basis = M2_SCORING_BASIS.get(dim["id"], "")
    rsn = dim_reasoning.get(dim["id"], "")
    st.markdown(f"""
    <div class="card" style="padding:0.9rem 1.2rem;margin-bottom:0.6rem;min-height:0;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span>{dim['icon']} <b>{dim['label']}</b> <span style="color:#888;font-size:0.75rem;">({dim['role']})</span></span>
        <span style="font-weight:700;color:{col};">{s:.1f}/5</span>
      </div>
      <div style="background:#eee;border-radius:8px;height:8px;margin-top:6px;">
        <div style="background:{col};width:{pct}%;height:8px;border-radius:8px;"></div>
      </div>
      {f'<div style="font-size:0.78rem;color:#444;margin-top:7px;font-style:italic;">📌 {rsn}</div>' if rsn else ""}
      <div class="score-basis">
        <span class="basis-label">Score basis — what the AI evaluated</span>
        {basis}
      </div>
    </div>""", unsafe_allow_html=True)

# ── Reasoning ────────────────────────────────────────────────────────────
st.markdown("### 🧠 Reasoning")
if result.get("overall_summary"):
    st.markdown(f'<div class="review-box">{result["overall_summary"]}</div>', unsafe_allow_html=True)
st.write("")
for dim in ASSESSMENT_DIMENSIONS:
    rsn = dim_reasoning.get(dim["id"], "")
    if rsn:
        st.markdown(f"**{dim['icon']} {dim['label']}:** {rsn}")

# ── Verdict ──────────────────────────────────────────────────────────────
st.markdown("### ✅ Verdict")
if hard_gate:
    st.error(f"🚫 Hard Gate Triggered: {hard_gate_reason}")

penalty_note = "&nbsp;· −0.3 ISO High-risk penalty applied" if hard_gate and "High" in hard_gate_reason else ""
gate_note = "&nbsp;· hard gate triggered" if hard_gate else ""

verdict_html = (
    f'<div style="background:{vc["bg"]};border:1.5px solid {vc["color"]};border-radius:14px;'
    f'padding:1.2rem 1.6rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;">'
    f'<div>'
    f'<div style="font-size:0.7rem;color:{vc["color"]};font-weight:700;letter-spacing:0.08em;">OVERALL SCORE {M2_OVERALL_FORMULA_HTML}</div>'
    f'<div style="font-size:1.9rem;font-weight:800;color:{vc["color"]};margin-top:2px;">{overall:.2f}<span style="font-size:1rem;opacity:0.6;"> / 5</span></div>'
    f'<div style="font-size:0.73rem;color:{vc["color"]};margin-top:4px;opacity:0.85;">mean of 6 dimension scores{penalty_note}{gate_note}</div>'
    f'</div>'
    f'<div style="font-size:1rem;font-weight:700;color:{vc["color"]};text-align:right;">'
    f'{vc["icon"]} {verdict}<br>'
    f'<span style="font-size:0.7rem;opacity:0.7;font-weight:400;">≥ 3.5 Feasible &nbsp;·&nbsp; 2.5–3.49 Conditional &nbsp;·&nbsp; &lt; 2.5 Not Feasible</span>'
    f'</div>'
    f'</div>'
)
st.markdown(verdict_html, unsafe_allow_html=True)

# ── Recommendations ──────────────────────────────────────────────────────
st.markdown("### 💡 Recommendations")
rec_col, risk_col = st.columns(2)
with rec_col:
    if result.get("strengths"):
        st.markdown("**✅ Strengths**")
        for s in result["strengths"]:
            st.markdown(f"- {s}")
    if result.get("recommendations"):
        st.markdown("**💡 Recommendations**")
        for r in result["recommendations"]:
            st.markdown(f"- {r}")
with risk_col:
    if result.get("risks"):
        st.markdown("**⚠️ Risks & Gaps**")
        for r in result["risks"]:
            st.markdown(f"- {r}")

assessments = db_load_assessments(problem_id)
if assessments:
    latest = assessments[0]
    with st.expander("Full AI Report", expanded=False):
        st.markdown(latest.get("ai_recommendation", ""))

    df = pd.DataFrame([{
        "Assessment ID": latest["id"], "Problem ID": problem_id,
        "Assessed at": latest["assessed_at"], "Overall Score": latest["overall_score"],
        "Verdict": latest["verdict"],
        **{d["label"]: scores.get(d["id"]) for d in ASSESSMENT_DIMENSIONS},
    }])
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(),
                        f"assessment_{latest['id']}.csv", "text/csv")
st.divider()

col1, col2 = st.columns([4, 1])

with col1:
    if st.button(
        "💾 Save Assessment",
        width = 'stretch'
    ):
        
        strengths = "\n".join(
            f"- {s}"
            for s in result.get("strengths", [])
        )

        risks = "\n".join(
            f"- {r}"
            for r in result.get("risks", [])
        )

        recommendations = "\n".join(
            f"- {r}"
            for r in result.get("recommendations", [])
        )

        dim_reasoning = result.get(
            "dimension_reasoning",
            {}
        )

        reasoning_md = "\n".join(
            f"**{dim['label']}** ({scores.get(dim['id'], 0):.1f}/5): "
            f"{dim_reasoning.get(dim['id'], '')}"
            for dim in ASSESSMENT_DIMENSIONS
        )
        
        ai_report = (

            f"""## AI Planning Context

            Timeline:
            {timeline}

            Owner:
            {owner}

            Why AI:
            {why_ai}

            Data Sensitivity:
            {data_sensitivity}

            ## Overall Assessment

            {result.get("overall_summary","")}

            ## Dimension Breakdown

            {reasoning_md}

            ## Strengths

            {strengths}

            ## Risks & Gaps

            {risks}

            ## Recommendations

            {recommendations}
            """
        )

        rec_id = f"FA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        db_save_assessment({
            "id": rec_id, "problem_id": problem_id,
            "timeline": timeline,

            "owner": owner,

            "why_ai": why_ai,

            "data_sensitivity": data_sensitivity,
            "assessed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "assessor_name": "AI Assessment",
            "ai_suitability_score": scores.get("ai_suitability", 0),
            "economic_viability_score": scores.get("economic_viability", 0),
            "data_readiness_score": scores.get("data_readiness", 0),
            "workflow_maturity_score": scores.get("workflow_maturity", 0),
            "change_management_score": scores.get("change_management", 0),
            "risk_compliance_score": scores.get("risk_compliance", 0),
            "hard_gate_triggered": 1 if result.get("hard_gate_triggered") else 0,
            "hard_gate_reason": result.get("hard_gate_reason", ""),
            "overall_score": overall, "verdict": verdict,
            "ai_recommendation": ai_report,
            "responses": json.dumps(
                result,
                indent=2
            ),
        })
        update_problem_planning_context(
            problem_id,
            timeline,
            owner
        )
        new_status = {"Feasible": "Under Review", "Conditional": "Deferred",
                    "Not Feasible": "Rejected"}.get(verdict, "Under Review")
        db_update_status(problem_id, new_status)
        st.success(
            "Assessment saved successfully."
        )

with col2:
    if st.button(
        "➡ Continue",
        type="primary",
        width='stretch',
    ):
        st.switch_page("pages/3_Gain_Pain_Analysis.py")
