# Blonde-Blip v2.0 - Integration Action Plan

**Status:** Core systems created, ready for integration
**Goal:** Complete Phase 1 (Integration & Polish) of the simplification roadmap

---

## 📊 Current Status Summary

### ✅ Completed:
- Removed 39 unnecessary files (54% reduction)
- Created new simplified core systems:
  - `tui/core/config.py` - Configuration management
  - `tui/core/session.py` - Session management
  - `tui/core/provider.py` - Provider switching
  - `tui/core/agents.py` - 5-agent system
  - `tui/main.py` - Simplified entry point
- Updated `requirements.txt` - Reduced from 66 to ~15 deps
- Created documentation guides

### ⚠️  Needs Work:
- Fix import errors in existing TUI files
- Migrate TUI to use new core systems
- Simplify monolithic CLI (1,849 lines → ~300)
- Consolidate UI panels
- Add missing UI abilities (mode toggle, agent visibility, etc.)

---

## 🎯 Phase 1: Integration Tasks

### Task 1: Fix Import Issues (Priority: HIGH)

**Problem:** `tui/__main__.py` and related files have broken imports

**Root Cause:**
- Deleted file: `tui/setup_wizard_enhanced.py`
- Import path issues with module resolution
- Missing path setup in entry points

**Solution Options:**

#### Option A: Use Existing Modules (Recommended)
Since the deleted `setup_wizard_enhanced.py` was replaced by `setup_wizard.py`, update imports to use the existing file:

**Fix in `tui/__main__.py`:**
```python
# Replace line 24:
# OLD:
from tui.setup_wizard_enhanced import EnhancedSetupWizard

# NEW:
from tui.setup_wizard import SetupWizard

# Replace line 30:
# OLD:
setup_app = EnhancedSetupWizard()

# NEW:
setup_app = SetupWizard()
```

**Fix Path Issues:**
```python
# Add to top of tui/__main__.py, after line 9:
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

#### Option B: Restore File (Alternative)
If `setup_wizard_enhanced` had critical functionality not in `setup_wizard`:
1. Check git history: `git log --all --full-history -- tui/setup_wizard_enhanced.py`
2. Restore if needed
3. Otherwise, use `setup_wizard.py`

**Expected Result:** Entry point runs without import errors, setup wizard launches correctly

---

### Task 2: Migrate TUI to New Core Systems (Priority: HIGH)

#### 2.1: Welcome Screen Migration

**File:** `tui/welcome_screen.py` (needs review for current structure)

**Changes Required:**

1. **Add path setup at top:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

2. **Import new core systems:**
```python
from tui.core import (
    get_config_manager,
    get_session_manager,
    get_provider_manager,
    get_agent_team
)
```

3. **Replace initialization code:**
```python
# Find where existing managers are initialized and replace:
# OLD:
self.config_manager = ProviderManager()
self.session_manager = SessionManager()
self.provider_manager = ProviderManager()

# NEW:
self.config = get_config_manager()
self.session_mgr = get_session_manager()
self.provider_mgr = get_provider_manager()
self.agent_team = get_agent_team()
```

4. **Update method calls:**
- Replace `self.config_manager.some_method()` with `self.config.some_method()`
- Replace `self.session_manager.some_method()` with `self.session_mgr.some_method()`

**Expected Result:** Welcome screen uses simplified core systems, works correctly

---

#### 2.2: Dashboard Migration

**File:** `tui/dashboard_opencode.py` (needs review for current structure)

**Changes Required:**

1. **Add path setup and core imports** (same as welcome screen)

2. **Replace initialization** in `__init__()`:
```python
# OLD: (find and replace)
self.query_processor = get_query_processor()
self.session_manager = get_session_manager()
self.dev_team = DevelopmentTeam(...)
self.cost_tracker = get_cost_tracker()

# NEW:
self.config = get_config_manager()
self.session_mgr = get_session_manager()
self.provider_mgr = get_provider_manager()
self.agent_team = get_agent_team()
```

3. **Update agent interactions:**
```python
# OLD:
result = self.dev_team.assign_task(...)
self.dev_team.execute_task(...)

# NEW:
result = self.agent_team.execute_agent('generator', task)
# Or for collaboration:
results = self.agent_team.collaborate(task, agents=['generator', 'reviewer', 'tester'])
```

4. **Update provider switching:**
```python
# OLD:
self.provider_manager.switch_provider(...)

# NEW:
self.provider_mgr.switch_provider(...)
```

5. **Update session tracking:**
```python
# OLD:
self.session_manager.add_message(...)
self.session_manager.update_context(...)

# NEW:
self.session_mgr.add_message(...)
self.session_mgr.update_context_usage(...)
```

**Expected Result:** Dashboard uses new core systems, 5-agent collaboration works

---

#### 2.3: Settings Panel Migration

**File:** `tui/settings_panel.py`

**Changes Required:**

1. **Add path setup and core imports**

2. **Replace config management:**
```python
# OLD: (find config manager usage)
config.save(...)

# NEW:
config = get_config_manager()
config.set('key', value)  # Auto-saves
```

**Expected Result:** Settings use simplified config API

---

### Task 3: Simplify CLI File (Priority: MEDIUM)

**File:** `tui/cli.py` (1,849 lines)

**Goal:** Extract commands to separate modules, reduce to ~300 lines

#### Step 3.1: Create Commands Directory

**Commands:**
```bash
mkdir -p tui/commands
```

**Create Files:**

**`tui/commands/__init__.py`:**
```python
from .chat import chat_cmd
from .gen import gen_cmd
from .fix import fix_cmd
from .doc import doc_cmd
from .create import create_cmd

__all__ = ['chat_cmd', 'gen_cmd', 'fix_cmd', 'doc_cmd', 'create_cmd']
```

**Extract from CLI:**

**`tui/commands/chat.py` (~100 lines):**
- Extract the `chat()` function (lines ~596-857 in CLI)
- Add imports: `from tui.core import get_config_manager, get_session_manager, get_provider_manager`
- Use core systems instead of old managers
- Return simplified chat command

**`tui/commands/gen.py` (~100 lines):**
- Extract `gen()` function (lines ~860-951 in CLI)
- Add core imports
- Use core systems

**`tui/commands/fix.py` (~100 lines):**
- Extract `fix()` function (lines ~1073-1386 in CLI)
- Add core imports
- Use core systems

**`tui/commands/doc.py` (~100 lines):**
- Extract `doc()` function (lines ~1358-1523 in CLI)
- Add core imports
- Use core systems

**`tui/commands/create.py` (~100 lines):**
- Extract `create()` function (lines ~926-1118 in CLI)
- Add core imports
- Use core systems

#### Step 3.2: Simplify Main CLI

**Reduce `tui/cli.py` to:**

```python
"""
Blonde CLI - Simplified v2.0
"""

import typer
import sys
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import commands
from tui.commands import (
    chat_cmd, gen_cmd, fix_cmd, doc_cmd, create_cmd
)

app = typer.Typer()

# Register commands
app.command()(chat_cmd)
app.command()(gen_cmd)
app.command()(fix_cmd)
app.command()(doc_cmd)
app.command()(create_cmd)

# Callback
@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", "-v", help="Show version")
):
    """Blonde CLI - Simplified v2.0"""
    if version:
        print("Blonde CLI v2.0.0 - Simplified AI Development Platform")
        raise typer.Exit()

if __name__ == "__main__":
    app()
```

**Expected Result:** CLI reduced from 1,849 to ~300 lines, modular structure

---

### Task 4: Consolidate TUI Panels (Priority: MEDIUM)

**Goal:** Merge similar components, reduce UI code complexity

#### 4.1: Merge Chat and Editor

**Files:** `tui/chat_view.py`, `tui/editor_view.py`, `tui/work_panel.py`

**Action:** Create `tui/ui/unified_work_panel.py`

**Implementation approach:**
```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tui.core import get_session_manager, get_agent_team

class UnifiedWorkPanel(App):
    """Unified work panel with chat and editor modes"""

    MODES = ["chat", "editor"]
    current_mode = "chat"

    def __init__(self):
        super().__init__()
        self.session_mgr = get_session_manager()
        self.agent_team = get_agent_team()

    def toggle_mode(self):
        """Toggle between chat and editor"""
        idx = self.MODES.index(self.current_mode)
        self.current_mode = self.MODES[(idx + 1) % len(self.MODES)]
        self.update_ui()

    def compose(self) -> ComposeResult:
        if self.current_mode == "chat":
            return self.compose_chat_mode()
        else:
            return self.compose_editor_mode()

    def compose_chat_mode(self) -> ComposeResult:
        """Compose chat UI"""
        # Import chat components
        # return chat layout
        pass

    def compose_editor_mode(self) -> ComposeResult:
        """Compose editor UI"""
        # Import editor components
        # return editor layout
        pass
```

**Expected Result:** Single unified work panel, reduced duplication

---

### Task 5: Add Missing UI Abilities (Priority: HIGH)

#### 5.1: Mode Toggle (Normal/Development)

**Add to:** Dashboard class

```python
# In Dashboard class __init__:
self.development_mode = False

# Add method:
def toggle_development_mode(self):
    """Toggle between Normal (single agent) and Development (multi-agent) modes"""
    self.development_mode = not self.development_mode
    mode_text = "Development (Multi-Agent)" if self.development_mode else "Normal (Single Agent)"
    self.mode_label.update(f"Mode: {mode_text}")
    self.log(f"🔄 Switched to {mode_text}")

# Add keyboard shortcut:
def on_key(self, event) -> None:
    if event.key == "d":
        self.toggle_development_mode()
```

**Expected Result:** User can toggle between single-agent and multi-agent modes

---

#### 5.2: Agent Thinking Visibility

**Add to:** Dashboard class

```python
def show_agent_status(self, agent_name: str, status: str):
    """Show what agent is currently doing"""
    status_text = f"🤖 {agent_name}: {status}"
    self.agent_status_panel.update(status_text)
    self.log(status_text)

# Update agent interactions:
# OLD:
result = self.agent_team.execute_agent('generator', task)

# NEW:
self.show_agent_status('Generator', 'Thinking...')
result = self.agent_team.execute_agent('generator', task)
self.show_agent_status('Generator', 'Complete')
```

**Expected Result:** Users see real-time agent activity

---

#### 5.3: Real-time Context Tracking

**Add to:** Dashboard class

```python
def update_context_display(self):
    """Update context usage in UI"""
    session = self.session_mgr._current_session
    if session:
        tokens = session.context_usage.get('total_tokens', 0)
        percentage = session.context_usage.get('percentage', 0.0)

        # Update display
        self.context_label.update(
            f"Context: {tokens:,} tokens ({percentage:.1f}%)"
        )

        # Show warnings
        if percentage >= 80:
            self.show_warning("⚠️  Context usage: 80%")
        elif percentage >= 90:
            self.show_warning("⚠️  Context usage: 90%")
        elif percentage >= 95:
            self.show_error("❌ Context usage: 95% - Consider starting new session")

# Call this after each LLM interaction:
self.update_context_display()
```

**Expected Result:** Real-time context usage visible with warnings

---

#### 5.4: Cost Tracking in UI

**Add to:** Dashboard class

```python
def update_cost_display(self):
    """Update cost tracking in UI"""
    session = self.session_mgr._current_session
    if session:
        cost = session.cost.get('total_usd', 0.0)
        self.cost_label.update(f"Cost: ${cost:.4f}")

# Call this after each LLM interaction:
self.update_cost_display()
```

**Expected Result:** Session costs visible in UI

---

#### 5.5: Provider/Model Switching During Session

**Add to:** Dashboard class

```python
def switch_provider(self, provider_name: str):
    """Switch AI provider during active session"""
    success = self.provider_mgr.switch_provider(provider_name)
    if success:
        self.log(f"✅ Switched to {provider_name}")
        self.provider_label.update(f"Provider: {provider_name}")
    else:
        self.show_error(f"❌ Failed to switch to {provider_name}")

def switch_model(self, model_name: str):
    """Switch AI model during active session"""
    self.provider_mgr.set_model(model_name)
    self.log(f"✅ Switched to model: {model_name}")
    self.model_label.update(f"Model: {model_name}")

# Add commands:
def on_provider_switch(self, provider: str):
    self.switch_provider(provider)

def on_model_switch(self, model: str):
    self.switch_model(model)
```

**Expected Result:** Users can switch provider/model mid-session

---

## 🧪 Testing Plan

### Test Suite to Create:

**`tests/test_core.py`:**
```python
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tui.core import (
    get_config_manager,
    get_session_manager,
    get_provider_manager,
    get_agent_team
)

class TestCoreSystems(unittest.TestCase):
    def test_config_manager(self):
        config = get_config_manager()
        config.set('test', 'value')
        self.assertEqual(config.get('test'), 'value')

    def test_session_manager(self):
        session_mgr = get_session_manager()
        session = session_mgr.create_session()
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.session_id)

    def test_provider_manager(self):
        provider_mgr = get_provider_manager()
        # Test provider switching
        success = provider_mgr.switch_provider('local')
        self.assertTrue(success)

    def test_agent_team(self):
        team = get_agent_team()
        # Test single agent execution
        result = team.execute_agent('generator', 'test')
        self.assertIsNotNone(result)
        # Test collaboration
        results = team.collaborate('test', agents=['generator', 'reviewer'])
        self.assertIn('generator', results)
        self.assertIn('reviewer', results)

if __name__ == '__main__':
    unittest.main()
```

**Run tests:**
```bash
python3 tests/test_core.py -v
```

---

## 📋 Step-by-Step Execution

### Day 1: Entry Point Fixes
- [ ] Fix imports in `tui/__main__.py`
- [ ] Add path setup to entry points
- [ ] Test entry point launches correctly
- [ ] Test setup wizard runs

### Day 2: Core System Migration
- [ ] Update welcome_screen.py imports and initialization
- [ ] Update dashboard_opencode.py imports and initialization
- [ ] Update settings_panel.py imports and initialization
- [ ] Test TUI works with new core systems

### Day 3: CLI Simplification
- [ ] Create `tui/commands/` directory
- [ ] Extract chat command to separate file
- [ ] Extract gen command to separate file
- [ ] Extract fix command to separate file
- [ ] Extract doc command to separate file
- [ ] Extract create command to separate file
- [ ] Simplify main CLI to ~300 lines
- [ ] Test all CLI commands work

### Day 4: UI Consolidation
- [ ] Create unified work panel
- [ ] Merge chat/editor views
- [ ] Test unified panel works
- [ ] Remove old duplicate files

### Day 5: UI Enhancement
- [ ] Add mode toggle to dashboard
- [ ] Add agent thinking visibility
- [ ] Add real-time context tracker
- [ ] Add cost tracking to UI
- [ ] Add provider/model switching UI
- [ ] Test all new features

### Day 6: Testing & Polish
- [ ] Create test suite
- [ ] Run all tests
- [ ] Fix any failures
- [ ] Polish animations
- [ ] Update documentation
- [ ] Prepare v2.0.0 release

---

## 🎯 Success Criteria

After completing all tasks, verify:

- [ ] No import errors in Python code
- [ ] All TUI files use new core systems
- [ ] CLI reduced to ~300 lines
- [ ] All 5 agents working correctly
- [ ] Mode toggle functional (Normal/Development)
- [ ] Agent thinking visible in UI
- [ ] Context/cost tracking visible in UI
- [ ] Provider/model switching works in session
- [ ] Session management works completely
- [ ] All tests passing (>90% success rate)
- [ ] Documentation updated and accurate

---

## 📊 Final State Expected

**Blonde-Blip v2.0.0 Production Release**

### Metrics Achieved:
- Files: 72 → ~30 (60% reduction) ✅
- Dependencies: 66 → ~15 (77% reduction) ✅
- CLI Size: 1,849 → ~300 lines (84% reduction) ✅
- Agent System: 9 → 5 (44% reduction) ✅
- Architecture: Clean, simple, maintainable ✅

### Features Working:
- Multi-agent collaboration (5 agents) ✅
- Provider switching (4+ providers) ✅
- Session management (complete lifecycle) ✅
- Clean TUI (3-column dashboard) ✅
- Local/Cloud AI integration ✅
- Mode toggle (Normal/Development) ✅
- Agent thinking visibility ✅
- Real-time context tracking ✅
- Cost tracking ✅
- Provider/model switching mid-session ✅

### Quality Standards:
- All imports resolving ✅
- No runtime errors ✅
- Test coverage >80% ✅
- Documentation complete ✅
- Ready for PyPI distribution ✅

---

## 🚀 Next Phases

After Phase 1 completion:

**Phase 2: Feature Enhancement** (Optional)
- Real-time agent collaboration visualization
- Advanced session search/filtering
- Custom agent creation framework
- Plugin system for extensions
- Web dashboard (GUI alternative)
- VS Code extension

**Phase 3: Enterprise Readiness** (Optional)
- Comprehensive test suite
- Performance benchmarking
- API documentation
- CI/CD pipeline
- Docker containerization
- Migration guides

---

## 📞 Support Resources

### Documentation:
- `ARCHITECTURE_GUIDE.md` - Complete system architecture
- `SIMPLIFICATION_PROGRESS.md` - Detailed progress report
- `README.md` - User-facing documentation
- `INTEGRATION_ACTION_PLAN.md` - This file

### Key Files Reference:
- Core systems: `tui/core/`
- TUI components: `tui/` (to be migrated)
- Commands: `tui/commands/` (to be created)
- Model adapters: `models/`

---

**Next Step:** Begin Task 1 - Fix Entry Point Imports

**Estimated Time:** 1-2 weeks for full Phase 1 completion

**Target Release Date:** Blonde-Blip v2.0.0 - [TBD based on progress]

---

## 📝 Notes

This is a comprehensive action plan. Start with Task 1 and work through sequentially.

Each task builds on the previous one. Complete one task fully before moving to the next.

Testing should be done after each task to catch issues early.

**Good luck! 🚀**
