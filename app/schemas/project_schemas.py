import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError


def slugify(text: str) -> str:
    """Generate a clean URL-friendly slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


@dataclass
class ProjectCreateSchema:
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    version: str = "1.0.0"
    is_public: bool = False
    slug: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectCreateSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a valid JSON object.")

        name = str(data.get("name", "")).strip()
        if not name:
            raise ValidationError("Project name is required.")
        if len(name) > 128:
            raise ValidationError("Project name cannot exceed 128 characters.")

        description = data.get("description")
        if description:
            description = str(description).strip()

        repository_url = data.get("repository_url")
        if repository_url:
            repository_url = str(repository_url).strip()

        version = str(data.get("version", "1.0.0")).strip()
        is_public = bool(data.get("is_public", False))

        slug = data.get("slug")
        if slug:
            slug = slugify(str(slug))
        else:
            slug = slugify(name)

        if not slug:
            slug = "project"

        return cls(
            name=name,
            description=description,
            repository_url=repository_url,
            version=version,
            is_public=is_public,
            slug=slug,
        )


@dataclass
class ProjectUpdateSchema:
    name: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None
    version: Optional[str] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectUpdateSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request payload must be a JSON object.")

        name = data.get("name")
        if name is not None:
            name = str(name).strip()
            if not name:
                raise ValidationError("Project name cannot be empty.")

        description = data.get("description")
        if description is not None:
            description = str(description).strip()

        repository_url = data.get("repository_url")
        if repository_url is not None:
            repository_url = str(repository_url).strip()

        version = data.get("version")
        if version is not None:
            version = str(version).strip()

        is_public = data.get("is_public")
        if is_public is not None:
            is_public = bool(is_public)

        is_favorite = data.get("is_favorite")
        if is_favorite is not None:
            is_favorite = bool(is_favorite)

        return cls(
            name=name,
            description=description,
            repository_url=repository_url,
            version=version,
            is_public=is_public,
            is_favorite=is_favorite,
        )
