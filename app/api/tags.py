from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.api.deps import get_current_user, get_db
from app.models.note import NoteTagLink, Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[TagRead])
def list_tags(
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[Tag]:
    tags = session.exec(select(Tag)).all()
    return tags


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate,
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Tag:
    existing = session.exec(select(Tag).where(Tag.name == tag_in.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    tag = Tag(name=tag_in.name)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.get("/popular", response_model=List[TagRead])
def popular_tags(
    limit: int = 10,
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[Tag]:
    stmt = (
        select(Tag)
        .join(NoteTagLink, NoteTagLink.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(func.count(NoteTagLink.note_id).desc())
        .limit(limit)
    )
    return session.exec(stmt).all()
