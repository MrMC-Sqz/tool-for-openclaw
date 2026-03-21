from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.routes.health import router as health_router
from app.routes.scan import router as scan_router
from app.routes.skills import router as skills_router

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(skills_router)
app.include_router(scan_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
