# config/auth_config.py
# ─────────────────────────────────────────────────────────────────────────
# Hardcoded DEMO identity + role-based access control for the Cortexa AI
# Governance Platform. There is no password: signing in is a lookup of the
# entered email against USERS below. Each user has exactly one role, and
# each role maps to a set of "page keys" — the same `active` strings the
# app already uses in ui.sidebar.render_sidebar()/ui.navbar.render_navbar()
# — describing exactly which pages that role may open.
#
# This is the single source of truth for auth: ui/auth.py reads USERS and
# ROLES from here, and both ui/navbar.py and ui/sidebar.py read PAGE_TARGETS
# from here to filter/redirect navigation by role.
# ─────────────────────────────────────────────────────────────────────────

# ── Page keys (must match the `active` values used across pages/*.py) ──────
PAGE_IDEA_SUBMISSION        = "idea_submission"
PAGE_ASSESSMENT_FEASIBILITY = "m2"
PAGE_ASSESSMENT_GAINPAIN    = "m3"
PAGE_GOVERNANCE_REVIEW      = "m4"
PAGE_GOVERNANCE_BOARD       = "m5"
PAGE_EXPERT_ADVICE          = "m6"
PAGE_PE_ASSUMPTIONS         = "pe_assumptions"
PAGE_PE_DATA                = "pe_data"
PAGE_PE_INFRASTRUCTURE      = "pe_infrastructure"
PAGE_PE_WORKFLOW            = "pe_workflow"
PAGE_PE_RESPONSIBILITY      = "pe_responsibility"
PAGE_PE_EXECUTION_APPROVAL  = "pe_execution_approval"
PAGE_TRACKING               = "tracking"

# Order here also defines the priority used to pick a role's default landing
# page (first entry the role can access "wins").
PAGE_TARGETS = {
    PAGE_IDEA_SUBMISSION:        "pages/1_Idea_Submission.py",
    PAGE_ASSESSMENT_FEASIBILITY: "pages/2_Feasibility_Assessment.py",
    PAGE_ASSESSMENT_GAINPAIN:    "pages/3_Gain_Pain_Analysis.py",
    PAGE_EXPERT_ADVICE:          "pages/6_Expert_Advice.py",
    PAGE_GOVERNANCE_REVIEW:      "pages/4_Governance_Review.py",
    PAGE_GOVERNANCE_BOARD:       "pages/5_Analytics_Dashboard.py",
    PAGE_PE_ASSUMPTIONS:         "pages/7_PE_Assumptions.py",
    PAGE_PE_DATA:                "pages/8_PE_Data.py",
    PAGE_PE_INFRASTRUCTURE:      "pages/9_PE_Infrastructure.py",
    PAGE_PE_WORKFLOW:            "pages/10_PE_Workflow.py",
    PAGE_PE_RESPONSIBILITY:      "pages/11_PE_Responsibility.py",
    PAGE_PE_EXECUTION_APPROVAL:  "pages/12_PE_Execution_Approval.py",
    PAGE_TRACKING:               "pages/13_Tracking.py",
}

ALL_PROTECTED_PAGES = list(PAGE_TARGETS.keys())

# Pages any signed-in user may open, regardless of role.
PUBLIC_PAGES = {"landing", "instructions"}

# ── Roles -> allowed page keys ──────────────────────────────────────────────
ROLES = {
    "business_sponsor": {
        "label": "Business Sponsor",
        "pages": set(ALL_PROTECTED_PAGES),
    },
    "business_leader": {
        "label": "Business Leader",
        # May inspect Portfolio Gate Review, but the page enforces read-only
        # access so a sponsor cannot approve or override their own submission.
        "pages": set(ALL_PROTECTED_PAGES),
    },
    "program_leader": {
        "label": "Program Leader",
        "pages": set(ALL_PROTECTED_PAGES),
    },
    "data_lead": {
        "label": "Data Lead",
        "pages": {PAGE_PE_DATA},
    },
    "infrastructure_lead": {
        "label": "Infrastructure Lead",
        "pages": {PAGE_PE_INFRASTRUCTURE},
    },
    "process_owner": {
        "label": "Process Owner",
        "pages": {PAGE_PE_ASSUMPTIONS},
    },
    "operations_manager": {
        "label": "Operations Manager",
        "pages": {PAGE_PE_WORKFLOW},
    },
    "change_management_lead": {
        "label": "Change Management Lead",
        "pages": {PAGE_TRACKING},
    },
}

# ── Hardcoded demo users (email -> name + role) ─────────────────────────────
# Sign-in is by email only (no password) — this is a demo environment.
USERS = {
    "cdo@cortexa.com":                {"name": "Sarah Mitchell", "role": "business_sponsor"},
    "businessleader@cortexa.com":     {"name": "Business Leader", "role": "business_leader"},
    "programleader@cortexa.com":      {"name": "Priya Sharma", "role": "program_leader"},
    "datalead@cortexa.com":           {"name": "Data Lead", "role": "data_lead"},
    "infrastructurelead@cortexa.com": {"name": "Infrastructure Lead", "role": "infrastructure_lead"},
    "processowner@cortexa.com":       {"name": "Process Owner", "role": "process_owner"},
    "opsmanager@cortexa.com":         {"name": "Operations Manager", "role": "operations_manager"},
    "changelead@cortexa.com":         {"name": "Change Management Lead", "role": "change_management_lead"},
}


def get_role_pages(role_key: str) -> set:
    return set(ROLES.get(role_key, {}).get("pages", set()))


def get_role_label(role_key: str) -> str:
    return ROLES.get(role_key, {}).get("label", role_key)
