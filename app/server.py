"""Minimal WSGI application serving the Liquid Notes experience."""
from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

from .storage import Storage

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")


@dataclass
class Response:
    status: str
    headers: list[tuple[str, str]]
    body: bytes


class NotesApp:
    """A tiny WSGI application exposing HTML and JSON endpoints."""

    def __init__(self, storage: Storage, static_root: Path) -> None:
        self._storage = storage
        self._static_root = static_root.resolve()
        self._index_file = (static_root / "index.html").resolve()

    # ------------------------------------------------------------------ WSGI
    def __call__(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        response = self._dispatch(environ)
        start_response(response.status, response.headers)
        return [response.body]

    # ---------------------------------------------------------------- Routing
    def _dispatch(self, environ: dict) -> Response:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")

        if method == "GET" and path == "/":
            return self._serve_static(self._index_file)
        if method == "GET" and path.startswith("/static/"):
            static_path = self._safe_static_path(path)
            if static_path is None:
                return self._json({"error": "Resource not found"}, status="404 Not Found")
            return self._serve_static(static_path)

        if path.startswith("/api/notes"):
            return self._handle_api(method, path, environ)

        return self._json({"error": "Resource not found"}, status="404 Not Found")

    # ---------------------------------------------------------- API handlers
    def _handle_api(self, method: str, path: str, environ: dict) -> Response:
        if path == "/api/notes" and method == "GET":
            return self._json(self._storage.list_notes())
        if path == "/api/notes" and method == "POST":
            payload = self._read_json(environ)
            title = (payload.get("title") or "").strip()
            content = (payload.get("content") or "").strip()
            if not title:
                return self._json({"error": "제목을 입력해주세요."}, status="400 Bad Request")
            if not content:
                return self._json({"error": "내용을 입력해주세요."}, status="400 Bad Request")
            note = self._storage.create_note(title=title, content=content)
            return self._json(note, status="201 Created")

        note_id = self._extract_note_id(path)
        if note_id is None:
            return self._json({"error": "Resource not found"}, status="404 Not Found")

        if method == "GET":
            note = self._storage.get_note(note_id)
            if note is None:
                return self._json({"error": "Resource not found"}, status="404 Not Found")
            return self._json(note)
        if method == "PUT":
            payload = self._read_json(environ)
            title = (payload.get("title") or "").strip()
            content = (payload.get("content") or "").strip()
            if not title:
                return self._json({"error": "제목을 입력해주세요."}, status="400 Bad Request")
            if not content:
                return self._json({"error": "내용을 입력해주세요."}, status="400 Bad Request")
            note = self._storage.update_note(note_id, title=title, content=content)
            if note is None:
                return self._json({"error": "Resource not found"}, status="404 Not Found")
            return self._json(note)
        if method == "DELETE":
            deleted = self._storage.delete_note(note_id)
            if not deleted:
                return self._json({"error": "Resource not found"}, status="404 Not Found")
            return Response(
                status="204 No Content",
                headers=[("Content-Length", "0")],
                body=b"",
            )

        return self._json({"error": "Method not allowed"}, status="405 Method Not Allowed")

    # --------------------------------------------------------------- Helpers
    def _safe_static_path(self, path: str) -> Optional[Path]:
        relative = Path(path[len("/static/") :])
        full_path = (self._static_root / relative).resolve()
        try:
            full_path.relative_to(self._static_root)
        except ValueError:
            return None
        return full_path

    def _serve_static(self, path: Path) -> Response:
        if not path.is_file():
            return self._json({"error": "Resource not found"}, status="404 Not Found")
        body = path.read_bytes()
        content_type, _ = mimetypes.guess_type(path.name)
        headers = [("Content-Type", content_type or "application/octet-stream")]
        headers.append(("Content-Length", str(len(body))))
        return Response(status="200 OK", headers=headers, body=body)

    def _json(self, payload: object, status: str = "200 OK") -> Response:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        return Response(status=status, headers=headers, body=body)

    def _read_json(self, environ: dict) -> dict:
        try:
            length = int(environ.get("CONTENT_LENGTH", "0"))
        except ValueError:
            length = 0
        stream = environ.get("wsgi.input")
        if stream is None or length <= 0:
            return {}
        raw = stream.read(length)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _extract_note_id(self, path: str) -> Optional[int]:
        segments = [segment for segment in path.strip("/").split("/") if segment]
        if len(segments) != 3 or segments[0] != "api" or segments[1] != "notes":
            return None
        try:
            return int(segments[2])
        except ValueError:
            return None
