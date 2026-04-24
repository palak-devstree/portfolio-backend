FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies directly with pip (faster than Poetry for Docker builds)
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    email-validator==2.1.0 \
    sqlalchemy==2.0.23 \
    alembic==1.12.1 \
    asyncpg==0.29.0 \
    redis==5.0.1 \
    structlog==23.2.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    google-generativeai==0.3.2 \
    openai==1.3.9 \
    PyGithub==2.1.1 \
    httpx==0.25.2 \
    cloudinary==1.36.0 \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0 \
    pyyaml==6.0.1 \
    bleach==6.1.0

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
