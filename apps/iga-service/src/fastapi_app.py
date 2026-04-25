from __future__ import annotations

from fastapi import FastAPI

from api_routes import router as api_router
from core.config import settings
from ui_routes import router as ui_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
    )
    app.include_router(api_router)
    app.include_router(ui_router)
    return app


app = create_app()
