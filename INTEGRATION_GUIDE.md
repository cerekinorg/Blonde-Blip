# 🚀 Dashboard Integration - FINAL IMPLEMENTATION GUIDE

## ✅ Phase 1: Session Data Loading - COMPLETE

### Completed Changes:

1. **Updated dashboard_opencode.py**:
   - ✅ Added SessionManager import
   - ✅ Added session_manager to __init__
   - ✅ Added context_update_timer
   - ✅ Updated on_mount() to load session data
   - ✅ Added _update_session_data() method
   - ✅ Added _update_context_usage() method
   - ✅ Added _update_provider_info() method
   - ✅ Added _update_modified_files() method
   - ✅ Added _update_context_from_session() timer callback

2. **Updated context_panel.py** (Complete Rewrite):
   - ✅ Fixed all method signatures
   - ✅ Added cost display to SessionInfoSection
   - ✅ Added session_cost reactive variable
   - ✅ Added update_provider() method to SessionInfoSection
   - ✅ Added update_cost() method to SessionInfoSection
   - ✅ Fixed all watch methods
   - ✅ Clean implementation without errors

### Files Modified:
- `tui/dashboard_opencode.py` - +70 lines
- `tui/context_panel.py` - Completely rewritten (clean version)

---

## ⏳ Phase 2: QueryProcessor Integration - IN PROGRESS

### What Needs to Be Done:

1. **Add SessionManager to QueryProcessor** (10 min)
   ```python
   # File: tui/query_processor.py:75-82
   def __init__(self):
       self.provider_manager = None
       self.development_team = None
       self.optimizer = None
       self.session_manager = None  # ADD THIS
       
       if MANAGERS_AVAILABLE:
           self.provider_manager = ProviderManager()
           try:
               from .session_manager import get_session_manager  # ADD THIS
               self.session_manager = get_session_manager()  # ADD THIS
           except:
               pass
           self._init_agents()
   ```

2. **Add Token Tracking to Local Adapter** (10 min)
   
   **Option A: Apply Patch** (Recommended)
   Run these commands:
   ```bash
   cd /home/amar/Reboot/Blonde-cli/models
   sed -i '26 a\        self.last_input_tokens = 0\n        self.last_output_tokens = 0' local.py
   sed -i '89 a\\            # Estimate input tokens (rough approximation: 1 token ≈ 4 chars)\\n            self.last_input_tokens = len(prompt) // 4' local.py
   sed -i '97 a\\n            # Estimate output tokens\\n            self.last_output_tokens = len(response) // 4' local.py
   sed -i '102 a\\n            if self.debug:\\n                console.print(f\"[yellow]Tokens - Input: {self.last_input_tokens}, Output: {self.last_output_tokens}[/yellow]\")' local.py
   ```
   
   **Option B: Manual Edit**
   File: `models/local.py`
   
   - **Line 26**: Add after `self.llm = self._load_model()`:
     ```python
     self.last_input_tokens = 0  # Track input tokens
     self.last_output_tokens = 0  # Track output tokens
     ```
   
   - **Line 89**: Before `output = self.llm(...)`:
     ```python
     # Estimate input tokens (rough approximation: 1 token ≈ 4 chars)
     self.last_input_tokens = len(prompt) // 4
     ```
   
   - **Line 97**: After `response = output["choices"][0]["text"].strip()`:
     ```python
     # Estimate output tokens
     self.last_output_tokens = len(response) // 4
     ```
   
   - **Line 102**: In the `if self.debug:` block:
     ```python
     if self.debug:
         console.print(f"[yellow]Tokens - Input: {self.last_input_tokens}, Output: {self.last_output_tokens}[/yellow]")
     ```

3. **Enhance Progress Callbacks** (15 min)
   
   File: `tui/query_processor.py`
   
   - **Line 886-887** (in `_handle_general_chat`):
     ```python
     if progress_callback:
         progress_callback("assistant", "Thinking...")
         
         # Update session with chat history
         if self.session_manager:
             self.session_manager.update_chat_history("user", query)
     ```
   
   - **Line 896** (before return):
     ```python
     self.session_manager.update_chat_history("assistant", response)
     ```

4. **Add Cost Tracking** (20 min)
   
   File: `tui/query_processor.py:886-896`
   
   - **Line 886** (in `_handle_general_chat`):
     ```python
     # Import at top
     from .cost_tracker import get_cost_tracker
     
     # Inside method
     if self.session_manager:
         # Get token counts
         input_tokens = getattr(llm_adapter, 'last_input_tokens', len(query) // 4)
         output_tokens = getattr(llm_adapter, 'last_output_tokens', len(response) // 4)
         
         # Calculate cost
         cost_tracker = get_cost_tracker()
         cost = cost_tracker.calculate_cost(
             provider="openrouter",  # Get from session or provider manager
             model="gpt-4",  # Get from session
             input_tokens=input_tokens,
             output_tokens=output_tokens
         )
         
         # Update session cost
         self.session_manager.update_cost(
             provider="openrouter",
             model="gpt-4",
             input_tokens=input_tokens,
             output_tokens=output_tokens,
             cost_usd=cost
         )
     ```

---

## ⏸️ Phase 3: Gradual Blip Movement - PENDING

### What Needs to Be Done:

File: `tui/blip_panel.py`

1. **Add Animation Support** (20 min)
   - Add `target_position` reactive to BlipSprite
   - Add `animation_timer` attribute
   - Add `animate_to_position()` method
   - Add `_animate_step()` method
   
2. **Update update_status()** (10 min)
   - Add state-to-position mapping
   - Trigger animation when state changes

---

## ⏸️ Phase 4: 50-Second Context Panel Updates - 80% COMPLETE

### What's Done:
- ✅ Timer started in dashboard on_mount()
- ✅ `_update_context_from_session()` method added
- ✅ Calls session_manager to get latest data
- ✅ Updates context panel with new data

### What's Left:
- Test that timer fires correctly (5 min)

---

## ⏸️ Phase 5: Context Panel Enhancements - 80% COMPLETE

### What's Done:
- ✅ `update_provider()` added to SessionInfoSection
- ✅ `update_cost()` added to SessionInfoSection
- ✅ Cost display added to compose
- ✅ All watch methods fixed

### What's Left:
- Test that methods work correctly (5 min)

---

## ⏸️ Phase 6: Modified Files Real-Time Tracking - PENDING

### What Needs to Be Done:

File: `tui/query_processor.py`

1. **Add File Tracking to All Agents** (30 min)
   - Add `files_modified` list initialization
   - Add file modification callback support
   - Track files during all agent operations

2. **Update Dashboard** (10 min)
   - Handle `result.files_modified` in `_on_query_complete()`
   - Update session manager with file edits
   - Update context panel with modified files

---

## 🎯 Implementation Order

1. **Phase 2A** - Add SessionManager to QueryProcessor (10 min)
2. **Phase 2B** - Add Token Tracking to Local Adapter (10 min)
3. **Phase 2C** - Enhance Progress Callbacks (15 min)
4. **Phase 2D** - Add Cost Tracking (20 min)
5. **Phase 3** - Blip Animation (30 min)
6. **Phase 4 Test** - Verify Timer Works (5 min)
7. **Phase 5 Test** - Verify Methods Work (5 min)
8. **Phase 6** - File Tracking (40 min)
9. **End-to-End Test** - Full Integration Test (15 min)

**Total Estimated Time:** 2.5 hours

---

## ✅ Success Criteria (Tracking)

- [x] Dashboard loads with actual session data
- [x] Context usage shows real token count (placeholder needs real data)
- [ ] Blip moves gradually when state changes
- [x] Context panel updates every 50 seconds (timer implemented, needs testing)
- [ ] Modified files from previous queries appear in context panel
- [ ] QueryProcessor updates SessionManager in real-time
- [ ] Cost tracking updates during queries

**Progress: 38%**

---

## 🚀 How to Complete Integration

### Quick Start (30 min):
```bash
# 1. Add SessionManager to QueryProcessor
# Edit: tui/query_processor.py line 75-82
# Add: self.session_manager = None
# Add: from .session_manager import get_session_manager
# Add: self.session_manager = get_session_manager()

# 2. Add Token Tracking to Local Adapter (Option B - Manual)
# Edit: models/local.py
# Follow Option B instructions above

# 3. Test
python3 -c "from tui.dashboard_opencode import launch_dashboard; launch_dashboard()"
```

### Full Integration (2.5 hours):
Follow all steps in Phase 2-6 above in order.

---

## 📝 Notes

### Current State:
- Dashboard: ✅ Can load session data
- Context Panel: ✅ Clean implementation
- QueryProcessor: ⏳ Needs session manager integration
- Local Adapter: ⏳ Needs token tracking
- Blip Panel: ⏳ Needs animation

### Configuration Working:
```
~/.blonde/config.json:
{
  "version": "1.0.0",
  "setup_completed": true,
  "default_provider": "openrouter",
  "providers": {
    "openrouter": {"model": "xiaomi/mimo-v2-flash:free"}
  },
  "preferences": {
    "blip_character": "axolotl",
    "blip_animation_speed": 0.3  # Use this for animation timing
  }
}
```

### Session Data Structure:
```json
{
  "session_id": "20260105_224738",
  "name": "Session 20260105_224738",
  "provider": "openrouter",
  "model": "xiaomi/mimo-v2-flash:free",
  "blip_character": "axolotl",
  "chat_history": [],
  "context_usage": {
    "total_tokens": 0,
    "context_window": 128000,
    "percentage": 0.0
  },
  "cost": {
    "total_usd": 0.0,
    "by_provider": {}
  },
  "files_edited": [],
  "metadata": {
    "version": "1.0.0",
    "archived": false
  }
}
```

---

## 🐛 Known Issues

1. **models/local.py Missing Dependency**
   - Error: `ModuleNotFoundError: No module named 'llama_cpp'`
   - Fix: `pip install llama-cpp-python` or use existing working model

2. **Import Errors in Old Files**
   - Old dashboard.py, welcome_screen.py, etc. have import errors
   - Fix: Not needed, using new dashboard_opencode.py

3. **Context Panel Fixed**
   - Old version had corrupted edits
   - Fix: ✅ Complete rewrite applied

---

**Last Updated:** 2025-01-05 23:00
**Status:** Ready for Phase 2 implementation
