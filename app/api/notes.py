from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.deps import get_current_user, get_db
from app.models.note import Note, Tag
from app.models.user import User
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=List[NoteRead])
def list_notes(
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    is_favorite: Optional[bool] = None,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Note]:
    query = select(Note).where(Note.owner_id == current_user.id)
    if search:
        like_pattern = f"%{search.lower()}%"
        query = query.where((Note.title.ilike(like_pattern)) | (Note.content.ilike(like_pattern)))
    if is_favorite is not None:
        query = query.where(Note.is_favorite == is_favorite)
    notes = session.exec(query).all()

    if tags:
        tags_set = set(tag.lower() for tag in tags)
        notes = [note for note in notes if {t.name.lower() for t in note.tags} & tags_set]

    return notes


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: NoteCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = Note(title=note_in.title, content=note_in.content, is_favorite=note_in.is_favorite, owner_id=current_user.id)
    note.tags = _get_or_create_tags(session, note_in.tags)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteRead)
def read_note(
    note_id: str,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = _get_note(session, note_id, current_user.id)
    return note


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: str,
    note_update: NoteUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = _get_note(session, note_id, current_user.id)
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.is_favorite is not None:
        note.is_favorite = note_update.is_favorite
    if note_update.tags is not None:
        note.tags = _get_or_create_tags(session, note_update.tags)
    note.touch()
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    note = _get_note(session, note_id, current_user.id)
    session.delete(note)
    session.commit()


@router.post("/{note_id}/favorite", response_model=NoteRead)
def toggle_favorite(
    note_id: str,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = _get_note(session, note_id, current_user.id)
    note.is_favorite = not note.is_favorite
    note.touch()
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def _get_note(session: Session, note_id: str, owner_id: str) -> Note:
    note = session.get(Note, note_id)
    if not note or note.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def _get_or_create_tags(session: Session, tag_names: List[str]) -> List[Tag]:
    normalized = [tag.strip() for tag in tag_names if tag.strip()]
    if not normalized:
        return []
    existing_tags = session.exec(select(Tag).where(Tag.name.in_(normalized))).all()
    existing_map = {tag.name: tag for tag in existing_tags}
    tags: List[Tag] = []
    for name in normalized:
        tag = existing_map.get(name)
        if not tag:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()
            existing_map[name] = tag
        tags.append(tag)
    return tags
