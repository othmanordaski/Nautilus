"""
Cross-platform path resolver for Nautilus.

Centralises every file-system decision so the rest of the codebase
never touches raw env vars or hard-coded ``/tmp`` paths.

Resolution order (config & data):
  1. Environment variable override  (NAUTILUS_CONFIG / NAUTILUS_DATA)
  2. Project-local file              (portable / dev mode — backward compat)
  3. Platform-standard directory      (XDG on Linux, AppData on Win, Library on macOS)
"""

import os
import sys
import tempfile
from pathlib import Path

# ── constants ────────────────────────────────────────────────────────
APP_NAME = "nautilus"
PROJECT_DIR = Path(__file__).resolve().parent.parent


# ── platform directories ─────────────────────────────────────────────

def _platform_config_dir() -> Path:
    """Return the OS-standard config root for *this user*."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / APP_NAME


def _platform_data_dir() -> Path:
    """Return the OS-standard data root for *this user*."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
    return base / APP_NAME


# ── public helpers ────────────────────────────────────────────────────

def config_dir() -> Path:
    """Return (and lazily create) the platform config directory."""
    d = _platform_config_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def data_dir() -> Path:
    """Return (and lazily create) the platform data directory."""
    d = _platform_data_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def tmp_dir() -> Path:
    """Platform-safe temp directory (never hard-codes /tmp)."""
    return Path(tempfile.gettempdir())


# ── resolved file paths ──────────────────────────────────────────────

def config_file() -> Path:
    """
    Resolve the config-file path.

    Priority:
      1. ``NAUTILUS_CONFIG`` env var   → use that path verbatim.
      2. ``nautilus_config.json`` next to the project root → portable / dev mode.
      3. Platform config dir           → ``<config_dir>/config.json``.
    """
    env = os.environ.get("NAUTILUS_CONFIG")
    if env:
        return Path(env).resolve()

    local = PROJECT_DIR / "nautilus_config.json"
    if local.exists():
        return local

    return config_dir() / "config.json"


def history_db(configured: str = "") -> Path:
    """
    Resolve the history-database path.

    Args:
        configured: Value from the user's config (may be empty, relative, or absolute).

    Priority:
      1. Absolute path in *configured*    → use as-is.
      2. Non-default relative path        → resolve from PROJECT_DIR.
      3. ``nautilus.db`` in PROJECT_DIR    → backward compat if file already exists.
      4. Platform data dir                → ``<data_dir>/nautilus.db``.
    """
    if configured and configured not in ("nautilus.db", ""):
        p = Path(configured)
        if p.is_absolute():
            return p
        return (PROJECT_DIR / p).resolve()

    # backward compat: honour an existing project-local database
    local = PROJECT_DIR / "nautilus.db"
    if local.exists():
        return local

    return data_dir() / "nautilus.db"


def watchlater_dir() -> Path:
    """Default mpv watch-later directory inside the data dir."""
    return data_dir() / "watchlater"


def default_editor() -> str:
    """Return a sensible text editor for the current platform."""
    return (
        os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or ("notepad" if sys.platform == "win32" else "nano")
    )
