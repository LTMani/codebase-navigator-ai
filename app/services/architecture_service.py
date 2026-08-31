import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple
from app.extensions import db
from app.models.architecture import ArchitectureFinding, ArchitectureViolation
from app.models.source_file import SourceFile
from app.repositories.architecture_repository import ArchitectureRepository
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository


class ArchitectureService:
    """Classifies codebase into architectural layers, computes confidence scores, and detects layer violations."""

    LAYERS_ORDER = [
        "presentation",
        "api",
        "service",
        "domain",
        "repository",
        "infrastructure",
        "utility",
    ]

    LAYER_METADATA = {
        "presentation": {
            "title": "Presentation & UI Layer",
            "description": "User interface components, HTML templates, CSS styles, client-side routing, and view state.",
            "patterns": ["components/", "views/", "templates/", "pages/", ".jsx", ".tsx", ".html", ".css"],
        },
        "api": {
            "title": "API & Controller Layer",
            "description": "HTTP request handlers, RESTful API endpoints, routing blueprints, and input parameter validation.",
            "patterns": ["routes/", "controllers/", "api/", "endpoints/", "handlers/", "blueprint", "router"],
        },
        "service": {
            "title": "Business Logic & Service Layer",
            "description": "Core application business rules, domain workflows, operations orchestration, and complex algorithms.",
            "patterns": ["services/", "managers/", "usecases/", "workflows/", "service.py", "service.js"],
        },
        "domain": {
            "title": "Domain & Entity Layer",
            "description": "Data models, entity schemas, validation constraints, and domain data contracts.",
            "patterns": ["models/", "entities/", "schemas/", "types/", "domain/"],
        },
        "repository": {
            "title": "Data Access & Repository Layer",
            "description": "Database persistence operations, ORM query builders, DAOs, and data storage connectors.",
            "patterns": ["repositories/", "repository.py", "dao/", "database/", "db/", "migrations/"],
        },
        "infrastructure": {
            "title": "Infrastructure & Configuration Layer",
            "description": "Server initialization, authentication middleware, environment settings, and container setups.",
            "patterns": ["config/", "settings.py", "middleware/", "security/", "Dockerfile", "nginx"],
        },
        "utility": {
            "title": "Utilities & Shared Helpers",
            "description": "Cross-cutting utility functions, math helpers, text formatters, and reusable tools.",
            "patterns": ["utils/", "helpers/", "common/", "formatters/"],
        },
    }

    def __init__(
        self,
        arch_repo: Optional[ArchitectureRepository] = None,
        file_repo: Optional[FileRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
    ):
        self.arch_repo = arch_repo or ArchitectureRepository()
        self.file_repo = file_repo or FileRepository()
        self.dep_repo = dep_repo or DependencyRepository()

    def analyze_architecture(self, project_id: str) -> Dict[str, Any]:
        """Perform layer inference, boundary violation checks, and interaction matrix generation."""
        source_files = self.file_repo.get_all_by_project(project_id)
        edges = self.dep_repo.get_by_project(project_id)

        # Clear existing findings for fresh run
        self.arch_repo.delete_by_project(project_id)

        layer_files_map: Dict[str, List[SourceFile]] = defaultdict(list)
        file_layer_map: Dict[str, str] = {}

        # 1. Classify each source file to an architectural layer
        for file_obj in source_files:
            layer, confidence = self._classify_file_layer(file_obj)
            file_obj.layer_classification = layer
            file_obj.layer_confidence = confidence
            layer_files_map[layer].append(file_obj)
            file_layer_map[file_obj.relative_path] = layer

        db.session.commit()

        # 2. Build Layer Findings Entities
        findings: List[ArchitectureFinding] = []
        for layer_key, layer_info in self.LAYER_METADATA.items():
            files = layer_files_map.get(layer_key, [])
            if not files:
                continue

            file_paths = [f.relative_path for f in files]
            inbound_count = sum(1 for e in edges if file_layer_map.get(e.target_path) == layer_key and file_layer_map.get(e.source_path) != layer_key)
            outbound_count = sum(1 for e in edges if file_layer_map.get(e.source_path) == layer_key and file_layer_map.get(e.target_path) != layer_key)

            finding = ArchitectureFinding(
                project_id=project_id,
                layer_name=layer_key,
                component_name=layer_info["title"],
                description=layer_info["description"],
                file_count=len(files),
                confidence_score=round(sum(f.layer_confidence for f in files) / max(len(files), 1), 2),
                patterns_detected_json=json.dumps(layer_info["patterns"]),
                associated_files_json=json.dumps(file_paths[:100]),
                inbound_dependencies_count=inbound_count,
                outbound_dependencies_count=outbound_count,
            )
            findings.append(finding)

        if findings:
            db.session.add_all(findings)
            db.session.commit()

        # 3. Detect Layer Boundary Violations
        violations = self._detect_boundary_violations(project_id, edges, file_layer_map)
        if violations:
            self.arch_repo.create_violations_batch(violations)

        # 4. Generate Layer Interaction Matrix
        interaction_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for edge in edges:
            src_layer = file_layer_map.get(edge.source_path, "external")
            tgt_layer = file_layer_map.get(edge.target_path, "external")
            if src_layer != tgt_layer:
                interaction_matrix[src_layer][tgt_layer] += 1

        return {
            "project_id": project_id,
            "layers": [f.to_dict() for f in findings],
            "violations": [v.to_dict() for v in violations],
            "interaction_matrix": interaction_matrix,
        }

    def _classify_file_layer(self, file_obj: SourceFile) -> Tuple[str, float]:
        """Heuristically assign layer based on path, extension, and content."""
        path = file_obj.relative_path.lower()

        # Direct folder matching
        if any(p in path for p in ("components/", "views/", "templates/", "pages/", "styles/", ".css", ".html")):
            return "presentation", 0.95
        if any(p in path for p in ("routes/", "controllers/", "api/", "endpoints/", "handlers/")):
            return "api", 0.95
        if any(p in path for p in ("services/", "managers/", "usecases/", "workflows/")):
            return "service", 0.90
        if any(p in path for p in ("models/", "entities/", "schemas/", "types/")):
            return "domain", 0.90
        if any(p in path for p in ("repositories/", "repository.", "dao/", "database/", "migrations/")):
            return "repository", 0.90
        if any(p in path for p in ("config/", "settings.", "middleware/", "security/")):
            return "infrastructure", 0.85
        if any(p in path for p in ("utils/", "helpers/", "common/", "formatters/")):
            return "utility", 0.80

        # Heuristic fallback based on extension and filename
        if path.endswith((".jsx", ".tsx", ".vue", ".svelte")):
            return "presentation", 0.85
        if "test" in path:
            return "utility", 0.70

        return "domain", 0.50

    def _detect_boundary_violations(
        self,
        project_id: str,
        edges: List[Any],
        file_layer_map: Dict[str, str],
    ) -> List[ArchitectureViolation]:
        """Check architectural layering rules."""
        violations: List[ArchitectureViolation] = []

        # Rules:
        # 1. presentation layer should not directly access repository layer
        # 2. domain layer should not depend on api or presentation layers
        # 3. repository layer should not depend on api or presentation layers

        for edge in edges:
            src_layer = file_layer_map.get(edge.source_path)
            tgt_layer = file_layer_map.get(edge.target_path)

            if not src_layer or not tgt_layer or src_layer == tgt_layer:
                continue

            if src_layer == "presentation" and tgt_layer == "repository":
                violations.append(
                    ArchitectureViolation(
                        project_id=project_id,
                        source_layer=src_layer,
                        target_layer=tgt_layer,
                        source_file_path=edge.source_path,
                        target_file_path=edge.target_path,
                        rule_name="Layer Bypass: UI Directly Accessing Repository",
                        severity="warning",
                        explanation=f"File '{edge.source_path}' in UI layer directly references repository '{edge.target_path}' bypassing the Service layer.",
                        refactoring_advice="Introduce a Service method to encapsulate domain business logic and delegate data access.",
                    )
                )

            if src_layer == "domain" and tgt_layer in ("api", "presentation"):
                violations.append(
                    ArchitectureViolation(
                        project_id=project_id,
                        source_layer=src_layer,
                        target_layer=tgt_layer,
                        source_file_path=edge.source_path,
                        target_file_path=edge.target_path,
                        rule_name="Inverted Dependency: Domain Coupling to Controller",
                        severity="error",
                        explanation=f"Domain model '{edge.source_path}' imports outer layer '{edge.target_path}'.",
                        refactoring_advice="Keep domain models independent of presentation or routing controllers.",
                    )
                )

        return violations
