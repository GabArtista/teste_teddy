"""Audit log routes."""

from typing import List

from fastapi import APIRouter, Depends, Query, status

from resume_ai.application.interfaces.audit_repository import AuditRepository
from resume_ai.interfaces.api.dependencies import provide_audit_repository
from resume_ai.interfaces.api.schemas.audit import AuditLogSchema

router = APIRouter(prefix="/v1/logs", tags=["audit"])


@router.get(
    "",
    response_model=List[AuditLogSchema],
    status_code=status.HTTP_200_OK,
    summary="List recent audit logs",
)
async def list_logs(
    limit: int = Query(default=20, ge=1, le=100),
    repository: AuditRepository = Depends(provide_audit_repository),
) -> List[AuditLogSchema]:
    """Return recent audit logs for traceability."""

    logs = await repository.list_logs(limit=limit)
    return [
        AuditLogSchema(
            request_id=log.request_id,
            user_id=log.user_id,
            timestamp=log.timestamp,
            query=log.query,
            result=log.result,
        )
        for log in logs
    ]

