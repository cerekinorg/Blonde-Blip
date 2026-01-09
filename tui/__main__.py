"""
Blonde CLI - Unified Entry Point v2.0
Clean, working entry point for application
"""

from pathlib import Path
import sys
import json

# Add project root to Python path for proper imports
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
            # Import new core systems
            from tui.core import get_config_manager

            # Create default config
            default_config = {
                'provider': 'openrouter',
                'model': 'openai/gpt-4',
                'blip_character': 'axolotl',
                'setup_complete': True
            }
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)

            print("\n✅ Setup complete!\n")

        except ImportError as e:
            print(f"\n⚠️  Core systems not available: {e}")
            print("Creating default configuration...\n")

            # Fallback: Create default config
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
    print("🚀 Launching Blonde CLI v2.0...\n")

    try:
        # Import with absolute imports
        from simple_dashboard import SimpleDashboard

        # Run dashboard
        app = SimpleDashboard()
        app.run()

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
