import streamlit as st
from database.project_execution_repository import get_approved_projects
from database.delivery_repository import load_lifecycle_evidence, save_lifecycle_evidence
from ui.auth import require_login, require_access
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb

st.set_page_config(page_title="AI Oversight & Evidence",page_icon="📍",layout="wide")
user=require_login(); apply_theme(); render_sidebar("tracking"); render_navbar("tracking")
require_access("tracking"); render_breadcrumb("AI Oversight & Evidence","Monitoring")
st.title("AI Oversight & Evidence")
projects=get_approved_projects()
if not projects: st.warning("No governance-approved projects found."); st.stop()
p=st.selectbox("Project",projects,format_func=lambda x:f"{x['id']} — {x['problem_statement'][:70]}")
with st.form("monitoring"):
    metric=st.text_input("Metric / control monitored")
    value=st.text_input("Current value")
    status=st.selectbox("Status",["On Track","Watch","Breach","Incident"])
    evidence=st.text_area("Evidence or incident reference")
    if st.form_submit_button("Add monitoring evidence",type="primary"):
        if not metric.strip(): st.error("Metric is required.")
        else:
            save_lifecycle_evidence(p['id'],metric,value,status,evidence,user['email'])
            st.success("Evidence recorded.")
rows=load_lifecycle_evidence(p['id'])
if rows: st.dataframe(rows,hide_index=True,width="stretch")
else: st.info("No monitoring evidence recorded yet.")
