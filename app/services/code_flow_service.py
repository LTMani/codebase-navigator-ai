import json
from collections import defaultdict
from typing import Any, Dict, List, Optional
from app.extensions import db
from app.models.code_flow import CodeFlow, FlowNode
from app.models.source_file import SourceFile
from app.models.symbol import FunctionDefinition
from app.repositories.file_repository import FileRepository
from app.repositories.flow_repository import FlowRepository
from app.repositories.symbol_repository import SymbolRepository


class CodeFlowService:
    """Discovers and synthesizes multi-layer execution paths (Route -> Service -> Repository -> Model)."""

    def __init__(
        self,
        flow_repo: Optional[FlowRepository] = None,
        file_repo: Optional[FileRepository] = None,
        symbol_repo: Optional[SymbolRepository] = None,
    ):
        self.flow_repo = flow_repo or FlowRepository()
        self.file_repo = file_repo or FileRepository()
        self.symbol_repo = symbol_repo or SymbolRepository()

    def discover_code_flows(self, project_id: str) -> List[Dict[str, Any]]:
        """Trace application execution flows from discovered entry points and endpoints."""
        source_files = self.file_repo.get_all_by_project(project_id)
        
        # Clear existing flows for fresh computation
        self.flow_repo.delete_by_project(project_id)

        # Index functions by name and qualified name for fast call resolution
        fn_lookup: Dict[str, List[FunctionDefinition]] = defaultdict(list)
        for sf in source_files:
            for fn in sf.functions:
                fn_lookup[fn.name].append(fn)

        discovered_flows: List[CodeFlow] = []

        # Find API Route Handlers / Entry points
        for sf in source_files:
            if sf.layer_classification not in ("api", "presentation") and not sf.is_entry_point:
                continue

            for fn in sf.functions:
                # Check decorators for routing (e.g. route, get, post, put, delete)
                is_endpoint = any(
                    any(verb in d.lower() for verb in ("route", "get", "post", "put", "delete", "patch"))
                    for d in fn.decorators
                ) or sf.is_entry_point

                if not is_endpoint and not fn.is_exported:
                    continue

                # Start tracing flow from this function
                flow_steps: List[Dict[str, Any]] = []
                visited_fns = set()

                # Step 1: Entry node
                flow_steps.append({
                    "step_number": 1,
                    "layer_name": sf.layer_classification,
                    "file_path": sf.relative_path,
                    "symbol_name": fn.name,
                    "action": f"Receives incoming request in {sf.filename} ({fn.name})",
                    "certainty": "confirmed",
                })
                visited_fns.add(fn.name)

                # Step 2: Trace downstream calls
                step_idx = 2
                current_calls = fn.calls

                for callee in current_calls:
                    if callee in visited_fns:
                        continue

                    matches = fn_lookup.get(callee, [])
                    for target_fn in matches:
                        target_file = target_fn.source_file
                        if target_file.id == sf.id and target_fn.name == fn.name:
                            continue

                        flow_steps.append({
                            "step_number": step_idx,
                            "layer_name": target_file.layer_classification,
                            "file_path": target_file.relative_path,
                            "symbol_name": target_fn.name,
                            "action": f"Executes {target_fn.name}() in {target_file.filename}",
                            "certainty": "confirmed" if len(matches) == 1 else "inferred",
                        })
                        visited_fns.add(callee)
                        step_idx += 1

                        # Trace one more level deep (Service -> Repository/DB)
                        for deeper_call in target_fn.calls:
                            if deeper_call in visited_fns or deeper_call in ("append", "get", "print", "len", "str", "int"):
                                continue

                            deep_matches = fn_lookup.get(deeper_call, [])
                            for deep_fn in deep_matches:
                                deep_file = deep_fn.source_file
                                flow_steps.append({
                                    "step_number": step_idx,
                                    "layer_name": deep_file.layer_classification,
                                    "file_path": deep_file.relative_path,
                                    "symbol_name": deep_fn.name,
                                    "action": f"Persists/queries data via {deep_fn.name}() in {deep_file.filename}",
                                    "certainty": "inferred",
                                })
                                visited_fns.add(deeper_call)
                                step_idx += 1
                                break
                        break

                # Create CodeFlow if meaningful steps found
                if len(flow_steps) >= 2 or sf.is_entry_point:
                    flow_title = f"{fn.name.replace('_', ' ').title()} Flow"
                    desc = f"Execution path initiating from {sf.relative_path}::{fn.name}"

                    code_flow = CodeFlow(
                        project_id=project_id,
                        flow_name=flow_title,
                        flow_type="request_response" if is_endpoint else "lifecycle",
                        entry_point=f"{sf.relative_path}::{fn.name}",
                        description=desc,
                        confidence_score=0.88,
                        step_count=len(flow_steps),
                        steps_json=json.dumps(flow_steps),
                    )
                    db.session.add(code_flow)
                    db.session.flush()

                    for step_item in flow_steps:
                        node = FlowNode(
                            code_flow_id=code_flow.id,
                            step_number=step_item["step_number"],
                            layer_name=step_item["layer_name"],
                            file_path=step_item["file_path"],
                            symbol_name=step_item["symbol_name"],
                            action=step_item["action"],
                            certainty=step_item["certainty"],
                        )
                        db.session.add(node)

                    discovered_flows.append(code_flow)

        db.session.commit()
        return [f.to_dict() for f in discovered_flows]
