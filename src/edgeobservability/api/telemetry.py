from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import structlog

from edgeobservability.models.schemas import EdgeTelemetryPayload, LogPayload
from edgeobservability.core.metrics_engine import (
    REGISTRY,
    EDGE_CPU_USAGE,
    EDGE_RAM_USAGE,
    EDGE_INFERENCE_COUNT,
    EDGE_INFERENCE_LATENCY
)

logger = structlog.get_logger()
telemetry_router = APIRouter()
exporter_router = APIRouter()

@telemetry_router.post("/telemetry/metrics")
async def ingest_metrics(payload: EdgeTelemetryPayload) -> dict[str, str]:
    # Ingest System Metrics
    if payload.system_metrics:
        EDGE_CPU_USAGE.labels(
            node_id=payload.node_id, 
            factory_location=payload.factory_location
        ).set(payload.system_metrics.cpu_usage_percent)
        
        EDGE_RAM_USAGE.labels(
            node_id=payload.node_id, 
            factory_location=payload.factory_location
        ).set(payload.system_metrics.ram_usage_bytes)

    # Ingest Inference Metrics
    for inf in payload.inference_metrics:
        status = "success" if inf.success else "failure"
        EDGE_INFERENCE_COUNT.labels(
            node_id=payload.node_id,
            factory_location=payload.factory_location,
            model_name=inf.model_name,
            status=status
        ).inc(inf.inference_count)
        
        EDGE_INFERENCE_LATENCY.labels(
            node_id=payload.node_id,
            factory_location=payload.factory_location,
            model_name=inf.model_name
        ).observe(inf.latency_ms)
        
    return {"status": "metrics_ingested"}

@telemetry_router.post("/telemetry/logs")
async def ingest_logs(payload: LogPayload) -> dict[str, str]:
    # In a real environment, this forwards to Loki or Elasticsearch.
    # Here, we use structlog to instantly emit a structured JSON string.
    log_func = getattr(logger, payload.level.lower(), logger.info)
    log_func(
        payload.message,
        node_id=payload.node_id,
        **payload.context
    )
    return {"status": "logs_ingested"}

@exporter_router.get("/metrics")
async def export_prometheus_metrics() -> Response:
    # This exposes the standard Prometheus /metrics endpoint
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
