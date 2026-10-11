from evals.tracking import version_metadata


def test_fingerprints_uncommitted_source_without_reading_env(tmp_path):
    source = tmp_path / 'rag_traffic'
    source.mkdir()
    code = source / 'retriever.py'
    code.write_text('version = 1\n')
    (tmp_path / '.env').write_text('OPENAI_API_KEY=sentinel-secret\n')
    before = version_metadata(tmp_path)
    code.write_text('version = 2\n')
    after = version_metadata(tmp_path)
    assert before['source_sha256']['rag_traffic/retriever.py'] != after['source_sha256']['rag_traffic/retriever.py']
    assert '.env' not in after['source_sha256']
    assert 'sentinel-secret' not in str(after)


def test_failed_run_is_saved_and_returns_failure(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    from evals import run_tests

    monkeypatch.setattr(run_tests, 'ROOT', tmp_path)
    monkeypatch.setattr(run_tests, 'version_metadata', lambda: {'test_version': 'fixture'})
    def fail(command, **kwargs):
        kwargs['stdout'].write('FAILED example test\n')
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(run_tests.subprocess, 'run', fail)
    assert run_tests.main() == 1
    manifest = next((tmp_path / 'evals/runs').glob('*/tests.json'))
    report = json.loads(manifest.read_text())
    assert report['status'] == 'failed'
    assert report['exit_code'] == 1
    assert 'FAILED' in (manifest.parent / 'pytest.txt').read_text()
