"""Append-only repository for the admin audit log (#196 Phase 1).

Phase 1 only needs ``insert``; query APIs (filtered list / detail) ship in
Phase 2 with the ``/admin/audit-log`` page.
"""

from src._core.infrastructure.admin.audit.dtos.audit_log_dto import AuditLogDTO
from src._core.infrastructure.admin.audit.models.audit_log_model import AdminAuditLog
from src._core.infrastructure.persistence.rdb.database import Database


class AdminAuditLogRepository:
    """Minimal repository — INSERT only.

    Deliberately not a ``BaseRepository`` subclass: an audit log is append-only
    and is not modelled as a generic CRUD entity. The query surface is added in
    Phase 2 when the audit-log UI lands.
    """

    def __init__(self, database: Database) -> None:
        self._database = database

    async def insert(self, dto: AuditLogDTO) -> None:
        """Persist a single audit-log entry.

        Raises whatever the database raises — the caller (``AuditLogger.log``)
        is responsible for swallowing/logging any failure so an audit-write
        error never breaks the user action it tried to record.
        """
        model = AdminAuditLog(
            admin_user_id=dto.admin_user_id,
            admin_username=dto.admin_username,
            action=dto.action.value,
            domain=dto.domain,
            record_id=dto.record_id,
            before_state=dto.before_state,
            after_state=dto.after_state,
            result=dto.result.value,
            failure_reason=dto.failure_reason,
            ip_address=dto.ip_address,
            correlation_id=dto.correlation_id,
        )
        async with self._database.session() as session:
            session.add(model)
            await session.commit()
