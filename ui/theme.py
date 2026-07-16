# ui/theme.py
import base64
import streamlit as st

LOGO_PATH = "assets/logo2.png"

def _get_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def apply_global_styles():

    # ── 1. Hide Streamlit's built-in multipage nav & header chrome ──────────
    st.markdown("""
    <style>
    /* Hide Streamlit default nav */
    [data-testid="stSidebarNav"]          { display: none !important; }
    section[data-testid="stSidebar"] nav  { display: none !important; }
                
                /* Remove Streamlit sidebar header */
[data-testid="stSidebarHeader"]{
    display:none !important;
    height:0 !important;
    min-height:0 !important;
    padding:0 !important;
    margin:0 !important;
}

    /* Kill the default top header bar (Deploy button, hamburger, etc.) */
    [data-testid="stHeader"]              { display: none !important; }
    #MainMenu                             { display: none !important; }
    footer                                { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── 2. Global layout — zero top gap, correct sidebar colour ─────────────
    st.markdown("""
    <style>
    html, body { margin: 0; padding: 0; }

    /* Remove ALL top padding Streamlit injects */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Push main content down below the brand band + navbar */
    section.main > div.block-container {
        margin-top: 116px;
    }

    section.main > div.block-container::after {
        content: "AI Maturity Governance - Powered by Cortexa.";
        display: block;
        text-align: center;
        padding: 2.2rem 0 1.2rem;
        font-size: 0.82rem;
        color: #94A3B8;
        border-top: 1px solid #E2E8F0;
        margin-top: 4.5rem;
        font-weight: 500;
        width: 100%;
    }

    .main { background-color: #f8fafc; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        top: 116px !important;          /* starts BELOW the full app header */
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] * { color: white; }

    /* No gap above sidebar content */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 3. Sticky top navbar ────────────────────────────────────────────────
    st.markdown("""
    <style>
    .cx-navbar {
        position: fixed;
        top: 60px; left: 0; right: 0;
        height: 56px;
        z-index: 999;
        background: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        padding: 0;
    }

    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) {
        position: fixed !important;
        top: 60px !important;
        left: 360px !important;
        right: 0 !important;
        height: 56px !important;
        z-index: 1001 !important;
        background: #FFFFFF !important;
        border-bottom: 1px solid #E5E7EB !important;
        align-items: center !important;
        padding: 0 24px !important;
        gap: 0 !important;
        justify-content: flex-start !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        height: 56px !important;
    }

    .cx-brand-band {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 60px;
        z-index: 1000;
        background: #1B2D57;
        border-bottom: 1px solid #1E293B;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 28px;
    }

    /* Make the Streamlit column wrapper inside the navbar flex-friendly */
    .cx-navbar [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        gap: 0 !important;
        align-items: center !important;
        height: 56px;
    }

    .cx-app-brand {
        color: #F8FAFC;
        font-size: 1.24rem;
        font-weight: 800;
        height: 60px;
        display: flex;
        align-items: center;
        white-space: nowrap;
    }

    .cx-brand-actions {
        display: flex;
        align-items: center;
        gap: 18px;
        height: 60px;
        padding-right: 48px;
    }

    .cx-user-pill {
        background: #F4E9FF;
        border: 1px solid #DFC7FF;
        border-radius: 999px;
        color: #6B21A8;
        font-size: 1rem;
        font-weight: 800;
        padding: 6px 18px 7px 10px;
        white-space: nowrap;
    }
    .cx-user-pill span {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 999px;
        background: #F8FAFC;
        color: #1B2D57;
        margin-right: 7px;
        font-weight: 900;
    }

    .cx-shell-icon {
        color: #A8B4CA;
        font-size: 1.05rem;
        line-height: 1;
    }

    /* All page_link anchors inside navbar */
    .cx-navbar [data-testid="stPageLink-NavLink"] {
        padding: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) a,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) a *,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) [data-testid="stPageLink-NavLink"],
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) [data-testid="stPageLink-NavLink"] *,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) a,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) a *,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) [data-testid="stPageLink-NavLink"],
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) [data-testid="stPageLink-NavLink"] *,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) a,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) a *,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) [data-testid="stPageLink-NavLink"],
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) [data-testid="stPageLink-NavLink"] * {
        background: transparent !important;
        background-color: transparent !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
    }
    /* The page links are rendered by Streamlit as siblings of the cx-navbar
       marker, so apply the text colour to the fixed column block as well.
       The broader anchor selectors keep this working across Streamlit releases
       that use either stPageLink or stPageLink-NavLink test ids. */
    .cx-navbar [data-testid="stPageLink-NavLink"] p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) a p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-item) a p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) [data-testid^="stPageLink"] p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-item) [data-testid^="stPageLink"] p {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin: 0 !important;
        white-space: nowrap;
    }
    .cx-navbar [data-testid="stPageLink-NavLink"]:hover p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) a:hover p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-item) a:hover p {
        color: #1E3A8A !important;
    }

    /* Active main tab */
    .cx-top-active [data-testid="stPageLink-NavLink"] {
        background: transparent !important;
        border-radius: 0 !important;
        border-bottom: 2px solid #5B8DEF !important;
        height: 56px;
    }
    .cx-top-active [data-testid="stPageLink-NavLink"] p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) .cx-top-active ~ [data-testid^="stPageLink"] p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) [data-testid="column"]:has(.cx-top-active) a p {
        color: #2563EB !important;
        font-weight: 700 !important;
    }

    /* Inactive main tab */
    .cx-top-item [data-testid="stPageLink-NavLink"] {
        background: transparent !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        height: 56px;
    }

    .cx-pe-tabs-marker + div[data-testid="stHorizontalBlock"],
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active),
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) {
        position: fixed !important;
        top: 116px !important;
        left: 0 !important;
        right: 0 !important;
        height: 56px !important;
        z-index: 1000 !important;
        background: #FFFFFF !important;
        border-bottom: 1px solid #E5E7EB !important;
        align-items: center !important;
        padding: 0 28px !important;
        gap: 0 !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) [data-testid="column"],
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        height: 56px !important;
    }
    .cx-pe-tab [data-testid="stPageLink-NavLink"],
    .cx-pe-tab-active [data-testid="stPageLink-NavLink"] {
        background: transparent !important;
        border-radius: 0 !important;
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
        box-shadow: none !important;
        height: 56px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }
    .cx-pe-tab [data-testid="stPageLink-NavLink"] p,
    .cx-pe-tab-active [data-testid="stPageLink-NavLink"] p {
        font-size: 0.96rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    .cx-pe-tab-active [data-testid="stPageLink-NavLink"] {
        border-bottom: 2px solid #5B8DEF !important;
    }
    .cx-pe-tab-active [data-testid="stPageLink-NavLink"] p {
        color: #2563EB !important;
    }

    /* Instructions link — smaller, muted, top right */
    .cx-instructions-link [data-testid="stPageLink-NavLink"] {
        background: rgba(255,255,255,0.07) !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        height: auto !important;
        margin: auto;
    }
    .cx-instructions-link [data-testid="stPageLink-NavLink"] p {
        font-size: 0.75rem !important;
        color: #64748B !important;
        font-weight: 500 !important;
    }
    .cx-instructions-link [data-testid="stPageLink-NavLink"]:hover p {
        color: #1E3A8A !important;
    }

    /* Account menu (person icon, top-right of navbar) */
    .cx-account {
        position: fixed;
        top: 15px;
        right: 22px;
        z-index: 1002;
        display: flex; align-items: center; justify-content: center;
        height: 30px;
    }
    div[data-testid="column"]:has(.cx-account) button {
        position: fixed !important;
        top: 15px !important;
        right: 22px !important;
        z-index: 1003 !important;
    }
    .cx-account [data-testid="stPopover"] {
        display: flex; align-items: center; justify-content: center;
    }
    .cx-account button {
        width: 30px !important; height: 30px !important;
        min-height: 30px !important; padding: 0 !important;
        border-radius: 50% !important;
        background: transparent !important;
        border: none !important;
        display: flex !important; align-items: center; justify-content: center;
    }
    .cx-account button p {
        margin: 0 !important; font-size: 1.05rem !important; line-height: 1 !important;
    }
    .cx-account button:hover {
        background: rgba(27,45,87,0.08) !important;
    }

    /* ── Assign Roles button (business_leader only, fixed in brand band) ── */
    /* Sits to the right of user pill, inside the dark brand-band bar       */
    .cx-assign-roles-wrap {
        position: fixed;
        top: 13px;
        right: 108px;      /* leaves room for the gear + bell icons at far right */
        z-index: 1005;
        display: flex;
        align-items: center;
    }
    div[data-testid="column"]:has(.cx-assign-roles-wrap) {
        /* keep columns clean — this wrapper escapes via position:fixed */
        overflow: visible !important;
    }
    .cx-assign-roles-wrap .stButton > button {
        background: #1B2D57 !important;
        color: #FFFFFF !important;
        border: 1.5px solid rgba(255,255,255,0.22) !important;
        border-radius: 999px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        padding: 4px 16px !important;
        height: 34px !important;
        min-height: 34px !important;
        white-space: nowrap !important;
        letter-spacing: 0.02em;
        box-shadow: 0 2px 8px rgba(27,45,87,0.22);
        transition: background 0.18s ease, box-shadow 0.18s ease;
    }
    .cx-assign-roles-wrap .stButton > button:hover {
        background: #2a4080 !important;
        box-shadow: 0 4px 14px rgba(27,45,87,0.34);
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 4. Sidebar logo + workflow list ─────────────────────────────────────
    st.markdown("""
    <style>
    .cx-workflow-label {
        color: #8EA3C8; font-size: 0.76rem; font-weight: 800;
        letter-spacing: 0.08em; margin: 18px 0 8px 14px;
    }

    .cx-nav-item {
        border-radius: 10px; overflow: hidden; margin-bottom: 2px;
    }
    .cx-nav-item [data-testid="stPageLink-NavLink"] {
        width: 100% !important;
        padding: 9px 12px !important;
        border-radius: 10px !important;
        background: transparent !important;
    }
    .cx-nav-item [data-testid="stPageLink-NavLink"] > div {
        display: flex; align-items: center; justify-content: flex-start !important; gap: 9px;
    }
    .cx-nav-item [data-testid="stPageLink-NavLink"] p {
        font-size: 1rem !important; font-weight: 650 !important;
        color: #CBD5E1 !important; margin: 0 !important;
    }
    .cx-nav-item [data-testid="stPageLink-NavLink"] span { font-size: 1rem !important; }
    .cx-nav-item:hover { background: rgba(255,255,255,0.06); }

    .cx-nav-active { background: #1F2B4D; border-left: 3px solid #5B8DEF; }
    .cx-nav-active [data-testid="stPageLink-NavLink"] p {
        color: #FFFFFF !important; font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 5. Breadcrumb + sub-tab pills ───────────────────────────────────────
    st.markdown("""
    <style>
    .cx-breadcrumb {
        font-size: 0.82rem; margin: 0.3rem 0 0.8rem 0;
    }
    .cx-breadcrumb-muted  { color: #94A3B8; }
    .cx-breadcrumb-sep    { color: #CBD5E1; margin: 0 5px; }
    .cx-breadcrumb-active { color: #0F172A; font-weight: 700; }

    .cx-subtabs [data-testid="stPageLink-NavLink"] {
        background: #F1F5F9 !important; border-radius: 10px !important;
        padding: 0.45rem 0.85rem !important; border: 1px solid #E2E8F0 !important;
    }
    .cx-subtabs [data-testid="stPageLink-NavLink"] p {
        font-size: 0.84rem !important; color: #374151 !important;
    }
    .cx-subtabs-active [data-testid="stPageLink-NavLink"] {
        background: #EEF2FF !important; border: 1px solid #6C63FF !important;
    }
    .cx-subtabs-active [data-testid="stPageLink-NavLink"] p {
        color: #6C63FF !important; font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 6. Cards, buttons, forms ─────────────────────────────────────────────
    st.markdown("""
    <style>
    .card {
        background: white; border: 1px solid #e5e7eb; border-radius: 16px;
        padding: 24px; box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }
    .stepper {
        background: white; border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 18px; margin-bottom: 20px;
    }
    .stButton > button {
        background-color: #6D5DFC; color: white; border: none;
        border-radius: 8px; font-weight: 600;
    }
    .stButton > button:hover { background-color: #5848f5; color: white; }
    .review-box {
        border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 20px; background: white;
    }
    .review-label { font-weight: 600; color: #4b5563; margin-top: 12px; }

    div[data-baseweb="select"] > div {
        background: linear-gradient(135deg, #6C63FF, #5A54E8) !important;
        color: white !important; border: none !important; border-radius: 14px !important;
    }

    [data-testid="stVerticalBlock"] > div:has(.card-title) {
        background: white; border: 1px solid #E5E7EB;
        border-radius: 16px; padding: 20px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }
    .score-number { text-align: center; font-size: 72px; font-weight: 700; }
    .score-label  { text-align: center; font-size: 24px; font-weight: 600; color: #22c55e; }
    </style>
    """, unsafe_allow_html=True)

    # ── 7. Status badges ─────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .badge { display:inline-block; padding:3px 11px; border-radius:20px; font-size:0.73rem; font-weight:700; }
    .b-submitted { background:#EDE9FF; color:#4A42CC; }
    .b-review    { background:#FFF3CD; color:#856404; }
    .b-approved  { background:#D1F5EA; color:#0f6e56; }
    .b-rejected  { background:#FDE8E8; color:#c0392b; }
    .b-deferred  { background:#F0F0F0; color:#555; }
    </style>
    """, unsafe_allow_html=True)

    # ── 8. Info tooltip + score basis (used in M3 Gain-Pain) ────────────────
    st.markdown("""
    <style>
    .info-wrap {
        display: inline-block; position: relative;
        vertical-align: middle; margin-left: 5px; cursor: pointer;
    }
    .info-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 16px; height: 16px; border-radius: 50%;
        background: #6C63FF; color: #fff;
        font-size: 0.62rem; font-weight: 800; font-style: normal;
        line-height: 1; user-select: none;
    }
    .info-wrap .info-tooltip {
        visibility: hidden; opacity: 0;
        transition: opacity 0.18s ease;
        position: absolute; bottom: 130%; left: 50%;
        transform: translateX(-50%);
        background: #1a1a2e; color: #f0f0f0;
        border-radius: 10px; padding: 0.7rem 0.9rem;
        font-size: 0.76rem; line-height: 1.6;
        width: 330px; z-index: 9999;
        box-shadow: 0 6px 20px rgba(0,0,0,0.35);
        white-space: normal; pointer-events: none;
    }
    .info-wrap .info-tooltip code {
        background: rgba(255,255,255,0.12); border-radius: 4px;
        padding: 1px 5px; font-size: 0.74rem; color: #C5C1FF;
    }
    .info-wrap .info-tooltip::after {
        content: ""; position: absolute; top: 100%; left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent; border-top-color: #1a1a2e;
    }
    .info-wrap:hover .info-tooltip { visibility: visible; opacity: 1; }

    .score-basis {
        background: #F7F7FF; border-left: 3px solid #C5C1FF;
        border-radius: 0 6px 6px 0; padding: 0.4rem 0.75rem;
        margin-top: 6px; font-size: 0.72rem; color: #555; line-height: 1.5;
    }
    .score-basis .basis-label {
        font-weight: 700; color: #6C63FF; font-size: 0.67rem;
        text-transform: uppercase; letter-spacing: 0.06em;
        display: block; margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 9. Sidebar expander styling ──────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stExpander"] details summary {
        background: #1f2b4d !important; color: white !important;
        border-radius: 10px !important; border: none !important;
    }
    [data-testid="stExpander"] details summary:hover { background: #2b3b66 !important; }
    [data-testid="stExpander"] details { background: transparent !important; border: none !important; }
    [data-testid="stExpander"] details div[role="group"] { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)


def apply_background_logo():
    try:
        logo_base64 = _get_base64(LOGO_PATH)
    except Exception:
        return
    st.markdown(f"""
    <style>
    .stApp::before {{
        content: "";
        position: fixed; top: 50%; left: 50%;
        width: 700px; height: 700px;
        transform: translate(-50%, -50%);
        background-image: url("data:image/png;base64,{logo_base64}");
        background-repeat: no-repeat; background-position: center;
        background-size: contain; opacity: 0.08;
        z-index: 1; pointer-events: none;
    }}
    </style>
    """, unsafe_allow_html=True)


def apply_login_styles():
    """CSS for the standalone login screen (app.py, signed-out state) —
    slim dark top bar + centered welcome card, no sidebar/navbar tabs."""
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    .stApp {
        background:
            radial-gradient(circle at 16% 18%, rgba(59, 130, 246, 0.38), transparent 34%),
            radial-gradient(circle at 84% 72%, rgba(96, 165, 250, 0.22), transparent 32%),
            linear-gradient(135deg, #07111F 0%, #0B2A5B 48%, #1D4ED8 100%) !important;
        min-height: 100vh;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stMain"] > div,
    [data-testid="stMain"] > div > div,
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stAppViewContainer"] > section,
    .main,
    section.main,
    section.main > div,
    section.main > div > div,
    .block-container {
        background: transparent !important;
        background-color: transparent !important;
    }
    .block-container {
        padding-top: 0 !important;
        max-width: 1400px;
    }
    section.main > div.block-container::after {
        display: none !important;
    }

    .cx-login-topbar {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background: #0B1220; border-bottom: 1px solid #1E293B;
        z-index: 1000; display: flex; align-items: center;
        justify-content: space-between; padding: 0 28px;
    }
    .cx-login-topbar-brand {
        color: #F8FAFC; font-size: 1.15rem; font-weight: 800;
        display: flex; align-items: center; gap: 10px;
    }
    .cx-login-topbar-brand .cx-login-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 9px;
        background: #3B82F6; color: white; font-size: 1.05rem;
    }
    .cx-login-topbar-tag {
        color: #93A5C4; font-style: italic; font-size: 0.92rem;
    }

    .cx-login-spacer { height: 30px; }

    div[data-testid="stVerticalBlock"]:has(.cx-login-card-header) {
        background: #FFFFFF;
        border-radius: 0;
        box-shadow: 0 18px 48px rgba(15, 23, 42, 0.26);
        overflow: hidden;
        padding: 0 2.4rem 2.4rem 2.4rem;
    }

    .cx-login-card {
        background: white; border-radius: 0; overflow: visible;
        box-shadow: none;
        max-width: none; margin: 0 -2.4rem;
    }
    .cx-login-card-header {
        background: #FFFFFF;
        text-align: center; padding: 2.6rem 2rem 2rem 2rem;
    }
    .cx-login-card-header h1 {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 2rem; font-weight: 800; color: #1a1a2e; margin: 0;
    }
    .cx-login-card-header p {
        color: #64748B; font-size: 1rem; margin: 10px 0 0 0;
    }
    .cx-login-card-body { padding: 2rem 0 0 0; }

    .cx-login-label {
        color: #7C8AA8; font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.08em; margin-bottom: 10px;
    }

    .cx-login-card-body div[data-testid="stTextInput"] input {
        border-radius: 10px !important; border: 1px solid #E2E8F0 !important;
        padding: 0.65rem 0.9rem !important;
    }
    .cx-login-card-body .stButton > button {
        width: 100%; padding: 0.65rem 0; border-radius: 10px;
        background-color: #6D5DFC; font-weight: 700; margin-top: 4px;
    }
    .cx-login-card-body .stButton > button:hover { background-color: #5848f5; }

    .cx-login-footer {
        text-align: center; color: rgba(255,255,255,0.82); font-size: 0.8rem; margin: 1.4rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_reference_ui():
    """Reference visual system supplied for the Cortexa governance demo."""
    st.markdown("""
    <style>
    :root {
        --cx-navy: #1D3263;
        --cx-navy-deep: #182C58;
        --cx-blue: #155EEF;
        --cx-blue-soft: #EAF1FF;
        --cx-canvas: #F4F7FC;
        --cx-card: #FFFFFF;
        --cx-line: #D9E2F0;
        --cx-text: #10203E;
        --cx-muted: #8EA2C3;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main, .main {
        background: var(--cx-canvas) !important;
        color: var(--cx-text) !important;
        font-family: Georgia, 'Times New Roman', serif !important;
    }
    .stApp, .stApp p, .stApp label, .stApp input, .stApp textarea,
    .stApp button, .stApp select, .stApp [data-baseweb="select"] * {
        font-family: Georgia, 'Times New Roman', serif !important;
    }
    .block-container {
        max-width: none !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        padding-bottom: 6rem !important;
    }
    section.main > div.block-container { margin-top: 152px; }
    section.main > div.block-container::after { display: none !important; }
    .stApp::after {
        content: "AI Maturity Governance — Powered By Cortexa™";
        position: fixed; left: 0; right: 0; bottom: 0; z-index: 990;
        height: 58px; display: flex; align-items: center; justify-content: center;
        background: #FFFFFF; border-top: 1px solid var(--cx-line);
        color: #8FA4C8; font: 1.05rem Georgia, 'Times New Roman', serif;
    }

    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] strong {
        color: var(--cx-text);
        font-family: Georgia, 'Times New Roman', serif !important;
    }
    h1 { font-size: 2rem !important; line-height: 1.15 !important; }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.25rem !important; }
    p, li, label { color: var(--cx-text); }
    [data-testid="stCaptionContainer"] { color: var(--cx-muted) !important; }
    hr { border-color: var(--cx-line) !important; }

    /* Top brand bar */
    .cx-brand-band {
        height: 76px !important; padding: 0 26px !important;
        background: var(--cx-navy) !important; border: 0 !important;
    }
    .cx-app-brand {
        height: 76px !important; gap: 18px; color: #FFFFFF !important;
        font-size: 1.35rem !important; font-weight: 700 !important;
    }
    .cx-brand-mark {
        width: 48px; height: 48px; display: inline-flex;
        align-items: center; justify-content: center; border-radius: 7px;
        background: #2F80ED; color: #FFFFFF; font: 2rem Georgia, serif;
    }
    .cx-brand-actions { height: 76px !important; gap: 26px !important; padding-right: 22px !important; }
    .cx-user-pill {
        background: #E7EDFF !important; border: 1px solid #CAD6F7 !important;
        color: #2024A5 !important; padding: 7px 22px 7px 12px !important;
        font-size: 1.05rem !important; font-weight: 700 !important;
    }
    .cx-user-pill span { background: #FFFFFF !important; color: #10203E !important; }
    .cx-shell-icon { color: #A8B6D0 !important; font-size: 1.35rem !important; }

    /* Primary navigation */
    .cx-navbar { top: 76px !important; height: 76px !important; background: #FFFFFF !important; }
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active),
    div[data-testid="stHorizontalBlock"]:has(.cx-top-item) {
        position: fixed !important; top: 76px !important; left: 0 !important; right: 0 !important;
        height: 76px !important; z-index: 1001 !important; padding: 0 34px !important;
        background: #FFFFFF !important; border-bottom: 1px solid var(--cx-line) !important;
        align-items: center !important; gap: 24px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) [data-testid="column"],
    div[data-testid="stHorizontalBlock"]:has(.cx-top-item) [data-testid="column"] {
        height: 76px !important; display: flex !important; align-items: center !important;
    }
    .cx-top-active [data-testid^="stPageLink"],
    .cx-top-item [data-testid^="stPageLink"] { height: 76px !important; padding: 0 10px !important; }
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) a p,
    div[data-testid="stHorizontalBlock"]:has(.cx-top-item) a p {
        color: #627695 !important; font-size: 1.02rem !important;
        font-weight: 700 !important; white-space: nowrap !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active)
    [data-testid="column"]:has(.cx-top-active) a p { color: #124FEA !important; }
    .cx-top-active [data-testid^="stPageLink"] { border-bottom: 3px solid #124FEA !important; }

    /* Product Delivery sub-navigation */
    .cx-pe-tabs-marker + div[data-testid="stHorizontalBlock"],
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active),
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) {
        position: relative !important; top: auto !important; left: auto !important;
        right: auto !important; z-index: auto !important;
        width: calc(100% + 4.4rem) !important; margin: 0 -2.2rem 0 !important;
        height: 70px !important; padding: 0 26px !important;
        background: #FFFFFF !important; border-bottom: 1px solid var(--cx-line) !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) [data-testid="column"],
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) [data-testid="column"] { height: 70px !important; }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) a p,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) a p,
    .cx-pe-tab [data-testid^="stPageLink"] p,
    .cx-pe-tab-active [data-testid^="stPageLink"] p {
        color: #526A90 !important; font-size: .9rem !important;
        font-weight: 700 !important; white-space: nowrap !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active)
    [data-testid="column"]:has(.cx-pe-tab-active) a p { color: #124FEA !important; }
    .cx-pe-tab-active [data-testid^="stPageLink"] { border-bottom: 3px solid #124FEA !important; }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) .stButton,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) .stButton {
        width: 100% !important; height: 70px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) .stButton > button,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) .stButton > button {
        width: 100% !important; height: 70px !important; min-height: 70px !important;
        padding: 0 6px !important; border: 0 !important; border-radius: 0 !important;
        background: #FFFFFF !important; color: #526A90 !important;
        box-shadow: none !important; font-size: .86rem !important;
        font-weight: 700 !important; white-space: normal !important; line-height: 1.15 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active)
    [data-testid="column"]:has(.cx-pe-tab-active) .stButton > button {
        color: #124FEA !important; border-bottom: 3px solid #124FEA !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab-active) .stButton > button:hover,
    div[data-testid="stHorizontalBlock"]:has(.cx-pe-tab) .stButton > button:hover {
        color: #124FEA !important; background: #F7F9FE !important;
    }

    /* Portfolio workflow sidebar */
    [data-testid="stSidebar"] {
        top: 152px !important; width: 350px !important; min-width: 350px !important;
        background: var(--cx-navy) !important; border-right: 0 !important;
    }
    [data-testid="stSidebar"] > div { width: 350px !important; padding: 0 !important; }
    .cx-workflow-label {
        height: 76px; display: flex; align-items: center; margin: 0 !important;
        padding: 0 22px; border-bottom: 1px solid rgba(255,255,255,.1);
        color: #8FB0EC !important; font-size: .83rem !important;
    }
    .cx-nav-item { margin: 0 !important; border-radius: 0 !important; border-left: 0 !important; }
    .cx-nav-item [data-testid^="stPageLink"] {
        min-height: 72px !important; padding: 18px 22px !important;
        border-radius: 0 !important; background: transparent !important;
    }
    .cx-nav-item [data-testid^="stPageLink"] p {
        color: #FFFFFF !important; font-size: .96rem !important; font-weight: 700 !important;
    }
    .cx-nav-active {
        background: rgba(255,255,255,.1) !important;
        border-right: 4px solid #55A4FF !important;
    }
    .cx-nav-item:hover { background: rgba(255,255,255,.07) !important; }
    [data-testid="stSidebar"] [data-testid^="stPageLink"] {
        min-height: 72px !important; padding: 18px 22px !important;
        border-radius: 0 !important; background: transparent !important;
    }
    [data-testid="stSidebar"] [data-testid^="stPageLink"] p {
        color: #FFFFFF !important; font-size: .96rem !important; font-weight: 700 !important;
    }
    [data-testid="stSidebar"] a[aria-current="page"] {
        background: rgba(255,255,255,.1) !important;
        border-right: 4px solid #55A4FF !important;
    }

    /* Breadcrumb and content */
    .cx-breadcrumb {
        margin: 0 -2.2rem 1.6rem !important; padding: 18px 2.2rem !important;
        background: #FFFFFF; border-bottom: 1px solid var(--cx-line);
        font-size: .92rem !important;
    }
    .cx-breadcrumb-muted { color: #8EA2C3 !important; }
    .cx-breadcrumb-active { color: #10203E !important; font-size: 1.03rem; }

    /* Cards and controls */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important; border: 1px solid var(--cx-line) !important;
        border-radius: 10px !important; box-shadow: none !important;
    }
    .card, .review-box, .stepper,
    [data-testid="stVerticalBlock"] > div:has(.card-title) {
        background: #FFFFFF !important; border: 1px solid var(--cx-line) !important;
        border-radius: 10px !important; box-shadow: none !important;
    }
    textarea, input, [data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        background: #F8FAFD !important; color: #10203E !important;
        border-color: var(--cx-line) !important; border-radius: 7px !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] *, textarea::placeholder, input::placeholder {
        color: #8EA2C3 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #FFFFFF !important; border: 1px dashed #C9D7EB !important;
        border-radius: 7px !important;
    }
    .stButton > button, [data-testid="stFormSubmitButton"] button {
        background: #155EEF !important; color: #FFFFFF !important;
        border: 0 !important; border-radius: 7px !important;
        font-weight: 700 !important; box-shadow: none !important;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        background: #0F4BD4 !important; color: #FFFFFF !important;
    }
    .stButton > button:disabled { background: #91B2F6 !important; opacity: 1 !important; }

    /* Assumption workflow stepper */
    .pe-step-name {
        color: #8EA2C3 !important; font-size: 1rem !important;
        font-weight: 700 !important; white-space: nowrap;
    }
    .pe-step-name b {
        display: inline-flex; width: 32px; height: 32px; align-items: center;
        justify-content: center; border: 1px solid #C7D4E9; border-radius: 50%;
        color: #8EA2C3; font-size: .9rem;
    }
    .pe-step-active, .pe-step-active b { color: #155EEF !important; }
    .pe-step-active b { color: #FFFFFF !important; background: #155EEF; border-color: #155EEF; }

    /* Keep Streamlit utility chrome out of the product shell. */
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display: none !important; }

    .cx-account, div[data-testid="column"]:has(.cx-account) button {
        top: 23px !important;
    }

    /* Premium high-contrast component system. These rules intentionally sit
       last so older page-level styles cannot create dark-on-dark controls. */
    [data-testid="stExpander"] {
        margin: 0 0 14px !important;
    }
    [data-testid="stExpander"] details {
        overflow: hidden !important;
        background: #FFFFFF !important;
        border: 1px solid var(--cx-line) !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 2px rgba(16, 32, 62, .03) !important;
    }
    [data-testid="stExpander"] details summary {
        min-height: 58px !important;
        padding: 0 18px !important;
        background: #FFFFFF !important;
        border: 0 !important;
        border-radius: 0 !important;
        color: var(--cx-text) !important;
        transition: background .16s ease, color .16s ease !important;
    }
    [data-testid="stExpander"] details summary:hover {
        background: #F4F7FD !important;
        color: #155EEF !important;
    }
    [data-testid="stExpander"] details[open] summary {
        background: #F7F9FE !important;
        border-bottom: 1px solid var(--cx-line) !important;
        color: #155EEF !important;
    }
    [data-testid="stExpander"] details summary *,
    [data-testid="stExpander"] details summary p,
    [data-testid="stExpander"] details summary span,
    [data-testid="stExpander"] details summary svg {
        color: inherit !important;
        fill: currentColor !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-testid="stExpander"] details div[role="group"] {
        background: #FFFFFF !important;
        color: var(--cx-text) !important;
        padding: 14px 18px 18px !important;
    }

    [data-testid="stAlert"] {
        border-radius: 9px !important;
        border-width: 1px !important;
        box-shadow: none !important;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: inherit !important;
        opacity: 1 !important;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--cx-line) !important;
        border-radius: 10px !important;
        padding: 16px 18px !important;
    }
    [data-testid="stMetricLabel"] p { color: #627695 !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] { color: var(--cx-text) !important; font-weight: 700 !important; }

    [data-baseweb="tab-list"] {
        gap: 10px !important;
        border-bottom: 1px solid var(--cx-line) !important;
    }
    [data-baseweb="tab"] {
        color: #627695 !important;
        background: transparent !important;
        font-weight: 700 !important;
    }
    [data-baseweb="tab"][aria-selected="true"] { color: #155EEF !important; }

    [data-testid="stDataFrame"], [data-testid="stTable"] {
        overflow: hidden !important;
        background: #FFFFFF !important;
        border: 1px solid var(--cx-line) !important;
        border-radius: 10px !important;
    }

    input:focus, textarea:focus,
    div[data-baseweb="select"] > div:focus-within,
    .stButton > button:focus-visible {
        outline: 3px solid rgba(21, 94, 239, .16) !important;
        outline-offset: 1px !important;
        border-color: #155EEF !important;
        box-shadow: none !important;
    }

    [data-baseweb="popover"], [role="listbox"], [data-baseweb="menu"] {
        background: #FFFFFF !important;
        color: var(--cx-text) !important;
        border-color: var(--cx-line) !important;
    }
    [role="option"] { color: var(--cx-text) !important; background: #FFFFFF !important; }
    [role="option"]:hover, [role="option"][aria-selected="true"] {
        color: #155EEF !important;
        background: #EAF1FF !important;
    }

    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label,
    [data-testid="stToggle"] label {
        color: var(--cx-text) !important;
        opacity: 1 !important;
    }

    /* Never allow disabled controls to become unreadable. */
    button:disabled, input:disabled, textarea:disabled,
    [aria-disabled="true"] {
        color: #6F819E !important;
        -webkit-text-fill-color: #6F819E !important;
        opacity: .78 !important;
    }

    @media (max-width: 1100px) {
        .cx-user-pill { max-width: 330px; overflow: hidden; text-overflow: ellipsis; }
        div[data-testid="stHorizontalBlock"]:has(.cx-top-active) a p,
        div[data-testid="stHorizontalBlock"]:has(.cx-top-item) a p { font-size: .85rem !important; }
        .cx-shell-icon { display: none; }
    }
    </style>
    """, unsafe_allow_html=True)


def apply_theme():
    apply_global_styles()
    apply_reference_ui()
