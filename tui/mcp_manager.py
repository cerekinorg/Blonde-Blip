import logging
import os
import json
import subprocess
import threading
import time
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Any, Dict, Optional

from .mcp_config import MCPServerDefinition


logger = logging.getLogger("blonde")


@dataclass
class MCPServerProcess:
    definition: MCPServerDefinition
    process: subprocess.Popen
    started_at: float


class MCPClient:
    def __init__(self, server: MCPServerProcess):
        self.server = server

    def list_tools(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        raise NotImplementedError


class StdioJsonRpcMCPClient(MCPClient):
    def __init__(self, server: MCPServerProcess, read_timeout_s: float = 30.0):
        super().__init__(server)
        self._read_timeout_s = read_timeout_s
        self._id_lock = threading.Lock()
        self._next_id = 1
        self._pending: Dict[int, Queue] = {}
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def initialize(self) -> None:
        self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "blonde-cli", "version": "0.1.3"},
                "capabilities": {"tools": {}},
            },
        )
        self._notify("initialized", {})

    def list_tools(self) -> list[dict[str, Any]]:
        resp = self._request("tools/list", {})
        tools = resp.get("tools")
        if isinstance(tools, list):
            return tools
        return []

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        resp = self._request("tools/call", {"name": name, "arguments": arguments})
        return resp

    def _notify(self, method: str, params: Dict[str, Any]) -> None:
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        self._send(msg)

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        with self._id_lock:
            request_id = self._next_id
            self._next_id += 1

        q: Queue = Queue(maxsize=1)
        self._pending[request_id] = q
        try:
            msg = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
            self._send(msg)
            try:
                result = q.get(timeout=self._read_timeout_s)
            except Empty:
                raise TimeoutError(f"Timed out waiting for MCP response: {method}")

            if "error" in result and result["error"] is not None:
                raise RuntimeError(str(result["error"]))

            payload = result.get("result")
            if isinstance(payload, dict):
                return payload
            return {"result": payload}
        finally:
            self._pending.pop(request_id, None)

    def _send(self, msg: Dict[str, Any]) -> None:
        if not self.server.process.stdin:
            raise RuntimeError("MCP server stdin is not available")
        wire = json.dumps(msg, separators=(",", ":"))
        self.server.process.stdin.write(wire + "\n")
        self.server.process.stdin.flush()

    def _reader_loop(self) -> None:
        stdout = self.server.process.stdout
        if stdout is None:
            return

        while True:
            if self.server.process.poll() is not None:
                return
            line = stdout.readline()
            if not line:
                time.sleep(0.01)
                continue
            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except Exception:
                continue

            msg_id = msg.get("id")
            if isinstance(msg_id, int) and msg_id in self._pending:
                try:
                    self._pending[msg_id].put_nowait(msg)
                except Exception:
                    pass


class MCPServerManager:
    def __init__(self):
        self._servers: Dict[str, MCPServerProcess] = {}
        self._clients: Dict[str, MCPClient] = {}
        self._lock = threading.Lock()

    def start_server(self, definition: MCPServerDefinition) -> MCPServerProcess:
        if definition.transport != "stdio":
            raise ValueError(f"Unsupported MCP transport: {definition.transport}")

        with self._lock:
            if definition.server_id in self._servers:
                return self._servers[definition.server_id]

            proc = subprocess.Popen(
                [definition.command, *definition.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, **definition.env},
            )
            server_proc = MCPServerProcess(definition=definition, process=proc, started_at=time.time())
            self._servers[definition.server_id] = server_proc
            client = StdioJsonRpcMCPClient(server_proc)
            try:
                client.initialize()
            except Exception:
                # Keep server alive for best-effort use; caller may stop it.
                pass
            self._clients[definition.server_id] = client
            logger.debug(f"Started MCP server {definition.server_id}: {definition.command} {definition.args}")
            return server_proc

    def stop_server(self, server_id: str, timeout_s: float = 3.0) -> None:
        with self._lock:
            server = self._servers.get(server_id)
            if not server:
                return

            self._clients.pop(server_id, None)

            try:
                server.process.terminate()
                server.process.wait(timeout=timeout_s)
            except Exception:
                try:
                    server.process.kill()
                except Exception:
                    pass
            finally:
                self._servers.pop(server_id, None)

    def stop_all(self) -> None:
        with self._lock:
            server_ids = list(self._servers.keys())
        for sid in server_ids:
            self.stop_server(sid)

    def get_client(self, server_id: str) -> Optional[MCPClient]:
        with self._lock:
            return self._clients.get(server_id)

    def list_server_ids(self) -> list[str]:
        with self._lock:
            return list(self._servers.keys())

    def status(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        with self._lock:
            for sid, server in self._servers.items():
                running = server.process.poll() is None
                out[sid] = "running" if running else "stopped"
        return out


class MCPToolAdapter:
    def __init__(self, server_manager: MCPServerManager):
        self.server_manager = server_manager

    def list_available_tools(self) -> Dict[str, Dict[str, Any]]:
        discovered: Dict[str, Dict[str, Any]] = {}
        for server_id in self.server_manager.list_server_ids():
            client = self.server_manager.get_client(server_id)
            if client is None:
                continue
            try:
                tools = client.list_tools()
            except Exception:
                continue

            for t in tools:
                name = t.get("name")
                if not isinstance(name, str) or not name:
                    continue
                discovered[name] = {"server_id": server_id, "remote_name": name, "meta": t}
        return discovered

    def build_tool_callable(self, server_id: str, tool_name: str):
        def _tool_callable(**kwargs):
            client = self.server_manager.get_client(server_id)
            if client is None:
                return f"❌ MCP server not available: {server_id}"
            try:
                result = client.call_tool(tool_name, kwargs)
                return str(result)
            except Exception as e:
                return f"❌ MCP tool error: {e}"

        return _tool_callable
