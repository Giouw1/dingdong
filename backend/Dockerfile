
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered real-time logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Create database directory for SQLite storage
RUN mkdir -p /app/databases

# 3. Copy application code
COPY ./app ./app
COPY ./configs ./configs
COPY ./frontend ./frontend
COPY main.py .

# 4. Declare volume mount point for persistent data
VOLUME ["/app/databases"]

EXPOSE 8000

CMD ["python", "main.py"]
