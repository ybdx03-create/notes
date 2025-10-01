from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from .database import db
from .models import Note

bp = Blueprint("main", __name__)


def _note_or_404(note_id: int) -> Note:
    note = Note.query.get(note_id)
    if note is None:
        from flask import abort

        abort(404, description="Note not found")
    return note


@bp.route("/")
def index():
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return render_template("index.html", notes=notes)


@bp.route("/api/notes", methods=["GET"])
def list_notes():
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])


@bp.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title:
        return jsonify({"error": "제목을 입력해주세요."}), 400
    if not content:
        return jsonify({"error": "내용을 입력해주세요."}), 400

    note = Note(title=title, content=content)
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


@bp.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id: int):
    note = _note_or_404(note_id)

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title:
        return jsonify({"error": "제목을 입력해주세요."}), 400
    if not content:
        return jsonify({"error": "내용을 입력해주세요."}), 400

    note.title = title
    note.content = content
    db.session.commit()
    return jsonify(note.to_dict())


@bp.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id: int):
    note = _note_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return ("", 204)
