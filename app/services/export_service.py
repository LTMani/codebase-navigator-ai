from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.services.architecture_service import ArchitectureService
from app.services.dependency_service import DependencyService
from app.services.health_service import HealthService
from app.services.onboarding_service import OnboardingService


class ExportService:
    """Generates structured architecture documentation, health audits, and compliance reports."""

    def __init__(self, project_repo: Optional[ProjectRepository] = None):
        self.project_repo = project_repo or ProjectRepository()
        self.health_service = HealthService()
        self.arch_service = ArchitectureService()
        self.dep_service = DependencyService()
        self.onboarding_service = OnboardingService()

    def generate_full_report(self, project_id: str, format_type: str = "markdown") -> Dict[str, Any]:
        """Generate comprehensive architectural report in Markdown, JSON, or HTML format."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return {"error": "Project not found"}

        health_data = self.health_service.evaluate_code_health(project_id)
        arch_data = self.arch_service.analyze_architecture(project_id)
        dep_data = self.dep_service.build_dependency_graph(project_id)
        onboard_data = self.onboarding_service.generate_onboarding_plan(project_id)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        if format_type.lower() == "json":
            return {
                "project": project.to_dict(),
                "generated_at": now_str,
                "health": health_data,
                "architecture": arch_data,
                "dependencies_summary": {
                    "nodes": dep_data["nodes_count"],
                    "edges": dep_data["edges_count"],
                    "cycles": dep_data["circular_cycles_count"],
                },
                "onboarding": onboard_data,
            }

        # Generate Markdown Report
        md_lines = [
            f"# CodeBase Navigator AI - Architecture & Health Audit Report",
            f"**Project**: {project.name} (v{project.version})  ",
            f"**Generated**: {now_str}  ",
            f"**Overall Code Health**: Grade **{health_data.get('maintainability_grade', 'A')}** ({health_data.get('overall_health_score', 100)} / 100)  ",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            onboard_data.get("executive_summary", "No executive summary available."),
            "",
            "### Codebase Metrics",
            f"- **Total Files**: {project.file_count}",
            f"- **Total Directories**: {project.folder_count}",
            f"- **Total Lines of Code**: {project.total_lines:,} ({project.code_lines:,} code, {project.comment_lines:,} comments)",
            f"- **Average Maintainability Index**: {health_data.get('average_maintainability_index', 100)} / 100",
            f"- **Average Cyclomatic Complexity**: {health_data.get('average_cyclomatic_complexity', 1.0)}",
            f"- **Estimated Technical Debt**: {health_data.get('estimated_technical_debt_hours', 0.0)} remediation hours",
            "",
            "---",
            "",
            "## 2. Architectural Layers & Structure",
            onboard_data.get("architecture_overview", ""),
            "",
            "| Layer | Component | Files | Confidence |",
            "|---|---|---|---|",
        ]

        for layer in arch_data.get("layers", []):
            md_lines.append(f"| {layer.get('layer_name', '').title()} | {layer.get('component_name', '')} | {layer.get('file_count', 0)} | {int(layer.get('confidence_score', 0) * 100)}% |")

        md_lines.extend([
            "",
            "---",
            "",
            "## 3. Dependency & Cycle Analysis",
            f"- **Graph Nodes**: {dep_data.get('nodes_count', 0)}",
            f"- **Dependency Edges**: {dep_data.get('edges_count', 0)}",
            f"- **Circular Dependency Loops Detected**: {dep_data.get('circular_cycles_count', 0)}",
            "",
        ])

        if dep_data.get("cycles"):
            md_lines.append("### Circular Dependency Paths")
            for c in dep_data["cycles"][:5]:
                md_lines.append(f"- `{' -> '.join(c)} -> {c[0]}`")
            md_lines.append("")

        md_lines.extend([
            "---",
            "",
            "## 4. Suggested Developer Reading Path",
            "Priority reading order determined by entry points and PageRank centrality:",
            "",
        ])

        for item in onboard_data.get("reading_path", [])[:8]:
            md_lines.append(f"{item.get('order')}. **{item.get('file_path')}** ({item.get('layer', '').title()} layer) - *{item.get('reason')}*")

        md_lines.extend([
            "",
            "---",
            "",
            "## 5. Actionable Recommendations",
            "",
        ])

        for rec in health_data.get("recommendations", []):
            md_lines.append(f"### [{rec.get('priority', 'Normal')}] {rec.get('title')}")
            md_lines.append(rec.get("detail", ""))
            md_lines.append("")

        report_content = "\n".join(md_lines)
        return {
            "format": "markdown",
            "filename": f"{project.slug}_architecture_report.md",
            "content": report_content,
        }
