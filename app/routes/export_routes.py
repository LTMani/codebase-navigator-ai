from flask import Blueprint, jsonify, Response
from app.services.sarif_exporter import SarifExporter
from app.services.sonar_exporter import SonarExporter
from app.services.report_generator_service import ReportGeneratorService
from app.storage.project_store import ProjectStore

export_bp = Blueprint('export_bp', __name__)

@export_bp.route('/api/projects/<project_id>/export/sarif', methods=['GET'])
def export_sarif(project_id):
    res = SarifExporter.export_sarif([], [])
    return jsonify(res)

@export_bp.route('/api/projects/<project_id>/export/sonar', methods=['GET'])
def export_sonar(project_id):
    res = SonarExporter.export_sonar([], [])
    return jsonify(res)

@export_bp.route('/api/projects/<project_id>/export/html', methods=['GET'])
def export_html(project_id):
    p = ProjectStore.get(project_id) or {'name': 'Project ' + project_id}
    html = ReportGeneratorService.generate_html_report(p.get('name', 'Project'), {}, [])
    return Response(html, mimetype='text/html')
