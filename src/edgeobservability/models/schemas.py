from pydantic import BaseModel, Field
from typing import Any

class SystemMetrics(BaseModel):
    cpu_usage_percent: float = Field(..., ge=0.0, le=100.0)
    ram_usage_bytes: int = Field(..., ge=0)
    disk_usage_bytes: int = Field(..., ge=0)

class InferenceMetrics(BaseModel):
    model_name: str
    inference_count: int = Field(default=1, ge=1)
    latency_ms: float = Field(..., ge=0.0)
    success: bool = True

class EdgeTelemetryPayload(BaseModel):
    node_id: str
    factory_location: str
    system_metrics: SystemMetrics | None = None
    inference_metrics: list[InferenceMetrics] = Field(default_factory=list)

class LogPayload(BaseModel):
    node_id: str
    level: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)
