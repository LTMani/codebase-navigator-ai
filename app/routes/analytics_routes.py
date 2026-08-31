from flask import Blueprint, jsonify, request
from app.services.graph_analytics_engine import GraphAnalyticsEngine
from app.storage.project_store import ProjectStore

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/api/projects/<project_id>/analytics/centrality', methods=['GET'])
def get_centrality(project_id):
    p = ProjectStore.get(project_id)
    if not p: return jsonify({'success': False, 'error': 'Not found'}), 404
    nodes = [f.get('file_path') for f in p.get('files_data', [])]
    edges = [(f.get('file_path', ''), imp.get('module', '')) for f in p.get('files_data', []) for imp in f.get('imports', [])]
    result = GraphAnalyticsEngine.compute_betweenness_centrality(nodes, edges)
    return jsonify({'success': True, 'betweenness': result})

@analytics_bp.route('/api/projects/<project_id>/analytics/communities', methods=['GET'])
def get_communities(project_id):
    p = ProjectStore.get(project_id)
    if not p: return jsonify({'success': False, 'error': 'Not found'}), 404
    nodes = [f.get('file_path') for f in p.get('files_data', [])]
    edges = [(f.get('file_path', ''), imp.get('module', '')) for f in p.get('files_data', []) for imp in f.get('imports', [])]
    result = GraphAnalyticsEngine.detect_communities_louvain(nodes, edges)
    return jsonify({'success': True, 'communities': result})
