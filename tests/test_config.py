from secondsmatter.config import LLM_MODEL, get_settings


def test_missing_or_blank_api_key_is_reported(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  ")

    settings = get_settings()

    assert settings.llm_model == LLM_MODEL
    assert settings.has_api_key is False


def test_api_key_is_detected_but_not_stored(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    settings = get_settings()

    assert settings.has_api_key is True
    assert "test-key-not-real" not in repr(settings)
