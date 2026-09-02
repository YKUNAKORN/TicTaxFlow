"""Shared Chroma retrieval for the tax knowledge base.

Single source of truth for the vector DB client and collection so agents
don't each open their own connection to the same persistent store.
"""
import logging

import chromadb

from app.core.config import settings

logger = logging.getLogger(__name__)

chroma_client = chromadb.PersistentClient(path=str(settings.EMBEDDINGS_DIR))
collection = chroma_client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)


def retrieve_context(query: str, n_results: int = None) -> list:
    """Query the vector database for relevant document chunks."""
    if n_results is None:
        n_results = settings.RAG_N_RESULTS

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        chunks = []
        if results.get("documents"):
            for doc_list in results["documents"]:
                chunks.extend(doc_list)

        return chunks

    except Exception as e:
        logger.error("Error retrieving context: %s", e)
        return []
