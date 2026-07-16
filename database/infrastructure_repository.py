import json
from datetime import datetime

from database.db import get_conn

def save_infrastructure_review(
    problem_id,
    review,
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
            infrastructure_review_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            infrastructure_review_json=excluded.infrastructure_review_json,

            updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(review),
            now,
            now,
        ),
    )

    conn.commit()

    conn.close()

def load_infrastructure_review(
    problem_id,
):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT infrastructure_review_json

        FROM project_execution

        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:

        return {}

    if not row["infrastructure_review_json"]:

        return {}

    return json.loads(
        row["infrastructure_review_json"]
    )

def save_infrastructure_output(
    problem_id,
    output,
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
            infrastructure_output_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            infrastructure_output_json=excluded.infrastructure_output_json,

            updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(output),
            now,
            now,
        ),
    )

    conn.commit()

    conn.close()

def load_infrastructure_output(
    problem_id,
):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT infrastructure_output_json

        FROM project_execution

        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:

        return {}

    if not row["infrastructure_output_json"]:

        return {}

    return json.loads(
        row["infrastructure_output_json"]
    )

def update_review(
    problem_id,
    key,
    value,
):

    review = load_infrastructure_review(
        problem_id
    )

    review[key] = value

    save_infrastructure_review(
        problem_id,
        review,
    )

def update_security_answer(
    problem_id,
    question,
    answer,
):

    review = load_infrastructure_review(
        problem_id
    )

    review.setdefault(
        "security",
        {}
    )[question] = answer

    save_infrastructure_review(
        problem_id,
        review,
    )

def load_security_questions(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT security_questions_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return None

    if not row["security_questions_json"]:
        return None

    return json.loads(
        row["security_questions_json"]
    )

def save_security_questions(
    problem_id,
    questions,
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
            security_questions_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            security_questions_json=excluded.security_questions_json,

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