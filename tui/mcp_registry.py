from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class RegistryConnector:
    def list_servers(self) -> List[Dict[str, Any]]:
        raise NotImplementedError


@dataclass(frozen=True)
class RegistryDiscovery:
    connectors: List[RegistryConnector]

    def discover(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for c in self.connectors:
            try:
                out.extend(c.list_servers())
            except Exception:
                continue
        return out


class GitHubRegistryConnector(RegistryConnector):
    def __init__(self, registry_url: str):
        self.registry_url = registry_url

    def list_servers(self) -> List[Dict[str, Any]]:
        return []


class DockerHubRegistryConnector(RegistryConnector):
    def __init__(self, registry_url: str):
        self.registry_url = registry_url

    def list_servers(self) -> List[Dict[str, Any]]:
        return []
