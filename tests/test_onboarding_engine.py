import pytest
from unittest.mock import MagicMock
from app.models.project import Project
from app.models.source_file import SourceFile
from app.services.onboarding_service import OnboardingService


def test_onboarding_plan_generation_and_quiz(app):
    mock_project_repo = MagicMock()
    mock_file_repo = MagicMock()
    mock_onboarding_repo = MagicMock()

    proj = Project(
        id="p1",
        name="ShopEngine",
        slug="shop-engine",
        file_count=5,
        folder_count=2,
        total_lines=1200,
        languages_json='{"Python": {"files": 5, "lines": 1200}}',
        frameworks_json='["Flask", "SQLAlchemy"]',
    )
    mock_project_repo.get_by_id.return_value = proj

    file_1 = SourceFile(
        id="f1",
        relative_path="app.py",
        filename="app.py",
        language="Python",
        layer_classification="api",
        is_entry_point=True,
        total_lines=100,
        classes=[],
        functions=[],
        imports=[],
    )
    mock_file_repo.get_all_by_project.return_value = [file_1]

    with app.app_context():
        service = OnboardingService(
            project_repo=mock_project_repo,
            file_repo=mock_file_repo,
            onboarding_repo=mock_onboarding_repo,
        )

        plan = service.generate_onboarding_plan("p1")

        assert "ShopEngine" in plan["title"]
        assert len(plan["reading_path"]) == 1
        assert plan["reading_path"][0]["file_path"] == "app.py"
        assert len(plan["knowledge_check"]) >= 2
