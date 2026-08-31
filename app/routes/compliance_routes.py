from flask import Blueprint, jsonify, request
from app.services.architecture_compliance_engine import ArchitectureComplianceEngine
from app.storage.project_store import ProjectStore

compliance_bp = Blueprint('compliance_bp', __name__)

@compliance_bp.route('/api/projects/<project_id>/compliance/validate', methods=['GET', 'POST'])
def validate_compliance(project_id):
    p = ProjectStore.get(project_id)
    if not p: return jsonify({'success': False, 'error': 'Not found'}), 404
    rules = request.get_json() if request.is_json else None
    violations = ArchitectureComplianceEngine.validate_layer_boundaries(p.get('files_data', []), rules)
    return jsonify({'success': True, 'violations': violations, 'total_violations': len(violations)})
