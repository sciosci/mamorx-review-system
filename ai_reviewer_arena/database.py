import sqlite3
from contextlib import contextmanager

DATABASE_NAME = "review_comparison.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                paper_id TEXT,
                reviewer_a INTEGER,
                reviewer_b INTEGER,
                technical_quality TEXT,
                constructiveness TEXT,
                clarity TEXT,
                overall_quality TEXT
            )
        """
        )
        conn.commit()


def store_comparison(user_email, paper_id, reviewer_a, reviewer_b, comparisons):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO comparisons (user_email, paper_id, reviewer_a, reviewer_b,
                                     technical_quality, constructiveness, clarity, overall_quality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_email,
                paper_id,
                reviewer_a,
                reviewer_b,
                comparisons.get("Technical Quality"),
                comparisons.get("Constructiveness"),
                comparisons.get("Clarity"),
                comparisons.get("Overall Quality"),
            ),
        )
        conn.commit()


def get_all_comparisons():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT reviewer_a, reviewer_b, technical_quality, constructiveness, clarity, overall_quality
            FROM comparisons
            ORDER BY id
        """
        )
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
