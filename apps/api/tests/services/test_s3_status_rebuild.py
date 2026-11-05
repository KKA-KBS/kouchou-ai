import io
import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from src.services import report_status
from src.services.storage import S3StorageService


def make_s3_service(objects: dict[str, bytes]) -> S3StorageService:
    """objects（キーと中身）を持つバケットの S3StorageService を作る"""
    service = S3StorageService.__new__(S3StorageService)
    service.bucket = "bucket"
    service.client = MagicMock()
    modified = datetime(2026, 11, 2, 0, 0, tzinfo=UTC)
    paginator = MagicMock()
    paginator.paginate.return_value = [{"Contents": [{"Key": key, "LastModified": modified} for key in objects]}]
    service.client.get_paginator.return_value = paginator
    service.client.get_object.side_effect = lambda Bucket, Key: {"Body": io.BytesIO(objects[Key])}
    return service


def test_status_file_is_under_the_kouchou_prefix():
    """タスクのロールは kouchou/* だけを読み書きできる"""
    service = S3StorageService.__new__(S3StorageService)
    assert service._key("status/report_status.json") == "kouchou/_shared/status/report_status.json"


def test_list_reports_needs_both_config_and_result():
    config = json.dumps({"question": "質問", "intro": "説明", "model": "m"}).encode()
    service = make_s3_service({
        "kouchou/demo1/configs/a.json": config,
        "kouchou/demo1/outputs/a/hierarchical_result.json": b"{}",
        # 結果が無いレポートは戻さない
        "kouchou/demo1/configs/b.json": config,
        # 設定が無いレポートは戻さない
        "kouchou/demo2/outputs/c/hierarchical_result.json": b"{}",
        "kouchou/_shared/status/report_status.json": b"{}",
    })

    reports = service.list_reports_of_all_tenants()

    assert [(r["tenant_id"], r["slug"], r["config"]["question"]) for r in reports] == [("demo1", "a", "質問")]


def test_rebuild_restores_reports_when_status_is_empty(tmp_path):
    config = json.dumps({"question": "質問", "intro": "説明", "provider": "bedrock"}).encode()
    service = make_s3_service({
        "kouchou/demo1/configs/a.json": config,
        "kouchou/demo1/outputs/a/hierarchical_result.json": b"{}",
    })
    state_file = tmp_path / "report_status.json"

    with (
        patch.object(report_status, "STATE_FILE", state_file),
        patch("src.services.storage.get_storage_service", return_value=service),
        patch("src.services.report_sync.ReportSyncService") as sync,
    ):
        restored = report_status.rebuild_status_from_storage_if_empty()

    assert restored == 1
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    record = saved["demo1:a"]
    assert record["tenant_id"] == "demo1"
    assert record["status"] == "ready"
    assert record["visibility"] == "unlisted"
    assert record["title"] == "質問"
    sync.return_value.sync_status_file_to_storage.assert_called_once()


def test_rebuild_does_nothing_when_status_exists(tmp_path):
    state_file = tmp_path / "report_status.json"
    state_file.write_text(json.dumps({"demo1:x": {"slug": "x", "status": "ready"}}), encoding="utf-8")

    with (
        patch.object(report_status, "STATE_FILE", state_file),
        patch("src.services.storage.get_storage_service") as get_service,
    ):
        assert report_status.rebuild_status_from_storage_if_empty() == 0

    get_service.assert_not_called()
