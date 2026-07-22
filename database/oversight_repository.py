# database/oversight_repository.py
# ─────────────────────────────────────────────────────────────────────────────
# Data layer for Module 3 — "AI Oversight & Evidence" (the `tracking` section).
#
# This module is fully self-contained: it creates and owns its own tables and
# never modifies the shared schema in database/db.py or the AI Product Delivery
# tables (project_execution*). It reuses ONLY get_conn() from database.db so the
# whole platform keeps talking to a single SQLite file.
#
# Tables owned here (all prefixed `oversight_`):
#   oversight_deployments      — one monitored row per approved/deployed use case
#   oversight_kpis             — KPI definitions + latest value per deployment
#   oversight_kpi_readings     — time-series readings behind each KPI (trends)
#   oversight_incidents        — drift / incident / alert log
#   oversight_evidence         — evidence artifacts + compliance attestations
#   oversight_meta             — internal bookkeeping (one-time seed flags)
#
# The registry is populated from the REAL approved projects in
# problem_statements (status='Approved'). A small, clearly-illustrative set of
# sample KPIs / incidents / evidence is seeded once per deployment so the demo
# looks populated; everything is fully editable and persists.
# ─────────────────────────────────────────────────────────────────────────────

import random
import hashlib
from datetime import datetime, timedelta

from database.db import get_conn


# ==========================================================================
# Helpers
# ==========================================================================

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _rng(*parts) -> random.Random:
    """Deterministic RNG seeded from the given parts, so seeded demo numbers
    are stable across reruns (no flicker)."""
    key = "|".join(str(p) for p in parts)
    seed = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2 ** 32)
    return random.Random(seed)


LIFECYCLE_STATUSES = ["Onboarding", "Live", "Paused", "Retired"]
HEALTH_LEVELS = ["Healthy", "Watch", "At Risk"]
INCIDENT_CATEGORIES = [
    "Model Drift", "Data Quality", "Performance", "Bias / Fairness",
    "Security", "Availability", "Human Oversight",
]
INCIDENT_SEVERITIES = ["Low", "Medium", "High", "Critical"]
INCIDENT_STATUSES = ["Open", "Investigating", "Mitigated", "Resolved", "Closed"]
EVIDENCE_TYPES = ["Document", "Link", "Attestation", "Metric Export"]
EVIDENCE_STATUSES = ["Pending", "Submitted", "Approved", "Rejected"]


# ==========================================================================
# Schema
# ==========================================================================

def ensure_oversight_schema():
    """Idempotently create every table this module owns. Safe to call on each
    page load — uses CREATE TABLE IF NOT EXISTS only."""
    conn = get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oversight_deployments (
                problem_id        TEXT PRIMARY KEY,
                deployment_name   TEXT,
                owner             TEXT,
                environment       TEXT,
                model_type        TEXT,
                risk_tier         TEXT,
                lifecycle_status  TEXT,
                health            TEXT,
                deployed_at       TEXT,
                last_reviewed_at  TEXT,
                notes             TEXT,
                created_at        TEXT,
                updated_at        TEXT,
                FOREIGN KEY(problem_id) REFERENCES problem_statements(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS oversight_kpis (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id     TEXT,
                kpi_name       TEXT,
                unit           TEXT,
                direction      TEXT,
                baseline_value REAL,
                target_value   REAL,
                current_value  REAL,
                created_at     TEXT,
                updated_at     TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS oversight_kpi_readings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                kpi_id      INTEGER,
                value       REAL,
                recorded_at TEXT,
                FOREIGN KEY(kpi_id) REFERENCES oversight_kpis(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS oversight_incidents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id  TEXT,
                title       TEXT,
                category    TEXT,
                severity    TEXT,
                status      TEXT,
                owner       TEXT,
                description TEXT,
                mitigation  TEXT,
                detected_at TEXT,
                resolved_at TEXT,
                created_at  TEXT,
                updated_at  TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS oversight_evidence (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id    TEXT,
                control_ref   TEXT,
                title         TEXT,
                description   TEXT,
                evidence_type TEXT,
                evidence_ref  TEXT,
                status        TEXT,
                owner         TEXT,
                attested_by   TEXT,
                attested_at   TEXT,
                due_date      TEXT,
                created_at    TEXT,
                updated_at    TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS oversight_meta (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
    finally:
        conn.close()


def _meta_get(conn, key):
    row = conn.execute(
        "SELECT value FROM oversight_meta WHERE key=?", (key,)
    ).fetchone()
    return row["value"] if row else None


def _meta_set(conn, key, value):
    conn.execute(
        "INSERT INTO oversight_meta(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


# ==========================================================================
# Registry — sourced from real approved projects
# ==========================================================================

def _approved_projects(conn):
    return conn.execute(
        "SELECT id, problem_statement, business_objective, business_value, "
        "action_owner, iso_risk_category, workflow_location, submitted_at "
        "FROM problem_statements p "
        "WHERE p.status = 'Approved' "
        "   OR EXISTS ("
        "       SELECT 1 FROM governance_decisions gd "
        "       WHERE gd.problem_id = p.id AND gd.status = 'Approved' "
        "         AND gd.id = (SELECT MAX(gd2.id) FROM governance_decisions gd2 "
        "                      WHERE gd2.problem_id = p.id)) "
        "ORDER BY submitted_at ASC"
    ).fetchall()


def _derive_name(row) -> str:
    """A short human name for a deployment, derived from the real proposal."""
    text = (row["business_objective"] or row["problem_statement"] or "").strip()
    text = text.replace("\n", " ")
    if not text:
        return "Use case " + str(row["id"])
    words = text.split()
    short = " ".join(words[:8])
    if len(words) > 8:
        short += "…"
    return short[:80]


def _risk_tier(row) -> str:
    raw = (row["iso_risk_category"] or "").lower()
    if "unaccept" in raw or "prohibit" in raw:
        return "Unacceptable"
    if "high" in raw:
        return "High"
    if "limited" in raw:
        return "Limited"
    if "minim" in raw or "low" in raw:
        return "Minimal"
    return "Limited"


def _ensure_deployment(conn, row):
    """Create a registry row for an approved project if it doesn't exist yet."""
    exists = conn.execute(
        "SELECT 1 FROM oversight_deployments WHERE problem_id=?", (row["id"],)
    ).fetchone()
    if exists:
        return

    r = _rng(row["id"], "registry")
    deployed = datetime.now() - timedelta(days=r.randint(20, 160))
    reviewed = datetime.now() - timedelta(days=r.randint(1, 21))

    conn.execute(
        "INSERT INTO oversight_deployments "
        "(problem_id, deployment_name, owner, environment, model_type, "
        " risk_tier, lifecycle_status, health, deployed_at, last_reviewed_at, "
        " notes, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            row["id"],
            _derive_name(row),
            (row["action_owner"] or "Unassigned"),
            "Production",
            "Decision-support model",
            _risk_tier(row),
            "Live",
            "Healthy",
            deployed.strftime("%Y-%m-%d"),
            reviewed.strftime("%Y-%m-%d"),
            "",
            _now(),
            _now(),
        ),
    )


# ==========================================================================
# Seeding (one-time per deployment; fully editable afterwards)
# ==========================================================================

_KPI_TEMPLATES = [
    # name, unit, direction, baseline, target
    ("Model accuracy",            "%",   "higher_better", 76.0, 90.0),
    ("User adoption",             "%",   "higher_better", 24.0, 70.0),
    ("Avg decision latency",      "s",   "lower_better",   6.5,  2.5),
    ("Population stability (PSI)", "idx", "lower_better",  0.03, 0.10),
]

_INCIDENT_TEMPLATES = [
    ("Input feature distribution drift detected", "Model Drift", "Medium",
     "Monitoring flagged a PSI breach on the primary input feature vs. the "
     "training baseline."),
    ("Prediction latency exceeded SLA", "Performance", "Low",
     "P95 inference latency crossed the 3s SLA during peak load."),
    ("Upstream data feed gap", "Data Quality", "High",
     "A source table stopped refreshing, producing stale features for scoring."),
    ("Subgroup performance disparity observed", "Bias / Fairness", "Medium",
     "Accuracy for one segment dropped below the fairness floor agreed at "
     "governance review."),
]

_EVIDENCE_TEMPLATES = [
    ("ISO 42001 §9.1", "Performance monitoring report", "Metric Export",
     "Latest monitoring export showing KPIs vs. thresholds."),
    ("NIST MEASURE 2.7", "Drift-monitoring plan", "Document",
     "Documented drift detection method, thresholds, and alert owners."),
    ("ISO 42001 §8.4", "Human oversight sign-off", "Attestation",
     "Named accountable owner attests human-override controls are operating."),
    ("NIST MANAGE 2.4", "Incident response runbook", "Document",
     "Runbook for triaging and mitigating model incidents."),
    ("ISO 42001 §10.1", "Continual improvement log", "Document",
     "Record of retraining / tuning actions taken since deployment."),
]


def _seed_kpis(conn, problem_id):
    for name, unit, direction, baseline, target in _KPI_TEMPLATES:
        r = _rng(problem_id, name)
        if direction == "higher_better":
            current = round(r.uniform(baseline + (target - baseline) * 0.55,
                                      target + (target - baseline) * 0.12), 2)
        else:
            current = round(r.uniform(target * 0.82, target * 1.35), 2)

        now = _now()
        cur = conn.execute(
            "INSERT INTO oversight_kpis "
            "(problem_id, kpi_name, unit, direction, baseline_value, "
            " target_value, current_value, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (problem_id, name, unit, direction, baseline, target, current,
             now, now),
        )
        kpi_id = cur.lastrowid

        points = 8
        for i in range(points):
            frac = i / (points - 1)
            base = baseline + (current - baseline) * frac
            noise_scale = max(abs(target - baseline) * 0.05, abs(base) * 0.03)
            val = base + r.uniform(-noise_scale, noise_scale)
            val = round(max(val, 0.0), 3)
            recorded = (datetime.now() - timedelta(weeks=(points - 1 - i))
                        ).strftime("%Y-%m-%d")
            conn.execute(
                "INSERT INTO oversight_kpi_readings (kpi_id, value, recorded_at) "
                "VALUES (?, ?, ?)",
                (kpi_id, val, recorded),
            )


def _seed_incidents(conn, problem_id):
    r = _rng(problem_id, "incidents")
    n = r.choices([0, 1, 2], weights=[3, 5, 2])[0]
    if n == 0:
        return
    chosen = r.sample(_INCIDENT_TEMPLATES, k=min(n, len(_INCIDENT_TEMPLATES)))
    for title, category, severity, desc in chosen:
        detected = datetime.now() - timedelta(days=r.randint(2, 45))
        status = r.choice(["Open", "Investigating", "Mitigated", "Resolved"])
        resolved_at = None
        mitigation = ""
        if status in ("Mitigated", "Resolved"):
            mitigation = "Applied mitigation and re-validated against thresholds."
            resolved_at = (detected + timedelta(days=r.randint(1, 6))
                           ).strftime("%Y-%m-%d")
        conn.execute(
            "INSERT INTO oversight_incidents "
            "(problem_id, title, category, severity, status, owner, "
            " description, mitigation, detected_at, resolved_at, "
            " created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (problem_id, title, category, severity, status, "Unassigned",
             desc, mitigation, detected.strftime("%Y-%m-%d"), resolved_at,
             _now(), _now()),
        )


def _seed_evidence(conn, problem_id):
    r = _rng(problem_id, "evidence")
    for control_ref, title, ev_type, desc in _EVIDENCE_TEMPLATES:
        status = r.choices(EVIDENCE_STATUSES, weights=[4, 3, 3, 1])[0]
        attested_by = ""
        attested_at = ""
        if status in ("Submitted", "Approved"):
            attested_by = "Governance Team"
            attested_at = (datetime.now() - timedelta(days=r.randint(1, 30))
                           ).strftime("%Y-%m-%d")
        due = (datetime.now() + timedelta(days=r.randint(-10, 40))
               ).strftime("%Y-%m-%d")
        conn.execute(
            "INSERT INTO oversight_evidence "
            "(problem_id, control_ref, title, description, evidence_type, "
            " evidence_ref, status, owner, attested_by, attested_at, "
            " due_date, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (problem_id, control_ref, title, desc, ev_type, "",
             status, "Unassigned", attested_by, attested_at, due,
             _now(), _now()),
        )


def _derive_health(conn, problem_id) -> str:
    """Coherent initial health from seeded signals: off-track KPIs or an active
    High/Critical incident => At Risk; any at-risk KPI or active incident =>
    Watch; otherwise Healthy."""
    kpis = conn.execute(
        "SELECT direction, target_value, current_value FROM oversight_kpis "
        "WHERE problem_id=?", (problem_id,)
    ).fetchall()
    off = at = 0
    for k in kpis:
        s = kpi_status(dict(k))
        if s == "Off Track":
            off += 1
        elif s == "At Risk":
            at += 1
    active = conn.execute(
        "SELECT severity FROM oversight_incidents WHERE problem_id=? "
        "AND status IN ('Open','Investigating')", (problem_id,)
    ).fetchall()
    severe = any(a["severity"] in ("High", "Critical") for a in active)
    if off or severe:
        return "At Risk"
    if at or active:
        return "Watch"
    return "Healthy"


def bootstrap_oversight():
    """Ensure schema, onboard all approved projects into the registry, and
    seed illustrative KPIs/incidents/evidence once per deployment. Idempotent;
    call at the top of every oversight page."""
    ensure_oversight_schema()
    conn = get_conn()
    try:
        for row in _approved_projects(conn):
            _ensure_deployment(conn, row)
            flag = "seeded:" + str(row["id"])
            if not _meta_get(conn, flag):
                _seed_kpis(conn, row["id"])
                _seed_incidents(conn, row["id"])
                _seed_evidence(conn, row["id"])
                conn.execute(
                    "UPDATE oversight_deployments SET health=? WHERE problem_id=?",
                    (_derive_health(conn, row["id"]), row["id"]),
                )
                _meta_set(conn, flag, "1")
        conn.commit()
    finally:
        conn.close()


# ==========================================================================
# Registry reads / writes
# ==========================================================================

def get_deployments():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM oversight_deployments ORDER BY "
            "CASE lifecycle_status WHEN 'Live' THEN 0 WHEN 'Onboarding' THEN 1 "
            "WHEN 'Paused' THEN 2 ELSE 3 END, deployment_name ASC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_deployment(problem_id):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM oversight_deployments WHERE problem_id=?",
            (problem_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_deployment(problem_id, **fields):
    allowed = {
        "deployment_name", "owner", "environment", "model_type", "risk_tier",
        "lifecycle_status", "health", "deployed_at", "last_reviewed_at", "notes",
    }
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return
    sets["updated_at"] = _now()
    cols = ", ".join(k + "=?" for k in sets)
    vals = list(sets.values()) + [problem_id]
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE oversight_deployments SET " + cols + " WHERE problem_id=?",
            vals,
        )
        conn.commit()
    finally:
        conn.close()


def registry_counts():
    deps = get_deployments()
    return {
        "total": len(deps),
        "live": sum(d["lifecycle_status"] == "Live" for d in deps),
        "onboarding": sum(d["lifecycle_status"] == "Onboarding" for d in deps),
        "paused": sum(d["lifecycle_status"] == "Paused" for d in deps),
        "retired": sum(d["lifecycle_status"] == "Retired" for d in deps),
        "healthy": sum(d["health"] == "Healthy" for d in deps),
        "watch": sum(d["health"] == "Watch" for d in deps),
        "at_risk": sum(d["health"] == "At Risk" for d in deps),
    }


# ==========================================================================
# KPIs
# ==========================================================================

def get_kpis(problem_id=None):
    conn = get_conn()
    try:
        if problem_id:
            rows = conn.execute(
                "SELECT * FROM oversight_kpis WHERE problem_id=? ORDER BY id",
                (problem_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM oversight_kpis ORDER BY problem_id, id"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_kpi_readings(kpi_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT value, recorded_at FROM oversight_kpi_readings "
            "WHERE kpi_id=? ORDER BY recorded_at ASC, id ASC",
            (kpi_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_kpi(problem_id, kpi_name, unit, direction, baseline_value,
            target_value, current_value):
    conn = get_conn()
    try:
        now = _now()
        cur = conn.execute(
            "INSERT INTO oversight_kpis "
            "(problem_id, kpi_name, unit, direction, baseline_value, "
            " target_value, current_value, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (problem_id, kpi_name, unit, direction, baseline_value,
             target_value, current_value, now, now),
        )
        kpi_id = cur.lastrowid
        conn.execute(
            "INSERT INTO oversight_kpi_readings (kpi_id, value, recorded_at) "
            "VALUES (?, ?, ?)",
            (kpi_id, current_value, now[:10]),
        )
        conn.commit()
        return kpi_id
    finally:
        conn.close()


def log_kpi_reading(kpi_id, value, recorded_at=None):
    """Append a reading and update the KPI's current value."""
    conn = get_conn()
    try:
        recorded_at = recorded_at or _now()[:10]
        conn.execute(
            "INSERT INTO oversight_kpi_readings (kpi_id, value, recorded_at) "
            "VALUES (?, ?, ?)",
            (kpi_id, value, recorded_at),
        )
        conn.execute(
            "UPDATE oversight_kpis SET current_value=?, updated_at=? WHERE id=?",
            (value, _now(), kpi_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_kpi(kpi_id, **fields):
    allowed = {"kpi_name", "unit", "direction", "baseline_value",
               "target_value", "current_value"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return
    sets["updated_at"] = _now()
    cols = ", ".join(k + "=?" for k in sets)
    vals = list(sets.values()) + [kpi_id]
    conn = get_conn()
    try:
        conn.execute("UPDATE oversight_kpis SET " + cols + " WHERE id=?", vals)
        conn.commit()
    finally:
        conn.close()


def delete_kpi(kpi_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM oversight_kpi_readings WHERE kpi_id=?", (kpi_id,))
        conn.execute("DELETE FROM oversight_kpis WHERE id=?", (kpi_id,))
        conn.commit()
    finally:
        conn.close()


def kpi_status(kpi) -> str:
    """On Track / At Risk / Off Track from current vs target and direction."""
    cur = kpi.get("current_value")
    tgt = kpi.get("target_value")
    if cur is None or tgt is None:
        return "Unknown"
    if kpi.get("direction") == "lower_better":
        if cur <= tgt:
            return "On Track"
        if cur <= tgt * 1.10:
            return "At Risk"
        return "Off Track"
    if cur >= tgt:
        return "On Track"
    if cur >= tgt * 0.90:
        return "At Risk"
    return "Off Track"


# ==========================================================================
# Incidents
# ==========================================================================

def get_incidents(problem_id=None, status=None, severity=None):
    clauses, params = [], []
    if problem_id:
        clauses.append("problem_id=?")
        params.append(problem_id)
    if status and status != "All":
        clauses.append("status=?")
        params.append(status)
    if severity and severity != "All":
        clauses.append("severity=?")
        params.append(severity)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM oversight_incidents " + where + " ORDER BY "
            "CASE severity WHEN 'Critical' THEN 0 WHEN 'High' THEN 1 "
            "WHEN 'Medium' THEN 2 ELSE 3 END, detected_at DESC",
            params
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_incident(problem_id, title, category, severity, status, owner,
                 description, mitigation="", detected_at=None):
    conn = get_conn()
    try:
        now = _now()
        conn.execute(
            "INSERT INTO oversight_incidents "
            "(problem_id, title, category, severity, status, owner, "
            " description, mitigation, detected_at, resolved_at, "
            " created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (problem_id, title, category, severity, status, owner,
             description, mitigation, (detected_at or now[:10]), None,
             now, now),
        )
        conn.commit()
    finally:
        conn.close()


def update_incident(incident_id, **fields):
    allowed = {"title", "category", "severity", "status", "owner",
               "description", "mitigation", "detected_at", "resolved_at"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return
    if sets.get("status") in ("Resolved", "Closed") and "resolved_at" not in sets:
        sets["resolved_at"] = _now()[:10]
    if sets.get("status") in ("Open", "Investigating"):
        sets["resolved_at"] = None
    sets["updated_at"] = _now()
    cols = ", ".join(k + "=?" for k in sets)
    vals = list(sets.values()) + [incident_id]
    conn = get_conn()
    try:
        conn.execute("UPDATE oversight_incidents SET " + cols + " WHERE id=?", vals)
        conn.commit()
    finally:
        conn.close()


def delete_incident(incident_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM oversight_incidents WHERE id=?", (incident_id,))
        conn.commit()
    finally:
        conn.close()


def incident_counts():
    inc = get_incidents()
    active = [i for i in inc if i["status"] in ("Open", "Investigating")]
    return {
        "total": len(inc),
        "active": len(active),
        "open": sum(i["status"] == "Open" for i in inc),
        "investigating": sum(i["status"] == "Investigating" for i in inc),
        "mitigated": sum(i["status"] == "Mitigated" for i in inc),
        "resolved": sum(i["status"] in ("Resolved", "Closed") for i in inc),
        "critical": sum(i["severity"] == "Critical" for i in active),
        "high": sum(i["severity"] == "High" for i in active),
    }


# ==========================================================================
# Evidence / attestations
# ==========================================================================

def get_evidence(problem_id=None, status=None):
    clauses, params = [], []
    if problem_id:
        clauses.append("problem_id=?")
        params.append(problem_id)
    if status and status != "All":
        clauses.append("status=?")
        params.append(status)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM oversight_evidence " + where +
            " ORDER BY control_ref ASC, id ASC",
            params
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_evidence(problem_id, control_ref, title, description, evidence_type,
                 evidence_ref, status, owner, due_date=None):
    conn = get_conn()
    try:
        now = _now()
        conn.execute(
            "INSERT INTO oversight_evidence "
            "(problem_id, control_ref, title, description, evidence_type, "
            " evidence_ref, status, owner, attested_by, attested_at, "
            " due_date, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (problem_id, control_ref, title, description, evidence_type,
             evidence_ref, status, owner, "", "", (due_date or ""),
             now, now),
        )
        conn.commit()
    finally:
        conn.close()


def update_evidence(evidence_id, **fields):
    allowed = {"control_ref", "title", "description", "evidence_type",
               "evidence_ref", "status", "owner", "attested_by",
               "attested_at", "due_date"}
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return
    if sets.get("status") in ("Submitted", "Approved"):
        sets.setdefault("attested_at", _now()[:10])
    sets["updated_at"] = _now()
    cols = ", ".join(k + "=?" for k in sets)
    vals = list(sets.values()) + [evidence_id]
    conn = get_conn()
    try:
        conn.execute("UPDATE oversight_evidence SET " + cols + " WHERE id=?", vals)
        conn.commit()
    finally:
        conn.close()


def delete_evidence(evidence_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM oversight_evidence WHERE id=?", (evidence_id,))
        conn.commit()
    finally:
        conn.close()


def evidence_counts(problem_id=None):
    ev = get_evidence(problem_id=problem_id)
    total = len(ev)
    approved = sum(e["status"] == "Approved" for e in ev)
    return {
        "total": total,
        "approved": approved,
        "submitted": sum(e["status"] == "Submitted" for e in ev),
        "pending": sum(e["status"] == "Pending" for e in ev),
        "rejected": sum(e["status"] == "Rejected" for e in ev),
        "pct_complete": round(100 * approved / total) if total else 0,
    }
