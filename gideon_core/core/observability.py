import logging
from pythonjsonlogger import jsonlogger
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app

def setup_observability(app: FastAPI):
    # 1. Structured JSON Logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s %(span_id)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    # 2. OpenTelemetry Tracing Setup (Basic Console Exporter or just Provider for now)
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # 3. Prometheus Metrics Endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    logging.info("Observability (Logs, Tracing, Metrics) initialized.")
