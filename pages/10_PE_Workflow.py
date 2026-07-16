import streamlit as st
from database.project_execution_repository import get_approved_projects
from database.delivery_repository import load_controls, upsert_control
from ui.auth import require_login, require_access
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb

st.set_page_config(page_title="Operational Integration", page_icon="🔄", layout="wide")
user = require_login(); apply_theme(); render_sidebar("pe_workflow"); render_navbar("pe_workflow")
require_access("pe_workflow"); render_breadcrumb("AI Product Delivery", "Operational Integration & Metrics")
st.title("🔄 Operational Integration & Metrics")
projects = get_approved_projects()
if not projects: st.warning("No governance-approved projects found."); st.stop()
p = st.selectbox("Project", projects, format_func=lambda x: f"{x['id']} — {x['problem_statement'][:70]}")
existing = {r['control_key']: r for r in load_controls(p['id'], 'workflow')}
controls = {
    "process_map": "Current and future workflow documented",
    "human_handoff": "Human review and override points defined",
    "success_metrics": "Operational KPIs and acceptance thresholds defined",
    "incident_process": "Failure escalation and incident response process defined",
}
with st.form("workflow_controls"):
    values = {}
    for key, label in controls.items():
        old = existing.get(key, {})
        st.subheader(label)
        c1, c2 = st.columns(2)
        values[key] = {
            "status": c1.selectbox("Status", ["Not Started", "In Progress", "Complete"],
                index=["Not Started", "In Progress", "Complete"].index(old.get('status','Not Started')), key=f"s_{key}"),
            "owner": c2.text_input("Owner", old.get('owner',''), key=f"o_{key}"),
            "evidence": st.text_input("Evidence link/reference", old.get('evidence',''), key=f"e_{key}"),
            "notes": st.text_area("Notes", old.get('notes',''), key=f"n_{key}"),
        }
    if st.form_submit_button("Save workflow controls", type="primary"):
        for key, v in values.items(): upsert_control(p['id'], 'workflow', key, **v, user=user['email'])
        st.success("Workflow controls saved and audited.")
