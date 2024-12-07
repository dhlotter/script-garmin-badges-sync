# Build stage
FROM python:3.11-alpine as builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

# Create and work in /app
WORKDIR /app

# Copy only the requirements first
COPY requirements.txt .

# Create venv and install dependencies
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache openssl ca-certificates

# Copy virtual env from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user and data directory
RUN adduser -D appuser && \
    mkdir -p /home/appuser/data/.garth /home/appuser/data/.garminbadges && \
    chown -R appuser:appuser /home/appuser

# Set working directory
WORKDIR /app

# Copy only the necessary files
COPY sync.py .

# Use non-root user
USER appuser

# Set Python path to use venv
ENV PATH="/opt/venv/bin:$PATH"

# Run script
CMD ["python", "sync.py"]
