# PathRAG with ArangoDB - Docker Image
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Add metadata
LABEL maintainer="PathRAG Team" \
      description="PathRAG with ArangoDB integration" \
      version="$VERSION" \
      build-date="$BUILD_DATE" \
      vcs-ref="$VCS_REF"

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r pathrag && useradd -r -g pathrag pathrag

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user
RUN groupadd -r pathrag && useradd -r -g pathrag pathrag

# Create application directories
RUN mkdir -p /app /app/data /app/logs /app/backups && \
    chown -R pathrag:pathrag /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=pathrag:pathrag . .

# Create necessary directories and set permissions
RUN mkdir -p data logs backups && \
    chown -R pathrag:pathrag /app && \
    chmod +x scripts/*.py 2>/dev/null || true

# Switch to non-root user
USER pathrag

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["python", "-m", "scripts.api_server"]

# Development stage (optional)
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    jupyter

# Switch back to pathrag user
USER pathrag

# Override command for development
CMD ["python", "-m", "scripts.api_server", "--debug"]