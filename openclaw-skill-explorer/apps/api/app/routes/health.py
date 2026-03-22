from fastapi import APIRouter, Depends

from app.core.observability import snapshot_metrics
from app.core.security import require_roles
from app.schemas.health import HealthResponse, MetricsResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
def readiness_check() -> ReadyResponse:
    return ReadyResponse(status="ready")


@router.get("/metrics", response_model=MetricsResponse)
def metrics(
    _role: str = Depends(require_roles("admin")),
) -> MetricsResponse:
    return MetricsResponse(**snapshot_metrics())
