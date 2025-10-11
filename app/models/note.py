from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import IDMixin, TimestampMixin


class NoteTagLink(SQLModel, table=True):
    note_id: str = Field(foreign_key="note.id", primary_key=True)
    tag_id: str = Field(foreign_key="tag.id", primary_key=True)


class NoteBase(SQLModel):
    title: str
    content: str
    is_favorite: bool = False


class Note(IDMixin, TimestampMixin, NoteBase, table=True):
    owner_id: str = Field(foreign_key="user.id")

    owner: Optional["User"] = Relationship(back_populates="notes")
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTagLink)
    insights: list["Insight"] = Relationship(back_populates="note")


class Tag(IDMixin, TimestampMixin, table=True):
    name: str = Field(index=True, sa_column_kwargs={"unique": True})

    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTagLink)


class InsightBase(SQLModel):
    summary: str
    key_questions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    action_items: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class Insight(IDMixin, TimestampMixin, InsightBase, table=True):
    note_id: str = Field(foreign_key="note.id")
    thread_id: str = Field(foreign_key="conversationthread.id")
    chunk_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    note: Note | None = Relationship(back_populates="insights")
    thread: Optional["ConversationThread"] = Relationship(back_populates="insights")


from app.models.user import User  # noqa: E402  # pylint: disable=wrong-import-position
from app.models.conversation import ConversationThread  # noqa: E402  # pylint: disable=wrong-import-position
