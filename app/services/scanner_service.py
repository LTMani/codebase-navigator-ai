import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from app.models.base import db
from app.models.project import AnalysisRun, Project
from app.models.source_file import SourceFile, SourceFolder
from app.models.symbol import ClassDefinition, FunctionDefinition, ImportStatement, Symbol
from app.parsers.config_parser import ConfigParser
from app.parsers.manifest_parser import ManifestParser, ManifestParseResult
from app.parsers.parser_factory import ParserFactory


class ScannerService:
    """Recursively traverses imported codebase folders, extracts symbols via AST, and builds tree hierarchy."""

    IGNORED_DIRS: Set[str] = {
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        "coverage",
        "htmlcov",
        ".next",
        ".nuxt",
        ".cache",
        ".idea",
        ".vscode",
        ".DS_Store",
    }

    IGNORED_EXTENSIONS: Set[str] = {
        ".pyc",
        ".pyo",
        ".pyd",
        ".so",
        ".dll",
        ".dylib",
        ".exe",
        ".bin",
        ".iso",
        ".tar",
        ".gz",
        ".zip",
        ".7z",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp4",
        ".mp3",
        ".wav",
        ".pdf",
        ".db",
        ".sqlite",
        ".sqlite3",
    }

    @classmethod
    def calculate_file_hash(cls, content: str) -> str:
        """Generate sha256 hash of file content."""
        return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()

    def scan_and_parse_project(self, project: Project, project_dir: Path) -> Dict[str, Any]:
        """Perform full scan and parse across all files in project directory."""
        folders_map: Dict[str, SourceFolder] = {}
        source_files: List[SourceFile] = []
        all_symbols: List[Symbol] = []
        all_functions: List[FunctionDefinition] = []
        all_classes: List[ClassDefinition] = []
        all_imports: List[ImportStatement] = []

        manifest_results: List[ManifestParseResult] = []
        frameworks_detected: Set[str] = set()
        entry_points: List[Dict[str, Any]] = []

        total_lines = 0
        total_code_lines = 0
        total_comment_lines = 0
        total_blank_lines = 0
        total_bytes = 0
        language_stats: Dict[str, Dict[str, int]] = {}

        # 1. First pass: Collect folders and files
        for root_str, dirs, files in os.walk(project_dir):
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS and not d.startswith(".")]

            current_root = Path(root_str)
            rel_folder = current_root.relative_to(project_dir).as_posix()
            if rel_folder == ".":
                rel_folder = ""

            if rel_folder and rel_folder not in folders_map:
                depth = len(rel_folder.split("/"))
                name = current_root.name
                
                folder_obj = SourceFolder(
                    project_id=project.id,
                    relative_path=rel_folder,
                    name=name,
                    depth=depth,
                )
                folders_map[rel_folder] = folder_obj

            for file_name in files:
                file_path = current_root / file_name
                rel_path = file_path.relative_to(project_dir).as_posix()
                ext = file_path.suffix.lower()

                if ext in self.IGNORED_EXTENSIONS or file_name.startswith("."):
                    continue

                try:
                    file_size = file_path.stat().st_size
                except Exception:
                    file_size = 0

                if file_size > 5 * 1024 * 1024:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    content = ""

                if file_name.lower() in ("package.json", "requirements.txt", "pyproject.toml", "setup.py", "pipfile", "cargo.toml", "go.mod", "pom.xml", "composer.json"):
                    man_res = ManifestParser.parse_manifest(file_name, content)
                    manifest_results.append(man_res)
                    for fw in man_res.frameworks_detected:
                        frameworks_detected.add(fw)

                parse_res = ParserFactory.parse_file(content, rel_path)
                file_hash = self.calculate_file_hash(content)

                lang = parse_res.language
                if lang not in language_stats:
                    language_stats[lang] = {"files": 0, "lines": 0, "code": 0, "bytes": 0}

                m = parse_res.metrics
                language_stats[lang]["files"] += 1
                language_stats[lang]["lines"] += m.total_lines
                language_stats[lang]["code"] += m.code_lines
                language_stats[lang]["bytes"] += file_size

                total_lines += m.total_lines
                total_code_lines += m.code_lines
                total_comment_lines += m.comment_lines
                total_blank_lines += m.blank_lines
                total_bytes += file_size

                if parse_res.is_entry_point:
                    entry_points.append({
                        "file_path": rel_path,
                        "language": lang,
                        "type": "application_entry_point",
                    })

                # Create SourceFile Model
                source_file_obj = SourceFile(
                    project_id=project.id,
                    relative_path=rel_path,
                    filename=file_name,
                    extension=ext,
                    language=lang,
                    file_hash=file_hash,
                    size_bytes=file_size,
                    total_lines=m.total_lines,
                    code_lines=m.code_lines,
                    comment_lines=m.comment_lines,
                    blank_lines=m.blank_lines,
                    cyclomatic_complexity=m.cyclomatic_complexity,
                    cognitive_complexity=m.cognitive_complexity,
                    maintainability_index=m.maintainability_index,
                    documentation_ratio=m.documentation_ratio,
                    layer_classification=parse_res.layer_hint or "unclassified",
                    is_entry_point=parse_res.is_entry_point,
                    is_test_file=parse_res.is_test_file,
                    is_config_file=parse_res.is_config_file,
                    ast_parsed=len(parse_res.errors) == 0,
                    purpose_summary=parse_res.purpose_summary,
                )
                source_files.append(source_file_obj)

                # Link Symbols
                for sym in parse_res.symbols:
                    all_symbols.append(
                        Symbol(
                            project_id=project.id,
                            source_file=source_file_obj,
                            name=sym.name,
                            kind=sym.kind,
                            qualified_name=sym.qualified_name,
                            visibility=sym.visibility,
                            start_line=sym.start_line,
                            end_line=sym.end_line,
                            is_exported=sym.is_exported,
                            docstring=sym.docstring,
                        )
                    )

                # Link Functions
                for fn in parse_res.functions:
                    all_functions.append(
                        FunctionDefinition(
                            project_id=project.id,
                            source_file=source_file_obj,
                            name=fn.name,
                            qualified_name=fn.qualified_name,
                            start_line=fn.start_line,
                            end_line=fn.end_line,
                            line_count=fn.line_count,
                            parameters=[p.name if hasattr(p, "name") else str(p) for p in fn.parameters],
                            return_type=fn.return_type,
                            decorators=fn.decorators,
                            is_async=fn.is_async,
                            is_static=fn.is_static,
                            is_method=fn.is_method,
                            visibility=fn.visibility,
                            cyclomatic_complexity=fn.cyclomatic_complexity,
                            cognitive_complexity=fn.cognitive_complexity,
                            parameter_count=fn.parameter_count,
                            return_count=fn.return_count,
                            docstring=fn.docstring,
                            calls=fn.calls,
                        )
                    )

                # Link Classes
                for cls in parse_res.classes:
                    all_classes.append(
                        ClassDefinition(
                            project_id=project.id,
                            source_file=source_file_obj,
                            name=cls.name,
                            qualified_name=cls.qualified_name,
                            start_line=cls.start_line,
                            end_line=cls.end_line,
                            line_count=cls.line_count,
                            base_classes=cls.base_classes,
                            interfaces=cls.interfaces,
                            decorators=cls.decorators,
                            methods_count=len(cls.methods) or cls.methods_count,
                            docstring=cls.docstring,
                        )
                    )

                # Link Imports
                for imp in parse_res.imports:
                    all_imports.append(
                        ImportStatement(
                            project_id=project.id,
                            source_file=source_file_obj,
                            module_name=imp.module_name,
                            imported_symbols=imp.imported_symbols,
                            alias=imp.alias,
                            line_number=imp.line_number,
                            is_relative=imp.is_relative,
                            is_external=imp.is_external,
                        )
                    )

        # Update Project Summary Attributes
        project.file_count = len(source_files)
        project.folder_count = len(folders_map)
        project.total_lines = total_lines
        project.code_lines = total_code_lines
        project.comment_lines = total_comment_lines
        project.blank_lines = total_blank_lines
        project.languages = language_stats
        project.frameworks = sorted(list(frameworks_detected))
        project.entry_points = entry_points

        return {
            "folders": list(folders_map.values()),
            "source_files": source_files,
            "symbols": all_symbols,
            "functions": all_functions,
            "classes": all_classes,
            "imports": all_imports,
            "manifests": manifest_results,
            "frameworks": sorted(list(frameworks_detected)),
            "entry_points": entry_points,
        }

    def scan_project_directory(self, project: Project, directory_path: str) -> Tuple[AnalysisRun, List[SourceFile]]:
        """Scans local directory, persists database entities, and records an AnalysisRun."""
        start_time = time.time()
        res = self.scan_and_parse_project(project, Path(directory_path))

        db.session.add(project)
        for folder in res["folders"]:
            db.session.add(folder)
        for sf in res["source_files"]:
            db.session.add(sf)
        for sym in res["symbols"]:
            db.session.add(sym)
        for fn in res["functions"]:
            db.session.add(fn)
        for cls in res["classes"]:
            db.session.add(cls)
        for imp in res["imports"]:
            db.session.add(imp)

        duration_ms = int((time.time() - start_time) * 1000)
        run = AnalysisRun(
            project_id=project.id,
            trigger="cli/scan",
            status="completed",
            duration_ms=duration_ms,
            files_analyzed=len(res["source_files"]),
            symbols_extracted=len(res["symbols"]),
            dependencies_found=len(res["imports"]),
        )
        db.session.add(run)
        db.session.commit()

        return run, res["source_files"]
