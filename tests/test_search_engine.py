import pytest
from unittest.mock import MagicMock
from app.models.source_file import SourceFile
from app.models.symbol import ClassDefinition, FunctionDefinition, Symbol
from app.schemas.search_schemas import SearchQuerySchema
from app.services.search_service import SearchService


def test_search_service_files_and_symbols():
    mock_file_repo = MagicMock()
    mock_symbol_repo = MagicMock()

    fn_obj = FunctionDefinition(name="calculate_tax", qualified_name="calculate_tax", start_line=10, end_line=20)
    cls_obj = ClassDefinition(name="PaymentManager", qualified_name="PaymentManager", start_line=1, end_line=50)

    file_a = SourceFile(
        id="1",
        relative_path="services/payment_service.py",
        filename="payment_service.py",
        language="Python",
        layer_classification="service",
        total_lines=60,
        cyclomatic_complexity=3,
        functions=[fn_obj],
        classes=[cls_obj],
        symbols=[],
    )
    fn_obj.source_file = file_a
    cls_obj.source_file = file_a

    mock_file_repo.get_all_by_project.return_value = [file_a]

    service = SearchService(file_repo=mock_file_repo, symbol_repo=mock_symbol_repo)

    # Search for "payment"
    schema = SearchQuerySchema(query="payment", search_type="all")
    results = service.search("proj1", schema)

    assert results["total_results"] >= 2
    assert len(results["results"]["files"]) == 1
    assert results["results"]["files"][0]["filename"] == "payment_service.py"
    assert len(results["results"]["classes"]) == 1
    assert results["results"]["classes"][0]["name"] == "PaymentManager"
