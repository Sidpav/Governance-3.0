import streamlit as st
from database.project_execution_repository import get_approved_projects
from database.delivery_repository import execution_readiness, load_execution_decisions, save_execution_decision
from ui.auth import require_login, require_access
from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb

st.set_page_config(page_title="Delivery Gate Review",page_icon="📍",layout="wide")
user=require_login(); apply_theme(); render_sidebar("pe_execution_approval"); render_navbar("pe_execution_approval")
require_access("pe_execution_approval"); render_breadcrumb("AI Delivery & Operational Readiness","Delivery Gate Review")
st.title("📍 Delivery Gate Review")
projects=get_approved_projects()
if not projects: st.warning("No governance-approved projects found."); st.stop()
p=st.selectbox("Project",projects,format_func=lambda x:f"{x['id']} — {x['problem_statement'][:70]}")
ready,missing=execution_readiness(p['id'])
if ready: st.success("Required delivery control areas have completion evidence.")
else: st.error("Execution gate is blocked. Missing completed areas: "+", ".join(missing))
with st.form("execution_gate"):
    decision=st.selectbox("Decision",["Approved for Execution","Approved with Conditions","Deferred","Rejected"])
    conditions=st.text_area("Conditions / rationale")
    review_date=st.date_input("Next review date")
    if st.form_submit_button("Record delivery decision",type="primary",disabled=not ready):
        save_execution_decision(p['id'],decision,user['email'],conditions,str(review_date))
        st.success("Execution decision recorded in the audit trail.")
history=load_execution_decisions(p['id'])
if history: st.dataframe(history,hide_index=True,width="stretch")
