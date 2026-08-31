#!/usr/bin/env python3
"""
CodeBase Navigator AI - Interactive Command Line Interface (CLI)
Analyze, understand, and navigate software codebases directly from the terminal.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from app import create_app
from app.models.project import Project
from app.models.user import User
from app.parsers.parser_factory import ParserFactory
from app.repositories.file_repository import FileRepository
from app.repositories.project_repository import ProjectRepository
from app.services.architecture_service import ArchitectureService
from app.services.dependency_service import DependencyService
from app.services.export_service import ExportService
from app.services.health_service import HealthService
from app.services.impact_service import ImpactService
from app.services.onboarding_service import OnboardingService
from app.services.project_service import ProjectService
from app.services.scanner_service import ScannerService
from app.services.search_service import SearchService


def print_banner():
    print("=" * 70)
    print("  CODEBASE NAVIGATOR AI - CLI CODE INTELLIGENCE ENGINE")
    print("  Understand Any Codebase. Navigate with Intelligence.")
    print("=" * 70)


def handle_scan(args):
    """Scan and index a local source code directory."""
    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"❌ Error: Path '{target_path}' does not exist.")
        sys.exit(1)

    print(f"🚀 Scanning directory: {target_path}")
    flask_app = create_app("testing")

    with flask_app.app_context():
        proj_service = ProjectService()
        scanner = ScannerService()
        proj_repo = ProjectRepository()

        # Create or fetch project
        proj_name = args.name or os.path.basename(target_path) or "Local Project"
        project = proj_repo.get_by_slug(proj_name.lower().replace(" ", "-"))

        if not project:
            user = User(username="cli_admin", email="cli@navigator.ai")
            user.set_password("Admin@1234")
            project = Project(
                name=proj_name,
                slug=proj_name.lower().replace(" ", "-"),
                storage_path=target_path,
                user_id="cli_user_id",
            )
            proj_repo.create(project)
        else:
            project.storage_path = target_path

        run, files = scanner.scan_project_directory(project, target_path)

        print("✅ Scan Completed Successfully!")
        print(f"   Files Parsed: {len(files):,}")
        print(f"   Total Lines:  {project.total_lines:,}")
        print(f"   Languages:    {', '.join(project.languages.keys())}")
        if project.frameworks:
            print(f"   Frameworks:   {', '.join(project.frameworks)}")


def handle_health(args):
    """Audit health metrics, complexity hotspots, and technical debt."""
    target_path = os.path.abspath(args.path)
    flask_app = create_app("testing")

    with flask_app.app_context():
        scanner = ScannerService()
        proj_repo = ProjectRepository()
        health_service = HealthService()

        proj_name = os.path.basename(target_path)
        project = proj_repo.get_by_slug(proj_name.lower().replace(" ", "-"))
        if not project:
            project = Project(name=proj_name, slug=proj_name.lower().replace(" ", "-"), storage_path=target_path, user_id="cli")
            proj_repo.create(project)
            scanner.scan_project_directory(project, target_path)

        health = health_service.evaluate_code_health(project.id)

        print("\n🩺 CODEBASE HEALTH AUDIT")
        print("-" * 50)
        print(f"  Overall Health Score:     {health['overall_health_score']} / 100")
        print(f"  Maintainability Grade:    {health['maintainability_grade']}")
        print(f"  Avg Cyclomatic Complexity: {health['average_cyclomatic_complexity']}")
        print(f"  Avg Maintainability Index: {health['average_maintainability_index']} / 100")
        print(f"  Documentation Coverage:   {health['documentation_coverage_percent']}%")
        print(f"  Circular Cycles Detected: {health['circular_dependency_cycles_count']}")
        print(f"  Estimated Technical Debt: {health['estimated_technical_debt_hours']} remediation hours")

        if health.get("hotspots"):
            print("\n🔥 Top Complexity Hotspots:")
            for h in health["hotspots"][:5]:
                print(f"   - {h['file_path']} (Score: {h['hotspot_score']} pts, CC: {h['cyclomatic_complexity']}, MI: {h['maintainability_index']})")


def handle_report(args):
    """Generate Markdown architecture & health report."""
    target_path = os.path.abspath(args.path)
    flask_app = create_app("testing")

    with flask_app.app_context():
        scanner = ScannerService()
        proj_repo = ProjectRepository()
        export_service = ExportService()

        proj_name = os.path.basename(target_path)
        project = proj_repo.get_by_slug(proj_name.lower().replace(" ", "-"))
        if not project:
            project = Project(name=proj_name, slug=proj_name.lower().replace(" ", "-"), storage_path=target_path, user_id="cli")
            proj_repo.create(project)
            scanner.scan_project_directory(project, target_path)

        report = export_service.generate_full_report(project.id, format_type="markdown")
        output_file = args.output or f"{project.slug}_report.md"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report["content"])

        print(f"✅ Architecture report saved to: {os.path.abspath(output_file)}")


def main():
    parser = argparse.ArgumentParser(
        description="CodeBase Navigator AI - Understand Any Codebase with Intelligence."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # scan
    scan_p = subparsers.add_parser("scan", help="Scan and index a codebase directory")
    scan_p.add_argument("path", help="Path to source code directory")
    scan_p.add_argument("--name", help="Custom project name")

    # health
    health_p = subparsers.add_parser("health", help="Audit codebase health and technical debt")
    health_p.add_argument("path", help="Path to source code directory")

    # report
    report_p = subparsers.add_parser("report", help="Generate full markdown architecture report")
    report_p.add_argument("path", help="Path to source code directory")
    report_p.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    print_banner()

    if args.command == "scan":
        handle_scan(args)
    elif args.command == "health":
        handle_health(args)
    elif args.command == "report":
        handle_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
