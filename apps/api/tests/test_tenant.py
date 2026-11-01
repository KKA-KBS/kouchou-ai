from unittest.mock import patch

import pytest
from fastapi import Request

from src.tenant import resolve_tenant


def _request(path: str, headers: dict[str, str] | None = None) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "server": ("testserver", 80),
            "path": path,
            "query_string": b"",
            "headers": [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()],
        }
    )


class TestResolveTenant:
    @pytest.fixture(autouse=True)
    def _tenant_mode(self, monkeypatch):
        monkeypatch.setenv("MEMBERSHIPS_TABLE", "memberships")

    def test_rejects_request_without_identity(self):
        """利用者が分からないリクエストは、全テナントが見えないよう通さない"""
        with pytest.raises(PermissionError):
            resolve_tenant(_request("/reports"))

    @pytest.mark.parametrize("path", ["/", "/meta/metadata.json", "/meta/icon.png"])
    def test_open_paths_need_no_identity(self, path):
        assert resolve_tenant(_request(path)) is None

    def test_uses_the_only_membership(self):
        with patch("src.tenant._memberships", return_value=[{"tenantId": "ashisuto", "role": "member"}]):
            assert resolve_tenant(_request("/reports", {"x-amzn-oidc-identity": "sub-1"})) == "ashisuto"

    def test_rejects_tenant_without_membership(self):
        with patch("src.tenant._memberships", return_value=[{"tenantId": "ashisuto", "role": "member"}]):
            with pytest.raises(PermissionError):
                resolve_tenant(_request("/reports", {"x-amzn-oidc-identity": "sub-1", "x-tenant-id": "demo1"}))

    def test_no_tenant_mode_without_table(self, monkeypatch):
        """テナント台帳を使わないローカル開発では、これまでどおりテナントなしで通す"""
        monkeypatch.delenv("MEMBERSHIPS_TABLE")
        assert resolve_tenant(_request("/reports")) is None
