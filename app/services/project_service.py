import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from werkzeug.datastructures import FileStorage
from app.errors.exceptions import ArchiveExtractionError, ConflictError, NotFoundError, ValidationError
from app.extensions import db
from app.models.project import AnalysisRun, Project
from app.repositories.architecture_repository import ArchitectureRepository
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.flow_repository import FlowRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.impact_repository import ImpactRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.symbol_repository import SymbolRepository
from app.schemas.project_schemas import ProjectCreateSchema, ProjectUpdateSchema
from app.security.archive_validator import ArchiveValidator
from app.services.scanner_service import ScannerService


class ProjectService:
    """Business logic for project registration, archive upload extraction, and lifecycle management."""

    def __init__(
        self,
        project_repo: Optional[ProjectRepository] = None,
        file_repo: Optional[FileRepository] = None,
        symbol_repo: Optional[SymbolRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
        arch_repo: Optional[ArchitectureRepository] = None,
        flow_repo: Optional[FlowRepository] = None,
        impact_repo: Optional[ImpactRepository] = None,
        health_repo: Optional[HealthRepository] = None,
        onboarding_repo: Optional[OnboardingRepository] = None,
    ):
        self.project_repo = project_repo or ProjectRepository()
        self.file_repo = file_repo or FileRepository()
        self.symbol_repo = symbol_repo or SymbolRepository()
        self.dep_repo = dep_repo or DependencyRepository()
        self.arch_repo = arch_repo or ArchitectureRepository()
        self.flow_repo = flow_repo or FlowRepository()
        self.impact_repo = impact_repo or ImpactRepository()
        self.health_repo = health_repo or HealthRepository()
        self.onboarding_repo = onboarding_repo or OnboardingRepository()
        self.scanner_service = ScannerService()

    def create_project(self, schema: ProjectCreateSchema, owner_id: str, storage_base_dir: Path) -> Project:
        """Register a new project record and allocate storage directory."""
        if self.project_repo.slug_exists(schema.slug):
            # Append random suffix if slug collision occurs
            import uuid
            schema.slug = f"{schema.slug}-{uuid.uuid4().hex[:6]}"

        project_dir = storage_base_dir / "extracted" / schema.slug
        project_dir.mkdir(parents=True, exist_ok=True)

        project = Project(
            name=schema.name,
            slug=schema.slug,
            description=schema.description,
            repository_url=schema.repository_url,
            version=schema.version,
            owner_id=owner_id,
            is_public=schema.is_public,
            storage_path=str(project_dir),
            status="pending",
        )
        return self.project_repo.create(project)

    def upload_and_extract_archive(
        self,
        project_id: str,
        file_storage: FileStorage,
        upload_dir: Path,
        extract_base_dir: Path,
    ) -> Dict[str, Any]:
        """Safely save uploaded project archive and extract contents."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found.")

        filename = file_storage.filename or "archive.zip"
        fn_lower = filename.lower()

        if not (fn_lower.endswith(".zip") or fn_lower.endswith(".tar.gz") or fn_lower.endswith(".tgz") or fn_lower.endswith(".tar")):
            raise ValidationError("Unsupported archive format. Please upload .zip, .tar.gz, or .tar files.")

        upload_dir.mkdir(parents=True, exist_ok=True)
        dest_extract_dir = extract_base_dir / project.id
        dest_extract_dir.mkdir(parents=True, exist_ok=True)

        # Save archive file
        archive_path = upload_dir / f"{project.id}_{filename}"
        file_storage.save(str(archive_path))

        # Safely extract archive
        extracted_files: List[str] = []
        if fn_lower.endswith(".zip"):
            extracted_files = ArchiveValidator.extract_zip(archive_path, dest_extract_dir)
        else:
            extracted_files = ArchiveValidator.extract_tar(archive_path, dest_extract_dir)

        # Update Project record with path
        project.storage_path = str(dest_extract_dir)
        project.archive_filename = filename
        project.status = "scanning"
        self.project_repo.update(project)

        return {
            "project_id": project.id,
            "archive_filename": filename,
            "extracted_files_count": len(extracted_files),
            "destination": str(dest_extract_dir),
        }

    def scan_and_index_project(self, project_id: str) -> Dict[str, Any]:
        """Execute scan and AST parsing for an extracted project directory."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found.")

        project_dir = Path(project.storage_path)
        if not project_dir.exists():
            raise NotFoundError(f"Project storage directory does not exist at '{project.storage_path}'.")

        # Clear existing parsed database entities for clean re-analysis
        self.symbol_repo.delete_by_project(project.id)
        self.file_repo.delete_by_project(project.id)

        # Run scanner
        scan_data = self.scanner_service.scan_and_parse_project(project, project_dir)

        # Persist folders
        folders = scan_data["folders"]
        if folders:
            db.session.add_all(folders)

        # Persist source files, symbols, functions, classes, imports
        source_files = scan_data["source_files"]
        if source_files:
            db.session.add_all(source_files)

        symbols = scan_data["symbols"]
        if symbols:
            db.session.add_all(symbols)

        functions = scan_data["functions"]
        if functions:
            db.session.add_all(functions)

        classes = scan_data["classes"]
        if classes:
            db.session.add_all(classes)

        imports = scan_data["imports"]
        if imports:
            db.session.add_all(imports)

        project.status = "analyzed"
        project.status_message = "Scan and AST parsing complete."
        project.last_analyzed_at = datetime.now(timezone.utc).isoformat()
        db.session.commit()

        return {
            "project_id": project.id,
            "status": project.status,
            "file_count": len(source_files),
            "folder_count": len(folders),
            "total_lines": project.total_lines,
            "symbols_count": len(symbols),
            "functions_count": len(functions),
            "classes_count": len(classes),
            "languages": project.languages,
            "frameworks": project.frameworks,
            "entry_points": project.entry_points,
        }

    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Fetch full project overview and metrics."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found.")
        return project.to_dict()

    def list_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """List all projects owned by user."""
        projects = self.project_repo.get_by_owner(user_id)
        return [p.to_dict() for p in projects]

    def delete_project(self, project_id: str) -> bool:
        """Delete project and remove its filesystem directories."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found.")

        # Clean storage
        if project.storage_path and Path(project.storage_path).exists():
            try:
                shutil.rmtree(project.storage_path, ignore_errors=True)
            except Exception:
                pass

        return self.project_repo.delete(project)
