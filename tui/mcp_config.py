import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_MCP_CONFIG: Dict[str, Any] = {
    "servers": {
        "text-editor": {
            "name": "Text Editor MCP",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"],
            "env": {},
            "transport": "stdio",
            "priority": 1,
        },
        "web-search": {
            "name": "Web Search MCP",
            "command": "npx",
            "args": ["-y", "@tavily-ai/tavily-mcp"],
            "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"},
            "transport": "stdio",
            "priority": 2,
        },
        "github": {
            "name": "GitHub MCP",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
            "transport": "stdio",
            "priority": 3,
        },
    },
    "registries": {
        "github": "https://github.com/modelcontextprotocol/servers",
        "dockerhub": "https://hub.docker.com/r/mcp/toolkit",
    },
}


@dataclass(frozen=True)
class MCPServerDefinition:
    server_id: str
    name: str
    command: str
    args: list[str]
    env: Dict[str, str]
    transport: str
    priority: int


class MCPConfig:
    def __init__(self, raw: Dict[str, Any]):
        self.raw = raw

    @staticmethod
    def default_config_path() -> Path:
        return Path.home() / ".blonde" / "mcp_servers.json"

    @staticmethod
    def _expand_env(value: str) -> str:
        if not isinstance(value, str):
            return value
        if value.startswith("${") and value.endswith("}"):
            key = value[2:-1]
            return os.environ.get(key, "")
        return value

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "MCPConfig":
        config_path = path or cls.default_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if not config_path.exists():
            config_path.write_text(json.dumps(DEFAULT_MCP_CONFIG, indent=2))
            return cls(DEFAULT_MCP_CONFIG)

        data = json.loads(config_path.read_text())
        return cls(data)

    @classmethod
    def load_if_exists(cls, path: Optional[Path] = None) -> Optional["MCPConfig"]:
        config_path = path or cls.default_config_path()
        if not config_path.exists():
            return None
        data = json.loads(config_path.read_text())
        return cls(data)

    def iter_server_definitions(self) -> list[MCPServerDefinition]:
        servers = self.raw.get("servers", {})
        out: list[MCPServerDefinition] = []

        for server_id, s in servers.items():
            env = {k: self._expand_env(v) for k, v in (s.get("env") or {}).items()}
            out.append(
                MCPServerDefinition(
                    server_id=server_id,
                    name=s.get("name") or server_id,
                    command=s.get("command") or "",
                    args=list(s.get("args") or []),
                    env=env,
                    transport=s.get("transport") or "stdio",
                    priority=int(s.get("priority") or 100),
                )
            )

        out.sort(key=lambda d: d.priority)
        return out
