import pytest
from app.models.source_file import SourceFile
from app.models.symbol import ClassDefinition, FunctionDefinition
from app.services.diff_engine import DiffEngine


def test_semantic_diff_breaking_changes():
    fn_old = FunctionDefinition(name="calculate_tax", parameters=["amount"], return_type="float", is_exported=True)
    fn_new = FunctionDefinition(name="calculate_tax", parameters=["amount", "country_code"], return_type="float", is_exported=True)

    file_old = SourceFile(
        relative_path="tax.py",
        layer_classification="api",
        functions=[fn_old],
        classes=[],
    )

    file_new = SourceFile(
        relative_path="tax.py",
        layer_classification="api",
        functions=[fn_new],
        classes=[],
    )

    engine = DiffEngine()
    diff = engine.compare_files(file_old, file_new)

    assert diff["has_breaking_changes"] is True
    assert diff["breaking_changes_count"] >= 1
    assert len(diff["signature_changes"]) == 1
    assert diff["signature_changes"][0]["function_name"] == "calculate_tax"
