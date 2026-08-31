import os
import pytest
from app.models.project import Project
from app.models.user import User
from app.services.architecture_service import ArchitectureService
from app.services.copilot_service import CopilotService
from app.services.dependency_service import DependencyService
from app.services.health_service import HealthService
from app.services.impact_service import ImpactService
from app.services.onboarding_service import OnboardingService
from app.services.scanner_service import ScannerService


def test_full_codebase_navigator_end_to_end_pipeline(app):
    """End-to-End integration test: scan sample repo -> dependency graph -> architecture -> health -> copilot."""
    with app.app_context():
        # 1. Initialize user and project
        user = User(username="test_e2e_user", email="e2e@navigator.ai")
        user.set_password("SecurePass@123")

        fixture_dir = os.path.abspath("fixtures/flask_ecommerce")
        project = Project(
            name="Flask ECommerce Test",
            slug="flask-ecommerce-test",
            storage_path=fixture_dir,
            user_id=user.id,
        )

        # 2. Scanner Service indexes files
        scanner = ScannerService()
        run, files = scanner.scan_project_directory(project, fixture_dir)

        assert len(files) >= 5
        assert project.file_count >= 5
        assert project.total_lines > 100

        # 3. Dependency Service builds graph and cycles
        dep_service = DependencyService()
        dep_graph = dep_service.build_dependency_graph(project.id)

        assert dep_graph["nodes_count"] >= 5
        assert isinstance(dep_graph["cycles"], list)

        # 4. Architecture Service classifies 6 tiers
        arch_service = ArchitectureService()
        arch_data = arch_service.analyze_architecture(project.id)

        assert len(arch_data["layers"]) >= 3
        layer_names = [l["layer_name"] for l in arch_data["layers"]]
        assert "api" in layer_names or "domain" in layer_names

        # 5. Code Health Service calculates metrics and technical debt
        health_service = HealthService()
        health = health_service.evaluate_code_health(project.id)

        assert health["overall_health_score"] > 0
        assert health["maintainability_grade"] in ("A", "B", "C", "D", "F")

        # 6. Change Impact Simulation
        impact_service = ImpactService()
        sample_file = files[0].relative_path
        impact = impact_service.calculate_impact(project.id, sample_file)

        assert "blast_radius_score" in impact
        assert "risk_level" in impact

        # 7. Onboarding Guide generation
        onboarding_service = OnboardingService()
        onboarding = onboarding_service.generate_onboarding_plan(project.id)

        assert "Flask ECommerce Test" in onboarding["title"]
        assert len(onboarding["reading_path"]) > 0
        assert len(onboarding["knowledge_check"]) > 0

        # 8. Grounded AI Copilot Query
        copilot_service = CopilotService()
        from app.schemas.copilot_schemas import CopilotPromptSchema
        copilot_res = copilot_service.process_query(
            project_id=project.id,
            user_id=user.id,
            schema=CopilotPromptSchema(prompt="Explain the architecture of this e-commerce app"),
            ai_provider="offline",
        )

        assert copilot_res["role"] == "assistant"
        assert "Flask ECommerce Test" in copilot_res["content"]
