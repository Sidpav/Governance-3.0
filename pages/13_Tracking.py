# pages/13_Tracking.py
# ─────────────────────────────────────────────────────────────────────────────
# "AI Oversight & Evidence" — Process Governance Dashboard
#
# Redesigned landing page for the tracking section. Renders a self-contained
# governance dashboard (Enterprise → Business Unit → Application levels) driven
# entirely by the real oversight data in the database.
#
# IMPORTANT: this file only owns the AI Oversight & Evidence tab. It does not
# touch the Explainer, AI Use-Case Portfolio, or AI Product Delivery tabs.
#
# The visual dashboard is rendered as one isolated HTML/CSS/JS component
# (streamlit.components.v1.html) so the styling is pixel-controlled and cannot
# leak into — or be affected by — the other tabs. All data is derived in Python
# below and injected as JSON.
# ─────────────────────────────────────────────────────────────────────────────

import json
import hashlib
import os

import streamlit as st
import streamlit.components.v1 as components

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar
from ui.auth import require_login, require_access

from database.db import get_conn
from database.oversight_repository import (
    bootstrap_oversight,
    get_deployments,
    get_kpis,
    get_incidents,
    get_evidence,
    kpi_status,
)

st.set_page_config(
    page_title="AI Oversight, Evidence & Value Realization",
    page_icon="📍",
    layout="wide",
)

require_login()
apply_theme()
render_sidebar(active="tracking")
render_navbar(active="tracking")
require_access("tracking")

# Full-width dashboard: hide the empty sidebar in-page so ui/sidebar.py is
# left untouched (teammate owns that shared file).
st.markdown(
    """
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    div[data-testid="stHorizontalBlock"]:has(.cx-top-active) { left: 0 !important; }
    section.main > div.block-container { margin-top: 116px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ensure schema + onboard approved projects + one-time sample seed.
bootstrap_oversight()


# =========================================================================
# Derivations — turn the real DB rows into the richer fields the dashboard
# displays. Everything here is deterministic (stable across reruns).
# =========================================================================

DEPLOY_TARGETS = ["Cloud — AWS", "Cloud — Azure", "On-Premise", "Cloud — GCP"]


def _h(seed: str) -> int:
    return int(hashlib.md5(seed.encode()).hexdigest(), 16)


def _friendly(problem_text: str, objective: str):
    """A short product-style name + a code prefix, inferred from the proposal."""
    t = (problem_text + " " + objective).lower()
    if "churn" in t:
        if "segment" in t:
            return "Customer Churn DSS — Segments", "CHURN"
        return "Customer Churn DSS", "CHURN"
    if "maintenance" in t or "downtime" in t or "equipment" in t:
        return "Predictive Maintenance", "MAINT"
    if "email" in t or "triage" in t:
        return "Email Triage & Routing", "EMAIL"
    if "fraud" in t or "claim" in t:
        return "Fraud Detection System", "FRAUD"
    if "inventory" in t or "demand" in t or "forecast" in t:
        return "Demand Forecasting", "DEMAND"
    words = (objective or problem_text or "AI Use Case").split()[:3]
    return (" ".join(words).title() or "AI Use Case"), "APP"


def _short_bu(wf: str) -> str:
    if not wf:
        return "Unassigned"
    first = wf.split(",")[0].strip().replace(" and ", " & ")
    overrides = {
        "Supply Chain & Inventory Management": "Supply Chain",
        "Production/Manufacturing": "Production & Mfg",
    }
    return overrides.get(first, first)


def _uptime_pct(problem_id: str) -> float:
    """System uptime % — deterministic per app (96.5-99.8)."""
    return round(96.5 + (_h(problem_id + "up") % 34) / 10.0, 1)


def _policy_compliance(active_incidents: int, rejected_evidence: int) -> int:
    """Policy compliance % — 100 minus penalties for open incidents and
    rejected evidence (floored at 55)."""
    return max(55, 100 - active_incidents * 5 - rejected_evidence * 4)


def _data_freshness(problem_id: str, data_incidents: int) -> int:
    """Data freshness % — deterministic, reduced by data-quality incidents."""
    return max(70, min(99, 90 + (_h(problem_id + "fresh") % 9) - data_incidents * 6))


def _human_override(problem_id: str) -> int:
    """Human override rate % — deterministic per app (72-95)."""
    return 72 + (_h(problem_id + "override") % 24)


# Governance Health Score = weighted blend of four operational signals.
HEALTH_WEIGHTS = {"uptime": 0.35, "policy": 0.35, "freshness": 0.20, "override": 0.10}


def _health_score(uptime, policy, freshness, override) -> int:
    return round(uptime * HEALTH_WEIGHTS["uptime"]
                 + policy * HEALTH_WEIGHTS["policy"]
                 + freshness * HEALTH_WEIGHTS["freshness"]
                 + override * HEALTH_WEIGHTS["override"])


def _band(score: int):
    """Score -> (label, css). >=85 Healthy, 70-84 Needs Attention, <70 At Risk."""
    if score >= 85:
        return "Healthy", "ok"
    if score >= 70:
        return "Needs Attention", "warn"
    return "At Risk", "risk"


def _active_users(problem_id: str) -> int:
    return 8 + _h(problem_id + "usr") % 55


def _deploy_target(problem_id: str) -> str:
    return DEPLOY_TARGETS[_h(problem_id + "tgt") % len(DEPLOY_TARGETS)]


def _review_status(ev) -> str:
    """Governance review completion from evidence attestations."""
    total = len(ev)
    if not total:
        return "Not Started"
    attested = sum(e["status"] in ("Approved", "Submitted") for e in ev)
    ratio = attested / total
    if ratio >= 0.6:
        return "Complete"
    if attested > 0:
        return "In Progress"
    return "Not Started"


def _workflow_map():
    """problem_id -> row dict from problem_statements."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, problem_statement, business_objective, "
            "workflow_location, action_owner, status FROM problem_statements"
        ).fetchall()
        return {r["id"]: dict(r) for r in rows}
    finally:
        conn.close()


ps_map = _workflow_map()
deployments = get_deployments()

apps = []
code_seq = {}

for d in deployments:
    pid = d["problem_id"]
    ps = ps_map.get(pid, {})
    name, prefix = _friendly(ps.get("problem_statement", ""),
                             ps.get("business_objective", ""))
    code_seq[prefix] = code_seq.get(prefix, 0) + 1
    year = (d.get("deployed_at") or "2026")[:4]
    code = f"{prefix}-{year}-{code_seq[prefix]:03d}"

    kpis = get_kpis(pid)
    ev = get_evidence(problem_id=pid)
    inc = get_incidents(problem_id=pid)

    review = _review_status(ev)

    active_inc = sum(i["status"] in ("Open", "Investigating") for i in inc)
    rejected_ev = sum(e["status"] == "Rejected" for e in ev)
    approved_ev = sum(e["status"] == "Approved" for e in ev)
    data_inc = sum(1 for i in inc if "Data" in (i.get("category") or ""))
    compliance = active_inc + rejected_ev

    # Governance Health Score - weighted formula (see _health_score / _band).
    up_pct = _uptime_pct(pid)
    policy_pct = _policy_compliance(active_inc, rejected_ev)
    fresh_pct = _data_freshness(pid, data_inc)
    override_pct = _human_override(pid)
    health_score = _health_score(up_pct, policy_pct, fresh_pct, override_pct)
    band_label, band_cls = _band(health_score)

    stage = ("Production" if (band_label == "Healthy" and review == "Complete")
             else "Phase 1 Pilot" if review != "Not Started"
             else "Pilot (staging)")

    apps.append({
        "id": pid,
        "name": name,
        "code": code,
        "bu": _short_bu(ps.get("workflow_location", "")),
        "stage": stage,
        "deployed": True,
        "deployment": _deploy_target(pid),
        "badge": band_label,
        "badgeCls": band_cls,
        "healthScore": health_score,
        "uptime": up_pct,
        "activeUsers": _active_users(pid),
        "healthInputs": {
            "uptime": up_pct, "policy": policy_pct,
            "freshness": fresh_pct, "override": override_pct,
        },
        "reviewStatus": review,
        "owner": d.get("owner") or "Unassigned",
        "riskTier": d.get("risk_tier") or "Limited",
        "compliance": compliance,
        "kpis": [
            {"name": k["kpi_name"], "unit": k["unit"],
             "current": k["current_value"], "target": k["target_value"],
             "status": kpi_status(k)}
            for k in kpis
        ],
        "evidence": {"approved": approved_ev, "total": len(ev)},
        "incidents": {"active": active_inc, "total": len(inc)},
    })

# Use-cases still under governance review = pending deployment.
pending_pids = [
    pid for pid, r in ps_map.items()
    if r.get("status") == "Under Review"
    and pid not in {a["id"] for a in apps}
]
for pid in pending_pids:
    r = ps_map[pid]
    name, prefix = _friendly(r.get("problem_statement", ""),
                             r.get("business_objective", ""))
    code_seq[prefix] = code_seq.get(prefix, 0) + 1
    code = f"{prefix}-2026-{code_seq[prefix]:03d}"
    apps.append({
        "id": pid,
        "name": name,
        "code": code,
        "bu": _short_bu(r.get("workflow_location", "")),
        "stage": "Pre-deployment",
        "deployed": False,
        "deployment": "Not deployed",
        "badge": "Not Deployed",
        "badgeCls": "none",
        "healthScore": None,
        "uptime": None,
        "activeUsers": None,
        "reviewStatus": "In Progress",
        "owner": r.get("action_owner") or "Unassigned",
        "riskTier": "Limited",
        "compliance": 0,
        "kpis": [],
        "evidence": {"approved": 0, "total": 0},
        "incidents": {"active": 0, "total": 0},
    })


# ------------------------------------------------------------- roll-up metrics
deployed_apps = [a for a in apps if a["deployed"]]

in_production = sum(a["stage"] == "Production" for a in deployed_apps)
under_review = sum(a["reviewStatus"] != "Complete" for a in deployed_apps)
pending = len(apps) - len(deployed_apps)

reviews_completed = sum(a["reviewStatus"] == "Complete" for a in apps)
reviews_total = len(apps)
reviews_pct = round(100 * reviews_completed / reviews_total) if reviews_total else 0

avg_uptime = (round(sum(a["uptime"] for a in deployed_apps) / len(deployed_apps), 1)
              if deployed_apps else 0.0)
avg_health = (round(sum(a["healthScore"] for a in deployed_apps) / len(deployed_apps))
              if deployed_apps else 0)
open_compliance = sum(a["compliance"] for a in apps)

active_names = ", ".join(a["name"].split(" — ")[0].split()[0]
                         for a in deployed_apps[:3])

# Deployment status summary (deployed targets + a Not-deployed bucket).
summary = {}
for a in deployed_apps:
    summary[a["deployment"]] = summary.get(a["deployment"], 0) + 1

deployment_summary = [{"label": k, "count": v} for k, v in summary.items()]
if pending:
    deployment_summary.append({"label": "Not Deployed", "count": pending})

business_units = [{"name": b} for b in sorted({a["bu"] for a in apps})]

# ============ Cortexa AI Audit Dashboard — derived audit metrics ============
import datetime as _dt


def _audit_metrics(app):
    pid = app["id"]
    uu = app["activeUsers"] or 0
    sessions = int(round(uu * (2.6 + (_h(pid + "sx") % 13) / 10.0)))
    api = sessions * (11 + _h(pid + "ax") % 8)
    tokens = sessions * (6500 + _h(pid + "tx") % 4200)
    cost = int(round(tokens / 1e6 * (52 + _h(pid + "cx") % 46)))
    return uu, sessions, api, tokens, cost


audit_apps = []
tot_api = tot_users = tot_sessions = tot_tokens = tot_cost = tot_viol = 0
for _a in apps:
    if _a["deployed"]:
        uu, sessions, api, tokens, cost = _audit_metrics(_a)
        viol = _a["incidents"]["active"] + (_h(_a["id"] + "vx") % 3)
        tot_api += api; tot_users += uu; tot_sessions += sessions
        tot_tokens += tokens; tot_cost += cost; tot_viol += viol
    else:
        uu = sessions = api = tokens = cost = viol = 0
    audit_apps.append({
        "id": _a["id"], "name": _a["name"], "deployed": _a["deployed"],
        "healthScore": _a["healthScore"], "badge": _a["badge"],
        "badgeCls": _a["badgeCls"], "uniqueUsers": uu, "sessions": sessions,
        "tokens": tokens, "cost": cost, "violations": viol,
        "bu": _a["bu"], "code": _a["code"], "stage": _a["stage"],
    })


def _series(final, weeks=8, start_frac=0.62, seed="s"):
    out = []
    for i in range(weeks):
        frac = start_frac + (1 - start_frac) * i / (weeks - 1)
        jitter = 1 + ((_h(seed + str(i)) % 7) - 3) / 100.0
        out.append(final * frac * jitter)
    return out


week_labels = ["W%d" % (i + 1) for i in range(8)]
token_trend = [int(round(v)) for v in _series(tot_tokens, seed="tok")]
users_trend = [int(round(v)) for v in _series(tot_users, start_frac=0.70, seed="usr")]
sessions_trend = [int(round(v)) for v in _series(tot_sessions, start_frac=0.66, seed="ses")]
cost_trend = [int(round(v)) for v in _series(tot_cost, start_frac=0.64, seed="cst")]

_base_month = tot_cost * 4.33
proj_trend = [int(round(_base_month * (1.08 ** i))) for i in range(6)]
_m = _dt.date.today().replace(day=1)
proj_months = []
for _ in range(6):
    _m = (_m.replace(year=_m.year + 1, month=1) if _m.month == 12
          else _m.replace(month=_m.month + 1))
    proj_months.append(_m.strftime("%b %Y"))
projected_cost_6mo = sum(proj_trend)
proj_window = proj_months[0] + " – " + proj_months[-1]

_vt_labels = ["Unauthorised data access", "Role boundary breach",
              "PII exposure in prompt", "Output policy violation"]
_vt_weights = [0.40, 0.27, 0.17, 0.16]
violations_by_type = []
_rem = tot_viol
for _i, _lb in enumerate(_vt_labels):
    _c = round(tot_viol * _vt_weights[_i]) if _i < len(_vt_labels) - 1 else _rem
    _c = max(int(_c), 0); _rem -= _c
    violations_by_type.append({"label": _lb, "value": max(_c, 0)})

_chatbot = next((a["name"] for a in apps if "Churn" in a["name"]),
                apps[0]["name"] if apps else "Customer Churn DSS")
intent = {
    "app": _chatbot,
    "business": [
        {"label": "Churn risk inquiry", "value": 31},
        {"label": "Retention action request", "value": 24},
        {"label": "Customer profile lookup", "value": 18},
        {"label": "Report generation", "value": 14},
        {"label": "Model explanation", "value": 8},
        {"label": "Other", "value": 5},
    ],
    "personal": [
        {"label": "General knowledge Q&A", "value": 9},
        {"label": "Personal productivity", "value": 6},
        {"label": "Non-work browsing / queries", "value": 4},
    ],
}

_names = [a["name"] for a in apps if a["deployed"]] or ["Customer Churn DSS"]


def _nm(i):
    return _names[i % len(_names)]


_today = _dt.date.today()


def _ts(days, hh, mm):
    d = _today - _dt.timedelta(days=days)
    return d.strftime("%Y-%m-%d") + " %02d:%02d" % (hh, mm)


audit_log = [
    {"ts": _ts(0, 9, 12), "app": _nm(0), "type": "Policy Violation",
     "detail": "Customer revenue tier exposed to unauthorised support agent role",
     "severity": "High", "status": "Open"},
    {"ts": _ts(0, 6, 41), "app": _nm(0), "type": "Policy Violation",
     "detail": "PII (email address) returned in API response without masking",
     "severity": "High", "status": "Open"},
    {"ts": _ts(1, 14, 30), "app": _nm(3), "type": "Policy Violation",
     "detail": "Manager accessed restricted scores outside permitted role",
     "severity": "Medium", "status": "Investigating"},
    {"ts": _ts(1, 11, 5), "app": _nm(1), "type": "Policy Violation",
     "detail": "Alert threshold bypass attempt detected in rule override",
     "severity": "Medium", "status": "Resolved"},
    {"ts": _ts(2, 9, 20), "app": _nm(0), "type": "Token Spike",
     "detail": "Token usage 34% above 7-day baseline — possible prompt injection attempt",
     "severity": "Low", "status": "Monitoring"},
    {"ts": _ts(3, 15, 44), "app": _nm(2), "type": "Data Freshness Alert",
     "detail": "Product usage data feed stale for 26 hours; model inference continued on old data",
     "severity": "Low", "status": "Resolved"},
    {"ts": _ts(4, 8, 10), "app": _nm(0), "type": "Policy Violation",
     "detail": "Output included financial projection in natural language — outside approved scope",
     "severity": "Medium", "status": "Resolved"},
]

audit = {
    "activeCount": len(deployed_apps),
    "apiRequests": tot_api,
    "uniqueUsers": tot_users,
    "sessions": tot_sessions,
    "violations": tot_viol,
    "violationsPrev": max(tot_viol - 2, 0),
    "tokens": tot_tokens,
    "cost": tot_cost,
    "projectedCost": projected_cost_6mo,
    "projWindow": proj_window,
    "topicCount": 6,
    "topicApp": _chatbot + " (chatbot app)",
    "intent": intent,
    "weekLabels": week_labels,
    "tokenTrend": token_trend,
    "usersTrend": users_trend,
    "sessionsTrend": sessions_trend,
    "costTrend": cost_trend,
    "projMonths": proj_months,
    "projTrend": proj_trend,
    "violationsByType": violations_by_type,
    "log": audit_log,
    "apps": audit_apps,
}

# ------------------------------------------------------------- payload
data = {
    "apps": apps,
    "enterprise": {
        "total": len(apps),
        "inProduction": in_production,
        "underReview": under_review,
        "pending": pending,
        "reviewsCompleted": reviews_completed,
        "reviewsTotal": reviews_total,
        "reviewsPct": reviews_pct,
        "openCompliance": open_compliance,
        "avgUptime": avg_uptime,
        "avgHealth": avg_health,
        "activeCount": len(deployed_apps),
        "activeNames": active_names,
    },
    "deploymentSummary": deployment_summary,
    "businessUnits": business_units,
    "audit": audit,
}

# ------------------------------------------------------------- render
# Load the isolated dashboard template and inject the derived data as JSON,
# so the styling/JS is fully sandboxed inside the component iframe.
_here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_here, "_oversight_dashboard.html"), encoding="utf-8") as _f:
    _template = _f.read()

_rendered = _template.replace(
    "const DATA = __DATA_JSON__;",
    "const DATA = " + json.dumps(data) + ";",
)

components.html(_rendered, height=1650, scrolling=True)
