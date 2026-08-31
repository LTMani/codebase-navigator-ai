"""
Architecture Rule Engine
Enforces structural architectural invariants (e.g. Hexagonal, Clean Architecture,
layer separation: Controllers cannot call Repositories directly).
"""

from typing import List, Dict, Any

class ArchitectureRuleEngine:
    def __init__(self, file_repo=None, dep_repo=None):
        self.file_repo = file_repo
        self.dep_repo = dep_repo
        self.rules = [
            {
                "rule_id": "ARCH-001",
                "name": "Domain Layer Isolation",
                "description": "Domain Models must never depend on Web Frameworks or API Transport Layers",
                "forbidden_pair": ("domain", "api")
            },
            {
                "rule_id": "ARCH-002",
                "name": "Strict Controller-Repository Separation",
                "description": "Controllers and API routes must communicate through Services and never import Repositories directly",
                "forbidden_pair": ("controllers", "repositories")
            },
            {
                "rule_id": "ARCH-003",
                "name": "Domain Infrastructure Isolation",
                "description": "Domain Models must never depend on Web Controllers",
                "forbidden_pair": ("models", "controllers")
            }
        ]

    def check_violations(self, project_id: str) -> Dict[str, Any]:
        violations = []
        if not self.dep_repo:
            return {"violations_count": 0, "critical_count": 0, "violations": []}

        edges = self.dep_repo.get_by_project(project_id) if hasattr(self.dep_repo, "get_by_project") else []
        for edge in edges:
            source = getattr(edge, "source_path", "")
            target = getattr(edge, "target_path", "")
            for rule in self.rules:
                src_kw, forbidden_kw = rule["forbidden_pair"]
                if src_kw in source.lower() and forbidden_kw in target.lower():
                    violations.append({
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["name"],
                        "source": source,
                        "target": target,
                        "severity": "CRITICAL",
                        "recommendation": rule["description"]
                    })

        return {
            "violations_count": len(violations),
            "critical_count": len(violations),
            "violations": violations
        }

    def validate_dependency_graph(self, imports_map: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        violations = []
        for source_file, imported_targets in imports_map.items():
            for target in imported_targets:
                for rule in self.rules:
                    src_kw, forbidden_kw = rule["forbidden_pair"]
                    if src_kw in source_file.lower() and forbidden_kw in target.lower():
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "rule_name": rule["name"],
                            "source": source_file,
                            "target": target,
                            "severity": "ERROR",
                            "recommendation": rule["description"]
                        })
        return violations
