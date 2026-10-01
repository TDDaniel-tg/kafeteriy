from typing import Optional, Dict, Any
from .models import AuditLog

def log_audit_event(
    action: str,
    entity_type: str,
    description: str,
    actor=None,
    entity_id: str = '',
    payload: Optional[Dict[str, Any]] = None,
    ip_address: str = ''
) -> AuditLog:
    """Creates an immutable audit log record."""
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        description=description,
        payload=payload or {},
        ip_address=ip_address
    )
