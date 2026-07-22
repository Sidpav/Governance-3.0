from datetime import date

import streamlit as st

from database.data_repository import load_data_review
from database.delivery_repository import save_execution_decision
from database.infrastructure_repository import load_infrastructure_output, load_infrastructure_review
from database.project_execution_repository import (
    get_approved_projects,
    load_delivery_gate,
    load_responsibility,
    load_workflow,
    save_delivery_gate,
)
from ui.auth import require_access, require_login
from ui.navbar import render_breadcrumb, render_navbar
from ui.sidebar import render_sidebar
from ui.theme import apply_theme
from utils.pdf_generator import generate_execution_report


st.set_page_config(page_title="Delivery Gate Review", page_icon="✅", layout="wide")
user = require_login()
apply_theme()
render_sidebar("pe_execution_approval")
render_navbar("pe_execution_approval")
require_access("pe_execution_approval")
render_breadcrumb("AI Delivery & Operational Readiness", "Delivery Gate Review")

st.markdown(
    """
    <style>
    section.main > div.block-container{padding-top:0!important}.cx-breadcrumb{display:none!important}
    .gate-label{font-size:.78rem;font-weight:800;letter-spacing:.06em;color:#627695;margin:15px 0 5px}.gate-help{font-size:.84rem;color:#8ea2c3;margin:-2px 0 14px}
    div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff!important;border-color:#d9e2f0!important;padding:3px!important}
    div[data-testid="stVerticalBlockBorderWrapper"]>div{padding:8px 12px!important}
    .gate-title{font-size:1.14rem;font-weight:800;color:#10203e;margin:2px 0 9px}
    .gate-head{color:#526a90;font-size:.94rem;font-weight:800;padding:7px 2px;border-bottom:1px solid #d9e2f0}
    .gate-area{color:#10203e;font-size:.94rem;font-weight:800;padding:5px 2px}.gate-row{display:none}
    div[data-testid="stHorizontalBlock"]:has(.gate-row){align-items:center;border-bottom:1px solid #e7edf6;padding:4px 0;min-height:58px;gap:.8rem}
    div[data-testid="stHorizontalBlock"]:has(.gate-row) [data-testid="stVerticalBlock"]{gap:0!important}
    div[data-testid="stHorizontalBlock"]:has(.gate-row) [data-testid="stElementContainer"]{margin:0!important}
    div[data-testid="stHorizontalBlock"]:has(.gate-row) [data-testid="stTextInput"] input,div[data-testid="stHorizontalBlock"]:has(.gate-row) [data-testid="stSelectbox"]>div>div{height:42px!important;min-height:42px!important}
    [data-testid="stSelectbox"] p{white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important;max-width:none!important}
    .gate-actions{display:none}div[data-testid="stHorizontalBlock"]:has(.gate-actions){margin:15px 0 18px;gap:12px;align-items:center}
    div[data-testid="stHorizontalBlock"]:has(.gate-actions) .stButton>button,div[data-testid="stHorizontalBlock"]:has(.gate-actions) .stDownloadButton>button{min-height:48px!important;white-space:normal!important;font-weight:800!important}
    div[data-testid="column"]:has(.gate-proceed) .stButton>button{background:#00a36c!important;border-color:#00a36c!important;color:#fff!important}
    div[data-testid="column"]:has(.gate-revision) .stButton>button{background:#fff!important;border-color:#ffb300!important;color:#b44b00!important}
    div[data-testid="column"]:has(.gate-committee) .stButton>button{background:#fff!important;border-color:#8bb4ff!important;color:#155eef!important}
    .gate-proceed,.gate-revision,.gate-committee,.gate-report{display:none}
    .approval-marker{display:none}div[data-testid="stHorizontalBlock"]:has(.approval-marker){align-items:center;border-bottom:1px solid #e7edf6;padding:5px 0;min-height:55px}
    div[data-testid="stHorizontalBlock"]:has(.approval-marker) [data-testid="stCheckbox"] p{font-size:.95rem!important;font-weight:750!important;color:#10203e!important}
    div[data-testid="stHorizontalBlock"]:has(.approval-marker) [data-testid="stDateInput"]{max-width:260px;margin-left:auto}
    [data-testid="stTextArea"] textarea{line-height:1.45!important}
    @media(max-width:900px){.gate-head{display:none}div[data-testid="stHorizontalBlock"]:has(.gate-actions){overflow-x:auto}}
    </style>
    """,
    unsafe_allow_html=True,
)

STATUSES = ["Approved", "Approved with Conditions", "Requires Review", "Pending"]
STAKEHOLDERS = ["Business Head", "Program Lead", "Product Lead", "Infrastructure Lead", "Compliance Lead", "Data Lead", "Security Lead", "Finance Lead"]


def status_from_sources(area, sources):
    infrastructure, infra_review, workflow, responsibility, data_review = sources
    if area == "Infrastructure readiness":
        decision = infrastructure.get("decision", "")
        if decision == "Approved": return "Approved", infrastructure.get("comments", "")
        if decision == "Approved with Conditions": return "Approved with Conditions", infrastructure.get("comments", "Conditions must be tracked")
        return ("Requires Review", "Infrastructure output requires final review") if infrastructure else ("Pending", "Infrastructure output not saved")
    if area == "Security readiness":
        answers = list((infra_review.get("security") or {}).values())
        if not answers: return "Pending", "Security review not completed"
        if "No" in answers: return "Requires Review", "One or more security controls are not defined"
        if "Partial" in answers: return "Approved with Conditions", "Complete partial security controls before production"
        return "Approved", "Security controls confirmed"
    if area == "Data readiness":
        return ("Approved", "Data readiness review completed") if data_review else ("Pending", "Data readiness review not completed")
    if area == "Workflow readiness":
        return ("Approved", "Workflow output saved") if workflow.get("output_saved") else ("Pending", "Workflow output not saved")
    if area == "Performance metrics":
        rows = workflow.get("business", []) + workflow.get("technical", []) + workflow.get("environmental", [])
        return ("Approved", "Recommended metrics approved") if any(r.get("status") in {"Approve", "Approved", "Defined"} for r in rows) else ("Pending", "Approve the required performance metrics")
    if area == "Explainability":
        rows = workflow.get("explainability", [])
        return ("Approved", "Defined by stakeholder") if any(r.get("status") in {"Approve", "Approved", "Defined"} for r in rows) else ("Pending", "Explainability requirements not approved")
    if area == "Responsibility":
        return ("Approved", "Approved with human oversight") if responsibility.get("output_saved") else ("Pending", "Responsibility output not saved")
    if area == "Economics / OPEX":
        if responsibility.get("total_opex"): return "Approved", "OPEX estimate confirmed"
        if responsibility.get("costs"): return "Approved with Conditions", "Estimated; Finance validation pending"
        return "Pending", "OPEX has not been estimated"
    if area == "Compliance":
        rows = responsibility.get("accountability", [])
        return ("Approved", "Controlled pilot allowed") if any(r.get("status") == "Confirmed" for r in rows) else ("Requires Review", "Compliance accountability must be confirmed")
    return "Pending", "Final decision pending"


projects = get_approved_projects()
if not projects:
    st.warning("No approved projects are available. Approve a project in Portfolio Gate Review first.")
    st.stop()
project_map = {f"{p['id']} — {p['problem_statement']}": p for p in projects}
st.markdown('<div class="gate-label">APPROVED PROJECT</div>', unsafe_allow_html=True)
selected = st.selectbox("Approved project", list(project_map), label_visibility="collapsed")
st.markdown('<div class="gate-help">Readiness evidence, stakeholder approvals, blockers, and the final delivery decision are saved for this project.</div>', unsafe_allow_html=True)
project = project_map[selected]
project_id = project["id"]
gate = load_delivery_gate(project_id)
infra_output = load_infrastructure_output(project_id)
infrastructure = infra_output.get("final_output", {})
if infra_output.get("decision"): infrastructure = {**infrastructure, "decision": infra_output.get("decision"), "comments": infra_output.get("comments", "")}
sources = (infrastructure, load_infrastructure_review(project_id), load_workflow(project_id), load_responsibility(project_id), load_data_review(project_id))

areas = ["Infrastructure readiness", "Security readiness", "Data readiness", "Workflow readiness", "Performance metrics", "Explainability", "Responsibility", "Economics / OPEX", "Compliance", "Final decision"]
prior_rows = {row.get("area"): row for row in gate.get("readiness", [])}
readiness = []
with st.container(border=True):
    st.markdown('<div class="gate-title">Execution Readiness Summary</div>', unsafe_allow_html=True)
    heads = st.columns([2.2, 2.65, 4.15])
    for col, label in zip(heads, ["Readiness Area", "Status", "Notes"]): col.markdown(f'<div class="gate-head">{label}</div>', unsafe_allow_html=True)
    for index, area in enumerate(areas):
        generated_status, generated_notes = status_from_sources(area, sources)
        old = prior_rows.get(area, {})
        if area == "Final decision" and not old:
            other_statuses = [row["status"] for row in readiness]
            generated_status = "Requires Review" if "Requires Review" in other_statuses else "Approved with Conditions" if any(x in other_statuses for x in ["Pending", "Approved with Conditions"]) else "Approved"
            generated_notes = "Proceed to MVP planning" if generated_status == "Approved" else "Resolve conditions before unrestricted execution"
        cols = st.columns([2.2, 2.65, 4.15], vertical_alignment="center")
        cols[0].markdown('<span class="gate-row"></span>'+f'<div class="gate-area">{area}</div>', unsafe_allow_html=True)
        current_status = old.get("status", generated_status); current_status = current_status if current_status in STATUSES else generated_status
        status = cols[1].selectbox("Status", STATUSES, index=STATUSES.index(current_status), key=f"gate_status_{project_id}_{index}", label_visibility="collapsed")
        notes = cols[2].text_input("Notes", value=old.get("notes", generated_notes), key=f"gate_notes_{project_id}_{index}", label_visibility="collapsed", placeholder="Add notes…")
        readiness.append({"area": area, "status": status, "notes": notes})

action_slot = st.container()

with st.container(border=True):
    st.markdown('<div class="gate-title">Open Blockers</div>', unsafe_allow_html=True)
    blockers = st.text_area("Open blockers", value=gate.get("blockers", ""), height=125, label_visibility="collapsed", placeholder="List any open blockers that must be resolved before execution proceeds…")

stakeholder_values = []
prior_stakeholders = {row.get("role"): row for row in gate.get("stakeholders", [])}
with st.container(border=True):
    st.markdown('<div class="gate-title">Stakeholder Approvals</div>', unsafe_allow_html=True)
    for index, role in enumerate(STAKEHOLDERS):
        old = prior_stakeholders.get(role, {})
        cols = st.columns([6.8, 2.2], vertical_alignment="center")
        cols[0].markdown('<span class="approval-marker"></span>', unsafe_allow_html=True)
        approved = cols[0].checkbox(role, value=bool(old.get("approved", False)), key=f"stakeholder_approval_{project_id}_{index}")
        old_date = old.get("date")
        parsed_date = date.fromisoformat(old_date) if old_date else None
        approval_date = cols[1].date_input(f"{role} approval date", value=parsed_date, key=f"stakeholder_date_{project_id}_{index}", label_visibility="collapsed", format="DD-MM-YYYY")
        stakeholder_values.append({"role": role, "approved": approved, "date": str(approval_date) if approval_date else ""})


def gate_payload(action):
    return {
        "readiness": readiness,
        "blockers": blockers,
        "stakeholders": stakeholder_values,
        "action": action,
        "updated_by": user["email"],
    }


report_payload = gate_payload("Execution report generated")
report_bytes = generate_execution_report(project, report_payload)
with action_slot:
    st.markdown('<span class="gate-actions"></span>', unsafe_allow_html=True)
    proceed, revision, committee, report = st.columns([1.35, 1.2, 1.85, 1.65])
    with proceed:
        st.markdown('<span class="gate-proceed"></span>', unsafe_allow_html=True)
        proceed_clicked = st.button("◉  Proceed to Tracking", key=f"gate_proceed_{project_id}", use_container_width=True)
    with revision:
        st.markdown('<span class="gate-revision"></span>', unsafe_allow_html=True)
        revision_clicked = st.button("⚠  Request Revision", key=f"gate_revision_{project_id}", use_container_width=True)
    with committee:
        st.markdown('<span class="gate-committee"></span>', unsafe_allow_html=True)
        committee_clicked = st.button("♙  Send to Governance Committee", key=f"gate_committee_{project_id}", use_container_width=True)
    with report:
        st.markdown('<span class="gate-report"></span>', unsafe_allow_html=True)
        st.download_button("⇩  Generate Execution Report", data=report_bytes, file_name=f"{project_id}_execution_gate_report.pdf", mime="application/pdf", key=f"gate_report_{project_id}", use_container_width=True)

if revision_clicked:
    payload = gate_payload("Revision Requested")
    payload["readiness"][-1]["status"] = "Requires Review"
    payload["readiness"][-1]["notes"] = "Revision requested before execution"
    save_delivery_gate(project_id, payload)
    save_execution_decision(project_id, "Revision Requested", user["email"], blockers, str(date.today()))
    st.warning("Revision request saved and added to the audit trail.")

if committee_clicked:
    payload = gate_payload("Sent to Governance Committee")
    save_delivery_gate(project_id, payload)
    save_execution_decision(project_id, "Sent to Governance Committee", user["email"], blockers, str(date.today()))
    st.success("The review has been recorded for Governance Committee consideration.")

if proceed_clicked:
    payload = gate_payload("Approved for Tracking")
    payload["readiness"][-1]["status"] = "Approved" if not blockers.strip() else "Approved with Conditions"
    payload["readiness"][-1]["notes"] = "Proceed to Tracking" if not blockers.strip() else "Proceed with documented blockers as conditions"
    save_delivery_gate(project_id, payload)
    save_execution_decision(project_id, "Approved for Tracking", user["email"], blockers, str(date.today()))
    st.switch_page("pages/13_Tracking.py")
