FROM python:3.11-slim

WORKDIR /app

# Install git (required by GitPython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy worker requirements
COPY apps/worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY apps/worker /app

# Copy shared packages
COPY packages /app/packages

ENV PYTHONPATH=/app

CMD ["python", "worker.py"]