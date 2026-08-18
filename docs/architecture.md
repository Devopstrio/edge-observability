# Edge Observability Architecture

Because physical edge factories reside behind strict corporate firewalls, central cloud monitoring systems (like Prometheus) cannot initiate inbound TCP connections to scrape metrics. 

To bypass this, we use the **Edge Observability Gateway** as an inverted proxy. The Edge Nodes act as clients, establishing outbound connections to *push* data to this Gateway. The Gateway then holds this state in a centralized `prometheus_client` registry, which the cloud Prometheus TSDB can seamlessly scrape.

---

## High-Level Design (HLD)

```mermaid
graph TD
    classDef highContrast fill:#f4f4f4,stroke:#333,stroke-width:2px,color:#000000;
    
    EdgeA[Factory A Edge Nodes]:::highContrast
    EdgeB[Factory B Edge Nodes]:::highContrast
    
    Gateway[Edge Observability Gateway]:::highContrast
    
    Prometheus[(Prometheus TSDB)]:::highContrast
    Loki[(Loki Log Engine)]:::highContrast
    Grafana[Grafana Dashboards]:::highContrast
    
    EdgeA -->|Push Metrics & Logs| Gateway
    EdgeB -->|Push Metrics & Logs| Gateway
    
    Prometheus -->|Scrapes /metrics| Gateway
    Gateway -->|Forwards JSON logs| Loki
    
    Grafana -->|Queries| Prometheus
    Grafana -->|Queries| Loki
```

### HLD Component Details
1. **Edge Observability Gateway (FastAPI)**: The highly-available API layer that absorbs tens of thousands of metric payloads per second from edge nodes.
2. **Prometheus TSDB**: Periodically pulls the aggregated metrics from the Gateway.
3. **Grafana Dashboards**: Provides visual charts and alerting mechanics to the DevopsTrio network operations center (NOC).

---

## Low-Level Design (LLD) - Metrics Execution Flow

This sequence diagram details the precise execution path when an AI Model finishes an inference on the edge and reports its latency back to the central cloud.

```mermaid
sequenceDiagram
    autonumber
    
    participant EdgeNode as Edge Runtime (Factory)
    participant API as Telemetry API
    participant Registry as Prometheus Registry (Memory)
    participant Prom as Prometheus TSDB (Cloud)
    
    Note over EdgeNode, API: Push Phase
    EdgeNode->>EdgeNode: AI Model completes inference (150ms)
    EdgeNode->>API: POST /api/v1/telemetry/metrics (latency_ms=150)
    API->>Registry: EDGE_INFERENCE_LATENCY.observe(150)
    API->>Registry: EDGE_INFERENCE_COUNT.inc(1)
    API-->>EdgeNode: 200 OK (metrics_ingested)
    
    Note over Prom, API: Pull Phase (Every 15s)
    Prom->>API: GET /metrics
    API->>Registry: generate_latest()
    Registry-->>API: returns raw prometheus text output
    API-->>Prom: 200 OK (text/plain)
    Prom->>Prom: Index time-series data
```
