# Blonde-Blip Integration Guide

**Phase 1: Core Integration - Complete Implementation Plan**

This guide provides step-by-step instructions to integrate new core systems with existing TUI.

---

## 📋 Integration Tasks Overview

### Task 1: Fix Entry Point ✅
**File:** `tui/__main__.py`
**Status:** Needs fixing
**Action:** Update imports to use existing modules properly

### Task 2: Migrate TUI to Use New Core Systems
**Files:** 
- `tui/welcome_screen.py`
- `tui/dashboard_opencode.py`
- `tui/settings_panel.py`
**Status:** Needs migration to new core systems

### Task 3: Simplify CLI File
**File:** `tui/cli.py` (1,849 lines → ~300 lines)
**Status:** Needs extraction to separate modules

### Task 4: Consolidate TUI Panels
**Files:** Multiple UI components
**Status:** Needs consolidation

### Task 5: Add Missing UI Abilities
**Features:** Mode toggle, agent visibility, cost tracking
**Status:** Needs implementation

---

## 🔧 Task 1: Fix Entry Point

### Current Issues in `tui/__main__.py`:
1. Line 24: Imports deleted file `tui.setup_wizard_enhanced`
2. Line 37-38: Import paths may not resolve correctly
3. Missing proper path setup

### Fix:

```python
"""
Blonde CLI - Unified Entry Point
Clean, working entry point for application
"""

from pathlib import Path
import sys
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


def main():
    """
    Main entry point:
    1. Check/setup wizard
    2. Launch welcome screen
    3. Run dashboard
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    # Setup wizard if needed
    if not CONFIG_FILE.exists():
        print("\n🎨 Welcome to Blonde CLI!")
        print("Running setup wizard...\n")

        try:
            from tui import setup_wizard
            setup_app = setup_wizard.SetupWizard()
            setup_app.run()

            # Create default config if not created
            if not CONFIG_FILE.exists():
                default_config = {
                    'provider': 'openrouter',
                    'model': 'openai/gpt-4',
                    'blip_character': 'axolotl',
                    'setup_complete': True
                }
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(default_config, f, indent=2)

            print("\n✅ Setup complete!\n")

        except ImportError as e:
            print(f"\n⚠️  Setup wizard not available: {e}")
            print("Creating default configuration...\n")

            default_config = {
                'provider': 'openrouter',
                'model': 'openai/gpt-4',
                'blip_character': 'axolotl',
                'setup_complete': True
            }
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)

    # Launch main application
    print("🚀 Launching Blonde CLI...\n")

    try:
        # Import with proper path setup
        from tui import welcome_screen
        from tui import dashboard_opencode

        # Run welcome screen
        welcome_app = welcome_screen.WelcomeScreen()
        result = welcome_app.run()

        # If session started, launch dashboard
        if result and isinstance(result, dict):
            session_id = result.get('session_id')
            first_prompt = result.get('first_prompt', '')

            print(f"✅ Session: {session_id[:8]}...\n")

            dashboard = dashboard_opencode.Dashboard(
                session_id=session_id,
                first_prompt=first_prompt
            )
            dashboard.run()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

---

## 🔧 Task 2: Migrate TUI to Use New Core Systems

### 2.1 Update Welcome Screen

**File:** `tui/welcome_screen.py`

**Changes needed:**

```python
# Add at top of file, after existing imports:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new core systems
from tui.core import get_config_manager, get_session_manager, get_provider_manager, get_agent_team

# Replace old imports:
# OLD:
# from tui.provider_manager import ProviderManager
# from tui.session_manager import SessionManager
# from tui.cost_tracker import CostTracker
# from tui.dev_team import DevelopmentTeam

# NEW (add these):
config = get_config_manager()
session_mgr = get_session_manager()
provider_mgr = get_provider_manager()
agent_team = get_agent_team()
```

**Update methods:**

1. `__init__()`:
   ```python
   def __init__(self):
       super().__init__()
       self.config = get_config_manager()
       self.session_mgr = get_session_manager()
       self.provider_mgr = get_provider_manager()
       self.agent_team = get_agent_team()
   ```

2. `create_session()`:
   ```python
   # OLD:
   # session = self.session_manager.create_session(...)

   # NEW:
   session = self.session_mgr.create_session(
       provider=self.provider_mgr.current_provider(),
       model=self.provider_mgr.current_model()
   )
   ```

3. `save_config()`:
   ```python
   # OLD:
   # self.config_manager.save_config(...)

   # NEW:
   self.config.set('key', value)  # Auto-saves
   ```

---

### 2.2 Update Dashboard

**File:** `tui/dashboard_opencode.py`

**Changes needed:**

```python
# Add at top:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new core systems
from tui.core import get_config_manager, get_session_manager, get_provider_manager, get_agent_team

# Replace old imports in __init__:
config = get_config_manager()
session_mgr = get_session_manager()
provider_mgr = get_provider_manager()
agent_team = get_agent_team()
```

**Update methods:**

1. `__init__()`:
   ```python
   def __init__(self, session_id, first_prompt=""):
       super().__init__()
       self.config = get_config_manager()
       self.session_mgr = get_session_manager()
       self.provider_mgr = get_provider_manager()
       self.agent_team = get_agent_team()
   ```

2. `handle_chat()`:
   ```python
   # OLD:
   # self.dev_team.execute_task(...)

   # NEW:
   result = self.agent_team.execute_agent('generator', task)
   # or:
   results = self.agent_team.collaborate(task, agents=['generator', 'reviewer'])
   ```

3. `update_context()`:
   ```python
   # NEW:
   self.session_mgr.update_context_usage(tokens, percentage)
   ```

4. `switch_provider()`:
   ```python
   # NEW:
   self.provider_mgr.switch_provider(provider_name)
   ```

---

### 2.3 Update Settings Panel

**File:** `tui/settings_panel.py`

**Changes needed:**

```python
# Add at top:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new core systems
from tui.core import get_config_manager

# Replace old imports:
config = get_config_manager()
```

**Update methods:**

1. `save_provider()`:
   ```python
   # NEW:
   config.provider = new_provider_value  # Auto-saves
   ```

2. `save_model()`:
   ```python
   # NEW:
   config.model = new_model_value  # Auto-saves
   ```

3. `save_blip_character()`:
   ```python
   # NEW:
   config.blip_character = new_character  # Auto-saves
   ```

---

## 🔧 Task 3: Simplify CLI File

### 3.1 Create Commands Directory

**Create:** `tui/commands/` directory

**Create files:**

**`tui/commands/__init__.py`:**
```python
from .chat import chat
from .gen import gen
from .fix import fix
from .doc import doc
from .create import create

__all__ = ['chat', 'gen', 'fix', 'doc', 'create']
```

**`tui/commands/chat.py`**: Extract chat logic from CLI (approx 100 lines)

**`tui/commands/gen.py`**: Extract gen logic from CLI (approx 100 lines)

**`tui/commands/fix.py`**: Extract fix logic from CLI (approx 100 lines)

**`tui/commands/doc.py`**: Extract doc logic from CLI (approx 100 lines)

**`tui/commands/create.py`**: Extract create logic from CLI (approx 100 lines)

### 3.2 Simplify Main CLI

**Reduce `tui/cli.py` to ~300 lines:**

```python
"""
Blonde CLI - Simplified v2.0
Clean, modular command structure
"""

import typer
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import commands
from tui.commands import chat, gen, fix, doc, create

app = typer.Typer()

# Register commands
app.command()(chat)
app.command()(gen)
app.command()(fix)
app.command()(doc)
app.command()(create)

# Callback for default behavior
@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
    no_tui: bool = typer.Option(False, "--no-tui", help="Disable TUI"),
):
    """Blonde CLI - Simplified v2.0"""
    if version:
        print("Blonde CLI v2.0.0 - Simplified AI Development Platform")
        print("Privacy-First | Multi-Agent | Provider-Agnostic")
        print(f"Reduced from 72 to ~30 files (60% smaller)")
        print(f"Dependencies: 66 to ~15 (77% reduction)")
        raise typer.Exit()

if __name__ == "__main__":
    app()
```

---

## 🔧 Task 4: Consolidate TUI Panels

### 4.1 Merge Chat and Editor

**Create:** `tui/ui/unified_work_panel.py`

**Features:**
- Single class `UnifiedWorkPanel`
- Mode toggle (Chat ↔ Editor)
- Shared state
- Uses core systems

**Implementation sketch:**
```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tui.core import get_session_manager

class UnifiedWorkPanel(App):
    """Unified work panel with chat and editor modes"""

    MODES = ["chat", "editor"]
    current_mode = "chat"

    def __init__(self):
        super().__init__()
        self.session_mgr = get_session_manager()

    def toggle_mode(self):
        """Toggle between chat and editor"""
        idx = self.MODES.index(self.current_mode)
        self.current_mode = self.MODES[(idx + 1) % len(self.MODES)]

    def compose(self) -> ComposeResult:
        if self.current_mode == "chat":
            return self.compose_chat()
        else:
            return self.compose_editor()
```

---

## 🔧 Task 5: Add Missing UI Abilities

### 5.1 Mode Toggle (Normal/Development)

**Add to Dashboard:**

```python
class Dashboard(App):
    def __init__(self, session_id, first_prompt=""):
        super().__init__()
        self.development_mode = False
        self.config = get_config_manager()
        self.agent_team = get_agent_team()

    def toggle_mode(self):
        """Toggle between Normal and Development modes"""
        self.development_mode = not self.development_mode
        mode = "Development Mode (Multi-Agent)" if self.development_mode else "Normal Mode (Single Agent)"

        # Update UI
        self.mode_label.update(f"Mode: {mode}")
        self.log(f"🔄 Switched to {mode}")
```

### 5.2 Agent Thinking Visibility

**Add to Dashboard:**

```python
def show_agent_thinking(self, agent_name: str, status: str):
    """Show agent thinking status"""
    thinking_text = f"🤖 {agent_name}: {status}"
    self.agent_status.update(thinking_text)
    self.log(thinking_text)
```

### 5.3 Real-time Context Tracker

**Add to Dashboard:**

```python
def update_context_display(self):
    """Update context usage display"""
    session = self.session_mgr._current_session
    if session:
        tokens = session.context_usage.get('total_tokens', 0)
        percentage = session.context_usage.get('percentage', 0.0)

        # Update display
        self.context_display.update(
            f"Context: {tokens:,} tokens ({percentage:.1f}%)"
        )

        # Warnings
        if percentage >= 80:
            self.warning("⚠️  Context usage: 80%")
        if percentage >= 90:
            self.warning("⚠️  Context usage: 90%")
        if percentage >= 95:
            self.error("❌ Context usage: 95% - Consider new session")
```

### 5.4 Cost Tracking in UI

**Add to Dashboard:**

```python
def update_cost_display(self):
    """Update cost tracking display"""
    session = self.session_mgr._current_session
    if session:
        cost = session.cost.get('total_usd', 0.0)
        self.cost_display.update(f"Cost: ${cost:.4f}")
```

### 5.5 Provider/Model Switching During Session

**Add to Dashboard:**

```python
def switch_provider_in_session(self, provider: str):
    """Switch provider during active session"""
    success = self.provider_mgr.switch_provider(provider)
    if success:
        self.log(f"✅ Switched to {provider}")
        self.provider_label.update(f"Provider: {provider}")
    else:
        self.error(f"❌ Failed to switch to {provider}")

def switch_model_in_session(self, model: str):
    """Switch model during active session"""
    self.provider_mgr.set_model(model)
    self.log(f"✅ Switched to model: {model}")
    self.model_label.update(f"Model: {model}")
```

---

## ✅ Testing Plan

### Test 1: Core Systems
```bash
# Test config
python3 -c "from tui.core import get_config_manager; cm = get_config_manager(); print('Config OK')"

# Test session
python3 -c "from tui.core import get_session_manager; sm = get_session_manager(); s = sm.create_session(); print('Session OK')"

# Test provider
python3 -c "from tui.core import get_provider_manager; pm = get_provider_manager(); print('Provider OK')"

# Test agents
python3 -c "from tui.core import get_agent_team; at = get_agent_team(); print('Agents OK')"
```

### Test 2: Integration Flow
```bash
# Test entry point
python3 tui/__main__.py

# Test: Setup → Welcome → Dashboard flow works
# Test: Create session
# Test: Chat with agent
# Test: Switch provider
# Test: Toggle mode
```

### Test 3: CLI Commands
```bash
# Test each command
blonde chat   # Should start interactive chat
blonde gen    # Should generate code
blonde fix    # Should fix code
blonde doc    # Should generate docs
blonde create # Should create file
```

---

## 📋 Execution Order

### Day 1: Entry Point & Core Tests
1. ✅ Fix `tui/__main__.py` imports
2. ✅ Test core systems work independently
3. ✅ Test entry point launches

### Day 2: TUI Migration
1. ✅ Update welcome_screen.py to use core
2. ✅ Update dashboard_opencode.py to use core
3. ✅ Update settings_panel.py to use core
4. ✅ Test TUI still works with new core

### Day 3: CLI Simplification
1. ✅ Create `tui/commands/` directory
2. ✅ Extract chat command
3. ✅ Extract gen command
4. ✅ Extract fix command
5. ✅ Extract doc command
6. ✅ Extract create command
7. ✅ Simplify main CLI to ~300 lines

### Day 4: UI Consolidation
1. ✅ Merge chat/editor into unified panel
2. ✅ Create simplified dashboard
3. ✅ Add mode toggle UI
4. ✅ Add agent thinking visibility

### Day 5: UI Enhancement
1. ✅ Add real-time context tracker
2. ✅ Add cost tracking to UI
3. ✅ Add provider/model switching in session
4. ✅ Test all UI features
5. ✅ Polish animations

### Day 6: Testing & Polish
1. ✅ Run all tests
2. ✅ Fix any issues
3. ✅ Update documentation
4. ✅ Prepare v2.0.0 release

---

## 🎯 Success Criteria

After completing all tasks:

- [ ] All import errors resolved
- [ ] All TUI files use new core systems
- [ ] CLI reduced to ~300 lines
- [ ] All 5 agents working correctly
- [ ] Mode toggle functional
- [ ] Agent thinking visible
- [ ] Context/cost tracking in UI
- [ ] Provider/model switching works in session
- [ ] Session management works completely
- [ ] All tests passing
- [ ] Documentation updated

---

## 📊 Expected Final State

**Blonde-Blip v2.0.0**
- ✅ Clean, working codebase with ~30 files
- ✅ All imports resolving correctly
- ✅ New core systems integrated everywhere
- ✅ Simplified CLI (~300 lines)
- ✅ Consolidated UI panels
- ✅ All missing abilities added
- ✅ Complete testing passing
- ✅ Production-ready

**Metrics:**
- Files: 72 → ~30 (60% reduction)
- Dependencies: 66 → ~15 (77% reduction)
- CLI Size: 1,849 → ~300 lines (84% reduction)
- Agent System: 9 → 5 (44% reduction)

---

## 🚀 Next Phase

After integration is complete, proceed to:
- **Phase 3**: Comprehensive Testing & Documentation
- **Phase 4**: Final Polish & v2.0.0 Release

See main roadmap in `SIMPLIFICATION_PROGRESS.md`.
