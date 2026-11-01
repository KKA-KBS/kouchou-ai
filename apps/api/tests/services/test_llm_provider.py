from unittest.mock import patch

import pytest

from src.services.llm_provider import apply_server_llm_settings


@pytest.fixture
def aws_settings(test_settings):
    with (
        patch.object(test_settings, "DEFAULT_LLM_PROVIDER", "bedrock"),
        patch.object(test_settings, "LOCAL_LLM_ADDRESS", "http://litellm.internal:4000/v1"),
        patch.object(test_settings, "EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0"),
        patch("src.services.llm_provider.settings", test_settings),
    ):
        yield test_settings


def test_bedrock_ignores_values_from_the_screen(aws_settings):
    """画面の既定値（ollama のアドレスなど）が送られても、サーバーの設定で上書きする"""
    config = {
        "provider": "openai",
        "local_llm_address": "ollama:11434",
        "is_embedded_at_local": True,
        "embedding": {"model": "text-embedding-3-small"},
    }

    result = apply_server_llm_settings(config)

    assert result["provider"] == "bedrock"
    assert result["local_llm_address"] == "http://litellm.internal:4000/v1"
    assert result["is_embedded_at_local"] is False
    assert result["embedding"]["model"] == "amazon.titan-embed-text-v2:0"


def test_bedrock_requires_gateway_address(aws_settings):
    with patch.object(aws_settings, "LOCAL_LLM_ADDRESS", None):
        with pytest.raises(ValueError):
            apply_server_llm_settings({"provider": "bedrock"})


def test_other_providers_are_left_as_is(test_settings):
    with (
        patch.object(test_settings, "DEFAULT_LLM_PROVIDER", None),
        patch("src.services.llm_provider.settings", test_settings),
    ):
        config = {"provider": "local", "local_llm_address": "ollama:11434", "is_embedded_at_local": True}
        assert apply_server_llm_settings(dict(config)) == config
