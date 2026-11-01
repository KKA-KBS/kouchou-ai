from unittest.mock import patch

import pytest

from analysis_core.services.llm import request_to_chat_ai, request_to_embed


def test_chat_goes_through_the_gateway():
    with patch("analysis_core.services.llm.request_to_local_llm", return_value=("ok", 1, 1, 2)) as local:
        result = request_to_chat_ai(
            [{"role": "user", "content": "hi"}],
            model="amazon.nova-lite-v1:0",
            provider="bedrock",
            local_llm_address="http://litellm:4000/v1",
        )

    assert result == ("ok", 1, 1, 2)
    assert local.call_args.args[4] == "http://litellm:4000/v1"


def test_embedding_goes_through_the_gateway():
    with patch("analysis_core.services.llm.request_to_local_llm_embed", return_value=[[0.1]]) as embed:
        request_to_embed(
            ["a"], "amazon.titan-embed-text-v2:0", provider="bedrock", local_llm_address="http://litellm:4000/v1"
        )

    embed.assert_called_once_with(["a"], "amazon.titan-embed-text-v2:0", "http://litellm:4000/v1")


def test_bedrock_without_gateway_address_fails():
    """黙って localhost の Ollama に繋がない"""
    with pytest.raises(ValueError):
        request_to_chat_ai([{"role": "user", "content": "hi"}], model="m", provider="bedrock")
