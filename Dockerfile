FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling python packages if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    psycopg2-binary \
    python-dotenv

# Copy application source directories and static frontend resources
COPY backend/ ./backend/
COPY index.html ./
COPY style_v4.css ./
COPY app_v4.js ./
COPY course_standardization_map.json ./
COPY seat_matrix_data_2026.json ./
COPY seat_matrix_data.json ./
COPY seat_matrix_data_2024.json ./

# Expose backend port
EXPOSE 8000

# Set environment defaults
ENV PORT=8000
ENV DB_HOST=db
ENV DB_PORT=5432
ENV DB_NAME=kcet
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres

# Run server using Uvicorn
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
