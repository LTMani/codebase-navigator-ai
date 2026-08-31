import pytest
from app.models.source_file import SourceFile
from app.services.architecture_service import ArchitectureService


def test_layer_classification_heuristics():
    service = ArchitectureService()

    routes_file = SourceFile(
        project_id="test",
        relative_path="routes/auth_routes.py",
        filename="auth_routes.py",
        language="Python",
    )
    layer, conf = service._classify_file_layer(routes_file)
    assert layer == "api"
    assert conf >= 0.8

    service_file = SourceFile(
        project_id="test",
        relative_path="services/payment_service.py",
        filename="payment_service.py",
        language="Python",
    )
    layer, conf = service._classify_file_layer(service_file)
    assert layer == "service"

    ui_file = SourceFile(
        project_id="test",
        relative_path="components/Header.jsx",
        filename="Header.jsx",
        language="JavaScript",
    )
    layer, conf = service._classify_file_layer(ui_file)
    assert layer == "presentation"
