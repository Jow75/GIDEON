# Use Debian slim base image as recommended
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (e.g. for audio/image processing libraries if needed)
# libportaudio2 is required for sounddevice
RUN apt-get update && \
    apt-get install -y --no-install-recommends libportaudio2 libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose API port
EXPOSE 8000

# Start Gideon
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
