# Use a slim Python image to reduce container size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy env file (required for load_dotenv to work)
COPY .env .env

# Create necessary directories
RUN mkdir -p /app/static /app/templates

# Copy application files
COPY . /app

# Copy static and template files
COPY static/ /app/static/
COPY templates/ /app/templates/

# Environment variables for FastAPI & Cloud Run
ENV PORT=8080
EXPOSE 8080

# ✅ Run init_db and start the app 
CMD sh -c "python scripts/init_db.py && uvicorn main:app --host 0.0.0.0 --port 8080"

