from datetime import datetime

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagRead(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
