from flask import Blueprint, jsonify, request
from app.services.refactoring_engine import RefactoringEngine

refactor_bp = Blueprint('refactor_bp', __name__)

@refactor_bp.route('/api/refactor/preview', methods=['POST'])
def preview_refactor():
    data = request.get_json() or {}
    orig = data.get('original_code', '')
    new_c = data.get('modified_code', '')
    diff = RefactoringEngine.generate_unified_diff(orig, new_c, data.get('filename', 'file.py'))
    return jsonify({'success': True, 'diff': diff})
