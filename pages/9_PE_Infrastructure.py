import streamlit as st

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access
from database.project_execution_repository import (
    get_approved_projects,
    load_hypotheses,
    load_experiments,
    load_prototype_spec,
)
from database.infrastructure_repository import (
    load_infrastructure_review,
    save_infrastructure_review,
    load_infrastructure_output,
    save_infrastructure_output,
)
from llm.infrastructure_recommendation_generator import generate_infrastructure_recommendation
from llm.infrastructure_output_generator import generate_infrastructure_output


st.set_page_config(page_title="AI Product Delivery - Infrastructure", page_icon="🏗️", layout="wide")
require_login()
apply_theme()
render_sidebar(active="pe_infrastructure")
render_navbar(active="pe_infrastructure")
require_access("pe_infrastructure")
render_breadcrumb("AI Product Delivery", "Infrastructure")


st.markdown(
    """
    <style>
    section.main > div.block-container { padding-top: 0 !important; }
    .cx-breadcrumb { display: none !important; }
    .infra-project-label { color:#627695; font-size:.82rem; font-weight:700; margin:18px 0 6px; }
    .infra-project-help { color:#8EA2C3; font-size:.84rem; margin:-4px 0 14px; }

    div[data-testid="stHorizontalBlock"]:has(.infra-step-marker) {
        width:calc(100% + 4.4rem); margin:0 -2.2rem 34px; padding:8px 26px;
        background:#fff; border-bottom:1px solid #D9E2F0; gap:12px;
    }
    div[data-testid="stHorizontalBlock"]:has(.infra-step-marker) [data-testid="column"] { display:flex; align-items:center; }
    div[data-testid="stHorizontalBlock"]:has(.infra-step-marker) .stButton { width:100%; }
    div[data-testid="stHorizontalBlock"]:has(.infra-step-marker) .stButton > button {
        width:100%; min-height:44px; padding:4px 8px; background:transparent !important;
        color:#8EA2C3 !important; border:0 !important; box-shadow:none !important;
        font-size:.92rem; white-space:normal; line-height:1.15;
    }
    div[data-testid="stHorizontalBlock"]:has(.infra-step-marker)
    [data-testid="column"]:has(.infra-step-active) .stButton > button { color:#155EEF !important; }
    .infra-step-marker { display:none; }

    .infra-card-title { font-size:1.2rem; font-weight:700; color:#10203E; margin:2px 0 4px; }
    .infra-stakeholders { color:#8EA2C3; font-size:1rem; margin-bottom:22px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding:10px 4px; }
    div[data-testid="stVerticalBlockBorderWrapper"] hr { margin:.45rem 0 !important; }

    div[data-testid="stHorizontalBlock"]:has(.infra-question) { align-items:center; min-height:70px; }
    .infra-question { color:#10203E; font-size:1rem; line-height:1.35; padding-top:8px; }
    div[data-testid="stHorizontalBlock"]:has(.infra-question) [data-testid="stSegmentedControl"] { justify-content:flex-end; }
    [data-testid="stSegmentedControl"] button {
        min-height:42px !important; background:#fff !important; color:#405678 !important;
        border-color:#D9E2F0 !important; font-weight:700 !important;
    }
    [data-testid="stSegmentedControl"] button[aria-pressed="true"] {
        color:#155EEF !important; background:#EAF1FF !important; border-color:#9FC0FF !important;
    }
    [data-testid="stSegmentedControl"] button p { color:inherit !important; }
    .infra-field-label { color:#10203E; font-size:1rem; padding-top:12px; }

    .infra-table-head, .infra-table-cell { padding:12px 10px; border-bottom:1px solid #E6ECF5; }
    .infra-table-head { color:#526A90; font-weight:700; font-size:1rem; }
    .infra-table-area { color:#10203E; font-weight:700; font-size:1rem; }
    .infra-table-copy { color:#526A90; font-size:.98rem; line-height:1.55; }
    .infra-table-recommendation { color:#10203E; font-size:.98rem; line-height:1.55; }

    .security-title { color:#405678; font-size:1rem; font-weight:700; margin-bottom:4px; }
    .security-question { color:#10203E; font-size:.96rem; line-height:1.35; }
    .output-label { color:#10203E; font-weight:700; font-size:.96rem; padding-top:12px; }

    div[data-testid="stHorizontalBlock"]:has(.infra-actions) { margin-top:20px; }
    .infra-actions { display:none; }
    div[data-testid="stHorizontalBlock"]:has(.infra-actions) [data-testid="column"]:first-child .stButton > button {
        background:#FFFFFF !important; color:#10203E !important; border:1px solid #D9E2F0 !important;
    }
    .infra-save + div .stButton > button, div[data-testid="stElementContainer"]:has(.infra-save) + div .stButton > button {
        background:#00A36C !important;
    }
    @media (max-width: 900px) {
        div[data-testid="stHorizontalBlock"]:has(.infra-step-marker) { overflow-x:auto; }
        div[data-testid="stHorizontalBlock"]:has(.infra-step-marker) .stButton > button { font-size:.78rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


STAGES = [
    "Infrastructure Decision Intake",
    "Model and Compute Recommendation",
    "Security Review",
    "Infrastructure Output",
]

SECURITY_QUESTIONS = [
    ("Customer PII", "Are customer names, emails, transcripts, or complaints used?"),
    ("Access Control", "Has role-based access been defined for model outputs and sensitive actions?"),
    ("Data Masking", "Should customer data be anonymized or masked for the prototype?"),
    ("Model Access", "Is customer data sent to external model providers?"),
    ("Audit Log", "Are prompts, recommendations, approvals, and overrides logged?"),
    ("Data Retention", "Is a data retention period defined for model outputs and explanations?"),
    ("Sensitive Actions", "Are discounts, escalations, or other sensitive actions human-approved?"),
    ("Failure Fallback", "Is a fallback defined if the model or API is unavailable?"),
]


def fallback_recommendation(review):
    confidential = review.get("confidential", "Yes") == "Yes"
    processing = review.get("processing", "Batch")
    deployment = review.get("deployment", "Cloud")
    llm = review.get("llm_type", "Closed LLM")
    return {
        "recommendations": [
            {"area": "LLM choice", "recommendation": f"{llm} for the Phase 1 prototype", "reason": "Balance deployment speed, data restrictions, and the option to move to a controlled model when sensitivity requires it."},
            {"area": "Processing type", "recommendation": f"{processing} processing with monitored retries", "reason": "Matches the selected responsiveness requirement while keeping the pilot reliable and measurable."},
            {"area": "Compute", "recommendation": "CPU-first compute; add GPU only for fine-tuning or heavy NLP", "reason": "Avoids unnecessary cost for orchestration, RAG, and conventional model workloads."},
            {"area": "Infrastructure strategy", "recommendation": f"Use {deployment.lower()} managed services for the pilot", "reason": "Start with elastic capacity and revisit reserved or owned capacity after usage is validated."},
            {"area": "Data storage", "recommendation": "Encrypted internal store with role-based access" + (" and mandatory masking" if confidential else ""), "reason": "Keeps source data governed and limits exposure of sensitive records."},
            {"area": "Integration", "recommendation": "API gateway, identity provider, audit log, and approved business data sources", "reason": "Creates a traceable integration boundary for production readiness."},
        ]
    }


def fallback_output(review):
    users = review.get("users", "50 internal users")
    requests = review.get("requests_per_day", "200 requests/day")
    return {
        "deployment_recommendation": f"{review.get('deployment', 'Cloud')} deployment with a governed {review.get('processing', 'Batch').lower()} pipeline",
        "training_requirement": "No continuous training in Phase 1; validate and retrain through an approved offline workflow",
        "inference_requirement": f"Designed for {requests} and {users}",
        "compute_estimate": "CPU — 4 vCPU / 16GB RAM for pilot; GPU only if fine-tuning is approved",
        "storage_estimate": "Encrypted object and structured data storage sized from validated source volumes",
        "security_controls": "Role-based access, encryption, secrets management, PII masking, monitoring, and audit logging",
        "data_access_restrictions": "Least-privilege access; raw sensitive data restricted to approved teams",
        "estimated_monthly_cost": "Pilot estimate to be validated with the selected cloud and usage profile",
    }


def show_stepper(active_step):
    cols = st.columns([1.02, 1.25, .72, .9])
    for index, (col, label) in enumerate(zip(cols, STAGES), start=1):
        with col:
            st.markdown(f'<span class="infra-step-marker {"infra-step-active" if index == active_step else ""}"></span>', unsafe_allow_html=True)
            if st.button(f"{index}  {label}", key=f"infra_nav_{index}", use_container_width=True):
                st.session_state.infra_step = index
                st.session_state[project_step_key] = index
                st.rerun()


def action_row(back_step=None, next_step=None, next_label="Next"):
    st.markdown('<span class="infra-actions"></span>', unsafe_allow_html=True)
    left, spacer, right = st.columns([1.1, 6, 2.8])
    with left:
        if back_step and st.button("← Back", key=f"back_{back_step}_{next_step}", use_container_width=True):
            st.session_state.infra_step = back_step
            st.session_state[project_step_key] = back_step
            st.rerun()
    with right:
        if next_step and st.button(next_label, key=f"next_{back_step}_{next_step}", use_container_width=True):
            st.session_state.infra_step = next_step
            st.session_state[project_step_key] = next_step
            st.rerun()


projects = get_approved_projects()
if not projects:
    st.warning("No approved projects are available. Complete Portfolio Gate Review and approve a project first.")
    st.stop()

project_map = {f"{p['id']} — {p['problem_statement']}": p for p in projects}
st.markdown('<div class="infra-project-label">APPROVED PROJECT</div>', unsafe_allow_html=True)
selected = st.selectbox("Approved project", list(project_map), label_visibility="collapsed")
st.markdown('<div class="infra-project-help">Infrastructure decisions and evidence are saved separately for the selected project.</div>', unsafe_allow_html=True)
project = project_map[selected]
project_id = project["id"]

prototype_spec = load_prototype_spec(project_id) or {}
hypotheses = [h for h in load_hypotheses(project_id) if h.get("status") == "Approved"]
experiments = [e for e in load_experiments(project_id) if e.get("status") == "Approved"]
review = load_infrastructure_review(project_id) or {}
saved_output = load_infrastructure_output(project_id) or {}

project_step_key = f"infra_step_{project_id}"
if project_step_key not in st.session_state:
    st.session_state[project_step_key] = 1
st.session_state.infra_step = st.session_state[project_step_key]
show_stepper(st.session_state.infra_step)
step = st.session_state.infra_step


if step == 1:
    with st.container(border=True):
        st.markdown('<div class="infra-card-title">Infrastructure Decision Intake</div>', unsafe_allow_html=True)
        st.markdown('<div class="infra-stakeholders">Stakeholders: Infrastructure Lead · Business Owner · Data Team</div>', unsafe_allow_html=True)
        with st.form("infrastructure_intake"):
            decisions = [
                ("Will the solution use a closed LLM or open LLM?", "llm_type", ["Closed LLM", "Open LLM", "Both", "TBD"]),
                ("Will deployment be cloud, on-prem, or hybrid?", "deployment", ["Cloud", "On-Prem", "Hybrid", "TBD"]),
                ("Is the use case batch, near-real-time, or real-time?", "processing", ["Batch", "Near-Real-Time", "Real-Time"]),
                ("Is the usage continuous or seasonal/spike-based?", "usage", ["Continuous", "Spike-Based", "Seasonal"]),
                ("Does training or fine-tuning happen?", "training", ["Yes", "No", "Later"]),
                ("Is this RAG-only, fine-tuning, or hybrid?", "architecture", ["RAG Only", "Fine-Tuning", "Hybrid", "Neither"]),
                ("Is customer data confidential?", "confidential", ["Yes", "No", "Partial"]),
            ]
            values = {}
            for question, key, options in decisions:
                qcol, acol = st.columns([5.8, 4.2], vertical_alignment="center")
                qcol.markdown(f'<div class="infra-question">{question}</div>', unsafe_allow_html=True)
                current = review.get(key, options[0])
                if current not in options:
                    current = options[0]
                values[key] = acol.segmented_control(question, options, default=current, key=f"intake_{project_id}_{key}", label_visibility="collapsed") or current
                st.divider()

            qcol, acol = st.columns([7.6, 2.4], vertical_alignment="center")
            qcol.markdown('<div class="infra-field-label">What is expected user volume in Phase 1?</div>', unsafe_allow_html=True)
            values["users"] = acol.text_input("Expected users", value=str(review.get("users", "")), placeholder="e.g. 50 internal users", label_visibility="collapsed")
            st.divider()
            qcol, acol = st.columns([7.6, 2.4], vertical_alignment="center")
            qcol.markdown('<div class="infra-field-label">What is expected request volume per day?</div>', unsafe_allow_html=True)
            values["requests_per_day"] = acol.text_input("Requests per day", value=str(review.get("requests_per_day", "")), placeholder="e.g. 200 requests/day", label_visibility="collapsed")
            st.divider()
            _, submit_col = st.columns([7, 3])
            submitted = submit_col.form_submit_button("Generate AI Recommendation →", use_container_width=True)

        if submitted:
            review.update(values)
            save_infrastructure_review(project_id, review)
            with st.spinner("Generating the model and compute recommendation…"):
                try:
                    recommendation = generate_infrastructure_recommendation(project, hypotheses, experiments, prototype_spec, review)
                    if not recommendation.get("recommendations"):
                        raise ValueError("No recommendations returned")
                except Exception:
                    recommendation = fallback_recommendation(review)
                saved_output["recommendation"] = recommendation
                save_infrastructure_output(project_id, saved_output)
            st.session_state.infra_step = 2
            st.session_state[project_step_key] = 2
            st.rerun()


elif step == 2:
    recommendation = saved_output.get("recommendation") or fallback_recommendation(review)
    if "recommendation" not in saved_output:
        saved_output["recommendation"] = recommendation
        save_infrastructure_output(project_id, saved_output)
    with st.container(border=True):
        st.markdown('<div class="infra-card-title">Model and Compute Recommendation</div>', unsafe_allow_html=True)
        heads = st.columns([1.7, 3.7, 4.5])
        for col, label in zip(heads, ["Decision Area", "AI Recommendation", "Reasoning"]):
            col.markdown(f'<div class="infra-table-head">{label}</div>', unsafe_allow_html=True)
        for row in recommendation.get("recommendations", []):
            cols = st.columns([1.7, 3.7, 4.5])
            cols[0].markdown(f'<div class="infra-table-cell infra-table-area">{row.get("area", "")}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="infra-table-cell infra-table-recommendation">{row.get("recommendation", "")}</div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="infra-table-cell infra-table-copy">{row.get("reason", row.get("reasoning", ""))}</div>', unsafe_allow_html=True)
    action_row(1, 3, "Next → Security Review →")


elif step == 3:
    with st.container(border=True):
        st.markdown('<div class="infra-card-title">Security Review</div>', unsafe_allow_html=True)
        with st.form("security_review"):
            answers = {}
            current_answers = review.get("security", {})
            for index, (category, question) in enumerate(SECURITY_QUESTIONS):
                qcol, acol = st.columns([7.5, 2.5], vertical_alignment="center")
                qcol.markdown(f'<div class="security-title">{category}</div><div class="security-question">{question}</div>', unsafe_allow_html=True)
                current = current_answers.get(question, "Partial")
                if current not in ["Yes", "No", "Partial"]:
                    current = "Partial"
                answers[question] = acol.segmented_control(question, ["Yes", "No", "Partial"], default=current, key=f"security_{project_id}_{index}", label_visibility="collapsed") or current
                st.divider()
            left, _, right = st.columns([1.1, 6, 2.8])
            back = left.form_submit_button("← Back", use_container_width=True)
            next_security = right.form_submit_button("Generate Infrastructure Output →", use_container_width=True)
        if back:
            st.session_state.infra_step = 2
            st.session_state[project_step_key] = 2
            st.rerun()
        if next_security:
            review["security"] = answers
            save_infrastructure_review(project_id, review)
            with st.spinner("Generating the infrastructure output…"):
                try:
                    final_output = generate_infrastructure_output(project, prototype_spec, saved_output.get("recommendation", fallback_recommendation(review)), answers)
                    if not final_output.get("deployment_recommendation"):
                        raise ValueError("No infrastructure output returned")
                except Exception:
                    final_output = fallback_output(review)
                saved_output["final_output"] = final_output
                save_infrastructure_output(project_id, saved_output)
            st.session_state.infra_step = 4
            st.session_state[project_step_key] = 4
            st.rerun()


elif step == 4:
    final_output = saved_output.get("final_output") or fallback_output(review)
    field_map = [
        ("Deployment Recommendation", "deployment_recommendation"),
        ("Training Requirement", "training_requirement"),
        ("Inference Requirement", "inference_requirement"),
        ("Compute Estimate", "compute_estimate"),
        ("Storage Estimate", "storage_estimate"),
        ("Security Controls", "security_controls"),
        ("Data Access Restrictions", "data_access_restrictions"),
        ("Estimated Infra Cost", "estimated_monthly_cost"),
    ]
    with st.container(border=True):
        st.markdown('<div class="infra-card-title">Infrastructure Output Summary</div>', unsafe_allow_html=True)
        with st.form("infrastructure_output"):
            edited = {}
            for label, key in field_map:
                lcol, fcol = st.columns([2, 8], vertical_alignment="center")
                lcol.markdown(f'<div class="output-label">{label}</div>', unsafe_allow_html=True)
                edited[key] = fcol.text_input(label, value=str(final_output.get(key, "")), label_visibility="collapsed")
                st.divider()
            lcol, fcol = st.columns([4.8, 5.2], vertical_alignment="center")
            lcol.markdown('<div class="output-label">Approval Status</div>', unsafe_allow_html=True)
            options = ["Approved", "Approved with Conditions", "Requires Further Review"]
            current_decision = saved_output.get("decision", "Requires Further Review")
            decision = fcol.segmented_control("Approval Status", options, default=current_decision if current_decision in options else options[-1], label_visibility="collapsed") or current_decision
            comments = st.text_area("Reviewer Comments", value=saved_output.get("comments", ""), placeholder="Record conditions, owners, and follow-up actions…")
            st.markdown('<span class="infra-save"></span>', unsafe_allow_html=True)
            saved = st.form_submit_button("✓  Save Infrastructure Output", use_container_width=False)
        if saved:
            saved_output["final_output"] = edited
            saved_output["decision"] = decision
            saved_output["comments"] = comments
            save_infrastructure_output(project_id, saved_output)
            st.success("Infrastructure output saved successfully.")
    action_row(3, None)
    _, right = st.columns([7, 3])
    if right.button("Proceed → Operational Integration & Metrics", use_container_width=True):
        st.switch_page("pages/10_PE_Workflow.py")


st.session_state[project_step_key] = st.session_state.infra_step
