"""SQLite persistence for MaizeSecure scan history."""

import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


DB_PATH = Path("maizesecure_scans.db")
TIMEZONE = ZoneInfo("Africa/Accra")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanned_at TEXT NOT NULL,
                image BLOB NOT NULL,
                image_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                source TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            UPDATE scans
            SET severity = 'Early to Moderate'
            WHERE severity = 'Early'
            """
        )


def save_scan(uploaded_file, prediction: dict) -> int | None:
    severity = prediction.get("severity")
    if uploaded_file is None or not severity:
        return None

    init_db()
    scanned_at = datetime.now(TIMEZONE).isoformat(timespec="seconds")
    image_type = getattr(uploaded_file, "type", None) or "image/jpeg"

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO scans (scanned_at, image, image_type, severity, confidence, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                scanned_at,
                uploaded_file.getvalue(),
                image_type,
                severity,
                int(prediction.get("confidence", 0)),
                prediction.get("source", "model"),
            ),
        )
        return int(cursor.lastrowid)


def get_scans(severity: str = "All") -> list[dict]:
    init_db()
    query = """
        SELECT id, scanned_at, image, image_type, severity, confidence, source
        FROM scans
    """
    params: tuple[str, ...] = ()
    if severity != "All":
        query += " WHERE severity = ?"
        params = (severity,)
    query += " ORDER BY scanned_at DESC"

    with get_connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_scan(scan_id: int) -> dict | None:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, scanned_at, image, image_type, severity, confidence, source
            FROM scans
            WHERE id = ?
            """,
            (scan_id,),
        ).fetchone()
        return dict(row) if row else None


def format_scan_time(value: str) -> str:
    scanned_at = datetime.fromisoformat(value)
    return scanned_at.strftime("%b %d, %Y - %I:%M %p")
