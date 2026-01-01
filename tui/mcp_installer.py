from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class MCPInstallResult:
    server_id: str
    install_dir: Path
    success: bool
    message: str


class MCPServerInstaller:
    def __init__(self, install_root: Optional[Path] = None):
        self.install_root = install_root or (Path.home() / ".blonde" / "mcp_servers")
        self.install_root.mkdir(parents=True, exist_ok=True)

    def install(self, server_id: str) -> MCPInstallResult:
        install_dir = self.install_root / server_id
        install_dir.mkdir(parents=True, exist_ok=True)
        return MCPInstallResult(
            server_id=server_id,
            install_dir=install_dir,
            success=False,
            message="Installer not implemented yet",
        )
