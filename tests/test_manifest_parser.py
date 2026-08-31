import pytest
from app.parsers.manifest_parser import ManifestParser


def test_package_json_parsing():
    content = '''{
  "name": "my-react-app",
  "version": "2.1.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.4.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^4.3.0"
  }
}'''
    res = ManifestParser.parse_manifest("package.json", content)
    assert res.manifest_type == "npm"
    assert res.project_name == "my-react-app"
    assert len(res.dependencies) == 5
    assert "React" in res.frameworks_detected


def test_requirements_txt_parsing():
    content = '''Flask==3.0.0
flask-cors>=4.0.0
sqlalchemy>=2.0.0
pytest==7.4.0
'''
    res = ManifestParser.parse_manifest("requirements.txt", content)
    assert res.manifest_type == "pip"
    assert len(res.dependencies) == 4
    assert "Flask" in res.frameworks_detected
