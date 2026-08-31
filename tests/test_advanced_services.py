import pytest
from unittest.mock import MagicMock
from app.models.dependency import DependencyEdge
from app.models.source_file import SourceFile
from app.models.symbol import FunctionDefinition
from app.services.architecture_rule_engine import ArchitectureRuleEngine
from app.services.call_graph_service import CallGraphService
from app.services.clone_detection_engine import CloneDetectionEngine
from app.services.git_integration_service import GitIntegrationService


def test_call_graph_service():
    mock_file_repo = MagicMock()
    fn_a = FunctionDefinition(name="controller_action", calls=["service_method"])
    fn_b = FunctionDefinition(name="service_method", calls=["db_query"])
    fn_c = FunctionDefinition(name="db_query", calls=[])

    file_1 = SourceFile(id="1", relative_path="api/controller.py", functions=[fn_a])
    file_2 = SourceFile(id="2", relative_path="services/service.py", functions=[fn_b])
    file_3 = SourceFile(id="3", relative_path="repos/repo.py", functions=[fn_c])

    mock_file_repo.get_all_by_project.return_value = [file_1, file_2, file_3]

    cg_service = CallGraphService(file_repo=mock_file_repo)
    res = cg_service.build_project_call_graph("proj_1")

    assert res["nodes_count"] == 3
    assert res["edges_count"] >= 2


def test_architecture_rule_engine_violations():
    mock_file_repo = MagicMock()
    mock_dep_repo = MagicMock()

    file_domain = SourceFile(id="1", relative_path="domain/order.py", layer_classification="domain")
    file_api = SourceFile(id="2", relative_path="api/routes.py", layer_classification="api")

    mock_file_repo.get_all_by_project.return_value = [file_domain, file_api]

    # Domain illegally importing API layer
    violation_edge = DependencyEdge(
        source_path="domain/order.py",
        target_path="api/routes.py",
        is_external=False,
    )
    mock_dep_repo.get_by_project.return_value = [violation_edge]

    rule_engine = ArchitectureRuleEngine(file_repo=mock_file_repo, dep_repo=mock_dep_repo)
    res = rule_engine.check_violations("proj_1")

    assert res["violations_count"] >= 1
    assert res["critical_count"] >= 1
    assert res["violations"][0]["rule_id"] == "ARCH-001"


def test_clone_detection_engine():
    engine = CloneDetectionEngine(min_chunk_lines=3)
    lines_1 = ["def compute_total():", "    x = 10", "    return x * 2"]
    norm = engine.normalize_token_stream(lines_1)
    assert "NUM_LIT" in norm


def test_git_integration_service_non_git():
    git_service = GitIntegrationService()
    res = git_service.analyze_git_metrics("p1", "/non_existent_folder_xyz")
    assert res["is_git_repo"] is False
