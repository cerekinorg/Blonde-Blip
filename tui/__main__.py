"""
Unified entry point for Blonde CLI
Handles first-time setup, migration, and main app launch

This ensures setup wizard runs for first-time users before launching CLI.
"""

from pathlib import Path
import sys

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


def main():
    """
    Main entry point that handles:
    1. First-time setup (if no config)
    2. Config migration (if needed)
    3. Main app launch
    """
    # Check if setup needed
    if not CONFIG_FILE.exists():
        from tui.setup_wizard_enhanced import EnhancedSetupWizard

        print("\nWelcome to Blonde CLI!")
        print("Running setup wizard...")

        # Run enhanced setup wizard
        setup_app = EnhancedSetupWizard()
        setup_app.run()
        
        # After setup, launch main TUI
        print("\nLaunching Blonde CLI TUI...\n")
    
    # Launch main application (welcome screen → dashboard)
    from tui.welcome_screen import WelcomeScreen
    from tui.dashboard_opencode import Dashboard
    
    # Run welcome screen and get session data
    welcome_app = WelcomeScreen()
    
    try:
        result = welcome_app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return
    except Exception as e:
        print(f"Error in welcome screen: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # If we got session data, launch dashboard
    if result and isinstance(result, dict):
        session_id = result.get('session_id')
        first_prompt = result.get('first_prompt', '')
        provider = result.get('provider', 'openrouter')
        model = result.get('model', 'openai/gpt-4')
        
        print(f"\n✓ Session started: {session_id}")
        print(f"  Provider: {provider}")
        print(f"  Model: {model}")
        print(f"\n🚀 Launching dashboard...\n")
        
        # Create and run dashboard
        dashboard = Dashboard(
            session_id=session_id, 
            first_prompt=first_prompt
        )
        try:
            dashboard.run()
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print(f"Error in dashboard: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No session started. Exiting.")


if __name__ == "__main__":
    main()
