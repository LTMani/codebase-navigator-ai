from collections import defaultdict
from typing import Any, Dict, List, Optional, Set
from app.models.source_file import SourceFile
from app.models.symbol import ClassDefinition, FunctionDefinition
from app.repositories.file_repository import FileRepository


class CallGraphService:
    """Inter-procedural call graph constructor resolving callers, callees, and execution paths."""

    def __init__(self, file_repo: Optional[FileRepository] = None):
        self.file_repo = file_repo or FileRepository()

    def build_project_call_graph(self, project_id: str) -> Dict[str, Any]:
        """Construct call graph linking all function declarations to their invocations."""
        source_files = self.file_repo.get_all_by_project(project_id)
        
        # 1. Index all functions by qualified_name and simple name
        functions_by_qname: Dict[str, FunctionDefinition] = {}
        functions_by_name: Dict[str, List[FunctionDefinition]] = defaultdict(list)
        qname_to_file: Dict[str, str] = {}

        for sf in source_files:
            for fn in sf.functions:
                qname = f"{sf.relative_path}::{fn.qualified_name or fn.name}"
                functions_by_qname[qname] = fn
                functions_by_name[fn.name].append(fn)
                qname_to_file[qname] = sf.relative_path

        # 2. Build Call Graph Edges
        call_edges: List[Dict[str, Any]] = []
        callers_map: Dict[str, Set[str]] = defaultdict(set)
        callees_map: Dict[str, Set[str]] = defaultdict(set)

        for sf in source_files:
            for caller_fn in sf.functions:
                caller_qname = f"{sf.relative_path}::{caller_fn.qualified_name or caller_fn.name}"
                
                # Check each callee invoked in function body
                for callee_name in caller_fn.calls:
                    # Match callee to known declarations
                    matches = functions_by_name.get(callee_name, [])
                    if matches:
                        for matched_fn in matches:
                            target_file = matched_fn.source_file.relative_path if matched_fn.source_file else sf.relative_path
                            callee_qname = f"{target_file}::{matched_fn.qualified_name or matched_fn.name}"
                            
                            call_edges.append({
                                "caller": caller_qname,
                                "caller_name": caller_fn.name,
                                "callee": callee_qname,
                                "callee_name": callee_name,
                                "is_cross_file": sf.relative_path != target_file,
                                "caller_file": sf.relative_path,
                                "callee_file": target_file,
                            })
                            callers_map[callee_qname].add(caller_qname)
                            callees_map[caller_qname].add(callee_qname)
                    else:
                        # External library or unresolved runtime invocation
                        ext_qname = f"external::{callee_name}"
                        call_edges.append({
                            "caller": caller_qname,
                            "caller_name": caller_fn.name,
                            "callee": ext_qname,
                            "callee_name": callee_name,
                            "is_cross_file": True,
                            "caller_file": sf.relative_path,
                            "callee_file": "external",
                        })
                        callees_map[caller_qname].add(ext_qname)

        # 3. Identify Root Entry Points (In-Degree = 0) and Terminal Leaves (Out-Degree = 0)
        all_nodes = set(functions_by_qname.keys())
        entry_points = [node for node in all_nodes if len(callers_map.get(node, set())) == 0]
        leaf_nodes = [node for node in all_nodes if len(callees_map.get(node, set())) == 0]

        return {
            "project_id": project_id,
            "nodes_count": len(all_nodes),
            "edges_count": len(call_edges),
            "entry_points_count": len(entry_points),
            "leaf_nodes_count": len(leaf_nodes),
            "edges": call_edges[:100],
            "top_callers": sorted(
                [{"function": k, "call_count": len(v)} for k, v in callees_map.items()],
                key=lambda x: x["call_count"],
                reverse=True
            )[:15],
            "top_called": sorted(
                [{"function": k, "called_by_count": len(v)} for k, v in callers_map.items()],
                key=lambda x: x["called_by_count"],
                reverse=True
            )[:15],
        }

    def trace_call_hierarchy(self, project_id: str, symbol_name: str, max_depth: int = 5) -> Dict[str, Any]:
        """Trace upstream callers and downstream callees for a specific function symbol."""
        graph_data = self.build_project_call_graph(project_id)
        edges = graph_data["edges"]

        downstream: List[str] = []
        upstream: List[str] = []

        for e in edges:
            if symbol_name in e["caller_name"] or symbol_name in e["caller"]:
                downstream.append(e["callee"])
            if symbol_name in e["callee_name"] or symbol_name in e["callee"]:
                upstream.append(e["caller"])

        return {
            "symbol_name": symbol_name,
            "upstream_callers": list(set(upstream)),
            "downstream_callees": list(set(downstream)),
            "call_depth": min(len(downstream), max_depth),
        }
