from fastapi import APIRouter

from app.schemas.health import HealthResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
def readiness_check() -> ReadyResponse:
    return ReadyResponse(status="ready")
