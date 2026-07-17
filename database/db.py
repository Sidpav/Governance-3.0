# database/db.py
# ─────────────────────────────────────────────────────────────────────────────
# Canonical database layer for the unified AI Governance Platform.
#
# This schema is inherited from "My Project" (the richer ISO 42001 / NIST AI
# RMF data model) because business logic, AI logic, and ISO/NIST mappings are
# preserved from My Project per the merge spec. "Friend's Project" pages
# (Module 1 home page, Module 4 Governance Review) talk to this same database
# through thin adapter repositories — see problem_repository.py,
# feasibility_repository.py, gain_pain_repository.py, governance_repository.py
# — so there is exactly ONE database, no duplicated tables, and Friend's pages
# did not need their visual/flow code changed to read from it.
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "ai_governance.db")


def get_conn():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=30
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")

    return conn


def init_db():
    conn = get_conn()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_human_comments (
            project_id TEXT NOT NULL,
            recommendation_scope TEXT NOT NULL,
            recommendation_key TEXT NOT NULL,
            comment TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (project_id, recommendation_scope, recommendation_key)
        )
    """)

    # ── Module 1 — Problem Statements ───────────────────────────────────────
    # 13 ISO 42001 fields (My Project) + 3 fields captured by Friend's intake
    # form (stakeholders / why_ai / data_sensitivity) so no Module 1 data is
    # lost when Friend's "Problem Definition" UI is used as the front door.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problem_statements (
            id                    TEXT PRIMARY KEY,
            submitted_at          TEXT,
            status                TEXT,
            problem_statement     TEXT,
            business_objective    TEXT,
            solution_approach     TEXT,
            workflow_location     TEXT,
            decision_support      TEXT,
            business_value        TEXT,
            iso_risk_category     TEXT,
            affected_stakeholders TEXT,
            human_override        TEXT,
            data_sources          TEXT,
            success_criteria      TEXT
        )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS project_execution (

        problem_id TEXT PRIMARY KEY,

        hypotheses_json TEXT,

        experiment_json TEXT,
                 
        prototype_spec_json TEXT,
                 
        feedback_questions_json TEXT,
                 
        feedback_summary_json TEXT,
                 
        feedback_json TEXT,
                 
        consolidated_feedback_json TEXT,

        created_at TEXT,

        updated_at TEXT,

        data_requirements_json TEXT,
        data_review_json TEXT,
                 
        model_requirements_json TEXT,

        infrastructure_json TEXT,

        workflow_json TEXT,

        responsible_json TEXT,

        FOREIGN KEY(problem_id)
            REFERENCES problem_statements(id)

    )
    """)


    existing = [r[1] for r in conn.execute("PRAGMA table_info(problem_statements)").fetchall()]
    for col in ["iso_risk_category", "affected_stakeholders", "human_override",
                "data_sources", "success_criteria",
                # Friend's Module 1 fields
                "stakeholders", "why_ai", "data_sensitivity",
                # Referenced by db_insert_record()'s cols list but missing from
                # both CREATE TABLE above and this bulletproofing loop until now —
                # any pre-existing on-disk DB created before this fix would hit
                # "table problem_statements has no column named timeline" the
                # moment save_problem()/save_problem_v2() was first called.
                "timeline", "action_owner"]:
        if col not in existing:
            conn.execute(f"ALTER TABLE problem_statements ADD COLUMN {col} TEXT")

    # ── Module 2 — Feasibility Assessments ──────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feasibility_assessments (
            id                       TEXT PRIMARY KEY,
            problem_id               TEXT,
            timeline                 TEXT,
            owner                    TEXT,
            why_ai                   TEXT,
            data_sensitivity         TEXT,
            assessed_at              TEXT,
            assessor_name            TEXT,
            ai_suitability_score     REAL,
            economic_viability_score REAL,
            data_readiness_score     REAL,
            workflow_maturity_score  REAL,
            change_management_score  REAL,
            risk_compliance_score    REAL,
            hard_gate_triggered      INTEGER DEFAULT 0,
            hard_gate_reason         TEXT,
            overall_score            REAL,
            verdict                  TEXT,
            ai_recommendation        TEXT,
            responses                TEXT,
            FOREIGN KEY (problem_id) REFERENCES problem_statements(id)
        )
    """)

    existing3 = [
        r[1]
        for r in conn.execute(
            "PRAGMA table_info(project_execution)"
        ).fetchall()
    ]

    for col in [
        "prototype_spec_json",
        "feedback_questions_json",
        "feedback_json",
        "feedback_summary_json",
        "consolidated_feedback_json",
        "data_json",
        "infrastructure_json",
        "workflow_json",
        "responsible_json",
        "infrastructure_review_json",
        "infrastructure_output_json",
        "security_questions_json",
    ]:
        if col not in existing3:
            conn.execute(
                f"ALTER TABLE project_execution ADD COLUMN {col} TEXT"
            )
    existing2 = [r[1] for r in conn.execute("PRAGMA table_info(feasibility_assessments)").fetchall()]
    for col, typ in [

        ("timeline", "TEXT"),

        ("owner", "TEXT"),

        ("why_ai", "TEXT"),

        ("data_sensitivity", "TEXT"),

        ("risk_compliance_score", "REAL"),

        ("hard_gate_triggered", "INTEGER"),

        ("hard_gate_reason", "TEXT")

    ]:
        if col not in existing2:
            conn.execute(
                f"ALTER TABLE feasibility_assessments ADD COLUMN {col} {typ}"
            )

    init_m3_table(conn)
    init_committee_table(conn)
    init_team_responses_table(conn)
    init_governance_decisions_table(conn)
    init_expert_review_tables(conn)
    init_audit_log_table(conn)
    init_legacy_archive_tables(conn)
    init_idea_intake_v2_tables(conn)
    init_delivery_governance_tables(conn)

    conn.commit()
    conn.close()


def init_delivery_governance_tables(conn):
    """Persistent controls for assignment, delivery gates, and monitoring."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stakeholder_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT NOT NULL,
            role_key TEXT NOT NULL,
            person_name TEXT NOT NULL,
            person_email TEXT NOT NULL,
            assigned_by TEXT,
            assigned_at TEXT NOT NULL,
            UNIQUE(problem_id, role_key),
            FOREIGN KEY(problem_id) REFERENCES problem_statements(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS delivery_controls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT NOT NULL,
            control_area TEXT NOT NULL,
            control_key TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Not Started',
            owner TEXT,
            evidence TEXT,
            notes TEXT,
            updated_by TEXT,
            updated_at TEXT NOT NULL,
            UNIQUE(problem_id, control_area, control_key),
            FOREIGN KEY(problem_id) REFERENCES problem_statements(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS execution_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            approver TEXT NOT NULL,
            conditions TEXT,
            review_date TEXT,
            decided_at TEXT NOT NULL,
            FOREIGN KEY(problem_id) REFERENCES problem_statements(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lifecycle_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value TEXT,
            status TEXT NOT NULL DEFAULT 'On Track',
            evidence TEXT,
            recorded_by TEXT,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY(problem_id) REFERENCES problem_statements(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS llm_runs (
            id TEXT PRIMARY KEY,
            problem_id TEXT,
            task_type TEXT NOT NULL,
            provider TEXT,
            model TEXT,
            prompt_hash TEXT,
            response_hash TEXT,
            status TEXT NOT NULL,
            error TEXT,
            created_at TEXT NOT NULL
        )
    """)


def init_legacy_archive_tables(conn):
    """
    Friend's original database (database/governance.db) used a different,
    simpler feasibility/gain-pain rubric (e.g. revenue_increase, fairness_risk,
    technology_readiness — fields that don't correspond 1:1 to My Project's
    6-dimension / 8-dimension models). Per "Do NOT lose existing records",
    those rows are preserved here byte-for-byte rather than being force-fit
    into the canonical scoring columns (which would fabricate AI-assessment
    values that were never actually produced by the preserved AI logic).
    Migrated Problem Statements and Governance Decisions from Friend's
    database, by contrast, mapped losslessly onto the canonical schema and
    live in problem_statements / governance_decisions like any other row.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS legacy_friend_feasibility_assessments (
            legacy_id            INTEGER,
            problem_id           TEXT,
            ai_suitability       REAL,
            economic_viability   REAL,
            data_readiness       REAL,
            technology_readiness REAL,
            workflow_maturity    REAL,
            change_management    REAL,
            privacy_risk         REAL,
            fairness_risk        REAL,
            human_oversight      REAL,
            governance_score     REAL,
            overall_score        REAL,
            recommendation       TEXT,
            migrated_at          TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS legacy_friend_gain_pain_analysis (
            legacy_id               INTEGER,
            problem_id              TEXT,
            revenue_increase        REAL,
            cost_reduction          REAL,
            customer_experience     REAL,
            operational_efficiency  REAL,
            risk_reduction          REAL,
            implementation_cost     REAL,
            privacy_security        REAL,
            compliance_risk         REAL,
            change_management       REAL,
            adoption_risk           REAL,
            gain_score              REAL,
            pain_score              REAL,
            priority_score          REAL,
            migrated_at             TEXT
        )
    """)


# ══════════════════════════════════════════════════════════════════════════
# Module 1 — Problem Statements
# ══════════════════════════════════════════════════════════════════════════

def db_insert_record(record: dict):
    conn = get_conn()
    # Allow callers to pass a subset of fields — fill the rest with None.
    cols = ["id", "submitted_at", "status",
            "problem_statement", "business_objective", "solution_approach",
            "timeline", "action_owner", "workflow_location", "decision_support",
            "business_value", "iso_risk_category", "affected_stakeholders",
            "human_override", "data_sources", "success_criteria",
            "stakeholders", "why_ai", "data_sensitivity"]
    full = {c: record.get(c) for c in cols}
    conn.execute(f"""
        INSERT OR REPLACE INTO problem_statements ({', '.join(cols)})
        VALUES ({', '.join(':' + c for c in cols)})
    """, full)
    conn.commit()
    conn.close()


def db_load_all() -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM problem_statements ORDER BY submitted_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_get_problem(problem_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM problem_statements WHERE id=?", (problem_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def db_update_status(record_id: str, new_status: str):
    conn = get_conn()
    conn.execute("UPDATE problem_statements SET status=? WHERE id=?", (new_status, record_id))
    conn.commit()
    conn.close()

def db_update_problem_planning_context(problem_id: str, timeline: str, owner: str):
    conn = get_conn()

    conn.execute("""
        UPDATE problem_statements
        SET
            timeline = ?,
            action_owner = ?
        WHERE id = ?
    """, (timeline, owner, problem_id))

    conn.commit()
    conn.close()


def db_search(query: str) -> list:
    conn = get_conn()
    q = f"%{query.strip()}%"
    rows = conn.execute("""
        SELECT * FROM problem_statements
        WHERE id LIKE ? OR problem_statement LIKE ? OR business_objective LIKE ?
           OR action_owner LIKE ? OR iso_risk_category LIKE ?
        ORDER BY submitted_at DESC
    """, (q, q, q, q, q)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════════════
# Module 2 — Feasibility Assessments
# ══════════════════════════════════════════════════════════════════════════

def db_save_assessment(rec: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO feasibility_assessments
        (
            id,
            problem_id,

            timeline,
            owner,
            why_ai,
            data_sensitivity,

            assessed_at,
            assessor_name,

            ai_suitability_score,
            economic_viability_score,
            data_readiness_score,
            workflow_maturity_score,
            change_management_score,
            risk_compliance_score,

            hard_gate_triggered,
            hard_gate_reason,

            overall_score,
            verdict,

            ai_recommendation,
            responses
        )

        VALUES
        (
            :id,
            :problem_id,

            :timeline,
            :owner,
            :why_ai,
            :data_sensitivity,

            :assessed_at,
            :assessor_name,

            :ai_suitability_score,
            :economic_viability_score,
            :data_readiness_score,
            :workflow_maturity_score,
            :change_management_score,
            :risk_compliance_score,

            :hard_gate_triggered,
            :hard_gate_reason,

            :overall_score,
            :verdict,

            :ai_recommendation,
            :responses
        )
    """, rec)
    conn.commit()
    conn.close()


def db_load_assessments(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM feasibility_assessments WHERE problem_id=? ORDER BY assessed_at DESC",
            (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM feasibility_assessments ORDER BY assessed_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════════════
# Module 3 — Gain-Pain Analyses
# ══════════════════════════════════════════════════════════════════════════

def init_m3_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gainpain_analyses (
            id                     TEXT PRIMARY KEY,
            problem_id             TEXT,
            assessment_id          TEXT,
            analysed_at            TEXT,
            business_value_gain    REAL,
            strategic_alignment    REAL,
            efficiency_gain        REAL,
            innovation_potential   REAL,
            implementation_cost    REAL,
            operational_risk       REAL,
            adoption_resistance    REAL,
            compliance_burden      REAL,
            avg_gains              REAL,
            avg_pains              REAL,
            priority_score         REAL,
            priority_score_scaled  REAL,
            priority_band          TEXT,
            ai_analysis            TEXT,
            question_mode          TEXT,
            expert_reviewed        INTEGER DEFAULT 0,
            FOREIGN KEY (problem_id) REFERENCES problem_statements(id)
        )
    """)
    existing = [r[1] for r in conn.execute("PRAGMA table_info(gainpain_analyses)").fetchall()]
    for col, typ in [("question_mode", "TEXT"), ("expert_reviewed", "INTEGER DEFAULT 0")]:
        if col not in existing:
            conn.execute(f"ALTER TABLE gainpain_analyses ADD COLUMN {col} {typ}")


def db_save_gainpain(rec: dict):
    rec = {**rec}
    rec.setdefault("question_mode", "")
    rec.setdefault("expert_reviewed", 0)
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO gainpain_analyses
        (id, problem_id, assessment_id, analysed_at,
         business_value_gain, strategic_alignment, efficiency_gain, innovation_potential,
         implementation_cost, operational_risk, adoption_resistance, compliance_burden,
         avg_gains, avg_pains, priority_score, priority_score_scaled, priority_band,
         ai_analysis, question_mode, expert_reviewed)
        VALUES
        (:id, :problem_id, :assessment_id, :analysed_at,
         :business_value_gain, :strategic_alignment, :efficiency_gain, :innovation_potential,
         :implementation_cost, :operational_risk, :adoption_resistance, :compliance_burden,
         :avg_gains, :avg_pains, :priority_score, :priority_score_scaled, :priority_band,
         :ai_analysis, :question_mode, :expert_reviewed)
    """, rec)
    conn.commit()
    conn.close()


def db_load_gainpain(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM gainpain_analyses WHERE problem_id=? ORDER BY analysed_at DESC",
            (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM gainpain_analyses ORDER BY analysed_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_get_gainpain(gainpain_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM gainpain_analyses WHERE id=?", (gainpain_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


GAIN_FIELD_IDS = ["business_value_gain", "strategic_alignment", "efficiency_gain", "innovation_potential"]
PAIN_FIELD_IDS = ["implementation_cost", "operational_risk", "adoption_resistance", "compliance_burden"]


def _priority_band(scaled: float) -> str:
    if scaled >= 7.0:
        return "High Priority"
    if scaled >= 4.0:
        return "Medium Priority"
    return "Low Priority"


def db_apply_expert_overrides(gainpain_id: str, updates: dict, expert_name: str, reason: str) -> dict | None:
    """
    Expert Review — apply a dict of {field_id: new_value} overrides to a
    gain-pain analysis row, recompute avg_gains / avg_pains / priority_score /
    priority_score_scaled / priority_band, persist the change, and write one
    audit_log entry per modified field (old value -> expert value, timestamp,
    expert name, reason). Returns the updated row, or None if not found.
    """
    row = db_get_gainpain(gainpain_id)
    if not row:
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed_any = False
    for field, new_val in updates.items():
        if field not in GAIN_FIELD_IDS + PAIN_FIELD_IDS:
            continue
        old_val = row.get(field)
        try:
            changed = float(old_val or 0) != float(new_val)
        except (TypeError, ValueError):
            changed = old_val != new_val
        if changed:
            db_log_audit(
                action_type="expert_gainpain_override",
                problem_id=row["problem_id"],
                field_name=field,
                old_value=old_val,
                new_value=new_val,
                user_name=expert_name,
                reason=reason,
                gainpain_id=gainpain_id,
            )
            row[field] = new_val
            changed_any = True

    gains = [float(row.get(f) or 0) for f in GAIN_FIELD_IDS]
    pains = [float(row.get(f) or 0) for f in PAIN_FIELD_IDS]
    avg_gains = round(sum(gains) / len(gains), 2)
    avg_pains = round(sum(pains) / len(pains), 2)
    priority_score = round(avg_gains * 0.6 - avg_pains * 0.4, 2)
    priority_score_scaled = round(max(0, min(10, ((priority_score + 2) / 5) * 10)), 2)
    old_band = row.get("priority_band")
    new_band = _priority_band(priority_score_scaled)

    if changed_any and old_band != new_band:
        db_log_audit(
            action_type="expert_gainpain_override",
            problem_id=row["problem_id"],
            field_name="priority_band",
            old_value=old_band,
            new_value=new_band,
            user_name=expert_name,
            reason=reason,
            gainpain_id=gainpain_id,
        )

    row["avg_gains"] = avg_gains
    row["avg_pains"] = avg_pains
    row["priority_score"] = priority_score
    row["priority_score_scaled"] = priority_score_scaled
    row["priority_band"] = new_band
    row["expert_reviewed"] = 1

    db_save_gainpain(row)

    # Priority is advisory and cannot change governance approval status.

    return row


# ══════════════════════════════════════════════════════════════════════════
# Module 4 — Committee Decisions (legacy notes table, used inside the
# Governance Dashboard's embedded ISO committee-action widget)
# ══════════════════════════════════════════════════════════════════════════

def init_committee_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS committee_notes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id  TEXT,
            noted_at    TEXT,
            decision    TEXT,
            note        TEXT
        )
    """)


def init_team_responses_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_responses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id  TEXT,
            saved_at    TEXT,
            responses   TEXT
        )
    """)


def db_save_committee_note(problem_id: str, note: str, decision: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO committee_notes (problem_id, noted_at, decision, note) VALUES (?, ?, ?, ?)",
        (problem_id, datetime.now().strftime("%Y-%m-%d %H:%M"), decision, note)
    )
    conn.commit()
    conn.close()


def db_load_committee_notes(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM committee_notes WHERE problem_id=? ORDER BY noted_at DESC", (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM committee_notes ORDER BY noted_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_save_team_responses(problem_id: str, responses: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO team_responses (problem_id, saved_at, responses) VALUES (?, ?, ?)",
        (problem_id, datetime.now().strftime("%Y-%m-%d %H:%M"), responses)
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════
# Module 4 — Governance Decisions (drives Friend's "Governance Review" page)
# ══════════════════════════════════════════════════════════════════════════

def init_governance_decisions_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS governance_decisions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id    TEXT,
            status        TEXT,
            reviewer      TEXT,
            comments      TEXT,
            decision_date TEXT
        )
    """)


def db_save_governance_decision(data: dict):
    """Used by database/governance_repository.py (Friend's Module 4 page)."""
    problem_id = data["problem_id"]

    prev = db_get_problem(problem_id)
    old_status = prev.get("status") if prev else None

    conn = get_conn()
    conn.execute("""
        INSERT INTO governance_decisions (problem_id, status, reviewer, comments, decision_date)
        VALUES (?, ?, ?, ?, ?)
    """, (problem_id, data["status"], data.get("reviewer", ""),
          data.get("comments", ""), data["decision_date"]))
    conn.commit()
    conn.close()

    # Keep the canonical problem status (used by the dashboard's "Committee
    # Decision Summary" graph and by Modules 2/3 status badges) in sync.
    db_update_status(problem_id, data["status"])

    db_log_audit(
        action_type="committee_decision",
        problem_id=problem_id,
        field_name="status",
        old_value=old_status,
        new_value=data["status"],
        user_name=data.get("reviewer", ""),
        reason=data.get("comments", ""),
    )


def db_load_governance_decisions() -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, problem_id, status, reviewer, comments, decision_date "
        "FROM governance_decisions ORDER BY decision_date DESC"
    ).fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def db_governance_status_count(status: str) -> int:
    conn = get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM governance_decisions WHERE status=?", (status,)
    ).fetchone()[0]
    conn.close()
    return count


# ══════════════════════════════════════════════════════════════════════════
# Expert Review workflow (new feature)
# ══════════════════════════════════════════════════════════════════════════

def init_expert_review_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expert_review_requests (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id   TEXT,
            gainpain_id  TEXT,
            query_type   TEXT,
            query_text   TEXT,
            submitted_at TEXT,
            status       TEXT DEFAULT 'Pending'
        )
    """)


def db_save_expert_review_request(rec: dict) -> int:
    conn = get_conn()
    cur = conn.execute("""
        INSERT INTO expert_review_requests
        (problem_id, gainpain_id, query_type, query_text, submitted_at, status)
        VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (rec["problem_id"], rec.get("gainpain_id"), rec["query_type"],
          rec["query_text"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def db_load_expert_review_requests(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM expert_review_requests WHERE problem_id=? ORDER BY submitted_at DESC",
            (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM expert_review_requests ORDER BY submitted_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_mark_expert_review_reviewed(request_id: int):
    conn = get_conn()
    conn.execute("UPDATE expert_review_requests SET status='Reviewed' WHERE id=?", (request_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════
# Audit Trail (generic — committee decisions, expert overrides, priority
# changes; every entry carries old value, new value, timestamp, user, reason)
# ══════════════════════════════════════════════════════════════════════════

def init_audit_log_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type  TEXT,
            problem_id   TEXT,
            gainpain_id  TEXT,
            field_name   TEXT,
            old_value    TEXT,
            new_value    TEXT,
            user_name    TEXT,
            reason       TEXT,
            timestamp    TEXT
        )
    """)


def db_log_audit(action_type: str, problem_id: str, field_name: str, old_value, new_value,
                  user_name: str = "", reason: str = "", gainpain_id: str = None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO audit_log
        (action_type, problem_id, gainpain_id, field_name, old_value, new_value,
         user_name, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (action_type, problem_id, gainpain_id, field_name,
          "" if old_value is None else str(old_value),
          "" if new_value is None else str(new_value),
          user_name, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def db_load_audit(problem_id: str = None) -> list:
    conn = get_conn()
    if problem_id:
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE problem_id=? ORDER BY timestamp DESC", (problem_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════════════
# Deduplication (My Project)
# ══════════════════════════════════════════════════════════════════════════

def db_remove_duplicate_problems():
    """
    Find problem_statements with identical problem_statement text and remove
    duplicates, keeping the one with the most related data (assessments +
    gain-pain analyses), tie-broken by earliest submitted_at.
    Cascades deletion to related tables for removed problem ids.
    Returns list of removed problem ids.
    """
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, problem_statement, submitted_at FROM problem_statements"
    ).fetchall()

    groups = {}
    for r in rows:
        key = (r["problem_statement"] or "").strip().lower()
        groups.setdefault(key, []).append(dict(r))

    removed_ids = []

    for key, recs in groups.items():
        if len(recs) <= 1 or not key:
            continue

        def score(rec):
            pid = rec["id"]
            n_assess = conn.execute(
                "SELECT COUNT(*) FROM feasibility_assessments WHERE problem_id=?", (pid,)
            ).fetchone()[0]
            n_gp = conn.execute(
                "SELECT COUNT(*) FROM gainpain_analyses WHERE problem_id=?", (pid,)
            ).fetchone()[0]
            return (n_assess + n_gp, rec["submitted_at"] or "")

        recs_sorted = sorted(recs, key=lambda r: (-score(r)[0], score(r)[1]))
        keep = recs_sorted[0]
        for rec in recs_sorted[1:]:
            pid = rec["id"]
            for table in ("feasibility_assessments", "gainpain_analyses",
                           "committee_notes", "team_responses",
                           "governance_decisions", "expert_review_requests",
                           "audit_log"):
                try:
                    conn.execute(f"DELETE FROM {table} WHERE problem_id=?", (pid,))
                except Exception:
                    pass
            conn.execute("DELETE FROM problem_statements WHERE id=?", (pid,))
            removed_ids.append(pid)

    conn.commit()
    conn.close()
    return removed_ids


# ══════════════════════════════════════════════════════════════════════════
# Idea Submission v2 — Document-Aware Intake
# (uploaded documents, contradiction flags, solution proposals/validation
# loop). Kept in their own tables so the original problem_statements schema
# is untouched per the merge spec ("Existing database schema unless
# necessary"). Each row links back to a problem_id once the idea is saved;
# while still in-progress (pre-save), problem_id may be a temporary draft id.
# ══════════════════════════════════════════════════════════════════════════

def init_idea_intake_v2_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_documents (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id   TEXT,
            filename     TEXT,
            file_type    TEXT,
            unit_count   INTEGER,
            error        TEXT,
            uploaded_at  TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contradiction_flags (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id           TEXT,
            user_input           TEXT,
            source_file          TEXT,
            source_location      TEXT,
            extracted_statement  TEXT,
            confidence_pct       INTEGER,
            explanation          TEXT,
            resolved             INTEGER DEFAULT 0,
            detected_at          TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS solution_proposals (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id            TEXT,
            round_number          INTEGER,
            solution_name         TEXT,
            solution_type         TEXT,
            solution_description  TEXT,
            expected_benefits     TEXT,
            key_assumptions       TEXT,
            accepted              INTEGER DEFAULT 0,
            clarification_qa      TEXT,
            created_at            TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decision_proposals (
            problem_id          TEXT PRIMARY KEY,
            title                TEXT,
            problem_statement    TEXT,
            business_objective   TEXT,
            business_value       TEXT,
            business_unit        TEXT,
            status               TEXT,
            engines_json         TEXT,
            generated_at         TEXT
        )
    """)


def db_save_uploaded_documents(problem_id: str, documents: list):
    """`documents` is a list of ExtractedDocument objects (document_intel.extractors)."""
    conn = get_conn()
    for doc in documents:
        conn.execute("""
            INSERT INTO uploaded_documents (problem_id, filename, file_type, unit_count, error, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (problem_id, doc.filename, doc.file_type, len(doc.units), doc.error,
              datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def db_load_uploaded_documents(problem_id: str) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM uploaded_documents WHERE problem_id=? ORDER BY id", (problem_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_save_contradiction_flags(problem_id: str, contradictions: list):
    conn = get_conn()
    for c in contradictions:
        conn.execute("""
            INSERT INTO contradiction_flags
            (problem_id, user_input, source_file, source_location, extracted_statement,
             confidence_pct, explanation, resolved, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (problem_id, c.get("user_input", ""), c.get("source_file", ""),
              c.get("source_location", ""), c.get("extracted_statement", ""),
              int(c.get("confidence_pct", 0) or 0), c.get("explanation", ""),
              datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def db_load_contradiction_flags(problem_id: str) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM contradiction_flags WHERE problem_id=? ORDER BY id", (problem_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_resolve_contradiction(flag_id: int):
    conn = get_conn()
    conn.execute("UPDATE contradiction_flags SET resolved=1 WHERE id=?", (flag_id,))
    conn.commit()
    conn.close()


def db_save_solution_proposal(problem_id: str, round_number: int, proposal: dict,
                                accepted: bool = False, clarification_qa: list = None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO solution_proposals
        (problem_id, round_number, solution_name, solution_type, solution_description,
         expected_benefits, key_assumptions, accepted, clarification_qa, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (problem_id, round_number, proposal.get("solution_name", ""),
          proposal.get("solution_type", ""), proposal.get("solution_description", ""),
          json.dumps(proposal.get("expected_benefits", [])),
          json.dumps(proposal.get("key_assumptions", [])),
          1 if accepted else 0,
          json.dumps(clarification_qa or []),
          datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def db_load_solution_proposals(problem_id: str) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM solution_proposals WHERE problem_id=? ORDER BY round_number", (problem_id,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["expected_benefits"] = json.loads(d.get("expected_benefits") or "[]")
        d["key_assumptions"] = json.loads(d.get("key_assumptions") or "[]")
        d["clarification_qa"] = json.loads(d.get("clarification_qa") or "[]")
        result.append(d)
    return result


def db_save_decision_proposal(problem_id: str, data: dict):
    """Persists the final Module 1 "Business Proposal" doc (Figma's
    Decision Support System Architecture) — title, problem statement,
    business objective, business value, business unit, status, and the
    list of approved/ignored decision engines."""
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO decision_proposals
        (problem_id, title, problem_statement, business_objective, business_value,
         business_unit, status, engines_json, generated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (problem_id, data.get("title", ""), data.get("problem_statement", ""),
          data.get("business_objective", ""), data.get("business_value", ""),
          data.get("business_unit", ""), data.get("status", "Approved"),
          json.dumps(data.get("engines", [])),
          datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()


def db_load_decision_proposal(problem_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM decision_proposals WHERE problem_id=?", (problem_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["engines"] = json.loads(d.get("engines_json") or "[]")
    return d
