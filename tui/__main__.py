"""
Unified entry point for Blonde CLI
Handles first-time setup, migration, and main app launch

This ensures setup wizard runs for first-time users before launching CLI.
"""

from pathlib import Path

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
        from tui.setup_wizard import run_setup_wizard
        
        print("\nWelcome to Blonde CLI!")
        print("Running setup wizard...")
        
        # Run setup wizard
        run_setup_wizard()
        
        # After setup, launch main TUI
        print("\nLaunching Blonde CLI TUI...\n")
        
    # Check for migration needed (can be added later)
    # else:
    #     from tui.config_migration import check_migration_needed
    #     if check_migration_needed():
    #         from tui.config_migration import run_migration
    #         run_migration()
    
    # Launch main application
    from tui.main_tui import launch_modern_tui
    
    try:
        launch_modern_tui()
    except Exception as e:
        print(f"Error launching TUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
