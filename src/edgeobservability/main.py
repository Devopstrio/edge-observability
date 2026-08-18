import structlog
import uvicorn
from fastapi import FastAPI

from edgeobservability.api.telemetry import exporter_router, telemetry_router

logger = structlog.get_logger()

app = FastAPI(
    title="Edge Observability Gateway",
    description="Central Telemetry Gateway for the Edge AI Ecosystem",
    version="1.0.0"
)

# API routes for Edge Nodes to push data to
app.include_router(telemetry_router, prefix="/api/v1")

# Standard Prometheus scraping route (usually on root)
app.include_router(exporter_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

def start() -> None:
    uvicorn.run("edgeobservability.main:app", host="0.0.0.0", port=8002, reload=True)

if __name__ == "__main__":
    start()
