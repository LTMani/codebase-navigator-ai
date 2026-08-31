import pytest
from unittest.mock import MagicMock
from app.models.copilot import CopilotConversation, CopilotMessage
from app.models.project import Project
from app.schemas.copilot_schemas import CopilotPromptSchema
from app.services.copilot_service import CopilotService


def test_copilot_intent_detection():
    service = CopilotService()

    assert service._detect_intent("Explain this project to me") == "explain_project"
    assert service._detect_intent("What is the architecture of this app?") == "explain_architecture"
    assert service._detect_intent("How does user authentication and login work?") == "explain_auth"
    assert service._detect_intent("What happens if I change services/user.py?") == "change_impact"
    assert service._detect_intent("Where is function calculate_tax located?") == "find_symbol"
    assert service._detect_intent("How healthy is this codebase?") == "health_inquiry"


def test_copilot_deterministic_response(app):
    mock_copilot_repo = MagicMock()
    mock_project_repo = MagicMock()
    mock_file_repo = MagicMock()

    proj = Project(
        id="p1",
        name="NavigatorApp",
        slug="navigator-app",
        file_count=10,
        folder_count=3,
        total_lines=2500,
        code_lines=2000,
        comment_lines=300,
        languages_json='{"Python": {"files": 10, "lines": 2500}}',
        frameworks_json='["Flask"]',
    )
    mock_project_repo.get_by_id.return_value = proj
    mock_file_repo.get_all_by_project.return_value = []

    conv = CopilotConversation(id="c1", project_id="p1", user_id="u1")
    mock_copilot_repo.get_by_id.return_value = conv
    mock_copilot_repo.create.return_value = conv

    with app.app_context():
        service = CopilotService(
            copilot_repo=mock_copilot_repo,
            project_repo=mock_project_repo,
            file_repo=mock_file_repo,
        )

        schema = CopilotPromptSchema(prompt="Explain this project")
        res = service.process_query(
            project_id="p1",
            user_id="u1",
            schema=schema,
            ai_provider="offline",
        )

        assert res["role"] == "assistant"
        assert res["provider_used"] == "deterministic"
        assert "NavigatorApp" in res["content"]
