"""Configuração do OpenTelemetry para rastreamento de requisições."""

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_telemetry(
    app: FastAPI, service_name: str, endpoint: str, console_debug: bool = False
) -> None:
    """Configura o OpenTelemetry para a aplicação.

    Args:
        app: Instância do FastAPI.
        service_name: Nome do serviço.
        endpoint: Endpoint do OTLP exporter.
        console_debug: Se True, também exporta Spans para o console.
    """
    import os

    is_testing = os.getenv("TESTING", "").lower() == "true"
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if console_debug:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    if not is_testing:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except Exception as e:
            print(f"Aviso: Jaeger (OTLP) não disponível em {endpoint}: {e}")

    trace.set_tracer_provider(provider)

    # Configurar métricas (prompt usage, llm calls, tokens)
    if not is_testing:
        try:
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"),
                export_interval_millis=15000,
            )
            meter_provider = MeterProvider(metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
        except Exception as e:
            print(f"Aviso: Exportador de métricas não disponível: {e}")

    FastAPIInstrumentor.instrument_app(app)


def get_tracer(name: str):
    """Retorna um tracer para uso manual."""
    return trace.get_tracer(name)
