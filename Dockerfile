# 1️⃣ Use official Python image
FROM python:3.12-slim

# 2️⃣ Set working directory inside the container
WORKDIR /app

# 3️⃣ Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Install Poetry
RUN pip install --no-cache-dir poetry

# 5️⃣ Copy dependency files first (for caching)
COPY pyproject.toml poetry.lock* ./

# 6️⃣ Install dependencies using Poetry (fixed for v1.5+)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# 7️⃣ Copy project source code
COPY ./src ./src
COPY ./celery_tasks.py .
COPY ./run.py .

# 8️⃣ Default command to run Flask server
CMD ["python", "run.py"]