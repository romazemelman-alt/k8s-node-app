# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .

# Install dependencies to a local user directory
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Final minimal runtime image ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY app/app.py .

# Expose local environment variables for the user binary path
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Security Best Practice: Run container processes as a non-privileged user (non-root)
USER 10001

EXPOSE 8080

CMD ["python", "app.py"]