import pytest
from unittest.mock import MagicMock
from app.models.source_file import SourceFile
from app.models.symbol import ClassDefinition, FunctionDefinition
from app.services.refactoring_advisor import RefactoringAdvisor


def test_refactoring_advisor_smell_detection():
    mock_file_repo = MagicMock()

    fn_long = FunctionDefinition(name="process_monolith", line_count=60, cyclomatic_complexity=12, parameters=["a", "b", "c", "d", "e"])
    cls_god = ClassDefinition(name="GodController", methods_count=18, start_line=1)

    file_a = SourceFile(
        id="1",
        relative_path="legacy.py",
        filename="legacy.py",
        code_lines=450,
        documentation_ratio=0.01,
        functions=[fn_long],
        classes=[cls_god],
    )

    mock_file_repo.get_all_by_project.return_value = [file_a]

    advisor = RefactoringAdvisor(file_repo=mock_file_repo)
    res = advisor.analyze_project_smells("p1")

    assert res["total_smells"] >= 3
    smell_types = list(res["smells_by_type"].keys())
    assert "Long Method" in smell_types
    assert "Long Parameter List" in smell_types
    assert "Large Class / God Object" in smell_types
