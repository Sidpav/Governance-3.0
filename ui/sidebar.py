import streamlit as st

from utils.helpers import get_api_key, resolve_model
from ui.auth import get_current_user


# Which page keys each sidebar item corresponds to, for role filtering.
# An item is shown if the signed-in role has access to ANY key in its list.
ITEM_ACCESS_KEYS = {
    "idea_submission": ["idea_submission"],
    "assessment": ["m2", "m3"],
    "expert_review": ["m6"],
    "governance_review": ["m4"],
    "governance_board": ["m5"],
    "pe_assumptions": ["pe_assumptions"],
    "pe_data": ["pe_data"],
    "pe_infrastructure": ["pe_infrastructure"],
    "pe_workflow": ["pe_workflow"],
    "pe_responsibility": ["pe_responsibility"],
    "pe_execution_approval": ["pe_execution_approval"],
}


PAGE_BADGES = {
    "landing": ("🤖", "AI Governance Platform"),
    "instructions": ("📘", "Explainer"),

    # -----------------------------
    # Problem Selection
    # -----------------------------
    "idea_submission": ("💡", "Use-case Intake"),
    "m2": ("📊", "Use-case Scoring & Prioritization"),
    "m3": ("⚖️", "Use-case Scoring & Prioritization"),
    "m4": ("🏛️", "Portfolio Gate Review"),
    "m5": ("📊", "Portfolio Dashboard"),
    "m6": ("🧑‍⚖️", "Expert Advice"),

    # -----------------------------
    # Project Execution
    # -----------------------------
    "pe_assumptions": ("🧪", "Assumption & Hypothesis Register"),
    "pe_data": ("🗄️", "Data"),
    "pe_infrastructure": ("🏗️", "Infrastructure"),
    "pe_workflow": ("🔄", "Operational Integration & Metrics"),
    "pe_responsibility": ("👤", "Governance Operating Model & Decision Rights"),
    "pe_execution_approval": ("📍", "Delivery Gate Review"),

    "tracking": ("📍", "AI Oversight, Evidence & Value Realization"),
}


# ==========================================================
# Sections
# ==========================================================

PROBLEM_SELECTION_SECTION = {
    "idea_submission",
    "m2",
    "m3",
    "m4",
    "m5",
    "m6",
}

PROJECT_EXECUTION_SECTION = {
    "pe_assumptions",
    "pe_data",
    "pe_infrastructure",
    "pe_workflow",
    "pe_responsibility",
    "pe_execution_approval",
}


# ==========================================================
# Sidebar Items
# ==========================================================

PROBLEM_SELECTION_ITEMS = [
    ("idea_submission", "💡 Use-case Intake", "pages/1_Idea_Submission.py"),
    ("assessment", "📊 Use-case Scoring & Prioritization", "pages/2_Feasibility_Assessment.py"),
    ("governance_review", "🏛️ Portfolio Gate Review", "pages/4_Governance_Review.py"),
    ("governance_board", "🗂️ Use-Case History", "pages/5_Analytics_Dashboard.py"),
]

PROJECT_EXECUTION_ITEMS = [
    ("pe_assumptions", "🧪 Assumption & Hypothesis Register", "pages/7_PE_Assumptions.py"),
    ("pe_data", "🗄️ Data", "pages/8_PE_Data.py"),
    ("pe_infrastructure", "🏗️ Infrastructure", "pages/9_PE_Infrastructure.py"),
    ("pe_workflow", "🔄 Operational Integration & Metrics", "pages/10_PE_Workflow.py"),
    ("pe_responsibility", "👤 Governance Operating Model & Decision Rights", "pages/11_PE_Responsibility.py"),
    ("pe_execution_approval", "📍 Delivery Gate Review", "pages/12_PE_Execution_Approval.py"),
]


def _init_llm_defaults():
    if "llm_provider" in st.session_state and "llm_model" in st.session_state:
        return

    api_key = get_api_key()

    if not api_key:
        return

    provider, model = resolve_model(api_key)

    st.session_state["api_key_input"] = api_key
    st.session_state["llm_provider"] = provider
    st.session_state["llm_model"] = model


def render_sidebar(active: str = "landing"):

    _init_llm_defaults()

    if active in PROJECT_EXECUTION_SECTION:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"],
            [data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.cx-top-active),
            div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active),
            div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) {
                left: 0 !important;
            }
            section.main > div.block-container {
                margin-top: 152px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        return

    with st.sidebar:

        # ------------------------------------
        # Decide which workflow to display
        # ------------------------------------

        if active in PROBLEM_SELECTION_SECTION:

            items = PROBLEM_SELECTION_ITEMS

            assessment_active = active in ("m2", "m3")
            governance_active = active in ("m4", "m5")
            review_active = active == "m4"

        elif active in PROJECT_EXECUTION_SECTION:

            items = PROJECT_EXECUTION_ITEMS

        else:

            items = []

        if items:

            st.markdown(
                '<div class="cx-workflow-label">WORKFLOW</div>',
                unsafe_allow_html=True,
            )

            user = get_current_user()

            for code, label, target in items:

                if code == "expert_review" and (not user or "m6" not in user["allowed_pages"]):
                    continue

                access_keys = ITEM_ACCESS_KEYS.get(code, [])
                if user and access_keys and not any(k in user["allowed_pages"] for k in access_keys):
                    continue

                if active in PROBLEM_SELECTION_SECTION:

                    is_active = (
                        (code == "expert_review" and active == "m6")
                        or (code == "idea_submission" and active == "idea_submission")
                        or (code == "assessment" and assessment_active)
                        or (code == "governance_review" and review_active)
                        or (code == "governance_board" and governance_active)
                    )

                else:

                    is_active = active == code

                # Streamlit marks the current page with aria-current="page".
                # Rendering only the real link avoids the extra empty markdown
                # blocks that previously stretched the sidebar vertically.
                st.page_link(target, label=label)
