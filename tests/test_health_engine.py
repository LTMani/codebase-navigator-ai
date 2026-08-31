import pytest
from unittest.mock import MagicMock
from app.models.source_file import SourceFile
from app.services.health_service import HealthService


def test_health_service_metrics_and_grades(app):
    mock_file_repo = MagicMock()
    mock_health_repo = MagicMock()

    file_1 = SourceFile(
        id="1",
        relative_path="main.py",
        filename="main.py",
        code_lines=50,
        comment_lines=10,
        cyclomatic_complexity=2,
        maintainability_index=88.0,
        functions=[],
        imports=[],
    )

    mock_file_repo.get_all_by_project.return_value = [file_1]

    with app.app_context():
        service = HealthService(file_repo=mock_file_repo, health_repo=mock_health_repo)
        health = service.evaluate_code_health("test_proj")

        assert health["overall_health_score"] >= 80.0
        assert health["maintainability_grade"] in ("A", "B")
        assert health["average_cyclomatic_complexity"] == 2.0
        assert health["average_maintainability_index"] == 88.0
