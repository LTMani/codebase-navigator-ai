from typing import Any, Dict, List, Optional
from app.models.source_file import SourceFile
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository


class ArchitectureRuleEngine:
    """Evaluates architectural fitness functions and detects structural layer violations."""

    def __init__(
        self,
        file_repo: Optional[FileRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
    ):
        self.file_repo = file_repo or FileRepository()
        self.dep_repo = dep_repo or DependencyRepository()

        # Architecture Rules Definition
        self.forbidden_dependencies = [
            {
                "rule_id": "ARCH-001",
                "source_layer": "domain",
                "forbidden_target_layer": "api",
                "severity": "Critical",
                "name": "Domain Layer Poluted by API Details",
                "description": "Domain layer models/logic must not import presentation controllers or HTTP web frameworks.",
                "remediation": "Move web-specific concerns into API routes or controllers.",
            },
            {
                "rule_id": "ARCH-002",
                "source_layer": "domain",
                "forbidden_target_layer": "presentation",
                "severity": "Critical",
                "name": "Domain Layer Depended on UI",
                "description": "Core business domain must remain decoupled from UI components.",
                "remediation": "Extract UI state to front-end views and keep domain pure.",
            },
            {
                "rule_id": "ARCH-003",
                "source_layer": "api",
                "forbidden_target_layer": "repository",
                "severity": "High",
                "name": "API Layer Bypassing Service Layer",
                "description": "API controllers should call domain services rather than directly querying database repositories.",
                "remediation": "Encapsulate repository calls inside a domain service method.",
            },
            {
                "rule_id": "ARCH-004",
                "source_layer": "domain",
                "forbidden_target_layer": "infrastructure",
                "severity": "Medium",
                "name": "Domain Depending on Infrastructure",
                "description": "Domain entities should depend on interfaces/abstractions rather than concrete infrastructure clients.",
                "remediation": "Apply Dependency Inversion Principle (DIP) with dependency injection.",
            },
        ]

    def check_violations(self, project_id: str) -> Dict[str, Any]:
        """Audit all dependency edges against architectural constraint rules."""
        source_files = self.file_repo.get_all_by_project(project_id)
        edges = self.dep_repo.get_by_project(project_id)

        file_layer_map: Dict[str, str] = {
            sf.relative_path: sf.layer_classification or "unclassified"
            for sf in source_files
        }

        violations: List[Dict[str, Any]] = []

        for edge in edges:
            src_layer = file_layer_map.get(edge.source_path, "unclassified")
            tgt_layer = file_layer_map.get(edge.target_path, "unclassified")

            if edge.is_external:
                continue

            for rule in self.forbidden_dependencies:
                if src_layer == rule["source_layer"] and tgt_layer == rule["forbidden_target_layer"]:
                    violations.append({
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["name"],
                        "severity": rule["severity"],
                        "source_file": edge.source_path,
                        "source_layer": src_layer,
                        "target_file": edge.target_path,
                        "target_layer": tgt_layer,
                        "description": rule["description"],
                        "remediation": rule["remediation"],
                    })

        return {
            "project_id": project_id,
            "violations_count": len(violations),
            "critical_count": len([v for v in violations if v["severity"] == "Critical"]),
            "high_count": len([v for v in violations if v["severity"] == "High"]),
            "medium_count": len([v for v in violations if v["severity"] == "Medium"]),
            "violations": violations[:50],
        }
