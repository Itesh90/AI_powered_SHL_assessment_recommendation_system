FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Create data directory
RUN mkdir -p backend/data

WORKDIR /app/backend

# Generate assessment data on build
RUN python crawler.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]