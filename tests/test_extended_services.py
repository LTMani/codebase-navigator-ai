"""
Unit Tests for Extended Domain Intelligence Services
"""

import pytest
from app.services.call_graph_builder import CallGraphBuilder
from app.services.clone_detection_engine import CloneDetectionEngine
from app.services.data_flow_analysis_engine import DataFlowAnalysisEngine
from app.services.mutation_testing_engine import MutationTestingEngine
from app.services.dependency_vulnerability_matcher import DependencyVulnerabilityMatcher
from app.services.architecture_rule_engine import ArchitectureRuleEngine
from app.services.technical_debt_calculator import TechnicalDebtCalculator
from app.services.git_integration_service import GitIntegrationService
from app.services.code_search_engine import CodeSearchEngine
from app.services.semantic_diff_engine import SemanticDiffEngine

def test_call_graph_construction():
    code = """
def alpha():
    beta()

def beta():
    gamma()

def gamma():
    pass
"""
    builder = CallGraphBuilder()
    builder.parse_and_build("main.py", code)
    graph = builder.get_graph()
    assert "main.py::alpha" in graph
    assert "main.py::beta" in graph["main.py::alpha"]

def test_clone_detection():
    code1 = "def sum_vals(a, b):\n    return a + b\n"
    code2 = "def add_numbers(x, y):\n    return x + y\n"
    detector = CloneDetectionEngine()
    detector.index_snippet("file1.py", code1)
    detector.index_snippet("file2.py", code2)
    clones = detector.find_clones()
    assert len(clones) >= 1

def test_mutation_engine():
    code = "def check(x):\n    if x > 10:\n        return True\n    return False\n"
    engine = MutationTestingEngine()
    mutants = engine.generate_mutants(code)
    assert len(mutants) >= 1
    score = engine.calculate_mutation_score(10, 8)
    assert score == 80.0

def test_dependency_vulnerabilities():
    matcher = DependencyVulnerabilityMatcher()
    results = matcher.scan_dependencies({"requests": "2.25.1", "numpy": "1.24.0"})
    assert len(results) >= 1
    assert results[0]["cve_id"] == "CVE-2023-32681"

def test_architecture_rules():
    engine = ArchitectureRuleEngine()
    imports = {"app/controllers/user_controller.py": ["app/repositories/user_repo.py"]}
    violations = engine.validate_dependency_graph(imports)
    assert len(violations) == 1
    assert violations[0]["rule_id"] in ("ARCH001", "ARCH-001", "ARCH-002")

def test_technical_debt_calculation():
    debt = TechnicalDebtCalculator.estimate_file_debt(complexity=25, duplication_pct=15.0, code_smell_count=4)
    assert debt["debt_hours"] > 0
    assert debt["financial_cost_usd"] > 0

def test_semantic_diff():
    diff = SemanticDiffEngine.compare_symbols(["fnA", "fnB"], ["fnB", "fnC"])
    assert diff["is_breaking_change"] is True
    assert "fnA" in diff["removed_symbols"]
    assert "fnC" in diff["added_symbols"]
