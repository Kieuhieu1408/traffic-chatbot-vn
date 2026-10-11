from rag_traffic.config import Settings


def test_openai_configuration_and_default_model(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", " test-key ")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    settings = Settings.from_env()
    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "gpt-5.4-mini"
    monkeypatch.setenv("OPENAI_MODEL", "custom-model")
    assert Settings.from_env().openai_model == "custom-model"


def test_blank_openai_key_disables_generation(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "  ")
    assert Settings.from_env().openai_api_key is None
