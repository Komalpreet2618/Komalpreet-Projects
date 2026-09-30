import sqlite3
from datetime import datetime
from typing import Optional

import pandas as pd


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            role TEXT NOT NULL,
            score REAL NOT NULL,
            emotion TEXT,
            question TEXT,
            transcript TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_interview(
    db_path: str,
    role: str,
    score: float,
    emotion: str,
    question: str,
    transcript: str,
    date: Optional[str] = None,
) -> None:
    row_date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO interviews (date, role, score, emotion, question, transcript)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (row_date, role, float(score), emotion, question, transcript),
    )
    conn.commit()
    conn.close()


def fetch_history(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    query = "SELECT date, role, score, emotion, question, transcript FROM interviews"
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df
