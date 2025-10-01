"""Persistence layer for Liquid Notes."""
from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Protocol
from urllib.parse import urlparse

DEFAULT_SQLITE_NAME = "notes_dev.db"


class Storage(Protocol):
    def list_notes(self) -> list[dict]:
        ...

    def get_note(self, note_id: int) -> Optional[dict]:
        ...

    def create_note(self, title: str, content: str) -> dict:
        ...

    def update_note(self, note_id: int, title: str, content: str) -> Optional[dict]:
        ...

    def delete_note(self, note_id: int) -> bool:
        ...


# ----------------------------------------------------------------- SQLite impl
class SQLiteStorage:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._lock = threading.Lock()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def list_notes(self) -> list[dict]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, content, created_at, updated_at FROM notes ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def get_note(self, note_id: int) -> Optional[dict]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()
            return dict(row) if row else None

    def create_note(self, title: str, content: str) -> dict:
        timestamp = self._now()
        with self._lock, self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (title, content, timestamp, timestamp),
            )
            conn.commit()
            note_id = cursor.lastrowid
            row = conn.execute(
                "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()
        return dict(row)

    def update_note(self, note_id: int, title: str, content: str) -> Optional[dict]:
        timestamp = self._now()
        with self._lock, self._connect() as conn:
            cursor = conn.execute(
                "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
                (title, content, timestamp, note_id),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return None
            row = conn.execute(
                "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()
        return dict(row) if row else None

    def delete_note(self, note_id: int) -> bool:
        with self._lock, self._connect() as conn:
            cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0


# --------------------------------------------------------------- Factory logic
class StorageError(RuntimeError):
    """Raised when a requested storage backend cannot be constructed."""


def create_storage(database_url: Optional[str] = None) -> Storage:
    url = database_url or os.getenv("DATABASE_URL")
    if not url or url.startswith("sqlite://"):
        return SQLiteStorage(_sqlite_path_from_url(url))

    parsed = urlparse(url)
    if parsed.scheme in {"postgres", "postgresql"}:
        driver = _load_postgres_driver()
        if driver is None:
            raise StorageError(
                "PostgreSQL URL supplied but no psycopg-compatible driver is installed. "
                "Install 'psycopg[binary]' or 'psycopg2-binary' to enable PostgreSQL support."
            )
        return PostgresStorage(url, driver)

    raise StorageError(f"Unsupported DATABASE_URL scheme: {url}")


def _sqlite_path_from_url(url: Optional[str]) -> Path:
    if url and url.startswith("sqlite:///"):
        relative_path = url[len("sqlite:///") :]
    else:
        relative_path = DEFAULT_SQLITE_NAME
    path = Path(relative_path)
    if not path.is_absolute():
        base = Path(os.getenv("APP_DATA_DIR", Path.cwd()))
        path = base / path
    return path


# ----------------------------------------------------------- PostgreSQL helper
class PostgresStorage:
    def __init__(self, dsn: str, driver_module) -> None:
        self._dsn = dsn
        self._driver = driver_module
        self._lock = threading.Lock()
        self._initialize()

    def _connect(self):  # type: ignore[override]
        if self._driver.__name__ == "psycopg":
            conn = self._driver.connect(self._dsn, autocommit=True)
        else:
            conn = self._driver.connect(self._dsn)
            conn.autocommit = True
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )

    def _now(self):
        return datetime.now(timezone.utc).replace(microsecond=0)

    def list_notes(self) -> list[dict]:
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, title, content, created_at, updated_at FROM notes ORDER BY updated_at DESC"
                )
                rows = cur.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_note(self, note_id: int) -> Optional[dict]:
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = %s",
                    (note_id,),
                )
                row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def create_note(self, title: str, content: str) -> dict:
        timestamp = self._now()
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO notes (title, content, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, created_at, updated_at
                    """,
                    (title, content, timestamp, timestamp),
                )
                note_id, created_at, updated_at = cur.fetchone()
        return {
            "id": note_id,
            "title": title,
            "content": content,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        }

    def update_note(self, note_id: int, title: str, content: str) -> Optional[dict]:
        timestamp = self._now()
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE notes SET title = %s, content = %s, updated_at = %s
                    WHERE id = %s
                    RETURNING id, title, content, created_at, updated_at
                    """,
                    (title, content, timestamp, note_id),
                )
                row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def delete_note(self, note_id: int) -> bool:
        with self._lock, self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
                return cur.rowcount > 0

    def _row_to_dict(self, row) -> Optional[dict]:
        if row is None:
            return None
        return {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "updated_at": row[4].isoformat() if row[4] else None,
        }


def _load_postgres_driver():
    for module_name in ("psycopg", "psycopg2"):
        try:
            return __import__(module_name)
        except ImportError:
            continue
    return None
