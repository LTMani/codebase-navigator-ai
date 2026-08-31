import pytest
from unittest.mock import MagicMock
from app.models.dependency import DependencyEdge
from app.models.source_file import SourceFile
from app.services.impact_service import ImpactService


def test_impact_analysis_transitive_propagation():
    # Setup mock repositories
    mock_file_repo = MagicMock()
    mock_dep_repo = MagicMock()
    mock_impact_repo = MagicMock()

    file_a = SourceFile(id="1", relative_path="models/user.py", filename="user.py", layer_classification="domain", symbols=[])
    file_b = SourceFile(id="2", relative_path="services/user_service.py", filename="user_service.py", layer_classification="service", symbols=[])
    file_c = SourceFile(id="3", relative_path="routes/auth_routes.py", filename="auth_routes.py", layer_classification="api", symbols=[])

    mock_file_repo.get_all_by_project.return_value = [file_a, file_b, file_c]

    # Edges: auth_routes -> user_service -> user
    edge_1 = DependencyEdge(source_path="routes/auth_routes.py", target_path="services/user_service.py")
    edge_2 = DependencyEdge(source_path="services/user_service.py", target_path="models/user.py")
    mock_dep_repo.get_by_project.return_value = [edge_1, edge_2]
    mock_impact_repo.get_by_target.return_value = None

    service = ImpactService(
        impact_repo=mock_impact_repo,
        dep_repo=mock_dep_repo,
        file_repo=mock_file_repo,
    )

    # When models/user.py changes:
    # Direct dependent: services/user_service.py
    # Indirect dependent: routes/auth_routes.py
    res = service.calculate_impact(project_id="test_proj", target_file_path="models/user.py")

    assert res["direct_dependents_count"] == 1
    assert "services/user_service.py" in res["direct_dependents"]
    assert res["indirect_dependents_count"] == 1
    assert "routes/auth_routes.py" in res["indirect_dependents"]
    assert "routes/auth_routes.py" in res["affected_routes"]
