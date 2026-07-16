import json
from datetime import datetime

from database.db import get_conn


# ==========================================================
# DATA REQUIREMENTS
# ==========================================================

def load_data_requirements(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT data_requirements_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return None

    if not row["data_requirements_json"]:
        return None

    return json.loads(
        row["data_requirements_json"]
    )


def save_data_requirements(
    problem_id,
    data,
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
            data_requirements_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            data_requirements_json=excluded.data_requirements_json,

            updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(data),
            now,
            now,
        ),
    )

    conn.commit()

    conn.close()


# ==========================================================
# USER DATA REVIEW
# ==========================================================

def load_data_review(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT data_review_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return {}

    if not row["data_review_json"]:
        return {}

    return json.loads(
        row["data_review_json"]
    )


def save_data_review(
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
            data_review_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            data_review_json=excluded.data_review_json,

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


# ==========================================================
# UPDATE HELPERS
# ==========================================================

def update_attribute(
    problem_id,
    attribute,
    available,
    missing_percent,
):

    review = load_data_review(problem_id)

    if "attributes" not in review:
        review["attributes"] = {}

    review["attributes"][attribute] = {

        "available": available,

        "missing_percent": missing_percent,

    }

    save_data_review(
        problem_id,
        review,
    )


def update_leakage_answer(
    problem_id,
    question,
    answer,
):

    review = load_data_review(problem_id)

    if "leakage" not in review:
        review["leakage"] = {}

    review["leakage"][question] = answer

    save_data_review(
        problem_id,
        review,
    )


def update_quality_answer(
    problem_id,
    question,
    answer,
):

    review = load_data_review(problem_id)

    if "quality" not in review:
        review["quality"] = {}

    review["quality"][question] = answer

    save_data_review(
        problem_id,
        review,
    )


def update_source_trust(
    problem_id,
    source,
    value,
):

    review = load_data_review(problem_id)

    if "trustworthiness" not in review:
        review["trustworthiness"] = {}

    review["trustworthiness"][source] = value

    save_data_review(
        problem_id,
        review,
    )


def update_topic(
    problem_id,
    topic,
    status,
):

    review = load_data_review(problem_id)

    review.setdefault(
        "topics",
        {}
    )[topic] = status

    save_data_review(
        problem_id,
        review,
    )

def load_model_requirements(problem_id):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT model_requirements_json
        FROM project_execution
        WHERE problem_id=?
        """,
        (problem_id,),
    ).fetchone()

    conn.close()

    if not row:
        return None

    if not row["model_requirements_json"]:
        return None

    return json.loads(
        row["model_requirements_json"]
    )

def save_model_requirements(
    problem_id,
    models,
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
            model_requirements_json,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,?,?,?
        )

        ON CONFLICT(problem_id)

        DO UPDATE SET

            model_requirements_json=excluded.model_requirements_json,

            updated_at=excluded.updated_at
        """,
        (
            problem_id,
            json.dumps(models),
            now,
            now,
        ),
    )

    conn.commit()

    conn.close()