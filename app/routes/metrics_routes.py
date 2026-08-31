from flask import Blueprint, jsonify, request
from app.services.metrics_engine import MetricsEngine
from app.storage.project_store import ProjectStore

metrics_bp = Blueprint('metrics_bp', __name__)

@metrics_bp.route('/api/projects/<project_id>/metrics/lcom4', methods=['GET'])
def get_lcom4(project_id):
    p = ProjectStore.get(project_id)
    if not p: return jsonify({'success': False, 'error': 'Not found'}), 404
    return jsonify({'success': True, 'lcom4': 1})
