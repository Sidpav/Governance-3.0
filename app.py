# app.py — Entry point. Run: streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────
# Signed OUT: this file renders the login screen (email lookup against the
# hardcoded demo accounts in config/auth_config.py — see ui/auth.py).
# Signed IN: it renders the same welcome / landing hub as before, with the
# CTA adapted to the signed-in role.
# ─────────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

# Streamlit Cloud can start the script with the repository root omitted from
# sys.path. Always make sibling packages (database, ui, config, llm) importable.
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import streamlit as st

from database.db import init_db
from ui.theme import apply_theme, apply_login_styles
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar
from ui.auth import get_current_user, login, first_accessible_page, demo_mode
from config.auth_config import USERS, get_role_label

st.set_page_config(
    page_title="AI Governance Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

apply_theme()

user = get_current_user()


# ─────────────────────────────────────────────────────────────────────
# SIGNED OUT — login screen
# ─────────────────────────────────────────────────────────────────────
if user is None:

    apply_login_styles()

    st.markdown(
        """
        <div class="cx-login-topbar">
          <div class="cx-login-topbar-brand">
            <span class="cx-login-icon">⚡</span> AI Maturity Governance
          </div>
          <div class="cx-login-topbar-tag"><i>Responsible AI. Governed at every stage.</i></div>
        </div>
        <div class="cx-login-spacer"></div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:

        def select_demo_account(demo_email):
            """Populate the normal login widgets; authentication still occurs via Sign In."""
            st.session_state["cx_login_email"] = demo_email
            st.session_state["cx_login_password"] = demo_email

        st.markdown(
            """
            <div class="cx-login-card-header">
              <h1>Welcome Back</h1>
              <p>Enter your registered email to access your governance workspace</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="cx-login-card-body">', unsafe_allow_html=True)

        st.markdown('<div class="cx-login-label">EMAIL ADDRESS</div>', unsafe_allow_html=True)

        email = st.text_input(
            "Email address",
            key="cx_login_email",
            placeholder="you@cortexa.ai",
            label_visibility="collapsed",
        )
        password = st.text_input(
            "Demo access password", key="cx_login_password", type="password",
            placeholder="Deployment access password", label_visibility="collapsed",
        )

        login_clicked = st.button("Sign In", type="primary", width='stretch')

        if login_clicked:
            signed_in_user = login(email, password)
            if signed_in_user:
                st.session_state.pop("cx_login_email", None)
                st.rerun()
            else:
                st.error("Sign-in failed. Check the registered email and access password.")

        if demo_mode():
            st.markdown(
                "<div class='cx-demo-notice'>Demo environment — do not enter confidential information.</div>",
                unsafe_allow_html=True,
            )
            with st.expander("Demo credentials", expanded=True):
                st.markdown(
                    "<div class='cx-demo-heading'>Choose a role to fill the email and password automatically</div>"
                    "<div class='cx-demo-password'>Demo password = selected email address</div>",
                    unsafe_allow_html=True,
                )
                st.markdown('<span class="cx-demo-account-list"></span>', unsafe_allow_html=True)
                for index, (demo_email, info) in enumerate(USERS.items()):
                    role_label = get_role_label(info["role"])
                    if st.button(
                        f"{role_label}  ·  {demo_email}",
                        key=f"cx_demo_account_{index}",
                        on_click=select_demo_account,
                        args=(demo_email,),
                        help=f"Use the {role_label} demo account",
                        width="stretch",
                    ):
                        pass

        st.markdown(
            "<div style='text-align: center; color: #94A3B8; font-size: 0.85rem; margin-top: 18px;'>Powered by Cortexa</div>",
            unsafe_allow_html=True
        )

    st.stop()


# ─────────────────────────────────────────────────────────────────────
# SIGNED IN — landing hub
# ─────────────────────────────────────────────────────────────────────
render_sidebar("landing")
render_navbar("landing")

st.write("")

st.markdown(f"""
<div class="card" style="text-align:center;padding:3.2rem 2rem;min-height:0;">
  <div style="font-size:2.1rem;font-weight:800;color:#1a1a2e;margin-top:6px;">
    AI Governance Platform
  </div>
  <div style="font-size:1.05rem;color:#666;margin-top:10px;max-width:620px;margin-left:auto;margin-right:auto;">
    End-to-End AI Governance, Assessment, and Approval Platform
  </div>
  <div style="font-size:0.9rem;color:#8a8a8a;margin-top:14px;">
    Welcome back, <b>{user['name']}</b> — signed in as <b>{user['role_label']}</b>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="card" style="min-height:160px;">
      <div style="font-size:1.6rem;">💡</div>
      <div style="font-weight:700;margin-top:6px;">Submit an Idea</div>
      <div style="font-size:0.85rem;color:#666;margin-top:4px;">
        Describe a business problem, attach supporting documents, and let AI
        help shape it into a governance-ready proposal.
      </div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card" style="min-height:160px;">
      <div style="font-size:1.6rem;">📊</div>
      <div style="font-weight:700;margin-top:6px;">Assess & Prioritize</div>
      <div style="font-size:0.85rem;color:#666;margin-top:4px;">
        Run feasibility and gain-pain analysis grounded in NIST AI RMF and
        ISO 42001 frameworks.
      </div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="card" style="min-height:160px;">
      <div style="font-size:1.6rem;">🏛️</div>
      <div style="font-weight:700;margin-top:6px;">Govern & Track</div>
      <div style="font-size:0.85rem;color:#666;margin-top:4px;">
        Route ideas through committee review, then track execution and
        lifecycle status end to end.
      </div>
    </div>""", unsafe_allow_html=True)

st.write("")
st.write("")

target = first_accessible_page(user)

col_a, col_b, col_c = st.columns([1, 1, 1])
with col_b:
    if st.button("🚀 Go to My Workspace", type="primary", width='stretch'):
        st.switch_page(target)

st.write("")
st.caption("Need help getting started? Open **Explainer** in the navigation bar on the top.")
