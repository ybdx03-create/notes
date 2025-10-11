from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.tag import TagRead


class NoteBase(BaseModel):
    title: str
    content: str
    is_favorite: bool = False


class NoteCreate(NoteBase):
    tags: List[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None


class NoteRead(NoteBase):
    id: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagRead]

    class Config:
        orm_mode = True
