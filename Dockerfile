
FROM python:3.12-slim

WORKDIR /app

# Install system libraries required by PaddleOCR and PaddlePaddle
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libgl1 \
    libstdc++6 \
    libgcc-s1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# FastAPI port
EXPOSE 8000

# Start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
