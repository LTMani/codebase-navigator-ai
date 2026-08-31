from typing import Any, Dict, List

class ReportGeneratorService:
    """Standalone HTML Executive Report & SVG Architecture Diagrams."""

    @classmethod
    def generate_html_report(cls, project_name: str, summary_stats: Dict[str, Any], issues: List[Dict[str, Any]]) -> str:
        return f'<!DOCTYPE html><html><head><title>{project_name} - Codebase Navigator AI Report</title></head><body style="font-family: sans-serif; padding: 40px; background: #1e2433; color: #e6edf3;"><h1>{project_name}</h1><h3>Executive Health & Security Summary</h3><p>Total Issues: {len(issues)}</p></body></html>'

    @classmethod
    def generate_svg_diagram(cls, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> str:
        return '<svg width="1000" height="600" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#0d1117"/><text x="50" y="50" fill="#39d353" font-size="20">Codebase Architectural SVG</text></svg>'
