from rag_traffic.generation import evidence_only_answer
from rag_traffic.retriever import SearchResult


def test_evidence_only_answer_uses_source_rank() -> None:
    result = SearchResult(
        rank=1,
        score=0.8,
        chunk_id="x",
        document_id="01/2024/TT-BGTVT",
        document_id_source="header",
        title="Văn bản thử nghiệm",
        article="Điều 1. Phạm vi",
        source_file="document.docx",
        content="Nội dung làm căn cứ.",
    )
    answer = evidence_only_answer([result])
    assert "[1] Điều 1. Phạm vi" in answer
    assert "đối chiếu toàn văn" in answer


def _source() -> SearchResult:
    return SearchResult(
        rank=1, score=0.8, chunk_id="fixture", document_id="DOC",
        document_id_source="header", title="Nguồn thử nghiệm",
        article="Điều 1", source_file="fixture.docx", content="Căn cứ thử nghiệm.",
    )


def test_generation_calls_openai_with_sources_and_history(monkeypatch) -> None:
    import httpx
    import rag_traffic.generation as generation

    def post(url, *, headers, json, timeout):
        assert url == "https://api.openai.com/v1/chat/completions"
        assert headers["Authorization"] == "Bearer test-key"
        assert json["model"] == "gpt-5.4-mini"
        assert "Căn cứ thử nghiệm." in json["messages"][1]["content"]
        assert "Câu hỏi trước" in json["messages"][1]["content"]
        return httpx.Response(200, request=httpx.Request("POST", url), json={
            "choices": [{"message": {"content": " Trả lời có căn cứ [1]. "}}]
        })

    monkeypatch.setattr(generation.httpx, "post", post)
    assert generation.generate_answer(
        "Câu hỏi mới", [_source()], "test-key", "gpt-5.4-mini",
        [("Câu hỏi trước", "Trả lời trước")],
    ) == ("Trả lời có căn cứ [1].", "rag")


def test_generation_without_key_does_not_call_network(monkeypatch) -> None:
    import rag_traffic.generation as generation

    def unexpected(*args, **kwargs):
        raise AssertionError("Không được gọi mạng khi thiếu key")

    monkeypatch.setattr(generation.httpx, "post", unexpected)
    answer, mode = generation.generate_answer("Câu hỏi", [_source()], None, "gpt-5.4-mini")
    assert mode == "evidence_only"
    assert "[1]" in answer


def test_openai_errors_and_empty_content_fall_back(monkeypatch) -> None:
    import httpx
    import rag_traffic.generation as generation

    for status, body in [
        (401, {"error": {"message": "Invalid API key"}}),
        (429, {"error": {"message": "Rate limited"}}),
        (200, {"choices": [{"message": {"content": None}}]}),
        (200, {"choices": [{"message": {"content": " "}}]}),
    ]:
        def post(url, **kwargs):
            return httpx.Response(status, request=httpx.Request("POST", url), json=body)

        monkeypatch.setattr(generation.httpx, "post", post)
        answer, mode = generation.generate_answer("Câu hỏi", [_source()], "test-key", "gpt-5.4-mini")
        assert mode == "evidence_only"
        assert "[1]" in answer
        assert "Không gọi được mô hình" in answer
        assert "test-key" not in answer
