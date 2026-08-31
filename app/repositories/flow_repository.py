from typing import List, Optional
from sqlalchemy import delete, select
from app.extensions import db
from app.models.code_flow import CodeFlow, FlowNode
from app.repositories.base_repository import BaseRepository


class FlowRepository(BaseRepository[CodeFlow]):
    """Data access repository for CodeFlow execution paths and FlowNodes."""

    def __init__(self):
        super().__init__(CodeFlow)

    def get_by_project(self, project_id: str) -> List[CodeFlow]:
        """Fetch all discovered code flows for project."""
        stmt = select(CodeFlow).where(CodeFlow.project_id == project_id).order_by(CodeFlow.confidence_score.desc())
        return list(db.session.execute(stmt).scalars().all())

    def get_nodes_by_flow(self, code_flow_id: str) -> List[FlowNode]:
        """Fetch steps in a code flow ordered by sequence."""
        stmt = select(FlowNode).where(FlowNode.code_flow_id == code_flow_id).order_by(FlowNode.step_number)
        return list(db.session.execute(stmt).scalars().all())

    def create_nodes_batch(self, nodes: List[FlowNode]) -> List[FlowNode]:
        """Bulk insert flow node steps."""
        if not nodes:
            return []
        db.session.add_all(nodes)
        db.session.commit()
        return nodes

    def delete_by_project(self, project_id: str):
        """Remove code flows and associated flow nodes for project."""
        stmt_flow_ids = select(CodeFlow.id).where(CodeFlow.project_id == project_id)
        flow_ids = list(db.session.execute(stmt_flow_ids).scalars().all())
        if flow_ids:
            db.session.execute(delete(FlowNode).where(FlowNode.code_flow_id.in_(flow_ids)))
        db.session.execute(delete(CodeFlow).where(CodeFlow.project_id == project_id))
        db.session.commit()
