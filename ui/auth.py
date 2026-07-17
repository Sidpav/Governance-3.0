# ui/auth.py
# ─────────────────────────────────────────────────────────────────────────
# Session-based demo auth + role-based page access, built on top of the
# hardcoded USERS/ROLES table in config/auth_config.py.
#
# Usage in every protected page (pages/*.py except 0_Instructions.py):
#
#   from ui.auth import require_login, require_access
#
#   require_login()                 # right after st.set_page_config(...)
#   apply_theme()
#   render_sidebar("m2")
#   render_navbar("m2")
#   require_access("m2")            # right after the navbar/sidebar render
#
# require_login() bounces anyone who isn't signed in back to the login
# screen (app.py). require_access() lets the navbar/sidebar render first
# (so a denied user still sees the header + account menu + logout), then
# swaps the rest of the page for an "Access Restricted" placeholder if
# their role doesn't include that page.
# ─────────────────────────────────────────────────────────────────────────

import streamlit as st
import hmac
import os

from config.auth_config import USERS, PUBLIC_PAGES, PAGE_TARGETS, get_role_pages, get_role_label

SESSION_KEY = "cx_auth_user"


def get_current_user():
    """Returns the signed-in user's dict, or None."""
    return st.session_state.get(SESSION_KEY)


def is_logged_in() -> bool:
    return get_current_user() is not None


def _setting(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.environ.get(name, default)


def demo_mode():
    return str(_setting("DEMO_MODE", "false")).lower() in {"1", "true", "yes"}


def login(email: str, password: str = ""):
    """Looks up `email` (case-insensitive) in the hardcoded USERS table.
    On success, stores the resolved user + role in session_state and
    returns it. Returns None if the email isn't recognized."""
    if not email:
        return None

    record = USERS.get(email.strip().lower())
    if not record:
        return None
    expected = str(_setting("APP_PASSWORD", ""))
    if not demo_mode() and (not expected or not hmac.compare_digest(password, expected)):
        return None

    user = {
        "email": email.strip().lower(),
        "name": record["name"],
        "role": record["role"],
        "role_label": get_role_label(record["role"]),
        "allowed_pages": get_role_pages(record["role"]),
    }
    st.session_state[SESSION_KEY] = user
    return user


def logout():
    """Clears the session and sends the person back to the login screen."""
    # Prevent the next person using this browser session from inheriting
    # documents, LLM output, API state, or another user's project selections.
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("app.py")


def can_access(page_key: str) -> bool:
    if page_key in PUBLIC_PAGES:
        return True
    user = get_current_user()
    if not user:
        return False
    return page_key in user["allowed_pages"]


def first_accessible_page(user=None) -> str:
    """Best default page for a role — used for nav-tab targets and the
    'Go to my workspace' button on the Access Restricted placeholder."""
    user = user or get_current_user()
    if not user:
        return "app.py"
    for page_key, target in PAGE_TARGETS.items():
        if page_key in user["allowed_pages"]:
            return target
    return "app.py"


def require_login():
    """Call at the top of every protected page. Redirects unauthenticated
    visitors to the login screen."""
    if not is_logged_in():
        st.switch_page("app.py")
        st.stop()
    return get_current_user()


def require_access(page_key: str):
    """Call after render_sidebar()/render_navbar(). Halts the page with an
    Access Restricted placeholder if the signed-in role can't open
    `page_key`."""
    user = get_current_user()

    if user is None:
        st.switch_page("app.py")
        st.stop()

    if can_access(page_key):
        return user

    target = first_accessible_page(user)

    st.write("")
    st.markdown(
        f"""
        <div class="card" style="text-align:center;padding:3rem 2rem;
                    max-width:560px;margin:4rem auto 0 auto;">
          <div style="font-size:2.4rem;">🔒</div>
          <div style="font-size:1.3rem;font-weight:800;color:#1a1a2e;margin-top:10px;">
            Access Restricted
          </div>
          <div style="font-size:0.92rem;color:#666;margin-top:10px;line-height:1.6;">
            Your signed-in role doesn't include
            access to this page.<br>Contact your platform admin if you believe
            this is a mistake.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⬅ Go to My Workspace", type="primary", width='stretch'):
            st.switch_page(target)

    st.stop()


def render_account_menu(container):
    """Renders the small person-icon account menu (name / role / logout)
    inside the given st.columns() cell — called from ui.navbar.render_navbar()."""
    user = get_current_user()
    if not user:
        return

    with container:
        st.markdown('<div class="cx-account">', unsafe_allow_html=True)
        with st.popover("👤"):
            st.markdown(f"**{user['name']}**")
            st.caption(user["role_label"])
            st.caption(user["email"])
            st.divider()
            if st.button("Log out", key="cx_logout_btn", width='stretch'):
                logout()
        st.markdown("</div>", unsafe_allow_html=True)


def render_logout_icon(container, key_suffix=""):
    """Renders a compact account icon that returns the user to login."""
    if not get_current_user():
        return

    with container:
        st.markdown('<div class="cx-account">', unsafe_allow_html=True)
        if st.button(
            "👤",
            key=f"cx_logout_icon_btn_{key_suffix}",
            help="Back to login",
        ):
            logout()
        st.markdown("</div>", unsafe_allow_html=True)
