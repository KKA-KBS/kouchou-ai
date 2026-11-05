"""サーバー設定で決まる LLM の項目

AWS の環境では、LLM は国内（東京リージョンと、jp. の推論プロファイルで東京か大阪）の Bedrock を LiteLLM（OpenAI 互換）経由で使う。
接続先と埋め込みはサーバーが決め、画面から送られた値は使わない。
"""

from src.config import settings

BEDROCK_PROVIDER = "bedrock"


def apply_server_llm_settings(config: dict) -> dict:
    """新規作成・複製の config に、サーバー設定で決まる LLM の項目を反映する

    DEFAULT_LLM_PROVIDER があれば画面の選択より優先する。この環境から届かないプロバイダで
    分析を始めないため。
    """
    if settings.DEFAULT_LLM_PROVIDER:
        config["provider"] = settings.DEFAULT_LLM_PROVIDER
    if config.get("provider") != BEDROCK_PROVIDER:
        return config

    if not settings.LOCAL_LLM_ADDRESS:
        raise ValueError("Bedrock を使うには LOCAL_LLM_ADDRESS（LiteLLM のアドレス）が必要です")
    config["local_llm_address"] = settings.LOCAL_LLM_ADDRESS
    # 埋め込みも Bedrock（Titan）で行う。サーバ内のローカルモデルは使わない。
    config["is_embedded_at_local"] = False
    if settings.EMBEDDING_MODEL:
        config.setdefault("embedding", {})["model"] = settings.EMBEDDING_MODEL
    return config
