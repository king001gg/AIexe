from services.rag.chunker import chunk_text
from services.rag.retriever import BM25Index, tokenize


def test_chunk_text_splits_long_text():
    text = "字" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 3
    assert all(len(c) <= 500 for c in chunks)


def test_chunk_text_empty():
    assert chunk_text("") == []


def test_tokenize_cjk_uses_unigram_and_bigram():
    tokens = tokenize("你好世界")
    assert "你" in tokens
    assert "你好" in tokens


def test_bm25_retrieval_hits_relevant_doc():
    index = BM25Index()
    index.add("1", "Python", "Python 是一种流行的编程语言")
    index.add("2", "美食", "红烧肉是一道美味的菜肴")

    results = index.search("编程语言")

    assert results
    assert results[0]["id"] == "1"
