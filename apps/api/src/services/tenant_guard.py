"""テナントをまたいでレポートや入力を読まないための確認

ローカルのレポート・設定・入力の置き場所はテナントで分かれていない。slug やファイル名だけで
ファイルを開くと、他テナントのものが見える。ファイルを開く前にここで確かめる。
"""

from fastapi import HTTPException

from src.services.report_status import slug_exists, slug_exists_in_any_tenant
from src.tenant import current_tenant


def require_own_report(slug: str) -> None:
    """今のテナントのレポートでなければ 404 にする"""
    if current_tenant() and not slug_exists(slug):
        raise HTTPException(status_code=404, detail="Report not found")


def require_input_not_of_other_tenant(file_name: str) -> None:
    """他テナントのレポートの入力 CSV なら 404 にする

    レポートを作る前の取り込み途中の CSV には持ち主の記録が無いので、ここで防げるのは
    記録のある他テナントのレポートの入力だけ。取り込み途中のものまで分けるには、
    置き場所をテナントごとに分ける必要がある（docs/future-work.md）。
    """
    if current_tenant() and slug_exists_in_any_tenant(file_name) and not slug_exists(file_name):
        raise HTTPException(status_code=404, detail="Input file not found")
