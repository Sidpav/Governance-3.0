from datetime import datetime, timezone

from database.db import get_conn, db_log_audit


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_assignment(problem_id, role_key, person_name, person_email, assigned_by):
    conn = get_conn()
    conn.execute("""
        INSERT INTO stakeholder_assignments
        (problem_id, role_key, person_name, person_email, assigned_by, assigned_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(problem_id, role_key) DO UPDATE SET
          person_name=excluded.person_name, person_email=excluded.person_email,
          assigned_by=excluded.assigned_by, assigned_at=excluded.assigned_at
    """, (problem_id, role_key, person_name, person_email.lower(), assigned_by, _now()))
    conn.commit()
    conn.close()


def load_assignments(problem_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM stakeholder_assignments WHERE problem_id=? ORDER BY role_key", (problem_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_control(problem_id, area, key, status, owner, evidence, notes, user):
    conn = get_conn()
    old = conn.execute("""SELECT status FROM delivery_controls
        WHERE problem_id=? AND control_area=? AND control_key=?""", (problem_id, area, key)).fetchone()
    conn.execute("""
        INSERT INTO delivery_controls
        (problem_id, control_area, control_key, status, owner, evidence, notes, updated_by, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(problem_id, control_area, control_key) DO UPDATE SET
          status=excluded.status, owner=excluded.owner, evidence=excluded.evidence,
          notes=excluded.notes, updated_by=excluded.updated_by, updated_at=excluded.updated_at
    """, (problem_id, area, key, status, owner, evidence, notes, user, _now()))
    conn.commit()
    conn.close()
    db_log_audit("delivery_control_update", problem_id, f"{area}.{key}",
                 old["status"] if old else None, status, user, notes)


def load_controls(problem_id, area=None):
    conn = get_conn()
    if area:
        rows = conn.execute("SELECT * FROM delivery_controls WHERE problem_id=? AND control_area=? ORDER BY control_key",
                            (problem_id, area)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM delivery_controls WHERE problem_id=? ORDER BY control_area, control_key",
                            (problem_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_execution_decision(problem_id, decision, approver, conditions, review_date):
    conn = get_conn()
    conn.execute("""INSERT INTO execution_approvals
        (problem_id, decision, approver, conditions, review_date, decided_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (problem_id, decision, approver, conditions, review_date, _now()))
    conn.commit()
    conn.close()
    db_log_audit("execution_gate_decision", problem_id, "execution_decision", None,
                 decision, approver, conditions)


def load_execution_decisions(problem_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM execution_approvals WHERE problem_id=? ORDER BY id DESC",
                        (problem_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_lifecycle_evidence(problem_id, metric, value, status, evidence, user):
    conn = get_conn()
    conn.execute("""INSERT INTO lifecycle_evidence
        (problem_id, metric_name, metric_value, status, evidence, recorded_by, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (problem_id, metric, value, status, evidence, user, _now()))
    conn.commit()
    conn.close()


def load_lifecycle_evidence(problem_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM lifecycle_evidence WHERE problem_id=? ORDER BY id DESC",
                        (problem_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execution_readiness(problem_id):
    controls = load_controls(problem_id)
    required_areas = {"workflow", "responsibility", "data", "infrastructure"}
    completed = {r["control_area"] for r in controls if r["status"] in {"Complete", "Approved"}}
    conn = get_conn()
    row = conn.execute("""SELECT data_review_json, infrastructure_output_json
        FROM project_execution WHERE problem_id=?""", (problem_id,)).fetchone()
    conn.close()
    if row and row["data_review_json"]: completed.add("data")
    if row and row["infrastructure_output_json"]: completed.add("infrastructure")
    return required_areas.issubset(completed), sorted(required_areas - completed)
