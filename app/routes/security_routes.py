from flask import Blueprint, jsonify, request
from app.services.security_analyzer_engine import SecurityAnalyzerEngine
from app.storage.project_store import ProjectStore

security_bp = Blueprint('security_bp', __name__)

@security_bp.route('/api/projects/<project_id>/security/audit', methods=['GET'])
def get_security_audit(project_id):
    p = ProjectStore.get(project_id)
    if not p: return jsonify({'success': False, 'error': 'Not found'}), 404
    all_issues = []
    for file_obj in p.get('files_data', []):
        content = file_obj.get('content', '')
        path = file_obj.get('file_path', '')
        issues = SecurityAnalyzerEngine.scan_source(content, path)
        all_issues.extend(issues)
    return jsonify({'success': True, 'vulnerabilities': all_issues, 'total': len(all_issues)})
