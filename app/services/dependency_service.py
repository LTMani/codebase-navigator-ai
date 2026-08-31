from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple
from app.extensions import db
from app.models.dependency import DependencyEdge
from app.models.health import CircularDependencyCluster
from app.models.source_file import SourceFile
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository


class DependencyService:
    """Graph construction, import resolution, Tarjan's SCC cycle detection, and centrality calculation."""

    def __init__(self, dep_repo: Optional[DependencyRepository] = None, file_repo: Optional[FileRepository] = None):
        self.dep_repo = dep_repo or DependencyRepository()
        self.file_repo = file_repo or FileRepository()

    def build_dependency_graph(self, project_id: str) -> Dict[str, Any]:
        """Construct graph nodes, edges, resolve imports, detect cycles and compute PageRank."""
        # 1. Fetch all files and imports for project
        source_files = self.file_repo.get_all_by_project(project_id)
        file_path_map: Dict[str, SourceFile] = {f.relative_path: f for f in source_files}

        # Clear existing edges for fresh computation
        self.dep_repo.delete_by_project(project_id)

        edges: List[DependencyEdge] = []
        adjacency: Dict[str, Set[str]] = defaultdict(set)
        reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)

        # 2. Map imports to edges
        for source_file in source_files:
            for imp in source_file.imports:
                target_file: Optional[SourceFile] = None
                mod_name = imp.module_name

                # Resolution Strategy 1: Exact relative path match
                if imp.is_relative:
                    base_dir = Path_Dirname(source_file.relative_path)
                    candidates = [
                        f"{base_dir}/{mod_name}.py" if base_dir else f"{mod_name}.py",
                        f"{base_dir}/{mod_name}.js" if base_dir else f"{mod_name}.js",
                        f"{base_dir}/{mod_name}.ts" if base_dir else f"{mod_name}.ts",
                        f"{base_dir}/{mod_name}/index.js" if base_dir else f"{mod_name}/index.js",
                        f"{base_dir}/{mod_name}/__init__.py" if base_dir else f"{mod_name}/__init__.py",
                    ]
                    for cand in candidates:
                        clean_cand = cand.replace("//", "/").lstrip("/")
                        if clean_cand in file_path_map:
                            target_file = file_path_map[clean_cand]
                            break

                # Resolution Strategy 2: Absolute / module package match (e.g. app.models.user)
                if not target_file and not imp.is_external:
                    mod_path = mod_name.replace(".", "/")
                    candidates = [
                        f"{mod_path}.py",
                        f"{mod_path}.js",
                        f"{mod_path}.ts",
                        f"{mod_path}/__init__.py",
                        f"{mod_path}/index.js",
                        f"app/{mod_path}.py",
                        f"src/{mod_path}.ts",
                        f"src/{mod_path}.js",
                    ]
                    for cand in candidates:
                        if cand in file_path_map:
                            target_file = file_path_map[cand]
                            break

                target_path = target_file.relative_path if target_file else mod_name
                is_ext = target_file is None

                edge = DependencyEdge(
                    project_id=project_id,
                    source_file_id=source_file.id,
                    target_file_id=target_file.id if target_file else None,
                    source_path=source_file.relative_path,
                    target_path=target_path,
                    target_module=mod_name,
                    dependency_type="import",
                    is_external=is_ext,
                    is_circular=False,
                    weight=max(len(imp.imported_names), 1),
                )
                edges.append(edge)

                if target_file:
                    adjacency[source_file.relative_path].add(target_file.relative_path)
                    reverse_adjacency[target_file.relative_path].add(source_file.relative_path)

        # 3. Detect Circular Dependencies with Tarjan's SCC Algorithm
        cycles, sccs = self._find_strongly_connected_components(adjacency)
        
        # Mark edges participating in circular loops
        circular_pairs = set()
        for cycle in cycles:
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i + 1) % len(cycle)]
                circular_pairs.add((u, v))

        for edge in edges:
            if (edge.source_path, edge.target_path) in circular_pairs:
                edge.is_circular = True

        # Save edges
        if edges:
            db.session.add_all(edges)
            db.session.commit()

        # 4. Compute PageRank Centrality
        pagerank = self._compute_pagerank(source_files, adjacency)

        # 5. Format Nodes & Edges payload for visual graphs
        nodes = []
        for f in source_files:
            in_degree = len(reverse_adjacency[f.relative_path])
            out_degree = len(adjacency[f.relative_path])
            nodes.append({
                "id": f.id,
                "label": f.filename,
                "path": f.relative_path,
                "language": f.language,
                "layer": f.layer_classification,
                "lines": f.total_lines,
                "complexity": f.cyclomatic_complexity,
                "maintainability": f.maintainability_index,
                "pagerank": round(pagerank.get(f.relative_path, 0.0), 4),
                "in_degree": in_degree,
                "out_degree": out_degree,
                "is_entry_point": f.is_entry_point,
            })

        edge_payloads = [
            {
                "id": e.id,
                "source": e.source_path,
                "target": e.target_path,
                "is_external": e.is_external,
                "is_circular": e.is_circular,
                "weight": e.weight,
            }
            for e in edges
        ]

        return {
            "project_id": project_id,
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "circular_cycles_count": len(cycles),
            "nodes": nodes,
            "edges": edge_payloads,
            "cycles": cycles,
        }

    def _find_strongly_connected_components(self, adj: Dict[str, Set[str]]) -> Tuple[List[List[str]], List[List[str]]]:
        """Tarjan's algorithm for finding Strongly Connected Components and cycles."""
        index = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        on_stack: Dict[str, bool] = {}
        stack: List[str] = []
        sccs: List[List[str]] = []
        cycles: List[List[str]] = []

        all_nodes = set(adj.keys())
        for targets in adj.values():
            all_nodes.update(targets)

        def strongconnect(v: str):
            nonlocal index
            indices[v] = index
            lowlinks[v] = index
            index += 1
            stack.append(v)
            on_stack[v] = True

            for w in adj.get(v, []):
                if w not in indices:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif on_stack.get(w, False):
                    lowlinks[v] = min(lowlinks[v], indices[w])

            if lowlinks[v] == indices[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)
                # An SCC with > 1 node or a self-loop is a circular cycle
                if len(scc) > 1:
                    cycles.append(list(reversed(scc)))
                elif len(scc) == 1 and scc[0] in adj.get(scc[0], []):
                    cycles.append(scc)

        for node in all_nodes:
            if node not in indices:
                strongconnect(node)

        return cycles, sccs

    def _compute_pagerank(self, source_files: List[SourceFile], adj: Dict[str, Set[str]], d: float = 0.85, max_iter: int = 40) -> Dict[str, float]:
        """Compute PageRank centrality scores over the code dependency graph."""
        nodes = [f.relative_path for f in source_files]
        n = len(nodes)
        if n == 0:
            return {}

        ranks = {node: 1.0 / n for node in nodes}
        out_degrees = {node: len(adj.get(node, [])) for node in nodes}

        for _ in range(max_iter):
            new_ranks: Dict[str, float] = {}
            dangling_sum = sum(ranks[node] for node in nodes if out_degrees[node] == 0)

            for u in nodes:
                # Sum inbound contributions
                inbound_sum = 0.0
                for v in nodes:
                    if u in adj.get(v, []):
                        inbound_sum += ranks[v] / max(out_degrees[v], 1)

                new_ranks[u] = ((1.0 - d) / n) + d * (inbound_sum + (dangling_sum / n))

            ranks = new_ranks

        # Normalize ranks so max is 1.0
        max_r = max(ranks.values()) if ranks else 1.0
        if max_r > 0:
            return {k: round(v / max_r, 4) for k, v in ranks.items()}
        return ranks


def Path_Dirname(path_str: str) -> str:
    """Return parent directory string for POSIX path."""
    if "/" not in path_str:
        return ""
    return path_str.rsplit("/", 1)[0]
