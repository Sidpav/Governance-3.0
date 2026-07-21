import json
from datetime import datetime

from database.db import get_conn


# ==========================================================
# FEEDBACK QUESTIONS
# ==========================================================

def load_feedback_questions(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT feedback_questions_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return None

    if not row["feedback_questions_json"]:
        return None

    return json.loads(row["feedback_questions_json"])


def save_feedback_questions(problem_id, questions):

    conn = get_conn()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        """
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
            now,
        ),
    )

    conn.commit()
    conn.close()


# ==========================================================
# FEEDBACK RESULTS
# ==========================================================

def load_feedback(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT feedback_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return {}

    if not row["feedback_json"]:
        return {}

    return json.loads(row["feedback_json"])


def save_feedback(problem_id, feedback):

    conn = get_conn()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        """
        INSERT INTO project_execution
        (
            problem_id,
            feedback_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            feedback_json=excluded.feedback_json,

            updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(feedback),
            now,
            now,
        ),
    )

    conn.commit()
    conn.close()


# ==========================================================
# UPDATE ONE STAKEHOLDER
# ==========================================================

def update_feedback(problem_id, stakeholder, review):

    feedback = load_feedback(problem_id)

    feedback[stakeholder] = review

    save_feedback(
        problem_id,
        feedback,
    )


# ==========================================================
# GET ONE STAKEHOLDER
# ==========================================================

def get_feedback(problem_id, stakeholder):

    feedback = load_feedback(problem_id)

    return feedback.get(stakeholder, {})


# ==========================================================
# COMPLETED STAKEHOLDERS
# ==========================================================

def completed_stakeholders(problem_id):

    feedback = load_feedback(problem_id)

    completed = []

    for stakeholder, review in feedback.items():

        if review.get("submitted", False):

            completed.append(stakeholder)

    return completed


# ==========================================================
# PROGRESS
# ==========================================================

def feedback_progress(problem_id):

    completed = completed_stakeholders(problem_id)

    return len(completed)


# ==========================================================
# STAKEHOLDER SUMMARIES
# ==========================================================

def load_consolidated_summary(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT consolidated_feedback_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return {}

    if not row["consolidated_feedback_json"]:
        return {}

    return json.loads(
        row["consolidated_feedback_json"]
    )

def save_feedback_summary(
    problem_id,
    stakeholder,
    summary,
):

    summaries = load_feedback_summaries(
        problem_id
    )

    summaries[stakeholder] = summary

    conn = get_conn()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute(
        """
        INSERT INTO project_execution
        (
            problem_id,
            feedback_summary_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?, ?, ?, ?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            feedback_summary_json=excluded.feedback_summary_json,

            updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(summaries),
            now,
            now,
        ),
    )

    conn.commit()

    conn.close()

def load_feedback_summary(
    problem_id,
    stakeholder,
):

    summaries = load_feedback_summaries(problem_id)

    return summaries.get(
        stakeholder
    )

# ==========================================================
# CONSOLIDATED FEEDBACK SUMMARY
# ==========================================================

def save_consolidated_summary(
    problem_id,
    summary,
):

    conn = get_conn()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute(
        """
        INSERT INTO project_execution
        (
            problem_id,
            consolidated_feedback_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?, ?, ?, ?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            consolidated_feedback_json = excluded.consolidated_feedback_json,

            updated_at = excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(summary),
            now,
            now,
        ),
    )

    conn.commit()

    conn.close()

def all_feedback_complete(problem_id):

    questions = load_feedback_questions(problem_id)

    feedback = load_feedback(problem_id)

    if not questions:
        return False

    required = len(questions["stakeholders"])

    completed = 0

    for stakeholder in questions["stakeholders"]:

        role = stakeholder["role"]

        if (
            role in feedback
            and feedback[role].get("submitted", False)
        ):
            completed += 1

    return completed == required

def load_feedback_summaries(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT feedback_summary_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return {}

    if not row["feedback_summary_json"]:
        return {}

    return json.loads(
        row["feedback_summary_json"]
    )