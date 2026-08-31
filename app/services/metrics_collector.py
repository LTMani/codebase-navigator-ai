from collections import defaultdict
from typing import Any, Dict, List, Optional
from app.models.source_file import SourceFile
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository


class MetricsCollector:
    """Calculates Martin's Package Coupling Metrics (Ca, Ce, I, A, D) and cohesion indicators."""

    def __init__(
        self,
        file_repo: Optional[FileRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
    ):
        self.file_repo = file_repo or FileRepository()
        self.dep_repo = dep_repo or DependencyRepository()

    def collect_package_metrics(self, project_id: str) -> Dict[str, Any]:
        """Compute architectural stability and distance from main sequence for all packages."""
        source_files = self.file_repo.get_all_by_project(project_id)
        edges = self.dep_repo.get_by_project(project_id)

        # 1. Group files by top-level package / module directory
        package_files: Dict[str, List[SourceFile]] = defaultdict(list)
        file_to_pkg: Dict[str, str] = {}

        for sf in source_files:
            parts = sf.relative_path.split("/")
            pkg = parts[0] if len(parts) > 1 else "root"
            package_files[pkg].append(sf)
            file_to_pkg[sf.relative_path] = pkg

        # 2. Compute Ca (Afferent Coupling) and Ce (Efferent Coupling)
        ca_map: Dict[str, set] = defaultdict(set)
        ce_map: Dict[str, set] = defaultdict(set)

        for edge in edges:
            src_pkg = file_to_pkg.get(edge.source_path, "root")
            tgt_pkg = file_to_pkg.get(edge.target_path, "root")

            if src_pkg != tgt_pkg and not edge.is_external:
                # src depends on tgt -> src has efferent, tgt has afferent
                ce_map[src_pkg].add(tgt_pkg)
                ca_map[tgt_pkg].add(src_pkg)

        packages_report: List[Dict[str, Any]] = []

        for pkg_name, files in package_files.items():
            ca = len(ca_map.get(pkg_name, set()))
            ce = len(ce_map.get(pkg_name, set()))

            # Instability I = Ce / (Ca + Ce)
            total_coupling = ca + Ce
            instability = round(Ce / total_coupling, 3) if total_coupling > 0 else 0.0

            # Abstractness A = Abstract Classes / Total Classes
            total_classes = sum(len(f.classes) for f in files)
            # Interfaces or Base classes treated as abstract
            abstract_classes = sum(
                len([c for c in f.classes if "abstract" in c.name.lower() or "base" in c.name.lower() or "interface" in c.name.lower()])
                for f in files
            )
            abstractness = round(abstract_classes / max(total_classes, 1), 3) if total_classes > 0 else 0.0

            # Distance from Main Sequence: D = |A + I - 1|
            distance = round(abs(abstractness + instability - 1.0), 3)

            zone = "Main Sequence"
            if distance > 0.6:
                if instability < 0.3 and abstractness < 0.3:
                    zone = "Zone of Pain (Rigid / Hard to change)"
                elif instability > 0.7 and abstractness > 0.7:
                    zone = "Zone of Uselessness (Over-abstracted)"

            packages_report.append({
                "package_name": pkg_name,
                "file_count": len(files),
                "afferent_coupling_ca": ca,
                "efferent_coupling_ce": ce,
                "instability_i": instability,
                "abstractness_a": abstractness,
                "distance_d": distance,
                "architectural_zone": zone,
            })

        packages_report.sort(key=lambda x: x["distance_d"], reverse=True)

        return {
            "project_id": project_id,
            "packages_count": len(packages_report),
            "packages": packages_report,
        }
