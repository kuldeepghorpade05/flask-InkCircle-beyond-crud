# official Python image
FROM python:3.12-slim

# working directory inside the container
WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first (for caching)
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry (fixed for v1.5+)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# Copy project source code
COPY ./src ./src
COPY ./celery_tasks.py .
COPY ./run.py .

# Default command to run Flask server
CMD ["python", "run.py"]