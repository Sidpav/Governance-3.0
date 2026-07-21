# pages/6_Expert_Advice.py
#
# Expert Advice workflow:
# - Assessment users submit feedback against a completed Gain-Pain analysis.
# - Governance reviewers see only problems with pending expert-review requests.

import streamlit as st
import pandas as pd

from config.constants import GAIN_DIMENSIONS, PAIN_DIMENSIONS
from database.db import (
    db_get_problem,
    db_load_gainpain,
    db_get_gainpain,
    db_save_expert_review_request,
    db_load_expert_review_requests,
    db_mark_expert_review_reviewed,
    db_apply_expert_overrides,
    db_load_audit,
)
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access


st.set_page_config(
    page_title="AI Governance Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_login()

apply_theme()
render_sidebar("m6")
render_navbar("m6")
user = require_access("m6")
render_breadcrumb("AI Strategy & Use-Case Portfolio", "Expert Advice")

st.title("Expert Advice")

all_gp = db_load_gainpain()
analysed_problem_ids = sorted({g["problem_id"] for g in all_gp})

if not analysed_problem_ids:
    st.warning("No Value-Risk analyses found yet. Complete **Value-Risk Assessment** first.")
    st.stop()

id_to_label = {
    pid: (db_get_problem(pid) or {}).get("problem_statement", pid)
    for pid in analysed_problem_ids
}

prefill_pid = st.session_state.pop("expert_review_problem_id", None)
prefill_gainpain_id = st.session_state.pop("expert_review_gainpain_id", None)
is_governance_reviewer = user.get("role") in {
    "business_sponsor", "program_leader"
}
show_feedback_form = bool(prefill_pid) or not is_governance_reviewer


def _problem_label(pid: str) -> str:
    return f"{id_to_label.get(pid, pid)[:90]}  ({pid})"


def _latest_gainpain(problem_id: str, gainpain_id: str | None = None) -> dict | None:
    if gainpain_id:
        gp = db_get_gainpain(gainpain_id)
        if gp:
            return gp

    rows = db_load_gainpain(problem_id)
    return rows[0] if rows else None


def render_feedback_form():
    st.caption("Submit feedback on a completed Gain-Pain analysis.")
    st.markdown("### Submit Feedback")

    options = list(id_to_label.keys())
    default_index = options.index(prefill_pid) if prefill_pid in options else 0

    sel_pid = st.selectbox(
        "Problem",
        options,
        index=default_index,
        format_func=_problem_label,
        key="user_feedback_pid",
    )

    latest_gp = _latest_gainpain(
        sel_pid,
        prefill_gainpain_id if sel_pid == prefill_pid else None,
    )

    if not latest_gp:
        st.warning("No Gain-Pain analysis was found for this problem.")
        return

    with st.container(border=True):
        st.write("**Problem Statement**")
        st.info(id_to_label[sel_pid])
        c1, c2, c3 = st.columns(3)
        c1.metric("Gain Score", f"{latest_gp['avg_gains']:.2f}")
        c2.metric("Pain Score", f"{latest_gp['avg_pains']:.2f}")
        c3.metric("Priority Score", f"{latest_gp['priority_score_scaled']:.1f}/10")

    query_type = st.radio(
        "What would you like to raise?",
        ["Query", "Suggestion", "Concern", "Explanation"],
        horizontal=True,
    )
    query_text = st.text_area(
        "Details",
        placeholder='e.g. "I believe implementation cost should be lower."',
        height=120,
    )

    if st.button("Submit", type="primary"):
        if not query_text.strip():
            st.warning("Please enter a query, suggestion, concern, or explanation before submitting.")
        else:
            db_save_expert_review_request({
                "problem_id": sel_pid,
                "gainpain_id": latest_gp["id"],
                "query_type": query_type,
                "query_text": query_text.strip(),
            })
            st.success("your idea has been sent for expert review")

    st.divider()
    st.markdown("##### Your previously submitted feedback for this problem")
    history = db_load_expert_review_requests(sel_pid)
    if history:
        st.dataframe(
            pd.DataFrame(history)[["submitted_at", "query_type", "query_text", "status"]]
            .rename(columns={
                "submitted_at": "Submitted",
                "query_type": "Type",
                "query_text": "Details",
                "status": "Status",
            }),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("No feedback submitted yet for this problem.")


def render_expert_review_panel():
    st.caption("Governance Board review panel for pending expert-review requests.")
    st.markdown("### Expert Review Panel")

    all_requests = db_load_expert_review_requests()
    pending_requests = [r for r in all_requests if r.get("status") == "Pending"]
    pending_problem_ids = []
    seen = set()
    for req in pending_requests:
        pid = req["problem_id"]
        if pid in id_to_label and pid not in seen:
            pending_problem_ids.append(pid)
            seen.add(pid)

    if not pending_problem_ids:
        st.info("No problems are currently pending expert review.")
        return

    exp_pid = st.selectbox(
        "Problem",
        pending_problem_ids,
        format_func=_problem_label,
        key="expert_review_pid",
    )

    problem_pending = [r for r in pending_requests if r["problem_id"] == exp_pid]
    requested_gainpain_id = problem_pending[0].get("gainpain_id") if problem_pending else None
    gp = _latest_gainpain(exp_pid, requested_gainpain_id)
    problem = db_get_problem(exp_pid) or {}

    if not gp:
        st.warning("No Gain-Pain analysis was found for this pending request.")
        return

    st.write("**Problem Statement**")
    st.info(problem.get("problem_statement", id_to_label.get(exp_pid, "")))

    m1, m2, m3 = st.columns(3)
    m1.metric("Gain Score", f"{gp['avg_gains']:.2f}")
    m2.metric("Pain Score", f"{gp['avg_pains']:.2f}")
    m3.metric("Priority Score", f"{gp['priority_score_scaled']:.1f}/10  ({gp['priority_band']})")

    st.markdown("**User Feedback**")
    for req in problem_pending:
        st.markdown(
            f"- *{req['query_type']}* - {req['query_text']}  \n"
            f"  <span style='font-size:0.75rem;color:#888;'>submitted {req['submitted_at']}</span>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("##### Adjust Gain-Pain Dimensions")

    col_g, col_p = st.columns(2)
    new_values = {}
    with col_g:
        st.markdown("**Gains**")
        for d in GAIN_DIMENSIONS:
            new_values[d["id"]] = st.slider(
                d["label"],
                1.0,
                5.0,
                float(gp.get(d["id"]) or 1.0),
                0.5,
                key=f"expert_{exp_pid}_{d['id']}",
            )
    with col_p:
        st.markdown("**Pains**")
        for d in PAIN_DIMENSIONS:
            new_values[d["id"]] = st.slider(
                d["label"],
                1.0,
                5.0,
                float(gp.get(d["id"]) or 1.0),
                0.5,
                key=f"expert_{exp_pid}_{d['id']}",
            )

    expert_name = user["email"]
    st.caption(f"Reviewer: {expert_name}")
    reason = st.text_area("Reason for adjustment", height=90, key=f"expert_reason_{exp_pid}")

    if st.button("Save", type="primary"):
        if not reason.strip():
            st.warning("Please provide a reason for the adjustment. It is recorded in the audit trail.")
        else:
            updated = db_apply_expert_overrides(gp["id"], new_values, expert_name, reason.strip())
            if updated:
                for req in problem_pending:
                    db_mark_expert_review_reviewed(req["id"])
                st.success(
                    f"Saved. Priority Score recomputed to {updated['priority_score_scaled']:.1f}/10 "
                    f"({updated['priority_band']})."
                )
                st.rerun()

    st.divider()
    st.markdown("##### Audit Trail")
    audit_rows = [a for a in db_load_audit(exp_pid) if a["action_type"] == "expert_gainpain_override"]
    if audit_rows:
        st.dataframe(
            pd.DataFrame(audit_rows)[["timestamp", "field_name", "old_value", "new_value", "user_name", "reason"]]
            .rename(columns={
                "timestamp": "Timestamp",
                "field_name": "Field",
                "old_value": "Old Value",
                "new_value": "Expert Value",
                "user_name": "Expert Name",
                "reason": "Reason",
            }),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("No expert adjustments recorded yet for this problem.")


if show_feedback_form:
    render_feedback_form()
else:
    render_expert_review_panel()
