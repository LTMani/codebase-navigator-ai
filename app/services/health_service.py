import json
from typing import Any, Dict, List, Optional
from app.extensions import db
from app.models.health import CircularDependencyCluster, HealthMetric
from app.models.source_file import SourceFile
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.health_repository import HealthRepository
from app.services.dependency_service import DependencyService


class HealthService:
    """Computes codebase health metrics, technical debt, hotspots, and refactoring recommendations."""

    def __init__(
        self,
        health_repo: Optional[HealthRepository] = None,
        file_repo: Optional[FileRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
    ):
        self.health_repo = health_repo or HealthRepository()
        self.file_repo = file_repo or FileRepository()
        self.dep_repo = dep_repo or DependencyRepository()
        self.dep_service = DependencyService()

    def evaluate_code_health(self, project_id: str) -> Dict[str, Any]:
        """Perform comprehensive health audit on project."""
        source_files = self.file_repo.get_all_by_project(project_id)
        if not source_files:
            return {"overall_health_score": 100.0, "maintainability_grade": "A"}

        # Clear existing metrics for fresh evaluation
        self.health_repo.delete_by_project(project_id)

        # 1. Dependency Graph & Cycles
        dep_data = self.dep_service.build_dependency_graph(project_id)
        cycles = dep_data.get("cycles", [])

        # Store Circular Clusters
        clusters: List[CircularDependencyCluster] = []
        for c in cycles:
            path_str = " -> ".join(c) + f" -> {c[0]}"
            suggestion = f"Break mutual dependency between {c[0]} and {c[1]} by introducing an interface or shared utility."
            cluster_obj = CircularDependencyCluster(
                project_id=project_id,
                cycle_length=len(c),
                severity="critical" if len(c) <= 2 else "warning",
                files_in_cycle_json=json.dumps(c),
                cycle_path_json=json.dumps(c),
                refactoring_suggestion=suggestion,
            )
            clusters.append(cluster_obj)

        if clusters:
            db.session.add_all(clusters)

        # 2. Aggregations
        total_files = len(source_files)
        total_loc = sum(f.code_lines or 0 for f in source_files)
        total_comments = sum(f.comment_lines or 0 for f in source_files)
        doc_coverage = round((total_comments / max(total_loc + total_comments, 1)) * 100.0, 1)

        cc_list = [f.cyclomatic_complexity or 1 for f in source_files]
        avg_cc = round(sum(cc_list) / max(total_files, 1), 2)
        max_cc = max(cc_list) if cc_list else 1

        mi_list = [f.maintainability_index or 100.0 for f in source_files]
        avg_mi = round(sum(mi_list) / max(total_files, 1), 1)

        large_files = [f for f in source_files if (f.code_lines or 0) > 300]
        complex_fns = []
        for f in source_files:
            for fn in f.functions:
                if (fn.cyclomatic_complexity or 1) > 8:
                    complex_fns.append({
                        "file_path": f.relative_path,
                        "function_name": fn.name,
                        "complexity": fn.cyclomatic_complexity,
                        "lines": fn.line_count,
                    })

        # 3. Identify Hotspots (Low MI, High CC, or Large size)
        hotspots: List[Dict[str, Any]] = []
        for f in source_files:
            hotspot_score = 0
            reasons = []

            cc = f.cyclomatic_complexity or 1
            mi = f.maintainability_index or 100.0
            cl = f.code_lines or 0
            dr = f.documentation_ratio or 0.0

            if cc > 10:
                hotspot_score += 35
                reasons.append(f"High cyclomatic complexity ({cc})")
            if mi < 65.0:
                hotspot_score += 30
                reasons.append(f"Low maintainability index ({mi})")
            if cl > 250:
                hotspot_score += 25
                reasons.append(f"Large file size ({cl} lines)")
            if dr < 0.05 and cl > 50:
                hotspot_score += 15
                reasons.append("Sparse documentation")

            if hotspot_score >= 30:
                hotspots.append({
                    "file_path": f.relative_path,
                    "filename": f.filename,
                    "language": f.language,
                    "layer": f.layer_classification,
                    "hotspot_score": min(hotspot_score, 100),
                    "cyclomatic_complexity": cc,
                    "maintainability_index": mi,
                    "code_lines": cl,
                    "reasons": reasons,
                })

        hotspots.sort(key=lambda x: x["hotspot_score"], reverse=True)

        # 4. Technical Debt Estimation (Hours)
        debt_hours = 0.0
        debt_hours += len(cycles) * 2.0
        debt_hours += len(complex_fns) * 0.75
        debt_hours += len(large_files) * 1.5
        if doc_coverage < 15.0:
            debt_hours += (15.0 - doc_coverage) * 0.4

        debt_hours = round(debt_hours, 1)

        # 5. Overall Health Score Calculation (0 - 100)
        base_score = avg_mi * 0.65
        cycle_penalty = min(len(cycles) * 6.0, 30.0)
        cc_penalty = min(max(avg_cc - 2.0, 0.0) * 4.0, 20.0)
        health_score = round(max(min(base_score + 35.0 - cycle_penalty - cc_penalty, 100.0), 10.0), 1)

        if health_score >= 88.0:
            grade = "A"
        elif health_score >= 75.0:
            grade = "B"
        elif health_score >= 60.0:
            grade = "C"
        elif health_score >= 45.0:
            grade = "D"
        else:
            grade = "F"

        # 6. Actionable Recommendations
        recommendations: List[Dict[str, Any]] = []
        if cycles:
            recommendations.append({
                "category": "Architecture",
                "priority": "High",
                "title": f"Resolve {len(cycles)} Circular Dependency Loops",
                "detail": f"Circular imports create tight coupling. Break cycle between {cycles[0][0]} and {cycles[0][1]} using dependency injection or shared interfaces.",
            })
        if complex_fns:
            top_fn = complex_fns[0]
            recommendations.append({
                "category": "Refactoring",
                "priority": "Medium",
                "title": f"Decompose Complex Function '{top_fn['function_name']}'",
                "detail": f"Function has cyclomatic complexity of {top_fn['complexity']} in {top_fn['file_path']}. Extract sub-methods to simplify control flow.",
            })
        if large_files:
            recommendations.append({
                "category": "Modularity",
                "priority": "Medium",
                "title": f"Split {len(large_files)} Large Files",
                "detail": f"Files like {large_files[0].filename} exceed 250 LOC. Extract domain sub-modules to adhere to Single Responsibility Principle.",
            })
        if doc_coverage < 10.0:
            recommendations.append({
                "category": "Documentation",
                "priority": "Low",
                "title": "Enhance Public Interface Docstrings",
                "detail": f"Documentation coverage is {doc_coverage}%. Add docstrings and type annotations to core public service functions.",
            })

        # Save Health Metric Record
        metric_obj = HealthMetric(
            project_id=project_id,
            overall_health_score=health_score,
            maintainability_grade=grade,
            average_cyclomatic_complexity=avg_cc,
            max_cyclomatic_complexity=max_cc,
            average_maintainability_index=avg_mi,
            documentation_coverage_percent=doc_coverage,
            circular_dependency_cycles_count=len(cycles),
            large_files_count=len(large_files),
            complex_functions_count=len(complex_fns),
            estimated_technical_debt_hours=debt_hours,
            hotspots_json=json.dumps(hotspots[:30]),
            recommendations_json=json.dumps(recommendations),
            debt_breakdown_json=json.dumps({
                "cycles_debt_hours": len(cycles) * 2.0,
                "complexity_debt_hours": len(complex_fns) * 0.75,
                "structure_debt_hours": len(large_files) * 1.5,
            }),
        )
        self.health_repo.create(metric_obj)

        return {
            "project_id": project_id,
            "overall_health_score": health_score,
            "maintainability_grade": grade,
            "average_cyclomatic_complexity": avg_cc,
            "max_cyclomatic_complexity": max_cc,
            "average_maintainability_index": avg_mi,
            "documentation_coverage_percent": doc_coverage,
            "circular_dependency_cycles_count": len(cycles),
            "large_files_count": len(large_files),
            "complex_functions_count": len(complex_fns),
            "estimated_technical_debt_hours": debt_hours,
            "hotspots": hotspots[:30],
            "recommendations": recommendations,
            "clusters": [c.to_dict() for c in clusters],
        }
