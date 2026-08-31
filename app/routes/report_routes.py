from flask import Blueprint, jsonify, request, Response
from app.middleware.auth_middleware import login_required
from app.services.export_service import ExportService

report_bp = Blueprint("reports", __name__, url_prefix="/api/projects/<project_id>/reports")
export_service = ExportService()


@report_bp.route("/generate", methods=["GET"])
@login_required
def generate_report(project_id: str):
    """Generate architectural and health audit report in Markdown or JSON."""
    fmt = request.args.get("format", "markdown").lower()
    report = export_service.generate_full_report(project_id, format_type=fmt)

    if fmt == "markdown" and request.args.get("download") == "true":
        return Response(
            report["content"],
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment;filename={report['filename']}"},
        )

    return jsonify({
        "success": True,
        "data": report,
    }), 200
