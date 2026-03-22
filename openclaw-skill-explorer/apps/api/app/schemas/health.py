from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str


class RouteMetrics(BaseModel):
    count: int
    errors: int
    avg_duration_ms: float


class MetricsResponse(BaseModel):
    total_requests: int
    total_errors: int
    avg_duration_ms: float
    by_route: dict[str, RouteMetrics]
