"""
Context Tracker - Track token usage and context window size
Provides warnings at thresholds (80%, 90%, 95%)
"""

from typing import Optional, Dict
from pathlib import Path
import json
from rich.console import Console

console = Console()


class ContextTracker:
    """Tracks context usage and provides warnings"""
    
    # Context window sizes for different models
    CONTEXT_WINDOWS = {
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-preview": 128000,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
        "claude-2.1": 100000,
        "claude-2.0": 100000,
        "claude-instant-1.2": 100000,
        "mistral-large": 32000,
        "mistral-medium": 32000,
        "mistral-small": 32000,
        "gemini-pro": 28000,
        "llama-2-7b": 4096,
        "llama-2-13b": 4096,
        "llama-2-70b": 4096,
        "llama-3-8b": 8192,
        "llama-3-70b": 8192,
        "default": 128000  # Fallback
    }
    
    # Warning thresholds
    WARNING_YELLOW = 80.0  # Show yellow warning
    WARNING_ORANGE = 90.0  # Show orange warning
    WARNING_CRITICAL = 95.0  # Show red critical
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path.home() / ".blonde" / "context.json")
        
        # Context tracking data
        self.context_data: Dict[str, Dict] = {}
        
        self._load_context_data()
    
    def _load_context_data(self):
        """Load context tracking data from disk"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.context_data = json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load context data: {e}[/yellow]")
    
    def _save_context_data(self):
        """Save context tracking data to disk"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.context_data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving context data: {e}[/red]")
    
    def get_context_window(self, model: str) -> int:
        """
        Get context window size for a model
        
        Args:
            model: Model name
        
        Returns:
            Context window size in tokens
        """
        # Try exact match first
        model_lower = model.lower()
        
        for model_name, window_size in self.CONTEXT_WINDOWS.items():
            if model_name.lower() in model_lower:
                return window_size
        
        # Try partial match
        for model_name, window_size in self.CONTEXT_WINDOWS.items():
            if model_name.lower() in model_lower or model_lower in model_name.lower():
                return window_size
        
        # Fallback to default
        console.print(f"[yellow]Warning: Unknown model '{model}', using default window size[/yellow]")
        return self.CONTEXT_WINDOWS["default"]
    
    def track_usage(self, session_id: str, provider: str, model: str,
                   input_tokens: int, output_tokens: int) -> Dict:
        """
        Track context usage for a session
        
        Args:
            session_id: Session identifier
            provider: AI provider
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
        
        Returns:
            Updated context data
        """
        # Initialize session data if not exists
        if session_id not in self.context_data:
            self.context_data[session_id] = {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "model": model,
                "provider": provider,
                "warnings": []
            }
        
        session = self.context_data[session_id]
        
        # Update token counts
        session["input_tokens"] += input_tokens
        session["output_tokens"] += output_tokens
        session["total_tokens"] += (input_tokens + output_tokens)
        session["model"] = model
        session["provider"] = provider
        
        # Calculate percentage
        context_window = self.get_context_window(model)
        session["context_window"] = context_window
        session["percentage"] = min(100.0, (session["total_tokens"] / context_window) * 100)
        
        # Check for warnings
        self._check_warnings(session_id)
        
        # Save
        self._save_context_data()
        
        return session
    
    def _check_warnings(self, session_id: str):
        """
        Check for context warnings and add to session
        
        Args:
            session_id: Session to check
        """
        session = self.context_data.get(session_id, {})
        if not session:
            return
        
        percentage = session.get("percentage", 0.0)
        warnings = session.get("warnings", [])
        
        # Clear old warnings for this session
        warnings.clear()
        
        # Check thresholds
        if percentage >= self.WARNING_CRITICAL:
            warnings.append({
                "level": "critical",
                "threshold": self.WARNING_CRITICAL,
                "message": f"Context usage at {percentage:.1f}% - Approaching limit!"
            })
            console.print(f"[red]⚠ CRITICAL: Session {session_id[:8]}... at {percentage:.1f}% context usage[/red]")
        
        elif percentage >= self.WARNING_ORANGE:
            warnings.append({
                "level": "orange",
                "threshold": self.WARNING_ORANGE,
                "message": f"Context usage at {percentage:.1f}% - High usage"
            })
        
        elif percentage >= self.WARNING_YELLOW:
            warnings.append({
                "level": "yellow",
                "threshold": self.WARNING_YELLOW,
                "message": f"Context usage at {percentage:.1f}% - Moderate usage"
            })
        
        session["warnings"] = warnings
    
    def get_session_context(self, session_id: str) -> Optional[Dict]:
        """
        Get context data for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session context data or None
        """
        return self.context_data.get(session_id)
    
    def get_all_sessions_context(self) -> Dict[str, Dict]:
        """
        Get context data for all sessions
        
        Returns:
            Dict of session_id to context data
        """
        return self.context_data.copy()
    
    def get_warning_status(self, session_id: str) -> Dict:
        """
        Get warning status for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Warning status dict
        """
        session = self.context_data.get(session_id, {})
        if not session:
            return {
                "has_warning": False,
                "level": "none",
                "message": ""
            }
        
        warnings = session.get("warnings", [])
        
        if not warnings:
            return {
                "has_warning": False,
                "level": "none",
                "message": "OK"
            }
        
        # Get highest warning level
        warning_levels = ["critical", "orange", "yellow"]
        current_level = "none"
        
        for warning in warnings:
            level = warning.get("level", "")
            level_index = warning_levels.index(level) if level in warning_levels else -1
            current_index = warning_levels.index(current_level) if current_level in warning_levels else -1
            
            if level_index > current_index:
                current_level = level
        
        return {
            "has_warning": True,
            "level": current_level,
            "message": warnings[-1].get("message", "") if warnings else ""
        }
    
    def get_color_for_status(self, status: str) -> str:
        """
        Get color code for warning status
        
        Args:
            status: Warning status (none, yellow, orange, critical)
        
        Returns:
            Color code string
        """
        colors = {
            "none": "bright_green",
            "yellow": "yellow",
            "orange": "orange",
            "critical": "bright_red"
        }
        
        return colors.get(status, "white")
    
    def clear_session_context(self, session_id: str):
        """
        Clear context data for a session
        
        Args:
            session_id: Session to clear
        """
        if session_id in self.context_data:
            del self.context_data[session_id]
            self._save_context_data()
    
    def reset_session_context(self, session_id: str):
        """
        Reset context data for a session (clear usage but keep model)
        
        Args:
            session_id: Session to reset
        """
        if session_id not in self.context_data:
            return
        
        session = self.context_data[session_id]
        model = session.get("model", "")
        provider = session.get("provider", "")
        
        # Reset to zero but keep model/provider
        self.context_data[session_id] = {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "model": model,
            "provider": provider,
            "warnings": []
        }
        
        self._save_context_data()
    
    def get_total_usage_across_sessions(self) -> Dict:
        """
        Get total usage across all sessions
        
        Returns:
            Total usage statistics
        """
        total_tokens = 0
        total_input = 0
        total_output = 0
        session_count = len(self.context_data)
        
        for session_id, session in self.context_data.items():
            total_tokens += session.get("total_tokens", 0)
            total_input += session.get("input_tokens", 0)
            total_output += session.get("output_tokens", 0)
        
        return {
            "total_tokens": total_tokens,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "session_count": session_count,
            "average_tokens_per_session": total_tokens / session_count if session_count > 0 else 0
        }
    
    def estimate_remaining_capacity(self, session_id: str, estimated_tokens: int) -> Dict:
        """
        Estimate remaining capacity for a session
        
        Args:
            session_id: Session identifier
            estimated_tokens: Estimated tokens for next prompt
        
        Returns:
            Capacity estimate
        """
        session = self.context_data.get(session_id)
        if not session:
            return {
                "remaining_tokens": 0,
                "remaining_percentage": 0.0,
                "can_fit": False
            }
        
        current_total = session.get("total_tokens", 0)
        context_window = session.get("context_window", self.CONTEXT_WINDOWS["default"])
        
        new_total = current_total + estimated_tokens
        new_percentage = min(100.0, (new_total / context_window) * 100)
        
        remaining_tokens = max(0, context_window - new_total)
        remaining_percentage = max(0.0, (remaining_tokens / context_window) * 100)
        
        can_fit = new_total < context_window
        
        return {
            "current_tokens": current_total,
            "current_percentage": session.get("percentage", 0.0),
            "estimated_tokens": estimated_tokens,
            "new_total": new_total,
            "new_percentage": new_percentage,
            "remaining_tokens": remaining_tokens,
            "remaining_percentage": remaining_percentage,
            "can_fit": can_fit,
            "context_window": context_window
        }


# Global context tracker instance
context_tracker = ContextTracker()


def get_context_tracker() -> ContextTracker:
    """Get the global context tracker instance"""
    return context_tracker


if __name__ == "__main__":
    # Demo context tracker
    tracker = ContextTracker()
    
    print("=== Context Tracker Demo ===\n")
    
    # Track some usage
    session_id = "test_session_123"
    
    print("Tracking usage...")
    result = tracker.track_usage(
        session_id=session_id,
        provider="openrouter",
        model="openai/gpt-4",
        input_tokens=1000,
        output_tokens=500
    )
    
    print(f"Session: {session_id}")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Percentage: {result['percentage']:.1f}%")
    print(f"Warnings: {len(result['warnings'])}")
    
    # Get warning status
    status = tracker.get_warning_status(session_id)
    print(f"Warning status: {status['level']}")
    print(f"Warning message: {status['message']}")
    
    # Estimate capacity
    estimate = tracker.estimate_remaining_capacity(session_id, 2000)
    print(f"\nEstimate for 2000 tokens:")
    print(f"  New percentage: {estimate['new_percentage']:.1f}%")
    print(f"  Remaining tokens: {estimate['remaining_tokens']}")
    print(f"  Can fit: {estimate['can_fit']}")
    
    # Get total usage
    total = tracker.get_total_usage_across_sessions()
    print(f"\nTotal across {total['session_count']} sessions:")
    print(f"  Total tokens: {total['total_tokens']}")
    print(f"  Average per session: {total['average_tokens_per_session']:.0f}")
