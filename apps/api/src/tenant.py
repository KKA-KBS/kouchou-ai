import os
from contextvars import ContextVar

from fastapi import Request
from fastapi.responses import JSONResponse

_tenant_id: ContextVar[str | None] = ContextVar("tenant_id", default=None)

OPEN_PATHS = {"/", "/health", "/api/health"}


def current_tenant() -> str | None:
    return _tenant_id.get()


def set_tenant(tenant_id: str | None):
    return _tenant_id.set(tenant_id)


def reset_tenant(token) -> None:
    _tenant_id.reset(token)


def _cookie(request: Request, name: str) -> str:
    for part in request.headers.get("cookie", "").split(";"):
        key, _, value = part.strip().partition("=")
        if key == name and value:
            return value
    return ""


def _memberships(sub: str) -> list[dict]:
    import boto3

    client = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION", "ap-northeast-1"))
    result = client.query(
        TableName=os.environ["MEMBERSHIPS_TABLE"],
        KeyConditionExpression="userSub = :sub",
        ExpressionAttributeValues={":sub": {"S": sub}},
    )
    rows = []
    for item in result.get("Items", []):
        tenant_id = item.get("tenantId", {}).get("S")
        if not tenant_id:
            continue
        rows.append({"tenantId": tenant_id, "role": item.get("role", {}).get("S") or "member"})
    return rows


def resolve_tenant(request: Request) -> str | None:
    if not os.getenv("MEMBERSHIPS_TABLE"):
        return None
    if request.url.path in OPEN_PATHS:
        return None

    sub = request.headers.get("x-amzn-oidc-identity", "").strip()
    if not sub:
        return None

    rows = _memberships(sub)
    tenants = [row["tenantId"] for row in rows]
    requested = request.headers.get("x-tenant-id", "").strip() or _cookie(request, "dd_tenant")
    if requested:
        if requested not in tenants:
            raise PermissionError("このテナントのメンバーではありません")
        chosen = requested
    elif len(tenants) == 1:
        chosen = tenants[0]
    elif not tenants:
        raise PermissionError("所属するテナントがありません")
    else:
        raise ValueError("x-tenant-id が必要です")

    role = next(row["role"] for row in rows if row["tenantId"] == chosen)
    if request.url.path.startswith("/admin") and role != "tenant-admin":
        raise PermissionError("このテナントの管理者ではありません")
    return chosen


async def tenant_middleware(request: Request, call_next):
    try:
        tenant_id = resolve_tenant(request)
    except PermissionError as exc:
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    token = set_tenant(tenant_id)
    try:
        return await call_next(request)
    finally:
        reset_tenant(token)
