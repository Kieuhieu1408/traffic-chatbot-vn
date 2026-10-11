import json
from dataclasses import replace
from unittest.mock import Mock

import pytest
from langsmith import Client

from rag_traffic.config import Settings
from rag_traffic import tracing


def settings(tmp_path, **overrides):
    return replace(Settings(tmp_path, tmp_path, tmp_path, 'unused', None,
                            'gpt-5.4-mini', 6, .55), **overrides)


def recorder(monkeypatch, tmp_path):
    client = tracing.Client(api_key='ls-test-secret', auto_batch_tracing=False)
    monkeypatch.setattr(Client, "create_run", Mock())
    monkeypatch.setattr(Client, "update_run", Mock())
    monkeypatch.setattr(Client, "flush", Mock())
    monkeypatch.setattr(tracing, 'Client', lambda **kwargs: client)
    service = tracing.ChatTracing(settings(tmp_path, langsmith_tracing=True,
                                           langsmith_api_key='ls-test-secret',
                                           openai_api_key='openai-test-secret'))
    return service, client


def test_nested_runs_include_evidence_history_and_no_credentials(monkeypatch, tmp_path):
    service, client = recorder(monkeypatch, tmp_path)
    source = Mock()
    source.to_dict.return_value = {'chunk_id': 'source-1', 'content': 'Căn cứ', 'rank': 1}
    retriever = Mock(manifest={'chunks_sha256': 'corpus-version'})
    retriever.search.return_value = [source]
    monkeypatch.setattr(tracing, 'generate_answer', lambda *args: ('Đáp án [1]', 'rag'))
    answer, mode, sources, run_id = service.run(retriever, 'Câu hỏi', [('q', 'a')], 'session-1')
    assert (answer, mode) == ('Đáp án [1]', 'rag')
    creates = [c.kwargs for c in Client.create_run.call_args_list]
    updates = [c.kwargs for c in Client.update_run.call_args_list]
    assert [c['name'] for c in creates] == ['rag-traffic-chat', 'retrieve-sources', 'generate-answer']
    root, retrieval, generation = creates
    assert str(root['id']) == run_id
    assert retrieval['parent_run_id'] == generation['parent_run_id'] == root['id']
    assert root['extra']['metadata']['session_id'] == 'session-1'
    assert generation['inputs']['history_used'] == [('q', 'a')]
    assert generation['inputs']['sources'] == sources
    assert any(u.get('outputs', {}).get('answer') == answer for u in updates)
    payload = json.dumps([creates, updates], default=str)
    assert 'ls-test-secret' not in payload
    assert 'openai-test-secret' not in payload
    service.close()
    client.flush.assert_called_once()


@pytest.mark.parametrize('enabled,status', [(False, 'disabled'), (True, 'missing_api_key')])
def test_disabled_or_missing_key_keeps_chat_working(monkeypatch, tmp_path, enabled, status):
    monkeypatch.setattr(tracing, 'Client', Mock(side_effect=AssertionError('Unexpected client')))
    service = tracing.ChatTracing(settings(tmp_path, langsmith_tracing=enabled))
    retriever = Mock(manifest={})
    retriever.search.return_value = []
    answer, mode, sources, run_id = service.run(retriever, 'Không có nguồn', [], 's')
    assert service.status == status
    assert mode == 'evidence_only' and sources == [] and run_id is None


def test_retrieval_failure_is_traced_and_propagated(monkeypatch, tmp_path):
    service, client = recorder(monkeypatch, tmp_path)
    retriever = Mock(manifest={})
    retriever.search.side_effect = ValueError('broken index')
    with pytest.raises(ValueError, match='broken index'):
        service.run(retriever, 'Câu hỏi', [], 's')
    assert any('broken index' in (c.kwargs.get('error') or '')
               for c in Client.update_run.call_args_list)


def test_upload_failure_does_not_break_answer(monkeypatch, tmp_path):
    service, client = recorder(monkeypatch, tmp_path)
    Client.create_run.side_effect = RuntimeError('LangSmith unavailable')
    Client.update_run.side_effect = RuntimeError('LangSmith unavailable')
    retriever = Mock(manifest={})
    retriever.search.return_value = []
    monkeypatch.setattr(tracing, 'generate_answer', lambda *args: ('Fallback', 'evidence_only'))
    assert service.run(retriever, 'Câu hỏi', [], 's')[:2] == ('Fallback', 'evidence_only')


def test_api_traces_each_turn_and_keeps_session_history(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import create_app
    service, client = recorder(monkeypatch, tmp_path)
    retriever = Mock(manifest={})
    retriever.search.return_value = []
    monkeypatch.setattr(tracing, 'generate_answer', lambda *args: ('Đáp án', 'evidence_only'))
    app = create_app(service.settings)
    with TestClient(app) as web:
        app.state.retriever = retriever
        first = web.post('/search', json={'query': 'Câu đầu'}).json()
        second = web.post('/search', json={'query': 'Câu tiếp', 'session_id': first['session_id']}).json()
        assert first['trace_id'] != second['trace_id']
        assert first['session_id'] == second['session_id']
    roots = [c.kwargs for c in Client.create_run.call_args_list if c.kwargs['name'] == 'rag-traffic-chat']
    assert roots[1]['inputs']['history'] == [('Câu đầu', 'Đáp án')]
    assert roots[1]['extra']['metadata']['session_id'] == first['session_id']
