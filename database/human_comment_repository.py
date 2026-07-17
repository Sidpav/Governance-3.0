from datetime import datetime

from database.db import get_conn


def _ensure_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_human_comments (
            project_id TEXT NOT NULL,
            recommendation_scope TEXT NOT NULL,
            recommendation_key TEXT NOT NULL,
            comment TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (project_id, recommendation_scope, recommendation_key)
        )
        """
    )


def load_human_comment(project_id, scope, recommendation_key):
    conn = get_conn()
    _ensure_table(conn)
    row = conn.execute(
        """
        SELECT comment FROM ai_human_comments
        WHERE project_id=? AND recommendation_scope=? AND recommendation_key=?
        """,
        (str(project_id), scope, str(recommendation_key)),
    ).fetchone()
    conn.close()
    return row["comment"] if row else ""


def save_human_comment(project_id, scope, recommendation_key, comment):
    conn = get_conn()
    _ensure_table(conn)
    conn.execute(
        """
        INSERT INTO ai_human_comments
            (project_id, recommendation_scope, recommendation_key, comment, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(project_id, recommendation_scope, recommendation_key)
        DO UPDATE SET comment=excluded.comment, updated_at=excluded.updated_at
        """,
        (
            str(project_id),
            scope,
            str(recommendation_key),
            comment.strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()
