from typing import List, Optional
from sqlalchemy import delete, desc, select
from app.extensions import db
from app.models.copilot import CopilotConversation, CopilotMessage
from app.repositories.base_repository import BaseRepository


class CopilotRepository(BaseRepository[CopilotConversation]):
    """Data access repository for CopilotConversation and CopilotMessage."""

    def __init__(self):
        super().__init__(CopilotConversation)

    def get_by_user_and_project(self, user_id: str, project_id: str) -> List[CopilotConversation]:
        """Fetch conversations for user in project."""
        stmt = (
            select(CopilotConversation)
            .where(
                CopilotConversation.user_id == user_id,
                CopilotConversation.project_id == project_id,
            )
            .order_by(desc(CopilotConversation.updated_at))
        )
        return list(db.session.execute(stmt).scalars().all())

    def get_messages(self, conversation_id: str) -> List[CopilotMessage]:
        """Fetch chronological messages in conversation."""
        stmt = select(CopilotMessage).where(CopilotMessage.conversation_id == conversation_id).order_by(CopilotMessage.created_at)
        return list(db.session.execute(stmt).scalars().all())

    def add_message(self, message: CopilotMessage) -> CopilotMessage:
        """Append message to conversation and increment count."""
        db.session.add(message)
        conv = self.get_by_id(message.conversation_id)
        if conv:
            conv.message_count += 1
        db.session.commit()
        db.session.refresh(message)
        return message

    def delete_by_project(self, project_id: str):
        """Remove all copilot conversations and messages for project."""
        stmt_conv_ids = select(CopilotConversation.id).where(CopilotConversation.project_id == project_id)
        conv_ids = list(db.session.execute(stmt_conv_ids).scalars().all())
        if conv_ids:
            db.session.execute(delete(CopilotMessage).where(CopilotMessage.conversation_id.in_(conv_ids)))
        db.session.execute(delete(CopilotConversation).where(CopilotConversation.project_id == project_id))
        db.session.commit()
