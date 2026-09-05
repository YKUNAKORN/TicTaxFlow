"""retrieve_context: query result shaping, and making a genuinely empty
knowledge base distinguishable in the logs from an embedding/query failure
(both must still return [] to callers - agents treat [] as "no context" -
but only one of them is an error worth paging someone about on demo day).

Also guards the property the whole RAG fix depends on: document_indexer
(build time) and retrieval (query time) must build their collection with
the exact same embedding function. A mismatch doesn't raise - it just
returns wrong nearest-neighbours, because the two sides land in different
vector spaces.
"""
import logging
from unittest.mock import MagicMock, patch

from app.services import retrieval


def _fake_collection(query_return=None, query_side_effect=None):
    collection = MagicMock()
    if query_side_effect is not None:
        collection.query.side_effect = query_side_effect
    else:
        collection.query.return_value = query_return
    return collection


def test_retrieve_context_flattens_documents_from_query_result():
    fake = _fake_collection(query_return={"documents": [["chunk a", "chunk b"]]})
    with patch.object(retrieval, "get_collection", return_value=fake):
        chunks = retrieval.retrieve_context("deductible donations", n_results=2)

    assert chunks == ["chunk a", "chunk b"]
    fake.query.assert_called_once_with(query_texts=["deductible donations"], n_results=2)


def test_retrieve_context_empty_result_logs_info_not_error(caplog):
    fake = _fake_collection(query_return={"documents": [[]]})
    with patch.object(retrieval, "get_collection", return_value=fake), \
         caplog.at_level(logging.INFO, logger="app.services.retrieval"):
        chunks = retrieval.retrieve_context("no such topic")

    assert chunks == []
    assert any(r.levelno == logging.INFO for r in caplog.records)
    assert not any(r.levelno >= logging.ERROR for r in caplog.records)


def test_retrieve_context_query_failure_logs_error_and_returns_empty(caplog):
    fake = _fake_collection(query_side_effect=RuntimeError("embedding model unavailable"))
    with patch.object(retrieval, "get_collection", return_value=fake), \
         caplog.at_level(logging.INFO, logger="app.services.retrieval"):
        chunks = retrieval.retrieve_context("deductible donations")

    assert chunks == []
    assert any(r.levelno == logging.ERROR for r in caplog.records)


def test_retrieve_context_error_and_empty_logs_are_distinguishable(caplog):
    empty = _fake_collection(query_return={"documents": [[]]})
    with patch.object(retrieval, "get_collection", return_value=empty), \
         caplog.at_level(logging.INFO, logger="app.services.retrieval"):
        retrieval.retrieve_context("q1")
    empty_messages = {r.getMessage() for r in caplog.records}
    caplog.clear()

    broken = _fake_collection(query_side_effect=RuntimeError("boom"))
    with patch.object(retrieval, "get_collection", return_value=broken), \
         caplog.at_level(logging.INFO, logger="app.services.retrieval"):
        retrieval.retrieve_context("q1")
    error_messages = {r.getMessage() for r in caplog.records}

    assert empty_messages.isdisjoint(error_messages)


def test_indexer_and_retrieval_build_collection_with_same_embedding_function():
    from app.services import document_indexer

    sentinel = object()
    with patch("app.services.embeddings.get_embedding_function", return_value=sentinel), \
         patch.object(retrieval, "_collection", None), \
         patch.object(document_indexer, "_collection", None), \
         patch.object(retrieval.chroma_client, "get_or_create_collection") as retrieval_get, \
         patch.object(document_indexer.chroma_client, "get_or_create_collection") as indexer_get, \
         patch.object(document_indexer.chroma_client, "delete_collection"):
        retrieval.get_collection()
        document_indexer.get_collection()

    assert retrieval_get.call_args.kwargs["embedding_function"] is sentinel
    assert indexer_get.call_args.kwargs["embedding_function"] is sentinel
