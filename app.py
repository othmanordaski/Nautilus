"""
Nautilus – Lobster-style media engine in Python.
Search → Movie/TV → Season → Episode → Play (mpv) with provider, subs, quality, continue, next episode.
"""
import argparse
import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

from __version__ import __version__
from rich.prompt import Prompt, IntPrompt
from rich.text import Text

from core.scraper import FlixScraper
from core.player import MediaPlayer
from core.database import Database
from models.media import MediaItem
from utils.config import config
from utils.validation import (
    validate_search_query,
    validate_download_path,
    check_disk_space,
    sanitize_filename,
    validate_url,
    check_dependency,
)
from ui import (
    console,
    banner,
    section_title,
    stream_panel,
    prompt_select_items,
    prompt_text,
    status_msg,
    ok_msg,
    err_msg,
    warn_msg,
    set_context,
    clear_context,
)


def parse_args():
    p = argparse.ArgumentParser(
        description="Nautilus – Search and play movies/TV (lobster-style).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nautilus                         # Search and play
  nautilus -l                      # Link only (copy URL for VLC)
  nautilus -c                      # Continue from history
  nautilus -j                      # Output JSON (video/subs) and exit
  nautilus -p UpCloud -q 720       # Provider and quality
  nautilus -n                      # No subtitles
  nautilus -d [path]               # Download (path defaults to config or cwd)
        """,
    )
    p.add_argument("--version", action="version", version=f"Nautilus {__version__}")
    p.add_argument("-c", "--continue", dest="continue_watch", action="store_true", help="Continue from history")
    p.add_argument("-d", "--download", nargs="?", const="", metavar="PATH", help="Download video (optional path, else config/cwd)")
    p.add_argument("-l", "--link", action="store_true", help="Only print stream URL (e.g. for VLC)")
    p.add_argument("-j", "--json", action="store_true", help="Output decrypt JSON and exit")
    p.add_argument("-p", "--provider", default=None, help="Provider (default: Vidcloud)")
    p.add_argument("-q", "--quality", default=None, help="Quality e.g. 1080, 720 (default from config)")
    p.add_argument("-n", "--no-subs", action="store_true", help="Disable subtitles")
    p.add_argument("-e", "--edit", action="store_true", help="Edit config file")
    p.add_argument("query", nargs="*", help="Search query (optional)")
    return p.parse_args()


def _apply_cli_config(args):
    if args.provider is not None:
        config.settings["provider"] = args.provider
    if args.quality is not None:
        config.settings["quality"] = args.quality
    if args.no_subs:
        config.settings["no_subs"] = True


def _safe_filename(title: str) -> str:
    """Sanitize title for use as filename (lobster: tr -d ':/')."""
    return sanitize_filename(title)


def _download_video(url: str, title: str, download_dir: str, subs_links: list) -> None:
    """Download stream with yt-dlp (faster) or ffmpeg fallback. Optional subtitles."""
    # Check for required dependencies
    has_ytdlp, _ = check_dependency("yt-dlp")
    has_ffmpeg, ffmpeg_err = check_dependency("ffmpeg")
    
    if not has_ytdlp and not has_ffmpeg:
        err_msg("Neither yt-dlp nor ffmpeg found. Install at least one to download videos.")
        return
    
    # Validate URL
    url_valid, url_error = validate_url(url)
    if not url_valid:
        err_msg(f"Invalid URL: {url_error}")
        return

    # Validate and prepare download directory
    out_dir = Path(download_dir or ".").resolve()
    path_valid, path_error = validate_download_path(str(out_dir))
    if not path_valid:
        err_msg(f"Invalid download path: {path_error}")
        return

    # Check disk space (require at least 500MB)
    has_space, space_warning = check_disk_space(str(out_dir), required_mb=500)
    if not has_space:
        err_msg(space_warning)
        return
    if space_warning:
        warn_msg(space_warning)

    out_dir.mkdir(parents=True, exist_ok=True)
    safe_title = _safe_filename(title)
    out_path = out_dir / f"{safe_title}.mkv"

    # Check if file already exists
    if out_path.exists():
        warn_msg(f"File already exists: {out_path.name}")
        return

    console.print(status_msg("Downloading to ") + str(out_path))
    console.print()
    
    # Always try yt-dlp first (5-10x faster than ffmpeg, especially with aria2c)
    if has_ytdlp:
        temp_out = out_path if not subs_links else out_path.with_suffix('.temp.mkv')
        try:
            cmd = [
                "yt-dlp",
                "--no-warnings",
                "--progress",
                "--console-title",
                "-f", "best",
                "-o", str(temp_out),
            ]
            
            # Add aria2c for parallel downloads if available (5x-10x faster)
            if shutil.which("aria2c"):
                cmd.extend([
                    "--downloader", "aria2c",
                    "--downloader-args", "aria2c:-x 16 -s 16 -k 1M --console-log-level=warn --summary-interval=0"
                ])
            
            # Add concurrent fragments for speed
            cmd.extend(["-N", "8"])  # 8 parallel fragments
            
            cmd.append(url)
            
            subprocess.run(cmd, check=True)
            
            # If we have external subtitles, mux them with ffmpeg
            if subs_links and has_ffmpeg:
                console.print()
                console.print(status_msg("Embedding subtitles..."))
                ffmpeg_cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats", "-i", str(temp_out)]
                for sub_url in subs_links:
                    if sub_url:
                        ffmpeg_cmd.extend(["-i", sub_url])
                ffmpeg_cmd.extend(["-map", "0:v", "-map", "0:a"])
                for i in range(1, len(subs_links) + 1):
                    ffmpeg_cmd.extend(["-map", str(i)])
                ffmpeg_cmd.extend(["-c:v", "copy", "-c:a", "copy", "-c:s", "srt", str(out_path)])
                
                subprocess.run(ffmpeg_cmd, check=True)
                temp_out.unlink()  # Remove temp file
            
            console.print()
            ok_msg("Saved: " + str(out_path))
            return
            
        except subprocess.CalledProcessError as e:
            if temp_out.exists() and temp_out != out_path:
                temp_out.unlink()
            warn_msg(f"yt-dlp failed (code {e.returncode}), trying ffmpeg...")
        except KeyboardInterrupt:
            console.print()
            warn_msg("Download cancelled")
            if temp_out.exists():
                temp_out.unlink()
            return
    
    # Fallback to ffmpeg only if yt-dlp unavailable or failed
    if has_ffmpeg:
        try:
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats", "-i", url]
            if subs_links:
                for sub_url in subs_links:
                    if sub_url:
                        cmd.extend(["-i", sub_url])
                cmd.extend(["-map", "0:v", "-map", "0:a"])
                for i in range(1, len(subs_links) + 1):
                    cmd.extend(["-map", str(i)])
                cmd.extend(["-c:v", "copy", "-c:a", "copy", "-c:s", "srt"])
            else:
                cmd.extend(["-c", "copy"])
            cmd.append(str(out_path))
            
            subprocess.run(cmd, check=True)
            console.print()
            ok_msg("Saved: " + str(out_path))
        except FileNotFoundError:
            err_msg("ffmpeg not found. Install ffmpeg to use -d/--download.")
        except subprocess.CalledProcessError as e:
            err_msg(f"Download failed (ffmpeg error code {e.returncode})")
        except KeyboardInterrupt:
            console.print()
            warn_msg("Download cancelled")
            if out_path.exists():
                out_path.unlink()
                console.print(f"[#e3b341]Removed partial file: {out_path.name}[/#e3b341]")
    else:
        err_msg("No download tool available. yt-dlp failed and ffmpeg not found.")


def _show_and_maybe_play(data, link_only: bool, json_output: bool, download: bool = False, download_dir: str = ""):
    """Print stream URL (and subs/json), download, or launch mpv."""
    url = data.get("url")
    title = data.get("title", "")
    subs = data.get("subs_links") or []
    json_data = data.get("json_data")

    if json_output and json_data is not None:
        console.print_json(data=json_data)
        return

    if download and url:
        _download_video(url, title, download_dir or config.get("download_dir") or ".", subs)
        return

    tmp = Path(os.environ.get("TMPDIR", os.environ.get("TEMP", "/tmp"))) / "nautilus_stream.txt"
    if url:
        tmp.write_text(url, encoding="utf-8")
    stream_panel(url or "", str(tmp))
    if link_only:
        info_text = Text()
        info_text.append("Copy with mouse or Ctrl+Shift+C", style="#8b949e")
        console.print()
        console.print(info_text)
        Prompt.ask("Press Enter to exit", default="")
        return
    if url:
        # Check for mpv before attempting to play
        has_mpv, mpv_err = check_dependency(config.get("player") or "mpv")
        if not has_mpv:
            err_msg(f"Player not found: {mpv_err}")
            err_msg("Install mpv or configure a different player in config")
            return None
        
        final_position = MediaPlayer.play(url, title, subs_links=subs if subs else None)
        return final_position


async def _handle_next_episode(scr, db, selected, seasons, episodes, current_season_num, current_episode_num, season_id, season_title, link_only, json_output, download, download_dir):
    """Handle 'Next Episode' prompt after watching an episode."""
    import questionary
    
    # Check if there's a next episode
    current_ep_index = current_episode_num - 1
    has_next_in_season = current_ep_index + 1 < len(episodes)
    has_next_season = current_season_num < len(seasons)
    
    if not has_next_in_season and not has_next_season:
        console.print()
        ok_msg(f"You've finished {selected.title}! 🎉")
        return None
    
    # Prompt for next episode
    console.print()
    console.print()
    
    choices = []
    if has_next_in_season:
        next_ep_num = current_episode_num + 1
        choices.append(f"→ Play Next Episode ({next_ep_num})")
    if has_next_season:
        choices.append(f"→ Next Season (Season {current_season_num + 1})")
    choices.append("✓ Exit")
    
    selection = await questionary.select(
        "Continue watching?",
        choices=choices,
        style=questionary.Style([
            ('qmark', 'fg:#58a6ff'),
            ('question', 'fg:#c9d1d9'),
            ('pointer', 'fg:#58a6ff bold'),
            ('highlighted', 'fg:#58a6ff bold'),
            ('selected', 'fg:#3fb9a2'),
            ('answer', 'fg:#79c0ff bold'),
            ('text', 'fg:#c9d1d9'),
        ])
    ).ask_async()
    
    if not selection or "Exit" in selection:
        return None
    
    # Clear screen for next episode
    console.clear()
    banner()
    set_context(selected.title)
    
    if "Next Episode" in selection:
        # Play next episode in same season
        next_ep = episodes[current_ep_index + 1]
        next_episode_id = next_ep["id"]
        next_episode_num = next_ep["number"]
        
        with console.status(status_msg("Loading next episode..."), spinner="dots"):
            data = await scr.get_stream_url_for_episode(selected, next_episode_id, current_season_num, next_episode_num)
        
        if not data:
            err_msg("Extraction failed.")
            return None
        
        section_title(f"{selected.title} · {season_title}", f"Episode {next_episode_num}")
        final_position = _show_and_maybe_play(data, link_only, json_output, download, download_dir)
        
        # Save history with actual position
        db.save_history(
            selected.id,
            selected.title,
            "tv",
            position=final_position or "00:00:00",
            season_id=season_id,
            episode_id=next_episode_id,
            season_title=season_title,
            episode_title=f"Episode {next_episode_num}",
            data_id=next_episode_id,
        )
        
        if link_only or json_output or download:
            return None
        
        # Recursive call for next episode
        return await _handle_next_episode(scr, db, selected, seasons, episodes, current_season_num, next_episode_num, season_id, season_title, link_only, json_output, download, download_dir)
    
    elif "Next Season" in selection:
        # Load next season
        next_season = seasons[current_season_num]
        next_season_id = next_season["id"]
        next_season_num = current_season_num + 1
        next_season_title = next_season["label"]
        
        set_context(next_season_title)
        
        with console.status(status_msg("Loading episodes..."), spinner="dots"):
            next_episodes = await scr.get_episodes(next_season_id)
        
        if not next_episodes:
            err_msg("Could not load episodes.")
            return None
        
        # Play first episode of next season
        first_ep = next_episodes[0]
        first_episode_id = first_ep["id"]
        first_episode_num = first_ep["number"]
        
        with console.status(status_msg("Loading stream..."), spinner="dots"):
            data = await scr.get_stream_url_for_episode(selected, first_episode_id, next_season_num, first_episode_num)
        
        if not data:
            err_msg("Extraction failed.")
            return None
        
        section_title(f"{selected.title} · {next_season_title}", f"Episode {first_episode_num}")
        final_position = _show_and_maybe_play(data, link_only, json_output, download, download_dir)
        
        # Save history with actual position
        db.save_history(
            selected.id,
            selected.title,
            "tv",
            position=final_position or "00:00:00",
            season_id=next_season_id,
            episode_id=first_episode_id,
            season_title=next_season_title,
            episode_title=f"Episode {first_episode_num}",
            data_id=first_episode_id,
        )
        
        if link_only or json_output or download:
            return None
        
        # Recursive call for next season's episodes
        return await _handle_next_episode(scr, db, selected, seasons, next_episodes, next_season_num, first_episode_num, next_season_id, next_season_title, link_only, json_output, download, download_dir)
    
    return None


async def run_search_flow(scr: FlixScraper, db: Database, link_only: bool, json_output: bool, query_from_args: str = "", download: bool = False, download_dir: str = ""):
    """Search → select media → movie play or TV season/episode → play."""
    clear_context()
    
    recent = db.get_recent()
    if recent:
        recent_text = Text()
        recent_text.append("Recent: ", style="#8b949e")
        recent_text.append(", ".join(r[0] for r in recent), style="#c9d1d9")
        console.print()
        console.print(recent_text)

    query_str = (query_from_args or "").strip()
    if not query_str:
        query_str = await prompt_text("Search")

    # Validate search query
    query_valid, query_error = validate_search_query(query_str)
    if not query_valid:
        err_msg(query_error)
        return None

    with console.status(status_msg("Searching..."), spinner="dots"):
        results = await scr.search(query_str)
    if not results:
        err_msg("No results found.")
        return None

    section_title("Search Results")
    # Compact selection - format function for display
    def format_result(idx, item):
        badge = "TV" if item.type == "tv" else "Movie"
        return f"{idx}  {item.title}  · {badge}"
    
    _, selected = await prompt_select_items("Select", results, format_result, allow_back=False)
    if selected is None:  # This shouldn't happen on first screen, but handle it
        return None

    # Clear console and show next step
    console.clear()
    banner()
    set_context(selected.title)

    if selected.type == "movie":
        with console.status(status_msg("Loading stream..."), spinner="dots"):
            data = await scr.get_movie_stream_data(selected)
        if data:
            if not link_only and not json_output and not download:
                # Play and get final position
                final_position = _show_and_maybe_play(data, link_only, json_output, download, download_dir)
                # Save history with actual position
                db.save_history(selected.id, selected.title, "movie", position=final_position or "00:00:00")
            else:
                # Just show link/json/download without playing
                db.save_history(selected.id, selected.title, "movie", position="00:00:00")
                _show_and_maybe_play(data, link_only, json_output, download, download_dir)
        else:
            err_msg("Extraction failed.")
        return None

    # TV: seasons → episodes → play
    while True:  # Loop to allow going back
        with console.status(status_msg("Loading seasons..."), spinner="dots"):
            seasons = await scr.get_seasons(selected.id)
        if not seasons:
            err_msg("Could not load seasons.")
            return None

        section_title(f"{selected.title}", f"Seasons", show_breadcrumb=True)
        _, chosen_season = await prompt_select_items(
            "Select season",
            seasons,
            lambda idx, s: f"{idx}  {s['label']}",
            allow_back=True
        )
        
        # If user selected Go Back, return to search results
        if chosen_season is None:
            return await run_search_flow(scr, db, link_only, json_output, query_str, download, download_dir)
        
        season_id = chosen_season["id"]
        season_num = chosen_season["number"]
        season_title = chosen_season["label"]

        # Clear and show next step
        console.clear()
        banner()
        set_context(season_title)

        with console.status(status_msg("Loading episodes..."), spinner="dots"):
            episodes = await scr.get_episodes(season_id)
        if not episodes:
            err_msg("Could not load episodes.")
            continue  # Go back to season selection

        section_title(f"{selected.title} · {chosen_season['label']}", f"{len(episodes)} episodes", show_breadcrumb=True)
        _, chosen_ep = await prompt_select_items(
            "Select episode",
            episodes,
            lambda idx, ep: f"{idx}  Episode {ep['number']}",
            allow_back=True
        )
        
        # If user selected Go Back, loop back to season selection
        if chosen_ep is None:
            console.clear()
            banner()
            set_context(selected.title)
            continue
        
        episode_id = chosen_ep["id"]
        episode_num = chosen_ep["number"]
        break  # Exit the while loop and continue with playback

    with console.status(status_msg("Loading stream...")):
        data = await scr.get_stream_url_for_episode(selected, episode_id, season_num, episode_num)

    if not data:
        err_msg("Extraction failed.")
        return None

    if link_only or json_output or download:
        # Save with 00:00:00 since we're not actually playing
        db.save_history(
            selected.id,
            selected.title,
            "tv",
            position="00:00:00",
            season_id=season_id,
            episode_id=episode_id,
            season_title=season_title,
            episode_title=f"Episode {episode_num}",
            data_id=episode_id,
        )
        _show_and_maybe_play(data, link_only, json_output, download, download_dir)
        return None
    
    # Play and get final position
    final_position = _show_and_maybe_play(data, link_only, json_output, download, download_dir)
    
    # Save history with actual position
    db.save_history(
        selected.id,
        selected.title,
        "tv",
        position=final_position or "00:00:00",
        season_id=season_id,
        episode_id=episode_id,
        season_title=season_title,
        episode_title=f"Episode {episode_num}",
        data_id=episode_id,
    )
    
    # Next Episode feature - ask if user wants to continue watching
    return await _handle_next_episode(scr, db, selected, seasons, episodes, season_num, episode_num, season_id, season_title, link_only, json_output, download, download_dir)


async def run_continue_flow(scr: FlixScraper, db: Database, link_only: bool, json_output: bool, download: bool = False, download_dir: str = ""):
    """Pick from history and resume (lobster --continue)."""
    history = db.get_history_list(limit=20)
    if not history:
        warn_msg("No history. Search first.")
        return None

    section_title("Continue Watching")
    # Compact selection for history
    def format_history(idx, h):
        title = h.get("title", "?")
        typ = h.get("media_type", "movie")
        prog = h.get("position", "00:00:00")
        
        if typ == "tv":
            st = h.get("season_title") or ""
            et = h.get("episode_title") or ""
            if st and et:
                prog = f"{st} · {et}"
            elif st or et:
                prog = st or et
        
        title_short = (title[:45] + "…") if len(title) > 45 else title
        return f"{idx}  {title_short}  · {typ.upper()}  · {prog}"
    
    _, entry = await prompt_select_items("Select entry", history, format_history)
    
    # Clear and show loading
    console.clear()
    banner()
    
    media_id = entry["media_id"]
    title = entry["title"]
    media_type = entry["media_type"]
    position = entry.get("position") or "00:00:00"
    season_id = entry.get("season_id") or ""
    episode_id = entry.get("episode_id") or ""
    season_title = entry.get("season_title") or ""
    episode_title = entry.get("episode_title") or ""
    data_id = entry.get("data_id") or ""

    selected = MediaItem(title=title, id=media_id, type=media_type, url="")

    if media_type == "movie":
        with console.status(status_msg("Resuming...")):
            data = await scr.get_movie_stream_data(selected)
        if data:
            if not link_only and not json_output and not download:
                final_position = MediaPlayer.play(
                    data["url"],
                    data["title"],
                    start=position if position != "00:00:00" else None,
                    subs_links=data.get("subs_links") or None,
                )
                # Update history with new position
                db.save_history(media_id, title, media_type, position=final_position or "00:00:00")
            else:
                _show_and_maybe_play(data, link_only, json_output, download, download_dir)
        else:
            err_msg("Extraction failed.")
        return None

    # TV: resume same episode
    with console.status(status_msg("Resuming...")):
        data = await scr.get_stream_url_for_episode(
            selected, data_id or episode_id, 0, 0
        )
    if not data:
        err_msg("Extraction failed.")
        return None
    # Fix title with S/E if we have season/episode in entry
    if not data.get("title") or "S0E0" in data.get("title", ""):
        data["title"] = f"{title} - {season_title} - {episode_title}"

    if not link_only and not json_output and not download:
        final_position = MediaPlayer.play(
            data["url"],
            data["title"],
            start=position if position != "00:00:00" else None,
            subs_links=data.get("subs_links") or None,
        )
        # Update history with new position
        db.save_history(
            media_id,
            title,
            media_type,
            position=final_position or "00:00:00",
            season_id=season_id,
            episode_id=episode_id,
            season_title=season_title,
            episode_title=episode_title,
            data_id=data_id,
        )
    else:
        _show_and_maybe_play(data, link_only, json_output, download, download_dir)
    return None


async def run():
    args = parse_args()
    _apply_cli_config(args)

    if args.edit:
        cfg_path = config.DEFAULT_CONFIG_PATH
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano"
        os.system(f"{editor} {cfg_path}")
        return

    banner()

    download = getattr(args, "download", None) is not None
    download_dir = (args.download if args.download else (config.get("download_dir") or ".")) if download else ""

    scr = FlixScraper()
    db = Database()
    try:
        if args.continue_watch:
            await run_continue_flow(scr, db, args.link, args.json, download, download_dir)
        else:
            query_str = " ".join(getattr(args, "query", []) or []).strip()
            await run_search_flow(scr, db, args.link, args.json, query_str, download, download_dir)
    finally:
        await scr.close()


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
