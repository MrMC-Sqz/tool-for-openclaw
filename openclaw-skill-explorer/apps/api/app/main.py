import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.observability import record_request
from app.db.init_db import init_db
from app.routes.health import router as health_router
from app.routes.scan import router as scan_router
from app.routes.skills import router as skills_router
from app.routes.sources import router as sources_router

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(sources_router)
app.include_router(skills_router)
app.include_router(scan_router)


@app.middleware("http")
async def request_metrics_middleware(request: Request, call_next):
    started_at = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - started_at) * 1000
        status_code = response.status_code if response is not None else 500
        record_request(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=duration_ms,
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
