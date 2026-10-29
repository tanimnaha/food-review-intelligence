"""SQLite storage manager for user-submitted reviews in Kolkata FoodLens."""

from __future__ import annotations
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "user_reviews.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_submitted_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                review_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sentiment_label TEXT NOT NULL,
                sentiment_confidence REAL NOT NULL,
                sentiment_food TEXT NOT NULL,
                sentiment_service TEXT NOT NULL,
                sentiment_hygiene TEXT NOT NULL,
                sentiment_ambience TEXT NOT NULL,
                sentiment_price TEXT NOT NULL
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rest_id ON user_submitted_reviews(restaurant_id);")
    conn.close()

def save_user_review(
    restaurant_id: str,
    user_name: str,
    rating: int,
    review_text: str,
    sentiment: Dict[str, Any],
    aspects: Dict[str, str],
) -> int:
    init_db()
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO user_submitted_reviews (
                restaurant_id, user_name, rating, review_text, created_at,
                sentiment_label, sentiment_confidence,
                sentiment_food, sentiment_service, sentiment_hygiene,
                sentiment_ambience, sentiment_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                restaurant_id,
                user_name.strip() or "Anonymous Diner",
                int(rating),
                review_text.strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                sentiment["label"],
                float(sentiment["confidence"]),
                aspects.get("food", "neutral"),
                aspects.get("service", "neutral"),
                aspects.get("hygiene", "neutral"),
                aspects.get("ambience", "neutral"),
                aspects.get("price", "neutral"),
            )
        )
        new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_user_reviews(restaurant_id: str) -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM user_submitted_reviews WHERE restaurant_id = ? ORDER BY id DESC",
        (restaurant_id,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_all_user_reviews() -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM user_submitted_reviews ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print(f"Initialized SQLite database at: {DB_PATH}")
