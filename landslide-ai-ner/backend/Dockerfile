FROM python:3.11-slim

# ── Build arguments ──────────────────────────────────────
ARG APP_ENV=production
ARG BUILD_DATE
ARG VCS_REF

# ── Labels ───────────────────────────────────────────────
LABEL maintainer="Landslide NER Team" \
      org.label-schema.name="landslide-ai-ner-backend" \
      org.label-schema.description="AI-Based Landslide Risk Monitoring — FastAPI Backend" \
      org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.schema-version="1.0"

# ── Environment ───────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    APP_ENV=${APP_ENV} \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── System dependencies ───────────────────────────────────
# libpq-dev  : PostgreSQL client library headers
# gcc        : C compiler for native extensions
# libgdal-dev: GDAL for geospatial processing
# gdal-bin   : GDAL command-line utilities
# libgeos-dev: Geometry engine for Shapely
# libproj-dev: PROJ cartographic library
# curl       : Health-check utility
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    g++ \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ── GDAL environment variables ────────────────────────────
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1

# ── Working directory ─────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ───────────────────────────
# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ─────────────────────────────────
COPY . .

# ── Create required directories ───────────────────────────
RUN mkdir -p /app/media/uploads \
             /app/media/exports \
             /app/data/models \
             /app/data/raw \
             /app/logs

# ── Non-root user for security ────────────────────────────
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

# ── Health check ─────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ── Expose port ───────────────────────────────────────────
EXPOSE 8000

# ── Default command ───────────────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--log-level", "info"]
