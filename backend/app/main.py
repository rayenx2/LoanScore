import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import activity, drift, health, metrics, prediction, reporting, retraining
from app.core.config import settings
from app.core.logging_middleware import RequestLoggingMiddleware


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)

    app = FastAPI(
        title=settings.project_name,
        version=settings.api_version,
        description="API for monitoring deployed machine learning model reliability.",
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(prediction.router, prefix="/api/v1", tags=["prediction"])
    app.include_router(drift.router, prefix="/api/v1", tags=["drift"])
    app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
    app.include_router(retraining.router, prefix="/api/v1", tags=["retraining"])
    app.include_router(reporting.router, prefix="/api/v1", tags=["reporting"])
    app.include_router(activity.router, prefix="/api/v1", tags=["activity"])

    return app


app = create_app()
