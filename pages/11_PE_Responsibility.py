import streamlit as st

from database.project_execution_repository import (
    get_approved_projects,
    load_responsibility,
    save_responsibility,
)
from ui.auth import require_access, require_login
from ui.navbar import render_breadcrumb, render_navbar
from ui.sidebar import render_sidebar
from ui.theme import apply_theme


st.set_page_config(page_title="Governance Operating Model & Decision Rights", page_icon="⚖️", layout="wide")
user = require_login()
apply_theme()
render_sidebar("pe_responsibility")
render_navbar("pe_responsibility")
require_access("pe_responsibility")
render_breadcrumb("AI Delivery & Operational Readiness", "Governance Operating Model & Decision Rights")

st.markdown(
    """
    <style>
    section.main > div.block-container{padding-top:0!important}
    .cx-breadcrumb{display:none!important}
    .gov-label{font-size:.78rem;font-weight:800;letter-spacing:.06em;color:#627695;margin:15px 0 5px}
    .gov-help{font-size:.84rem;color:#8ea2c3;margin:-2px 0 14px}
    .gov-step-marker,.gov-step-active,.gov-step-done{display:none}
    div[data-testid="stHorizontalBlock"]:has(.gov-step-marker){width:calc(100% + 4.4rem);margin:0 -2.2rem 26px;padding:5px 25px;background:#fff;border-bottom:1px solid #d9e2f0;gap:5px}
    div[data-testid="stHorizontalBlock"]:has(.gov-step-marker) .stButton>button{width:100%;min-height:46px;padding:3px 5px;background:transparent!important;border:0!important;box-shadow:none!important;color:#91a3bf!important;font-size:.88rem;line-height:1.12;white-space:normal}
    div[data-testid="column"]:has(.gov-step-active) .stButton>button{color:#155eef!important;font-weight:800!important}
    div[data-testid="column"]:has(.gov-step-done) .stButton>button{color:#00a36c!important;font-weight:800!important}
    div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:#d9e2f0!important;padding:3px!important}
    div[data-testid="stVerticalBlockBorderWrapper"]>div{padding:7px 10px!important}
    .gov-card-title{font-size:1.12rem;font-weight:800;color:#10203e;margin:2px 0 7px}
    .gov-card-copy{font-size:.96rem;line-height:1.58;color:#405678;margin:4px 0}
    .gov-good-marker,.gov-bad-marker{display:none}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.gov-good-marker){border:2px solid #00c98b!important;border-radius:8px!important;background:#ecfbf5!important;min-height:230px}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.gov-bad-marker){border:2px solid #ff6066!important;border-radius:8px!important;background:#fff1f2!important;min-height:230px}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.gov-good-marker) textarea{background:#ecfbf5!important;border:0!important;color:#405678!important;box-shadow:none!important;line-height:1.55!important;padding:4px!important}
    .gov-good-title{color:#00875a;font-size:1.06rem;font-weight:800;margin-bottom:10px}
    .gov-bad-title{color:#d00012;font-size:1.06rem;font-weight:800;margin-bottom:10px}
    .gov-bad-item{color:#405678;font-size:.93rem;line-height:1.45;margin:5px 0}.gov-x{color:#ff2e38;font-weight:900;margin-right:8px}
    .gov-section-title{font-size:1.08rem;font-weight:800;color:#10203e;margin:5px 0 8px;display:flex;align-items:center;gap:9px}
    .gov-accent{display:inline-block;width:8px;height:28px;border-radius:4px;background:#8447ff}.gov-accent.orange{background:#ff9800}
    .gov-section-help{color:#8ea2c3;font-size:.94rem;font-weight:400}
    .gov-head{color:#526a90;font-size:.91rem;font-weight:800;padding:6px 2px;border-bottom:1px solid #d9e2f0}
    .gov-name{color:#10203e;font-weight:800;font-size:.91rem;line-height:1.3;padding:5px 2px}
    .gov-copy{color:#526a90;font-size:.89rem;line-height:1.4;padding:5px 2px}.gov-demo{color:#8ea2c3;font-style:italic;font-size:.88rem;line-height:1.35;padding:5px 2px}
    .gov-row{display:none}div[data-testid="stHorizontalBlock"]:has(.gov-row){align-items:center;border-bottom:1px solid #e7edf6;padding:3px 0;min-height:55px;gap:.75rem}
    div[data-testid="stHorizontalBlock"]:has(.gov-row) [data-testid="stVerticalBlock"]{gap:0!important}
    div[data-testid="stHorizontalBlock"]:has(.gov-row) [data-testid="stElementContainer"]{margin:0!important}
    div[data-testid="stHorizontalBlock"]:has(.gov-row) [data-testid="stTextInput"] input,div[data-testid="stHorizontalBlock"]:has(.gov-row) [data-testid="stSelectbox"]>div>div{min-height:40px!important;height:40px!important}
    [data-testid="stSegmentedControl"]>div,[data-testid="stSegmentedControl"] [role="radiogroup"],[data-testid="stButtonGroup"]>div{display:flex!important;flex-flow:row nowrap!important;width:100%!important;gap:0!important}
    [data-testid="stSegmentedControl"] button,[data-testid="stButtonGroup"] button{min-height:38px!important;min-width:0!important;padding:5px 8px!important;white-space:nowrap!important;background:#fff!important;color:#405678!important;border-color:#d9e2f0!important;font-weight:750!important;flex:1 1 0!important}
    button[data-testid="stBaseButton-segmented_controlActive"],button[data-testid*="segmented_controlActive"],[data-testid="stSegmentedControl"] button[aria-checked="true"]{background:#e8f8f1!important;color:#00875a!important;border-color:#00a36c!important}
    .gov-actions{display:none}div[data-testid="stHorizontalBlock"]:has(.gov-actions){margin-top:18px;align-items:center}
    div[data-testid="stHorizontalBlock"]:has(.gov-actions) [data-testid="column"]:first-child .stButton>button{background:#fff!important;color:#10203e!important;border:1px solid #d9e2f0!important}
    .gov-save{display:none}div[data-testid="stElementContainer"]:has(.gov-save)+div .stButton>button{background:#00a36c!important;border-color:#00a36c!important}
    .gov-output{display:none}div[data-testid="stVerticalBlockBorderWrapper"]:has(.gov-output) [data-testid="stCheckbox"]{padding:2px 0!important;margin:0!important}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.gov-output) [data-testid="stCheckbox"] p{font-size:.96rem!important;font-weight:750!important;color:#10203e!important}
    @media(max-width:950px){div[data-testid="stHorizontalBlock"]:has(.gov-step-marker){overflow-x:auto}.gov-head{display:none}}
    </style>
    """,
    unsafe_allow_html=True,
)

STAGES = ["Positioning", "Blind-Use Risk", "Failure Impact", "Economics / OPEX", "Compliance & Accountability", "Responsibility Output"]
ASSESSMENTS = ["Select", "Acceptable", "Attention Needed", "High Risk", "Not Applicable"]
ROLES = ["Business Head", "Program Lead", "Product Lead", "Customer Success Head", "Support Lead", "Finance Lead", "Data Lead", "Infrastructure Lead", "Compliance Lead", "Security Lead"]


def defaults(project):
    text = " ".join(str(project.get(k, "")) for k in ("problem_statement", "business_objective", "solution_approach")).lower()
    learning = any(word in text for word in ("learner", "learning", "education", "certification", "skill"))
    if learning:
        positioning = "This is an AI-enabled educational assessment and skills recommendation decision-support system. It helps teams interpret learner evidence, identify skill gaps, recommend learning pathways and certification preparation resources, and monitor outcomes. It must not be treated as an automatic certification or high-stakes decision-maker."
        prohibited = ["It is not a fully automated certification decision engine", "It is not a replacement for educators or program leaders", "It does not guarantee certification readiness or success", "It is not the final authority on learner ability or professional potential"]
        context = "learners and professional learning outcomes"
    else:
        positioning = "This is an AI-enabled decision-support system. It helps accountable teams identify relevant signals, understand probable reasons, prioritize cases, recommend actions, and track outcomes. It must not be treated as an automatic decision-maker."
        prohibited = ["It is not a fully automated decision engine", "It is not a replacement for accountable business teams", "It does not guarantee an outcome", "It is not the final authority for high-impact decisions"]
        context = "customers, employees, money, access, or other affected people"
    ethics = [
        ("Responsible use classification", "Whether the use case is low, medium, or high impact", "Medium impact"),
        ("Sensitive decision involvement", f"Whether AI affects {context}", "Yes — human review required"),
        ("Human approval coverage", "% of high-impact recommendations requiring human approval before action", "100% for high-impact actions"),
        ("Prohibited use check", "Whether the system is used for disallowed or restricted decisions", "Passed"),
        ("Over-reliance risk", "Risk that users blindly trust AI output without critical review", "Medium"),
        ("Appeal / override", "Whether people can challenge, correct, or override an AI-supported outcome", "Available"),
    ]
    fairness = [
        ("Segment fairness check", "Whether some affected groups are unfairly deprioritized by the model", "Pending"),
        ("False positive rate by segment", "Whether groups are wrongly flagged more often than others", "To be monitored"),
        ("False negative rate by segment", "Whether groups are missed more often than others", "To be monitored"),
        ("Action fairness", "Whether interventions are unevenly distributed across groups", "Attention needed"),
        ("High-value bias", "Whether only high-value groups receive AI-assisted support", "Medium risk"),
        ("Bias audit completion", "Whether a formal bias review was completed before pilot deployment", "Not complete"),
        ("Fairness review owner", "Who is accountable for the fairness and bias review", "Compliance Lead"),
    ]
    failures = [
        ("LLM / API unavailable", "No new explanations or recommendations", "Use the last validated output and manual review"),
        ("Data refresh fails", "Scores and recommendations become stale", "Show a visible data-outdated warning and stop automation"),
        ("Wrong recommendation", "Poor or harmful intervention", "Human approval, correction, and override"),
        ("Operational alert fails", "A high-impact case is not escalated", "Manual watchlist and escalation procedure"),
        ("Security incident", "Sensitive-data exposure risk", "Disable access, notify security and compliance, preserve audit logs"),
    ]
    costs = [
        ("LLM / API token cost", "~$200–500/month for a controlled prototype"),
        ("Infrastructure cost", "~$800/month cloud compute for Phase 1"),
        ("Data integration cost", "One-time implementation estimate for source-system pipelines"),
        ("Monitoring cost", "~$100–200/month for logs, alerts, and dashboards"),
        ("Human review cost", "~2–4 hours/week across accountable business and control teams"),
        ("Maintenance cost", "Quarterly model, policy, and governance maintenance"),
    ]
    accountability = [
        ("Business outcome", "Business Head"), ("Operational actions", "Program Lead"),
        ("User outreach workflow", "Customer Success Head"), ("Support escalation", "Support Lead"),
        ("Product causes and remediation", "Product Lead"), ("ROI validation", "Finance Lead"),
        ("Data quality", "Data Lead"), ("Security and hosting", "Infrastructure Lead"),
        ("Privacy, fairness, and audit", "Compliance Lead"),
    ]
    return {"positioning": positioning, "prohibited": prohibited, "ethics": ethics, "fairness": fairness, "failures": failures, "costs": costs, "accountability": accountability}


def saved_value(area, index, field, fallback=""):
    try:
        return saved[area][index].get(field, fallback)
    except (KeyError, IndexError, TypeError):
        return fallback


def stepper(active, completed):
    cols = st.columns([.85, .9, .9, 1.05, 1.35, 1.05])
    for index, (col, label) in enumerate(zip(cols, STAGES), 1):
        state = "gov-step-active" if index == active else "gov-step-done" if index in completed else ""
        icon = "✓" if index in completed else str(index)
        with col:
            st.markdown(f'<span class="gov-step-marker {state}"></span>', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"gov_nav_{project_id}_{index}", use_container_width=True):
                st.session_state[step_key] = index
                st.rerun()


def save_and_move(stage, next_stage, payload):
    saved.update(payload)
    completed.add(stage)
    saved["completed_steps"] = sorted(completed)
    saved["active_step"] = next_stage
    save_responsibility(project_id, saved)
    st.session_state[step_key] = next_stage
    st.rerun()


def actions(back=None):
    st.markdown('<span class="gov-actions"></span>', unsafe_allow_html=True)
    left, _ = st.columns([1.05, 8.95])
    if back and left.button("← Back", key=f"gov_back_{project_id}_{back}", use_container_width=True):
        st.session_state[step_key] = back
        st.rerun()


projects = get_approved_projects()
if not projects:
    st.warning("No approved projects are available. Approve a project in Portfolio Gate Review first.")
    st.stop()
project_map = {f"{p['id']} — {p['problem_statement']}": p for p in projects}
st.markdown('<div class="gov-label">APPROVED PROJECT</div>', unsafe_allow_html=True)
selected = st.selectbox("Approved project", list(project_map), label_visibility="collapsed")
st.markdown('<div class="gov-help">Governance decisions, assessments, ownership, costs, and evidence are saved for this project.</div>', unsafe_allow_html=True)
project = project_map[selected]
project_id = project["id"]
saved = load_responsibility(project_id)
content = defaults(project)
step_key = f"responsibility_step_{project_id}"
st.session_state.setdefault(step_key, int(saved.get("active_step", 1)))
completed = set(saved.get("completed_steps", []))
stepper(st.session_state[step_key], completed)
step = st.session_state[step_key]


if step == 1:
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<span class="gov-good-marker"></span><div class="gov-good-title">Correct Positioning</div>', unsafe_allow_html=True)
            positioning = st.text_area("Correct positioning", value=saved.get("positioning", content["positioning"]), height=155, label_visibility="collapsed")
    with right:
        with st.container(border=True):
            bad_items = "".join(f'<div class="gov-bad-item"><span class="gov-x">×</span>{item}</div>' for item in content["prohibited"])
            st.markdown(f'<span class="gov-bad-marker"></span><div class="gov-bad-title">What Not to Say</div>{bad_items}', unsafe_allow_html=True)
    with st.container(border=True):
        confirmed = st.checkbox("Positioning Confirmed", value=bool(saved.get("positioning_confirmed", False)), key=f"position_confirmed_{project_id}")
        comment = st.text_input("Feedback / Comment", value=saved.get("positioning_comment", ""), placeholder="Add feedback or clarification…")
        if st.button("Save Positioning & Continue →", type="primary", use_container_width=True):
            save_and_move(1, 2, {"positioning": positioning, "positioning_confirmed": confirmed, "positioning_comment": comment, "prohibited": content["prohibited"]})


elif step == 2:
    results = {}
    with st.form(f"blind_use_{project_id}"):
        for section, accent, help_text in [("ethics", "", "Responsible use, transparency, and human oversight"), ("fairness", "orange", "Equitable treatment across affected groups")]:
            with st.container(border=True):
                title = "Ethics" if section == "ethics" else "Bias & Fairness"
                st.markdown(f'<div class="gov-section-title"><span class="gov-accent {accent}"></span>{title}<span class="gov-section-help">— {help_text}</span></div>', unsafe_allow_html=True)
                heads = st.columns([1.7, 2.1, 1.7, 1.55, 2.25])
                for col, label in zip(heads, ["Metric", "What it checks", "Demo Example", "Assessment", "Feedback / Comment"]): col.markdown(f'<div class="gov-head">{label}</div>', unsafe_allow_html=True)
                rows = []
                for i, (metric, check, example) in enumerate(content[section]):
                    c = st.columns([1.7, 2.1, 1.7, 1.55, 2.25], vertical_alignment="center")
                    c[0].markdown('<span class="gov-row"></span>'+f'<div class="gov-name">{metric}</div>', unsafe_allow_html=True)
                    c[1].markdown(f'<div class="gov-copy">{check}</div>', unsafe_allow_html=True); c[2].markdown(f'<div class="gov-demo">{example}</div>', unsafe_allow_html=True)
                    old = saved_value(section, i, "assessment", "Select"); old = old if old in ASSESSMENTS else "Select"
                    assessment = c[3].selectbox("Assessment", ASSESSMENTS, index=ASSESSMENTS.index(old), key=f"{section}_assessment_{project_id}_{i}", label_visibility="collapsed")
                    comment = c[4].text_input("Feedback / Comment", value=saved_value(section, i, "comment"), key=f"{section}_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add comment or note…")
                    rows.append({"metric": metric, "check": check, "example": example, "assessment": assessment, "comment": comment})
                results[section] = rows
        submitted = st.form_submit_button("Save Blind-Use Assessment & Continue →", type="primary", use_container_width=True)
    if submitted:
        save_and_move(2, 3, results)
    actions(1)


elif step == 3:
    with st.container(border=True):
        st.markdown('<div class="gov-card-title">Failure Impact and Backup</div>', unsafe_allow_html=True)
        heads = st.columns([1.55, 2.45, 2.65, 1.75, 1.9])
        for col, label in zip(heads, ["Failure Scenario", "Impact", "Backup", "Status", "Feedback / Comment"]): col.markdown(f'<div class="gov-head">{label}</div>', unsafe_allow_html=True)
        rows = []
        with st.form(f"failure_{project_id}"):
            for i, (scenario, impact, backup) in enumerate(content["failures"]):
                c = st.columns([1.55, 2.45, 2.65, 1.75, 1.9], vertical_alignment="center")
                c[0].markdown('<span class="gov-row"></span>'+f'<div class="gov-name">{scenario}</div>', unsafe_allow_html=True); c[1].markdown(f'<div class="gov-copy">{impact}</div>', unsafe_allow_html=True); c[2].markdown(f'<div class="gov-copy">{backup}</div>', unsafe_allow_html=True)
                old = saved_value("failures", i, "status", "Not Planned"); old = old if old in ["Planned", "Not Planned"] else "Not Planned"
                status = c[3].segmented_control("Status", ["Planned", "Not Planned"], default=old, key=f"failure_status_{project_id}_{i}", label_visibility="collapsed") or old
                comment = c[4].text_input("Feedback / Comment", value=saved_value("failures", i, "comment"), key=f"failure_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add comment…")
                rows.append({"scenario": scenario, "impact": impact, "backup": backup, "status": status, "comment": comment})
            submitted = st.form_submit_button("Save Failure Plan & Continue →", type="primary", use_container_width=True)
    if submitted:
        save_and_move(3, 4, {"failures": rows})
    actions(2)


elif step == 4:
    with st.container(border=True):
        st.markdown('<div class="gov-card-title">Economics / OPEX</div>', unsafe_allow_html=True)
        heads = st.columns([1.8, 3.9, 1.55, 1.8])
        for col, label in zip(heads, ["Cost Area", "Example Estimate", "Your Estimate", "Notes"]): col.markdown(f'<div class="gov-head">{label}</div>', unsafe_allow_html=True)
        rows = []
        with st.form(f"opex_{project_id}"):
            for i, (area, example) in enumerate(content["costs"]):
                c = st.columns([1.8, 3.9, 1.55, 1.8], vertical_alignment="center")
                c[0].markdown('<span class="gov-row"></span>'+f'<div class="gov-name">{area}</div>', unsafe_allow_html=True); c[1].markdown(f'<div class="gov-copy">{example}</div>', unsafe_allow_html=True)
                estimate = c[2].text_input("Estimate", value=saved_value("costs", i, "estimate"), key=f"cost_estimate_{project_id}_{i}", label_visibility="collapsed", placeholder="Estimate")
                notes = c[3].text_input("Notes", value=saved_value("costs", i, "notes"), key=f"cost_notes_{project_id}_{i}", label_visibility="collapsed", placeholder="Notes")
                rows.append({"area": area, "example": example, "estimate": estimate, "notes": notes})
            total = st.text_input("Total Estimated OPEX", value=saved.get("total_opex", ""), placeholder="Enter total estimate or calculation reference")
            submitted = st.form_submit_button("Save OPEX & Continue →", type="primary", use_container_width=True)
    if submitted:
        save_and_move(4, 5, {"costs": rows, "total_opex": total})
    actions(3)


elif step == 5:
    with st.container(border=True):
        st.markdown('<div class="gov-card-title">Compliance and Stakeholder Accountability</div>', unsafe_allow_html=True)
        heads = st.columns([2.0, 2.55, 2.75, 2.2])
        for col, label in zip(heads, ["Area", "Responsible Stakeholder", "Status", "Feedback / Comment"]): col.markdown(f'<div class="gov-head">{label}</div>', unsafe_allow_html=True)
        rows = []
        with st.form(f"accountability_{project_id}"):
            for i, (area, default_role) in enumerate(content["accountability"]):
                c = st.columns([2.0, 2.55, 2.75, 2.2], vertical_alignment="center")
                c[0].markdown('<span class="gov-row"></span>'+f'<div class="gov-name">{area}</div>', unsafe_allow_html=True)
                old_role = saved_value("accountability", i, "stakeholder", default_role); old_role = old_role if old_role in ROLES else default_role
                role = c[1].selectbox("Stakeholder", ROLES, index=ROLES.index(old_role), key=f"accountability_role_{project_id}_{i}", label_visibility="collapsed")
                old_status = saved_value("accountability", i, "status", "Pending"); old_status = old_status if old_status in ["Confirmed", "Pending", "Not Assigned"] else "Pending"
                status = c[2].segmented_control("Status", ["Confirmed", "Pending", "Not Assigned"], default=old_status, key=f"accountability_status_{project_id}_{i}", label_visibility="collapsed") or old_status
                comment = c[3].text_input("Feedback / Comment", value=saved_value("accountability", i, "comment"), key=f"accountability_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add comment…")
                rows.append({"area": area, "stakeholder": role, "status": status, "comment": comment})
            submitted = st.form_submit_button("Save Accountability & Continue →", type="primary", use_container_width=True)
    if submitted:
        save_and_move(5, 6, {"accountability": rows})
    actions(4)


else:
    derived = [
        ("Positioning approved", bool(saved.get("positioning_confirmed"))),
        ("Blind-use risks documented", bool(saved.get("ethics")) and bool(saved.get("fairness"))),
        ("Failure impact assessed", bool(saved.get("failures"))),
        ("Backup plan defined", any(x.get("status") == "Planned" for x in saved.get("failures", []))),
        ("OPEX estimated", bool(saved.get("costs"))),
        ("Compliance ownership defined", bool(saved.get("accountability"))),
        ("Stakeholder accountability confirmed", any(x.get("status") == "Confirmed" for x in saved.get("accountability", []))),
    ]
    prior = saved.get("output_checklist", {})
    checks = {}
    with st.container(border=True):
        st.markdown('<span class="gov-output"></span>', unsafe_allow_html=True)
        st.markdown('<div class="gov-card-title">Responsibility Output</div>', unsafe_allow_html=True)
        for i, (label, ready) in enumerate(derived):
            checks[label] = st.checkbox(label, value=bool(prior.get(label, ready)), key=f"responsibility_output_{project_id}_{i}")
        st.markdown('<span class="gov-save"></span>', unsafe_allow_html=True)
        if st.button("✓  Save Responsibility Output", type="primary", key=f"save_responsibility_output_{project_id}"):
            saved["output_checklist"] = checks; saved["output_complete"] = all(checks.values()); saved["output_saved"] = True; saved["saved_by"] = user["email"]
            completed.add(6); saved["completed_steps"] = sorted(completed); saved["active_step"] = 6
            save_responsibility(project_id, saved)
            st.success("Responsibility output saved. You can proceed to Execution Approval.")
    st.markdown('<span class="gov-actions"></span>', unsafe_allow_html=True)
    back, _, proceed = st.columns([1.05, 5.2, 3.75])
    if back.button("← Back", key=f"responsibility_output_back_{project_id}", use_container_width=True):
        st.session_state[step_key] = 5; st.rerun()
    if proceed.button("Proceed to Execution Approval  ›", type="primary", key=f"to_execution_approval_{project_id}", use_container_width=True):
        saved["output_checklist"] = checks; saved["output_complete"] = all(checks.values()); saved["output_saved"] = True; saved["saved_by"] = user["email"]
        completed.add(6); saved["completed_steps"] = sorted(completed); saved["active_step"] = 6
        save_responsibility(project_id, saved)
        st.switch_page("pages/12_PE_Execution_Approval.py")
