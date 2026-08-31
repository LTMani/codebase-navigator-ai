import json
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set
from app.extensions import db
from app.models.impact import ImpactAnalysisResult
from app.models.source_file import SourceFile
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.impact_repository import ImpactRepository
from app.repositories.symbol_repository import SymbolRepository


class ImpactService:
    """Calculates change blast radius, affected downstream modules, and breaking change risks."""

    def __init__(
        self,
        impact_repo: Optional[ImpactRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
        file_repo: Optional[FileRepository] = None,
        symbol_repo: Optional[SymbolRepository] = None,
    ):
        self.impact_repo = impact_repo or ImpactRepository()
        self.dep_repo = dep_repo or DependencyRepository()
        self.file_repo = file_repo or FileRepository()
        self.symbol_repo = symbol_repo or SymbolRepository()

    def calculate_impact(
        self,
        project_id: str,
        target_file_path: str,
        target_symbol_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform reverse dependency graph traversal to compute blast radius."""
        source_files = self.file_repo.get_all_by_project(project_id)
        edges = self.dep_repo.get_by_project(project_id)

        file_map: Dict[str, SourceFile] = {f.relative_path: f for f in source_files}
        target_file = file_map.get(target_file_path)

        # Build reverse dependency map: target -> list of sources that depend on target
        reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        for edge in edges:
            reverse_graph[edge.target_path].add(edge.source_path)

        # 1. Direct Dependents
        direct_dependents: Set[str] = reverse_graph.get(target_file_path, set())

        # 2. Transitive / Indirect Dependents via BFS
        indirect_dependents: Set[str] = set()
        queue: deque[str] = deque(list(direct_dependents))
        visited: Set[str] = set(direct_dependents)
        visited.add(target_file_path)

        while queue:
            current = queue.popleft()
            for neighbor in reverse_graph.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    indirect_dependents.add(neighbor)
                    queue.append(neighbor)

        all_affected = direct_dependents.union(indirect_dependents)

        # 3. Affected Routes & Tests
        affected_routes: List[str] = []
        affected_tests: List[str] = []

        for aff_path in all_affected:
            aff_file = file_map.get(aff_path)
            if not aff_file:
                continue

            if aff_file.layer_classification == "api" or aff_file.is_entry_point:
                affected_routes.append(aff_path)
            if aff_file.is_test_file or "test" in aff_path.lower():
                affected_tests.append(aff_path)

        # 4. Public Interfaces of Target
        public_interfaces: List[str] = []
        if target_file:
            for sym in target_file.symbols:
                if sym.is_exported or sym.visibility == "public":
                    public_interfaces.append(sym.name)

        # 5. Blast Radius Score (0 - 100)
        total_files = max(len(source_files), 1)
        reach_ratio = (len(direct_dependents) * 2 + len(indirect_dependents)) / (total_files * 2)
        reach_ratio = min(reach_ratio, 1.0)

        raw_score = (reach_ratio * 70.0) + (min(len(public_interfaces), 10) * 2.0) + (len(affected_routes) * 5.0)
        blast_score = round(min(max(raw_score, 5.0 if direct_dependents else 0.0), 100.0), 1)

        # 6. Risk Level
        if blast_score >= 70.0:
            risk_level = "critical"
        elif blast_score >= 45.0:
            risk_level = "high"
        elif blast_score >= 20.0:
            risk_level = "medium"
        else:
            risk_level = "low"

        # 7. Persist or Update Result Record
        res_obj = self.impact_repo.get_by_target(project_id, target_file_path, target_symbol_name)
        if not res_obj:
            res_obj = ImpactAnalysisResult(
                project_id=project_id,
                target_file_path=target_file_path,
                target_symbol_name=target_symbol_name,
            )
            db.session.add(res_obj)

        res_obj.direct_dependents_count = len(direct_dependents)
        res_obj.indirect_dependents_count = len(indirect_dependents)
        res_obj.blast_radius_score = blast_score
        res_obj.risk_level = risk_level
        res_obj.direct_dependents_json = json.dumps(sorted(list(direct_dependents)))
        res_obj.indirect_dependents_json = json.dumps(sorted(list(indirect_dependents)))
        res_obj.affected_routes_json = json.dumps(sorted(affected_routes))
        res_obj.affected_tests_json = json.dumps(sorted(affected_tests))
        res_obj.public_interfaces_json = json.dumps(public_interfaces)

        db.session.commit()

        return {
            "project_id": project_id,
            "target_file_path": target_file_path,
            "target_symbol_name": target_symbol_name,
            "blast_radius_score": blast_score,
            "risk_level": risk_level,
            "direct_dependents_count": len(direct_dependents),
            "indirect_dependents_count": len(indirect_dependents),
            "direct_dependents": sorted(list(direct_dependents)),
            "indirect_dependents": sorted(list(indirect_dependents)),
            "affected_routes": sorted(affected_routes),
            "affected_tests": sorted(affected_tests),
            "public_interfaces": public_interfaces,
        }
