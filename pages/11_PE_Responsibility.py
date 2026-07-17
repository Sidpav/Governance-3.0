import streamlit as st
from database.project_execution_repository import get_approved_projects
from database.delivery_repository import load_assignments, load_controls, upsert_control
from ui.auth import require_login, require_access
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb

st.set_page_config(page_title="Decision Rights", page_icon="👤", layout="wide")
user=require_login(); apply_theme(); render_sidebar("pe_responsibility"); render_navbar("pe_responsibility")
require_access("pe_responsibility"); render_breadcrumb("AI Delivery & Operational Readiness", "Governance Operating Model & Decision Rights")
st.title("👤 Governance Operating Model & Decision Rights")
projects=get_approved_projects()
if not projects: st.warning("No governance-approved projects found."); st.stop()
p=st.selectbox("Project", projects, format_func=lambda x:f"{x['id']} — {x['problem_statement'][:70]}")
assignments=load_assignments(p['id'])
if assignments:
    st.dataframe([{"Role":a['role_key'].replace('_',' ').title(),"Name":a['person_name'],"Email":a['person_email']} for a in assignments], hide_index=True, width="stretch")
else: st.warning("No persistent stakeholder assignments exist for this project.")
old={r['control_key']:r for r in load_controls(p['id'],'responsibility')}
with st.form("responsibility"):
    accountable=st.text_input("Accountable executive", old.get('raci',{}).get('owner',''))
    evidence=st.text_input("RACI / decision-rights evidence", old.get('raci',{}).get('evidence',''))
    notes=st.text_area("Escalation path and decision boundaries", old.get('raci',{}).get('notes',''))
    status=st.selectbox("Status",["Not Started","In Progress","Complete"])
    if st.form_submit_button("Save operating model",type="primary"):
        upsert_control(p['id'],'responsibility','raci',status,accountable,evidence,notes,user['email'])
        st.success("Decision rights saved and audited.")
