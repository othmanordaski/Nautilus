import os
import subprocess
import shutil
import sys
import hashlib
import time
from pathlib import Path
from typing import Optional, List, Tuple

from utils.config import config
from rich.console import Console

console = Console()


class MediaPlayer:
    """Nautilus Media Engine: mpv implementation aligned with lobster behavior."""

    @staticmethod
    def _get_watch_later_file(url: str, watchlater_dir: str) -> Optional[Path]:
        """Get the watch-later file path for a given URL (mpv uses MD5 hash)."""
        if not watchlater_dir:
            return None
        
        # mpv creates watch-later files using MD5 hash of the URL
        url_hash = hashlib.md5(url.encode()).hexdigest().upper()
        watch_file = Path(watchlater_dir) / url_hash
        
        return watch_file if watch_file.exists() else None

    @staticmethod
    def _parse_watch_later_position(watch_file: Path) -> Optional[str]:
        """Parse mpv watch-later file to extract playback position."""
        try:
            with open(watch_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('start='):
                        # Extract position in seconds
                        position_seconds = float(line.split('=')[1].strip())
                        # Convert to HH:MM:SS format
                        hours = int(position_seconds // 3600)
                        minutes = int((position_seconds % 3600) // 60)
                        seconds = int(position_seconds % 60)
                        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except Exception:
            pass
        return None

    @staticmethod
    def get_playback_position(url: str) -> str:
        """Get the last playback position for a URL from mpv watch-later files."""
        watchlater_dir = config.get("watchlater_dir")
        if not watchlater_dir:
            return "00:00:00"
        
        watch_file = MediaPlayer._get_watch_later_file(url, watchlater_dir)
        if not watch_file:
            return "00:00:00"
        
        position = MediaPlayer._parse_watch_later_position(watch_file)
        return position if position else "00:00:00"

    @staticmethod
    def play(
        url: str,
        title: str,
        start: Optional[str] = None,
        subs_links: Optional[List[str]] = None,
        callback_on_exit: Optional[callable] = None,
    ) -> Optional[str]:
        """
        Launch mpv with the given stream URL and title.
        Lobster-style: options first, URL last; optional resume and subtitles.
        Returns the final playback position after mpv exits.
        """
        player_bin = config.get("player")

        # Windows/WSL: prefer mpv.exe if mpv not in PATH
        if not shutil.which(player_bin) and shutil.which(f"{player_bin}.exe"):
            player_bin = f"{player_bin}.exe"

        if not shutil.which(player_bin):
            console.print(f"[#f85149]Player '{player_bin}' not found. Install mpv or set 'player' in config.[/#f85149]")
            return None

        # Watch-later directory for resume (like lobster's watchlater_dir)
        watchlater_dir = config.get("watchlater_dir")
        if watchlater_dir:
            Path(watchlater_dir).mkdir(parents=True, exist_ok=True)

        # Build argv: all options first, URL last (same as lobster)
        cmd = [
            player_bin,
            "--force-media-title=" + title,
            "--hwdec=auto-safe",
            "--demuxer-max-bytes=150M",
            "--save-position-on-quit",
            "--write-filename-in-watch-later-config",
            "--quiet",
        ]

        if start:
            cmd.append(f"--start={start}")

        # Subtitles (lobster: --sub-file or --sub-files)
        if subs_links:
            for sub_url in subs_links:
                if sub_url:
                    cmd.append(f"--sub-file={sub_url}")

        # Lobster: only set watch-later-directory on non-Windows (mpv default on Windows is fine)
        if watchlater_dir and sys.platform != "win32":
            cmd.append(f"--watch-later-directory={watchlater_dir}")

        # Optional: IPC socket for scripting (e.g. progress); same idea as lobster
        socket_path = Path(os.environ.get("TMPDIR", "/tmp")) / "nautilus.sock"
        if sys.platform != "win32" and socket_path.parent.exists():
            cmd.append(f"--input-ipc-server={socket_path}")

        cmd.append(url)

        console.print(f"[bold #58a6ff]▸ Launching mpv...[/bold #58a6ff]")
        try:
            # Wait for mpv to finish (blocking) so we can get final position
            process = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            
            # Small delay to ensure watch-later file is written
            time.sleep(0.5)
            
            # Get final position after playback
            final_position = MediaPlayer.get_playback_position(url)
            
            # Call callback if provided
            if callback_on_exit:
                callback_on_exit(final_position)
            
            return final_position
            
        except OSError as e:
            console.print(f"[#f85149]Failed to start player: {e}[/#f85149]")
            return None
