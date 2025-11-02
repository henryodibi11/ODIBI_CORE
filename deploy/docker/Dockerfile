# ODIBI CORE - Multi-stage Docker Build
# Optimized for LearnODIBI Studio (Streamlit UI)

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml setup.py README.md ./
COPY requirements.txt ./

# Install dependencies to /install directory
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install \
    pandas>=1.5.0 \
    typing-extensions>=4.0.0 \
    click>=8.0.0 \
    rich>=13.0.0 \
    streamlit>=1.30.0 \
    plotly>=5.18.0 \
    watchdog>=4.0.0 \
    duckdb>=0.9.0 \
    iapws>=1.5.0

# ============================================
# Stage 2: Runtime - Minimal production image
# ============================================
FROM python:3.10-slim

# Add metadata
LABEL maintainer="Henry Odibi <henry@odibi.com>"
LABEL description="ODIBI CORE - Node-centric, engine-agnostic data engineering framework with LearnODIBI Studio"
LABEL version="1.1.0"

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash odibi && \
    mkdir -p /app /data /logs && \
    chown -R odibi:odibi /app /data /logs

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=odibi:odibi odibi_core/ ./odibi_core/
COPY --chown=odibi:odibi pyproject.toml setup.py README.md ./
COPY --chown=odibi:odibi examples/ ./examples/

# Install ODIBI CORE in production mode
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER odibi

# Expose Streamlit port
EXPOSE 8501

# Health check - verify Streamlit is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Default command: Run LearnODIBI Studio
CMD ["streamlit", "run", "odibi_core/learnodibi_ui/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
