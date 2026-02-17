# Dockerfile - แก้ไขเพิ่ม error handling
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python packages with timeout
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout 300 -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p models data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run with proper logging
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
