"""Embedding function shared by document_indexer (build time) and
retrieval (query time).

Chroma's default embedding function (all-MiniLM-L6-v2 ONNX) downloads its
weights from an S3 bucket the first time it's called, and is weak on Thai.
This pins an explicit multilingual SentenceTransformer instead so retrieval
never has a hidden runtime dependency on that bucket.

The model must already be present in the local sentence-transformers/HF
cache before this ever runs for real (see Dockerfile) - do not rely on
this reaching the network live during a demo.

index_documents() and retrieve_context() MUST use this exact same
embedding function. A mismatch does not raise - it silently returns wrong
nearest-neighbours, because the two sides land in different vector
spaces. If you change EMBEDDING_MODEL_NAME, re-run document_indexer to
rebuild backend/data/embeddings from scratch.
"""
import logging

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = logging.getLogger(__name__)

# Pinned: multilingual (incl. Thai), unlike Chroma's default English-only
# all-MiniLM-L6-v2. https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE = "cpu"

_embedding_function = None


def get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Build (once per process) the embedding function shared by the
    index and query paths. Lazy on purpose: importing this module (which
    happens on every app startup via the agent import chain) must not by
    itself force a model load - the cost should land on the first real
    index/query call, not on every process that merely imports retrieval.
    """
    global _embedding_function
    if _embedding_function is None:
        logger.info(
            "Loading embedding model %s (device=%s)",
            EMBEDDING_MODEL_NAME,
            EMBEDDING_DEVICE,
        )
        _embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME,
            device=EMBEDDING_DEVICE,
            normalize_embeddings=True,
        )
    return _embedding_function
