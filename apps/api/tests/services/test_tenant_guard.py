from unittest.mock import patch

import pytest
from fastapi import HTTPException

from src.services.tenant_guard import require_input_not_of_other_tenant, require_own_report


class TestRequireOwnReport:
    def test_rejects_report_of_another_tenant(self):
        with (
            patch("src.services.tenant_guard.current_tenant", return_value="ashisuto"),
            patch("src.services.tenant_guard.slug_exists", return_value=False),
        ):
            with pytest.raises(HTTPException) as error:
                require_own_report("demo1-report")
        assert error.value.status_code == 404

    def test_allows_own_report(self):
        with (
            patch("src.services.tenant_guard.current_tenant", return_value="ashisuto"),
            patch("src.services.tenant_guard.slug_exists", return_value=True),
        ):
            require_own_report("own-report")

    def test_skips_check_without_tenant_mode(self):
        """テナント台帳を使わないローカル開発では確かめない"""
        with (
            patch("src.services.tenant_guard.current_tenant", return_value=None),
            patch("src.services.tenant_guard.slug_exists", return_value=False),
        ):
            require_own_report("any-report")


class TestRequireInputNotOfOtherTenant:
    def test_rejects_input_of_another_tenants_report(self):
        with (
            patch("src.services.tenant_guard.current_tenant", return_value="ashisuto"),
            patch("src.services.tenant_guard.slug_exists_in_any_tenant", return_value=True),
            patch("src.services.tenant_guard.slug_exists", return_value=False),
        ):
            with pytest.raises(HTTPException) as error:
                require_input_not_of_other_tenant("demo1-report")
        assert error.value.status_code == 404

    def test_allows_input_of_own_report(self):
        with (
            patch("src.services.tenant_guard.current_tenant", return_value="ashisuto"),
            patch("src.services.tenant_guard.slug_exists_in_any_tenant", return_value=True),
            patch("src.services.tenant_guard.slug_exists", return_value=True),
        ):
            require_input_not_of_other_tenant("own-report")

    def test_allows_input_without_any_report(self):
        """レポートを作る前の取り込み途中の CSV は持ち主の記録が無いので通る"""
        with (
            patch("src.services.tenant_guard.current_tenant", return_value="ashisuto"),
            patch("src.services.tenant_guard.slug_exists_in_any_tenant", return_value=False),
            patch("src.services.tenant_guard.slug_exists", return_value=False),
        ):
            require_input_not_of_other_tenant("new-input")
