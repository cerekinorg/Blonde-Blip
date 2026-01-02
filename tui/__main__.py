"""
Unified entry point for Blonde CLI
Handles first-time setup, migration, and main app launch

This ensures setup wizard runs for first-time users before launching CLI.
"""

from pathlib import Path

def main():
    """
    Main entry point that handles:
    1. First-time setup (if no config)
    2. Config migration (if needed)
    3. Main app launch
    """
    CONFIG_DIR = Path.home() / ".blonde"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    # Check if setup needed
    if not CONFIG_FILE.exists():
        from tui.setup_wizard import SetupWizard
        from tui.blip import blip

        blip.happy("Welcome to Blonde CLI! Let's get you set up...")
        wizard = SetupWizard()
        wizard.run()

    # Check for migration needed
    else:
        from tui.config_migration import check_migration_needed
        if check_migration_needed():
            from tui.config_migration import run_migration
            run_migration()

    # Launch main application
    from tui.cli import app
    app()


if __name__ == "__main__":
    main()
