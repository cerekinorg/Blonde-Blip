"""
Blonde CLI - Session Manager
Simple, clean session management
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


class Session:
    """Session data structure"""

    def __init__(
        self,
        session_id: str = None,
        name: str = None,
        provider: str = "openrouter",
        model: str = "openai/gpt-4"
    ):
        self.session_id = session_id or self._generate_id()
        self.name = name or f"Session {self.session_id[:8]}"
        self.created_at = datetime.now().isoformat()
        self.provider = provider
        self.model = model
        self.chat_history: List[Dict[str, str]] = []
        self.files_edited: List[str] = []
        self.context_usage = {"total_tokens": 0, "percentage": 0.0}
        self.cost = {"total_usd": 0.0}
        self.metadata = {"version": "2.0", "archived": False}

    @staticmethod
    def _generate_id() -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4()).replace('-', '')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'name': self.name,
            'created_at': self.created_at,
            'provider': self.provider,
            'model': self.model,
            'chat_history': self.chat_history,
            'files_edited': self.files_edited,
            'context_usage': self.context_usage,
            'cost': self.cost,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create from dictionary"""
        session = cls(
            session_id=data.get('session_id'),
            name=data.get('name'),
            provider=data.get('provider'),
            model=data.get('model')
        )
        session.created_at = data.get('created_at')
        session.chat_history = data.get('chat_history', [])
        session.files_edited = data.get('files_edited', [])
        session.context_usage = data.get('context_usage', {})
        session.cost = data.get('cost', {})
        session.metadata = data.get('metadata', {})
        return session


class SessionManager:
    """Simple session manager"""

    def __init__(self, sessions_dir: Path = None):
        self.sessions_dir = sessions_dir or Path.home() / ".blonde" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._current_session: Optional[Session] = None
        self._sessions_cache: Dict[str, Session] = {}

    def create_session(self, provider: str = "openrouter", model: str = "openai/gpt-4") -> Session:
        """Create new session"""
        session = Session(provider=provider, model=model)
        self._current_session = session
        self._sessions_cache[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        if session_id in self._sessions_cache:
            return self._sessions_cache[session_id]

        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
            session = Session.from_dict(data)
            self._sessions_cache[session_id] = session
            return session
        return None

    def save_session(self, session: Session) -> None:
        """Save session to disk"""
        session_file = self.sessions_dir / f"{session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
        self._sessions_cache[session.session_id] = session

    def list_sessions(self) -> List[Session]:
        """List all sessions"""
        sessions = []
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                sessions.append(Session.from_dict(data))
            except Exception:
                continue
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)

    def archive_session(self, session_id: str) -> bool:
        """Archive old session"""
        archive_dir = self.sessions_dir / "archived"
        archive_dir.mkdir(exist_ok=True)

        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.rename(archive_dir / f"{session_id}.json")
            return True
        return False

    def add_message(self, role: str, content: str) -> None:
        """Add message to current session"""
        if self._current_session:
            self._current_session.chat_history.append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            self.save_session(self._current_session)

    def add_file_edited(self, file_path: str) -> None:
        """Add file to edited list"""
        if self._current_session:
            if file_path not in self._current_session.files_edited:
                self._current_session.files_edited.append(file_path)
            self.save_session(self._current_session)

    def update_context_usage(self, tokens: int, percentage: float) -> None:
        """Update context usage"""
        if self._current_session:
            self._current_session.context_usage['total_tokens'] += tokens
            self._current_session.context_usage['percentage'] = percentage
            self.save_session(self._current_session)

    def update_cost(self, cost_usd: float) -> None:
        """Update session cost"""
        if self._current_session:
            self._current_session.cost['total_usd'] += cost_usd
            self.save_session(self._current_session)


# Global instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
