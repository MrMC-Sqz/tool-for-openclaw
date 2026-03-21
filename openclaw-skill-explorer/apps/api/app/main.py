from fastapi import FastAPI

from app.core.config import settings
from app.routes.health import router as health_router

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
