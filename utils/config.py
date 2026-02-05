import json
import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent.parent
    DEFAULT_CONFIG_PATH = BASE_DIR / "nautilus_config.json"
    _default_watchlater = Path(os.environ.get("TMPDIR", os.environ.get("TEMP", "/tmp"))) / "nautilus_watchlater"

    DEFAULTS = {
        "base_url": "https://flixhq.to",
        "decrypt_api": "https://dec.eatmynerds.live",
        "player": "mpv",
        "history_db": "nautilus.db",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "watchlater_dir": str(_default_watchlater),
        "provider": "Vidcloud",
        "subs_language": "english",
        "quality": "1080",
        "no_subs": False,
        "history": True,
        "download_dir": ".",
    }

    def __init__(self):
        self.settings = self.DEFAULTS.copy()
        if self.DEFAULT_CONFIG_PATH.exists():
            try:
                with open(self.DEFAULT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    self.settings.update(json.load(f))
            except (json.JSONDecodeError, IOError):
                # Fall back to defaults if config is malformed or unreadable
                pass

    def get(self, key):
        return self.settings.get(key)

config = Config()