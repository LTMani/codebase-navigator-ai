import json
from typing import Any, Dict, List, Optional
from flask import request
from app.models.audit import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """Service to record and query user and system audit events."""

    def __init__(self, audit_repo: Optional[AuditRepository] = None):
        self.audit_repo = audit_repo or AuditRepository()

    def log(
        self,
        action: str,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        resource_type: str = "project",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create structured audit log entry."""
        ip_addr = request.remote_addr if request else "127.0.0.1"
        user_agent = request.headers.get("User-Agent", "") if request else ""

        entry = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_addr,
            user_agent=user_agent[:256] if user_agent else None,
            details_json=json.dumps(details or {}),
        )
        return self.audit_repo.create(entry)

    def get_project_trail(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve audit history for project."""
        logs = self.audit_repo.get_by_project(project_id, limit=limit)
        return [l.to_dict() for l in logs]
