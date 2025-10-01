"""Application factory for the Liquid Notes web app."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .server import NotesApp
from .storage import create_storage


def create_app(database_url: Optional[str] = None) -> NotesApp:
    """Create a fully configured WSGI application.

    Parameters
    ----------
    database_url:
        Optional database connection string. When omitted the value is read
        from the ``DATABASE_URL`` environment variable and defaults to a
        SQLite file placed alongside the project directory. PostgreSQL URLs
        are also supported when a ``psycopg`` compatible driver is available.
    """

    static_dir = Path(__file__).resolve().parent / "static"
    storage = create_storage(database_url)
    return NotesApp(storage=storage, static_root=static_dir)
