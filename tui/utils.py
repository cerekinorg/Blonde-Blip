# In utils.py (create if not exists)
import logging
import os
import json
from pathlib import Path

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    print("Warning: keyring not available, falling back to config storage")

# Configuration file path
CONFIG_FILE = Path.home() / ".blonde" / "config.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)

def setup_logging(debug: bool = False):
    """Sets up logging to file and console.
    Args:
        debug: If True, log debug messages to console and file.
    """
    log_dir = Path.home() / ".blonde"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "debug.log"

    logger = logging.getLogger("blonde")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # File handler (always log DEBUG)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console handler (INFO unless debug)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)

    # Avoid duplicate handlers
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def save_api_key(key_name: str, key_value: str):
    """Save API key securely using keyring, fallback to config file.

    Args:
        key_name: Name of the API key (e.g., 'OPENAI_API_KEY')
        key_value: The API key value
    """
    if KEYRING_AVAILABLE:
        try:
            keyring.set_password("blonde-cli", key_name, key_value)
            # Mark as configured in config (without storing the key)
            _mark_key_configured(key_name, True)
            return
        except Exception as e:
            print(f"Warning: Failed to save to keyring, falling back to config: {e}")

    # Fallback: save to config.json (less secure)
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except:
            config = {}
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][key_name] = key_value
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def load_api_key(key_name: str) -> str:
    """Load API key from keyring or config file.

    Args:
        key_name: Name of the API key to load

    Returns:
        API key value or empty string if not found
    """
    # Try keyring first
    if KEYRING_AVAILABLE:
        try:
            key = keyring.get_password("blonde-cli", key_name)
            if key:
                return key
        except Exception:
            pass

    # Fallback: try config.json
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            return config.get("api_keys", {}).get(key_name, "")
        except:
            pass

    return ""


def _mark_key_configured(key_name: str, configured: bool):
    """Mark an API key as configured in config.json (without storing the key).

    Args:
        key_name: Name of the API key
        configured: Whether the key is configured
    """
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except:
            config = {}

    if "api_keys_configured" not in config:
        config["api_keys_configured"] = {}

    config["api_keys_configured"][key_name] = configured
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def is_key_configured(key_name: str) -> bool:
    """Check if an API key is configured.

    Args:
        key_name: Name of the API key to check

    Returns:
        True if the key is configured, False otherwise
    """
    # Try keyring first
    if KEYRING_AVAILABLE:
        try:
            key = keyring.get_password("blonde-cli", key_name)
            if key:
                return True
        except Exception:
            pass

    # Check config.json markers
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            if config.get("api_keys_configured", {}).get(key_name, False):
                return True
            # Also check if key exists directly in config
            if config.get("api_keys", {}).get(key_name):
                return True
        except:
            pass

    return False




