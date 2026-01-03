"""
Session Manager - Manage Blonde CLI sessions
Handles session creation, switching, persistence, and archiving
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import shutil
from rich.console import Console

console = Console()


class SessionManager:
    """Manages Blonde CLI sessions with persistence and archiving"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path.home() / ".blonde" / "config.json")
        self.sessions_dir = Path.home() / ".blonde" / "sessions"
        self.archive_dir = Path.home() / ".blonde" / "sessions_archive"
        
        self.current_session_id: Optional[str] = None
        self.current_session_data: Dict = {}
        
        self._ensure_directories()
        self._load_or_create_session()
    
    def _ensure_directories(self):
        """Ensure session directories exist"""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_or_create_session(self):
        """Load existing session or create new one"""
        if self.current_session_id:
            self.load_session(self.current_session_id)
        else:
            self.create_session()
    
    def generate_session_name(self, first_prompt: str = "") -> str:
        """
        Generate session name from first prompt or timestamp
        
        Args:
            first_prompt: Optional first prompt to create name from
        
        Returns:
            Generated session name
        """
        if first_prompt:
            # Extract first line/summary (max 30 chars)
            summary = first_prompt.split('\n')[0].strip()
            if len(summary) > 30:
                summary = summary[:27] + "..."
            return f"Session - {summary}"
        else:
            # Timestamp fallback
            return f"Session {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    
    def create_session(self, name: str = "", provider: str = "", model: str = "", 
                     blip_character: str = "axolotl") -> str:
        """
        Create a new session
        
        Args:
            name: Optional session name
            provider: AI provider
            model: AI model
            blip_character: Blip character to use
        
        Returns:
            Session ID
        """
        session_id = self.generate_session_id()
        session_name = name or self.generate_session_name()
        
        # Load config for defaults
        provider, model, blip_character = self._get_defaults_from_config(
            provider, model, blip_character
        )
        
        # Create session data
        session_data = {
            "session_id": session_id,
            "name": session_name,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "blip_character": blip_character,
            "chat_history": [],
            "context_usage": {
                "total_tokens": 0,
                "context_window": self._get_context_window(model),
                "percentage": 0.0
            },
            "cost": {
                "total_usd": 0.0,
                "by_provider": {}
            },
            "files_edited": [],
            "metadata": {
                "version": "1.0.0",
                "archived": False
            }
        }
        
        # Save session
        session_path = self.sessions_dir / f"{session_id}.json"
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Set as current
        self.current_session_id = session_id
        self.current_session_data = session_data
        
        console.print(f"[green]✓ Created new session:[/green] {session_name}")
        console.print(f"[dim]Session ID: {session_id}[/dim]")
        
        return session_id
    
    def _get_defaults_from_config(self, provider: str, model: str, 
                                  blip_character: str) -> tuple:
        """Get defaults from config if not provided"""
        if not provider or not model:
            if self.config_path.exists():
                try:
                    with open(self.config_path, 'r') as f:
                        config = json.load(f)
                    if not provider:
                        provider = config.get('default_provider', 'openrouter')
                    if not model:
                        providers_config = config.get('providers', {})
                        provider_data = providers_config.get(provider, {})
                        model = provider_data.get('model', 'openai/gpt-4')
                except Exception:
                    pass
        
        if not provider:
            provider = "openrouter"
        if not model:
            model = "openai/gpt-4"
        if not blip_character:
            blip_character = "axolotl"
        
        return provider, model, blip_character
    
    def _get_context_window(self, model: str) -> int:
        """Get context window size for model"""
        context_windows = {
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 4096,
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "mistral-large": 32000
        }
        
        for model_name, window in context_windows.items():
            if model_name.lower() in model.lower():
                return window
        
        return 128000  # Default
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a session
        
        Args:
            session_id: Session ID to load
        
        Returns:
            True if successful
        """
        session_path = self.sessions_dir / f"{session_id}.json"
        
        if not session_path.exists():
            console.print(f"[red]Session not found: {session_id}[/red]")
            return False
        
        try:
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            self.current_session_id = session_id
            self.current_session_data = session_data
            
            console.print(f"[green]✓ Loaded session:[/green] {session_data['name']}")
            return True
        except Exception as e:
            console.print(f"[red]Failed to load session: {e}[/red]")
            return False
    
    def switch_session(self, session_id: str) -> bool:
        """
        Switch to a different session
        
        Args:
            session_id: Session ID to switch to
        
        Returns:
            True if successful
        """
        # Save current session first
        if self.current_session_id:
            self.save_session()
        
        # Load new session
        return self.load_session(session_id)
    
    def save_session(self):
        """Save current session"""
        if not self.current_session_id:
            return
        
        # Update last modified
        self.current_session_data["last_modified"] = datetime.now().isoformat()
        
        # Save to file
        session_path = self.sessions_dir / f"{self.current_session_id}.json"
        try:
            with open(session_path, 'w') as f:
                json.dump(self.current_session_data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Failed to save session: {e}[/red]")
    
    def list_sessions(self, include_archived: bool = False) -> List[Dict]:
        """
        List all sessions
        
        Args:
            include_archived: Whether to include archived sessions
        
        Returns:
            List of session info dicts
        """
        sessions = []
        
        # Load active sessions
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    "id": session_data["session_id"],
                    "name": session_data["name"],
                    "created_at": session_data["created_at"],
                    "last_modified": session_data["last_modified"],
                    "provider": session_data["provider"],
                    "model": session_data["model"],
                    "messages": len(session_data.get("chat_history", [])),
                    "archived": False
                })
            except Exception:
                pass
        
        # Load archived sessions if requested
        if include_archived:
            for session_file in self.archive_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    sessions.append({
                        "id": session_data["session_id"],
                        "name": session_data["name"],
                        "created_at": session_data["created_at"],
                        "last_modified": session_data["last_modified"],
                        "provider": session_data["provider"],
                        "model": session_data["model"],
                        "messages": len(session_data.get("chat_history", [])),
                        "archived": True
                    })
                except Exception:
                    pass
        
        # Sort by last modified (newest first)
        sessions.sort(key=lambda x: x["last_modified"], reverse=True)
        
        return sessions
    
    def delete_session(self, session_id: str, archive: bool = True) -> bool:
        """
        Delete or archive a session
        
        Args:
            session_id: Session ID to delete
            archive: If True, move to archive instead of delete
        
        Returns:
            True if successful
        """
        session_path = self.sessions_dir / f"{session_id}.json"
        
        if not session_path.exists():
            console.print(f"[red]Session not found: {session_id}[/red]")
            return False
        
        if archive:
            # Move to archive
            archive_path = self.archive_dir / f"{session_id}.json"
            try:
                shutil.move(str(session_path), str(archive_path))
                
                # Mark as archived in data
                with open(archive_path, 'r') as f:
                    data = json.load(f)
                data["metadata"]["archived"] = True
                with open(archive_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                console.print(f"[yellow]📦 Archived session:[/yellow] {session_id}")
                return True
            except Exception as e:
                console.print(f"[red]Failed to archive session: {e}[/red]")
                return False
        else:
            # Permanently delete
            try:
                session_path.unlink()
                console.print(f"[red]🗑️ Deleted session:[/red] {session_id}")
                return True
            except Exception as e:
                console.print(f"[red]Failed to delete session: {e}[/red]")
                return False
    
    def archive_old_sessions(self, days: int = 50, max_sessions: int = 50):
        """
        Archive old sessions
        
        Args:
            days: Age in days to trigger archiving
            max_sessions: Maximum active sessions before archiving oldest
        """
        sessions = self.list_sessions(include_archived=False)
        
        if len(sessions) <= max_sessions:
            return
        
        # Archive sessions older than days
        cutoff_date = datetime.now() - timedelta(days=days)
        archived_count = 0
        
        for session in sessions:
            last_modified = datetime.fromisoformat(session["last_modified"])
            
            if last_modified < cutoff_date:
                self.delete_session(session["id"], archive=True)
                archived_count += 1
        
        if archived_count > 0:
            console.print(f"[yellow]📦 Archived {archived_count} old sessions[/yellow]")
    
    def update_chat_history(self, role: str, content: str):
        """
        Update chat history with a new message
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        if "chat_history" not in self.current_session_data:
            self.current_session_data["chat_history"] = []
        
        self.current_session_data["chat_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        self.save_session()
    
    def update_context_usage(self, input_tokens: int, output_tokens: int):
        """
        Update context usage statistics
        
        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens used
        """
        if "context_usage" not in self.current_session_data:
            self.current_session_data["context_usage"] = {
                "total_tokens": 0,
                "context_window": self._get_context_window(
                    self.current_session_data.get("model", "")
                ),
                "percentage": 0.0
            }
        
        usage = self.current_session_data["context_usage"]
        usage["total_tokens"] += (input_tokens + output_tokens)
        usage["percentage"] = min(
            100.0,
            (usage["total_tokens"] / usage["context_window"]) * 100
        )
        
        self.save_session()
    
    def update_cost(self, provider: str, model: str, input_tokens: int, 
                   output_tokens: int, cost_usd: float):
        """
        Update cost tracking
        
        Args:
            provider: AI provider used
            model: Model used
            input_tokens: Input tokens
            output_tokens: Output tokens
            cost_usd: Cost in USD
        """
        if "cost" not in self.current_session_data:
            self.current_session_data["cost"] = {
                "total_usd": 0.0,
                "by_provider": {}
            }
        
        cost_data = self.current_session_data["cost"]
        cost_data["total_usd"] += cost_usd
        
        if provider not in cost_data["by_provider"]:
            cost_data["by_provider"][provider] = {
                "total_usd": 0.0,
                "models": {}
            }
        
        provider_cost = cost_data["by_provider"][provider]
        provider_cost["total_usd"] += cost_usd
        
        if model not in provider_cost["models"]:
            provider_cost["models"][model] = {
                "total_usd": 0.0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        
        model_cost = provider_cost["models"][model]
        model_cost["total_usd"] += cost_usd
        model_cost["input_tokens"] += input_tokens
        model_cost["output_tokens"] += output_tokens
        
        self.save_session()
    
    def add_file_edit(self, file_path: str, changes: str = ""):
        """
        Record a file edit
        
        Args:
            file_path: Path to edited file
            changes: Summary of changes
        """
        if "files_edited" not in self.current_session_data:
            self.current_session_data["files_edited"] = []
        
        self.current_session_data["files_edited"].append({
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "changes": changes
        })
        
        self.save_session()


# Global session manager instance
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    return session_manager


if __name__ == "__main__":
    # Demo Session Manager
    manager = SessionManager()
    
    print("=== Session Manager Demo ===\n")
    
    # Create a session
    session_id = manager.create_session(name="Demo Session")
    
    # Update chat history
    manager.update_chat_history("user", "Hello, how are you?")
    manager.update_chat_history("assistant", "I'm doing well, thank you!")
    
    # Update usage
    manager.update_context_usage(100, 50)
    
    # Update cost
    manager.update_cost("openrouter", "openai/gpt-4", 100, 50, 0.01)
    
    # List sessions
    print("\nSessions:")
    for session in manager.list_sessions():
        print(f"  - {session['name']}: {session['messages']} messages")
    
    # Archive old sessions
    manager.archive_old_sessions(days=1, max_sessions=1)
