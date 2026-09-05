"""Shared Chroma retrieval for the tax knowledge base.

Single source of truth for the vector DB client and collection so agents
don't each open their own connection to the same persistent store.
"""
import logging

import chromadb

from app.core.config import settings
from app.services import embeddings

logger = logging.getLogger(__name__)

chroma_client = chromadb.PersistentClient(path=str(settings.EMBEDDINGS_DIR))
_collection = None


def get_collection():
    """Return the shared collection, bound to the pinned embedding
    function. Built lazily (not at import time) so importing this module
    never forces an embedding model load - that cost lands on the first
    real retrieve_context() call instead.
    """
    global _collection
    if _collection is None:
        _collection = chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embeddings.get_embedding_function(),
        )
    return _collection


def retrieve_context(query: str, n_results: int = None) -> list:
    """Query the vector database for relevant document chunks.

    Returns [] both when the knowledge base genuinely has no match and
    when the embedding/query call itself fails - the two are distinguished
    in the logs (INFO vs ERROR), not in the return value, so callers keep
    treating [] as "no context" either way.
    """
    if n_results is None:
        n_results = settings.RAG_N_RESULTS

    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
    except Exception as e:
        logger.error("retrieve_context: query failed (embedding or DB error): %s", e, exc_info=True)
        return []

    chunks = []
    if results.get("documents"):
        for doc_list in results["documents"]:
            chunks.extend(doc_list)

    if not chunks:
        logger.info("retrieve_context: no matching chunks found (empty result, not an error)")

    return chunks
