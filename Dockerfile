# =============================================
# Stage 1: Builder
# =============================================
FROM python:3.12-slim AS builder

# Install system dependencies required for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY app/requirements.txt .

# Install dependencies 
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# =============================================
# Stage 2: Runtime (Final Image)
# =============================================
FROM python:3.12-slim AS runtime

# Create non-root user
RUN useradd -m -r -u 1001 appuser

# Create working directory
WORKDIR /app

# Copy wheels and install 
COPY --from=builder /wheels /wheels 
RUN pip install --no-cache /wheels/* 

# Copy application code
COPY app/ .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port your app runs on
EXPOSE 5000

CMD ["python", "wait_for_mongo.py"]

