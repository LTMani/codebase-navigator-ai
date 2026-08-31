from flask import Blueprint, jsonify, request
from app.services.git_forensics_service import GitForensicsService
from app.storage.project_store import ProjectStore

git_bp = Blueprint('git_bp', __name__)

@git_bp.route('/api/projects/<project_id>/git/bus-factor', methods=['GET'])
def get_bus_factor(project_id):
    p = ProjectStore.get(project_id)
    if not p: return jsonify({'success': False, 'error': 'Not found'}), 404
    count, devs = GitForensicsService.calculate_bus_factor({'Developer 1': 45, 'Developer 2': 25, 'Developer 3': 10})
    return jsonify({'success': True, 'bus_factor': count, 'key_developers': devs})
