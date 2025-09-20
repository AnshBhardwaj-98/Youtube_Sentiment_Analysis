# Use official slim Python image (smaller)
FROM python:3.10-slim

# Avoid Python buffering (helps logs)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install OS packages needed for some python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching: only re-run pip when requirements change)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app code and model files
COPY . .

# Create a non-root user to run the app (better security)
RUN useradd --create-home appuser
USER appuser

EXPOSE 5000

# Run with Gunicorn (production WSGI server). Use 4 workers as a starting point.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
