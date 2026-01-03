#!/usr/bin/env python3
"""
Demo/Test script for Modern Textual TUI
Shows a quick demonstration of the TUI features without requiring full CLI setup
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Horizontal, Vertical, Container
from rich.text import Text
from rich.panel import Panel

class DemoTUI(App):
    """Simple demo of the modern TUI"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 3 1fr 1fr 3;
    }
    
    #header {
        column-span: 2;
        height: 3;
    }
    
    #content {
        column-span: 2;
    }
    
    #footer {
        column-span: 2;
        height: 3;
    }
    
    Button {
        width: 30;
        margin: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear", "Clear Screen")
    ]
    
    def compose(self) -> ComposeResult:
        """Compose demo UI"""
        yield Header("Blonde CLI - Modern TUI Demo")
        
        with Container(id="content"):
            with Vertical():
                yield Static(
                    Panel(
                        Text(
                            "🚀 Modern Textual TUI Implementation\n\n"
                            "This is a demo of the new TUI features:\n\n"
                            "✓ File browser & editor\n"
                            "✓ Blip mascot integration\n"
                            "✓ Agent status panel\n"
                            "✓ Working directory display\n"
                            "✓ Command palette (Ctrl+P)\n"
                            "✓ Settings modal (Ctrl+S)\n\n"
                            "Press buttons below to explore features!",
                            justify="center"
                        ),
                        title="Features",
                        border_style="cyan"
                    )
                )
                
                with Horizontal():
                    yield Button("Launch Full TUI", id="launch")
                    yield Button("Show Components", id="show")
                    yield Button("View Docs", id="docs")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "launch":
            self.action_launch()
        elif event.button.id == "show":
            self.action_show()
        elif event.button.id == "docs":
            self.action_docs()
    
    def action_launch(self) -> None:
        """Launch full TUI"""
        from tui.modern_tui import launch_modern_tui
        self.exit()
        launch_modern_tui()
    
    def action_show(self) -> None:
        """Show component list"""
        from tui.modern_tui import ModernTUI
        app = ModernTUI()
        
        components = [
            ("BlipWidget", "Blip mascot with states"),
            ("AgentStatusTable", "8 agent status display"),
            ("WorkingDirectoryDisplay", "Current directory"),
            ("FileEditor", "File viewer and editor"),
            ("ChatPanel", "Interactive chat"),
            ("CommandPalette", "Quick command access"),
            ("SettingsModal", "Tabbed settings"),
        ]
        
        content = "\n".join([
            f"  • {name:30s} - {desc}"
            for name, desc in components
        ])
        
        self.query_one("#content").update(
            Panel(
                Text(f"📦 Components Loaded:\n\n{content}"),
                title="Components",
                border_style="green"
            )
        )
    
    def action_docs(self) -> None:
        """Show docs location"""
        docs = [
            "MODERN_TUI_README.md",
            "MODERN_TUI_QUICKSTART.md", 
            "MODERN_TUI_SUMMARY.md"
        ]
        
        content = "\n".join([
            f"  📄 {doc}"
            for doc in docs
        ])
        
        self.query_one("#content").update(
            Panel(
                Text(f"📚 Documentation:\n\n{content}\n\nLocated in project root."),
                title="Documentation",
                border_style="yellow"
            )
        )
    
    def action_clear(self) -> None:
        """Clear content"""
        self.query_one("#content").update(
            Panel(
                Text("Screen cleared. Press 'c' again or 'Show Components'."),
                title="Cleared",
                border_style="dim"
            )
        )


def main():
    """Run demo"""
    print("\n🚀 Blonde CLI - Modern TUI Demo\n")
    print("=" * 50)
    print()
    print("This demo showcases the new Textual TUI.")
    print("Press 'q' to quit, 'c' to clear screen.")
    print()
    print("=" * 50)
    
    import time
    time.sleep(1)
    
    app = DemoTUI()
    app.run()


if __name__ == "__main__":
    main()
