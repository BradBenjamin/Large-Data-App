# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build dependencies for packages like lightgbm if wheels are unavailable
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI and Streamlit ports
EXPOSE 8000 8501

# Default environment for local container deployment
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000

# Start both backend and frontend together
CMD ["python", "run_app.py"]
