from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from app.models.base import IDMixin, TimestampMixin


class ConversationThread(IDMixin, TimestampMixin, table=True):
    __tablename__ = "conversationthread"

    owner_id: str = Field(foreign_key="user.id")
    source: str
    external_url: str | None = None
    captured_at: datetime | None = None

    owner: "User | None" = Relationship(back_populates="threads")
    chunks: list["ConversationChunk"] = Relationship(back_populates="thread")
    insights: list["Insight"] = Relationship(back_populates="thread")


class ConversationChunk(IDMixin, TimestampMixin, table=True):
    __tablename__ = "conversationchunk"

    thread_id: str = Field(foreign_key="conversationthread.id")
    role: str
    content: str
    sequence: int
    embedding_vector: list[float] | None = Field(default=None, sa_column=Column(JSON))
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    thread: ConversationThread | None = Relationship(back_populates="chunks")


from app.models.user import User  # noqa: E402  # pylint: disable=wrong-import-position
from app.models.note import Insight  # noqa: E402  # pylint: disable=wrong-import-position
