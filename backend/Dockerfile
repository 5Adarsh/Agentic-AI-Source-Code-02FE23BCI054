# =============================================================================
# Backend Dockerfile — multi-stage build
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: builder — install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Install system build dependencies (needed for psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements first so Docker layer cache works efficiently
COPY requirements.txt .

# Install all Python packages into /install (isolated from system Python)
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: runtime — lean final image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Runtime system libraries only (libpq for psycopg2 at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Default production command (override in docker-compose for --reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
