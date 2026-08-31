from collections import defaultdict
from typing import Any, Dict, List, Optional
from app.models.source_file import SourceFile
from app.repositories.architecture_repository import ArchitectureRepository
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.symbol_repository import SymbolRepository
from app.services.dependency_service import DependencyService


class KnowledgeMapService:
    """Generates high-level conceptual knowledge maps connecting domains, services, and core concepts."""

    def __init__(
        self,
        file_repo: Optional[FileRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
        symbol_repo: Optional[SymbolRepository] = None,
        arch_repo: Optional[ArchitectureRepository] = None,
    ):
        self.file_repo = file_repo or FileRepository()
        self.dep_repo = dep_repo or DependencyRepository()
        self.symbol_repo = symbol_repo or SymbolRepository()
        self.arch_repo = arch_repo or ArchitectureRepository()
        self.dep_service = DependencyService()

    def generate_knowledge_map(self, project_id: str) -> Dict[str, Any]:
        """Synthesize high-level domain clusters, key abstraction nodes, and relationship links."""
        source_files = self.file_repo.get_all_by_project(project_id)
        edges = self.dep_repo.get_by_project(project_id)
        dep_data = self.dep_service.build_dependency_graph(project_id)
        nodes_by_path = {n["path"]: n for n in dep_data.get("nodes", [])}

        # 1. Group files by Domain / Subdirectory
        domain_clusters: Dict[str, List[SourceFile]] = defaultdict(list)
        for f in source_files:
            parts = f.relative_path.split("/")
            domain_name = parts[0] if len(parts) > 1 else "root"
            domain_clusters[domain_name].append(f)

        cluster_nodes = []
        for d_name, files in domain_clusters.items():
            primary_layer = files[0].layer_classification if files else "general"
            total_lines = sum(f.total_lines for f in files)
            avg_mi = sum(f.maintainability_index for f in files) / max(len(files), 1)

            # Find top abstraction in this domain
            top_symbols = []
            for f in files:
                for cls in f.classes:
                    top_symbols.append(cls.name)
                for fn in f.functions[:2]:
                    top_symbols.append(fn.name)

            cluster_nodes.append({
                "id": f"domain_{d_name}",
                "name": d_name.title(),
                "type": "domain_cluster",
                "layer": primary_layer,
                "file_count": len(files),
                "total_lines": total_lines,
                "maintainability": round(avg_mi, 1),
                "key_abstractions": top_symbols[:5],
            })

        # 2. Key Concept Nodes (Classes & Hub Modules with high PageRank)
        concept_nodes = []
        for f in source_files:
            pr = nodes_by_path.get(f.relative_path, {}).get("pagerank", 0.0)
            if pr > 0.4 or f.is_entry_point or len(f.classes) > 0:
                for cls in f.classes:
                    concept_nodes.append({
                        "id": f"cls_{cls.id}",
                        "name": cls.name,
                        "type": "class",
                        "file_path": f.relative_path,
                        "layer": f.layer_classification,
                        "base_classes": cls.base_classes,
                        "methods_count": cls.methods_count,
                        "pagerank": pr,
                    })

        # 3. Inter-Domain Cross-Links
        cluster_links: Dict[Tuple[str, str], int] = defaultdict(int)
        for e in edges:
            src_domain = e.source_path.split("/")[0] if "/" in e.source_path else "root"
            tgt_domain = e.target_path.split("/")[0] if "/" in e.target_path else "root"
            if src_domain != tgt_domain and not e.is_external:
                cluster_links[(src_domain, tgt_domain)] += 1

        links = [
            {
                "source": f"domain_{src}",
                "target": f"domain_{tgt}",
                "weight": w,
            }
            for (src, tgt), w in cluster_links.items()
        ]

        return {
            "project_id": project_id,
            "domain_clusters": cluster_nodes,
            "key_concepts": concept_nodes[:25],
            "relationships": links,
        }
