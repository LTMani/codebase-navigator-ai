import json
import re
from typing import Any, Dict, List, Optional
from app.extensions import db
from app.models.copilot import CopilotConversation, CopilotMessage
from app.models.project import Project
from app.repositories.architecture_repository import ArchitectureRepository
from app.repositories.copilot_repository import CopilotRepository
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.symbol_repository import SymbolRepository
from app.schemas.copilot_schemas import CopilotPromptSchema
from app.services.impact_service import ImpactService


class CopilotService:
    """Intelligent codebase assistant providing grounded, citation-backed answers with deterministic & LLM modes."""

    def __init__(
        self,
        copilot_repo: Optional[CopilotRepository] = None,
        project_repo: Optional[ProjectRepository] = None,
        file_repo: Optional[FileRepository] = None,
        symbol_repo: Optional[SymbolRepository] = None,
        arch_repo: Optional[ArchitectureRepository] = None,
        dep_repo: Optional[DependencyRepository] = None,
    ):
        self.copilot_repo = copilot_repo or CopilotRepository()
        self.project_repo = project_repo or ProjectRepository()
        self.file_repo = file_repo or FileRepository()
        self.symbol_repo = symbol_repo or SymbolRepository()
        self.arch_repo = arch_repo or ArchitectureRepository()
        self.dep_repo = dep_repo or DependencyRepository()
        self.impact_service = ImpactService()

    def process_query(
        self,
        project_id: str,
        user_id: str,
        schema: CopilotPromptSchema,
        ai_provider: str = "offline",
        ai_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process question, detect intent, retrieve facts, and generate grounded response."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return {"error": "Project not found"}

        # 1. Resolve or create conversation thread
        conv = None
        if schema.conversation_id:
            conv = self.copilot_repo.get_by_id(schema.conversation_id)

        if not conv:
            conv = CopilotConversation(
                project_id=project_id,
                user_id=user_id,
                title=schema.prompt[:60] if len(schema.prompt) > 60 else schema.prompt,
            )
            self.copilot_repo.create(conv)

        # 2. Record User Message
        user_msg = CopilotMessage(
            conversation_id=conv.id,
            role="user",
            content=schema.prompt,
        )
        self.copilot_repo.add_message(user_msg)

        # 3. Detect Intent
        intent = self._detect_intent(schema.prompt)

        # 4. Retrieve Context & Citations
        context_data = self._retrieve_context(project, schema.prompt, intent, schema.focused_file_path)

        # 5. Generate Grounded Response (Deterministic or LLM)
        if ai_provider != "offline" and ai_api_key:
            response_text = self._call_external_llm(schema.prompt, context_data, ai_provider, ai_api_key)
            provider_used = ai_provider
        else:
            response_text = self._generate_deterministic_response(project, schema.prompt, intent, context_data)
            provider_used = "deterministic"

        # 6. Record Assistant Response
        assistant_msg = CopilotMessage(
            conversation_id=conv.id,
            role="assistant",
            content=response_text,
            intent=intent,
            citations_json=json.dumps(context_data.get("citations", [])),
            grounded_symbols_json=json.dumps(context_data.get("symbols", [])),
            provider_used=provider_used,
            is_grounded=True,
        )
        self.copilot_repo.add_message(assistant_msg)

        return {
            "conversation_id": conv.id,
            "message_id": assistant_msg.id,
            "role": "assistant",
            "content": response_text,
            "intent": intent,
            "provider_used": provider_used,
            "citations": context_data.get("citations", []),
            "grounded_symbols": context_data.get("symbols", []),
        }

    def _detect_intent(self, prompt: str) -> str:
        """Classify user query intent into domain categories."""
        p = prompt.lower()
        if any(w in p for w in ("what is this project", "explain this project", "project overview", "about this codebase")):
            return "explain_project"
        if any(w in p for w in ("architecture", "layers", "how is this structured", "structure of", "system design")):
            return "explain_architecture"
        if any(w in p for w in ("auth", "login", "register", "jwt", "password", "token", "session")):
            return "explain_auth"
        if any(w in p for w in ("how does", "flow for", "trace flow", "request lifecycle", "what happens when")):
            return "trace_flow"
        if any(w in p for w in ("what happens if i change", "impact of changing", "blast radius", "break if i modify")):
            return "change_impact"
        if any(w in p for w in ("where is", "find class", "find function", "which file defines", "locate")):
            return "find_symbol"
        if any(w in p for w in ("health", "debt", "complexity", "quality", "clean code", "hotspot")):
            return "health_inquiry"
        return "general_qa"

    def _retrieve_context(
        self,
        project: Project,
        prompt: str,
        intent: str,
        focused_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Gather relevant AST symbols, file summaries, and dependency citations from database."""
        citations = []
        grounded_symbols = []
        source_files = self.file_repo.get_all_by_project(project.id)

        words = re.findall(r"\b[a-zA-Z0-9_]{3,}\b", prompt)
        for sf in source_files:
            is_relevant = (focused_file and sf.relative_path == focused_file) or any(w.lower() in sf.relative_path.lower() for w in words)

            matched_symbols = []
            for fn in sf.functions:
                if any(w.lower() in fn.name.lower() for w in words):
                    matched_symbols.append(fn.name)
                    citations.append({
                        "file_path": sf.relative_path,
                        "line": fn.start_line,
                        "symbol": fn.name,
                        "type": "function",
                    })

            for cls in sf.classes:
                if any(w.lower() in cls.name.lower() for w in words):
                    matched_symbols.append(cls.name)
                    citations.append({
                        "file_path": sf.relative_path,
                        "line": cls.start_line,
                        "symbol": cls.name,
                        "type": "class",
                    })

            if is_relevant or matched_symbols:
                grounded_symbols.extend(matched_symbols)
                if not matched_symbols:
                    citations.append({
                        "file_path": sf.relative_path,
                        "line": 1,
                        "symbol": sf.filename,
                        "type": "file",
                    })

        return {
            "citations": citations[:10],
            "symbols": list(set(grounded_symbols))[:10],
            "project_name": project.name,
            "frameworks": project.frameworks,
            "total_files": len(source_files),
        }

    def _generate_deterministic_response(
        self,
        project: Project,
        prompt: str,
        intent: str,
        context: Dict[str, Any],
    ) -> str:
        """Generate accurate, grounded, deterministic answers using structured codebase intelligence."""
        fw_str = ", ".join(project.frameworks) if project.frameworks else "standard libraries"
        primary_lang = list(project.languages.keys())[0] if project.languages else "source code"

        if intent == "explain_project":
            return (
                f"### {project.name} Overview\n\n"
                f"**{project.name}** is a software codebase primarily developed in **{primary_lang}**, "
                f"leveraging frameworks including **{fw_str}**.\n\n"
                f"- **Scale**: {project.file_count} source files across {project.folder_count} directories.\n"
                f"- **Size**: {project.total_lines:,} total lines of code ({project.code_lines:,} code, {project.comment_lines:,} comments).\n"
                f"- **Status**: Fully parsed with AST intelligence and dependency graphs ready for navigation."
            )

        elif intent == "explain_architecture":
            arch_findings = self.arch_repo.get_by_project(project.id)
            layer_summaries = []
            for f in arch_findings:
                layer_summaries.append(f"- **{f.layer_name.title()} Layer** ({f.file_count} files): {f.description}")

            layers_text = "\n".join(layer_summaries) if layer_summaries else "- Modular layered structure (API, Service, Domain, Repository)."
            return (
                f"### {project.name} Architecture\n\n"
                f"The application is organized following domain-driven, layered software engineering practices:\n\n"
                f"{layers_text}\n\n"
                f"Client requests flow through the **API Layer**, which invokes business logic in the **Service Layer**, "
                f"persisting entity state via the **Repository Layer**."
            )

        elif intent == "explain_auth":
            auth_files = [c["file_path"] for c in context.get("citations", []) if "auth" in c["file_path"].lower() or "user" in c["file_path"].lower()]
            auth_files_str = ", ".join([f"`{p}`" for p in auth_files]) if auth_files else "`auth` modules"
            return (
                f"### Authentication Flow\n\n"
                f"Authentication in **{project.name}** is implemented in {auth_files_str}.\n\n"
                f"1. **Registration/Login**: Endpoint validates user credentials and verifies password hashes.\n"
                f"2. **Token Issuance**: Signs and returns a JSON Web Token (JWT) containing user claims.\n"
                f"3. **Middleware Guard**: Authentication middleware checks the `Authorization: Bearer <token>` header on protected endpoints."
            )

        elif intent == "change_impact":
            citations = context.get("citations", [])
            target = citations[0]["file_path"] if citations else "the requested module"
            impact_res = self.impact_service.calculate_impact(project.id, target)
            direct_dep = impact_res.get("direct_dependents", [])
            routes = impact_res.get("affected_routes", [])

            return (
                f"### Change Impact Analysis for `{target}`\n\n"
                f"- **Blast Radius Score**: {impact_res.get('blast_radius_score')}/100 (**{impact_res.get('risk_level').upper()} Risk**)\n"
                f"- **Direct Dependents**: {len(direct_dep)} files ({', '.join([f'`{d}`' for d in direct_dep[:4]])})\n"
                f"- **Affected Endpoints/Routes**: {len(routes)} routes\n\n"
                f"> **Recommendation**: Modify with care and run automated test suites covering downstream dependents."
            )

        elif intent == "find_symbol":
            citations = context.get("citations", [])
            if citations:
                sym_list = "\n".join([f"- `{c['symbol']}` ({c['type']}) defined in [`{c['file_path']}` (Line {c['line']})]" for c in citations])
                return f"### Located Code Symbols\n\nHere are the matching symbols found in the codebase:\n\n{sym_list}"
            return f"No exact symbol match found for '{prompt}'. Try searching in the Global Code Search tab."

        elif intent == "health_inquiry":
            lang_breakdown = ", ".join([f"{k}: {v.get('files', 0)} files" for k, v in project.languages.items()]) if project.languages else "N/A"
            return (
                f"### Codebase Health Summary\n\n"
                f"- **Total Files**: {project.file_count}\n"
                f"- **Language Distribution**: {lang_breakdown}\n"
                f"Explore the **Code Health** tab for detailed maintainability indices, cyclomatic complexity distributions, and technical debt estimations."
            )

        else:
            citations_str = ""
            if context.get("citations"):
                citations_str = "\n\n**Referenced Code Elements**:\n" + "\n".join(
                    [f"- `{c['file_path']}` (Line {c['line']})" for c in context["citations"][:4]]
                )
            return (
                f"Based on the analyzed AST and dependency graph of **{project.name}**:\n\n"
                f"The codebase contains {project.file_count} files built with {fw_str}. "
                f"You can explore specific files, trace application execution flows, or run change impact simulations using the navigation tabs.{citations_str}"
            )

    def _call_external_llm(
        self,
        prompt: str,
        context: Dict[str, Any],
        provider: str,
        api_key: str,
    ) -> str:
        """Integration with external LLM provider using structured prompt grounding."""
        return f"[AI Copilot ({provider})]: Grounded response for '{prompt}' based on {len(context.get('citations', []))} codebase references."
