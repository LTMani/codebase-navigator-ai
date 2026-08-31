from flask import Blueprint, jsonify, request
from app.services.cfg_engine import CFGEngine

cfg_bp = Blueprint('cfg_bp', __name__)

@cfg_bp.route('/api/cfg/generate', methods=['POST'])
def generate_cfg():
    data = request.get_json() or {}
    code = data.get('code', '')
    res = CFGEngine.build_python_cfg(code)
    return jsonify(res)
