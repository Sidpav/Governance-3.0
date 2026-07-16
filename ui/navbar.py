import streamlit as st

from config.auth_config import PAGE_TARGETS
from ui.auth import get_current_user, render_logout_icon


SECTION_PAGE_KEYS = {
    "help": ["instructions"],
    "problem_selection": ["idea_submission", "m2", "m3", "m4", "m5", "m6"],
    "project_execution": [
        "pe_assumptions", "pe_data", "pe_infrastructure",
        "pe_workflow", "pe_responsibility", "pe_execution_approval",
    ],
    "tracking": ["tracking"],
}


def _tab_target(section_code: str, default_target: str):
    user = get_current_user()

    if section_code == "help":
        return default_target

    if not user:
        return default_target

    for page_key in SECTION_PAGE_KEYS.get(section_code, []):
        if page_key in user["allowed_pages"]:
            return PAGE_TARGETS.get(page_key, default_target)

    return None


SECTION_OF = {
    "landing": "problem_selection",
    "instructions": "help",
    "idea_submission": "problem_selection",
    "m2": "problem_selection",
    "m3": "problem_selection",
    "m4": "problem_selection",
    "m5": "problem_selection",
    "m6": "problem_selection",
    "pe_assumptions": "project_execution",
    "pe_data": "project_execution",
    "pe_infrastructure": "project_execution",
    "pe_workflow": "project_execution",
    "pe_responsibility": "project_execution",
    "pe_execution_approval": "project_execution",
    "tracking": "tracking",
}


MAIN_TABS = [
    ("help", "▣  Explainer", "pages/0_Instructions.py"),
    ("problem_selection", "♧  AI Use-Case Portfolio", "pages/1_Idea_Submission.py"),
    ("project_execution", "▷  AI Product Delivery", "pages/7_PE_Assumptions.py"),
    ("tracking", "〽  AI Oversight & Evidence", "pages/13_Tracking.py"),
]


PROJECT_EXECUTION_TABS = [
    ("pe_assumptions", "Assumption & Hypothesis Register", "pages/7_PE_Assumptions.py"),
    ("pe_data", "Data", "pages/8_PE_Data.py"),
    ("pe_infrastructure", "Infrastructure", "pages/9_PE_Infrastructure.py"),
    ("pe_workflow", "Operational Integration & Metrics", "pages/10_PE_Workflow.py"),
    ("pe_responsibility", "Governance Operating Model & Decision Rights", "pages/11_PE_Responsibility.py"),
    ("pe_execution_approval", "Delivery Gate Review", "pages/12_PE_Execution_Approval.py"),
]


def _user_badge(user=None) -> str:
    if user is None:
        user = get_current_user()
    if not user:
        return ""

    initials = "".join(part[0] for part in user["name"].split()[:2]).upper()
    return (
        f'<div class="cx-user-pill"><span>{initials}</span> '
        f'{user["name"]} <b>·</b> {user["role_label"]}</div>'
    )


def render_assign_roles_btn(key_suffix=""):
    """Renders the 'Assign Roles' button — fixed position in top brand band,
    only visible to business_leader. Uses its own fixed CSS wrapper so it
    never disrupts the navbar column layout."""
    user = get_current_user()
    if not user or user.get("role") != "business_leader":
        return

    st.markdown('<div class="cx-assign-roles-wrap">', unsafe_allow_html=True)
    if st.button(
        "👤 Assign Roles",
        key=f"cx_assign_roles_btn_{key_suffix}",
        help="Assign delivery stakeholders for a selected AI project",
    ):
        st.switch_page("pages/14_Assign_Stakeholders.py")
    st.markdown('</div>', unsafe_allow_html=True)


def render_navbar(active: str = "landing"):
    active_section = SECTION_OF.get(active, "problem_selection")
    user = get_current_user()
    is_bl = user and user.get("role") == "business_leader"

    st.markdown(
        f"""
        <div class="cx-brand-band">
          <div class="cx-app-brand"><span class="cx-brand-mark">ϟ</span>AI Maturity Governance</div>
          <div class="cx-brand-actions">
            {_user_badge(user)}
            <span class="cx-shell-icon">♧</span>
            <span class="cx-shell-icon">⚙</span>
            <span class="cx-shell-icon">♙</span>
          </div>
        </div>
        <div class="cx-navbar" id="cx-navbar">
        """,
        unsafe_allow_html=True,
    )

    # Original 5-column layout — unchanged for all roles
    cols = st.columns([1.0, 2.35, 1.9, 2.25, 5.5])

    for i, (code, label, default_target) in enumerate(MAIN_TABS):
        with cols[i]:
            target = _tab_target(code, default_target)
            if target is None:
                continue

            css = "cx-top-active" if code == active_section else "cx-top-item"
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            st.page_link(target, label=label)
            st.markdown("</div>", unsafe_allow_html=True)

    # Assign Roles — rendered OUTSIDE the columns so fixed CSS positions it correctly
    if is_bl:
        render_assign_roles_btn(key_suffix=active)

    # Logout icon — exactly as before
    render_logout_icon(cols[4])

    st.markdown("</div>", unsafe_allow_html=True)

    if active_section == "project_execution":
        st.markdown('<div class="cx-pe-tabs-marker"></div>', unsafe_allow_html=True)
        user = get_current_user()
        visible_tabs = [
            item for item in PROJECT_EXECUTION_TABS
            if not user or item[0] in user["allowed_pages"]
        ]
        if visible_tabs:
            widths = []
            for page_key, _label, _target in visible_tabs:
                widths.append({
                    "pe_assumptions": 4.2,
                    "pe_data": 0.9,
                    "pe_infrastructure": 1.7,
                    "pe_workflow": 4.3,
                    "pe_responsibility": 5.6,
                    "pe_execution_approval": 2.4,
                }.get(page_key, 1.5))
            # Use explicit switch-page buttons here. Streamlit page_link anchors
            # can lose their click target when their row is fixed with CSS.
            pe_cols = st.columns(widths)
            for i, (page_key, label, target) in enumerate(visible_tabs):
                with pe_cols[i]:
                    css = "cx-pe-tab-active" if active == page_key else "cx-pe-tab"
                    st.markdown(f'<span class="{css}"></span>', unsafe_allow_html=True)
                    if st.button(
                        label,
                        key=f"cx_pe_nav_{page_key}_{active}",
                        width="stretch",
                    ):
                        st.switch_page(target)


def render_subtabs(items, active_target):
    cols = st.columns(len(items) + 4)

    for i, (label, target) in enumerate(items):
        with cols[i]:
            css = "cx-subtabs cx-subtabs-active" if target == active_target else "cx-subtabs"
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            st.page_link(target, label=label)
            st.markdown("</div>", unsafe_allow_html=True)


def render_breadcrumb(section_label: str, page_label: str):
    st.markdown(
        f"""
        <div class="cx-breadcrumb">
            <span class="cx-breadcrumb-muted">{section_label}</span>
            <span class="cx-breadcrumb-sep">/</span>
            <span class="cx-breadcrumb-active">{page_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
