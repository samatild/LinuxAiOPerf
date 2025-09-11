# Universal Dockerfile for Linux AIO Performance Checker
# Works for both local development and Azure Web App deployment
# Stage 1: Build stage
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        graphviz-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir gunicorn gevent

# Stage 2: Runtime stage
FROM python:3.11-slim-bookworm AS runtime

# Set environment variables with Azure compatibility
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    FLASK_APP=app.py \
    PATH="/opt/venv/bin:$PATH" \
    UPLOAD_FOLDER=/linuxaio/digest \
    WORKERS=4 \
    TIMEOUT=300 \
    PORT=80 \
    AZURE_MODE=false

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        graphviz \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create directories for both local and Azure deployment
RUN mkdir -p /linuxaio/digest /home/site/wwwroot/digest /app

# Create non-root user for local development
RUN groupadd -r linuxaio && useradd -r -g linuxaio linuxaio

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Set permissions for both local and Azure modes
RUN chmod -R 755 /app && \
    chmod -R 755 /linuxaio && \
    chmod -R 755 /home/site/wwwroot

# Expose port
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Universal startup script that adapts to environment
COPY <<EOF /app/start.sh
#!/bin/bash

# Detect if running in Azure (Azure sets WEBSITE_SITE_NAME)
if [ -n "\$WEBSITE_SITE_NAME" ] || [ "\$AZURE_MODE" = "true" ]; then
    echo "Starting in Azure Web App mode..."
    # Azure-specific settings
    export UPLOAD_FOLDER="/home/site/wwwroot/digest"
    export WORKERS=\${WORKERS:-2}
    export PORT=\${PORT:-80}
    # Run as root (Azure requirement)
    exec gunicorn --bind=0.0.0.0:\$PORT --workers=\$WORKERS --worker-class=gevent --timeout=\${TIMEOUT:-300} --access-logfile=- --error-logfile=- --log-level=info app:app
else
    echo "Starting in local development mode..."
    # Local development settings
    export UPLOAD_FOLDER="/linuxaio/digest"
    export WORKERS=\${WORKERS:-4}
    export PORT=\${PORT:-80}
    # Run as non-root user for security
    exec gunicorn --bind=0.0.0.0:\$PORT --workers=\$WORKERS --worker-class=gevent --timeout=\${TIMEOUT:-300} --access-logfile=- --error-logfile=- --log-level=info app:app
fi
EOF

RUN chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]