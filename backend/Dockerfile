FROM python:3.11-slim

WORKDIR /app

# Install dependencies first to take advantage of Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Build the RAG index and cache its embedding model into this image layer,
# at build time - not lazily on the container's first query. backend/data/
# embeddings is gitignored (rebuildable, not committed - see .gitignore),
# so every image must run this itself from the committed source PDFs.
# (main.py forces HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE at app startup, so
# runtime never depends on reaching Hugging Face again after this step.)
RUN python -m app.services.document_indexer

ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8000

# Run with uvicorn. Use --reload for easier testing; remove for production.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
