#!/usr/bin/env python3
"""
Blonde CLI - Simplified Entry Point
Clean, minimal entry point that works with existing TUI
"""

from pathlib import Path
import sys

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


def main():
    """
    Simplified main entry point:
    1. Ensure config directory exists
    2. Launch welcome screen
    3. Run dashboard if session started
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    # Setup wizard if needed
    if not CONFIG_FILE.exists():
        print("\n🎨 Welcome to Blonde CLI!")
        print("Running setup wizard...\n")

        try:
            # Try to import and run setup wizard
            import setup_wizard
            setup_app = setup_wizard.SetupWizard()
            setup_app.run()
            print("\n✓ Setup complete!\n")
        except ImportError as e:
            print(f"\n⚠️  Setup wizard not available: {e}")
            print("Using default configuration...\n")

            # Create default config
            import json
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
        # Try to import and run welcome screen
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import welcome_screen

        welcome_app = welcome_screen.WelcomeScreen()
        result = welcome_app.run()

        # If session started, try to launch dashboard
        if result and isinstance(result, dict):
            session_id = result.get('session_id')
            first_prompt = result.get('first_prompt', '')

            print(f"✓ Session: {session_id[:8]}...\n")

            try:
                import dashboard_opencode
                dashboard = dashboard_opencode.Dashboard(
                    session_id=session_id,
                    first_prompt=first_prompt
                )
                dashboard.run()
            except Exception as e:
                print(f"\n❌ Dashboard error: {e}")
                import traceback
                traceback.print_exc()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
