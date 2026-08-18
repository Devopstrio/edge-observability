import pytest
from httpx import AsyncClient, ASGITransport
from edgeobservability.main import app

@pytest.mark.asyncio
async def test_ingest_metrics_and_export() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Post Metrics
        payload = {
            "node_id": "factory-cam-01",
            "factory_location": "detroit-a",
            "system_metrics": {
                "cpu_usage_percent": 45.5,
                "ram_usage_bytes": 1024000,
                "disk_usage_bytes": 500000
            },
            "inference_metrics": [
                {
                    "model_name": "defect-detection-v2",
                    "inference_count": 1,
                    "latency_ms": 150.5,
                    "success": True
                }
            ]
        }
        post_resp = await ac.post("/api/v1/telemetry/metrics", json=payload)
        assert post_resp.status_code == 200
        assert post_resp.json() == {"status": "metrics_ingested"}
        
        # 2. Verify Prometheus Exporter
        get_resp = await ac.get("/metrics")
        assert get_resp.status_code == 200
        metrics_text = get_resp.text
        
        # Check if the metrics are correctly exposed
        assert 'edge_node_cpu_usage_percent{factory_location="detroit-a",node_id="factory-cam-01"} 45.5' in metrics_text
        assert 'edge_inference_total_total{factory_location="detroit-a",model_name="defect-detection-v2",node_id="factory-cam-01",status="success"} 1.0' in metrics_text

@pytest.mark.asyncio
async def test_ingest_logs() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "node_id": "factory-cam-02",
            "level": "ERROR",
            "message": "Camera thermal runaway detected",
            "context": {
                "temperature_celsius": 85.0
            }
        }
        post_resp = await ac.post("/api/v1/telemetry/logs", json=payload)
        assert post_resp.status_code == 200
        assert post_resp.json() == {"status": "logs_ingested"}
