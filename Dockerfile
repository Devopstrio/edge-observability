FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY src/ src/

# Expose Telemetry and Prometheus ports
EXPOSE 8002

CMD ["uvicorn", "edgeobservability.main:app", "--host", "0.0.0.0", "--port", "8002"]
