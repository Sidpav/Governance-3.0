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

st.set_page_config(page_title="AI Governance Platform", page_icon="🤖",
                    layout="wide", initial_sidebar_state="expanded")

apply_theme()
render_sidebar("m5")
render_navbar("m5")
render_breadcrumb("Problem Selection", "Governance Board")

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

    st.title("Governance Dashboard")
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

    if not records:
        st.info("No use cases available. Complete Module 1 first.")
        return

    st.markdown("#### 📋 ISO 42001 Clause Compliance Matrix")
    st.markdown("<div style='font-size:0.8rem;color:#888;margin-bottom:0.8rem;'>"
                "Automated compliance check based on captured M1 + M2 data.</div>",
                unsafe_allow_html=True)

    for r in records:
        asmt = all_asmt.get(r["id"], {})
        checks = _iso_compliance_checks(r, asmt)

        passed = sum(1 for c in checks.values() if c["ok"])
        total = len(checks)
        pct = int(passed / total * 100)
        color = "#1D9E75" if pct >= 80 else "#C07A10" if pct >= 50 else "#C0392B"

        with st.expander(f"**{r['id']}** · ISO Compliance {pct}% ({passed}/{total} clauses) — {r.get('action_owner','—')}", expanded=False):
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
                chk = checks.get(clause["id"], {"ok": False, "note": "Not evaluated"})
                icon = "✅" if chk["ok"] else "⚠️"
                bcol = "#D1F5EA" if chk["ok"] else "#FFF3CD"
                tcol = "#1D9E75" if chk["ok"] else "#C07A10"
                st.markdown(f"""
                <div style="background:{bcol};border-radius:8px;padding:0.5rem 0.8rem;
                            margin-bottom:0.4rem;display:flex;align-items:flex-start;gap:8px;">
                  <span style="font-size:1rem;">{icon}</span>
                  <div>
                    <div style="font-size:0.8rem;font-weight:700;color:{tcol};">
                      {clause['icon']} Clause {clause['id']} — {clause['label']}
                    </div>
                    <div style="font-size:0.72rem;color:#666;margin-top:2px;">{chk['note']}</div>
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
    _iso_portfolio_chart(records, all_asmt)


def _iso_compliance_checks(r: dict, asmt: dict) -> dict:
    """Map M1/M2 data to ISO 42001 clause compliance."""
    iso = r.get("iso_risk_category", "")

    checks = {}
    checks["6.1"] = {
        "ok": bool(iso and iso not in ["", "None"]),
        "note": f"ISO risk category: {iso}" if iso else "ISO risk category not captured in M1."
    }

    sc = r.get("success_criteria", "")
    checks["6.2"] = {
        "ok": bool(sc and len(sc) > 10),
        "note": f"KPIs defined: {sc[:80]}…" if sc else "Success criteria / KPIs not captured."
    }

    ho = r.get("human_override", "")
    checks["8.4"] = {
        "ok": bool(ho and len(ho) > 10),
        "note": f"Override mechanism: {ho[:80]}…" if ho else "Human override process not documented."
    }

    ds = r.get("data_sources", "")
    checks["A.8"] = {
        "ok": bool(ds and len(ds) > 10),
        "note": f"Data sources: {ds[:80]}…" if ds else "Data sources and PII handling not declared."
    }

    mon = float(asmt.get("data_readiness_score", 0) or 0)
    checks["9.1"] = {
        "ok": mon >= 3.5,
        "note": f"M2 Data Readiness (includes monitoring plan): {mon:.1f}/5" if mon else "No M2 assessment available."
    }

    ai_rec = asmt.get("ai_recommendation", "")
    checks["10.1"] = {
        "ok": bool(ai_rec and len(ai_rec) > 20),
        "note": "M2 recommendations captured — corrective actions available." if ai_rec else "No M2 AI recommendations to drive improvement."
    }

    return checks


def _iso_portfolio_chart(records, all_asmt):
    rows = []
    for r in records:
        asmt = all_asmt.get(r["id"], {})
        checks = _iso_compliance_checks(r, asmt)
        passed = sum(1 for c in checks.values() if c["ok"])
        rows.append({"ID": r["id"][:12], "ISO Compliance %": int(passed / len(checks) * 100)})

    if rows:
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

    approved_records = [r for r in records if r.get("status") in ["Approved", "Under Review"]]
    if not approved_records:
        st.info("No Approved or Under Review use cases to monitor. Use Tab 2 to approve use cases.")
        all_records_option = st.checkbox("Show all use cases regardless of status")
        approved_records = records if all_records_option else []
        if not approved_records:
            return

    st.markdown("#### 🔬 NIST AI RMF Signal Matrix")
    st.markdown("<div style='font-size:0.8rem;color:#888;margin-bottom:0.8rem;'>"
                "Real-time compliance signals derived from M2 assessment scores. "
                "Green = within safe thresholds · Orange = attention required · Red = action needed.</div>",
                unsafe_allow_html=True)

    for r in approved_records:
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
            col1, col2 = st.columns(2)
            for i, sig in enumerate(NIST_SIGNALS):
                s = signals.get(sig["id"], {"status": "fail", "note": "Not evaluated", "score": 0})
                icol = col1 if i % 2 == 0 else col2
                sc = {"ok": "#1D9E75", "warn": "#C07A10", "fail": "#C0392B"}.get(s["status"], "#aaa")
                bg = {"ok": "#D1F5EA", "warn": "#FFF3CD", "fail": "#FDE8E8"}.get(s["status"], "#f5f5f5")
                emoji = {"ok": "✅", "warn": "⚠️", "fail": "🔴"}.get(s["status"], "—")
                fn_badge_col = {"GOVERN": "#6C63FF", "MAP": "#0F6E56", "MEASURE": "#C07A10", "MANAGE": "#C0392B"}.get(sig["fn"], "#888")

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
                      <div style="font-size:0.72rem;color:#666;">{s['note']}</div>
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
    _nist_heatmap(approved_records, all_asmt)


def _nist_signals(r: dict, asmt: dict, gp: dict) -> dict:
    """Derive NIST signal status from M1/M2/M3 data."""
    signals = {}

    def score(key):
        return float(asmt.get(key, 0) or 0)

    m1_complete = all(r.get(k) for k in ["problem_statement", "business_objective", "solution_approach",
                                          "affected_stakeholders", "iso_risk_category"])
    signals["govern_1_1"] = {
        "status": "ok" if m1_complete else "warn",
        "note": "M1 context fields complete." if m1_complete else "Some M1 context fields missing.",
        "score": 5.0 if m1_complete else 2.5,
    }

    wm = score("workflow_maturity_score")
    signals["govern_1_2"] = {
        "status": "ok" if wm >= 3.5 else "warn" if wm >= 2.5 else "fail",
        "note": f"Workflow Maturity (human-in-loop): {wm:.1f}/5",
        "score": wm,
    }

    dr = score("data_readiness_score")
    signals["map_2_2"] = {
        "status": "ok" if dr >= 3.5 else "warn" if dr >= 2.5 else "fail",
        "note": f"Data Readiness (includes bias audit): {dr:.1f}/5",
        "score": dr,
    }

    op_risk = float(gp.get("operational_risk", 0)) if gp else 0
    ai_suit = score("ai_suitability_score")
    if op_risk:
        fail_ok = op_risk <= 2.5
        signals["map_2_3"] = {
            "status": "ok" if fail_ok else "warn" if op_risk <= 3.5 else "fail",
            "note": f"M3 Operational Risk: {op_risk:.1f}/5 (lower is better)",
            "score": op_risk,
        }
    else:
        signals["map_2_3"] = {
            "status": "ok" if ai_suit >= 3.5 else "warn",
            "note": f"AI Suitability (failure proxy): {ai_suit:.1f}/5",
            "score": ai_suit,
        }

    signals["measure_2_5"] = {
        "status": "ok" if dr >= 4.0 else "warn" if dr >= 2.5 else "fail",
        "note": f"Data Readiness (explainability component): {dr:.1f}/5",
        "score": dr,
    }

    signals["measure_2_7"] = {
        "status": "ok" if dr >= 3.5 else "warn" if dr >= 2.0 else "fail",
        "note": f"Monitoring plan assessed via Data Readiness: {dr:.1f}/5",
        "score": dr,
    }

    rc = score("risk_compliance_score")
    signals["manage_2_4"] = {
        "status": "ok" if rc >= 3.5 else "warn" if rc >= 2.5 else "fail",
        "note": f"Risk & Compliance (incident response readiness): {rc:.1f}/5",
        "score": rc,
    }

    signals["govern_6_1"] = {
        "status": "ok" if rc >= 3.5 else "warn" if rc >= 2.0 else "fail",
        "note": f"Risk & Compliance (ethical risk component): {rc:.1f}/5",
        "score": rc,
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


# ── Tab 4: Graphs — GRAPH CHANGES per merge spec: both now horizontal ───────
def _tab_graphs():
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    records = db_load_all()
    all_gp = db_load_gainpain()

    # ── Graph 1: AI Use Cases by Priority (horizontal) ──────────────────────
    st.markdown("""
    <div style="background:#fff;border:1px solid #EAEBF5;border-radius:14px;
                padding:1.2rem 1.4rem;margin-bottom:1.2rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);">
      <div style="font-weight:700;font-size:1rem;color:#1A1A2E;margin-bottom:0.2rem;">
        AI Use Cases by Priority
      </div>
      <div style="font-size:0.78rem;color:#888;margin-bottom:1rem;">
        Distributed by Gain–Pain priority band (High ≥ 7.0 · Medium 4.0–6.9 · Low &lt; 4.0)
      </div>
    """, unsafe_allow_html=True)

    if not all_gp:
        st.info("No data available. Complete Module 3 (Gain–Pain Analysis) to see priority distribution.")
    else:
        counts = {"High Priority": 0, "Medium Priority": 0, "Low Priority": 0}
        for g in all_gp:
            score = float(g.get("priority_score_scaled") or 0)
            if score >= 7.0:
                counts["High Priority"] += 1
            elif score >= 4.0:
                counts["Medium Priority"] += 1
            else:
                counts["Low Priority"] += 1

        # Y-axis order top-to-bottom: High, Medium, Low
        labels = ["Low Priority", "Medium Priority", "High Priority"]
        values = [counts[l] for l in labels]

        try:
            import plotly.graph_objects as go
            bar_colors = ["#C0392B", "#C07A10", "#1D9E75"]
            fig = go.Figure(go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color=bar_colors,
                text=values,
                textposition="outside",
                textfont=dict(size=14, color="#1A1A2E"),
            ))
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=20, r=40, t=20, b=40),
                xaxis=dict(
                    title="Number of Problem Statements",
                    tickfont=dict(size=12, color="#888"),
                    gridcolor="#F0F0F8",
                    zeroline=False,
                ),
                yaxis=dict(
                    title=None,
                    tickfont=dict(size=13, color="#444"),
                    linecolor="#EAEBF5",
                    showgrid=False,
                ),
                bargap=0.35,
                height=380,
            )
            st.plotly_chart(fig, width='stretch')
        except ImportError:
            df_priority = pd.DataFrame({"Priority": labels, "Number of Use Cases": values})
            st.bar_chart(df_priority.set_index("Priority")["Number of Use Cases"], color="#6C63FF", height=300)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Graph 2: Committee Decision Distribution (horizontal) ──────────────
    st.markdown("""
    <div style="background:#fff;border:1px solid #EAEBF5;border-radius:14px;
                padding:1.2rem 1.4rem;margin-bottom:1.2rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);">
      <div style="font-weight:700;font-size:1rem;color:#1A1A2E;margin-bottom:0.2rem;">
        Committee Decision Summary
      </div>
      <div style="font-size:0.78rem;color:#888;margin-bottom:1rem;">
        Distribution of committee decisions across all submitted use cases
      </div>
    """, unsafe_allow_html=True)

    if not records:
        st.info("No data available. Submit a use case in Module 1 to see decision distribution.")
    else:
        decision_order = ["Approved", "Under Review", "Submitted", "Deferred", "Rejected"]
        decision_colors = {
            "Approved": "#1D9E75", "Under Review": "#C07A10", "Submitted": "#6C63FF",
            "Deferred": "#8B2FC9", "Rejected": "#C0392B",
        }
        counts_dec = {d: 0 for d in decision_order}
        for r in records:
            status = r.get("status", "Submitted")
            if status in counts_dec:
                counts_dec[status] += 1
            else:
                counts_dec["Submitted"] += 1

        filtered_dec = {k: v for k, v in counts_dec.items() if v > 0}

        if not filtered_dec:
            st.info("No decision data available.")
        else:
            labels_dec = list(reversed(list(filtered_dec.keys())))
            values_dec = [filtered_dec[l] for l in labels_dec]

            try:
                import plotly.graph_objects as go
                bar_cols = [decision_colors.get(d, "#6C63FF") for d in labels_dec]
                fig2 = go.Figure(go.Bar(
                    x=values_dec,
                    y=labels_dec,
                    orientation="h",
                    marker_color=bar_cols,
                    text=values_dec,
                    textposition="outside",
                    textfont=dict(size=14, color="#1A1A2E"),
                ))
                fig2.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    margin=dict(l=20, r=40, t=20, b=40),
                    xaxis=dict(
                        title="Number of Use Cases",
                        tickfont=dict(size=12, color="#888"),
                        gridcolor="#F0F0F8",
                        zeroline=False,
                    ),
                    yaxis=dict(
                        title="Committee Status",
                        tickfont=dict(size=13, color="#444"),
                        linecolor="#EAEBF5",
                        showgrid=False,
                    ),
                    bargap=0.35,
                    height=380,
                )
                st.plotly_chart(fig2, width='stretch')
            except ImportError:
                df_dec = pd.DataFrame({"Decision": labels_dec, "Number of Use Cases": values_dec})
                st.bar_chart(df_dec.set_index("Decision")["Number of Use Cases"], color="#6C63FF", height=300)

    st.markdown("</div>", unsafe_allow_html=True)


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
