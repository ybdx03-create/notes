from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: str
    content: str
    sequence: Optional[int] = None
    embedding_vector: Optional[List[float]] = None
    keywords: Optional[List[str]] = None


class ConversationImportRequest(BaseModel):
    source: str
    external_url: Optional[str] = None
    captured_at: Optional[datetime] = None
    messages: List[ConversationMessage]


class ConversationChunkRead(BaseModel):
    id: str
    role: str
    content: str
    sequence: int
    keywords: List[str]

    class Config:
        orm_mode = True


class ConversationThreadRead(BaseModel):
    id: str
    source: str
    external_url: Optional[str]
    captured_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    chunks: List[ConversationChunkRead]

    class Config:
        orm_mode = True


class InsightCreate(BaseModel):
    summary: str
    key_questions: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    chunk_ids: List[str] = Field(default_factory=list)


class InsightRead(BaseModel):
    id: str
    summary: str
    key_questions: List[str]
    action_items: List[str]
    chunk_ids: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
