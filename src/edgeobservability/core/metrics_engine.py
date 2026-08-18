from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram

# Central isolated registry so we don't pollute the global python runtime registry in tests
REGISTRY = CollectorRegistry(auto_describe=True)

EDGE_CPU_USAGE = Gauge(
    "edge_node_cpu_usage_percent",
    "Current CPU utilization of the Edge Node",
    ["node_id", "factory_location"],
    registry=REGISTRY
)

EDGE_RAM_USAGE = Gauge(
    "edge_node_ram_usage_bytes",
    "Current RAM utilization of the Edge Node in bytes",
    ["node_id", "factory_location"],
    registry=REGISTRY
)

EDGE_INFERENCE_COUNT = Counter(
    "edge_inference_total",
    "Total number of inferences executed",
    ["node_id", "factory_location", "model_name", "status"],
    registry=REGISTRY
)

EDGE_INFERENCE_LATENCY = Histogram(
    "edge_inference_latency_ms",
    "Latency of model inferences in milliseconds",
    ["node_id", "factory_location", "model_name"],
    buckets=(10.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0),
    registry=REGISTRY
)
