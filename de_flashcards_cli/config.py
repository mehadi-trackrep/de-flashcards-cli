"""
Manages local config stored at ~/.de-flashcards-cli/config.json
Stores: anthropic_api_key, firestore_project_id, preferences
"""

import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".de-flashcards-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get(key: str, default=None):
    """Get a config value. Falls back to environment variable."""
    # Environment variable takes priority
    env_map = {
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "firestore_project_id": "FIRESTORE_PROJECT_ID",
        "google_credentials": "GOOGLE_APPLICATION_CREDENTIALS",
    }
    env_key = env_map.get(key)
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]

    return _load().get(key, default)


def set_value(key: str, value: str):
    """Persist a config value."""
    data = _load()
    data[key] = value
    _save(data)
    # Also export to environment for current session
    env_map = {
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "firestore_project_id": "FIRESTORE_PROJECT_ID",
    }
    if key in env_map:
        os.environ[env_map[key]] = value


def show_config():
    """Print current config (masking secrets)."""
    data = _load()
    if not data:
        print("  No config saved yet. Run: de-flashcards-cli config")
        return
    for k, v in data.items():
        if "key" in k or "secret" in k:
            display = v[:8] + "..." if len(v) > 8 else "****"
        else:
            display = v
        print(f"  {k}: {display}")


def apply_to_env():
    """Load saved config values into environment variables for the session."""
    data = _load()
    mapping = {
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "firestore_project_id": "FIRESTORE_PROJECT_ID",
        "google_credentials": "GOOGLE_APPLICATION_CREDENTIALS",
    }
    for cfg_key, env_key in mapping.items():
        if cfg_key in data and not os.environ.get(env_key):
            os.environ[env_key] = data[cfg_key]
