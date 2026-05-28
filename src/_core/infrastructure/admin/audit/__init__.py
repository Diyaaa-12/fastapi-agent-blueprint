"""Admin audit log infrastructure (#196 Phase 1).

Side effect: importing this package registers the ``AdminAuditLog`` model on
``Base.metadata`` so it is picked up by ``Base.metadata.create_all()``
(quickstart / e2e test conftest) and Alembic autogenerate.
"""

from src._core.infrastructure.admin.audit.dtos.audit_log_dto import (
    AdminAction,
    AuditLogDTO,
    AuditResult,
)
from src._core.infrastructure.admin.audit.logger import (
    AuditLogger,
    configure_audit_logger,
    get_audit_logger,
)
from src._core.infrastructure.admin.audit.models.audit_log_model import AdminAuditLog
from src._core.infrastructure.admin.audit.repository import AdminAuditLogRepository
from src._core.infrastructure.admin.audit.safe_state import safe_user_snapshot

__all__ = [
    "AdminAction",
    "AdminAuditLog",
    "AdminAuditLogRepository",
    "AuditLogDTO",
    "AuditLogger",
    "AuditResult",
    "configure_audit_logger",
    "get_audit_logger",
    "safe_user_snapshot",
]
