# Blonde CLI Welcome Screen UI Update Plan

## 📋 Overview

Complete redesign of the welcome screen from full-screen layout to compact centered design with theme-aware logo, expandable chatbox, and integrated configuration system.

---

## 🎯 Requirements Summary

### **Core Requirements**
- ✅ Compact centered layout (not full-screen)
- ✅ One-size ASCII logo with theme-aware coloring
- ✅ Chatbox: 2-3 sentences tall, auto-scroll, expandable
- ✅ Provider/Model info as compact badges (non-clickable)
- ✅ Real-time updates when settings change
- ✅ First-time setup flow (provider, model, API, blip, theme, privacy)
- ✅ In-session configuration via settings menu

### **Design Decisions**
- **Logo Size:** One specific size (one-size-fits-all)
- **Default Theme:** None theme (user can switch later)
- **Chat Scroll:** Auto-scroll to show what's being typed
- **Quick Switch:** Add to settings menu (not Ctrl+P)
- **Setup Scope:** Provider, model, API, blip, theme, privacy (blip+ can skip)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                Screen (centered)                    │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           #welcome_container               │   │
│  │  (80x25, centered, border, background)      │   │
│  │                                             │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │         #logo_section               │   │   │
│  │  │    (ASCII logo, theme-colored)      │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  │                                             │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │         #chat_section               │   │   │
│  │  │  ┌─────────────┬─────────────────┐ │   │   │
│  │  │  │#chat_input  │  #model_info    │ │   │   │
│  │  │  │(2-3 lines,  │ (compact badges)│ │   │   │
│  │  │  │scrollable)  │                 │ │   │   │
│  │  │  └─────────────┴─────────────────┘ │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  │                                             │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │         #help_text                   │   │   │
│  │  │    (minimal help text)               │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Files to Modify

### **Primary Files**
1. `tui/welcome_screen.py` - **Major restructure**
2. `tui/enhanced_settings.py` - Add quick switch options
3. `tui/setup_wizard_enhanced.py` - Update first-time setup
4. `blonde` - Entry point logic

### **Supporting Files**
5. `tui/cli.py` - Update app initialization
6. `tui/provider_manager.py` - Add quick config methods
7. `tui/session_manager.py` - Ensure proper session handling

---

## 🎨 Component Design Specifications

### **1. ASCII Logo System**

#### **Logo Specifications**
```python
# Resized ASCII logo (one-size-fits-all)
ASCII_LOGO = r"""
 ██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
 ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══██╗██╔════╝
██████╔╝██║     ██║   ██║██╔██╗ ██║██║  ██║█████╗  
 ██╔══██╗██║     ██║   ██║██║╚██╗██║██║  ██║██╔══╝  
 ██████╔╝███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
 ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝
"""
```

#### **Theme Color Mapping**
```python
THEME_COLORS = {
    "none": "white",      # Default theme
    "auto": "cyan",       # Auto-detect theme
    "light": "blue",      # Light theme
    "dark": "cyan",       # Dark theme
}
```

#### **Reactive Color System**
```python
class WelcomeScreen(App):
    logo_color = reactive('white')  # Start with 'none' theme
    
    def get_theme_color(self) -> str:
        """Get current theme color for logo"""
        theme = self.config.get('preferences', {}).get('colors', 'none')
        return THEME_COLORS.get(theme, 'white')
    
    def watch_logo_color(self, old_color, new_color):
        """Update logo color when theme changes"""
        logo_widget = self.query_one("#ascii_logo", Static)
        logo_widget.update(f"[bold {new_color}]{ASCII_LOGO}[/bold {new_color}]")
```

### **2. Chat Input Component**

#### **Specifications**
- **Height:** 2 lines minimum, 3 lines maximum
- **Behavior:** Auto-expand to 3 lines, then vertical scroll
- **Scroll:** Auto-scroll to show what's being typed
- **Widget:** `Input` with custom styling

#### **CSS Implementation**
```css
#chat_input {
    width: 60%;
    height: 2;
    max-height: 3;
    overflow-y: auto;
    border: solid $primary;
    background: $surface;
    padding: 1;
}

#chat_input:focus {
    border: solid $accent;
    background: $primary;
}
```

#### **Behavior Implementation**
```python
class ChatInput(Input):
    """Custom chat input with auto-scroll behavior"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = 3
    
    def _on_change(self, event: Input.Changed) -> None:
        """Handle input change and auto-scroll"""
        # Auto-scroll to show what's being typed
        self.scroll_end()
        
        # Expand height if needed (up to 3 lines)
        line_count = len(self.value.split('\n'))
        if line_count > self.max_lines:
            self.styles.height = self.max_lines
```

### **3. Provider/Model Badge System**

#### **Badge Design**
```css
#model_info {
    width: 40%;
    margin-left: 2;
    padding: 1;
    background: $surface;
    border: solid $accent;
    border-title: "Current Model";
    border-title-align: center;
}

#provider_badge, #model_badge {
    width: 100%;
    padding: 0 1;
    margin: 0 0 1 0;
    border: solid $primary;
    background: $panel;
    text-align: center;
}
```

#### **Badge Content**
```python
def _update_provider_model_badges(self):
    """Update provider/model display badges"""
    config = self._load_config()
    provider = config.get('default_provider', 'openrouter')
    providers = config.get('providers', {})
    model = providers.get(provider, {}).get('model', 'openai/gpt-4')
    
    provider_badge = self.query_one("#provider_badge", Static)
    model_badge = self.query_one("#model_badge", Static)
    
    provider_badge.update(f"Provider: [bold cyan]{provider}[/bold cyan]")
    model_badge.update(f"Model: [bold cyan]{model}[/bold cyan]")
```

### **4. Container Layout System**

#### **Main Container CSS**
```css
Screen {
    align: center middle;
    background: $background;
}

#welcome_container {
    width: 80;
    height: auto;
    min-height: 20;
    border: solid $primary;
    border-title: "Blonde CLI";
    border-title-align: center;
    background: $panel;
    padding: 2;
    margin: 2;
}

#logo_section {
    text-align: center;
    padding: 1;
    height: 8;
}

#chat_section {
    display: flex;
    height: auto;
    margin-top: 1;
}

#help_text {
    text-align: center;
    text-style: dim;
    padding: 1;
    margin-top: 1;
}
```

---

## ⚙️ Configuration System Integration

### **1. First-Time Setup Flow**

#### **Setup Wizard Enhancement**
**File:** `tui/setup_wizard_enhanced.py`

**Setup Steps:**
1. **Provider Selection** (Required)
   - OpenRouter, OpenAI, Anthropic, Local
   - API key input for cloud providers
2. **Model Selection** (Required)
   - Provider-specific model dropdown
   - Custom model input option
3. **API Configuration** (Required)
   - Test connection functionality
   - Save provider settings
4. **Blip Character** (Optional - can skip)
   - Character selection with preview
   - Default: axolotl
5. **Theme Selection** (Optional - can skip)
   - Default: "none" theme
   - Options: none, auto, light, dark
6. **Privacy Settings** (Optional - can skip)
   - Default: "balanced"
   - Options: strict, balanced, permissive

#### **Setup Completion Flow**
```python
# In setup_wizard_enhanced.py
def action_complete_setup(self):
    """Complete setup and launch welcome screen"""
    # Save configuration
    self._save_config()
    
    # Exit setup wizard
    self.exit()
    
    # CLI will automatically launch welcome screen
    # since config.json now exists
```

### **2. In-Session Configuration**

#### **Enhanced Settings Integration**
**File:** `tui/enhanced_settings.py`

**Add to Model & Provider Tab:**
```python
def _compose_model_provider_tab(self):
    """Compose model and provider selection tab"""
    with Vertical(id="model_provider_tab"):
        # ... existing provider/model selection ...
        
        yield Static()  # Spacer
        
        # Quick Switch Section (NEW)
        yield Static("[bold]Quick Configuration[/bold]")
        yield Static("Add new provider configurations:")
        yield Button("Add OpenRouter Config", id="add_openrouter_btn")
        yield Button("Add OpenAI Config", id="add_openai_btn")
        yield Button("Add Anthropic Config", id="add_anthropic_btn")
        yield Button("Add Local Model", id="add_local_btn")
        
        yield Static()  # Spacer
        
        # Current Status
        yield Static("Current Status:")
        yield Static(id="current_status_display")
```

#### **Quick Config Dialogs**
```python
@on(Button.Pressed, "#add_openrouter_btn")
def on_add_openrouter_config(self):
    """Add OpenRouter configuration dialog"""
    self.push_screen(ProviderConfigDialog("openrouter"), self._on_provider_config_result)

class ProviderConfigDialog(ModalScreen[dict]):
    """Dialog for adding provider configuration"""
    
    def compose(self) -> ComposeResult:
        with Container():
            yield Static(f"[bold]Add {self.provider_name} Configuration[/bold]")
            yield Static("API Key:")
            yield Input(placeholder="Enter API key", password=True, id="api_key")
            yield Static("Model:")
            yield Select(values=self._get_model_options(), id="model_select")
            yield Static("Custom Model (optional):")
            yield Input(placeholder="e.g., meta-llama/llama-3-70b", id="custom_model")
            with Horizontal():
                yield Button("Save", id="save_btn", variant="primary")
                yield Button("Cancel", id="cancel_btn")
```

### **3. Real-time Configuration Updates**

#### **Configuration Watcher**
```python
class WelcomeScreen(App):
    def __init__(self):
        super().__init__()
        self._config_watcher = None
        self._last_config_mtime = 0
    
    def on_mount(self) -> None:
        """Start configuration file watcher"""
        self._start_config_watcher()
        self._update_from_config()
    
    def _start_config_watcher(self):
        """Watch configuration file for changes"""
        import time
        
        def watch_config():
            while True:
                try:
                    config_path = Path.home() / ".blonde" / "config.json"
                    if config_path.exists():
                        mtime = config_path.stat().st_mtime
                        if mtime > self._last_config_mtime:
                            self._last_config_mtime = mtime
                            self.call_from_thread(self._update_from_config)
                except Exception:
                    pass
                time.sleep(1)  # Check every second
        
        import threading
        self._config_watcher = threading.Thread(target=watch_config, daemon=True)
        self._config_watcher.start()
    
    def _update_from_config(self):
        """Update UI when configuration changes"""
        config = self._load_config()
        
        # Update logo color
        theme = config.get('preferences', {}).get('colors', 'none')
        self.logo_color = THEME_COLORS.get(theme, 'white')
        
        # Update provider/model badges
        self._update_provider_model_badges()
        
        # Update other UI elements as needed
```

---

## 🔄 Flow Integration

### **1. Entry Point Flow**

#### **File:** `blonde`
```python
#!/usr/bin/env python3
"""
Blonde CLI Entry Point
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    config_path = Path.home() / ".blonde" / "config.json"
    
    if not config_path.exists():
        # First-time setup
        from tui.setup_wizard_enhanced import EnhancedSetupWizard
        setup_app = EnhancedSetupWizard()
        setup_app.run()
        
        # Setup completed, now launch main app
        from tui.cli import app
        app()
    else:
        # Configuration exists, launch main app
        from tui.cli import app
        app()
```

### **2. CLI Integration**

#### **File:** `tui/cli.py`
```python
# In main app class
def on_mount(self) -> None:
    """Initialize and show welcome screen"""
    # Load configuration
    config = self._load_config()
    
    # Push welcome screen
    self.push_screen(WelcomeScreen())
```

### **3. Session Management Integration**

#### **Welcome Screen Session Handling**
```python
class WelcomeScreen(App):
    def action_start_session(self):
        """Start new session with current configuration"""
        config = self._load_config()
        provider = config.get('default_provider', 'openrouter')
        providers = config.get('providers', {})
        model = providers.get(provider, {}).get('model', 'openai/gpt-4')
        
        # Create session
        session_id = self.session_manager.create_session(
            provider=provider,
            model=model
        )
        
        # Switch to dashboard
        self.app.push_screen(Dashboard())
```

---

## 🎯 Implementation Steps

### **Phase 1: Foundation**
1. **Create resized ASCII logo**
   - Generate one-size-fits-all logo
   - Test with different themes

2. **Restructure welcome_screen.py layout**
   - Remove full-screen containers
   - Implement centered compact layout
   - Add CSS for new structure

### **Phase 2: Core Components**
3. **Implement theme-aware logo system**
   - Add reactive color system
   - Create theme color mapping
   - Test with all themes

4. **Create expandable chat input**
   - Implement 2-3 line auto-expand
   - Add auto-scroll behavior
   - Test with long input

### **Phase 3: Configuration Integration**
5. **Add provider/model badge system**
   - Create compact badge design
   - Implement real-time updates
   - Test configuration changes

6. **Integrate with enhanced_settings.py**
   - Add quick configuration options
   - Create provider config dialogs
   - Test settings integration

### **Phase 4: Setup Flow**
7. **Update setup_wizard_enhanced.py**
   - Add all required setup steps
   - Implement skip functionality
   - Test first-time setup flow

8. **Update entry point logic**
   - Modify `blonde` entry point
   - Test setup → welcome screen flow

### **Phase 5: Polish & Testing**
9. **Add configuration watcher**
   - Implement real-time updates
   - Test file change detection

10. **Comprehensive testing**
    - Test all themes
    - Test configuration changes
    - Test first-time setup
    - Test in-session reconfiguration

---

## 🧪 Testing Checklist

### **Layout Testing**
- [ ] Welcome screen centered on different terminal sizes
- [ ] Logo displays correctly with all themes
- [ ] Chat input expands to 3 lines properly
- [ ] Chat input scrolls correctly after 3 lines
- [ ] Provider/model badges display correctly

### **Configuration Testing**
- [ ] First-time setup creates proper config
- [ ] Settings changes update badges in real-time
- [ ] Theme changes update logo color
- [ ] Provider switching works correctly

### **Flow Testing**
- [ ] `blonde` command runs setup first time
- [ ] `blonde` command runs welcome screen after setup
- [ ] Settings modal opens and closes correctly
- [ ] Configuration dialogs save properly

### **Integration Testing**
- [ ] Session manager integration works
- [ ] Provider manager integration works
- [ ] Enhanced settings integration works
- [ ] All keyboard shortcuts work

---

## 📝 Notes & Considerations

### **Performance Considerations**
- Configuration file watcher should be lightweight
- Real-time updates should not block UI
- Theme switching should be instant

### **Error Handling**
- Graceful handling of missing config file
- Proper error messages for invalid API keys
- Fallback to defaults if config is corrupted

### **Accessibility**
- High contrast themes should work properly
- Keyboard navigation should be complete
- Screen reader compatibility

### **Future Enhancements**
- Terminal theme detection for "auto" theme
- Provider-specific logo variations
- Animated logo transitions
- Custom logo upload support

---

## 🎉 Success Criteria

### **Must-Have Features**
- ✅ Compact centered welcome screen layout
- ✅ Theme-aware ASCII logo coloring
- ✅ 2-3 line expandable chat input with auto-scroll
- ✅ Real-time provider/model badge updates
- ✅ Complete first-time setup flow
- ✅ In-session configuration via settings

### **Nice-to-Have Features**
- ✅ Configuration file watcher
- ✅ Quick provider configuration dialogs
- ✅ Comprehensive error handling
- ✅ Full theme support testing

---

**Document Version:** 1.0  
**Created:** January 4, 2026  
**Author:** Blonde CLI Development Team  
**Status:** Ready for Implementation