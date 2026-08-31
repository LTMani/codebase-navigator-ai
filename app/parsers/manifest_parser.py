import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ManifestDependency:
    name: str
    version_spec: str
    is_dev: bool = False
    source_manifest: str = ""
    category: str = "runtime"  # runtime, dev, peer, optional


@dataclass
class ManifestParseResult:
    manifest_type: str  # npm, pip, poetry, cargo, go, maven, gradle, composer
    project_name: Optional[str] = None
    project_version: Optional[str] = None
    description: Optional[str] = None
    dependencies: List[ManifestDependency] = field(default_factory=list)
    scripts: Dict[str, str] = field(default_factory=dict)
    frameworks_detected: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ManifestParser:
    """Universal package and dependency manifest parser supporting all major ecosystems."""

    FRAMEWORK_SIGNATURES = {
        "react": "React",
        "react-dom": "React",
        "vue": "Vue.js",
        "@angular/core": "Angular",
        "svelte": "Svelte",
        "next": "Next.js",
        "nuxt": "Nuxt.js",
        "express": "Express",
        "fastify": "Fastify",
        "koa": "Koa",
        "nestjs": "NestJS",
        "@nestjs/core": "NestJS",
        "electron": "Electron",
        "tailwindcss": "Tailwind CSS",
        "flask": "Flask",
        "django": "Django",
        "fastapi": "FastAPI",
        "tornado": "Tornado",
        "sqlalchemy": "SQLAlchemy",
        "celery": "Celery",
        "pytest": "pytest",
        "spring-boot": "Spring Boot",
        "gin-gonic": "Gin",
        "fiber": "Fiber",
    }

    @classmethod
    def parse_manifest(cls, file_name: str, content: str) -> ManifestParseResult:
        """Parse package manifest file by its recognized filename."""
        fn = file_name.lower()
        if fn == "package.json":
            return cls.parse_package_json(content)
        elif fn in ("requirements.txt", "requirements-dev.txt", "requirements-prod.txt"):
            return cls.parse_requirements_txt(content, fn)
        elif fn == "pyproject.toml":
            return cls.parse_pyproject_toml(content)
        elif fn == "setup.py":
            return cls.parse_setup_py(content)
        elif fn == "pipfile":
            return cls.parse_pipfile(content)
        elif fn == "cargo.toml":
            return cls.parse_cargo_toml(content)
        elif fn == "go.mod":
            return cls.parse_go_mod(content)
        elif fn in ("pom.xml", "build.gradle", "composer.json"):
            return cls.parse_generic_manifest(content, fn)
        else:
            return ManifestParseResult(manifest_type="unknown")

    @classmethod
    def parse_package_json(cls, content: str) -> ManifestParseResult:
        """Parse Node.js / JavaScript package.json."""
        result = ManifestParseResult(manifest_type="npm")
        try:
            data = json.loads(content)
            result.project_name = data.get("name")
            result.project_version = data.get("version")
            result.description = data.get("description")
            result.scripts = data.get("scripts", {})

            # Runtime Dependencies
            for pkg, ver in data.get("dependencies", {}).items():
                result.dependencies.append(
                    ManifestDependency(name=pkg, version_spec=str(ver), is_dev=False, source_manifest="package.json")
                )
                if pkg in cls.FRAMEWORK_SIGNATURES:
                    result.frameworks_detected.append(cls.FRAMEWORK_SIGNATURES[pkg])

            # Dev Dependencies
            for pkg, ver in data.get("devDependencies", {}).items():
                result.dependencies.append(
                    ManifestDependency(name=pkg, version_spec=str(ver), is_dev=True, source_manifest="package.json")
                )
                if pkg in cls.FRAMEWORK_SIGNATURES:
                    result.frameworks_detected.append(cls.FRAMEWORK_SIGNATURES[pkg])

            # Peer Dependencies
            for pkg, ver in data.get("peerDependencies", {}).items():
                result.dependencies.append(
                    ManifestDependency(name=pkg, version_spec=str(ver), is_dev=False, source_manifest="package.json", category="peer")
                )

            result.frameworks_detected = sorted(list(set(result.frameworks_detected)))
            result.metadata = {
                "author": data.get("author"),
                "license": data.get("license"),
                "main": data.get("main"),
                "type": data.get("type", "commonjs"),
            }
        except Exception:
            pass
        return result

    @classmethod
    def parse_requirements_txt(cls, content: str, filename: str = "requirements.txt") -> ManifestParseResult:
        """Parse Python pip requirements.txt."""
        result = ManifestParseResult(manifest_type="pip")
        is_dev = "dev" in filename.lower()

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r") or line.startswith("-i"):
                continue

            # Split on operators ==, >=, <=, ~=, !=, <, >
            match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([=><~^!].*)?$", line)
            if match:
                pkg = match.group(1).strip()
                ver = match.group(2).strip() if match.group(2) else "*"
                result.dependencies.append(
                    ManifestDependency(name=pkg, version_spec=ver, is_dev=is_dev, source_manifest=filename)
                )
                pkg_lower = pkg.lower()
                if pkg_lower in cls.FRAMEWORK_SIGNATURES:
                    result.frameworks_detected.append(cls.FRAMEWORK_SIGNATURES[pkg_lower])

        result.frameworks_detected = sorted(list(set(result.frameworks_detected)))
        return result

    @classmethod
    def parse_pyproject_toml(cls, content: str) -> ManifestParseResult:
        """Parse PEP 621 / Poetry pyproject.toml."""
        result = ManifestParseResult(manifest_type="poetry")
        
        # Simple regex-based TOML parsing to avoid heavy external dependencies
        in_deps = False
        in_dev_deps = False

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("["):
                header = line.lower()
                in_deps = "dependencies" in header and "dev" not in header
                in_dev_deps = "dev-dependencies" in header or "group.dev.dependencies" in header or "optional-dependencies" in header
                continue

            if "=" in line and (in_deps or in_dev_deps):
                parts = line.split("=", 1)
                pkg = parts[0].strip().strip('"').strip("'")
                ver = parts[1].strip().strip('"').strip("'").strip(",")
                if pkg and not pkg.startswith("["):
                    result.dependencies.append(
                        ManifestDependency(
                            name=pkg,
                            version_spec=ver,
                            is_dev=in_dev_deps,
                            source_manifest="pyproject.toml",
                        )
                    )
                    pkg_lower = pkg.lower()
                    if pkg_lower in cls.FRAMEWORK_SIGNATURES:
                        result.frameworks_detected.append(cls.FRAMEWORK_SIGNATURES[pkg_lower])

        result.frameworks_detected = sorted(list(set(result.frameworks_detected)))
        return result

    @classmethod
    def parse_setup_py(cls, content: str) -> ManifestParseResult:
        """Extract install_requires from setup.py."""
        result = ManifestParseResult(manifest_type="setuptools")
        req_match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if req_match:
            block = req_match.group(1)
            for item in re.findall(r"['\"]([^'\"]+)['\"]", block):
                match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([=><~^!].*)?$", item.strip())
                if match:
                    pkg = match.group(1).strip()
                    ver = match.group(2).strip() if match.group(2) else "*"
                    result.dependencies.append(
                        ManifestDependency(name=pkg, version_spec=ver, is_dev=False, source_manifest="setup.py")
                    )
                    if pkg.lower() in cls.FRAMEWORK_SIGNATURES:
                        result.frameworks_detected.append(cls.FRAMEWORK_SIGNATURES[pkg.lower()])
        result.frameworks_detected = sorted(list(set(result.frameworks_detected)))
        return result

    @classmethod
    def parse_pipfile(cls, content: str) -> ManifestParseResult:
        """Parse Pipenv Pipfile."""
        result = ManifestParseResult(manifest_type="pipenv")
        in_packages = False
        in_dev_packages = False

        for line in content.splitlines():
            line = line.strip()
            if line == "[packages]":
                in_packages = True
                in_dev_packages = False
                continue
            elif line == "[dev-packages]":
                in_packages = False
                in_dev_packages = True
                continue
            elif line.startswith("["):
                in_packages = False
                in_dev_packages = False
                continue

            if (in_packages or in_dev_packages) and "=" in line:
                parts = line.split("=", 1)
                pkg = parts[0].strip().strip('"').strip("'")
                ver = parts[1].strip().strip('"').strip("'")
                result.dependencies.append(
                    ManifestDependency(name=pkg, version_spec=ver, is_dev=in_dev_packages, source_manifest="Pipfile")
                )
                if pkg.lower() in cls.FRAMEWORK_SIGNATURES:
                    result.frameworks_detected.append(cls.FRAMEWORK_SIGNATURES[pkg.lower()])

        result.frameworks_detected = sorted(list(set(result.frameworks_detected)))
        return result

    @classmethod
    def parse_cargo_toml(cls, content: str) -> ManifestParseResult:
        """Parse Rust Cargo.toml."""
        result = ManifestParseResult(manifest_type="cargo")
        in_deps = False
        in_dev_deps = False

        for line in content.splitlines():
            line = line.strip()
            if line == "[dependencies]":
                in_deps = True
                in_dev_deps = False
                continue
            elif line in ("[dev-dependencies]", "[build-dependencies]"):
                in_deps = False
                in_dev_deps = True
                continue
            elif line.startswith("["):
                in_deps = False
                in_dev_deps = False
                continue

            if (in_deps or in_dev_deps) and "=" in line:
                parts = line.split("=", 1)
                pkg = parts[0].strip()
                ver = parts[1].strip().strip('"').strip("'")
                result.dependencies.append(
                    ManifestDependency(name=pkg, version_spec=ver, is_dev=in_dev_deps, source_manifest="Cargo.toml")
                )

        return result

    @classmethod
    def parse_go_mod(cls, content: str) -> ManifestParseResult:
        """Parse Go go.mod."""
        result = ManifestParseResult(manifest_type="go")
        in_require = False

        for line in content.splitlines():
            line = line.strip()
            if line.startswith("module "):
                result.project_name = line.split(" ", 1)[1].strip()
                continue
            if line.startswith("require ("):
                in_require = True
                continue
            if in_require and line == ")":
                in_require = False
                continue

            if in_require or line.startswith("require "):
                raw = line.replace("require ", "").strip()
                parts = raw.split()
                if len(parts) >= 2:
                    pkg = parts[0].strip()
                    ver = parts[1].strip()
                    result.dependencies.append(
                        ManifestDependency(name=pkg, version_spec=ver, is_dev=False, source_manifest="go.mod")
                    )
                    if "gin-gonic/gin" in pkg:
                        result.frameworks_detected.append("Gin")
                    elif "gofiber/fiber" in pkg:
                        result.frameworks_detected.append("Fiber")

        result.frameworks_detected = sorted(list(set(result.frameworks_detected)))
        return result

    @classmethod
    def parse_generic_manifest(cls, content: str, filename: str) -> ManifestParseResult:
        """Fallback manifest parser for Maven pom.xml, Gradle, Composer."""
        result = ManifestParseResult(manifest_type="generic")
        if "composer.json" in filename:
            try:
                data = json.loads(content)
                result.project_name = data.get("name")
                for pkg, ver in data.get("require", {}).items():
                    result.dependencies.append(
                        ManifestDependency(name=pkg, version_spec=str(ver), is_dev=False, source_manifest="composer.json")
                    )
            except Exception:
                pass
        elif "pom.xml" in filename:
            for match in re.finditer(r"<artifactId>([^<]+)</artifactId>", content):
                artifact = match.group(1).strip()
                result.dependencies.append(
                    ManifestDependency(name=artifact, version_spec="*", is_dev=False, source_manifest="pom.xml")
                )
                if "spring-boot" in artifact:
                    result.frameworks_detected.append("Spring Boot")
        return result
