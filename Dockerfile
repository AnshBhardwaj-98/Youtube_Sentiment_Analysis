# Use official slim Python image
FROM python:3.10-slim

# Avoid Python buffering & bytecode files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Suppress TensorFlow logs
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV TF_ENABLE_ONEDNN_OPTS=0

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose Flask port
EXPOSE 5000

# Run app with Gunicorn (production)
# 2 workers to reduce memory usage
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120", "--log-level", "info"]
