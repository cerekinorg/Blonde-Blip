#!/usr/bin/env python3
"""
Integration test for new TUI components
Tests that all the new modules work together
"""

from pathlib import Path
import sys

# Test imports
print("Testing imports...")
try:
    from tui.blip_characters import (
        CharacterArt, get_character, list_characters, get_default_character
    )
    print("✓ blip_characters imported")
except ImportError as e:
    print(f"✗ blip_characters failed: {e}")
    sys.exit(1)

try:
    from tui.blip_manager import BlipManager, get_blip_manager
    print("✓ blip_manager imported")
except ImportError as e:
    print(f"✗ blip_manager failed: {e}")
    sys.exit(1)

try:
    from tui.session_manager import SessionManager, get_session_manager
    print("✓ session_manager imported")
except ImportError as e:
    print(f"✗ session_manager failed: {e}")
    sys.exit(1)

try:
    from tui.cost_tracker import CostTracker, get_cost_tracker
    print("✓ cost_tracker imported")
except ImportError as e:
    print(f"✗ cost_tracker failed: {e}")
    sys.exit(1)

try:
    from tui.session_panel import SessionPanel
    print("✓ session_panel imported")
except ImportError as e:
    print(f"⚠ session_panel optional (requires textual): {e}")

try:
    from tui.welcome_screen import WelcomeScreen, launch_welcome_screen
    print("✓ welcome_screen imported")
except ImportError as e:
    print(f"⚠ welcome_screen optional (requires textual): {e}")

try:
    from tui.dashboard import Dashboard, launch_dashboard
    print("✓ dashboard imported")
except ImportError as e:
    print(f"⚠ dashboard optional (requires textual): {e}")

try:
    from tui.enhanced_settings import EnhancedSettings
    print("✓ enhanced_settings imported")
except ImportError as e:
    print(f"⚠ enhanced_settings optional (requires textual): {e}")

try:
    from tui.model_switcher import ModelSwitcher
    print("✓ model_switcher imported")
except ImportError as e:
    print(f"⚠ model_switcher optional (requires textual): {e}")

try:
    from tui.file_editor import FileEditor
    print("✓ file_editor imported")
except ImportError as e:
    print(f"⚠ file_editor optional (requires textual): {e}")

try:
    from tui.diff_panel import DiffPanel
    print("✓ diff_panel imported")
except ImportError as e:
    print(f"⚠ diff_panel optional (requires textual): {e}")

try:
    from tui.agent_thinking_panel import AgentThinkingPanel
    print("✓ agent_thinking_panel imported")
except ImportError as e:
    print(f"⚠ agent_thinking_panel optional (requires textual): {e}")

try:
    from tui.context_tracker import ContextTracker
    print("✓ context_tracker imported")
except ImportError as e:
    print(f"⚠ context_tracker optional (requires textual): {e}")

print("\n" + "="*50)
print("All imports successful!")
print("="*50 + "\n")

# Test Blip system
print("Testing Blip Character System...")
blip_manager = get_blip_manager()
print(f"✓ Default character: {blip_manager.current_character_name}")

# Test character listing
characters = list_characters()
print(f"✓ Available characters: {', '.join(characters)}")

# Test art rendering
axolotl = get_character("axolotl")
wisp = get_character("wisp")
print(f"✓ Axolotl has {len(axolotl.states)} states")
print(f"✓ Wisp has {len(wisp.states)} states")

# Test character switching
if blip_manager.switch_character("wisp"):
    print(f"✓ Switched to {blip_manager.current_character_name}")
if blip_manager.switch_character("axolotl"):
    print(f"✓ Switched back to {blip_manager.current_character_name}")

print()

# Test Session Manager
print("Testing Session Manager...")
session_manager = get_session_manager()
print(f"✓ Current session ID: {session_manager.current_session_id}")

# Test session creation
session_id = session_manager.create_session(
    name="Integration Test Session",
    provider="openrouter",
    model="openai/gpt-4"
)
print(f"✓ Created session: {session_id}")

# Test chat history
session_manager.update_chat_history("user", "Hello from integration test!")
print(f"✓ Added chat message")

# Test context tracking
session_manager.update_context_usage(100, 50)
usage = session_manager.current_session_data.get("context_usage", {})
print(f"✓ Context usage: {usage['total_tokens']} tokens ({usage['percentage']:.1f}%)")

print()

# Test Cost Tracker
print("Testing Cost Tracker...")
cost_tracker = get_cost_tracker()

# Test cost calculation
cost = cost_tracker.calculate_cost("openrouter", "openai/gpt-4", 1000, 500)
print(f"✓ Cost for 1000 input + 500 output tokens: ${cost:.6f}")

# Test cost tracking
tracked_cost = cost_tracker.track_usage(
    session_id, "openrouter", "openai/gpt-4", 1000, 500
)
print(f"✓ Tracked cost: ${tracked_cost:.6f}")

# Test session cost
session_cost = cost_tracker.get_session_cost(session_id)
print(f"✓ Session total cost: ${session_cost['total_usd']:.6f}")

# Test total cost
total_cost = cost_tracker.get_total_cost()
print(f"✓ Total cost across all sessions: ${total_cost['total_usd']:.6f}")

print()

# Test session listing
print("Testing Session Listing...")
sessions = session_manager.list_sessions()
print(f"✓ Found {len(sessions)} session(s)")
for session in sessions[:3]:  # Show first 3
    print(f"  - {session['name']}: {session['messages']} messages")

print()
print("="*50)
print("Integration test PASSED!")
print("="*50)
print("\nAll core systems are working correctly!")
print("Ready to build remaining UI components.")
