# pages/4_Governance_Review.py
#
# MODULE 4 — Governance Review (Committee Decision).
# Taken ENTIRELY from Friend's Project per the merge spec: "No changes" to
# UI, flow, decision controls, or the Recent Decisions table. The only
# edit versus Friend's original file is mechanical — the repeated CSS +
# sidebar block at the top is now the shared apply_theme()/render_sidebar()
# (see ui/theme.py, ui/sidebar.py) instead of being pasted in again, and
# behind get_problems()/get_problem_by_id()/get_feasibility_by_problem()/
# get_gain_pain_by_problem()/save_decision()/get_decisions() now sits a
# unified canonical database — see the database/*_repository.py adapters.

import streamlit as st
import pandas as pd
from datetime import datetime

from database.feasibility_repository import (
    get_problems,
    get_problem_by_id,
    get_feasibility_by_problem
)

from database.gain_pain_repository import (
    get_gain_pain_by_problem
)

from database.governance_repository import (
    save_decision,
    get_decisions
)
from database.db import db_load_assessments

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access

st.set_page_config(page_title="AI Governance Platform", page_icon="🤖",
                    layout="wide", initial_sidebar_state="expanded")

require_login()

apply_theme()
render_sidebar("m4")
render_navbar("m4")
current_user = require_access("m4")
render_breadcrumb("AI Use-Case Portfolio", "Portfolio Gate Review")

# =====================================
# PAGE TITLE
# =====================================

st.title("Portfolio Gate Review")

problems = get_problems()

if not problems:
    st.warning("No opportunities available.")
    st.stop()

problem_dict = {row[1]: row[0] for row in problems}

options = ["-- Select Opportunity --"] + list(problem_dict.keys())

requested_problem_id = st.session_state.pop("gate_review_problem_id", None)
requested_label = next(
    (label for label, record_id in problem_dict.items() if record_id == requested_problem_id),
    None,
)
default_index = options.index(requested_label) if requested_label in options else 0
selected_problem = st.selectbox("Select Opportunity", options, index=default_index)

if selected_problem == "-- Select Opportunity --":
    st.info("Select an opportunity.")
    st.stop()

problem_id = problem_dict[selected_problem]

problem = get_problem_by_id(problem_id)

st.subheader("Problem Summary")

st.info(problem[1])

col1, col2 = st.columns(2)

with col1:
    st.write("**Business Objective**")
    st.write(problem[2])

    st.write("**Proposed Solution**")
    st.write(problem[3])

with col2:
    st.write("**Timeline**")
    st.write(problem[4])

    st.write("**Owner**")
    st.write(problem[5])

st.divider()

feasibility = get_feasibility_by_problem(problem_id)
assessment_rows = db_load_assessments(problem_id)
latest_assessment = assessment_rows[0] if assessment_rows else None

st.subheader("Use-case Scoring & Prioritization")

if feasibility:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("AI Suitability", feasibility[2])

    with c2:
        st.metric("Economic Viability", feasibility[3])

    with c3:
        st.metric("Data Readiness", feasibility[4])

    with c4:
        st.metric("Technology", feasibility[5])

else:
    st.warning("No feasibility assessment found.")

st.divider()

gain_pain = get_gain_pain_by_problem(problem_id)

st.subheader("Value-Risk Assessment")

if gain_pain:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Gain Score", gain_pain[12])

    with c2:
        st.metric("Pain Score", gain_pain[13])

    with c3:
        st.metric("Priority Score", gain_pain[14])

else:
    st.warning("No gain-pain analysis found.")

st.divider()

st.subheader("Governance Decision")

can_record_decision = current_user.get("role") != "business_leader"
if not can_record_decision:
    st.info(
        "You can review this governance gate, but an independent Program Leader "
        "must record the decision. Sign in as programleader@cortexa.com to approve "
        "the project for AI Product Delivery."
    )

status = st.selectbox(
    "Decision",
    ["Pending Review", "Approved", "Conditionally Approved", "Deferred", "Rejected"],
    disabled=not can_record_decision,
)

reviewer = current_user["email"]
st.caption(f"Authenticated reviewer: {reviewer}")

comments = st.text_area("Comments", disabled=not can_record_decision)

if st.button("Save Decision", width='stretch', disabled=not can_record_decision):
    blocked = not feasibility or not gain_pain
    hard_gate = bool(latest_assessment and latest_assessment.get("hard_gate_triggered"))
    if blocked:
        st.error("Complete both Feasibility and Value–Risk assessments before recording a decision.")
    elif status in {"Approved", "Conditionally Approved"} and hard_gate:
        st.error("Approval is blocked because the latest feasibility assessment triggered a hard gate.")
    elif status != "Pending Review" and not comments.strip():
        st.error("A decision rationale is required.")
    else:
        save_decision({
        "problem_id": problem_id,
        "status": status,
        "reviewer": reviewer,
        "comments": comments,
        "decision_date": str(datetime.now())
        })
        st.session_state["decision_saved"] = True
        st.rerun()


if st.session_state.get("decision_saved", False):
    st.success("Decision saved.")
    st.session_state["decision_saved"] = False


st.divider()

st.subheader("Recent Decisions")

decisions = get_decisions()

if decisions:
    df = pd.DataFrame(
        decisions,
        columns=["ID", "Problem ID", "Status", "Reviewer", "Comments", "Date"]
    )

    st.dataframe(df, width='stretch')
