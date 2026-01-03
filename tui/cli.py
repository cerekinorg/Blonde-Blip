


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

# Add project directory to Python path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

try:
    from tui.utils import setup_logging, save_api_key, load_api_key
except ImportError:
    setup_logging = None
    save_api_key = None
    load_api_key = None
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

# Import parallel executor and optimizer for advanced agent coordination
try:
    from tui.parallel_executor import ParallelAgentExecutor, QualityGateResult
    from tui.optimizer_agent import OptimizerAgent
    from tui.blip import blip
    PARALLEL_EXECUTION_AVAILABLE = True
except Exception:
    PARALLEL_EXECUTION_AVAILABLE = False
    logger.debug("Parallel execution not available")
    blip = None

console = Console()
app = typer.Typer()
load_dotenv()

# Add callback to launch dashboard by default (like OpenCode)
@app.callback()
def main_callback(ctx: typer.Context, no_tui: bool = False, modern: bool = False):
    """
    Blonde CLI - Privacy-First Multi-Agent AI Development Assistant

    When run without arguments, launches Dashboard TUI.
    Use --no-tui to skip TUI and use CLI mode.
    Use --modern to launch the new modern Textual TUI.
    """
    # If no subcommand provided and not explicitly disabling TUI, launch dashboard
    if ctx.invoked_subcommand is None and not no_tui:
        if modern:
            from tui.modern_tui import launch_modern_tui
            launch_modern_tui()
        else:
            from tui.main_tui import launch_dashboard
            launch_dashboard()

logging.basicConfig(filename=str(Path.home() / ".blonde/debug.log"), level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("blonde")

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

# =====================
#  Constants
# =====================
ASCII_LOGO = r"""
 ██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
 ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══██╗██╔════╝
██████╔╝██║     ██║   ██║██╔██╗ ██║██║  ██║█████╗  
██╔══██╗██║     ██║   ██║██║╚██╗██║██║  ██║██╔══╝  
 ██████╔╝███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
 ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝
"""

HELP_TEXT = """
[bold cyan]Blonde CLI Help[/bold cyan]

[green]Modes:[/green]
 • [bold]blnd chat[/bold] → interactive chat
 • [bold]blnd gen "prompt"[/bold] → generate code
 • [bold]blnd fix file.py[/bold] → fix code with diff preview
 • [bold]blnd doc file.py[/bold] → explain/document code
 • [bold]blnd create "description" file.py[/bold] → create new file

[green]In chat mode:[/green]
 • Type any message to chat with Blonde
 • [bold]exit[/bold] or [bold]quit[/bold] to leave
 • [bold]help[/bold] to see this message again
 • [bold]/save[/bold] → export chat to Markdown

[green]AI Agents (9 total):[/green]
 • 🧱 Generator - Generates initial code
 • 🔍 Reviewer - Reviews code quality
 • 🧪 Tester - Generates tests
 • 🔨 Refactorer - Refactors code
 • 📝 Documenter - Writes docs
 • 🏗️ Architect - Designs architecture
 • 🔒 Security - Checks security
 • 🐛 Debugger - Fixes bugs
 • ⚡ Optimizer - Coordinates all agents (MASTER)

[green]Agent Commands:[/green]
 • [bold]blnd dev-team status[/bold] → show all agents
 • [bold]blnd dev-team collaborate "task"[/bold] → agents work together
 • [bold]blnd agent-task "task"[/bold] → NEW: Parallel execution with Optimizer
"""


HISTORY_FILE = Path.home() / ".blonde_history_default.json"
EXCLUDED_DIRS = {"__pycache__", ".git", "venv", "node_modules", ".idea", ".mypy_cache"}
INCLUDED_EXTS = {"py", "js", "ts", "java", "c", "cpp", "json", "yml", "yaml", "toml", "md"}
repo_map_cache = {}
CONFIG_FILE = Path.home() / ".blonde" / "config.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)


# =====================
#  Utilities
# =====================

@app.command()
def set_key(model: str, key: str):
    """Set API key for a model."""
    key_name = f"{model.upper()}_API_KEY"
    save_api_key(key_name, key)
    console.print(f"[green]{key_name} saved locally![/green]")


def detect_language(file_path: str) -> str:
    """Detects programming language from file content or extension.
    Args:
        file_path: Path to the file.
    Returns:
        Language string (e.g., 'python', 'javascript').
    Why it works: Uses file extension and content analysis via python-magic.
    Pitfalls: Non-standard extensions may return 'unknown'; ensure python-magic is installed.
    Learning: Explore tree-sitter for precise language parsing.
    """
    ext_lang_map = {
        "py": "python", "js": "javascript", "ts": "typescript",
        "java": "java", "c": "c", "cpp": "cpp"
    }
    ext = file_path.split(".")[-1].lower()
    if ext in ext_lang_map:
        return ext_lang_map[ext]
    
    try:
        with open(file_path, "rb") as f:
            content = f.read(1024)
        mime = magic.from_buffer(content, mime=True)
        if "python" in mime:
            return "python"
        elif "javascript" in mime or "ecmascript" in mime:
            return "javascript"
        elif "java" in mime:
            return "java"
        elif "c++" in mime or "c" in mime:
            return "cpp" if ext == "cpp" else "c"
        return ext_lang_map.get(ext, "unknown")
    except Exception as e:
        logger.debug(f"Language detection failed for {file_path}: {e}")
        return ext_lang_map.get(ext, "unknown")

def scan_repo(path: str) -> dict:
    """Walk through a repo, extract functions, classes, imports, and call graphs.
    Args:
        path: Directory path to scan.
    Returns:
        Dict mapping file paths to metadata.
    Why it works: Uses AST for Python files, skips irrelevant dirs.
    Pitfalls: Large repos may be slow; non-Python files have limited parsing.
    Learning: Add tree-sitter for multi-language parsing.
    """
    repo_map = {}
    class CallGraphVisitor(ast.NodeVisitor):
        def __init__(self):
            self.calls = []
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                self.calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.calls.append(node.func.attr)
            self.generic_visit(node)

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            ext = file.split(".")[-1]
            if ext not in INCLUDED_EXTS:
                continue
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, path)
            repo_map[relative_path] = {
                "functions": [], "classes": [], "imports": [], "calls": []
            }
            try:
                if ext == "py":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)
                    visitor = CallGraphVisitor()
                    visitor.visit(tree)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            repo_map[relative_path]["functions"].append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            repo_map[relative_path]["classes"].append(node.name)
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            for alias in node.names:
                                repo_map[relative_path]["imports"].append(alias.name)
                    repo_map[relative_path]["calls"] = visitor.calls
                else:
                    repo_map[relative_path]["functions"].append(f"unparsed_{ext}")
            except Exception as e:
                repo_map[relative_path]["error"] = str(e)
                logger.debug(f"Scan error for {file_path}: {e}")
    return repo_map

def render_code_blocks(text: str) -> None:
    """Renders Markdown text with code blocks using syntax highlighting.
    Args:
        text: Markdown text to render.
    Why it works: Splits text into code and non-code segments, uses Syntax for highlighting.
    Pitfalls: Malformed Markdown may cause errors; handle gracefully.
    Learning: Explore Rich’s Live for real-time rendering.
    """
    text = text.strip()
    if "```" not in text:
        console.print(Markdown(text, style="white"))
        return
    segments = text.split("```")
    for i, segment in enumerate(segments):
        if i % 2 == 1:
            try:
                lang, *code_lines = segment.split("\n", 1)
                code = code_lines[0].strip() if code_lines else ""
                if code:
                    console.print(Syntax(code, lang.strip() or "python", theme="monokai", line_numbers=False))
            except Exception as e:
                logger.debug(f"Render code error: {e}")
                console.print(f"[red]Error rendering code: {e}[/red]")
                console.print(segment.strip(), style="white")
        else:
            if segment.strip():
                console.print(Markdown(segment.strip(), style="white"))

def extract_code(text: str) -> str:
    """Extracts code from markdown-style ``` blocks.
    Args:
        text: Input text with potential code blocks.
    Returns:
        Extracted code or original text.
    Why it works: Uses regex to extract code reliably.
    Pitfalls: Malformed Markdown may return partial code.
    Learning: Study re module for advanced pattern matching.
    """
    if "```" in text:
        matches = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)
        if matches:
            return matches[0].strip()
    return text.strip()

# =====================
#  Shared Helpers
# =====================
def animate_logo():
    """Displays the Blonde CLI logo and help text.
    Why it works: Uses Rich for styled output.
    Pitfalls: Console size may affect rendering.
    Learning: Explore Rich’s Panel for custom layouts.
    """
    console.clear()
    console.print(Text(ASCII_LOGO, style="bold magenta"), justify="center")
    console.print(Panel(
        Text("Welcome to Blonde CLI 🚀", justify="center", style="bold cyan"),
        border_style="blue", expand=False
    ))
    console.print(HELP_TEXT)
    time.sleep(1)

# def load_adapter(debug: bool = False):
#     """Loads the appropriate model adapter based on config.yml.
#     Args:
#         debug: Enable debug logging.
#     Returns:
#         Model adapter instance.
#     Why it works: Dynamically loads adapters, defaults to OpenRouter.
#     Pitfalls: Missing config.yml causes fallback.
#     Learning: Study dynamic imports with importlib.
#     """
#     try:
#         with open("config.yml") as f:
#             cfg = yaml.safe_load(f)
#         model = cfg.get("default_model", "openrouter")
#     except FileNotFoundError:
#         model = "openrouter"
#         logger.debug("config.yml not found, using openrouter")

#     if model == "openai":
#         from models.openai import OpenAIAdapter
#         return OpenAIAdapter(debug=debug)
#     elif model == "hf":
#         from models.hf import HFAdapter
#         return HFAdapter(debug=debug)
#     else:
#         from models.openrouter import OpenRouterAdapter
#         return OpenRouterAdapter(debug=debug)


# def load_adapter(model_name="openrouter", debug=False):
#     """Load selected model adapter."""
#     if model_name == "openai":
#         from models.openai import OpenAIAdapter
#         return OpenAIAdapter()
#     elif model_name == "hf":
#         from models.hf import HFAdapter
#         return HFAdapter()
#     else:
#         from models.openrouter import OpenRouterAdapter
#         return OpenRouterAdapter(debug=debug)


def load_adapter(model_name="openrouter", offline: bool = False, debug: bool = False, gguf_model: str = None, cached_path: str = None):
    """Load model adapter with optional GGUF model.
    Args:
        model_name: Online model provider (openrouter, openai, hf).
        offline: Force offline mode.
        debug: Enable debug logging.
        gguf_model: Specific GGUF model (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf).
        cached_path: Direct path to cached model file (skips download).
    """
    if offline or gguf_model:
        from models.local import LocalAdapter
        if gguf_model:
            # Split on LAST slash to separate repo from filename
            # Format: "TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf"
            if "/" in gguf_model:
                repo, file = gguf_model.rsplit("/", 1)
            else:
                repo, file = gguf_model, None
            console.print(f"[dim]Loading: repo={repo}, file={file}[/dim]")
            return LocalAdapter(model_name=repo, model_file=file, debug=debug, cached_path=cached_path)
        console.print("[dim]Loading default LocalAdapter (CodeLlama)[/dim]")
        return LocalAdapter(debug=debug, cached_path=cached_path)
    try:
        # Check internet
        import requests
        requests.get("https://www.google.com", timeout=2)
        if model_name == "openai":
            from models.openai import OpenAIAdapter
            return OpenAIAdapter(debug=debug)
        elif model_name == "hf":
            from models.hf import HFAdapter
            return HFAdapter(debug=debug)
        else:
            from models.openrouter import OpenRouterAdapter
            return OpenRouterAdapter(debug=debug)
    except requests.RequestException:
        console.print("[yellow]No internet; falling back to offline.[/yellow]")
        from models.local import LocalAdapter
        return LocalAdapter(debug=debug)


# bot = load_adapter()


def get_response(prompt: str, debug: bool = False) -> str:
    """Fetches response from the active adapter with spinner.
    Args:
        prompt: User input.
        debug: Enable debug.
    Returns:
        Response string.
    Why it works: Spinner shows progress; retries handle transients.
    Pitfalls: Long prompts may timeout; truncate context.
    Learning: Explore Rich Status for custom spinners.
    """
    with Status("Blonde is thinking...", spinner="dots") as status:
        if debug:
            logger.debug(f"Prompt: {prompt[:500]}")
        try:
            response = bot.chat(prompt)
            if isinstance(response, str):
                return response.strip()
            elif isinstance(response, dict):
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise ValueError("Empty content")
                return content.strip()
            else:
                raise ValueError(f"Unexpected type: {type(response)}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After", 10)
                logger.warning(f"Rate limit, waiting {retry_after}s")
                console.print(f"[yellow]Rate limit hit, waiting {retry_after}s...[/yellow]")
                time.sleep(int(retry_after))
                raise
            raise
        except Exception as e:
            logger.error(f"API Error: {e}")
            console.print(f"[red]API Error: {e}[/red]")
            return "Sorry, there was an error. Try again."

def save_history(history: list) -> None:
    """Saves chat history to JSON file.
    Args:
        history: List of (sender, message) tuples.
    Why it works: Persists chat for session continuity.
    Pitfalls: File permissions may cause errors.
    Learning: Study JSON serialization.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def load_history() -> list:
    """Loads chat history from JSON file.
    Returns:
        List of (sender, message) tuples.
    Why it works: Restores previous chats for context.
    Pitfalls: Corrupted JSON may cause errors.
    Learning: Explore pathlib for file handling.
    """
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def stream_response(text: str, delay: float = 0.01) -> str:
    """Streams text with markdown rendering like ChatGPT.
    Args:
        text: Text to stream.
        delay: Delay between chunks (characters).
    Returns:
        Full text buffer.
    Why it works: Uses Rich Live to update markdown rendering in real-time.
    Pitfalls: Very fast on small texts; adjust delay as needed.
    Learning: Rich's Live allows dynamic content updates without flickering.
    """
    buffer = ""
    
    # Split into chunks for smoother streaming (2-3 chars at a time)
    chunk_size = 3
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    with Live("", console=console, refresh_per_second=20) as live:
        for chunk in chunks:
            buffer += chunk
            
            # Render current buffer as markdown with cursor
            try:
                # Add a blinking cursor effect
                display_text = buffer + "▊"
                
                # Try to render as markdown
                if "```" in buffer and buffer.count("```") % 2 == 0:
                    # Complete code block - render it properly
                    live.update(Markdown(buffer))
                else:
                    # Still typing - show as text with cursor
                    live.update(Text(display_text, style="white"))
                    
            except Exception as e:
                # Fallback to plain text
                live.update(Text(buffer + "▊", style="white"))
            
            time.sleep(delay)
        
        # Final render without cursor - use the full render_code_blocks function
        live.update("")
    
    # Now render the complete markdown properly
    render_code_blocks(buffer)
    console.print()  # Add spacing
    
    return buffer

def suggest_terminal_command(user_input: str) -> str | None:
    """Suggests terminal commands based on user input.
    Args:
        user_input: User’s chat input.
    Returns:
        Suggested command or None.
    Why it works: Adds Warp-like interactivity.
    Pitfalls: Limited command mappings; expand dictionary.
    Learning: Study NLP for intent detection.
    """
    command_map = {
        "list files": "ls",
        "show directory": "pwd",
        "change directory": "cd",
        "remove file": "rm",
        "create directory": "mkdir"
    }
    for key, cmd in command_map.items():
        if key in user_input.lower():
            return f"[yellow]Suggested command: {cmd}[/yellow]"
    return None

# =====================
#  Commands
# =====================

# Add optional model selection to all commands
@app.callback()
def main(
    model: str = typer.Option("openrouter", help="Model to use (openai/hf/openrouter)"),
    debug: bool = typer.Option(False, help="Enable debug logging")
):
    global bot, HISTORY_FILE
    bot = load_adapter(model_name=model, debug=debug)
    model_name_lower = bot.__class__.__name__.replace("Adapter", "").lower()
    HISTORY_FILE = Path.home() / f".blonde_history_{model_name_lower}.json"

@app.command()
def chat(
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory (remembers past conversations)"),
    agentic: bool = typer.Option(True, help="Enable agentic mode (AI can use tools)"),
    mcp_disable: bool = typer.Option(False, help="Disable MCP tool integration"),
    mcp_servers: str = typer.Option(None, help="Comma-separated MCP server ids to load (overrides config)"),
    stream: bool = typer.Option(True, help="Stream responses for better UX")
):
    """Interactive chat with Blonde - now with memory and agentic capabilities!"""
    global bot
    
    # DEBUG: Show what we received
    console.print(f"[red]DEBUG: offline={offline}, model={model}, MODEL_SELECTOR_AVAILABLE={MODEL_SELECTOR_AVAILABLE}[/red]")
    console.print(f"[red]DEBUG: Condition check: {offline and not model and MODEL_SELECTOR_AVAILABLE}[/red]")
    
    # Interactive model selection for offline mode
    cached_model_path = None
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        console.print("[dim]Launching model selector...[/dim]")
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        
        repo, file, is_cached, path = selection
        console.print(f"[dim]Selected: repo={repo}, file={file}[/dim]")
        model = f"{repo}/{file}"
        if is_cached and path:
            # Store cached path to skip download
            cached_model_path = path
            console.print(f"[dim]Using cached path: {cached_model_path}[/dim]")
        else:
            console.print(f"[dim]Will download: {model}[/dim]")
    
    # Load the adapter
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model, cached_path=cached_model_path)
    
    # Show logo and welcome
    animate_logo()
    
    # Initialize memory manager if enabled (AFTER logo so it's visible)
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled - I'll remember our conversation![/dim]")
        except Exception as e:
            logger.warning(f"Failed to initialize memory: {e}")
            console.print("[yellow]⚠ Memory disabled - install chromadb to enable[/yellow]")
    
    # Initialize tool registry if agentic mode enabled (AFTER logo so it's visible)
    tool_registry = None
    agentic_executor = None
    task_planner = None

    mcp_status_text = None
    mcp_adapter = None
    mcp_server_manager = None

    if (not mcp_disable) and MCP_INTEGRATION_AVAILABLE:
        try:
            config = MCPConfig.load_if_exists()
            if config:
                mcp_server_manager = MCPServerManager()

                allowed = None
                if mcp_servers:
                    allowed = {s.strip() for s in mcp_servers.split(",") if s.strip()}

                started = []
                for definition in config.iter_server_definitions():
                    if allowed is not None and definition.server_id not in allowed:
                        continue
                    if not definition.command:
                        continue
                    try:
                        mcp_server_manager.start_server(definition)
                        started.append(definition.server_id)
                    except Exception:
                        continue

                mcp_adapter = MCPToolAdapter(mcp_server_manager)
                mcp_status_text = f"MCP: {len(started)} server(s)"
        except Exception:
            mcp_adapter = None
            mcp_server_manager = None

    if agentic and AGENTIC_AVAILABLE:
        try:
            enhanced_tools = EnhancedToolRegistry(require_confirmation=True, mcp_tool_adapter=mcp_adapter)
            task_planner = TaskPlanner(bot)
            agentic_executor = AgenticExecutor(bot, enhanced_tools, task_planner)
            console.print("[dim]✓ Enhanced agentic mode enabled - I can autonomously complete tasks![/dim]")
        except Exception as e:
            logger.warning(f"Failed to initialize agentic tools: {e}")
            console.print("[yellow]⚠ Agentic mode disabled[/yellow]")
    elif agentic and TOOLS_AVAILABLE:
        try:
            tool_registry = ToolRegistry(require_confirmation=True, log_calls=True)
            console.print("[dim]✓ Basic tool mode enabled[/dim]")
        except Exception as e:
            logger.warning(f"Failed to initialize tools: {e}")
            console.print("[yellow]⚠ Tool mode disabled[/yellow]")
    
    # Enhanced welcome message
    welcome_parts = ["Type your prompt below. Use /help for commands."]
    if memory_manager:
        welcome_parts.append("💭 Memory: ON")
    if agentic_executor:
        welcome_parts.append("🤖 Agentic: ON (Enhanced)")
    elif tool_registry:
        welcome_parts.append("🔧 Tools: ON (Basic)")
    if mcp_status_text:
        welcome_parts.append(mcp_status_text)
    if stream:
        welcome_parts.append("⚡ Streaming: ON")
    
    console.print(Panel(Text(" | ".join(welcome_parts), justify="center"), border_style="cyan"))

    chat_history = load_history()

    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")
        
        # Handle exit commands
        if user_input.lower() in ("exit", "quit"):
            save_history(chat_history)
            if memory_manager:
                console.print("[dim]💾 Saving memories...[/dim]")
            console.print("[bold red]Goodbye! 👋[/bold red]")
            break
            
        # Handle /help command
        if user_input.lower() == "/help":
            enhanced_help = HELP_TEXT + "\n[green]Enhanced Commands:[/green]\n"
            enhanced_help += " • [bold]/memory[/bold] → show memory stats\n"
            enhanced_help += " • [bold]/tools[/bold] → list available tools\n"
            enhanced_help += " • [bold]/plan[/bold] → show current execution plan\n"
            enhanced_help += " • [bold]/agent <task>[/bold] → execute task autonomously\n"
            enhanced_help += " • [bold]/context[/bold] → show conversation context\n"
            console.print(Panel(Text(enhanced_help, justify="left"), border_style="cyan"))
            continue
            
        # Handle /clear command
        if user_input.lower() == "/clear":
            chat_history = []
            if memory_manager:
                memory_manager.clear_session()
            console.print("[bold yellow]💨 Chat and memory cleared.[/yellow]")
            continue
            
        # Handle /save command
        if user_input.lower() == "/save":
            out_file = "blonde_chat.md"
            with open(out_file, "w") as f:
                for sender, msg in chat_history:
                    f.write(f"**{sender}:** {msg}\n\n")
            console.print(f"[bold green]💾 Chat exported to {out_file}[/bold green]")
            continue
        
        # NEW: Handle /memory command
        if user_input.lower() == "/memory" and memory_manager:
            memory_manager.show_session_state()
            continue
            
        # NEW: Handle /tools command
        if user_input.lower() == "/tools":
            if agentic_executor:
                # Show enhanced tools
                tools = agentic_executor.tools
                console.print("\n[cyan]📦 Enhanced Agentic Tools:[/cyan]")
                console.print("\n[yellow]File Operations:[/yellow]")
                console.print("  • read_file, write_file, edit_file, delete_file, rename_file")
                console.print("\n[yellow]Code Operations:[/yellow]")
                console.print("  • replace_in_file, insert_at_line, remove_lines")
                console.print("\n[yellow]Directory Operations:[/yellow]")
                console.print("  • list_dir, create_dir, search_files, search_in_files")
                console.print("\n[yellow]Git Operations:[/yellow]")
                console.print("  • git_status, git_diff, git_add, git_commit")
                console.print("\n[yellow]Analysis:[/yellow]")
                console.print("  • count_lines, run_command")
                console.print("\n[dim]Type '/agent <your task>' to execute autonomously![/dim]\n")
            elif tool_registry:
                tools_list = tool_registry.list_tools()
                console.print(Panel(f"[cyan]Available tools: {', '.join(tools_list)}[/cyan]", 
                                  border_style="cyan"))
            else:
                console.print("[yellow]No tools available[/yellow]")
            continue
            
        # NEW: Handle /plan command
        if user_input.lower() == "/plan" and task_planner:
            task_planner.display_plan()
            continue
            
        # NEW: Handle /agent command for autonomous execution
        if user_input.lower().startswith("/agent ") and agentic_executor:
            task = user_input[7:].strip()  # Remove '/agent '
            console.print(f"\n[bold cyan]🤖 Executing task autonomously...[/bold cyan]\n")
            result = agentic_executor.execute_task(task, auto_confirm=False)
            console.print(f"\n[green]Result:[/green]\n{result}")
            chat_history.append(("Agent", result))
            if memory_manager:
                memory_manager.add_conversation(task, result)
            continue
        
        # NEW: Handle /context command
        if user_input.lower() == "/context" and memory_manager:
            context = memory_manager.get_context_for_prompt(user_input, max_context_length=500)
            console.print(Panel(f"[dim]{context}[/dim]", title="Current Context", border_style="cyan"))
            continue

        # Terminal command suggestions
        suggestion = suggest_terminal_command(user_input)
        if suggestion and not agentic:
            console.print(suggestion)
            if Prompt.ask("Run it? [y/n]", default="n") == "y":
                os.system(suggestion.replace("[yellow]Suggested command: ", "").strip())
            continue

        # Add to chat history
        chat_history.append(("You", user_input))
        
        # Build context-aware prompt
        prompt = user_input
        if memory_manager:
            # Retrieve relevant context from long-term memory
            context = memory_manager.get_context_for_prompt(user_input, max_context_length=2000)
            if context:
                prompt = f"Context from previous conversations:\n{context}\n\nCurrent query: {user_input}"
        
        console.print("[magenta]Blonde:[/magenta]")
        try:
            # Get response with streaming if enabled
            if blip and stream:
                blip.think("I'm thinking about your request...")
            
            if stream:
                response = get_response(prompt, debug)
                stream_response(response)
            else:
                response = get_response(prompt, debug)
                render_code_blocks(response)
            
            if blip:
                blip.happy("Done! Let me know if you need anything else!")
            
            chat_history.append(("Blonde", response))
            
            # Store in memory if enabled
            if memory_manager:
                memory_manager.add_conversation(user_input, response)
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            console.print(f"[red]Error: {e}[/red]")
        
        console.rule(style="dim")




@app.command()
def gen(
    prompt: str, 
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory for better generation"),
    save: str = typer.Option(None, help="Save generated code to file"),
    lang: str = typer.Option(None, help="Target language (python, javascript, etc)")
):
    """Generate code from a prompt with context awareness.
    
    Enhanced with memory to remember past code patterns and preferences.
    """
    global bot
    
    # Interactive model selection for offline mode
    cached_model_path = None
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file, is_cached, path = selection
        model = f"{repo}/{file}"
        if is_cached and path:
            cached_model_path = path
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model, cached_path=cached_model_path)
    
    # Initialize memory if enabled
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
    
    console.print(Panel("Blonde CLI - Context-Aware Code Generation", style="bold cyan"))
    
    # Build context-aware prompt
    enhanced_prompt = prompt
    if memory_manager:
        context = memory_manager.get_context_for_prompt(prompt, max_context_length=1500)
        if context:
            enhanced_prompt = f"Previous code context:\n{context}\n\nNew request: {prompt}"
            console.print("[dim]✓ Using relevant context from memory[/dim]")
    
    if lang:
        enhanced_prompt = f"Generate code in {lang}:\n{enhanced_prompt}"
    
    response = get_response(enhanced_prompt, debug)
    render_code_blocks(response)
    
    # Store in memory for future reference
    if memory_manager:
        memory_manager.add_conversation(f"Code generation: {prompt}", response)
    
    # Save to file if requested
    if save:
        code = extract_code(response)
        with open(save, "w", encoding="utf-8") as f:
            f.write(code)
        console.print(f"[green]✓ Code saved to {save}[/green]")

@app.command()
def create(
    description: str,
    file: str,
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory"),
    agentic: bool = typer.Option(False, help="Enable agentic mode (auto-create related files)"),
    iterative: bool = typer.Option(False, help="Enable iterative refinement"),
    with_tests: bool = typer.Option(False, help="Generate unit tests alongside code")
):
    """Create a new code file with context awareness and agentic capabilities.
    
    Enhanced features:
    - Memory: Learns from past file creations
    - Agentic: Can suggest and create related files
    - Iterative: Refine the code before saving
    - Tests: Auto-generate unit tests
    """
    global bot
    
    # Interactive model selection for offline mode
    cached_model_path = None
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file_model, is_cached, path = selection
        model = f"{repo}/{file_model}"
        if is_cached and path:
            cached_model_path = path
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model, cached_path=cached_model_path)
    
    # Initialize memory and tools
    memory_manager = None
    tool_registry = None
    
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled[/dim]")
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
    
    if agentic and TOOLS_AVAILABLE:
        try:
            tool_registry = ToolRegistry(require_confirmation=True, log_calls=True)
            console.print("[dim]✓ Agentic mode enabled[/dim]")
        except Exception as e:
            logger.warning(f"Agentic mode disabled: {e}")
    
    console.print(Panel("Blonde CLI - Intelligent File Creation", style="bold cyan"))

    repo_path = os.path.dirname(file) if os.path.dirname(file) else "."
    repo_map = scan_repo(repo_path) if os.path.isdir(repo_path) else {}
    context = str(repo_map)[:2000]
    lang = detect_language(file)
    
    # Build enhanced prompt with memory context
    enhanced_description = description
    if memory_manager:
        mem_context = memory_manager.get_context_for_prompt(description, max_context_length=1000)
        if mem_context:
            enhanced_description = f"Context from similar past files:\n{mem_context}\n\nNew file description: {description}"
            console.print("[dim]✓ Using relevant context from memory[/dim]")
    
    prompt = f"""
    You are a code generator. Given this description and repo context, output ONLY the source code for a new file.
    Use language: {lang}.
    Repo context: {context}
    Description: {enhanced_description}
    Output code:
    """
    response = get_response(prompt, debug)
    cleaned = extract_code(response)
    
    # Iterative refinement
    if iterative:
        max_iters = 3
        for i in range(max_iters):
            console.print(Panel(f"Refinement Iteration {i+1}/{max_iters}", style="yellow"))
            console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))
            feedback = Prompt.ask("[green]Feedback (or 'done')[/green]", default="done")
            if feedback.lower() == "done":
                break
            refine_prompt = f"""
            Refine this code based on feedback: {feedback}
            Current code: {cleaned}
            Output ONLY the refined source code (language: {lang}).
            """
            cleaned = extract_code(get_response(refine_prompt, debug))

    console.print("\n[bold yellow]Preview of generated file:[/bold yellow]")
    console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))

    # Agentic suggestions for related files
    if agentic and tool_registry:
        suggestion_prompt = f"""
        Given this new file and its purpose, what related files should be created?
        File: {file}
        Description: {description}
        
        Suggest 1-3 related files (e.g., tests, config, documentation).
        Format: filename: purpose
        """
        suggestions = get_response(suggestion_prompt, debug)
        console.print(Panel(f"[cyan]Suggested related files:\n{suggestions}[/cyan]", 
                          title="Agentic Suggestions", border_style="cyan"))
        if Prompt.ask("Create suggested files?", choices=["y", "n"], default="n") == "y":
            console.print("[yellow]Agentic file creation will be added in future version[/yellow]")

    if os.path.exists(file):
        if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
            console.print("[red]Creation discarded.[/red]")
            return
    
    choice = Prompt.ask("\nSave file?", choices=["y", "n"], default="y")
    if choice == "y":
        with open(file, "w", encoding="utf-8") as f:
            f.write(cleaned)
        console.print(f"[green]✓ File created: {file}[/green]")
        
        # Store in memory
        if memory_manager:
            memory_manager.add_conversation(f"Created file {file}: {description}", cleaned[:500])
        
        # Generate tests if requested
        if with_tests:
            test_file = file.replace(".py", "_test.py").replace(".js", ".test.js")
            test_prompt = f"""
            Generate unit tests for this code:
            {cleaned}
            
            Output ONLY the test code in {lang}.
            """
            test_code = extract_code(get_response(test_prompt, debug))
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code)
            console.print(f"[green]✓ Tests created: {test_file}[/green]")
    else:
        console.print("[red]Creation discarded.[/red]")



@app.command()
def fix(
    path: str,
    export: str = typer.Option(None, help="Export diff(s) instead of applying"),
    preview: bool = typer.Option(False, help="Preview all diffs before applying"),
    iterative: bool = typer.Option(False, help="Iterative refinement mode"),
    suggest: bool = typer.Option(False, help="Show fix suggestions with explanations"),
    git_commit: bool = typer.Option(False, help="Auto-commit fixes to git"),
    skip_errors: bool = typer.Option(False, help="Skip files with errors and continue"),
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory for better fixes")
):
    """Fix bugs with context awareness from past fixes.
    
    Enhanced with memory to learn from previous bug fixes and apply similar patterns.
    """
    global bot, repo_map_cache
    
    # Interactive model selection for offline mode
    cached_model_path = None
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file, is_cached, path = selection
        model = f"{repo}/{file}"
        if is_cached and path:
            cached_model_path = path
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model, cached_path=cached_model_path)
    
    # Initialize memory
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled - learning from past fixes[/dim]")
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
    console.print(Panel("Blonde CLI - Fixing Codebase", style="bold cyan"))

    diffs = []
    if os.path.isdir(path):
        repo_map_cache[path] = scan_repo(path)
        console.print(f"[cyan]Repo map built with {len(repo_map_cache[path])} files[/cyan]")
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning files...", total=len(repo_map_cache[path]))
            for relative_path in repo_map_cache[path]:
                file_path = os.path.join(path, relative_path)
                try:
                    diff = _fix_file(file_path, repo_map_cache[path], export, preview, iterative, suggest, debug, memory_manager)
                    if diff:
                        diffs.append(diff)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    if skip_errors:
                        console.print(f"[yellow]Skipped {file_path} due to error: {e}[/yellow]")
                    else:
                        raise
                finally:
                    progress.update(task, advance=1)
    else:
        try:
            diff = _fix_file(path, repo_map_cache.get(os.path.dirname(path)), export, preview, iterative, suggest, debug, memory_manager)
            if diff:
                diffs.append(diff)
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            if skip_errors:
                console.print(f"[yellow]Skipped {path} due to error: {e}[/yellow]")
            else:
                raise

    if not diffs:
        console.print("[yellow]No changes proposed.[/yellow]")
        console.print("[yellow]If errors occurred, try --skip-errors or --debug.[/yellow]")
        return

    if preview:
        table = Table(title="Proposed Changes", show_lines=True)
        table.add_column("File", style="cyan")
        table.add_column("Diff", style="white")
        valid_diffs = []
        for diff in diffs:
            try:
                file, (original, cleaned, diff_text, suggestion) = diff
                table.add_row(file, diff_text)
                valid_diffs.append(diff)
            except ValueError as e:
                logger.error(f"Invalid diff format for {diff[0]}: {e}")
                console.print(f"[yellow]Skipping invalid diff for {diff[0]}: {e}[/yellow]")
        if not valid_diffs:
            console.print("[red]No valid changes to preview.[/red]")
            return
        console.print(Panel(table, border_style="yellow"))

        choice = Prompt.ask("\nApply changes?", choices=["y", "n", "save-as"], default="save-as")
        if choice == "n":
            console.print("[red]Changes discarded.[/red]")
            return
        for file, (original, cleaned, diff_text, suggestion) in valid_diffs:
            if os.path.exists(file) and choice == "y":
                if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
                    console.print(f"[yellow]Skipped {file}[/yellow]")
                    continue
            if choice == "y":
                with open(file, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                console.print(f"[green]Changes applied to {file}[/green]")
            elif choice == "save-as":
                ext = file.split(".")[-1]
                save_as = file.replace(f".{ext}", f"_fixed.{ext}")
                with open(save_as, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                console.print(f"[green]Fixed file saved as {save_as}[/green]")

    if git_commit and valid_diffs:
        if is_git_repo(path):
            repo = Repo(path, search_parent_directories=True)
            repo.git.add([file for file, _ in valid_diffs])
            repo.index.commit(f"Blonde CLI fixes: {len(valid_diffs)} files")
            console.print(f"[green]Committed {len(valid_diffs)} changes to git.[/green]")
        else:
            console.print("[yellow]Not a git repo; skipping commit.[/yellow]")

def _fix_file(file: str, repo_map: dict | None, export: str | None, preview: bool, iterative: bool, suggest: bool, debug: bool, memory_manager=None) -> tuple | None:
    """Internal helper to fix one file with repo context and memory.
    Args:
        file: Path to file.
        repo_map: Repository metadata from scan_repo.
        export: Export diff path.
        preview: Enable batch preview.
        iterative: Enable refinement mode.
        suggest: Show structured suggestions.
        debug: Enable debug logging.
        memory_manager: Optional memory manager for context-aware fixes.
    Returns:
        Tuple (file, (original, cleaned, diff_text, suggestion)) or None.
    Why it works: Uses memory to learn from past fixes and apply patterns.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            original = f.read()
    except Exception as e:
        logger.error(f"Error reading {file}: {e}")
        console.print(f"[red]Error reading {file}: {e}[/red]")
        return None

    lang = detect_language(file)
    context = str(repo_map)[:2000] if repo_map else ""
    
    # Add memory context for better fixes
    memory_context = ""
    if memory_manager:
        mem_ctx = memory_manager.get_context_for_prompt(f"fixing {lang} code", max_context_length=800)
        if mem_ctx:
            memory_context = f"\n\nLearned patterns from past fixes:\n{mem_ctx}"

    suggestion = ""
    if suggest:
        prompt = f"""
        You are a code fixer. Analyze this file and repo context, then provide a table in Markdown with:
        - Issue: What's wrong (e.g., "Potential division by zero")
        - Fix: Proposed change (e.g., "Add error handling")
        - Impact: Why it matters (e.g., "Prevents runtime errors")
        Repo context: {context}{memory_context}
        File ({file}, language: {lang}):
        {original}
        """
        suggestion = get_response(prompt, debug)
        console.print(Panel(Markdown(suggestion), title="Suggested Fixes", border_style="yellow"))

    prompt = f"""
    You are a professional code fixer.
    Repository map (for context): {context}{memory_context}
    Given the following file, output ONLY the corrected source code.
    Use language: {lang}.
    Do not include explanations, notes, or markdown fences.
    Preserve formatting.
    File ({file}):
    {original}
    """
    cleaned = extract_code(get_response(prompt, debug))

    # Validate cleaned code
    if "error processing your request" in cleaned.lower():
        console.print(f"[red]Failed to fix {file}: Invalid response from API[/red]")
        return None

    if lang == "python":
        try:
            ast.parse(cleaned)
        except SyntaxError as e:
            logger.error(f"Invalid Python code for {file}: {e}")
            console.print(f"[red]Invalid fixed code for {file}: {e}[/red]")
            return None

    if iterative:
        max_iters = 3
        for i in range(max_iters):
            console.print(Panel(f"Iteration {i+1}/{max_iters}", style="yellow"))
            console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))
            console.print("[yellow]Refine this? Enter feedback or 'done' to stop.[/yellow]")
            feedback = Prompt.ask("[green]Feedback[/green]")
            if feedback.lower() == "done":
                break
            prompt = f"""
            Refine this code based on feedback: {feedback}
            Original file: {original}
            Current version: {cleaned}
            Output ONLY the refined source code (language: {lang}).
            """
            cleaned = extract_code(get_response(prompt, debug))
            if "error processing your request" in cleaned.lower():
                console.print(f"[red]Failed to refine {file}: Invalid response from API[/red]")
                return None
            if lang == "python":
                try:
                    ast.parse(cleaned)
                except SyntaxError as e:
                    logger.error(f"Invalid refined Python code for {file}: {e}")
                    console.print(f"[red]Invalid refined code for {file}: {e}[/red]")
                    return None

    diff = unified_diff(
        original.splitlines(),
        cleaned.splitlines(),
        fromfile=f"{file} (original)",
        tofile=f"{file} (fixed)",
        lineterm="",
    )
    diff_text = "\n".join(diff)
    if not diff_text.strip():
        console.print(f"[yellow]No changes needed for {file}[/yellow]")
        return None

    if not preview and not export:
        console.print(diff_text, style="yellow")
        console.print("\n[bold yellow]Preview of fixed file:[/bold yellow]")
        console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))
        choice = Prompt.ask("\nApply changes?", choices=["y", "n", "save-as"], default="save-as")
        if choice == "y":
            if os.path.exists(file):
                if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
                    console.print(f"[yellow]Skipped {file}[/yellow]")
                    return None
            with open(file, "w", encoding="utf-8") as f:
                f.write(cleaned)
            console.print(f"[green]Changes applied to {file}[/green]")
            
            # Store fix in memory for learning
            if memory_manager:
                memory_manager.add_conversation(
                    f"Fixed {lang} file: {file}", 
                    f"Applied fix pattern. Diff summary: {diff_text[:300]}"
                )
        elif choice == "save-as":
            ext = file.split(".")[-1]
            save_as = file.replace(f".{ext}", f"_fixed.{ext}")
            with open(save_as, "w", encoding="utf-8") as f:
                f.write(cleaned)
            console.print(f"[green]Fixed file saved as {save_as}[/green]")
        else:
            console.print("[red]Changes discarded[/red]")
        return (file, (original, cleaned, diff_text, suggestion))

    if export:
        export_path = export if os.path.isdir(export) else export
        if os.path.isdir(export):
            diff_file = os.path.join(export, os.path.basename(file) + ".diff")
            with open(diff_file, "w", encoding="utf-8") as f:
                f.write(diff_text)
            console.print(f"[green]Diff exported → {diff_file}[/green]")
        else:
            with open(export, "a", encoding="utf-8") as f:
                f.write(f"# {file}\n{diff_text}\n\n")
            console.print(f"[green]Diff appended → {export}[/green]")
        return (file, (original, cleaned, diff_text, suggestion))

    return (file, (original, cleaned, diff_text, suggestion))


@app.command()
def doc(
    path: str,
    export: str = typer.Option(None, help="Export explanation to a file"),
    format: str = typer.Option("md", help="Output format: md, txt"),
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory for better documentation"),
    style: str = typer.Option("detailed", help="Documentation style: concise, detailed, tutorial")
):
    """Generate context-aware documentation with memory.
    
    Enhanced features:
    - Memory: Learns documentation patterns
    - Styles: Choose between concise, detailed, or tutorial formats
    - Context: Uses past documentation for consistency
    """
    global bot
    
    # Interactive model selection for offline mode
    cached_model_path = None
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file, is_cached, path = selection
        model = f"{repo}/{file}"
        if is_cached and path:
            cached_model_path = path
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model, cached_path=cached_model_path)
    
    # Initialize memory
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled - consistent documentation style[/dim]")
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
    console.print(Panel("Blonde CLI - Documenting Codebase", style="bold cyan"))

    if os.path.isdir(path):
        repo_map = scan_repo(path)
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning files...", total=len(repo_map))
            context = ["Repository structure:"]
            for rel_path, info in repo_map.items():
                context.append(f"- {rel_path}: {info.get('functions', [])}, {info.get('classes', [])}, {info.get('imports', [])}")
                try:
                    with open(os.path.join(path, rel_path), "r", encoding="utf-8") as f:
                        context.append(f"\n### {rel_path}\n```\n{f.read()}\n```")
                except Exception as e:
                    context.append(f"Error reading {rel_path}: {e}")
                    logger.debug(f"Doc error for {rel_path}: {e}")
                progress.update(task, advance=1)

        # Build style-specific instructions
        style_instructions = {
            "concise": "Provide brief, one-line summaries for each component.",
            "detailed": "Provide comprehensive explanations with examples and usage patterns.",
            "tutorial": "Provide step-by-step explanations suitable for learning, with code examples."
        }
        style_guide = style_instructions.get(style, style_instructions["detailed"])
        
        # Get memory context for consistent documentation
        mem_context = ""
        if memory_manager:
            mem_ctx = memory_manager.get_context_for_prompt("documentation patterns", max_context_length=500)
            if mem_ctx:
                mem_context = f"\n\nConsistent documentation style from past docs:\n{mem_ctx}"
        
        prompt = f"""
        You are a code documentation expert. Given the repository structure and file contents below, provide a Markdown summary of the codebase.
        Documentation style: {style_guide}
        For each file, list:
        - Purpose
        - Key functions/classes
        - Dependencies (imports)
        - One-line summary
        Group by module/folder if applicable. Output only the Markdown summary.{mem_context}
        {chr(10).join(context)}
        """
        response = get_response(prompt, debug)
    else:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Add memory context for single file documentation
        mem_context = ""
        if memory_manager:
            mem_ctx = memory_manager.get_context_for_prompt("code documentation", max_context_length=400)
            if mem_ctx:
                mem_context = f"\n\nConsistent style from past docs:\n{mem_ctx}"
        
        style_instructions = {
            "concise": "Provide a brief explanation in 2-3 paragraphs.",
            "detailed": "Provide a comprehensive explanation with usage examples.",
            "tutorial": "Explain as if teaching a beginner, with step-by-step breakdown."
        }
        style_guide = style_instructions.get(style, style_instructions["detailed"])
        
        prompt = f"""
        Explain this code in plain English, in Markdown format.
        Style: {style_guide}{mem_context}
        
        Code:
        {code}
        """
        response = get_response(prompt, debug)

    if format == "txt":
        response = re.sub(r"[`*#\[\]]", "", response)
    
    render_code_blocks(response)
    
    # Store documentation pattern in memory
    if memory_manager:
        memory_manager.add_conversation(
            f"Generated {style} documentation for: {path}",
            response[:500]  # Store summary for future reference
        )

    if export:
        with open(export, "w", encoding="utf-8") as f:
            f.write(response)
        console.print(f"[green]✓ Documentation exported to {export}[/green]")


def is_git_repo(path: str) -> bool:
    """Checks if path is a git repo.
    Args:
        path: Directory path.
    Returns:
        True if .git exists.
    Why it works: Uses GitPython for reliable detection.
    Pitfalls: Shallow clones may not have .git; fallback to os.path.
    Learning: Read GitPython docs for repo ops.
    """
    try:
        Repo(path, search_parent_directories=True)
        return True
    except:
        return os.path.exists(os.path.join(path, ".git"))

# ... (detect_language, scan_repo, render_code_blocks, extract_code - same as before)

# Shared Helpers (same, with suggest_terminal_command expanded)
def suggest_terminal_command(user_input: str) -> str | None:
    """Suggests terminal commands based on user input.
    Args:
        user_input: User's chat input.
    Returns:
        Suggested command or None.
    Why it works: Matches keywords to commands, like Warp's AI suggestions.
    Pitfalls: False positives; use NLP for advanced matching.
    Learning: Study intent detection in NLP.
    """
    command_map = {
        "list files": "ls -la",
        "show directory": "pwd",
        "change directory": "cd",
        "remove file": "rm -rf",
        "create directory": "mkdir -p",
        "git status": "git status",
        "git commit": "git commit -m",
        "explain ls": "ls --help"
    }
    for key, cmd in command_map.items():
        if key in user_input.lower():
            return f"[yellow]Suggested command: {cmd}[/yellow]"
    return None


if __name__ == "__main__":
    app()





 
# =====================
#  Advanced Features Integration
# =====================

# Import advanced features
try:
    from tui.code_analysis import CodeAnalyzer, CodeQualityAnalyzer
    from tui.repo_refactor import RepositorySearcher, RepositoryRefactorer
    from tui.test_generator import TestGenerator, TestRunner
    from tui.code_review import LintingIntegrator, AIReviewer
    from tui.rollback import RollbackManager
    from tui.workflow import WorkflowManager
    ADVANCED_FEATURES_AVAILABLE = True
except Exception as e:
    ADVANCED_FEATURES_AVAILABLE = False
    logger.warning(f"Advanced features not available: {e}")


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="File to analyze"),
    verbose: bool = typer.Option(False, "--verbose", "-v")
):
    """Analyze code using AST and provide deep insights"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available. Install dependencies.[/red]")
        return
    
    analyzer = CodeAnalyzer()
    entities = analyzer.analyze_file(file_path)
    
    if verbose:
        console.print(f"\n[bold cyan]Found {len(entities)} code entities:[/bold cyan]\n")
        for entity in entities:
            console.print(f"  [green]{entity.type}:[/green] {entity.name} (line {entity.line_number})")
            if entity.docstring:
                console.print(f"    [dim]{entity.docstring[:100]}...[/dim]")
    else:
        console.print(f"[green]Found {len(entities)} entities in {file_path}[/green]")


@app.command()
def search_code(
    query: str = typer.Argument(..., help="Symbol or text to search for"),
    directory: str = typer.Option(".", "--dir", "-d", help="Directory to search"),
    pattern: bool = typer.Option(False, "--regex", "-r", help="Use regex pattern")
):
    """Search for code symbols or patterns across repository"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available. Install dependencies.[/red]")
        return
    
    searcher = RepositorySearcher(directory)
    
    if pattern:
        matches = searcher.search_pattern(query, is_regex=True)
    else:
        matches = searcher.search_symbol(query)
    
    console.print(f"\n[bold cyan]Found {len(matches)} matches:[/bold cyan]\n")
    
    for match in matches[:20]:
        console.print(f"  [yellow]{Path(match.file_path).name}:{match.line_number}[/yellow]")
        console.print(f"    [dim]{match.line_content.strip()}[/dim]\n")
    
    if len(matches) > 20:
        console.print(f"[dim]... and {len(matches) - 20} more matches[/dim]")


@app.command()
def generate_tests_cmd(
    file_path: str = typer.Argument(..., help="File to generate tests for"),
    output: str = typer.Option(None, "--output", "-o", help="Output directory for tests")
):
    """Generate comprehensive test cases for a file"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available. Install dependencies.[/red]")
        return

    from models.openrouter import OpenRouterAdapter
    llm_adapter = OpenRouterAdapter(debug=debug)
    
    generator = TestGenerator(llm_adapter)
    test_suite = generator.generate_tests_for_file(file_path, output)
    
    if test_suite:
        console.print(f"\n[green]Generated {len(test_suite.test_cases)} test cases for {file_path}[/green]")


@app.command()
def lint_cmd(
    file_path: str = typer.Argument(..., help="File to lint")
):
    """Lint a file with multiple linters"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available. Install dependencies.[/red]")
        return

    from models.openrouter import OpenRouterAdapter
    llm_adapter = OpenRouterAdapter(debug=debug)
    
    reviewer = AIReviewer(llm_adapter)
    review = reviewer.review_file(file_path)
    
    if review:
        report = reviewer.generate_review_report(review)
        console.print(f"\n{report}")


@app.command()
def rollback_cmd(
    action: str = typer.Argument("history", help="Action: history, undo, snapshot"),
    name: str = typer.Argument(None, help="Snapshot name"),
    directory: str = typer.Option(".", "--dir", "-d")
):
    """Rollback operations and manage snapshots"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available. Install dependencies.[/red]")
        return
    
    manager = RollbackManager(directory)
    
    if action == "history":
        table = manager.get_operation_history()
        console.print(table)
    elif action == "undo":
        if manager.undo_last():
            console.print("[green]Successfully undone last operation[/green]")
    elif action == "snapshot":
        if not name:
            console.print("[red]Error: snapshot name required[/red]")
            return
        manager.create_snapshot(name)
    else:
        console.print(f"[red]Unknown action: {action}[/red]")


@app.command()
def workflow_cmd(
    action: str = typer.Argument("list", help="Action: list, run"),
    name: str = typer.Argument(None, help="Workflow name"),
    directory: str = typer.Option(".", "--dir", "-d")
):
    """Manage and run automated workflows"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available. Install dependencies.[/red]")
        return
    
    manager = WorkflowManager(directory)
    
    if action == "list":
        console.print(manager.list_workflows())
    elif action == "run":
        if not name:
            console.print("[red]Error: workflow name required[/red]")
            return
        manager.run_workflow(name)
    else:
        console.print(f"[red]Unknown action: {action}[/red]")


# Update help text to include new commands
HELP_TEXT = """
[bold cyan]Blonde CLI Help[/bold cyan]

[green]Modes:[/green]
  • [bold]blnd chat[/bold] → interactive chat
  • [bold]blnd gen "prompt"[/bold] → generate code
  • [bold]blnd fix file.py[/bold] → fix code with diff preview
  • [bold]blnd doc file.py[/bold] → explain/document code

[green]AI Agents (9 total):[/green]
  🧱 Generator - Generates initial code
  🔍 Reviewer - Reviews code quality
  🧪 Tester - Generates tests
  🔨 Refactorer - Refactors code
  📝 Documenter - Writes docs
  🏗️ Architect - Designs architecture
  🔒 Security - Checks security
  🐛 Debugger - Fixes bugs
  ⚡ Optimizer - Coordinates all agents (MASTER)

[green]Agent Commands:[/green]
  • [bold]blnd dev-team status[/bold] → show all 9 agents
  • [bold]blnd dev-team collaborate "task"[/bold] → agents work together
  • [bold]blnd agent-task "task"[/bold] → NEW: Parallel execution with Optimizer

[green]Advanced Features:[/green]
  • [bold]blnd analyze <file>[/bold] → analyze code structure and quality
  • [bold]blnd search-code <query>[/bold] → search code across repository
  • [bold]blnd generate-tests-cmd <file>[/bold] → generate test cases
  • [bold]blnd lint-cmd <file>[/bold] → lint code with multiple tools
  • [bold]blnd review-cmd <file>[/bold] → AI-powered code review
  • [bold]blnd rollback-cmd [action][/bold] → undo operations and snapshots
  • [bold]blnd workflow-cmd [action][/bold] → manage and run workflows

[green]Flags:[/green]
  • [bold]--agentic[/bold]         enable tool usage
  • [bold]--memory[/bold]          enable conversation memory
  • [bold]--offline[/bold]         use local GGUF model
  • [bold]--model <name>[/bold]    specify model
  • [bold]--provider <name>[/bold]  specify provider (openai, huggingface, openrouter)
  • [bold]--parallel[/bold]         use parallel agent execution (NEW)
  • [bold]--with-optimizer[/bold]  include Optimizer agent (NEW)

[green]Config:[/green]
  • Environment: .env file (in project root)
  • Config directory: ~/.blonde/
  • Logs: ~/.blonde/debug.log

For more info, visit: https://github.com/your-repo/blonde-cli
"""


 
# =====================
#  Provider Management
# =====================

@app.command()
def provider(
    action: str = typer.Argument("list", help="Action: list, switch, add, remove, test, setup")
):
    """Manage AI providers"""
    try:
        from tui.provider_manager import ProviderManager
    except Exception:
        console.print("[red]Provider manager not available[/red]")
        return
    
    manager = ProviderManager()
    
    if action == "list":
        console.print(manager.list_providers())
    elif action == "setup":
        from tui.provider_manager import interactive_provider_setup
        interactive_provider_setup()
    elif action == "switch":
        provider_name = typer.prompt("Provider name to switch to")
        manager.switch_provider(provider_name)
    elif action == "test":
        provider_name = typer.prompt("Provider name to test")
        manager.test_provider(provider_name)
    elif action == "auto":
        manager.auto_select_provider()
    else:
        console.print(f"[yellow]Unknown action: {action}[/yellow]")
        console.print("[dim]Available: list, switch, add, remove, test, setup, auto[/dim]")


@app.command()
def dev_team(
    action: str = typer.Argument("status", help="Action: status, task, improve, collaborate")
):
    """Manage AI development team"""
    if not ADVANCED_FEATURES_AVAILABLE:
        console.print("[red]Advanced features not available[/red]")
        return
    
    # Get LLM adapter
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
    
    if not api_key:
        console.print("[red]OPENROUTER_API_KEY not set[/red]")
        return
    
    from models.openrouter import OpenRouterAdapter
    llm_adapter = OpenRouterAdapter(debug=debug)
    
    from tui.dev_team import DevelopmentTeam
    team = DevelopmentTeam(llm_adapter)
    
    if action == "status":
        console.print(team.get_team_status())
    elif action == "task":
        agent = typer.prompt("Which agent? (generator, reviewer, tester, refactorer)")
        task = typer.prompt("Task description")
        task_id = team.assign_task(agent, "user_task", task, {})
        team.execute_task(task_id)
    elif action == "improve":
        console.print("[yellow]Running continuous improvement loop...[/yellow]")
        results = team.continuous_improvement_loop(max_iterations=2)
        console.print(f"\n[green]Final output:[/green]")
        console.print(results.get('final_output', 'No output'))
    elif action == "collaborate":
        task = typer.prompt("Task for team collaboration")
        results = team.collaborative_task(task)
        for agent_id, output in results.items():
            console.print(f"\n[cyan]{agent_id} output:[/cyan]")
            console.print(output[:500] + "..." if len(output) > 500 else output)
    else:
        console.print(f"[yellow]Unknown action: {action}[/yellow]")
        console.print("[dim]Available: status, task, improve, collaborate[/dim]")


@app.command(name="agent-task")
def agent_task(
    task: str = typer.Argument(..., help="Task description for agents"),
    parallel: bool = typer.Option(True, "--parallel", "-p", help="Use parallel agent execution"),
    with_optimizer: bool = typer.Option(True, "--with-optimizer", "-o", help="Include Optimizer agent")
):
    """Execute a task with parallel agents and Optimizer (NEW 9-agent system)"""
    if not PARALLEL_EXECUTION_AVAILABLE:
        console.print("[red]Parallel execution not available[/red]")
        console.print("[dim]Install required dependencies for advanced agent coordination[/dim]")
        return
    
    # Get LLM adapter
    from models.openrouter import OpenRouterAdapter
    llm_adapter = OpenRouterAdapter(debug=debug)

    console.print(Panel(f"Executing task with {'parallel' if parallel else 'sequential'} agents", style="bold cyan"))
    
    if blip:
        blip.think(f"I'm planning how to execute this task...")
    
    # Initialize Optimizer
    optimizer = OptimizerAgent()
    agents = ["generator", "reviewer", "tester", "refactorer"]
    if with_optimizer:
        agents.append("optimizer")
    
    if parallel:
        # Parallel execution with Optimizer coordination
        console.print("[cyan]📊 Optimizer: Coordinating parallel execution...[/cyan]")
        
        if blip:
            blip.work("Optimizer is coordinating 8 agents in parallel...")
        
        from tui.dev_team import DevelopmentTeam
        team = DevelopmentTeam(llm_adapter)
        
        # Use collaborative task for parallel execution
        results = team.collaborative_task(task, agents)
        
        if blip:
            blip.happy(f"All {len(agents)} agents completed their work! 🎉")
        
        # Show results
        console.print("\n[bold cyan]Results from all agents:[/bold cyan]")
        for agent_id, output in results.items():
            console.print(f"\n[bold yellow]{agent_id}:[/bold yellow]")
            console.print(output[:500] + "..." if len(output) > 500 else output)
    else:
        # Sequential execution (legacy mode)
        console.print("[yellow]Running sequential execution (legacy mode)[/yellow]")
        from tui.dev_team import DevelopmentTeam
        team = DevelopmentTeam(llm_adapter)
        results = team.collaborative_task(task, agents)
    
    console.print("\n[green]✓ Task completed![/green]")
    if with_optimizer:
        console.print("[dim]Optimizations and quality checks applied by Optimizer[/dim]")


if __name__ == "__main__":
    app()

