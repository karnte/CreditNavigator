# ------------------------------------------------------------
# Backend Dockerfile (FastAPI + Vertex AI)
# ------------------------------------------------------------

# 1️⃣ Base image
FROM python:3.11-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Install system dependencies (for google-cloud libs)
RUN apt-get update && apt-get install -y \
    gcc curl && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy source code
COPY . .

# 6️⃣ Expose FastAPI port
EXPOSE 8000

# 7️⃣ Command to run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
