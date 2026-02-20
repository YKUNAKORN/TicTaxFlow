FROM python:3.11-slim

WORKDIR /app

# Install dependencies first to take advantage of Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# Run with uvicorn. Use --reload for easier testing; remove for production.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
