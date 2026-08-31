import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConfigFinding:
    config_type: str  # docker, docker_compose, github_actions, typescript, vite, webpack, env
    file_path: str
    services_detected: List[str] = field(default_factory=list)
    ports_exposed: List[str] = field(default_factory=list)
    env_vars_declared: List[str] = field(default_factory=list)
    build_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigParser:
    """Analyzes infrastructure, build configuration, container definitions, and CI/CD workflows."""

    @classmethod
    def analyze_config_file(cls, filename: str, content: str, relative_path: str) -> Optional[ConfigFinding]:
        fn = filename.lower()
        if fn == "dockerfile" or fn.startswith("dockerfile."):
            return cls.parse_dockerfile(content, relative_path)
        elif fn in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
            return cls.parse_docker_compose(content, relative_path)
        elif ".github/workflows" in relative_path.replace("\\", "/").lower():
            return cls.parse_github_workflow(content, relative_path)
        elif fn == "tsconfig.json":
            return cls.parse_tsconfig(content, relative_path)
        elif fn in (".env.example", ".env.sample", ".env.template"):
            return cls.parse_env_template(content, relative_path)
        return None

    @classmethod
    def parse_dockerfile(cls, content: str, path: str) -> ConfigFinding:
        finding = ConfigFinding(config_type="docker", file_path=path)
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("FROM "):
                base_image = line[5:].split()[0].strip()
                finding.metadata["base_image"] = base_image
            elif line.startswith("EXPOSE "):
                ports = line[7:].split()
                finding.ports_exposed.extend(ports)
            elif line.startswith("ENV "):
                env_decl = line[4:].strip()
                var_name = env_decl.split("=")[0].split()[0]
                finding.env_vars_declared.append(var_name)
            elif line.startswith("CMD ") or line.startswith("ENTRYPOINT "):
                finding.metadata["entrypoint"] = line
        return finding

    @classmethod
    def parse_docker_compose(cls, content: str, path: str) -> ConfigFinding:
        finding = ConfigFinding(config_type="docker_compose", file_path=path)
        in_services = False
        current_service = None

        for line in content.splitlines():
            raw_line = line
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if stripped == "services:":
                in_services = True
                continue

            if in_services:
                indent = len(raw_line) - len(raw_line.lstrip())
                if indent == 2 and stripped.endswith(":"):
                    current_service = stripped[:-1].strip()
                    finding.services_detected.append(current_service)
                elif "ports:" in stripped or "- \"" in stripped or "- '" in stripped:
                    port_match = re.search(r"['\"]?(\d+:\d+)['\"]?", stripped)
                    if port_match:
                        finding.ports_exposed.append(port_match.group(1))

        return finding

    @classmethod
    def parse_github_workflow(cls, content: str, path: str) -> ConfigFinding:
        finding = ConfigFinding(config_type="github_actions", file_path=path)
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("name:"):
                finding.metadata["workflow_name"] = stripped[5:].strip().strip('"').strip("'")
            elif stripped.startswith("- name:"):
                finding.build_steps.append(stripped[7:].strip().strip('"').strip("'"))
            elif stripped.startswith("run:"):
                finding.build_steps.append(stripped[4:].strip())
        return finding

    @classmethod
    def parse_tsconfig(cls, content: str, path: str) -> ConfigFinding:
        finding = ConfigFinding(config_type="typescript", file_path=path)
        # Check target, jsx, module
        for key in ("target", "module", "jsx", "strict"):
            match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', content)
            if match:
                finding.metadata[key] = match.group(1)
        return finding

    @classmethod
    def parse_env_template(cls, content: str, path: str) -> ConfigFinding:
        finding = ConfigFinding(config_type="env", file_path=path)
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                var_name = line.split("=", 1)[0].strip()
                if var_name:
                    finding.env_vars_declared.append(var_name)
        return finding
