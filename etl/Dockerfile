FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed by pymssql (freetds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    freetds-dev \
    freetds-bin \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL script
COPY etl_app.py .

# Run the ETL script (not a server — runs once and exits)
CMD ["python", "etl_app.py"]
