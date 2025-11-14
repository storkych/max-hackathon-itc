from typing import Any, Dict, Optional

from .. import models


def write_audit_log(
    *,
    user: Optional[models.UserProfile],
    action: str,
    resource: str,
    request_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> models.AuditLogEntry:
    """Создать запись аудита."""
    return models.AuditLogEntry.objects.create(
        user=user,
        action=action,
        resource=resource,
        request_id=request_id or "",
        idempotency_key=idempotency_key or "",
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent or "",
    )

