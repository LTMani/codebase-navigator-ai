from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import login_required
from app.schemas.onboarding_schemas import QuizSubmissionSchema
from app.services.onboarding_service import OnboardingService

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/api/projects/<project_id>/onboarding")
onboarding_service = OnboardingService()


@onboarding_bp.route("", methods=["GET"])
@login_required
def get_onboarding_plan(project_id: str):
    """Retrieve synthesized developer onboarding roadmap and reading order."""
    plan_data = onboarding_service.generate_onboarding_plan(project_id)
    return jsonify({
        "success": True,
        "data": plan_data,
    }), 200


@onboarding_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit_quiz(project_id: str):
    """Submit developer knowledge check answers and receive instant graded score."""
    schema = QuizSubmissionSchema.from_dict(request.get_json() or {})
    plan_data = onboarding_service.generate_onboarding_plan(project_id)
    plan_id = plan_data.get("plan_id")

    results = onboarding_service.evaluate_quiz(plan_id, schema.answers)
    return jsonify({
        "success": True,
        "data": results,
    }), 200
