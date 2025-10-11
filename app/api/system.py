from datetime import datetime

from fastapi import APIRouter

from app.schemas.auth import HealthCheck

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthCheck)
def health_check() -> HealthCheck:
    return HealthCheck(status="ok", timestamp=datetime.utcnow())
