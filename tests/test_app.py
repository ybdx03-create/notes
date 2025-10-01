from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from typing import Tuple
from wsgiref.util import setup_testing_defaults

from app import create_app


class NotesAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(self.temp_dir.name, "test_notes.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        self.app = create_app()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        os.environ.pop("DATABASE_URL", None)

    # -------------------------------------------------------------- utilities
    def request(self, method: str, path: str, body: bytes | None = None) -> Tuple[int, dict, bytes]:
        environ = {}
        setup_testing_defaults(environ)
        environ["REQUEST_METHOD"] = method
        environ["PATH_INFO"] = path
        payload = body or b""
        environ["wsgi.input"] = io.BytesIO(payload)
        environ["CONTENT_LENGTH"] = str(len(payload))
        if payload:
            environ["CONTENT_TYPE"] = "application/json"

        captured = {}

        def start_response(status: str, headers: list[tuple[str, str]]):
            captured["status"] = int(status.split()[0])
            captured["headers"] = dict(headers)

        response_body = b"".join(self.app(environ, start_response))
        return captured["status"], captured["headers"], response_body

    # ----------------------------------------------------------------- helpers
    def _create_note(self, title: str = "测试", content: str = "正文") -> dict:
        status, _, body = self.request(
            "POST",
            "/api/notes",
            json.dumps({"title": title, "content": content}).encode("utf-8"),
        )
        self.assertEqual(status, 201)
        return json.loads(body)

    # ------------------------------------------------------------------- tests
    def test_list_initial_notes_is_empty(self):
        status, _, body = self.request("GET", "/api/notes")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), [])

    def test_create_and_fetch_note(self):
        created = self._create_note()
        status, _, body = self.request("GET", "/api/notes")
        self.assertEqual(status, 200)
        notes = json.loads(body)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["id"], created["id"])

    def test_update_note(self):
        created = self._create_note()
        payload = json.dumps({"title": "修改", "content": "更新内容"}).encode("utf-8")
        status, _, body = self.request("PUT", f"/api/notes/{created['id']}", payload)
        self.assertEqual(status, 200)
        updated = json.loads(body)
        self.assertEqual(updated["title"], "修改")
        self.assertEqual(updated["content"], "更新内容")

    def test_delete_note(self):
        created = self._create_note()
        status, _, _ = self.request("DELETE", f"/api/notes/{created['id']}")
        self.assertEqual(status, 204)
        status, _, body = self.request("GET", "/api/notes")
        self.assertEqual(json.loads(body), [])

    def test_validation_errors(self):
        status, _, body = self.request(
            "POST",
            "/api/notes",
            json.dumps({"title": " ", "content": " "}).encode("utf-8"),
        )
        self.assertEqual(status, 400)
        self.assertIn("请填写标题。", json.loads(body)["error"])

        note = self._create_note()
        status, _, body = self.request("PUT", f"/api/notes/{note['id']}", b"{}")
        self.assertEqual(status, 400)
        self.assertIn("请填写标题。", json.loads(body)["error"])


if __name__ == "__main__":
    unittest.main()
