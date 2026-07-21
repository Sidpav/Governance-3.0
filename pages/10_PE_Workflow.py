import streamlit as st

from database.project_execution_repository import (
    get_approved_projects,
    load_workflow,
    save_workflow,
)
from ui.auth import require_access, require_login
from ui.navbar import render_breadcrumb, render_navbar
from ui.sidebar import render_sidebar
from ui.theme import apply_theme


st.set_page_config(
    page_title="Operational Integration & Metrics",
    page_icon="🔄",
    layout="wide",
)
user = require_login()
apply_theme()
render_sidebar("pe_workflow")
render_navbar("pe_workflow")
require_access("pe_workflow")
render_breadcrumb("AI Delivery & Operational Readiness", "Operational Integration & Metrics")

st.markdown(
    """
    <style>
    section.main > div.block-container {padding-top:0!important}
    .cx-breadcrumb {display:none!important}
    .wf-label {font-size:.78rem;font-weight:800;letter-spacing:.06em;color:#627695;margin:16px 0 5px}
    .wf-help {font-size:.84rem;color:#8ea2c3;margin:-2px 0 15px}
    .wf-marker,.wf-active,.wf-done {display:none}
    div[data-testid="stHorizontalBlock"]:has(.wf-marker){width:calc(100% + 4.4rem);margin:0 -2.2rem 24px;padding:7px 25px;background:#fff;border-bottom:1px solid #d9e2f0;gap:8px}
    div[data-testid="stHorizontalBlock"]:has(.wf-marker) .stButton>button{width:100%;min-height:42px;background:transparent!important;border:0!important;box-shadow:none!important;color:#91a3bf!important;font-size:.91rem;line-height:1.15;white-space:normal;padding:3px}
    div[data-testid="column"]:has(.wf-active) .stButton>button{color:#155eef!important}
    div[data-testid="column"]:has(.wf-done) .stButton>button{color:#00a36c!important;font-weight:800!important}
    .wf-card-title{font-size:1.15rem;font-weight:800;color:#10203e;margin:2px 0 16px}
    .wf-section{font-size:1.08rem;font-weight:800;color:#10203e;margin:6px 0 12px}
    .wf-pipeline{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin:4px 0 10px}
    .wf-chip{display:inline-flex;align-items:center;padding:7px 14px;border:1px solid #afd0ff;border-radius:999px;background:#eef5ff;color:#155eef;font-weight:750;font-size:.9rem}
    .wf-arrow{color:#8ea2c3;font-size:1.1rem}
    .wf-head{color:#526a90;font-size:.94rem;font-weight:800;padding:10px 4px;border-bottom:1px solid #d9e2f0}
    .wf-name{color:#10203e;font-weight:800;font-size:.93rem;padding:12px 4px}
    .wf-copy{color:#405678;font-size:.91rem;line-height:1.35;padding:12px 4px}
    div[data-testid="stHorizontalBlock"]:has(.wf-row){align-items:center;border-bottom:1px solid #e7edf6;padding:2px 0}
    .wf-row{display:none}
    [data-testid="stSegmentedControl"] button,[data-testid="stButtonGroup"] button{min-height:40px!important;background:#fff!important;color:#405678!important;border-color:#d9e2f0!important;font-weight:750!important}
    [data-testid="stSegmentedControl"] button[aria-pressed="true"],[data-testid="stButtonGroup"] button[aria-pressed="true"]{background:#eaf1ff!important;color:#155eef!important;border-color:#8bb4ff!important}
    [data-testid="stSegmentedControl"] button p,[data-testid="stButtonGroup"] button p{color:inherit!important}
    div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:#d9e2f0!important;padding:5px 4px}
    div[data-testid="stVerticalBlockBorderWrapper"]>div{padding-left:8px!important;padding-right:8px!important}
    .wf-actions{display:none}
    div[data-testid="stHorizontalBlock"]:has(.wf-actions){margin-top:20px;align-items:center}
    div[data-testid="stHorizontalBlock"]:has(.wf-actions) [data-testid="column"]:first-child .stButton>button{background:#fff!important;color:#10203e!important;border:1px solid #d9e2f0!important}
    .wf-ready{display:flex;gap:11px;align-items:center;padding:7px 0;color:#10203e;font-weight:700}
    .wf-check{width:25px;height:25px;border-radius:6px;display:inline-flex;align-items:center;justify-content:center;background:#00a36c;color:white}
    .wf-missing{background:#fff;border:2px solid #9aabc3;color:transparent}
    .wf-add-marker{display:none}
    div[data-testid="stElementContainer"]:has(.wf-add-marker)+div .stButton>button{background:#fff!important;color:#155eef!important;border:1px dashed #8bb4ff!important;box-shadow:none!important}
    .wf-save-marker{display:none}
    div[data-testid="stElementContainer"]:has(.wf-save-marker)+div .stButton>button{background:#00a36c!important;border-color:#00a36c!important}
    @media(max-width:900px){div[data-testid="stHorizontalBlock"]:has(.wf-marker){overflow-x:auto}.wf-head{display:none}}
    </style>
    """,
    unsafe_allow_html=True,
)

STAGES = ["Workflow Placement", "Recommended Performance Metrics", "Explainability", "Consumability", "Workflow Output"]
OWNERS = ["— Select Owner —", "Business Owner", "Program Lead", "Product Lead", "Data Lead", "Engineering Lead", "Customer Success Lead", "Compliance Lead", "Infrastructure Lead", "Finance Lead"]


def defaults(project):
    text = " ".join(str(project.get(k, "")) for k in ("problem_statement", "business_objective", "solution_approach")).lower()
    learning = any(x in text for x in ("learner", "learning", "education", "certification", "skills"))
    if learning:
        pipeline = ["Learner Signals", "Readiness Assessment", "Skill-Gap Classification", "Pathway Prioritization", "Learning Recommendation", "Human Review", "Learner Intervention", "Outcome Tracking"]
        placements = [
            ("Learner profile review", "Shows learner readiness, evidence, and identified skill gaps"),
            ("Learning pathway planning", "Ranks relevant courses and certification preparation resources"),
            ("Assessment support", "Flags uncertain or high-impact recommendations for educator review"),
            ("Learner engagement", "Creates a targeted outreach and support queue"),
            ("Content review", "Summarises recurring skill gaps and content needs"),
            ("Certification readiness", "Supports readiness review without automatic certification decisions"),
            ("Program leadership review", "Tracks participation, readiness, fairness, and realized value"),
        ]
        business = [
            ("Certification readiness", "Improve evidence-based readiness", "+12% ready learners in 6 months"),
            ("Learning completion", "Increase pathway completion", "+8% completion in 12 months"),
            ("Learner confidence", "Improve confidence in recommendations", "≥80% positive feedback"),
            ("Participation equity", "Monitor equitable participation", "No material group disparity"),
            ("Recommendation adoption", "Measure intervention effectiveness", "≥60% accepted pathways"),
        ]
        technical = [
            ("Readiness engine", "Precision, recall, false positives, false negatives", "AUC ≥ 0.75"),
            ("Skill classifier", "Skill-gap classification accuracy", "Accuracy ≥ 70%"),
            ("Pathway ranker", "Ranking quality and policy match", "Top-10 precision ≥ 0.80"),
            ("Recommendation engine", "Acceptance rate and relevance", "Acceptance ≥ 60%"),
            ("RAG / explanation layer", "Citation accuracy and groundedness", "Groundedness ≥ 85%"),
            ("Overall system", "Latency, uptime, and error rate", "Latency < 2s; uptime ≥ 99%"),
        ]
    else:
        pipeline = ["Business Signals", "Risk Detection", "Outcome Classification", "Priority Scoring", "Recommended Action", "Human Approval", "Operational Intervention", "Outcome Tracking"]
        placements = [
            ("Business review", "Shows prioritized cases and supporting evidence"),
            ("Operational planning", "Flags cases requiring timely action"),
            ("Service handling", "Triggers a priority alert for high-impact cases"),
            ("Business operations", "Creates a governed action queue"),
            ("Product review", "Summarises product-related signals and outcomes"),
            ("Financial approval", "Routes financial actions to an accountable human"),
            ("Leadership review", "Tracks risk, value, and realized outcomes"),
        ]
        business = [
            ("Outcome improvement", "Improve the target business outcome", "5% improvement in 12 months"),
            ("Process efficiency", "Reduce manual processing effort", "20% cycle-time reduction"),
            ("Value protected", "Protect measurable business value", "Target confirmed by owner"),
            ("High-value case success", "Improve outcomes for priority cases", "≥60% successful actions"),
        ]
        technical = [
            ("Risk engine", "Precision, recall, false positives, false negatives", "AUC ≥ 0.75"),
            ("Classification engine", "Classification accuracy", "Accuracy ≥ 70%"),
            ("Prioritization engine", "Ranking quality and business-rule match", "Top-10 precision ≥ 0.80"),
            ("Recommendation engine", "Acceptance rate and relevance", "Acceptance ≥ 60%"),
            ("RAG / explanation layer", "Citation accuracy and groundedness", "Groundedness ≥ 85%"),
            ("Overall system", "Latency, uptime, error rate", "Latency < 2s; uptime ≥ 99%"),
        ]
    environmental = [
        ("Model size suitability", "Ensure model is fit-for-purpose", "Use smallest effective model"),
        ("Token usage per recommendation", "Control LLM cost and energy", "< 1,000 tokens/recommendation"),
        ("Batch vs real-time split", "Minimise unnecessary compute", "> 90% batch where appropriate"),
        ("GPU hours", "Track compute carbon impact", "GPU only for approved heavy workloads"),
        ("Storage footprint", "Control data storage growth", "< 100GB for Phase 1"),
        ("Cost per recommendation", "Measure delivery efficiency", "< $0.05/recommendation"),
    ]
    explain = [
        ("Business Head", "Why the case is prioritized and its business impact", "Executive summary"),
        ("Operations / Customer Success", "Why the case is high priority and what action is recommended", "Case-level card"),
        ("Support Team", "Why this case needs priority escalation", "Operational alert"),
        ("Product Lead", "Which product issue is linked to the outcome", "Product theme report"),
        ("Data Lead", "Which signals and features contributed to the score", "Feature importance view"),
        ("Compliance Lead", "Whether the recommendation is explainable, auditable, and human-approved", "Audit log"),
        ("Infrastructure Lead", "System health, latency, failure points, and usage load", "Monitoring dashboard"),
    ]
    consume = [
        ("Business Head", "Executive dashboard", "Summary view", "Weekly email + dashboard"),
        ("Operations Head", "Prioritized case list", "Case list", "Business system integration"),
        ("Customer Success", "Action queue", "Customer / learner level", "Operational tool"),
        ("Support", "Case-level alert", "Case view", "Support ticketing system"),
        ("Product", "Theme summary", "Aggregated", "Product review report"),
        ("Finance", "Approval queue", "Approval-only", "Finance approval workflow"),
        ("Compliance", "Audit and policy view", "Read-only audit", "Compliance portal"),
        ("Infrastructure", "System monitoring dashboard", "Technical view", "Monitoring tool"),
    ]
    return {"pipeline": pipeline, "placements": placements, "business": business, "technical": technical, "environmental": environmental, "explainability": explain, "consumability": consume}


def row_value(saved, area, index, field, fallback=""):
    try:
        return saved[area][index].get(field, fallback)
    except (KeyError, IndexError, TypeError):
        return fallback


def decision_default(value):
    """Map previously saved labels to the new two-state decision language."""
    return "Approve" if value in {"Approve", "Approved", "Defined", "Complete"} else "Ignore"


def custom_rows(area):
    """Keep saved user-added rows and any new unsaved rows for this session."""
    saved_custom = [row for row in saved.get(area, []) if row.get("custom")]
    key = f"wf_added_{project_id}_{area}"
    st.session_state.setdefault(key, len(saved_custom))
    rows = list(saved_custom)
    while len(rows) < st.session_state[key]:
        rows.append({"custom": True})
    return rows


def add_row_button(area, label):
    key = f"wf_added_{project_id}_{area}"
    st.session_state.setdefault(key, len([r for r in saved.get(area, []) if r.get("custom")]))
    st.markdown('<span class="wf-add-marker"></span>', unsafe_allow_html=True)
    if st.button(f"＋ {label}", key=f"wf_add_{project_id}_{area}"):
        st.session_state[key] += 1
        st.rerun()


def stepper(active, completed):
    cols = st.columns([1.05, 1.15, .82, .82, .95])
    for i, (col, label) in enumerate(zip(cols, STAGES), 1):
        state = "wf-active" if i == active else "wf-done" if i in completed else ""
        icon = "✓  " if i in completed else ""
        with col:
            st.markdown(f'<span class="wf-marker {state}"></span>', unsafe_allow_html=True)
            if st.button(f"{icon}{label}", key=f"wf_nav_{project_id}_{i}", use_container_width=True):
                st.session_state[step_key] = i
                st.rerun()


def actions(back=None, nxt=None, label="Next →"):
    st.markdown('<span class="wf-actions"></span>', unsafe_allow_html=True)
    left, _, right = st.columns([1.1, 6, 2.6])
    if back and left.button("← Back", key=f"wf_back_{project_id}_{back}_{nxt}", use_container_width=True):
        st.session_state[step_key] = back; st.rerun()
    if nxt and right.button(label, key=f"wf_next_{project_id}_{back}_{nxt}", type="primary", use_container_width=True):
        st.session_state[step_key] = nxt; st.rerun()


projects = get_approved_projects()
if not projects:
    st.warning("No approved projects are available. Approve a project in Portfolio Gate Review first.")
    st.stop()

project_map = {f"{p['id']} — {p['problem_statement']}": p for p in projects}
st.markdown('<div class="wf-label">APPROVED PROJECT</div>', unsafe_allow_html=True)
selected = st.selectbox("Approved project", list(project_map), label_visibility="collapsed")
st.markdown('<div class="wf-help">Workflow decisions, metrics, comments, and approvals are saved for this project.</div>', unsafe_allow_html=True)
project = project_map[selected]
project_id = project["id"]
saved = load_workflow(project_id)
content = defaults(project)
step_key = f"workflow_step_{project_id}"
st.session_state.setdefault(step_key, int(saved.get("active_step", 1)))
completed = set(saved.get("completed_steps", []))
stepper(st.session_state[step_key], completed)
step = st.session_state[step_key]


if step == 1:
    with st.container(border=True):
        st.markdown('<div class="wf-card-title">Workflow Pipeline</div>', unsafe_allow_html=True)
        chips = "".join(f'<span class="wf-chip">{x}</span>{"<span class=\"wf-arrow\">›</span>" if i < len(content["pipeline"])-1 else ""}' for i, x in enumerate(content["pipeline"]))
        st.markdown(f'<div class="wf-pipeline">{chips}</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="wf-card-title">Recommended Workflow Placement</div>', unsafe_allow_html=True)
        add_row_button("placements", "Add workflow placement")
        h = st.columns([1.55, 2.15, 2.8, 2.3, 2.4])
        for col, title in zip(h, ["Workflow Area", "How the Prototype Fits", "Owner", "Decision", "Feedback / Comment"]): col.markdown(f'<div class="wf-head">{title}</div>', unsafe_allow_html=True)
        values = []
        with st.form(f"placement_{project_id}"):
            rows = [(a, f, False) for a, f in content["placements"]] + [(r.get("area", ""), r.get("fit", ""), True) for r in custom_rows("placements")]
            for i, (area, fit, custom) in enumerate(rows):
                cols = st.columns([1.55, 2.15, 2.8, 2.3, 2.4], vertical_alignment="center")
                cols[0].markdown('<span class="wf-row"></span>', unsafe_allow_html=True)
                if custom:
                    area = cols[0].text_input("Workflow area", value=area, key=f"pl_area_{project_id}_{i}", label_visibility="collapsed", placeholder="Workflow area")
                    fit = cols[1].text_input("Prototype fit", value=fit, key=f"pl_fit_{project_id}_{i}", label_visibility="collapsed", placeholder="How the prototype fits")
                else:
                    cols[0].markdown(f'<div class="wf-name">{area}</div>', unsafe_allow_html=True)
                    cols[1].markdown(f'<div class="wf-copy">{fit}</div>', unsafe_allow_html=True)
                old_owner = row_value(saved, "placements", i, "owner", OWNERS[0]); old_owner = old_owner if old_owner in OWNERS else OWNERS[0]
                owner = cols[2].selectbox("Owner", OWNERS, index=OWNERS.index(old_owner), key=f"pl_owner_{project_id}_{i}", label_visibility="collapsed")
                status = cols[3].segmented_control("Decision", ["Approve", "Ignore"], default=decision_default(row_value(saved, "placements", i, "status", "Ignore")), key=f"pl_status_{project_id}_{i}", label_visibility="collapsed") or "Ignore"
                comment = cols[4].text_input("Feedback / Comment", value=row_value(saved, "placements", i, "comment"), key=f"pl_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add feedback…")
                values.append({"area": area, "fit": fit, "owner": owner, "status": status, "comment": comment, "custom": custom})
            submitted = st.form_submit_button("Save & Continue →", type="primary", use_container_width=True)
        if submitted:
            saved["pipeline"] = content["pipeline"]; saved["placements"] = values
            completed.add(1); saved["completed_steps"] = sorted(completed); saved["active_step"] = 2
            save_workflow(project_id, saved); st.session_state[step_key] = 2; st.rerun()


elif step == 2:
    metric_groups = [("Recommended Business Metrics", "business"), ("Recommended Technical Metrics by Component", "technical"), ("Recommended Environmental / Green Metrics", "environmental")]
    for title, key in metric_groups:
        add_row_button(key, f"Add {title.removeprefix('Recommended ').lower().rstrip('s')}")
    with st.form(f"metrics_{project_id}"):
        for title, key in metric_groups:
            with st.container(border=True):
                st.markdown(f'<div class="wf-card-title">{title}</div>', unsafe_allow_html=True)
                h = st.columns([1.7, 2.15, 1.8, 1.25, 2.2])
                labels = ["Metric" if key != "technical" else "Component", "Purpose" if key != "technical" else "Technical Metric", "Target", "Decision", "Feedback / Comment"]
                for col, label in zip(h, labels): col.markdown(f'<div class="wf-head">{label}</div>', unsafe_allow_html=True)
                result = []
                rows = [(n, p, t, False) for n, p, t in content[key]] + [(r.get("name", ""), r.get("purpose", ""), r.get("target", ""), True) for r in custom_rows(key)]
                for i, (name, purpose, target, custom) in enumerate(rows):
                    c = st.columns([1.7, 2.15, 1.8, 1.25, 2.2], vertical_alignment="center")
                    c[0].markdown('<span class="wf-row"></span>', unsafe_allow_html=True)
                    if custom:
                        name = c[0].text_input("Metric", value=name, key=f"{key}_name_{project_id}_{i}", label_visibility="collapsed", placeholder="Metric / component")
                        purpose = c[1].text_input("Purpose", value=purpose, key=f"{key}_purpose_{project_id}_{i}", label_visibility="collapsed", placeholder="Purpose")
                        target = c[2].text_input("Target", value=target, key=f"{key}_target_{project_id}_{i}", label_visibility="collapsed", placeholder="Target")
                    else:
                        c[0].markdown(f'<div class="wf-name">{name}</div>', unsafe_allow_html=True)
                        c[1].markdown(f'<div class="wf-copy">{purpose}</div>', unsafe_allow_html=True); c[2].markdown(f'<div class="wf-copy">{target}</div>', unsafe_allow_html=True)
                    status = c[3].segmented_control("Decision", ["Approve", "Ignore"], default=decision_default(row_value(saved, key, i, "status", "Ignore")), key=f"{key}_status_{project_id}_{i}", label_visibility="collapsed") or "Ignore"
                    comment = c[4].text_input("Feedback / Comment", value=row_value(saved, key, i, "comment"), key=f"{key}_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add feedback…")
                    result.append({"name": name, "purpose": purpose, "target": target, "status": status, "comment": comment, "custom": custom})
                st.session_state[f"wf_tmp_{project_id}_{key}"] = result
        submitted = st.form_submit_button("Save Metrics & Continue →", type="primary", use_container_width=True)
    if submitted:
        for _, key in metric_groups: saved[key] = st.session_state[f"wf_tmp_{project_id}_{key}"]
        completed.add(2); saved["completed_steps"] = sorted(completed); saved["active_step"] = 3
        save_workflow(project_id, saved); st.session_state[step_key] = 3; st.rerun()
    actions(1)


elif step == 3:
    with st.container(border=True):
        st.markdown('<div class="wf-card-title">Recommended Explainability by Stakeholder</div>', unsafe_allow_html=True)
        add_row_button("explainability", "Add stakeholder requirement")
        h = st.columns([1.55, 3.6, 1.55, 1.25, 2.1])
        for col, title in zip(h, ["Stakeholder", "Explanation Needed", "Format", "Decision", "Feedback / Comment"]): col.markdown(f'<div class="wf-head">{title}</div>', unsafe_allow_html=True)
        values = []
        with st.form(f"explain_{project_id}"):
            rows = [(w, n, f, False) for w, n, f in content["explainability"]] + [(r.get("stakeholder", ""), r.get("need", ""), r.get("format", ""), True) for r in custom_rows("explainability")]
            for i, (who, need, fmt, custom) in enumerate(rows):
                c = st.columns([1.55, 3.6, 1.55, 1.25, 2.1], vertical_alignment="center")
                c[0].markdown('<span class="wf-row"></span>', unsafe_allow_html=True)
                if custom:
                    who = c[0].text_input("Stakeholder", value=who, key=f"ex_who_{project_id}_{i}", label_visibility="collapsed", placeholder="Stakeholder")
                    need = c[1].text_input("Explanation needed", value=need, key=f"ex_need_{project_id}_{i}", label_visibility="collapsed", placeholder="Explanation needed")
                    fmt = c[2].text_input("Format", value=fmt, key=f"ex_fmt_{project_id}_{i}", label_visibility="collapsed", placeholder="Format")
                else:
                    c[0].markdown(f'<div class="wf-name">{who}</div>', unsafe_allow_html=True); c[1].markdown(f'<div class="wf-copy">{need}</div>', unsafe_allow_html=True); c[2].markdown(f'<div class="wf-copy">{fmt}</div>', unsafe_allow_html=True)
                status = c[3].segmented_control("Decision", ["Approve", "Ignore"], default=decision_default(row_value(saved, "explainability", i, "status", "Ignore")), key=f"ex_status_{project_id}_{i}", label_visibility="collapsed") or "Ignore"
                comment = c[4].text_input("Feedback / Comment", value=row_value(saved, "explainability", i, "comment"), key=f"ex_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add feedback…")
                values.append({"stakeholder": who, "need": need, "format": fmt, "status": status, "comment": comment, "custom": custom})
            submitted = st.form_submit_button("Save Explainability & Continue →", type="primary", use_container_width=True)
    if submitted:
        saved["explainability"] = values; completed.add(3); saved["completed_steps"] = sorted(completed); saved["active_step"] = 4
        save_workflow(project_id, saved); st.session_state[step_key] = 4; st.rerun()
    actions(2)


elif step == 4:
    with st.container(border=True):
        st.markdown('<div class="wf-card-title">Recommended Consumability</div>', unsafe_allow_html=True)
        add_row_button("consumability", "Add consumability view")
        h = st.columns([1.2, 1.7, 1.45, 1.8, 1.15, 1.9])
        for col, title in zip(h, ["User", "Format", "Access Level", "Delivery Mechanism", "Decision", "Feedback / Comment"]): col.markdown(f'<div class="wf-head">{title}</div>', unsafe_allow_html=True)
        values = []
        with st.form(f"consume_{project_id}"):
            rows = [(w, f, a, d, False) for w, f, a, d in content["consumability"]] + [(r.get("user", ""), r.get("format", ""), r.get("access", ""), r.get("delivery", ""), True) for r in custom_rows("consumability")]
            for i, (who, fmt, access, delivery, custom) in enumerate(rows):
                c = st.columns([1.2, 1.7, 1.45, 1.8, 1.15, 1.9], vertical_alignment="center")
                c[0].markdown('<span class="wf-row"></span>', unsafe_allow_html=True)
                if custom:
                    who = c[0].text_input("User", value=who, key=f"co_who_{project_id}_{i}", label_visibility="collapsed", placeholder="User")
                    fmt = c[1].text_input("Format", value=fmt, key=f"co_fmt_{project_id}_{i}", label_visibility="collapsed", placeholder="Format")
                    access = c[2].text_input("Access", value=access, key=f"co_access_{project_id}_{i}", label_visibility="collapsed", placeholder="Access level")
                    delivery = c[3].text_input("Delivery", value=delivery, key=f"co_delivery_{project_id}_{i}", label_visibility="collapsed", placeholder="Delivery mechanism")
                else:
                    c[0].markdown(f'<div class="wf-name">{who}</div>', unsafe_allow_html=True); c[1].markdown(f'<div class="wf-copy">{fmt}</div>', unsafe_allow_html=True); c[2].markdown(f'<div class="wf-copy">{access}</div>', unsafe_allow_html=True); c[3].markdown(f'<div class="wf-copy">{delivery}</div>', unsafe_allow_html=True)
                status = c[4].segmented_control("Decision", ["Approve", "Ignore"], default=decision_default(row_value(saved, "consumability", i, "status", "Ignore")), key=f"co_status_{project_id}_{i}", label_visibility="collapsed") or "Ignore"
                comment = c[5].text_input("Feedback / Comment", value=row_value(saved, "consumability", i, "comment"), key=f"co_comment_{project_id}_{i}", label_visibility="collapsed", placeholder="Add feedback…")
                values.append({"user": who, "format": fmt, "access": access, "delivery": delivery, "status": status, "comment": comment, "custom": custom})
            owner_cols = st.columns([1.2, 3, 5.8], vertical_alignment="center")
            owner_cols[0].markdown('<div class="wf-name">Workflow Owner:</div>', unsafe_allow_html=True)
            owner = owner_cols[1].text_input("Workflow Owner", value=saved.get("workflow_owner", ""), label_visibility="collapsed", placeholder="Enter workflow owner")
            submitted = st.form_submit_button("Assign & Continue →", type="primary", use_container_width=True)
    if submitted:
        saved["consumability"] = values; saved["workflow_owner"] = owner.strip(); completed.add(4); saved["completed_steps"] = sorted(completed); saved["active_step"] = 5
        save_workflow(project_id, saved); st.session_state[step_key] = 5; st.rerun()
    actions(3)


else:
    requirements = [
        ("Workflow placement approved", any(decision_default(x.get("status")) == "Approve" for x in saved.get("placements", []))),
        ("Recommended business metrics approved", any(decision_default(x.get("status")) == "Approve" for x in saved.get("business", []))),
        ("Recommended technical metrics approved", any(decision_default(x.get("status")) == "Approve" for x in saved.get("technical", []))),
        ("Recommended environmental metrics approved", any(decision_default(x.get("status")) == "Approve" for x in saved.get("environmental", []))),
        ("Explainability requirements approved", any(decision_default(x.get("status")) == "Approve" for x in saved.get("explainability", []))),
        ("Consumability views approved", any(decision_default(x.get("status")) == "Approve" for x in saved.get("consumability", []))),
        ("Workflow owner assigned", bool(saved.get("workflow_owner", "").strip())),
    ]
    with st.container(border=True):
        st.markdown('<div class="wf-card-title">Workflow Output</div>', unsafe_allow_html=True)
        for label, ready in requirements:
            st.markdown(f'<div class="wf-ready"><span class="wf-check {"" if ready else "wf-missing"}">✓</span>{label}</div>', unsafe_allow_html=True)
        if all(ready for _, ready in requirements):
            st.success("All workflow evidence is complete and ready to save.")
        else:
            st.info("Complete the outstanding items above. You can use the stage navigation to return to any section.")
        st.markdown('<span class="wf-save-marker"></span>', unsafe_allow_html=True)
        if st.button("✓  Save Workflow Output", type="primary", disabled=not all(ready for _, ready in requirements)):
            saved["output_saved"] = True; saved["saved_by"] = user["email"]; completed.add(5); saved["completed_steps"] = sorted(completed); saved["active_step"] = 5
            save_workflow(project_id, saved); st.success("Workflow output saved and ready for governance review."); st.rerun()
    actions(4)
