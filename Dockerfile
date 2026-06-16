FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY email_worker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY email_worker/ ./email_worker/
COPY email_worker/.env.example ./email_worker/.env

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Create data directory for message store
RUN mkdir -p /home/appuser/data

CMD ["python", "-m", "email_worker.main"]