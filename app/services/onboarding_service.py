import json
from typing import Any, Dict, List, Optional
from app.extensions import db
from app.models.onboarding import OnboardingPlan, OnboardingStep
from app.models.project import Project
from app.models.source_file import SourceFile
from app.repositories.architecture_repository import ArchitectureRepository
from app.repositories.dependency_repository import DependencyRepository
from app.repositories.file_repository import FileRepository
from app.repositories.flow_repository import FlowRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.project_repository import ProjectRepository
from app.services.dependency_service import DependencyService


class OnboardingService:
    """Generates structured developer onboarding journeys, curated reading paths, and knowledge checks."""

    def __init__(
        self,
        onboarding_repo: Optional[OnboardingRepository] = None,
        project_repo: Optional[ProjectRepository] = None,
        file_repo: Optional[FileRepository] = None,
        arch_repo: Optional[ArchitectureRepository] = None,
        flow_repo: Optional[FlowRepository] = None,
    ):
        self.onboarding_repo = onboarding_repo or OnboardingRepository()
        self.project_repo = project_repo or ProjectRepository()
        self.file_repo = file_repo or FileRepository()
        self.arch_repo = arch_repo or ArchitectureRepository()
        self.flow_repo = flow_repo or FlowRepository()
        self.dep_service = DependencyService()

    def generate_onboarding_plan(self, project_id: str) -> Dict[str, Any]:
        """Synthesize tailored developer guide based on analyzed project data."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return {}

        # Clear existing plan
        self.onboarding_repo.delete_by_project(project_id)

        source_files = self.file_repo.get_all_by_project(project_id)
        dep_graph = self.dep_service.build_dependency_graph(project_id)
        nodes_by_path = {n["path"]: n for n in dep_graph.get("nodes", [])}

        # 1. Executive Summary
        frameworks_str = ", ".join(project.frameworks) if project.frameworks else "Standard Libraries"
        languages_list = list(project.languages.keys()) if project.languages else ["Source Code"]
        primary_lang = languages_list[0] if languages_list else "Software"

        exec_summary = (
            f"Welcome to {project.name}. This is a {primary_lang} codebase utilizing {frameworks_str}. "
            f"The project comprises {project.file_count} source files across {project.folder_count} directories, "
            f"with {project.total_lines:,} total lines of code."
        )

        arch_overview = (
            f"{project.name} is structured around modular architectural layers to separate concerns. "
            f"Incoming client requests enter through API routing controllers, are processed by Domain Services, "
            f"and persist data via Repositories and Data Models."
        )

        # 2. Prioritized Reading Order (Sorted by PageRank + Entry Points)
        sorted_files = sorted(
            source_files,
            key=lambda f: (
                1 if f.is_entry_point else 0,
                nodes_by_path.get(f.relative_path, {}).get("pagerank", 0.0),
                f.total_lines,
            ),
            reverse=True,
        )

        reading_path: List[Dict[str, Any]] = []
        for rank, f in enumerate(sorted_files[:10], start=1):
            reason = "Application entry point" if f.is_entry_point else f"High central dependency in {f.layer_classification} layer"
            reading_path.append({
                "order": rank,
                "file_path": f.relative_path,
                "filename": f.filename,
                "language": f.language,
                "layer": f.layer_classification,
                "lines": f.total_lines,
                "reason": reason,
                "purpose": f.purpose_summary,
            })

        # 3. Core Domain Concepts
        core_concepts: List[Dict[str, Any]] = []
        for f in source_files:
            if f.layer_classification in ("domain", "service") or f.classes:
                for cls in f.classes[:2]:
                    core_concepts.append({
                        "name": cls.name,
                        "kind": "class",
                        "file_path": f.relative_path,
                        "docstring": cls.docstring or f"Core domain abstraction defined in {f.filename}.",
                        "methods_count": cls.methods_count,
                    })

        # 4. Interactive Knowledge Check (Quiz)
        quiz_questions = self._generate_knowledge_check(project, source_files, reading_path)

        # 5. Persist OnboardingPlan & Steps
        plan_obj = OnboardingPlan(
            project_id=project_id,
            title=f"Developer Onboarding Guide: {project.name}",
            executive_summary=exec_summary,
            architecture_overview=arch_overview,
            estimated_read_time_minutes=max(15, len(reading_path) * 4),
            reading_path_json=json.dumps(reading_path),
            core_concepts_json=json.dumps(core_concepts[:8]),
            knowledge_check_json=json.dumps(quiz_questions),
        )
        self.onboarding_repo.create(plan_obj)

        # Create detailed roadmap steps
        steps = [
            OnboardingStep(
                plan_id=plan_obj.id,
                step_order=1,
                title="1. Project Mission & Technology Stack",
                category="overview",
                file_path=reading_path[0]["file_path"] if reading_path else None,
                explanation=exec_summary,
                key_takeaways_json=json.dumps([
                    f"Primary language: {primary_lang}",
                    f"Detected frameworks: {frameworks_str}",
                    f"Total codebase size: {project.total_lines:,} lines",
                ]),
            ),
            OnboardingStep(
                plan_id=plan_obj.id,
                step_order=2,
                title="2. Architectural Overview & Layer Roles",
                category="architecture",
                explanation=arch_overview,
                key_takeaways_json=json.dumps([
                    "Presentation Layer: UI and views",
                    "API Layer: HTTP routes and input handling",
                    "Service Layer: Core business workflows",
                    "Repository Layer: Data access and persistence",
                ]),
            ),
            OnboardingStep(
                plan_id=plan_obj.id,
                step_order=3,
                title="3. First Files to Read",
                category="reading_order",
                file_path=reading_path[0]["file_path"] if reading_path else None,
                explanation="Start by reviewing the primary entry points and core domain models in the curated reading list.",
                key_takeaways_json=json.dumps([f"{item['order']}. {item['file_path']} ({item['reason']})" for item in reading_path[:4]]),
            ),
        ]
        self.onboarding_repo.create_steps_batch(steps)

        return {
            "project_id": project_id,
            "plan_id": plan_obj.id,
            "title": plan_obj.title,
            "executive_summary": exec_summary,
            "architecture_overview": arch_overview,
            "estimated_read_time_minutes": plan_obj.estimated_read_time_minutes,
            "reading_path": reading_path,
            "core_concepts": core_concepts[:8],
            "knowledge_check": quiz_questions,
            "steps": [s.to_dict() for s in steps],
        }

    def _generate_knowledge_check(
        self,
        project: Project,
        source_files: List[SourceFile],
        reading_path: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate multiple choice questions grounded in actual analyzed project facts."""
        questions: List[Dict[str, Any]] = []

        # Question 1: Entry Point
        entry_file = reading_path[0]["file_path"] if reading_path else "index.js"
        other_files = [f.relative_path for f in source_files if f.relative_path != entry_file][:3]
        options1 = [entry_file] + other_files
        import random
        # deterministic shuffle
        options1 = sorted(options1, key=lambda x: len(x))

        questions.append({
            "id": "q1",
            "question": f"What is the primary entry point or high-priority file to read first in {project.name}?",
            "options": options1,
            "correct_answer": entry_file,
            "explanation": f"'{entry_file}' is flagged as an application entry point or central dependency.",
        })

        # Question 2: Architecture layer of top file
        if len(reading_path) > 1:
            target_item = reading_path[1]
            correct_layer = target_item["layer"].title()
            layer_options = ["Presentation", "Api", "Service", "Domain", "Repository"]
            if correct_layer not in layer_options:
                layer_options.append(correct_layer)

            questions.append({
                "id": "q2",
                "question": f"Which architectural layer does '{target_item['filename']}' belong to?",
                "options": layer_options[:4],
                "correct_answer": correct_layer,
                "explanation": f"'{target_item['filename']}' is classified under the {correct_layer} layer.",
            })

        # Question 3: Frameworks detected
        if project.frameworks:
            correct_fw = project.frameworks[0]
            questions.append({
                "id": "q3",
                "question": f"Which framework is detected as part of {project.name}'s tech stack?",
                "options": [correct_fw, "Ruby on Rails", "Laravel", "Spring Framework"],
                "correct_answer": correct_fw,
                "explanation": f"{project.name} integrates {correct_fw}.",
            })

        return questions

    def evaluate_quiz(self, plan_id: str, submitted_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate submitted user quiz responses and calculate score."""
        plan = self.onboarding_repo.get_by_id(plan_id)
        if not plan:
            return {"score": 0, "total": 0, "passed": False}

        questions = plan.knowledge_check
        total_questions = len(questions)
        correct_count = 0
        detailed_results = []

        for q in questions:
            qid = q["id"]
            user_ans = str(submitted_answers.get(qid, "")).strip()
            expected = str(q["correct_answer"]).strip()
            is_correct = user_ans.lower() == expected.lower()

            if is_correct:
                correct_count += 1

            detailed_results.append({
                "question_id": qid,
                "question": q["question"],
                "user_answer": user_ans,
                "correct_answer": expected,
                "is_correct": is_correct,
                "explanation": q["explanation"],
            })

        score_pct = round((correct_count / max(total_questions, 1)) * 100.0, 1)
        return {
            "plan_id": plan_id,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "score_percent": score_pct,
            "passed": score_pct >= 70.0,
            "results": detailed_results,
        }
