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


def _memberships(sub: str) -> list[str]:
    import boto3

    client = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION", "ap-northeast-1"))
    result = client.query(
        TableName=os.environ["MEMBERSHIPS_TABLE"],
        KeyConditionExpression="userSub = :sub",
        ExpressionAttributeValues={":sub": {"S": sub}},
    )
    return [item["tenantId"]["S"] for item in result.get("Items", []) if item.get("tenantId", {}).get("S")]


def resolve_tenant(request: Request) -> str | None:
    if not os.getenv("MEMBERSHIPS_TABLE"):
        return None
    if request.url.path in OPEN_PATHS:
        return None

    sub = request.headers.get("x-amzn-oidc-identity", "").strip()
    if not sub:
        return None

    tenants = _memberships(sub)
    requested = request.headers.get("x-tenant-id", "").strip()
    if requested:
        if requested not in tenants:
            raise PermissionError("このテナントのメンバーではありません")
        return requested
    if len(tenants) == 1:
        return tenants[0]
    if not tenants:
        raise PermissionError("所属するテナントがありません")
    raise ValueError("x-tenant-id が必要です")


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
