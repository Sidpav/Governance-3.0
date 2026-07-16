# pages/1_Idea_Submission.py
# ─────────────────────────────────────────────────────────────────────────
# Idea Submission v3 — Figma "Cortexa" flow rework (replaces the v2 stepper
# flow). Implements, in order:
#
#   1. intake     Business Problem text + optional Supporting Files upload
#   2. duplicate  AI-driven duplicate detection against saved projects
#                 (skipped automatically if no close match is found)
#   3. gaps       Cross-document Gaps / Discrepancies, each with an
#                 editable AI-suggested resolution (skipped if no gaps,
#                 e.g. fewer than 2 documents)
#   4. value      One tailored, quantifiable Business Value Clarification
#                 question
#   5. engines    Decision Support Systems Required — AI proposes 4-5
#                 discrete decision-support engines, each Approve/Ignore
#   6. review     Review & Approval — Approve generates + saves the final
#                 proposal; Edit shows "coming soon" (matches reference)
#   7. done       Proposal Generated Successfully + View Proposal (dialog)
#
# Document extraction / autocapture / contradiction-detection groundwork
# from v2 is reused as-is (document_intel/*, llm/idea_intake.py's existing
# functions) — only the page-level flow and the new llm/idea_intake.py
# additions (find_similar_problem, detect_gaps, generate_business_value_
# question, propose_decision_engines) are new.
# ─────────────────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access

from document_intel.extractors import SUPPORTED_EXTENSIONS
from document_intel.context_builder import extract_all, build_unified_context, documents_summary

from llm.idea_intake import (
    autocapture_fields,
    find_similar_problem,
    detect_gaps,
    generate_business_value_question,
    propose_decision_engines,
)

from database.problem_repository import new_draft_id, save_problem_v2
from database.db import (
    db_load_all, db_save_uploaded_documents,
    db_save_decision_proposal, db_load_decision_proposal,
)

st.set_page_config(page_title="Idea Submission — AI Governance Platform",
                    page_icon="💡", layout="wide", initial_sidebar_state="expanded")

require_login()

apply_theme()
render_sidebar("idea_submission")
render_navbar("idea_submission")
require_access("idea_submission")
render_breadcrumb("AI Use-Case Portfolio", "Use-case Intake")

st.title("Use-case Intake")
st.caption("Describe your business problem clearly. The system will search for similar prior projects.")

st.markdown("""
<style>
/* Page-level Figma treatment for the Use-case Intake workflow. */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.cx-intake-definition),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.cx-intake-upload) {
    background: #FFFFFF !important;
    border: 1px solid #D9E2F0 !important;
    border-radius: 10px !important;
    padding: 8px !important;
    box-shadow: none !important;
}
.cx-intake-section-title {
    color: #31415F;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: .055em;
    margin: 2px 0 14px;
}
div[data-testid="stVerticalBlock"]:has(.cx-intake-definition) textarea {
    min-height: 240px !important;
    background: #F8FAFD !important;
    border: 1px solid #D9E2F0 !important;
    border-radius: 7px !important;
    color: #10203E !important;
    font-size: 1rem !important;
    line-height: 1.55 !important;
    padding: 18px !important;
}
div[data-testid="stVerticalBlock"]:has(.cx-intake-definition) textarea::placeholder {
    color: #8EA2C3 !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state scaffolding ───────────────────────────────────────────────
ss = st.session_state
ss.setdefault("m1_stage", "intake")
ss.setdefault("m1_stage_stack", [])          # for Back navigation
ss.setdefault("m1_draft_id", None)
ss.setdefault("m1_documents", [])
ss.setdefault("m1_unified_context", "")
ss.setdefault("m1_fields", {})               # problem_statement, business_objective, workflow_location, business_value
ss.setdefault("m1_duplicate", None)
ss.setdefault("m1_duplicate_choice", None)   # "new" | "existing"
ss.setdefault("m1_gaps", None)
ss.setdefault("m1_value_question", "")
ss.setdefault("m1_engines_result", None)     # {"rationale":..., "engines":[...]}
ss.setdefault("m1_engine_states", {})        # idx -> "approved" | "ignored"
ss.setdefault("m1_show_reasoning", False)
ss.setdefault("m1_saved_record_id", None)
ss.setdefault("m1_proposal", None)

ENGINE_COLORS = [
    {"bar": "#3B82F6", "bg": "#EFF6FF", "badge": "#3B82F6"},   # blue
    {"bar": "#A855F7", "bg": "#FAF5FF", "badge": "#A855F7"},   # purple
    {"bar": "#F59E0B", "bg": "#FFFBEB", "badge": "#F59E0B"},   # orange
    {"bar": "#10B981", "bg": "#ECFDF5", "badge": "#10B981"},   # green
    {"bar": "#E11D48", "bg": "#FFF1F2", "badge": "#E11D48"},   # red
]


def goto(stage: str, push: bool = True):
    if push and ss.m1_stage != stage:
        ss.m1_stage_stack.append(ss.m1_stage)
    ss.m1_stage = stage
    st.rerun()


def go_back(fallback: str = "intake"):
    prev = ss.m1_stage_stack.pop() if ss.m1_stage_stack else fallback
    ss.m1_stage = prev
    st.rerun()


def restart():
    for k in list(ss.keys()):
        if k.startswith("m1_"):
            del ss[k]
    st.rerun()


@st.dialog("Business Proposal", width="large")
def proposal_dialog():
    p = ss.m1_proposal
    if not p:
        st.info("No proposal available yet.")
        return

    st.markdown(f"#### {p.get('title', '')}")
    badges = (
        f"<span style='background:#D1F5EA;color:#1D9E75;padding:3px 12px;border-radius:14px;"
        f"font-size:0.78rem;font-weight:700;margin-right:6px;'>{p.get('status','Approved')}</span>"
        f"<span style='background:#E0E9FF;color:#3B5BDB;padding:3px 12px;border-radius:14px;"
        f"font-size:0.78rem;font-weight:700;margin-right:6px;'>{p.get('business_unit','') or 'Unspecified'}</span>"
        f"<span style='background:#F3E8FF;color:#9333EA;padding:3px 12px;border-radius:14px;"
        f"font-size:0.78rem;font-weight:700;margin-right:6px;'>AI Decision Support</span>"
        f"<span style='color:#888;font-size:0.78rem;'>🕒 Generated {p.get('generated_at','')}</span>"
    )
    st.markdown(badges, unsafe_allow_html=True)
    st.write("")

    st.markdown("**Problem Statement**")
    st.write(p.get("problem_statement", ""))
    st.markdown("**Business Objective**")
    st.write(p.get("business_objective", ""))
    if p.get("business_value"):
        st.markdown("**Business Value**")
        st.write(p.get("business_value", ""))

    st.markdown("**Decision Support System Architecture**")
    for i, eng in enumerate(p.get("engines", [])):
        c = ENGINE_COLORS[i % len(ENGINE_COLORS)]
        st.markdown(f"""
        <div style="border:1.5px solid {c['bar']}55;border-left:4px solid {c['bar']};
                    border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.5rem;background:{c['bg']};">
          <div style="display:flex;align-items:flex-start;gap:10px;">
            <div style="background:{c['badge']};color:white;width:22px;height:22px;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;font-size:0.75rem;
                        font-weight:800;flex-shrink:0;margin-top:2px;">{i+1}</div>
            <div>
              <div style="font-weight:700;font-size:0.92rem;color:#1a1a2e;">{eng.get('title','')}</div>
              <div style="font-size:0.83rem;color:#555;margin-top:2px;">{eng.get('description','')}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.write("")
    if st.button("Close", type="primary", width='stretch'):
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1 — Intake (business problem + supporting files)
# ═══════════════════════════════════════════════════════════════════════════
if ss.m1_stage == "intake":
    with st.container(border=True):
        st.markdown('<span class="cx-intake-definition"></span>', unsafe_allow_html=True)
        st.markdown('<div class="cx-intake-section-title">USE-CASE DEFINITION</div>', unsafe_allow_html=True)
        user_text = st.text_area(
            "Business problem", value=ss.m1_fields.get("_user_text", ""),
            height=240, label_visibility="collapsed",
            placeholder="Describe the business problem you are trying to solve...",
        )

    with st.container(border=True):
        st.markdown('<span class="cx-intake-upload"></span>', unsafe_allow_html=True)
        st.markdown('<div class="cx-intake-section-title">SUPPORTING FILES</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            f"Upload PDF, DOCX, PPT, or video transcript ({', '.join(e.upper() for e in SUPPORTED_EXTENSIONS)})",
            type=SUPPORTED_EXTENSIONS, accept_multiple_files=True,
            label_visibility="collapsed",
        )

    st.write("")
    _, col_btn = st.columns([4, 1])
    with col_btn:
        proceed = st.button("Proceed →", type="primary", width='stretch')

    if proceed:
        if not user_text.strip() and not uploaded_files:
            st.warning("Please provide a description or upload at least one document.")
            st.stop()

        ss.m1_fields["_user_text"] = user_text
        ss.m1_draft_id = ss.m1_draft_id or new_draft_id()

        if uploaded_files:
            with st.spinner("Extracting content from uploaded documents…"):
                ss.m1_documents = extract_all(uploaded_files)
        else:
            ss.m1_documents = []

        ss.m1_unified_context = build_unified_context(user_text, ss.m1_documents)

        with st.spinner("Searching DB for similar projects…"):
            ss.m1_duplicate = find_similar_problem(ss.m1_unified_context, db_load_all())

        with st.spinner("AI is identifying the problem statement and business objective…"):
            autocapture = autocapture_fields(ss.m1_unified_context)
        ss.m1_fields["problem_statement"] = autocapture.get("problem_statement", "")
        ss.m1_fields["business_objective"] = autocapture.get("business_objective", "")
        ss.m1_fields["workflow_location"] = autocapture.get("workflow_location", "")

        if ss.m1_duplicate.get("found"):
            goto("duplicate")
        else:
            goto("gaps")

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2 — Similar Project Found
# ═══════════════════════════════════════════════════════════════════════════
elif ss.m1_stage == "duplicate":
    dup = ss.m1_duplicate or {}
    with st.container(border=True):
        st.markdown("⚠️ **:orange[SIMILAR PROJECT FOUND]**")
        col_l, col_r = st.columns(2)
        with col_l:
            st.caption("Project ID")
            st.markdown(f"**{dup.get('project_id','—')}**")
            st.write("")
            st.caption("Title")
            st.markdown(f"**{dup.get('title','—')}**")
        with col_r:
            st.caption("Status")
            st.markdown(
                f"<span style='background:#D1F5EA;color:#1D9E75;padding:2px 12px;border-radius:14px;"
                f"font-size:0.8rem;font-weight:700;'>{dup.get('status','Unknown')}</span>",
                unsafe_allow_html=True)
            st.write("")
            st.caption("Business Unit")
            st.markdown(f"**{dup.get('business_unit','—')}**")
        if dup.get("reason"):
            st.caption(dup["reason"])

    with st.container(border=True):
        st.markdown("**A similar problem appears to have been solved earlier. Do you still want to submit this as a new idea?**")
        choice = st.radio(
            "Choice", ["Yes, submit as a new idea", "No, refer to the existing project"],
            label_visibility="collapsed", key="m1_dup_radio",
        )

        justification = ""
        if choice.startswith("Yes"):
            st.markdown("**PLEASE EXPLAIN WHY A NEW SUBMISSION IS WARRANTED**")
            justification = st.text_area(
                "Justification", height=110, label_visibility="collapsed",
                placeholder="Enter your justification here...", key="m1_dup_justification",
            )

    st.write("")
    col_back, _, col_btn = st.columns([1, 3, 1])
    with col_back:
        if st.button("← Back", width='stretch'):
            go_back("intake")
    with col_btn:
        if choice.startswith("Yes"):
            if st.button("Approve & Proceed →", type="primary", width='stretch'):
                if not justification.strip():
                    st.warning("Please explain why a new submission is warranted.")
                    st.stop()
                ss.m1_fields["duplicate_justification"] = justification.strip()
                goto("gaps")
        else:
            st.button("Approve & Proceed →", type="primary", width='stretch', disabled=True)

    if not choice.startswith("Yes"):
        st.info(f"This idea has been matched to existing project **{dup.get('project_id','—')}**. "
                f"You can review it in Use-case Scoring & Prioritization or Portfolio Dashboard, or start a new submission.")
        if st.button("Start over"):
            restart()

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3 — Gaps / Discrepancies Found
# ═══════════════════════════════════════════════════════════════════════════
elif ss.m1_stage == "gaps":
    if ss.m1_gaps is None:
        doc_only_context = build_unified_context("", ss.m1_documents)
        if len(ss.m1_documents) < 2 or not doc_only_context.strip():
            ss.m1_gaps = {"gaps": []}
        else:
            with st.spinner("Checking uploaded documents for gaps and discrepancies…"):
                ss.m1_gaps = detect_gaps(doc_only_context)

    gaps = ss.m1_gaps.get("gaps", [])

    if not gaps:
        # Nothing to resolve — skip straight through automatically.
        goto("value")
    else:
        with st.container(border=True):
            st.markdown("⚠️ **Gaps / Discrepancies Found**")
            st.write("")
            for i, g in enumerate(gaps, start=1):
                st.markdown(f"""
                <div style="background:#FFF8E8;border:1px solid #F4D58D;border-radius:10px;
                            padding:0.8rem 1.1rem;margin-bottom:0;">
                  <div style="font-size:0.78rem;color:#B8860B;font-weight:700;">Gap {i}</div>
                  <div style="font-size:0.88rem;color:#1a1a2e;margin-top:2px;">{g.get('description','')}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<div style='font-size:0.78rem;color:#1D9E75;font-weight:700;margin:6px 0 2px 2px;'>Resolution (editable)</div>", unsafe_allow_html=True)
                g["resolution"] = st.text_area(
                    f"Resolution {i}", value=g.get("resolution", ""), height=80,
                    label_visibility="collapsed", key=f"m1_gap_resolution_{i}",
                )
                st.write("")

        st.write("")
        col_back, _, col_btn = st.columns([1, 3, 1])
        with col_back:
            if st.button("← Back", width='stretch'):
                go_back("intake")
        with col_btn:
            if st.button("Approve & Proceed →", type="primary", width='stretch'):
                ss.m1_fields["gap_resolutions"] = [g.get("resolution", "") for g in gaps]
                goto("value")

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 4 — Business Value Clarification
# ═══════════════════════════════════════════════════════════════════════════
elif ss.m1_stage == "value":
    if not ss.m1_value_question:
        with st.spinner("Preparing your business value question…"):
            ss.m1_value_question = generate_business_value_question(ss.m1_fields)

    with st.container(border=True):
        st.markdown("📊 **Business Value Clarification**")
        st.write(ss.m1_value_question)
        business_value = st.text_area(
            "Business value", value=ss.m1_fields.get("business_value", ""),
            height=110, label_visibility="collapsed",
            placeholder="Enter your business value estimate here...",
        )

    st.write("")
    col_back, _, col_btn = st.columns([1, 3, 1])
    with col_back:
        if st.button("← Back", width='stretch'):
            go_back("intake")
    with col_btn:
        if st.button("Approve & Proceed →", type="primary", width='stretch'):
            if not business_value.strip():
                st.warning("Please provide a business value estimate.")
                st.stop()
            ss.m1_fields["business_value"] = business_value.strip()
            goto("engines")

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 5 — Decision Support Systems Required
# ═══════════════════════════════════════════════════════════════════════════
elif ss.m1_stage == "engines":
    if ss.m1_engines_result is None:
        with st.spinner("Designing the decision support system…"):
            ss.m1_engines_result = propose_decision_engines(ss.m1_fields)
        ss.m1_engine_states = {}

    engines = ss.m1_engines_result.get("engines", [])

    with st.container(border=True):
        col_title, col_reason = st.columns([5, 1])
        with col_title:
            st.markdown("🔗 **Decision Support Systems Required**")
            st.caption("Review each engine and approve or ignore it for this proposal.")
        with col_reason:
            if st.button("🧠 Reasoning", width='stretch'):
                ss.m1_show_reasoning = not ss.m1_show_reasoning

        if ss.m1_show_reasoning and ss.m1_engines_result.get("rationale"):
            st.info(ss.m1_engines_result["rationale"])

        st.write("")
        for i, eng in enumerate(engines):
            c = ENGINE_COLORS[i % len(ENGINE_COLORS)]
            state = ss.m1_engine_states.get(i)
            st.markdown(f"""
            <div style="border:1.5px solid {c['bar']}55;border-left:4px solid {c['bar']};
                        border-radius:10px;padding:0.8rem 1.1rem;background:{c['bg']};margin-bottom:0;">
              <div style="display:flex;align-items:flex-start;gap:10px;">
                <div style="background:{c['badge']};color:white;width:24px;height:24px;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;font-size:0.8rem;
                            font-weight:800;flex-shrink:0;">{i+1}</div>
                <div>
                  <div style="font-weight:700;font-size:0.95rem;color:#1a1a2e;">{eng.get('title','')}</div>
                  <div style="font-size:0.84rem;color:#555;margin-top:2px;">{eng.get('description','')}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            if state == "approved":
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown("<span style='color:#1D9E75;font-weight:700;'>✅ Approved</span>", unsafe_allow_html=True)
                with col_b:
                    if st.button("undo", key=f"undo_{i}"):
                        ss.m1_engine_states[i] = None
                        st.rerun()
            elif state == "ignored":
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown("<span style='color:#999;font-weight:700;'>✕ Ignored</span>", unsafe_allow_html=True)
                with col_b:
                    if st.button("undo", key=f"undo_{i}"):
                        ss.m1_engine_states[i] = None
                        st.rerun()
            else:
                col_a, col_b, _ = st.columns([1, 1, 3])
                with col_a:
                    if st.button("✓ Approve", key=f"approve_{i}", type="primary"):
                        ss.m1_engine_states[i] = "approved"
                        st.rerun()
                with col_b:
                    if st.button("✕ Ignore", key=f"ignore_{i}"):
                        ss.m1_engine_states[i] = "ignored"
                        st.rerun()
            st.write("")

    st.write("")
    col_back, _, col_btn = st.columns([1, 3, 1])
    with col_back:
        if st.button("← Back", width='stretch'):
            go_back("value")
    with col_btn:
        all_reviewed = engines and all(ss.m1_engine_states.get(i) for i in range(len(engines)))
        if st.button("Approve & Proceed →", type="primary", width='stretch', disabled=not all_reviewed):
            goto("review")
        if not all_reviewed:
            st.caption("Approve or ignore every engine to continue.")

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 6 — Review & Approval
# ═══════════════════════════════════════════════════════════════════════════
elif ss.m1_stage == "review":
    with st.container(border=True):
        st.markdown("✅ **Review & Approval**")
        st.write("The proposal has been prepared. Do you approve or would you like to edit?")
        col_approve, col_edit = st.columns([1, 1])
        with col_approve:
            approve_clicked = st.button("✓ Approve", type="primary", width='stretch')
        with col_edit:
            edit_clicked = st.button("✎ Edit", width='stretch')

        if edit_clicked:
            st.info("Edit mode coming soon. Please contact your project manager to request changes.")

        if approve_clicked:
            engines = ss.m1_engines_result.get("engines", [])
            approved_engines = [e for i, e in enumerate(engines) if ss.m1_engine_states.get(i) == "approved"]

            problem_title = (ss.m1_fields.get("problem_statement", "") or "Untitled Problem")[:90]
            proposal = {
                "title": f"{problem_title} — Decision Support System",
                "problem_statement": ss.m1_fields.get("problem_statement", ""),
                "business_objective": ss.m1_fields.get("business_objective", ""),
                "business_value": ss.m1_fields.get("business_value", ""),
                "business_unit": ss.m1_fields.get("workflow_location", ""),
                "status": "Approved",
                "engines": approved_engines,
                "generated_at": datetime.now().strftime("%d/%m/%Y"),
            }

            with st.spinner("Generating Business Proposal…"):
                record_id = save_problem_v2({
                    "problem_statement": proposal["problem_statement"],
                    "business_objective": proposal["business_objective"],
                    "business_value": proposal["business_value"],
                    "workflow_location": proposal["business_unit"],
                    "decision_support": "; ".join(e.get("title", "") for e in approved_engines),
                    "proposed_solution": proposal["title"],
                }, record_id=ss.m1_draft_id)

                if ss.m1_documents:
                    db_save_uploaded_documents(record_id, ss.m1_documents)

                db_save_decision_proposal(record_id, proposal)

            ss.m1_saved_record_id = record_id
            ss.m1_proposal = proposal
            goto("done")

    st.write("")
    if st.button("← Back"):
        go_back("engines")

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 7 — Proposal Generated Successfully
# ═══════════════════════════════════════════════════════════════════════════
elif ss.m1_stage == "done":
    if ss.m1_proposal is None and ss.m1_saved_record_id:
        loaded = db_load_decision_proposal(ss.m1_saved_record_id)
        if loaded:
            ss.m1_proposal = loaded

    with st.container(border=True):
        col_icon, col_text, col_btn = st.columns([0.5, 5, 1.5])
        with col_icon:
            st.markdown("<div style='font-size:1.6rem;'>✅</div>", unsafe_allow_html=True)
        with col_text:
            st.markdown("<span style='color:#1D9E75;font-weight:700;font-size:1.05rem;'>Proposal Generated Successfully</span>",
                        unsafe_allow_html=True)
            st.caption(f"Your business proposal document is ready · saved as **{ss.m1_saved_record_id}**")
        with col_btn:
            if st.button("View Proposal", type="primary", width='stretch'):
                proposal_dialog()

    st.write("")
    st.success("You can track this idea in Use-case Scoring & Prioritization or Portfolio Dashboard.")
    if st.button("Submit another idea"):
        restart()
