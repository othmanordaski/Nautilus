import json
from pathlib import Path

from utils.paths import config_file, watchlater_dir as _default_watchlater_dir


class Config:
    DEFAULT_CONFIG_PATH = config_file()

    DEFAULTS = {
        "base_url": "https://flixhq.to",
        "decrypt_api": "https://dec.eatmynerds.live",
        "player": "mpv",
        "history_db": "",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "watchlater_dir": str(_default_watchlater_dir()),
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