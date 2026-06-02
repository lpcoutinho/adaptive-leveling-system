"""Configuração do OpenTelemetry para rastreamento de requisições."""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI


def setup_telemetry(app: FastAPI, service_name: str, endpoint: str, debug: bool = False) -> None:
    """
    Configura o OpenTelemetry para a aplicação.

    Args:
        app: Instância do FastAPI.
        service_name: Nome do serviço.
        endpoint: Endpoint do OTLP exporter.
        debug: Se True, também exporta Spans para o console.
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Exportar para Console apenas em modo debug (evita poluir logs)
    if debug:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    try:
        otlp_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    except Exception as e:
        # Registra erro mas não interrompe a aplicação
        print(f"Aviso: Jaeger (OTLP) não disponível em {endpoint}: {e}")

    trace.set_tracer_provider(provider)

    # Instrumentação automática do FastAPI
    FastAPIInstrumentor.instrument_app(app)


def get_tracer(name: str):
    """Retorna um tracer para uso manual."""
    return trace.get_tracer(name)
