"""Scoped Level 1 cases: controlled candidates, real retrieval selection logic.

No embedding model, FAISS index or network is loaded. These cases check selection
and source integrity, not semantic relevance to a user's question.
"""
from types import SimpleNamespace

import numpy as np

from rag_traffic.retriever import VectorRetriever


def chunk(identity, article, content):
    return {
        'chunk_id': identity, 'document_id': 'DOC-DEMO',
        'document_id_source': 'header', 'title': 'Tài liệu thử nghiệm',
        'article': article, 'source_file': 'fixture.docx',
        'content': content, 'content_sha256': identity,
    }


def controlled_retriever(chunks, scores):
    """Replace only embedding/FAISS I/O; retain VectorRetriever.search itself."""
    calls = {'encode': 0, 'search': 0}

    def encode(*args, **kwargs):
        calls['encode'] += 1
        return np.array([[1.0, 0.0]], dtype=np.float32)

    def search(vector, limit):
        calls['search'] += 1
        return (np.array([scores[:limit]], dtype=np.float32),
                np.array([list(range(min(limit, len(chunks))))], dtype=np.int64))

    retriever = VectorRetriever.__new__(VectorRetriever)
    retriever.chunks = chunks
    retriever.manifest = {'query_prefix': 'query: '}
    retriever.model = SimpleNamespace(encode=encode)
    retriever.index = SimpleNamespace(search=search)
    return retriever, calls


def assert_source_integrity(results, chunks):
    """Shared assertions, independent of a particular question or scenario."""
    by_id = {item['chunk_id']: item for item in chunks}
    assert [item.rank for item in results] == list(range(1, len(results) + 1))
    assert {item.chunk_id for item in results} <= by_id.keys()
    for item in results:
        source = by_id[item.chunk_id]
        for field in ('content', 'document_id', 'article', 'source_file', 'title', 'document_id_source'):
            assert getattr(item, field) == source[field]


def test_returns_only_two_eligible_sources_when_k_is_six():
    chunks = [chunk('A', 'Điều 1', 'Nội dung A'),
              chunk('B', 'Điều 2', 'Nội dung B'),
              chunk('C', 'Điều 3', 'Nội dung C dưới ngưỡng')]
    retriever, _ = controlled_retriever(chunks, [0.90, 0.80, 0.40])
    results = retriever.search('Câu hỏi thử nghiệm', k=6, min_score=0.55)
    assert len(results) == 2
    assert {item.chunk_id for item in results} == {'A', 'B'}
    assert len(results) <= 6
    assert all(item.score >= 0.55 for item in results)
    assert_source_integrity(results, chunks)


def test_returns_empty_when_no_candidate_meets_threshold():
    chunks = [chunk('A', 'Điều 1', 'A'), chunk('B', 'Điều 2', 'B')]
    retriever, _ = controlled_retriever(chunks, [0.50, 0.40])
    assert retriever.search('Câu hỏi thử nghiệm', k=6, min_score=0.55) == []


def test_keeps_complementary_chunks_from_the_same_article():
    chunks = [chunk('A', 'Điều 11', 'Khoảng cách trong điều kiện khô ráo.'),
              chunk('B', 'Điều 11', 'Điều kiện bổ sung khi trời mưa.')]
    retriever, _ = controlled_retriever(chunks, [0.90, 0.80])
    results = retriever.search('Câu hỏi cần cả hai đoạn', k=6, min_score=0.55)
    assert {'A', 'B'} <= {item.chunk_id for item in results}
    assert_source_integrity(results, chunks)


def test_collapses_copies_with_only_whitespace_differences():
    chunks = [chunk('A', 'Điều 11', 'Điều kiện khi trời mưa.'),
              chunk('B', 'Điều 11', '  Điều kiện\nkhi  trời mưa.\t'),
              chunk('C', 'Điều 12', 'Căn cứ khác.')]
    chunks[1]['source_file'] = 'copy.pdf'
    retriever, _ = controlled_retriever(chunks, [0.90, 0.85, 0.80])
    results = retriever.search('Câu hỏi thử nghiệm', k=2, min_score=0.55)
    assert [item.chunk_id for item in results] == ['A', 'C']
    assert_source_integrity(results, chunks)


def test_preserves_identical_text_from_different_documents():
    chunks = [chunk('A', 'Điều 1', 'Cùng nội dung.'),
              chunk('B', 'Điều 1', 'Cùng nội dung.')]
    chunks[1]['document_id'] = 'OTHER-DOC'
    retriever, _ = controlled_retriever(chunks, [0.90, 0.80])
    results = retriever.search('Câu hỏi thử nghiệm', k=6, min_score=0.55)
    assert [item.chunk_id for item in results] == ['A', 'B']
    assert_source_integrity(results, chunks)


def test_idp_alias_expansion_preserves_question_and_is_idempotent():
    from rag_traffic.retriever import retrieval_query
    for alias in ['Bằng lái quốc tế', 'Bằng lái xe quốc tế', 'GPLX quốc tế', 'Giấy phép lái xe quốc tế']:
        result = retrieval_query(alias + ' bị mất có cấp lại không?')
        assert result == 'giấy phép lái xe quốc tế IDP bị mất có cấp lại không?'
        assert retrieval_query(result) == result


def test_foreign_and_domestic_licenses_are_not_inferred_to_be_idp():
    from rag_traffic.retriever import retrieval_query
    for query in ['Bằng lái nước ngoài bị mất', 'Bằng lái Việt Nam bị mất', 'Tôi cần cấp lại IDP']:
        assert retrieval_query(query) == query
