# Universal Dockerfile for Linux AIO Performance Checker
# Simplified approach based on original working Dockerfile
FROM python:3.14.2-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install graphviz and other OS-level packages
RUN apt-get update && \
    apt-get install -y graphviz curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the webapp directory contents into the container at /app
COPY webapp/ /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent

# Create upload directory with proper permissions for user 1000:1000
RUN mkdir -p /linuxaio/digest && \
    chmod 755 /linuxaio/digest && \
    chown 1000:1000 /linuxaio/digest

# Make port 80 available to the world outside this container
EXPOSE 80

# Set environment variables
ENV FLASK_ENV=production \
    UPLOAD_FOLDER=/linuxaio/digest \
    WORKERS=4 \
    TIMEOUT=300

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Command to run the application using gunicorn
# Azure will automatically set PORT environment variable
CMD ["sh", "-c", "gunicorn --bind=0.0.0.0:${PORT:-80} --workers=${WORKERS:-4} --worker-class=gevent --timeout=${TIMEOUT:-300} --access-logfile=- --error-logfile=- --log-level=info app:app"]