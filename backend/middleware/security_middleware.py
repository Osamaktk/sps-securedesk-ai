import re
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, Response

from database import AsyncSessionLocal
from services.audit_service import write_audit_log

INJECTION_PATTERNS = ("SELECT ", "DROP ", "INSERT ", "DELETE ", "UNION ", "--", "XP_")
SECRET_PATTERNS = (
    ("api_key", re.compile(r"(api[_-]?key|secret[_-]?key|access[_-]?token|anthropic_api_key)\s*[:=]\s*[\"']?[A-Za-z0-9_.\-]{8,}", re.IGNORECASE)),
    ("bearer_token", re.compile(r"bearer\s+[A-Za-z0-9_.\-]{20,}", re.IGNORECASE)),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("password_assignment", re.compile(r"password\s*=\s*[^&\s]{4,}", re.IGNORECASE)),
)


def _client_ip(request: Request | None) -> str | None:
    if not request or not request.client:
        return None
    return request.client.host


def _should_scan_body(request: Request) -> bool:
    if request.method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False

    content_type = request.headers.get("content-type", "").lower()
    if content_type.startswith("multipart/form-data"):
        return False
    if content_type.startswith("application/octet-stream"):
        return False
    return True


async def log_security_event(
    *,
    action: str,
    details: dict[str, Any],
    request: Request | None = None,
    db: AsyncSession | None = None,
    actor_id: uuid.UUID | None = None,
    ip_address: str | None = None,
) -> None:
    log_ip = ip_address or _client_ip(request)
    log_details = {
        "path": str(request.url.path) if request else None,
        **details,
    }

    try:
        if db:
            await write_audit_log(
                db,
                action=action,
                channel="security",
                actor_id=actor_id,
                details=log_details,
                ip_address=log_ip,
            )
            await db.commit()
            return

        async with AsyncSessionLocal() as session:
            await write_audit_log(
                session,
                action=action,
                channel="security",
                actor_id=actor_id,
                details=log_details,
                ip_address=log_ip,
            )
            await session.commit()
    except Exception:
        if db:
            await db.rollback()


def _detect_injection(body_text: str) -> str | None:
    upper_body = body_text.upper()
    for pattern in INJECTION_PATTERNS:
        if pattern in upper_body:
            return pattern
    return None


def _detect_secret(body_text: str, path: str) -> str | None:
    for name, pattern in SECRET_PATTERNS:
        if name == "password_assignment" and path.startswith("/auth/"):
            continue
        if pattern.search(body_text):
            return name
    return None


async def check_security_threats(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if not _should_scan_body(request):
        return await call_next(request)

    body = await request.body()
    body_text = body.decode("utf-8", errors="ignore")

    injection_pattern = _detect_injection(body_text)
    if injection_pattern:
        await log_security_event(
            action="security.injection_attempt",
            request=request,
            details={"pattern": injection_pattern, "method": request.method},
        )
        return JSONResponse(status_code=400, content={"detail": "Invalid request"})

    secret_pattern = _detect_secret(body_text, request.url.path)
    if secret_pattern:
        await log_security_event(
            action="security.secret_detected",
            request=request,
            details={"pattern": secret_pattern, "method": request.method},
        )
        return JSONResponse(status_code=400, content={"detail": "Sensitive values are not allowed in request body"})

    return await call_next(request)
