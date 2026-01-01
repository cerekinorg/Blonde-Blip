import difflib
import os
import sys
import time
import requests
import typer
import yaml
import json
import re
import ast
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.layout import Layout
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress
from rich.status import Status
from rich.live import Live
from difflib import unified_diff
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv
import magic
from git import Repo

# Add project directory to Python path for imports to work
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from tui.utils import setup_logging, save_api_key, load_api_key

# Import memory and tools for context-aware and agentic capabilities
try:
    from tui.memory import MemoryManager
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    logger = logging.getLogger("blonde")
    logger.debug("Memory system not available. Install dependencies: pip install chromadb")

try:
    from tools import ToolRegistry
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    logger = logging.getLogger("blonde")
    logger.debug("Tools system not available.")

try:
    from tui.agentic_tools import EnhancedToolRegistry, TaskPlanner, AgenticExecutor
    AGENTIC_AVAILABLE = True
except ImportError:
    AGENTIC_AVAILABLE = False
    logger = logging.getLogger("blonde")
    logger.debug("Enhanced agentic tools not available.")

try:
    from tui.mcp_config import MCPConfig
    from tui.mcp_manager import MCPServerManager, MCPToolAdapter
    MCP_INTEGRATION_AVAILABLE = True
except Exception:
    MCP_INTEGRATION_AVAILABLE = False

try:
    from model_selector import select_model
    MODEL_SELECTOR_AVAILABLE = True
    logger.info("Model selector loaded successfully")
except ImportError as e:
    MODEL_SELECTOR_AVAILABLE = False
    logger.warning(f"Model selector import failed: {e}")
except Exception as e:
    MODEL_SELECTOR_AVAILABLE = False
    logger.error(f"Model selector unexpected error: {e}")


console = Console()
app = typer.Typer()
load_dotenv()
logging.basicConfig(filename=str(Path.home() / ".blonde/debug.log"), level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("blonde")

# =====================
#  Constants
# =====================
ASCII_LOGO = r"""
 ██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
 ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══╝██╔════╝
 ██████╔╝██║     ██║   ██║██╔██╗ ██║  ██║  ██████╗  
 ██╔══██╗██║     ██║   ██║██╚██╗ ██║  ██║ ╚═════  
  ██████╔███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
 ██████╔╝███████╗ ╚═════╝ ╚═╝  ╚═╝╚═══╝╚═══════╝
 """

HELP_TEXT = """
[bold cyan]Blonde CLI Help[/bold cyan]

[green]Modes:[/green]
 • [bold]blnd chat[/bold] → interactive chat
 • [bold]blnd gen "prompt"[/bold] → generate code
 • [bold]blnd fix file.py[/bold] → fix code with diff preview
 • [bold]blnd doc file.py[/bold] → explain/document code

[green]In chat mode:[/green]
 • Type any message to chat with Blonde
 • [bold]exit[/bold] or [bold]quit[/bold] to leave
 • [bold]help[/bold] to see this message again
 • [bold]/save[/bold] → export chat to Markdown

"""


HISTORY_FILE = Path.home() / ".blonde_history_default.json"
EXCLUDED_DIRS = {"__pycache__", ".git", "venv", "node_modules", ".idea", ".mypy_cache"}
INCLUDED_EXTS = {"py", "js", "ts", "java", "c", "cpp", "json", "yml", "yaml", "toml", "md"}
repo_map_cache = {}
CONFIG_FILE = Path.home() / ".blonde" / "config.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)

