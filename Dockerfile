# STAGE 1: BUILDER
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy dependency file first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# STAGE 2: RUNTIME
FROM python:3.11-slim

# Set UTC timezone (CRITICAL REQUIREMENT)
ENV TZ=UTC

WORKDIR /app

# Update & install system dependencies
RUN apt-get update && \apt-get install -y --no-install-recommends \cron \tzdata \&& rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app.py .
COPY crypto_utils.py .
COPY totp_utils.py .

# Copy keys
COPY student_private.pem .
COPY instructor_public.pem .

# Copy cron job & script (you will add these next step)
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY cron/cron_logger.sh /cron/cron_logger.sh

# Set permissions for cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    chmod +x /cron/cron_logger.sh && \
    crontab /etc/cron.d/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose correct port (per spec)
EXPOSE 8080

# Start BOTH cron + API server
CMD service cron start && \
    uvicorn app:app --host 0.0.0.0 --port 8080
