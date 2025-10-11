from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class Message(BaseModel):
    message: str


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
