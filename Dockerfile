FROM python:3.12-slim

# Install system dependencies including FFmpeg for video conversion
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

RUN pip install --no-cache-dir fastapi fastapi-htmx pydantic uvicorn

# Copy the application code
COPY survin/ ./survin/
COPY pyproject.toml .

# Install the package in development mode
#RUN pip install -e .

# Expose the port
EXPOSE 8000

# Create directories for mounts
RUN mkdir -p /app/snapshots

# Run the application
CMD ["python", "-m", "uvicorn", "survin.app:app", "--host", "0.0.0.0", "--port", "8000"]
