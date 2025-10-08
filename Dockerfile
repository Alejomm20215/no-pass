# Multi-stage Docker build for PDF Password Recovery Tools

# Stage 1: Builder (for installing Python dependencies)
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Install PyInstaller for building the CLI executable
RUN pip install --no-cache-dir --user pyinstaller
# Ensure local bin (where --user installs CLIs) is on PATH in builder
ENV PATH="/root/.local/bin:${PATH}"

# Copy full source and build the CLI executable
COPY . .
RUN python -m PyInstaller --onefile --name pdf-password-tools scripts/cli_crack.py

# Stage 2: Runtime (minimal image for running the app)
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy the built CLI executable from builder stage
COPY --from=builder /app/dist/pdf-password-tools /usr/local/bin/pdf-password-tools

# Copy application code (for web server fallback)
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads data/outputs logs config/wordlists && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/home/appuser/.local/bin:/usr/local/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check using curl (no Python deps)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Default command for CLI tool (can be overridden for web server)
ENTRYPOINT ["pdf-password-tools"]
CMD ["--help"]
