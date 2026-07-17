# pages/5_Analytics_Dashboard.py
#
# MODULE 5 — Governance Dashboard. Taken ENTIRELY from My Project per the
# merge spec: same Overview / ISO 42001 Org Governance / NIST Technical
# Monitoring / Graphs tabs, same KPI header, same ISO clause + NIST signal
# logic, same data and scoring. Only Friend's visual theme/sidebar wrap it,
# and the two requested graphs (Priority distribution, Committee Decision
# Summary) are now horizontal bar charts per the merge spec's "GRAPH
# CHANGES" section. Nothing else in this file's logic was altered.

import streamlit as st
import json
import pandas as pd

from config.constants import STATUS_BADGE, GAIN_DIMENSIONS, PAIN_DIMENSIONS, PRIORITY_BANDS
from database.db import (
    db_load_all, db_load_assessments, db_load_gainpain,
    db_update_status, db_save_committee_note, db_save_team_responses,
)

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access

st.set_page_config(page_title="AI Governance Platform", page_icon="🤖",
                    layout="wide", initial_sidebar_state="expanded")

require_login()

apply_theme()
render_sidebar("m5")
render_navbar("m5")
require_access("m5")
render_breadcrumb("AI Strategy & Use-Case Portfolio", "Portfolio Dashboard")

# ── ISO 42001 Organisational Governance Clauses shown in dashboard ─────────
ISO_CLAUSES = [
    {"id": "6.1", "label": "Risk Identification",      "icon": "🔍", "desc": "Clause 6.1 — AI-related opportunities and risks identified"},
    {"id": "6.2", "label": "AI Objectives & KPIs",      "icon": "🎯", "desc": "Clause 6.2 — Measurable AI objectives set for each use case"},
    {"id": "8.4", "label": "Human Oversight Defined",   "icon": "👤", "desc": "Clause 8.4 — Human override/review mechanism documented"},
    {"id": "A.8", "label": "Data Governance Confirmed", "icon": "🗄️", "desc": "Annex A.8 — Data sources, PII handling, and ownership declared"},
    {"id": "9.1", "label": "Performance Monitoring",    "icon": "📊", "desc": "Clause 9.1 — Post-deployment KPI monitoring plan in place"},
    {"id": "10.1", "label": "Continual Improvement",    "icon": "🔄", "desc": "Clause 10.1 — Corrective actions for nonconformities identified"},
]

# ── NIST AI RMF Technical Monitoring signals ────────────────────────────────
NIST_SIGNALS = [
    {"id": "govern_1_1", "fn": "MAP",     "label": "AI Context Mapped",       "icon": "🗺️",  "desc": "NIST MAP 1.1 — Problem context, affected people, and deployment environment documented"},
    {"id": "govern_1_2", "fn": "GOVERN",  "label": "Human-in-Loop Verified",  "icon": "🔁",  "desc": "NIST GOVERN 1.2 — Human review step before consequential AI action"},
    {"id": "map_2_2",    "fn": "MAP",     "label": "Bias Audit Status",       "icon": "⚖️",  "desc": "NIST MAP 2.2 — Training data bias evaluation completed"},
    {"id": "map_2_3",    "fn": "MAP",     "label": "Failure Impact Assessed", "icon": "💥",  "desc": "NIST MAP 2.3 — Severity of wrong AI output assessed and mitigated"},
    {"id": "measure_2_5","fn": "MEASURE", "label": "Explainability Confirmed","icon": "💬",  "desc": "NIST MEASURE 2.5 — AI decisions explainable in plain language"},
    {"id": "measure_2_7","fn": "MEASURE", "label": "Drift Monitoring Active", "icon": "📡",  "desc": "NIST MEASURE 2.7 — Post-deployment monitoring with drift detection active"},
    {"id": "manage_2_4", "fn": "MANAGE",  "label": "Incident Response Ready","icon": "🚨",  "desc": "NIST MANAGE 2.4 — Incident response plan defined for AI failures"},
    {"id": "govern_6_1", "fn": "GOVERN",  "label": "Ethical Risk Cleared",    "icon": "🧭",  "desc": "NIST GOVERN 6.1 — Ethical risks (discrimination, manipulation) assessed and acceptable"},
]

TEAM_COLORS = {
    "Technical Team":     "#6C63FF",
    "Marketing Team":     "#C07A10",
    "Finance Team":       "#0F6E56",
    "Legal / Compliance": "#1A5276",
    "HR / Change Mgmt":   "#C0392B",
}


def _extract_responses(asmt: dict) -> dict:
    """
    Parse the M2 'responses' JSON stored in the feasibility_assessments table.
    Returns the full AI result dict (governance_flags, confidence, etc.) or {}.
    """
    try:
        raw = asmt.get("responses", "{}") or "{}"
        if isinstance(raw, dict):
            return raw
        return json.loads(raw)
    except Exception:
        return {}


def _kpi(col, label, value, color, tip):
    with col:
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #EAEBF5;border-radius:12px;
                    padding:0.9rem 1rem;text-align:center;" title="{tip}">
          <div style="font-size:1.6rem;font-weight:800;color:{color};">{value}</div>
          <div style="font-size:0.72rem;color:#888;margin-top:2px;">{label}</div>
        </div>""", unsafe_allow_html=True)


def _render_header():
    records = db_load_all()
    all_gp = db_load_gainpain()

    total = len(records)
    approved = sum(1 for r in records if r.get("status") == "Approved")
    review = sum(1 for r in records if r.get("status") == "Under Review")
    high_pri = sum(1 for g in all_gp if g.get("priority_band") == "High Priority")
    avg_score = (sum(g.get("priority_score_scaled", 0) for g in all_gp) / len(all_gp)) if all_gp else 0

    st.title("📊 Portfolio Dashboard")
    st.caption("Central committee view · ISO 42001 Organisational Governance · NIST AI RMF Technical Monitoring")
    st.page_link("pages/4_Governance_Review.py", label="🏛️ Record a formal committee decision →")

    c1, c2, c3, c4, c5 = st.columns(5)
    _kpi(c1, "Total Use Cases", str(total), "#6C63FF", "All submitted AI problems")
    _kpi(c2, "Approved", str(approved), "#1D9E75", "Ready for deployment")
    _kpi(c3, "Under Review", str(review), "#C07A10", "Awaiting committee decision")
    _kpi(c4, "High Priority", str(high_pri), "#C0392B", "Gain–Pain score ≥ 7.0")
    _kpi(c5, "Avg Priority Score", f"{avg_score:.1f}/10", "#1A5276", "Across all analysed use cases")


# ── Tab 1: Overview — all problems with drilldown ──────────────────────────
def _tab_overview():
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    records = db_load_all()
    all_gp = {g["problem_id"]: g for g in db_load_gainpain()}
    all_asmt = {a["problem_id"]: a for a in db_load_assessments()}

    if not records:
        st.info("No use cases submitted yet. Complete Modules 1–3 to populate the dashboard.")
        return

    col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
    with col_f1:
        search = st.text_input("🔍 Search", placeholder="ID, keyword, owner…", label_visibility="collapsed")
    with col_f2:
        status_filter = st.selectbox("Status", ["All", "Approved", "Under Review", "Submitted", "Deferred", "Rejected"],
                                      label_visibility="collapsed")
    with col_f3:
        band_filter = st.selectbox("Priority", ["All", "High Priority", "Medium Priority", "Low Priority"],
                                    label_visibility="collapsed")

    filtered = records
    if search:
        q = search.lower()
        filtered = [r for r in filtered if
                    q in r.get("id", "").lower() or
                    q in r.get("problem_statement", "").lower() or
                    q in r.get("action_owner", "").lower()]
    if status_filter != "All":
        filtered = [r for r in filtered if r.get("status") == status_filter]
    if band_filter != "All":
        filtered = [r for r in filtered
                    if all_gp.get(r["id"], {}).get("priority_band") == band_filter]

    st.markdown(f"<div style='font-size:0.75rem;color:#aaa;margin-bottom:0.6rem;'>"
                f"Showing {len(filtered)} of {len(records)} use cases</div>", unsafe_allow_html=True)

    for r in filtered:
        _problem_card(r, all_gp, all_asmt)


def _problem_card(r, all_gp, all_asmt):
    gp = all_gp.get(r["id"], {})
    asmt = all_asmt.get(r["id"], {})
    sc = STATUS_BADGE.get(r.get("status", ""), "b-submitted")
    band = gp.get("priority_band", "—")
    pb = PRIORITY_BANDS.get(band, {"color": "#aaa", "bg": "#f5f5f5", "icon": "—"})
    scaled = gp.get("priority_score_scaled", 0)

    verdict = asmt.get("verdict", "—")
    vc_col = {"Feasible": "#1D9E75", "Conditional": "#C07A10", "Not Feasible": "#C0392B"}.get(verdict, "#888")

    with st.expander(f"**{r['id']}** — {r.get('problem_statement','')[:80]}…", expanded=False):
        col_l, col_r = st.columns([2, 1])

        with col_l:
            st.markdown(f"""
            <div style="font-size:0.85rem;color:#444;line-height:1.7;">
              <b>Problem:</b> {r.get('problem_statement','—')}<br>
              <b>Objective:</b> {r.get('business_objective','—')}<br>
              <b>Solution:</b> {r.get('solution_approach','—')}<br>
              <b>Owner:</b> {r.get('action_owner','—')} &nbsp;|&nbsp;
              <b>Timeline:</b> {r.get('timeline','—')} &nbsp;|&nbsp;
              <b>ISO Risk:</b> {r.get('iso_risk_category','—')}<br>
              <b>Business Value:</b> {r.get('business_value','—')}<br>
              <b>Success Criteria:</b> {r.get('success_criteria','—')}
            </div>""", unsafe_allow_html=True)

        with col_r:
            st.markdown(f"""
            <div style="background:#FAFAFE;border:1px solid #EAEBF5;border-radius:10px;
                        padding:0.8rem;font-size:0.82rem;">
              <div style="margin-bottom:6px;">
                <span class="badge {sc}">{r.get('status','—')}</span>
              </div>
              <div style="color:{vc_col};font-weight:700;margin-bottom:4px;">M2: {verdict}
                {f"· {float(asmt.get('overall_score',0)):.2f}/5" if asmt else ""}
              </div>
              {"" if not gp else f'''
              <div style="margin-top:6px;background:{pb["bg"]};border:1px solid {pb["color"]};
                          border-radius:8px;padding:6px 10px;">
                <div style="font-size:0.68rem;color:{pb["color"]};font-weight:700;">PRIORITY SCORE</div>
                <div style="font-size:1.2rem;font-weight:800;color:{pb["color"]};">{scaled:.1f}<span style="font-size:0.75rem;"> /10</span></div>
                <div style="font-size:0.72rem;color:{pb["color"]};">{pb["icon"]} {band}</div>
              </div>'''}
            </div>""", unsafe_allow_html=True)

            new_status = st.selectbox(
                "Update Status",
                ["Submitted", "Under Review", "Approved", "Rejected", "Deferred"],
                index=["Submitted", "Under Review", "Approved", "Rejected", "Deferred"].index(r.get("status", "Submitted"))
                      if r.get("status") in ["Submitted", "Under Review", "Approved", "Rejected", "Deferred"] else 0,
                key=f"m4_status_{r['id']}",
                label_visibility="visible"
            )
            if new_status != r.get("status"):
                if st.button("💾 Save", key=f"m4_save_{r['id']}", width='stretch'):
                    db_update_status(r["id"], new_status)
                    st.success(f"Status updated to **{new_status}**")
                    st.rerun()

        if gp:
            st.markdown("---")
            _gainpain_detail(gp, r)


def _gainpain_detail(gp, r):
    ai_data = {}
    try:
        ai_data = json.loads(gp.get("ai_analysis", "{}"))
    except Exception:
        pass

    gains_data = ai_data.get("gains", {})
    pains_data = ai_data.get("pains", {})

    col_g, col_p = st.columns(2)
    with col_g:
        st.markdown("<div style='font-weight:700;font-size:0.82rem;color:#1D9E75;margin-bottom:4px;'>📈 Gains</div>",
                     unsafe_allow_html=True)
        for d in GAIN_DIMENSIONS:
            s = gains_data.get(d["id"], 0)
            pct = int(s / 5 * 100)
            st.markdown(f"""
            <div style="margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;font-size:0.78rem;">
                <span>{d['icon']} {d['label']}</span>
                <span style="font-weight:700;color:#1D9E75;">{s:.1f}</span>
              </div>
              <div style="background:#F0F0F8;border-radius:4px;height:5px;">
                <div style="background:#1D9E75;width:{pct}%;height:5px;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_p:
        st.markdown("<div style='font-weight:700;font-size:0.82rem;color:#C0392B;margin-bottom:4px;'>📉 Pains</div>",
                     unsafe_allow_html=True)
        for d in PAIN_DIMENSIONS:
            s = pains_data.get(d["id"], 0)
            pct = int(s / 5 * 100)
            col = "#C0392B" if s >= 3.5 else "#C07A10" if s >= 2.5 else "#1D9E75"
            st.markdown(f"""
            <div style="margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;font-size:0.78rem;">
                <span>{d['icon']} {d['label']}</span>
                <span style="font-weight:700;color:{col};">{s:.1f}</span>
              </div>
              <div style="background:#F0F0F8;border-radius:4px;height:5px;">
                <div style="background:{col};width:{pct}%;height:5px;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    summary = ai_data.get("net_benefit_summary", "")
    if summary:
        st.markdown(f"""
        <div style="background:#FAFAFE;border-left:3px solid #6C63FF;
                    border-radius:0 8px 8px 0;padding:0.6rem 0.9rem;
                    font-size:0.82rem;color:#444;margin-top:8px;">
          {summary}
        </div>""", unsafe_allow_html=True)


# ── Tab 2: ISO 42001 Organisational Governance ──────────────────────────────
def _render_iso_deepdive(r: dict, asmt: dict, all_gp: dict):
    """Per-project ISO 42001 + NIST compatibility deep-dive with radar chart."""
    import plotly.graph_objects as go

    gp = all_gp.get(r["id"], {})
    checks = _iso_compliance_checks(r, asmt)
    signals = _nist_signals(r, asmt, gp)

    weights = {"ok": 1.0, "partial": 0.5, "fail": 0.0}
    iso_pct = int(sum(weights.get(c["status"], 0) for c in checks.values()) / len(checks) * 100)

    nist_ok   = sum(1 for s in signals.values() if s["status"] == "ok")
    nist_warn = sum(1 for s in signals.values() if s["status"] == "warn")
    nist_fail = sum(1 for s in signals.values() if s["status"] == "fail")
    nist_pct  = int((nist_ok + nist_warn * 0.5) / len(signals) * 100)

    iso_col  = "#1D9E75" if iso_pct  >= 80 else "#C07A10" if iso_pct  >= 50 else "#C0392B"
    nist_col = "#1D9E75" if nist_pct >= 80 else "#C07A10" if nist_pct >= 50 else "#C0392B"

    # ── Compatibility Score Cards ─────────────────────────────────────────
    st.markdown("##### 🏆 Framework Compatibility Score")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="background:#fff;border:2px solid {iso_col};border-radius:14px;
                    padding:1.1rem;text-align:center;">
          <div style="font-size:0.68rem;font-weight:700;color:{iso_col};letter-spacing:0.07em;">ISO 42001 COMPLIANCE</div>
          <div style="font-size:2.2rem;font-weight:900;color:{iso_col};margin:4px 0;">{iso_pct}%</div>
          <div style="font-size:0.72rem;color:#888;">{'✅ Compliant' if iso_pct>=80 else '⚠️ Partial' if iso_pct>=50 else '❌ Non-compliant'}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background:#fff;border:2px solid {nist_col};border-radius:14px;
                    padding:1.1rem;text-align:center;">
          <div style="font-size:0.68rem;font-weight:700;color:{nist_col};letter-spacing:0.07em;">NIST AI RMF HEALTH</div>
          <div style="font-size:2.2rem;font-weight:900;color:{nist_col};margin:4px 0;">{nist_pct}%</div>
          <div style="font-size:0.72rem;color:#888;">✅{nist_ok} ⚠️{nist_warn} 🔴{nist_fail} signals</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        overall_pct = int((iso_pct + nist_pct) / 2)
        ov_col = "#1D9E75" if overall_pct >= 80 else "#C07A10" if overall_pct >= 50 else "#C0392B"
        st.markdown(f"""
        <div style="background:#fff;border:2px solid {ov_col};border-radius:14px;
                    padding:1.1rem;text-align:center;">
          <div style="font-size:0.68rem;font-weight:700;color:{ov_col};letter-spacing:0.07em;">OVERALL GOVERNANCE</div>
          <div style="font-size:2.2rem;font-weight:900;color:{ov_col};margin:4px 0;">{overall_pct}%</div>
          <div style="font-size:0.72rem;color:#888;">Combined ISO + NIST</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── ISO 42001 Radar Chart ────────────────────────────────────────────
    col_radar, col_evidence = st.columns([1, 1])
    with col_radar:
        st.markdown("**📡 ISO 42001 Clause Radar**")
        clause_labels = [f"Cl. {c['id']}\n{c['label']}" for c in ISO_CLAUSES]
        clause_scores = []
        for c in ISO_CLAUSES:
            chk = checks.get(c["id"], {"status": "fail"})
            clause_scores.append({"ok": 100, "partial": 50, "fail": 0}.get(chk["status"], 0))
        closed_labels  = clause_labels  + [clause_labels[0]]
        closed_scores  = clause_scores  + [clause_scores[0]]
        fig = go.Figure(go.Scatterpolar(
            r=closed_scores, theta=closed_labels,
            fill="toself", fillcolor="rgba(108,99,255,0.18)",
            line=dict(color="#6C63FF", width=2),
            name="ISO 42001",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                       tickvals=[0,50,100], ticktext=["❌","⚠️","✅"],
                       tickfont=dict(size=9))),
            showlegend=False, paper_bgcolor="white",
            margin=dict(l=40, r=40, t=20, b=20), height=280,
        )
        st.plotly_chart(fig, width="stretch")

    with col_evidence:
        st.markdown("**🔍 Evidence Source per Clause**")
        for c in ISO_CLAUSES:
            chk  = checks.get(c["id"], {"status": "fail", "note": "—"})
            stat = chk["status"]
            icon = {"ok": "✅", "partial": "⚠️", "fail": "❌"}.get(stat, "❌")
            tcol = {"ok": "#1D9E75", "partial": "#C07A10", "fail": "#C0392B"}.get(stat, "#C0392B")
            note = chk["note"]
            # Determine confidence level from note tag
            if "[Direct evidence]" in note or "[M1 direct" in note:
                conf_badge = "<span style='background:#D1F5EA;color:#1D9E75;font-size:0.6rem;padding:1px 5px;border-radius:3px;margin-left:4px;font-weight:700;'>DIRECT</span>"
            elif "[M1" in note:
                conf_badge = "<span style='background:#EEF2FF;color:#6C63FF;font-size:0.6rem;padding:1px 5px;border-radius:3px;margin-left:4px;font-weight:700;'>M1+M2</span>"
            else:
                conf_badge = "<span style='background:#FFF3CD;color:#C07A10;font-size:0.6rem;padding:1px 5px;border-radius:3px;margin-left:4px;font-weight:700;'>M2 ONLY</span>"
            note_clean = note.replace("[Direct evidence]","").replace("[M1 direct + M2]","").replace("[M1 + M2]","").replace("[M1 + M2 flag]","").replace("[M2 direct]","").replace("[M2 evidence]","").replace("[M2 dimension only]","").replace("[M2 flag]","").replace("[M2 + flag]","").replace("[M2 + M1]","")
            st.markdown(f"""
            <div style="padding:0.35rem 0.6rem;border-left:3px solid {tcol};
                        margin-bottom:0.35rem;background:#FAFAFE;border-radius:0 6px 6px 0;">
              <div style="font-size:0.77rem;font-weight:700;color:{tcol};">
                {icon} Clause {c['id']} — {c['label']} {conf_badge}
              </div>
              <div style="font-size:0.68rem;color:#666;margin-top:2px;">{note_clean.strip()}</div>
            </div>""", unsafe_allow_html=True)


def _tab_iso_governance():
    st.markdown("""
    <div style="background:#EEF2FF;border:1px solid #6C63FF;border-radius:12px;
                padding:0.8rem 1.2rem;margin:0.5rem 0 1rem;">
      <div style="font-size:0.78rem;font-weight:700;color:#6C63FF;letter-spacing:0.06em;">ISO 42001 — ORGANISATIONAL GOVERNANCE</div>
      <div style="font-size:0.82rem;color:#444;margin-top:3px;">
        Committee-level controls, approval workflows, policy compliance, and role accountability
        aligned to ISO 42001 AI Management System Standard.
      </div>
    </div>""", unsafe_allow_html=True)

    records = db_load_all()
    all_asmt = {a["problem_id"]: a for a in db_load_assessments()}
    all_gp   = {g["problem_id"]: g for g in db_load_gainpain()}

    if not records:
        st.info("No use cases available. Complete Module 1 first.")
        return

    # ── Per-Project Deep-Dive ─────────────────────────────────────────────
    st.markdown("#### 🔍 Project-Specific Framework Compatibility")
    project_options = ["— Select a project —"] + [r["id"] for r in records]
    chosen_id = st.selectbox(
        "Select a use case to see detailed ISO 42001 + NIST compatibility scoring",
        project_options, key="iso_deepdive_project", label_visibility="collapsed"
    )
    if chosen_id != "— Select a project —":
        chosen_r    = next((r for r in records if r["id"] == chosen_id), None)
        chosen_asmt = all_asmt.get(chosen_id, {})
        if chosen_r:
            with st.container(border=True):
                st.markdown(f"##### 📁 {chosen_id} — {chosen_r.get('problem_statement','')[:70]}…")
                if not chosen_asmt:
                    st.info("⚠️ No M2 assessment saved yet. Run Module 2 and save the assessment to unlock detailed scoring.")
                else:
                    _render_iso_deepdive(chosen_r, chosen_asmt, all_gp)

    st.markdown("---")
    st.markdown("#### 📋 ISO 42001 Clause Compliance Matrix")
    st.markdown("<div style='font-size:0.8rem;color:#888;margin-bottom:0.8rem;'>"
                "Evidence-based compliance check using M1 fields (primary) + M2 AI flags + M2 dimension scores."
                "</div>",
                unsafe_allow_html=True)

    st.markdown("#### 🔍 Filter Use Cases")
    
    col1, col2 = st.columns([3, 2])

    with col1:
        search = st.text_input(
            "Search Use Cases",
            placeholder="Problem ID, owner, keyword...",
            key="iso_search",
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            [
                "All Use Cases",
                "Approved",
                "Under Review",
                "Submitted",
                "Deferred",
                "Rejected",
            ],
            key="iso_status_filter",
        )

    display_records = records

    if search:
        q = search.lower()

        display_records = [
            r for r in display_records
            if (
                q in str(r.get("id", "")).lower()
                or q in str(r.get("problem_statement", "")).lower()
                or q in str(r.get("owner", "")).lower()
                or q in str(r.get("workflow_location", "")).lower()
            )
        ]

    if status_filter != "All Use Cases":
        display_records = [
            r for r in display_records
            if r.get("status") == status_filter
        ]

    if not display_records:
        st.info("No matching use cases found.")
        return

    for r in display_records:
        asmt = all_asmt.get(r["id"], {})
        checks = _iso_compliance_checks(r, asmt)

        # Weighted scoring: ok=1.0, partial=0.5, fail=0.0
        weights = {"ok": 1.0, "partial": 0.5, "fail": 0.0}
        total = len(checks)
        score_sum = sum(weights.get(c.get("status", "fail"), 0) for c in checks.values())
        pct = int(score_sum / total * 100) if total else 0
        color = "#1D9E75" if pct >= 80 else "#C07A10" if pct >= 50 else "#C0392B"
        ok_count = sum(1 for c in checks.values() if c.get("status") == "ok")
        partial_count = sum(1 for c in checks.values() if c.get("status") == "partial")
        summary_label = f"{ok_count} ✅ {partial_count} ⚠️ {total-ok_count-partial_count} ❌"

        with st.expander(f"**{r['id']}** · ISO Compliance {pct}% — {summary_label} — {r.get('action_owner','—')}", expanded=False):
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
              <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:4px;">
                <span style="color:{color};font-weight:700;">ISO 42001 Compliance Score</span>
                <span style="color:{color};font-weight:700;">{pct}%</span>
              </div>
              <div style="background:#F0F0F8;border-radius:6px;height:8px;">
                <div style="background:{color};width:{pct}%;height:8px;border-radius:6px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

            for clause in ISO_CLAUSES:
                chk    = checks.get(clause["id"], {"status": "fail", "note": "Not evaluated"})
                status = chk.get("status", "fail")
                note   = chk.get("note", "")
                icon   = {"ok": "✅", "partial": "⚠️", "fail": "❌"}.get(status, "❌")
                bcol   = {"ok": "#D1F5EA", "partial": "#FFF3CD", "fail": "#FDE8E8"}.get(status, "#FDE8E8")
                tcol   = {"ok": "#1D9E75", "partial": "#C07A10", "fail": "#C0392B"}.get(status, "#C0392B")
                # Evidence confidence badge
                if "[Direct evidence]" in note or "[M1 direct" in note:
                    badge = "<span style='background:#1D9E75;color:#fff;font-size:0.58rem;padding:1px 5px;border-radius:3px;margin-left:6px;font-weight:700;'>DIRECT</span>"
                elif "[M1 + M2 flag]" in note or "[M2 flag]" in note:
                    badge = "<span style='background:#C0392B;color:#fff;font-size:0.58rem;padding:1px 5px;border-radius:3px;margin-left:6px;font-weight:700;'>AI FLAG</span>"
                elif "[M1" in note:
                    badge = "<span style='background:#6C63FF;color:#fff;font-size:0.58rem;padding:1px 5px;border-radius:3px;margin-left:6px;font-weight:700;'>M1+M2</span>"
                elif "[M2 evidence]" in note or "[M2 direct]" in note:
                    badge = "<span style='background:#C07A10;color:#fff;font-size:0.58rem;padding:1px 5px;border-radius:3px;margin-left:6px;font-weight:700;'>M2</span>"
                else:
                    badge = ""
                # Strip all evidence tags from display note
                note_clean = (note
                    .replace("[Direct evidence]", "").replace("[M1 direct + M2]", "")
                    .replace("[M1 + M2]", "").replace("[M1 + M2 flag]", "")
                    .replace("[M2 direct]", "").replace("[M2 evidence]", "")
                    .replace("[M2 dimension only]", "").replace("[M2 flag]", "")
                    .replace("[M2 + flag]", "").replace("[M2 + M1]", "")
                    .strip()
                )
                st.markdown(f"""
                <div style="background:{bcol};border-radius:8px;padding:0.5rem 0.8rem;
                            margin-bottom:0.4rem;display:flex;align-items:flex-start;gap:8px;">
                  <span style="font-size:1rem;">{icon}</span>
                  <div style="flex:1;">
                    <div style="font-size:0.8rem;font-weight:700;color:{tcol};">
                      {clause['icon']} Clause {clause['id']} — {clause['label']} {badge}
                    </div>
                    <div style="font-size:0.72rem;color:#555;margin-top:2px;">{note_clean}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("**🏛️ Committee Action (ISO 42001 Clause 9.3 — Management Review)**")
            col_a, col_b = st.columns(2)
            with col_a:
                committee_note = st.text_area(
                    "Committee notes / conditions",
                    placeholder="Record conditions, concerns, or approval rationale here…",
                    key=f"iso_note_{r['id']}",
                    height=80
                )
            with col_b:
                decision = st.selectbox(
                    "Governance decision",
                    ["— Pending —", "✅ Approved — proceed", "⚠️ Conditional — address gaps first",
                     "❌ Rejected — does not meet ISO policy", "🔄 Deferred — revisit next cycle"],
                    key=f"iso_decision_{r['id']}"
                )
                if decision != "— Pending —":
                    status_map = {
                        "✅ Approved — proceed": "Approved",
                        "⚠️ Conditional — address gaps first": "Under Review",
                        "❌ Rejected — does not meet ISO policy": "Rejected",
                        "🔄 Deferred — revisit next cycle": "Deferred",
                    }
                    if st.button("💾 Record Decision", key=f"iso_save_{r['id']}", width='stretch'):
                        db_update_status(r["id"], status_map.get(decision, "Under Review"))
                        db_save_committee_note(r["id"], committee_note, decision)
                        st.success("ISO committee decision recorded.")
                        st.rerun()

    st.markdown("---")
    st.markdown("#### 📊 Portfolio ISO 42001 Summary")
    _iso_portfolio_chart(display_records, all_asmt)


def _iso_compliance_checks(r: dict, asmt: dict) -> dict:
    """
    ISO 42001 clause compliance — uses M1 fields as PRIMARY evidence,
    M2 governance_flags as SECONDARY, and M2 dimension scores as TERTIARY.

    Evidence priority per clause:
    ─────────────────────────────────────────────────────────────────────────
    6.1  Risk Identification     → M1 iso_risk_category (explicit ISO classification)
                                   + M2 risk_compliance_score (risk controls)
    6.2  AI Objectives & KPIs   → M1 success_criteria (ISO 42001 Clause 6.2 field)
                                   + M2 economic_viability_score (quantification)
    8.4  Human Oversight         → M1 human_override (explicit process documentation)
                                   + M2 workflow_maturity + governance_flags
    A.8  Data Governance         → M1 data_sources (PII & source declaration)
                                   + M2 data_readiness + privacy_review_required flag
    9.1  Performance Monitoring  → M1 success_criteria numeric thresholds (KPI targets)
                                   + M2 data_readiness (includes monitoring_plan sub-Q)
    10.1 Continual Improvement   → M2 ai_recommendation content (corrective actions)
                                   + M2 risk_compliance_score
    ─────────────────────────────────────────────────────────────────────────
    Status: "ok" / "partial" / "fail" → ✅ / ⚠️ / ❌
    Note tags: [Direct evidence] | [M1 + M2] | [M2 flag] | [M2 dimension only]
    """

    def s(key):
        return float(asmt.get(key, 0) or 0)

    resp  = _extract_responses(asmt)
    flags = resp.get("governance_flags", {}) if resp else {}

    # ── M1 fields (primary governance evidence) ───────────────────────────
    success_criteria = (r.get("success_criteria") or "").strip()
    human_override   = (r.get("human_override")   or "").strip()
    data_sources     = (r.get("data_sources")     or "").strip()
    iso_risk         = (r.get("iso_risk_category") or "").strip()

    has_success_criteria = len(success_criteria) > 15
    has_human_override   = len(human_override)   > 10
    has_data_sources     = len(data_sources)     > 8
    has_iso_risk         = bool(iso_risk)
    has_numeric_kpis     = has_success_criteria and any(c.isdigit() for c in success_criteria)

    # ── M2 governance flags (AI-flagged risk indicators) ──────────────────
    human_oversight_flag = bool(flags.get("human_oversight_required"))
    bias_flag            = bool(flags.get("bias_assessment_required"))
    privacy_flag         = bool(flags.get("privacy_review_required"))
    committee_flag       = bool(flags.get("additional_committee_review"))

    rc = s("risk_compliance_score")
    ev = s("economic_viability_score")
    wm = s("workflow_maturity_score")
    dr = s("data_readiness_score")
    cm = s("change_management_score")

    # ── Clause 6.1 — Risk Identification ─────────────────────────────────
    # PRIMARY: M1 iso_risk_category (explicit ISO 42001 Clause 6.1 classification)
    # SECONDARY: M2 risk_compliance_score
    if has_iso_risk and rc >= 3.5:
        c61 = ("ok",
               f"ISO Risk Category '{iso_risk}' classified (M1) · Risk & Compliance: {rc:.1f}/5. [Direct evidence]")
    elif has_iso_risk and rc >= 2.5:
        c61 = ("partial",
               f"ISO Risk Category '{iso_risk}' set (M1) · Risk & Compliance: {rc:.1f}/5 — review risk controls. [M1 + M2]")
    elif has_iso_risk:
        c61 = ("partial",
               f"ISO Risk Category '{iso_risk}' captured (M1) but Risk & Compliance score {rc:.1f}/5 is low. [M1 + M2]")
    elif rc >= 3.5:
        c61 = ("partial",
               f"Risk & Compliance: {rc:.1f}/5 — but ISO Risk Category not formally classified in M1. [M2 dimension only]")
    elif rc > 0:
        c61 = ("fail",
               f"Risk & Compliance: {rc:.1f}/5 · ISO Risk Category not set — risk identification incomplete. [M2 dimension only]")
    else:
        c61 = ("fail", "No M1 ISO risk classification and no M2 assessment — risk identification not evaluated.")

    # ── Clause 6.2 — AI Objectives & KPIs ────────────────────────────────
    # PRIMARY: M1 success_criteria (ISO 42001 Clause 6.2 explicitly requires
    # measurable AI success criteria and KPIs)
    # SECONDARY: M2 economic_viability_score (business case quantification)
    if has_success_criteria and ev >= 3.5:
        sc_preview = success_criteria[:70] + "…" if len(success_criteria) > 70 else success_criteria
        c62 = ("ok",
               f"Success criteria & KPIs defined in M1: '{sc_preview}' · Economic Viability: {ev:.1f}/5. [Direct evidence]")
    elif has_success_criteria and ev >= 2.5:
        c62 = ("partial",
               f"Success criteria defined (M1) · Economic Viability: {ev:.1f}/5 — KPIs may lack full quantification. [M1 + M2]")
    elif has_success_criteria:
        c62 = ("partial",
               f"M1 success criteria present · Economic Viability: {ev:.1f}/5 — business case needs strengthening. [M1 + M2]")
    elif ev >= 3.5:
        c62 = ("partial",
               f"Economic Viability: {ev:.1f}/5 — business case quantified, but no explicit success KPIs in M1. [M2 dimension only]")
    elif ev > 0:
        c62 = ("fail",
               f"Economic Viability: {ev:.1f}/5 · No M1 success criteria — measurable AI objectives not established. [M2 dimension only]")
    else:
        c62 = ("fail", "No M1 success criteria and no M2 assessment — AI objectives and KPIs not evaluated.")

    # ── Clause 8.4 — Human Oversight Defined ─────────────────────────────
    # PRIMARY: M1 human_override (explicit process documentation)
    # SECONDARY: M2 workflow_maturity + human_oversight_required flag
    if has_human_override and wm >= 3.5 and not human_oversight_flag:
        ho_preview = human_override[:70] + "…" if len(human_override) > 70 else human_override
        c84 = ("ok",
               f"Human override documented in M1: '{ho_preview}' · Workflow Maturity: {wm:.1f}/5. [Direct evidence]")
    elif has_human_override and human_oversight_flag:
        c84 = ("partial",
               f"Human override documented (M1) but M2 AI flagged additional oversight requirements — verify process completeness. [M1 + M2 flag]")
    elif has_human_override:
        c84 = ("partial",
               f"Human override documented (M1) · Workflow Maturity: {wm:.1f}/5 — process checkpoint could be stronger. [M1 + M2]")
    elif human_oversight_flag:
        c84 = ("fail",
               f"M2 AI explicitly flagged human oversight as required · Override mechanism missing in M1 · Workflow Maturity: {wm:.1f}/5. [M2 flag]")
    elif wm >= 3.5:
        c84 = ("partial",
               f"Workflow Maturity: {wm:.1f}/5 — process maturity implies oversight, but M1 human override field not completed. [M2 dimension only]")
    elif wm > 0:
        c84 = ("fail",
               f"Workflow Maturity: {wm:.1f}/5 · No human override documentation in M1. [M2 dimension only]")
    else:
        c84 = ("fail", "No M1 human override and no M2 assessment — human oversight mechanism not evaluated.")

    # ── Annex A.8 — Data Governance ──────────────────────────────────────
    # PRIMARY: M1 data_sources (explicit PII & data source declaration)
    # SECONDARY: M2 data_readiness + privacy_review_required flag
    if has_data_sources and dr >= 3.5 and not privacy_flag:
        ds_preview = data_sources[:70] + "…" if len(data_sources) > 70 else data_sources
        c_a8 = ("ok",
                f"Data sources & PII declared in M1: '{ds_preview}' · Data Readiness: {dr:.1f}/5. [Direct evidence]")
    elif has_data_sources and privacy_flag:
        c_a8 = ("partial",
                f"Data sources documented (M1) but M2 AI flagged a privacy review required — verify PII controls. [M1 + M2 flag]")
    elif has_data_sources:
        c_a8 = ("partial",
                f"Data sources declared (M1) · Data Readiness: {dr:.1f}/5 — data governance may need strengthening. [M1 + M2]")
    elif privacy_flag:
        c_a8 = ("fail",
                f"M2 AI flagged privacy review required · M1 data sources/PII field not completed · Data Readiness: {dr:.1f}/5. [M2 flag]")
    elif dr >= 3.5:
        c_a8 = ("partial",
                f"Data Readiness: {dr:.1f}/5 — infrastructure in place, but M1 data source/PII declaration missing. [M2 dimension only]")
    elif dr > 0:
        c_a8 = ("fail",
                f"Data Readiness: {dr:.1f}/5 · No M1 data source declaration — data governance not confirmed. [M2 dimension only]")
    else:
        c_a8 = ("fail", "No M1 data sources declaration and no M2 assessment — data governance not evaluated.")

    # ── Clause 9.1 — Performance Monitoring ──────────────────────────────
    # PRIMARY: M1 success_criteria with numeric thresholds (monitoring targets)
    # SECONDARY: M2 data_readiness (M2 prompt includes monitoring_plan sub-Q
    # for NIST MEASURE 2.7 within this dimension — better fit than change_management)
    monitoring_score = max(dr, cm)
    if has_numeric_kpis and dr >= 3.5:
        c91 = ("ok",
               f"Numeric KPIs in M1 success criteria · Data Readiness: {dr:.1f}/5 (incl. monitoring plan sub-question). [Direct evidence]")
    elif has_numeric_kpis and monitoring_score >= 2.5:
        c91 = ("partial",
               f"Numeric thresholds in M1 success criteria · Monitoring score: {monitoring_score:.1f}/5 — formalise post-deployment plan. [M1 + M2]")
    elif has_numeric_kpis:
        c91 = ("partial",
               f"Numeric KPIs exist in M1 · Monitoring score: {monitoring_score:.1f}/5 — monitoring plan weak. [M1 + M2]")
    elif has_success_criteria and monitoring_score >= 3.5:
        c91 = ("partial",
               f"Success criteria defined (M1) · Monitoring score: {monitoring_score:.1f}/5 — add numeric thresholds to strengthen 9.1. [M1 + M2]")
    elif monitoring_score >= 3.5:
        c91 = ("partial",
               f"Monitoring score: {monitoring_score:.1f}/5 — monitoring plan implied, but no M1 measurable success criteria. [M2 dimension only]")
    elif monitoring_score > 0:
        c91 = ("fail",
               f"Monitoring score: {monitoring_score:.1f}/5 · No M1 success criteria — post-deployment monitoring plan missing. [M2 dimension only]")
    else:
        c91 = ("fail", "No M1 success criteria and no M2 assessment — performance monitoring not evaluated.")

    # ── Clause 10.1 — Continual Improvement ──────────────────────────────
    # PRIMARY: M2 ai_recommendation (captures corrective action recommendations)
    # SECONDARY: M2 risk_compliance_score + additional_committee_review flag
    ai_rec  = asmt.get("ai_recommendation", "") or ""
    has_rec = bool(ai_rec and len(ai_rec.strip()) > 20)

    if has_rec and rc >= 3.5 and not committee_flag:
        c101 = ("ok",
                f"M2 improvement recommendations present · Risk & Compliance: {rc:.1f}/5 — corrective action framework in place. [M2 evidence]")
    elif has_rec and committee_flag:
        c101 = ("partial",
                f"Recommendations recorded but M2 AI flagged additional committee review needed — escalate improvement plan. [M2 + flag]")
    elif has_rec:
        c101 = ("partial",
                f"M2 recommendations captured · Risk & Compliance: {rc:.1f}/5 — improvement loop partially established. [M2 evidence]")
    elif rc >= 3.5:
        c101 = ("partial",
                f"Risk & Compliance: {rc:.1f}/5 — controls in place, but no M2 improvement recommendations recorded. [M2 dimension only]")
    elif committee_flag:
        c101 = ("fail",
                f"M2 AI flagged committee review required · No recommendations · Risk & Compliance: {rc:.1f}/5. [M2 flag]")
    else:
        c101 = ("fail", "No M2 recommendations and no risk controls data — continual improvement not evidenced.")

    return {
        "6.1":  {"status": c61[0],  "note": c61[1]},
        "6.2":  {"status": c62[0],  "note": c62[1]},
        "8.4":  {"status": c84[0],  "note": c84[1]},
        "A.8":  {"status": c_a8[0], "note": c_a8[1]},
        "9.1":  {"status": c91[0],  "note": c91[1]},
        "10.1": {"status": c101[0], "note": c101[1]},
    }


def _iso_portfolio_chart(display_records, all_asmt):
    rows = []
    weights = {"ok": 1.0, "partial": 0.5, "fail": 0.0}
    for r in display_records:
        asmt = all_asmt.get(r["id"], {})
        checks = _iso_compliance_checks(r, asmt)
        total = len(checks)
        score_sum = sum(weights.get(c.get("status", "fail"), 0) for c in checks.values())
        pct = int(score_sum / total * 100) if total else 0
        rows.append({"ID": r["id"][:14], "ISO Compliance %": pct})

    if rows:
        try:
            import plotly.graph_objects as go
            rows_sorted = sorted(rows, key=lambda x: x["ISO Compliance %"], reverse=True)
            ids    = [r["ID"] for r in rows_sorted]
            values = [r["ISO Compliance %"] for r in rows_sorted]
            colors = ["#1D9E75" if v >= 80 else "#C07A10" if v >= 50 else "#C0392B" for v in values]
            fig = go.Figure(go.Bar(
                x=ids, y=values,
                marker_color=colors,
                text=[f"{v}%" for v in values],
                textposition="outside",
                textfont=dict(size=12, color="#444"),
            ))
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=10, r=10, t=20, b=40),
                yaxis=dict(title="Compliance %", range=[0, 115], gridcolor="#F0F0F8", zeroline=False),
                xaxis=dict(tickfont=dict(size=11, color="#444")),
                height=320, bargap=0.3,
                shapes=[
                    dict(type="line", x0=-0.5, x1=len(ids)-0.5, y0=80, y1=80,
                         line=dict(color="#1D9E75", width=1.5, dash="dot")),
                    dict(type="line", x0=-0.5, x1=len(ids)-0.5, y0=50, y1=50,
                         line=dict(color="#C07A10", width=1.5, dash="dot")),
                ],
            )
            fig.add_annotation(x=len(ids)-0.5, y=81, text="80% target", showarrow=False,
                               font=dict(size=10, color="#1D9E75"), xanchor="right")
            st.plotly_chart(fig, width = 'stretch')
            st.caption("🟢 ≥ 80% Compliant · 🟡 50–79% Partial · 🔴 < 50% Non-compliant · Threshold lines shown")
        except ImportError:
            df = pd.DataFrame(rows).set_index("ID")
            st.bar_chart(df, color="#6C63FF")


# ── Tab 3: NIST AI RMF Technical Monitoring ─────────────────────────────────
def _tab_nist_monitoring():
    st.markdown("""
    <div style="background:#E8F5E9;border:1px solid #1D9E75;border-radius:12px;
                padding:0.8rem 1.2rem;margin:0.5rem 0 1rem;">
      <div style="font-size:0.78rem;font-weight:700;color:#0F6E56;letter-spacing:0.06em;">NIST AI RMF — TECHNICAL MONITORING</div>
      <div style="font-size:0.82rem;color:#444;margin-top:3px;">
        GOVERN · MAP · MEASURE · MANAGE signals tracking AI risk, drift, bias, explainability,
        and operational health across all active use cases.
      </div>
    </div>""", unsafe_allow_html=True)

    records = db_load_all()
    all_asmt = {a["problem_id"]: a for a in db_load_assessments()}
    all_gp = {g["problem_id"]: g for g in db_load_gainpain()}

    if not records:
        st.info("No use cases available.")
        return

    st.markdown("#### 🔍 Filter Use Cases")

    col1, col2 = st.columns([3, 2])

    with col1:
        search = st.text_input(
            "Search Use Cases",
            placeholder="Problem ID, owner, keyword...",
            key="nist_search",
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            [
                "All Use Cases",
                "Approved",
                "Under Review",
                "Submitted",
                "Deferred",
                "Rejected",
            ],
            key="nist_status_filter",
        )

    display_records = records

    if search:
        q = search.lower()
        display_records = [
            r for r in display_records
            if q in r.get("id", "").lower()
            or q in r.get("problem_statement", "").lower()
            or q in r.get("action_owner", "").lower()
        ]

    if status_filter != "All Use Cases":
        display_records = [
            r for r in display_records
            if r.get("status") == status_filter
        ]

    if not display_records:
        st.info("No matching use cases found.")
        return

    st.markdown("#### 🔬 NIST AI RMF Signal Matrix")
    st.markdown("<div style='font-size:0.8rem;color:#888;margin-bottom:0.8rem;'>"
                "Real-time compliance signals derived from M2 assessment scores. "
                "Green = within safe thresholds · Orange = attention required · Red = action needed.</div>",
                unsafe_allow_html=True)

    for r in display_records:
        asmt = all_asmt.get(r["id"], {})
        gp = all_gp.get(r["id"], {})
        signals = _nist_signals(r, asmt, gp)

        passed = sum(1 for s in signals.values() if s["status"] == "ok")
        warn = sum(1 for s in signals.values() if s["status"] == "warn")
        fail = sum(1 for s in signals.values() if s["status"] == "fail")

        health_label = "Healthy" if fail == 0 and warn <= 1 else "Attention" if fail <= 1 else "At Risk"

        with st.expander(
            f"**{r['id']}** · NIST Health: {health_label} · ✅{passed} ⚠️{warn} 🔴{fail} signals",
            expanded=False
        ):
            # ── NIST Function Summary ────────────────────────────────────────
            fn_groups = {"GOVERN": [], "MAP": [], "MEASURE": [], "MANAGE": []}
            for sig in NIST_SIGNALS:
                sv = signals.get(sig["id"], {"status": "warn", "score": 0})
                fn_groups[sig["fn"]].append(sv["status"])
            fn_cols = st.columns(4)
            fn_meta = {
                "GOVERN": ("#6C63FF", "Governance"),
                "MAP":    ("#0F6E56", "Mapping"),
                "MEASURE":("#C07A10", "Measurement"),
                "MANAGE": ("#C0392B", "Management"),
            }
            for fi, (fn, statuses) in enumerate(fn_groups.items()):
                fc, flabel = fn_meta[fn]
                fn_ok   = sum(1 for x in statuses if x == "ok")
                fn_warn = sum(1 for x in statuses if x == "warn")
                fn_fail = sum(1 for x in statuses if x == "fail")
                fn_pct  = int((fn_ok + fn_warn * 0.5) / max(len(statuses), 1) * 100)
                with fn_cols[fi]:
                    st.markdown(f"""
                    <div style="background:#fff;border:1.5px solid {fc}22;
                                border-top:3px solid {fc};border-radius:8px;
                                padding:0.5rem 0.7rem;text-align:center;">
                      <div style="font-size:0.62rem;font-weight:700;color:{fc};letter-spacing:0.06em;">{fn}</div>
                      <div style="font-size:1.1rem;font-weight:800;color:{fc};">{fn_pct}%</div>
                      <div style="font-size:0.62rem;color:#888;">✅{fn_ok} ⚠️{fn_warn} 🔴{fn_fail}</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

            # ── Signal Cards ─────────────────────────────────────────────────
            col1, col2 = st.columns(2)
            for i, sig in enumerate(NIST_SIGNALS):
                s = signals.get(sig["id"], {"status": "fail", "note": "Not evaluated", "score": 0, "source": ""})
                icol = col1 if i % 2 == 0 else col2
                sc = {"ok": "#1D9E75", "warn": "#C07A10", "fail": "#C0392B"}.get(s["status"], "#aaa")
                bg = {"ok": "#D1F5EA", "warn": "#FFF3CD", "fail": "#FDE8E8"}.get(s["status"], "#f5f5f5")
                emoji = {"ok": "✅", "warn": "⚠️", "fail": "🔴"}.get(s["status"], "—")
                fn_badge_col = {"GOVERN": "#6C63FF", "MAP": "#0F6E56", "MEASURE": "#C07A10", "MANAGE": "#C0392B"}.get(sig["fn"], "#888")
                note_clean = s["note"].replace("[M1 direct + M2]","").replace("[M1 + M2]","").replace("[M1 + M2 flag]","").replace("[M2 direct]","").replace("[M2 direct — best fit]","").replace("[M2 flag]","").replace("[M3 direct]","").replace("[M2 dimension]","").replace("[M2 + M1]","").replace("[M2 — incl. failure_impact_severity]","")
                src_label = s.get("source", "")

                with icol:
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:8px;padding:0.55rem 0.8rem;
                                margin-bottom:0.5rem;">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
                        <span style="font-size:0.78rem;font-weight:700;color:{sc};">
                          {emoji} {sig['icon']} {sig['label']}
                        </span>
                        <span style="font-size:0.65rem;font-weight:700;color:#fff;
                                     background:{fn_badge_col};border-radius:4px;padding:1px 6px;">
                          {sig['fn']}
                        </span>
                      </div>
                      <div style="font-size:0.72rem;color:#555;margin-bottom:3px;">{note_clean.strip()}</div>
                      {f'<div style="font-size:0.62rem;color:#999;font-style:italic;">📌 Evidence: {src_label}</div>' if src_label else ''}
                    </div>""", unsafe_allow_html=True)

            if asmt:
                st.markdown("**📊 NIST Risk Dimension Scores (from M2 Assessment)**")
                dims = {
                    "AI Suitability": float(asmt.get("ai_suitability_score", 0) or 0),
                    "Economic Viability": float(asmt.get("economic_viability_score", 0) or 0),
                    "Data Readiness": float(asmt.get("data_readiness_score", 0) or 0),
                    "Workflow Maturity": float(asmt.get("workflow_maturity_score", 0) or 0),
                    "Change Management": float(asmt.get("change_management_score", 0) or 0),
                    "Risk & Compliance": float(asmt.get("risk_compliance_score", 0) or 0),
                }
                df = pd.DataFrame.from_dict(dims, orient="index", columns=["Score"])
                df.index.name = "Dimension"
                st.bar_chart(df, color="#1D9E75")

            if asmt.get("hard_gate_triggered"):
                st.error(f"🚨 **NIST Hard Gate Triggered** — {asmt.get('hard_gate_reason','')}\n\n"
                         f"This use case requires immediate remediation before deployment.")

            if gp:
                op_risk = float(gp.get("operational_risk", 0))
                if op_risk >= 3.5:
                    st.warning(f"⚠️ **NIST MAP 2.3 — Elevated Operational Risk** ({op_risk:.1f}/5): "
                               f"Failure impact is significant. Ensure incident response plan is active.")

    st.markdown("---")
    st.markdown("#### 🌡️ Portfolio Risk Heatmap")
    _nist_heatmap(display_records, all_asmt)


def _nist_signals(r: dict, asmt: dict, gp: dict) -> dict:
    """
    NIST AI RMF signal derivation — uses M1 fields as PRIMARY evidence,
    M2 governance_flags as SECONDARY, and M2 dimension scores as TERTIARY.

    Key improvements over old version:
    ──────────────────────────────────────────────────────────────────────────
    govern_1_1  AI Context Mapped      → M2 ai_suitability (unchanged — best fit)

    govern_1_2  Human-in-Loop Verified → M1 human_override field (PRIMARY)
                                          + M2 workflow_maturity
                                          + governance_flags.human_oversight_required

    map_2_2     Bias Audit Status      → M2 data_readiness + bias_assessment_required flag
                                          (data_readiness includes bias evaluation per M2 prompt)

    map_2_3     Failure Impact Assessed→ M3 Operational Risk (primary)
                                          → M2 ai_suitability (fallback: M2 prompt
                                          includes failure_impact_severity sub-question)

    measure_2_5 Explainability         → M2 data_readiness (M2 prompt explicitly
                                          includes explainability NIST MEASURE 2.5
                                          in this dimension — better than change_management)

    measure_2_7 Drift Monitoring Active→ M2 data_readiness (M2 prompt explicitly
                                          includes monitoring_plan NIST MEASURE 2.7
                                          in this dimension)
                                          + M1 success_criteria numeric thresholds

    manage_2_4  Incident Response Ready→ M2 risk_compliance (unchanged — best fit)

    govern_6_1  Ethical Risk Cleared   → M2 risk_compliance (M2 prompt explicitly
                                          includes ethical_risk NIST GOVERN 6.1
                                          in this dimension)
                                          + M1 iso_risk_category + hard_gate
    ──────────────────────────────────────────────────────────────────────────
    """
    signals = {}

    def s(key):
        return float(asmt.get(key, 0) or 0)

    resp  = _extract_responses(asmt)
    flags = resp.get("governance_flags", {}) if resp else {}

    # M1 fields
    human_override   = (r.get("human_override")    or "").strip()
    success_criteria = (r.get("success_criteria")  or "").strip()
    data_sources     = (r.get("data_sources")      or "").strip()
    iso_risk         = (r.get("iso_risk_category") or "").strip()

    has_human_override   = len(human_override)   > 10
    has_success_criteria = len(success_criteria) > 15
    has_data_sources     = len(data_sources)     > 8
    has_numeric_kpis     = has_success_criteria and any(c.isdigit() for c in success_criteria)

    human_oversight_flag = bool(flags.get("human_oversight_required"))
    bias_flag            = bool(flags.get("bias_assessment_required"))
    privacy_flag         = bool(flags.get("privacy_review_required"))

    ai_suit = s("ai_suitability_score")
    wm      = s("workflow_maturity_score")
    dr      = s("data_readiness_score")
    cm      = s("change_management_score")
    rc      = s("risk_compliance_score")

    # ── GOVERN 1.1 — AI Context Mapped (AI Suitability) ──────────────────
    # M2 ai_suitability captures problem context, deployment environment, and
    # affected population mapping — the core of NIST MAP 1.1
    signals["govern_1_1"] = {
        "status": "ok"   if ai_suit >= 3.5 else
                  "warn" if ai_suit >= 2.5 else
                  "fail" if ai_suit >  0   else "warn",
        "note": (f"AI Suitability: {ai_suit:.1f}/5 — problem context and deployment environment well-mapped. [M2 direct]"
                 if ai_suit >= 3.5 else
                 f"AI Suitability: {ai_suit:.1f}/5 — AI context mapping needs strengthening. [M2 direct]"
                 if ai_suit > 0 else
                 "No M2 assessment — AI context mapping not evaluated."),
        "score": ai_suit,
        "source": "M2 AI Suitability score",
    }

    # ── GOVERN 1.2 — Human-in-Loop Verified ──────────────────────────────
    # PRIMARY: M1 human_override (explicit process documentation)
    # SECONDARY: M2 workflow_maturity (process checkpoint scoring)
    # FLAG: human_oversight_required (AI-flagged risk)
    if has_human_override and wm >= 3.5 and not human_oversight_flag:
        signals["govern_1_2"] = {
            "status": "ok",
            "note": f"Human review mechanism documented in M1 · Workflow Maturity: {wm:.1f}/5. [M1 direct + M2]",
            "score": wm,
            "source": "M1 human_override field (primary) + M2 Workflow Maturity",
        }
    elif has_human_override and human_oversight_flag:
        signals["govern_1_2"] = {
            "status": "warn",
            "note": f"Human override documented (M1) but M2 AI flagged oversight gaps — verify process. Workflow Maturity: {wm:.1f}/5. [M1 + M2 flag]",
            "score": wm,
            "source": "M1 human_override + M2 governance_flags (human_oversight_required)",
        }
    elif has_human_override:
        signals["govern_1_2"] = {
            "status": "ok" if wm >= 3.5 else "warn",
            "note": f"Human override documented (M1) · Workflow Maturity: {wm:.1f}/5. [M1 direct + M2]",
            "score": wm,
            "source": "M1 human_override field (primary) + M2 Workflow Maturity",
        }
    elif human_oversight_flag:
        signals["govern_1_2"] = {
            "status": "fail",
            "note": f"M2 AI flagged human oversight required · Override mechanism missing in M1 · Workflow Maturity: {wm:.1f}/5. [M2 flag]",
            "score": wm,
            "source": "M2 governance_flags (human_oversight_required)",
        }
    else:
        signals["govern_1_2"] = {
            "status": "ok"   if wm >= 3.5 else "warn" if wm >= 2.5 else "fail" if wm > 0 else "warn",
            "note": (f"Workflow Maturity: {wm:.1f}/5 — human checkpoint implied; formalise M1 override mechanism. [M2 dimension]"
                     if wm > 0 else "No M2 assessment and no M1 override mechanism — human-in-loop not verified."),
            "score": wm,
            "source": "M2 Workflow Maturity score",
        }

    # ── MAP 2.2 — Bias Audit Status ───────────────────────────────────────
    # PRIMARY: bias_assessment_required flag (AI directly flagged this)
    # SECONDARY: M2 data_readiness (M2 prompt includes bias evaluation explicitly)
    # TERTIARY: M1 data_sources (evidence of structured data governance)
    if bias_flag:
        signals["map_2_2"] = {
            "status": "fail",
            "note": f"M2 AI explicitly flagged bias assessment as required · Data Readiness: {dr:.1f}/5. [M2 flag]",
            "score": dr,
            "source": "M2 governance_flags (bias_assessment_required) — highest priority signal",
        }
    elif dr >= 3.5 and has_data_sources:
        signals["map_2_2"] = {
            "status": "ok",
            "note": f"Data Readiness: {dr:.1f}/5 · M1 data sources declared — training data evaluated for quality and bias. [M2 + M1]",
            "score": dr,
            "source": "M2 Data Readiness (incl. bias evaluation) + M1 data_sources",
        }
    elif dr >= 3.5:
        signals["map_2_2"] = {
            "status": "ok",
            "note": f"Data Readiness: {dr:.1f}/5 — training data evaluated for bias (per M2 assessment criteria). [M2 direct]",
            "score": dr,
            "source": "M2 Data Readiness score (includes bias evaluation)",
        }
    elif dr >= 2.5:
        signals["map_2_2"] = {
            "status": "warn",
            "note": f"Data Readiness: {dr:.1f}/5 — bias audit may be incomplete. [M2 direct]",
            "score": dr,
            "source": "M2 Data Readiness score",
        }
    else:
        signals["map_2_2"] = {
            "status": "fail" if dr > 0 else "warn",
            "note": (f"Data Readiness: {dr:.1f}/5 — bias audit not confirmed. [M2 direct]" if dr > 0
                     else "No M2 assessment — bias audit status not evaluated."),
            "score": dr,
            "source": "M2 Data Readiness score",
        }

    # ── MAP 2.3 — Failure Impact Assessed ────────────────────────────────
    # PRIMARY: M3 operational_risk (direct failure impact score, inverted)
    # SECONDARY: M2 ai_suitability (M2 prompt includes failure_impact_severity
    # sub-question for NIST MAP 2.3 within ai_suitability dimension)
    op_risk = float(gp.get("operational_risk", 0) or 0) if gp else 0
    if op_risk > 0:
        signals["map_2_3"] = {
            "status": "ok"   if op_risk <= 2.5 else "warn" if op_risk <= 3.5 else "fail",
            "note": (f"M3 Operational Risk: {op_risk:.1f}/5 — failure impact low and managed. [M3 direct]"
                     if op_risk <= 2.5 else
                     f"M3 Operational Risk: {op_risk:.1f}/5 — elevated; failure impact plan needed. [M3 direct]"
                     if op_risk <= 3.5 else
                     f"M3 Operational Risk: {op_risk:.1f}/5 — high failure impact; immediate mitigation required. [M3 direct]"),
            "score": op_risk,
            "source": "M3 Operational Risk (direct, inverted scale)",
        }
    else:
        # Fallback: ai_suitability explicitly includes failure_impact_severity sub-question
        signals["map_2_3"] = {
            "status": "ok"   if ai_suit >= 3.5 else "warn" if ai_suit >= 2.5 else "fail" if ai_suit > 0 else "warn",
            "note": (f"AI Suitability: {ai_suit:.1f}/5 includes failure severity assessment (M3 not run). [M2 — incl. failure_impact_severity]"
                     if ai_suit > 0 else "No M2/M3 data — failure impact not assessed."),
            "score": ai_suit,
            "source": "M2 AI Suitability (incl. failure_impact_severity sub-Q) — M3 not run",
        }

    # ── MEASURE 2.5 — Explainability Confirmed ───────────────────────────
    # M2 data_readiness dimension — M2 prompt explicitly states:
    # "explainability (NIST MEASURE 2.5)" as a scored element within data_readiness.
    # This is the most precise mapping available without per-question sub-scores.
    # (Previous version used change_management which has NO explainability sub-question.)
    signals["measure_2_5"] = {
        "status": "ok"   if dr >= 3.5 else
                  "warn" if dr >= 2.5 else
                  "fail" if dr >  0   else "warn",
        "note": (f"Data Readiness: {dr:.1f}/5 — includes explainability assessment (NIST MEASURE 2.5 per M2 prompt). [M2 direct — best fit]"
                 if dr >= 3.5 else
                 f"Data Readiness: {dr:.1f}/5 — AI decision explainability to affected people needs confirmation. [M2 direct]"
                 if dr > 0 else
                 "No M2 assessment — explainability not confirmed."),
        "score": dr,
        "source": "M2 Data Readiness (includes explainability sub-question per M2 prompt)",
    }

    # ── MEASURE 2.7 — Drift Monitoring Active ────────────────────────────
    # M2 data_readiness dimension — M2 prompt explicitly states:
    # "monitoring_plan (NIST MEASURE 2.7)" as a scored element within data_readiness.
    # BONUS: M1 success_criteria with numeric thresholds → monitoring targets exist.
    # (Previous version used change_management or M3 compliance_burden — neither
    # has a direct monitoring_plan question.)
    if dr >= 3.5 and has_numeric_kpis:
        signals["measure_2_7"] = {
            "status": "ok",
            "note": f"Data Readiness: {dr:.1f}/5 (incl. monitoring plan sub-Q) · M1 numeric KPIs define drift thresholds. [M2 direct + M1]",
            "score": dr,
            "source": "M2 Data Readiness (incl. monitoring_plan sub-Q) + M1 success_criteria",
        }
    elif dr >= 3.5:
        signals["measure_2_7"] = {
            "status": "ok",
            "note": f"Data Readiness: {dr:.1f}/5 — monitoring plan sub-question confirmed; drift detection viable. [M2 direct]",
            "score": dr,
            "source": "M2 Data Readiness (includes monitoring_plan sub-question per M2 prompt)",
        }
    elif dr >= 2.5:
        signals["measure_2_7"] = {
            "status": "warn",
            "note": f"Data Readiness: {dr:.1f}/5 — monitoring plan may be insufficient; confirm drift detection setup. [M2 direct]",
            "score": dr,
            "source": "M2 Data Readiness score",
        }
    elif dr > 0:
        signals["measure_2_7"] = {
            "status": "fail",
            "note": f"Data Readiness: {dr:.1f}/5 — post-deployment monitoring plan likely missing. [M2 direct]",
            "score": dr,
            "source": "M2 Data Readiness score",
        }
    else:
        signals["measure_2_7"] = {
            "status": "warn",
            "note": "No M2 assessment — drift monitoring plan not confirmed.",
            "score": 0,
            "source": "No data available",
        }

    # ── MANAGE 2.4 — Incident Response Ready ─────────────────────────────
    # M2 risk_compliance dimension — M2 prompt: "regulatory compliance, ethical risk,
    # audit trail, third-party risk, legal liability" — all incident response components.
    signals["manage_2_4"] = {
        "status": "ok"   if rc >= 3.5 else
                  "warn" if rc >= 2.5 else
                  "fail" if rc >  0   else "warn",
        "note": (f"Risk & Compliance: {rc:.1f}/5 — incident response, audit trail, and risk controls confirmed. [M2 direct]"
                 if rc >= 3.5 else
                 f"Risk & Compliance: {rc:.1f}/5 — incident response plan needs strengthening. [M2 direct]"
                 if rc > 0 else
                 "No M2 assessment — incident response not evaluated."),
        "score": rc,
        "source": "M2 Risk & Compliance score (direct — best fit)",
    }

    # ── GOVERN 6.1 — Ethical Risk Cleared ────────────────────────────────
    # PRIMARY: M2 risk_compliance — M2 prompt explicitly states:
    # "ethical risk (NIST GOVERN 6.1)" as a scored element within risk_compliance.
    # This is a direct mapping (previous version used economic_viability — indirect).
    # OVERRIDE: hard_gate_triggered + M1 iso_risk_category (High/Unacceptable)
    hard_gate        = bool(asmt.get("hard_gate_triggered"))
    hard_gate_reason = asmt.get("hard_gate_reason", "ethical/compliance block")
    iso_risk_high    = iso_risk in ("High", "Unacceptable")

    if hard_gate:
        signals["govern_6_1"] = {
            "status": "fail",
            "note": f"Hard gate triggered — {hard_gate_reason}. [M2 hard gate]",
            "score": 0,
            "source": "M2 hard gate (ethical/compliance block — overrides all scores)",
        }
    elif iso_risk_high and rc < 3.5:
        signals["govern_6_1"] = {
            "status": "fail",
            "note": f"ISO Risk Category '{iso_risk}' (M1) · Risk & Compliance: {rc:.1f}/5 — ethical risks insufficiently mitigated for high-risk use case. [M1 + M2]",
            "score": rc,
            "source": "M1 iso_risk_category + M2 Risk & Compliance (incl. ethical_risk sub-Q)",
        }
    elif rc >= 3.5:
        signals["govern_6_1"] = {
            "status": "ok",
            "note": f"Risk & Compliance: {rc:.1f}/5 — includes ethical risk assessment (NIST GOVERN 6.1 per M2 prompt). {f'ISO Risk: {iso_risk} (M1).' if iso_risk else ''} [M2 direct]",
            "score": rc,
            "source": "M2 Risk & Compliance (incl. ethical_risk sub-question per M2 prompt)",
        }
    elif rc >= 2.5:
        signals["govern_6_1"] = {
            "status": "warn",
            "note": f"Risk & Compliance: {rc:.1f}/5 — ethical risk assessment may be incomplete. [M2 direct]",
            "score": rc,
            "source": "M2 Risk & Compliance score",
        }
    elif rc > 0:
        signals["govern_6_1"] = {
            "status": "fail",
            "note": f"Risk & Compliance: {rc:.1f}/5 — ethical risks (discrimination, manipulation) may be unmitigated. [M2 direct]",
            "score": rc,
            "source": "M2 Risk & Compliance score",
        }
    else:
        signals["govern_6_1"] = {
            "status": "warn",
            "note": "No M2 assessment — ethical risk not evaluated.",
            "score": 0,
            "source": "No data available",
        }

    return signals


def _nist_heatmap(records, all_asmt):
    rows = []
    for r in records:
        asmt = all_asmt.get(r["id"], {})
        rows.append({
            "ID": r["id"],
            "AI Suitability": float(asmt.get("ai_suitability_score", 0) or 0),
            "Data Readiness": float(asmt.get("data_readiness_score", 0) or 0),
            "Workflow Maturity": float(asmt.get("workflow_maturity_score", 0) or 0),
            "Risk & Compliance": float(asmt.get("risk_compliance_score", 0) or 0),
        })

    if rows:
        df = pd.DataFrame(rows).drop_duplicates(subset=["ID"]).reset_index(drop=True)
        score_cols = ["AI Suitability", "Data Readiness", "Workflow Maturity", "Risk & Compliance"]
        try:
            styled = df.style.background_gradient(cmap="RdYlGn", subset=score_cols, vmin=1, vmax=5)
            st.dataframe(styled, width='stretch')
        except Exception:
            st.dataframe(df, width='stretch')
        st.markdown("<div style='font-size:0.72rem;color:#aaa;'>🟢 ≥ 4.0 Safe · 🟡 2.5–3.9 Attention · 🔴 < 2.5 Action Required</div>",
                    unsafe_allow_html=True)


# ── Tab 4: Visuals ────────────────────────────────────────────────────────────
def _tab_graphs():
    """
    Six charts, no pie/doughnut:
    Row 1 (2 cols): Priority Distribution (horizontal bar) · Portfolio Status (grouped bar)
    Row 2 (2 cols): Gain vs Pain by Use Case (grouped vertical bar) · NIST Radar Spider
    Row 3 (1 col):  M2 Dimension Heatmap (styled DataFrame, scores across all use cases)
    Row 4 (1 col):  Feasibility Score Timeline (line chart, submission order as x-axis)
    """
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    records   = db_load_all()
    all_gp_l  = db_load_gainpain()
    all_asmt_l = db_load_assessments()
    all_gp    = {g["problem_id"]: g for g in all_gp_l}
    all_asmt  = {a["problem_id"]: a for a in all_asmt_l}

    CARD = """<div style="background:#fff;border:1px solid #EAEBF5;border-radius:14px;
              padding:1.2rem 1.4rem;margin-bottom:1.2rem;
              box-shadow:0 2px 8px rgba(0,0,0,0.04);">
              <div style="font-weight:700;font-size:1rem;color:#1A1A2E;margin-bottom:0.15rem;">{title}</div>
              <div style="font-size:0.78rem;color:#888;margin-bottom:1rem;">{sub}</div>"""
    CARD_END = "</div>"

    # ── Row 1 ─────────────────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)

    # Graph 1: AI Use Cases by Priority (horizontal bar)
    with col_l:
        st.markdown(CARD.format(
            title="AI Use Cases by Priority",
            sub="Distributed by Gain–Pain priority band (High ≥ 7.0 · Medium 4.0–6.9 · Low < 4.0)",
        ), unsafe_allow_html=True)
        if not all_gp_l:
            st.info("Complete Module 3 to see priority distribution.")
        else:
            counts = {"High Priority": 0, "Medium Priority": 0, "Low Priority": 0}
            for g in all_gp_l:
                sc = float(g.get("priority_score_scaled") or 0)
                counts["High Priority" if sc >= 7 else "Medium Priority" if sc >= 4 else "Low Priority"] += 1
            labels = ["Low Priority", "Medium Priority", "High Priority"]
            values = [counts[l] for l in labels]
            colors = ["#C0392B", "#C07A10", "#1D9E75"]
            fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
                                   marker_color=colors, text=values,
                                   textposition="outside", textfont=dict(size=13)))
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(l=10, r=30, t=10, b=20),
                              xaxis=dict(title="Use Cases", gridcolor="#F0F0F8", zeroline=False),
                              yaxis=dict(showgrid=False), bargap=0.38, height=260)
            st.plotly_chart(fig, width = 'stretch')
        st.markdown(CARD_END, unsafe_allow_html=True)

    # Graph 2: Portfolio Status (grouped vertical bar, not pie)
    with col_r:
        st.markdown(CARD.format(
            title="Portfolio Status",
            sub="Count of use cases by committee decision status",
        ), unsafe_allow_html=True)
        if not records:
            st.info("Submit a use case to see portfolio status.")
        else:
            order  = ["Approved", "Under Review", "Submitted", "Deferred", "Rejected"]
            clrs   = {"Approved": "#1D9E75", "Under Review": "#C07A10",
                      "Submitted": "#6C63FF", "Deferred": "#8B2FC9", "Rejected": "#C0392B"}
            cnts   = {d: 0 for d in order}
            for r in records:
                status_val = r.get("status", "Submitted")
                cnts[status_val if status_val in cnts else "Submitted"] += 1
            active = {k: v for k, v in cnts.items() if v > 0}
            fig = go.Figure(go.Bar(
                x=list(active.keys()), y=list(active.values()),
                marker_color=[clrs.get(k, "#6C63FF") for k in active],
                text=list(active.values()), textposition="outside",
                textfont=dict(size=13),
            ))
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(l=10, r=10, t=10, b=20),
                              yaxis=dict(gridcolor="#F0F0F8", zeroline=False),
                              xaxis=dict(showgrid=False), bargap=0.35, height=260)
            st.plotly_chart(fig, width = 'stretch')
        st.markdown(CARD_END, unsafe_allow_html=True)

    # ── Row 2 ─────────────────────────────────────────────────────────────────
    col_l2, col_r2 = st.columns(2)

    # Graph 3: Gain vs Pain by Use Case (grouped vertical bar)
    with col_l2:
        st.markdown(CARD.format(
            title="Gain vs Pain Scores",
            sub="Average gain score (higher = better) vs average pain score (lower = better) per use case",
        ), unsafe_allow_html=True)
        gp_rows = [(r["id"][:12], float(all_gp[r["id"]].get("avg_gains", 0) or 0),
                    float(all_gp[r["id"]].get("avg_pains", 0) or 0))
                   for r in records if r["id"] in all_gp]
        if not gp_rows:
            st.info("Complete Module 3 (Gain–Pain) for at least one use case.")
        else:
            ids, gains, pains = zip(*gp_rows)
            fig = go.Figure([
                go.Bar(name="Gain", x=list(ids), y=list(gains), marker_color="#1D9E75",
                       text=[f"{v:.1f}" for v in gains], textposition="outside"),
                go.Bar(name="Pain", x=list(ids), y=list(pains), marker_color="#C0392B",
                       text=[f"{v:.1f}" for v in pains], textposition="outside"),
            ])
            fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(l=10, r=10, t=10, b=20),
                              yaxis=dict(range=[0, 6.5], gridcolor="#F0F0F8", zeroline=False),
                              xaxis=dict(showgrid=False), bargap=0.25, bargroupgap=0.05,
                              legend=dict(orientation="h", y=-0.25), height=280)
            st.plotly_chart(fig, width = 'stretch')
        st.markdown(CARD_END, unsafe_allow_html=True)

    # Graph 4: NIST Risk Dimensions — Spider/Radar for selected use case
    with col_r2:
        st.markdown(CARD.format(
            title="NIST Risk Dimensions — Radar",
            sub="M2 feasibility scores across all six NIST-mapped dimensions for each assessed use case",
        ), unsafe_allow_html=True)
        asmt_rows = [(r["id"][:12], all_asmt[r["id"]]) for r in records if r["id"] in all_asmt]
        if not asmt_rows:
            st.info("Complete Module 2 (Use-case Scoring & Prioritization) to see radar charts.")
        else:
            dims = ["AI Suit.", "Econ. Viab.", "Data Ready", "Workflow", "Change Mgmt", "Risk & Comp."]
            keys = ["ai_suitability_score", "economic_viability_score", "data_readiness_score",
                    "workflow_maturity_score", "change_management_score", "risk_compliance_score"]
            pal  = ["#6C63FF", "#1D9E75", "#C07A10", "#C0392B", "#8B2FC9", "#0F6E56"]
            fig  = go.Figure()
            for i, (pid, asmt) in enumerate(asmt_rows[:6]):   # max 6 traces
                vals = [float(asmt.get(k, 0) or 0) for k in keys]
                vals_closed = vals + [vals[0]]
                fig.add_trace(go.Scatterpolar(
                    r=vals_closed, theta=dims + [dims[0]],
                    name=pid, line=dict(color=pal[i % len(pal)], width=2),
                    fill="toself", fillcolor=pal[i % len(pal)],
                    opacity=0.15,
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=9))),
                showlegend=True, legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
                paper_bgcolor="white", margin=dict(l=30, r=30, t=20, b=50), height=300,
            )
            st.plotly_chart(fig, width = 'stretch')
        st.markdown(CARD_END, unsafe_allow_html=True)

    # ── Row 3: M2 Dimension Heatmap ────────────────────────────────────────
    st.markdown(CARD.format(
        title="M2 Feasibility Heatmap",
        sub="All six assessment dimensions across every use case — red < 2.5 · yellow 2.5–3.9 · green ≥ 4.0",
    ), unsafe_allow_html=True)
    score_keys = ["ai_suitability_score", "economic_viability_score", "data_readiness_score",
                  "workflow_maturity_score", "change_management_score", "risk_compliance_score"]
    col_labels = ["AI Suitability", "Econ. Viability", "Data Readiness",
                  "Workflow Maturity", "Change Mgmt", "Risk & Compliance"]
    hm_rows = []
    for r in records:
        asmt = all_asmt.get(r["id"], {})
        if any(asmt.get(k) for k in score_keys):
            row = {"Use Case": r["id"][:14]}
            for k, label in zip(score_keys, col_labels):
                row[label] = round(float(asmt.get(k, 0) or 0), 1)
            hm_rows.append(row)
    if not hm_rows:
        st.info("Complete Module 2 (Use-case Scoring & Prioritization) for at least one use case.")
    else:
        df_hm = pd.DataFrame(hm_rows).set_index("Use Case")
        try:
            styled = (df_hm.style
                      .background_gradient(cmap="RdYlGn", vmin=1, vmax=5)
                      .format("{:.1f}"))
            st.dataframe(styled, width = 'stretch')
        except Exception:
            st.dataframe(df_hm, width = 'stretch')
        st.caption("🟢 ≥ 4.0 Strong · 🟡 2.5–3.9 Attention · 🔴 < 2.5 Action Required")
    st.markdown(CARD_END, unsafe_allow_html=True)

    # ── Row 4: Feasibility Score over Submissions (line chart) ─────────────
    st.markdown(CARD.format(
        title="Feasibility Score Trend",
        sub="Overall feasibility score per use case in submission order — tracks portfolio quality over time",
    ), unsafe_allow_html=True)
    trend_rows = []
    for i, r in enumerate(records):
        asmt = all_asmt.get(r["id"], {})
        scores = [float(asmt.get(k, 0) or 0) for k in score_keys]
        scored = [s for s in scores if s > 0]
        if scored:
            trend_rows.append({
                "x":     i + 1,
                "label": r["id"][:10],
                "score": round(sum(scored) / len(scored), 2),
            })
    if len(trend_rows) < 2:
        st.info("At least 2 assessed use cases needed to show trend.")
    else:
        xs     = [t["x"]     for t in trend_rows]
        labels = [t["label"] for t in trend_rows]
        ys     = [t["score"] for t in trend_rows]
        avg    = sum(ys) / len(ys)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines+markers+text",
            text=labels, textposition="top center",
            textfont=dict(size=9), name="Avg Feasibility",
            line=dict(color="#6C63FF", width=2.5),
            marker=dict(color=["#1D9E75" if v >= 3.5 else "#C07A10" if v >= 2.5 else "#C0392B"
                                for v in ys], size=9),
        ))
        fig.add_hline(y=3.5, line_dash="dot", line_color="#1D9E75",
                      annotation_text="Target ≥ 3.5", annotation_position="right")
        fig.add_hline(y=avg, line_dash="dash", line_color="#6C63FF",
                      annotation_text=f"Portfolio avg {avg:.2f}", annotation_position="right")
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=100, t=20, b=30),
            yaxis=dict(range=[0, 5.5], gridcolor="#F0F0F8", zeroline=False,
                       title="Avg Score /5"),
            xaxis=dict(title="Submission order", showgrid=False, tickvals=xs, ticktext=labels,
                       tickfont=dict(size=9)),
            height=320, showlegend=False,
        )
        st.plotly_chart(fig, width = 'stretch')
    st.markdown(CARD_END, unsafe_allow_html=True)


# ── Preserved utility (not wired into a tab in My Project's original app
#    either — kept available for future use, e.g. inside Tab 1's drilldown) ──
def _render_smart_questions(result: dict):
    teams = result.get("teams", {})
    summary = result.get("analysis_gaps_summary", "")

    if summary:
        st.markdown(f"""
        <div style="background:#FAFAFE;border-left:3px solid #C07A10;
                    border-radius:0 8px 8px 0;padding:0.7rem 1rem;
                    font-size:0.85rem;color:#444;margin-bottom:1.2rem;">
          <strong>📋 Gap Analysis:</strong> {summary}
        </div>""", unsafe_allow_html=True)

    for team_name, team_data in teams.items():
        color = TEAM_COLORS.get(team_name, "#6C63FF")
        qs = team_data.get("questions", [])
        rationale = team_data.get("rationale", "")

        st.markdown(f"""
        <div style="border-left:4px solid {color};padding-left:1rem;margin-bottom:1.2rem;">
          <div style="font-size:0.85rem;font-weight:700;color:{color};margin-bottom:4px;">
            👥 {team_name}
          </div>
          <div style="font-size:0.78rem;color:#888;margin-bottom:0.6rem;font-style:italic;">
            {rationale}
          </div>
        """, unsafe_allow_html=True)

        for i, q in enumerate(qs, 1):
            dim = q.get("dimension", "")
            qtext = q.get("question", "")
            why = q.get("why", "")
            st.markdown(f"""
            <div style="background:#FAFAFE;border:1px solid #EAEBF5;border-radius:8px;
                        padding:0.6rem 0.9rem;margin-bottom:0.4rem;">
              <div style="font-size:0.82rem;font-weight:600;color:#1a1a2e;">
                Q{i}. {qtext}
              </div>
              <div style="font-size:0.72rem;color:{color};margin-top:3px;">
                📌 Impacts: <strong>{dim}</strong> · {why}
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📝 Record Team Responses** *(optional — answers will inform re-analysis)*")
    st.text_area(
        "Paste or type team responses here",
        placeholder="Technical team confirmed monitoring plan exists using DataDog with 30-day drift detection…\n"
                    "Finance team verified budget allocation of ₹45L for Phase 1…",
        height=120,
        key="m4_team_responses"
    )
    if st.button("💾 Save Responses", width='content'):
        responses = st.session_state.get("m4_team_responses", "")
        if responses:
            db_save_team_responses(st.session_state.get("m4_smart_q_pid", ""), responses)
            st.success("Responses saved. Run Module 3 Gain-Pain analysis again to incorporate new evidence.")


# ==========================================
# RENDER
# ==========================================

_render_header()

t1, t2, t3, t4 = st.tabs([
    "📋 Overview",
    "🏛️ Org Governance (ISO 42001)",
    "🔬 Technical Monitoring (NIST)",
    "📊 Visuals",
])

with t1:
    _tab_overview()
with t2:
    _tab_iso_governance()
with t3:
    _tab_nist_monitoring()
with t4:
    _tab_graphs()
