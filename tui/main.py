"""
Blonde CLI - Simplified Main Entry Point
Clean, minimal entry point for the application
"""

from pathlib import Path
import sys
import os

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


def main():
    """
    Simplified main entry point:
    1. Check setup
    2. Launch welcome screen
    3. Run dashboard
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    # Import and run setup if needed
    if not CONFIG_FILE.exists():
        print("\n🎨 Welcome to Blonde CLI!")
        print("Running setup wizard...\n")
        from tui.setup_wizard import SetupWizard

        setup_app = SetupWizard()
        setup_app.run()

    # Launch main application
    print("\n🚀 Launching Blonde CLI...\n")

    try:
        from tui.welcome_screen import WelcomeScreen
        from tui.dashboard_opencode import Dashboard

        welcome_app = WelcomeScreen()
        result = welcome_app.run()

        # If session started, launch dashboard
        if result and isinstance(result, dict):
            session_id = result.get('session_id')
            first_prompt = result.get('first_prompt', '')

            print(f"✓ Session: {session_id}\n")

            dashboard = Dashboard(
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
