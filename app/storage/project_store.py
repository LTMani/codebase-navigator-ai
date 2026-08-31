from typing import Any, Dict, Optional

class ProjectStore:
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, project_id: str) -> Optional[Dict[str, Any]]:
        if project_id in cls._cache:
            return cls._cache[project_id]
        try:
            from app.repositories.project_repository import ProjectRepository
            from app.repositories.file_repository import FileRepository
            repo = ProjectRepository()
            proj = repo.find_by_id(project_id)
            if not proj:
                return None
            file_repo = FileRepository()
            files = file_repo.find_by_project_id(project_id)
            return {
                'id': proj.id,
                'name': proj.name,
                'files_data': [{
                    'file_path': getattr(f, 'relative_path', ''),
                    'content': getattr(f, 'content', '') or '',
                    'language': getattr(f, 'language', ''),
                    'imports': [],
                    'functions': [],
                    'classes': []
                } for f in files]
            }
        except Exception:
            return cls._cache.get(project_id)

    @classmethod
    def set(cls, project_id: str, data: Dict[str, Any]):
        cls._cache[project_id] = data
