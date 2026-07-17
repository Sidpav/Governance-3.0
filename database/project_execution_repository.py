import json
from datetime import datetime

from database.db import get_conn


# ==========================================================
# APPROVED PROJECTS
# ==========================================================

def get_approved_projects():
    conn = get_conn()

    rows = conn.execute("""
        SELECT
            id,
            problem_statement,
            business_objective,
            solution_approach,
            timeline,
            action_owner,
            business_value,
            workflow_location,
            decision_support,
            status
        FROM problem_statements p
        WHERE EXISTS (
            SELECT 1 FROM governance_decisions gd
            WHERE gd.problem_id = p.id AND gd.status = 'Approved'
              AND gd.id = (SELECT MAX(gd2.id) FROM governance_decisions gd2 WHERE gd2.problem_id = p.id)
        )
        ORDER BY submitted_at DESC
    """).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def get_project(problem_id):

    conn = get_conn()

    row = conn.execute("""
        SELECT *
        FROM problem_statements
        WHERE id=?
    """, (problem_id,)).fetchone()

    conn.close()

    return dict(row) if row else None


# ==========================================================
# HYPOTHESES
# ==========================================================

def load_hypotheses(problem_id):

    conn = get_conn()

    row = conn.execute("""
        SELECT hypotheses_json
        FROM project_execution
        WHERE problem_id=?
    """, (problem_id,)).fetchone()

    conn.close()

    if not row:
        return []

    if not row["hypotheses_json"]:
        return []

    return json.loads(row["hypotheses_json"])


def save_hypotheses(problem_id, hypotheses):

    conn = get_conn()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""
        INSERT INTO project_execution
        (
            problem_id,
            hypotheses_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?, ?, ?, ?
        )

        ON CONFLICT(problem_id)
        DO UPDATE SET

            hypotheses_json=excluded.hypotheses_json,

            updated_at=excluded.updated_at
    """,
    (
        problem_id,
        json.dumps(hypotheses),
        now,
        now
    ))

    conn.commit()
    conn.close()

# ==========================================================
# EXPERIMENT DESIGN
# ==========================================================

def load_experiments(problem_id):

    conn = get_conn()

    row = conn.execute("""
        SELECT experiment_json
        FROM project_execution
        WHERE problem_id=?
    """, (problem_id,)).fetchone()

    conn.close()

    if not row:
        return []

    if not row["experiment_json"]:
        return []

    return json.loads(row["experiment_json"])


def save_experiments(problem_id, experiments):

    conn = get_conn()

    try:

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            INSERT INTO project_execution
            (
                problem_id,
                experiment_json,
                created_at,
                updated_at
            )

            VALUES
            (
                ?, ?, ?, ?
            )

            ON CONFLICT(problem_id)

            DO UPDATE SET

                experiment_json=excluded.experiment_json,

                updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(experiments),
            now,
            now,
        ))

        conn.commit()

    finally:
        conn.close()

# ==========================================================
# PROTOTYPE SPEC
# ==========================================================

def load_prototype_spec(problem_id):

    conn = get_conn()

    row = conn.execute("""
        SELECT prototype_spec_json
        FROM project_execution
        WHERE problem_id=?
    """,(problem_id,)).fetchone()

    conn.close()

    if not row:
        return None

    if not row["prototype_spec_json"]:
        return None

    return json.loads(row["prototype_spec_json"])


def save_prototype_spec(problem_id,spec):

    conn=get_conn()

    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""

        INSERT INTO project_execution(

            problem_id,

            prototype_spec_json,

            created_at,

            updated_at

        )

        VALUES(?,?,?,?)

        ON CONFLICT(problem_id)

        DO UPDATE SET

        prototype_spec_json=excluded.prototype_spec_json,

        updated_at=excluded.updated_at

    """,(

        problem_id,

        json.dumps(spec),

        now,

        now

    ))

    conn.commit()

    conn.close()

# ==========================================================
# FEEDBACK QUESTIONS
# ==========================================================

def load_feedback_questions(problem_id):

    conn = get_conn()

    row = conn.execute("""
        SELECT feedback_questions_json
        FROM project_execution
        WHERE problem_id=?
    """, (problem_id,)).fetchone()

    conn.close()

    if not row:
        return None

    if not row["feedback_questions_json"]:
        return None

    return json.loads(row["feedback_questions_json"])


def save_feedback_questions(problem_id, questions):

    conn = get_conn()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""
    INSERT INTO project_execution
    (
        problem_id,
        feedback_questions_json,
        created_at,
        updated_at
    )

    VALUES
    (
        ?,?,?,?
    )

    ON CONFLICT(problem_id)

    DO UPDATE SET

    feedback_questions_json=excluded.feedback_questions_json,

    updated_at=excluded.updated_at
    """,
    (
        problem_id,
        json.dumps(questions),
        now,
        now
    ))

    conn.commit()

    conn.close()
