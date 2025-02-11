# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5003

# Set work directory
WORKDIR /app

# Install system dependencies and datalake requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the application with Gunicorn
CMD gunicorn --bind 0.0.0.0:${PORT} \
    --workers=4 \
    --threads=4 \
    --worker-class=gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile=- \
    --error-logfile=- \
    "app:create_app()" 