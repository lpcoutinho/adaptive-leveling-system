"""Fábrica da aplicação FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    assessment,
    health,
    leveling,
    pdf,
    prerequisites,
    quiz,
    readiness,
    workflow,
)
from backend.config import get_settings
from backend.infrastructure.telemetry.logger import setup_logger
from backend.infrastructure.telemetry.tracer import setup_telemetry

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)
    setup_logger(debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_telemetry(
        app,
        service_name=settings.otel_service_name,
        endpoint=settings.otel_exporter_otlp_endpoint,
        console_debug=settings.otel_console_debug,
    )

    app.include_router(health.router)
    app.include_router(pdf.router, prefix="/api/v1")
    app.include_router(prerequisites.router, prefix="/api/v1")
    app.include_router(assessment.router, prefix="/api/v1")
    app.include_router(quiz.router, prefix="/api/v1")
    app.include_router(readiness.router, prefix="/api/v1")
    app.include_router(leveling.router, prefix="/api/v1")
    app.include_router(workflow.router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "Welcome to Adaptive Leveling System API", "docs": "/docs"}

    return app


app = create_app()
