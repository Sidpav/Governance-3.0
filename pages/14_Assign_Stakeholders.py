# pages/14_Assign_Stakeholders.py
# Stakeholder Role Assignment — Business Leader only
# ─────────────────────────────────────────────────────────────────────────
# Lets the Business Leader select an approved AI use case and assign
# named individuals (name + email) to each delivery role. Once confirmed,
# saves assignments to session state and navigates to PE Assumptions
# (the Hypotheses page of AI Product Delivery).
# ─────────────────────────────────────────────────────────────────────────

import streamlit as st
import json

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar
from ui.auth import require_login, get_current_user

from database.db import db_load_all
from database.delivery_repository import load_assignments, save_assignment

st.set_page_config(
    page_title="Assign Stakeholders — Cortexa",
    page_icon="👥",
    layout="wide",
)

require_login()

user = get_current_user()
if not user or user.get("role") != "business_leader":
    st.switch_page("app.py")
    st.stop()

apply_theme()
render_sidebar(active="idea_submission")
render_navbar(active="m5")  # highlight Portfolio tab while on this page

# ──────────────────────────────────────────────────────────────────────────
# Delivery Roles Definition
# ──────────────────────────────────────────────────────────────────────────
DELIVERY_ROLES = [
    {
        "id": "data_lead",
        "label": "Data Lead",
        "description": "Owns data readiness assessment, structured & unstructured data validation.",
        "color_bg": "#EFF6FF",
        "color_border": "#93C5FD",
        "color_label": "#1D4ED8",
        "dot": "#3B82F6",
    },
    {
        "id": "infrastructure_lead",
        "label": "Infrastructure Lead",
        "description": "Owns infrastructure planning, MLOps stack, and deployment architecture.",
        "color_bg": "#FFF7ED",
        "color_border": "#FCD34D",
        "color_label": "#B45309",
        "dot": "#F59E0B",
    },
    {
        "id": "process_owner",
        "label": "Process Owner",
        "description": "Owns assumptions, hypothesis validation, and experiment design.",
        "color_bg": "#ECFDF5",
        "color_border": "#6EE7B7",
        "color_label": "#065F46",
        "dot": "#10B981",
    },
    {
        "id": "operations_manager",
        "label": "Operations Manager",
        "description": "Owns operational integration, workflow design, and execution approval.",
        "color_bg": "#FFF7ED",
        "color_border": "#FCD34D",
        "color_label": "#92400E",
        "dot": "#F59E0B",
    },
    {
        "id": "change_management_lead",
        "label": "Change Management Lead",
        "description": "Owns stakeholder adoption, training, and AI oversight evidence.",
        "color_bg": "#FFF1F2",
        "color_border": "#FCA5A5",
        "color_label": "#9F1239",
        "dot": "#EF4444",
    },
]

# ──────────────────────────────────────────────────────────────────────────
# Page Styles
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Full-page background */
section.main > div.block-container {
    max-width: 860px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Role assignment card */
.sa-role-card {
    border-radius: 14px;
    padding: 1.2rem 1.4rem 1rem;
    margin-bottom: 1.1rem;
    border: 1px solid;
}

/* Assigned tick */
.sa-assigned-badge {
    font-size: 0.75rem;
    font-weight: 700;
    color: #059669;
}

/* Inputs */
.sa-role-card input[type="text"] {
    background: #fff !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
}

/* Summary box */
.sa-summary {
    background: #FAFAFE;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    margin-top: 1.4rem;
    margin-bottom: 1.4rem;
}
.sa-summary-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.8rem;
}
.sa-summary-dot {
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-right: 7px;
    vertical-align: middle;
}

/* Confirm button override */
div[data-testid="stButton"]:has(#sa-confirm-btn) > button {
    background: #1B2D57 !important;
    color: white !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    height: 52px !important;
    border: none !important;
}
div[data-testid="stButton"]:has(#sa-confirm-btn) > button:hover {
    background: #2a4080 !important;
}

/* Info banner */
.sa-info-banner {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 1.4rem;
    font-size: 0.85rem;
    color: #1E40AF;
    line-height: 1.6;
}

/* Field label */
.sa-field-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #6B7280;
    margin-bottom: 4px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# Back link
# ──────────────────────────────────────────────────────────────────────────
if st.button("← Back to Portfolio Gate Review", key="sa_back"):
    st.switch_page("pages/5_Analytics_Dashboard.py")

st.markdown("## Stakeholder Role Assignment")
st.markdown(
    "Assign team members to their delivery roles for the selected AI initiative. "
    "Each stakeholder will see only the sections relevant to their role when they sign in."
)

st.write("")

# ──────────────────────────────────────────────────────────────────────────
# Project Selector
# ──────────────────────────────────────────────────────────────────────────
all_records = db_load_all()
approved = [r for r in all_records if r.get("status") == "Approved"]

if not approved:
    st.warning(
        "No **Approved** use cases found. "
        "Go to the Portfolio Gate Review, approve a use case, then return here to assign roles."
    )
    st.stop()

project_options = {r["id"]: r for r in approved}
project_names   = {r["id"]: f"{r['id']}  —  {(r.get('problem_statement') or '')[:72]}" for r in approved}

selected_pid = st.selectbox(
    "Select an approved AI use case",
    list(project_options.keys()),
    format_func=lambda pid: project_names[pid],
    key="sa_project_select",
    label_visibility="visible",
)

selected_project = project_options[selected_pid]
project_label    = (selected_project.get("problem_statement") or selected_pid)[:64]

st.write("")

# ──────────────────────────────────────────────────────────────────────────
# Info Banner
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="sa-info-banner">
      ℹ️ &nbsp;<b>Portfolio Approved</b> — The <i>{project_label}</i> use case has been approved
      by the governance board. As the <b>Business Leader</b>, you are now assigning delivery
      responsibilities. Each stakeholder will receive a targeted workspace aligned to their function.
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# Load previously saved assignments from session state
# ──────────────────────────────────────────────────────────────────────────
sa_key = f"sa_assignments_{selected_pid}"
if sa_key not in st.session_state:
    saved = {a["role_key"]: {"name": a["person_name"], "email": a["person_email"]}
             for a in load_assignments(selected_pid)}
    st.session_state[sa_key] = {
        r["id"]: saved.get(r["id"], {"name": "", "email": ""}) for r in DELIVERY_ROLES
    }

assignments = st.session_state[sa_key]

# ──────────────────────────────────────────────────────────────────────────
# Role Assignment Cards
# ──────────────────────────────────────────────────────────────────────────
updated = {}

for role in DELIVERY_ROLES:
    rid    = role["id"]
    saved  = assignments.get(rid, {"name": "", "email": ""})
    is_assigned = bool(saved.get("name") and saved.get("email"))

    assigned_badge = (
        '<span class="sa-assigned-badge">✓ Assigned</span>'
        if is_assigned else ""
    )

    st.markdown(
        f"""
        <div class="sa-role-card" style="
            background:{role['color_bg']};
            border-color:{role['color_border']};">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-size:0.88rem;font-weight:700;color:{role['color_label']};
                         background:rgba(255,255,255,0.55);padding:3px 10px;border-radius:999px;
                         border:1px solid {role['color_border']};">
              {role['label']}
            </span>
            {assigned_badge}
          </div>
          <div style="font-size:0.82rem;color:#4B5563;margin-bottom:0.3rem;">{role['description']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_name, col_email = st.columns(2)

    with col_name:
        st.markdown('<div class="sa-field-label">FULL NAME</div>', unsafe_allow_html=True)
        name_val = st.text_input(
            f"Full name — {role['label']}",
            value=saved.get("name", ""),
            placeholder="e.g. David Chen",
            key=f"sa_name_{rid}_{selected_pid}",
            label_visibility="collapsed",
        )

    with col_email:
        st.markdown('<div class="sa-field-label">EMAIL ADDRESS</div>', unsafe_allow_html=True)
        email_val = st.text_input(
            f"Email — {role['label']}",
            value=saved.get("email", ""),
            placeholder="e.g. david.chen@company.com",
            key=f"sa_email_{rid}_{selected_pid}",
            label_visibility="collapsed",
        )

    updated[rid] = {"name": name_val.strip(), "email": email_val.strip()}
    st.write("")

# Persist to session state on each render
st.session_state[sa_key] = updated

# ──────────────────────────────────────────────────────────────────────────
# Assignment Summary
# ──────────────────────────────────────────────────────────────────────────
any_assigned = any(v["name"] and v["email"] for v in updated.values())

if any_assigned:
    summary_cells = []
    for role in DELIVERY_ROLES:
        v = updated.get(role["id"], {})
        if v.get("name") and v.get("email"):
            summary_cells.append(
                f'<span class="sa-summary-dot" style="background:{role["dot"]};"></span>'
                f'<b style="color:{role["color_label"]};">{role["label"]}:</b> '
                f'{v["name"]}'
            )

    # 2-column grid
    mid = (len(summary_cells) + 1) // 2
    left_items  = "".join(f'<div style="margin-bottom:6px;">{c}</div>' for c in summary_cells[:mid])
    right_items = "".join(f'<div style="margin-bottom:6px;">{c}</div>' for c in summary_cells[mid:])

    st.markdown(
        f"""
        <div class="sa-summary">
          <div class="sa-summary-title">Assignment Summary</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 24px;font-size:0.84rem;color:#374151;">
            <div>{left_items}</div>
            <div>{right_items}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────
# Confirm & Proceed button
# ──────────────────────────────────────────────────────────────────────────
all_assigned = all(v["name"] and v["email"] for v in updated.values())

if not all_assigned:
    missing_roles = [
        role["label"]
        for role in DELIVERY_ROLES
        if not (updated.get(role["id"], {}).get("name") and updated.get(role["id"], {}).get("email"))
    ]
    if missing_roles:
        st.caption(
            f"⚠️ Please fill in name and email for: {', '.join(missing_roles)}"
        )

confirm_clicked = st.button(
    "Confirm Assignments & Proceed to Delivery",
    key="sa_confirm_btn",
    type="primary",
    use_container_width=True,
    disabled=(not all_assigned),
)

if confirm_clicked:
    for role_key, assignment in updated.items():
        save_assignment(selected_pid, role_key, assignment["name"], assignment["email"], user["email"])
    # Keep a session copy for convenient navigation; the database is authoritative.
    st.session_state["delivery_stakeholders"] = {
        "project_id": selected_pid,
        "project_label": project_label,
        "assignments": updated,
    }
    st.success(
        f"✅ Stakeholders assigned for **{project_label}**. Navigating to AI Product Delivery…"
    )
    st.switch_page("pages/7_PE_Assumptions.py")
