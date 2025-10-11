from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user, get_db
from app.models.conversation import ConversationChunk, ConversationThread
from app.models.note import Insight, Note
from app.models.user import User
from app.schemas.conversation import (
    ConversationImportRequest,
    ConversationThreadRead,
    InsightCreate,
    InsightRead,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/import", response_model=ConversationThreadRead, status_code=status.HTTP_201_CREATED)
def import_conversation(
    payload: ConversationImportRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationThread:
    thread = ConversationThread(
        owner_id=current_user.id,
        source=payload.source,
        external_url=payload.external_url,
        captured_at=payload.captured_at,
    )
    session.add(thread)
    session.flush()

    chunks: list[ConversationChunk] = []
    for idx, message in enumerate(payload.messages):
        sequence = message.sequence if message.sequence is not None else idx
        chunk = ConversationChunk(
            thread_id=thread.id,
            role=message.role,
            content=message.content,
            sequence=sequence,
            embedding_vector=message.embedding_vector,
            keywords=message.keywords or [],
        )
        session.add(chunk)
        chunks.append(chunk)

    session.commit()
    session.refresh(thread)
    for chunk in chunks:
        session.refresh(chunk)
    thread.chunks = chunks
    return thread


@router.get("/{thread_id}/insights", response_model=list[InsightRead])
def get_insights(
    thread_id: str,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Insight]:
    thread = session.get(ConversationThread, thread_id)
    if not thread or thread.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return thread.insights


@router.post("/notes/{note_id}/insights", response_model=InsightRead, status_code=status.HTTP_201_CREATED)
def create_insight(
    note_id: str,
    insight_in: InsightCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Insight:
    note = session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if not insight_in.chunk_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="chunk_ids required")

    chunks = session.exec(select(ConversationChunk).where(ConversationChunk.id.in_(insight_in.chunk_ids))).all()
    if len(chunks) != len(insight_in.chunk_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chunk ids")

    thread_ids = {chunk.thread_id for chunk in chunks}
    if len(thread_ids) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chunks must belong to the same thread")

    thread = session.get(ConversationThread, next(iter(thread_ids)))
    if not thread or thread.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Thread does not belong to user")

    insight = Insight(
        note_id=note.id,
        thread_id=thread.id,
        summary=insight_in.summary,
        key_questions=insight_in.key_questions,
        action_items=insight_in.action_items,
        chunk_ids=insight_in.chunk_ids,
    )
    session.add(insight)
    session.commit()
    session.refresh(insight)
    return insight
