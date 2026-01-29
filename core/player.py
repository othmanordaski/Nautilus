import os
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional, List

from utils.config import config
from rich.console import Console

console = Console()


class MediaPlayer:
    """Nautilus Media Engine: mpv implementation aligned with lobster behavior."""

    @staticmethod
    def play(
        url: str,
        title: str,
        start: Optional[str] = None,
        subs_links: Optional[List[str]] = None,
    ):
        """
        Launch mpv with the given stream URL and title.
        Lobster-style: options first, URL last; optional resume and subtitles.
        """
        player_bin = config.get("player")

        # Windows/WSL: prefer mpv.exe if mpv not in PATH
        if not shutil.which(player_bin) and shutil.which(f"{player_bin}.exe"):
            player_bin = f"{player_bin}.exe"

        if not shutil.which(player_bin):
            console.print(f"[red]Player '{player_bin}' not found. Install mpv or set 'player' in config.[/red]")
            return

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

        console.print("[bold cyan]Launching mpv...[/bold cyan]")
        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as e:
            console.print(f"[red]Failed to start player: {e}[/red]")
