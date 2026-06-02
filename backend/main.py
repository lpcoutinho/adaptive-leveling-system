"""Fábrica da aplicação FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.api.routes import health
from backend.infrastructure.telemetry.tracer import setup_telemetry
from backend.infrastructure.telemetry.logger import setup_logger

settings = get_settings()


def create_app() -> FastAPI:
    """
    Cria e configura a instância do FastAPI.

    Returns:
        FastAPI: Aplicação configurada.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )

    # Configurar Logger
    setup_logger(debug=settings.debug)

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configurar Telemetria (OpenTelemetry)
    setup_telemetry(
        app, 
        service_name=settings.otel_service_name,
        endpoint=settings.otel_exporter_otlp_endpoint,
        debug=settings.debug
    )

    # Incluir Rotas
    app.include_router(health.router)

    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Adaptive Leveling System API",
            "docs": "/docs"
        }

    return app


app = create_app()
