from __future__ import annotations

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import IDMixin, TimestampMixin


class UserBase(SQLModel):
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    full_name: str | None = None


class User(IDMixin, TimestampMixin, UserBase, table=True):
    password_hash: str

    notes: list["Note"] = Relationship(back_populates="owner")
    threads: list["ConversationThread"] = Relationship(back_populates="owner")


from app.models.note import Note  # noqa: E402  # pylint: disable=wrong-import-position
from app.models.conversation import ConversationThread  # noqa: E402  # pylint: disable=wrong-import-position
