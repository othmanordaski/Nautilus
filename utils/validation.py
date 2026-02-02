"""Input validation utilities for Nautilus."""
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse


def check_dependency(command: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a command-line dependency is available.
    
    Args:
        command: The command to check (e.g., 'mpv', 'ffmpeg', 'yt-dlp')
    
    Returns:
        (is_available, path_or_error)
    """
    path = shutil.which(command)
    if path:
        return True, path
    
    # Check for .exe variant on Windows
    if not path:
        exe_path = shutil.which(f"{command}.exe")
        if exe_path:
            return True, exe_path
    
    return False, f"{command} not found in PATH"


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate search query string.
    
    Returns:
        (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Search query cannot be empty"
    
    # Remove extra whitespace
    cleaned = " ".join(query.split())
    
    if len(cleaned) < 2:
        return False, "Search query must be at least 2 characters"
    
    if len(cleaned) > 200:
        return False, "Search query is too long (max 200 characters)"
    
    # Check for only special characters
    if re.match(r'^[^a-zA-Z0-9]+$', cleaned):
        return False, "Search query must contain letters or numbers"
    
    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format.
    
    Returns:
        (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "URL must include protocol (http:// or https://)"
        
        if parsed.scheme not in ['http', 'https']:
            return False, f"Invalid protocol: {parsed.scheme}. Use http:// or https://"
        
        if not parsed.netloc:
            return False, "URL must include a domain name"
        
        return True, None
    except Exception as e:
        return False, f"Invalid URL format: {e}"


def validate_download_path(path: str, filename: str = "test.mkv") -> Tuple[bool, Optional[str]]:
    """
    Validate download directory path and permissions.
    
    Returns:
        (is_valid, error_message)
    """
    if not path or not path.strip():
        return False, "Download path cannot be empty"
    
    try:
        dir_path = Path(path).resolve()
        
        # Check if path exists or parent exists for creation
        if not dir_path.exists():
            if not dir_path.parent.exists():
                return False, f"Parent directory does not exist: {dir_path.parent}"
            # Try to create it
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                return False, f"Permission denied: Cannot create directory {dir_path}"
            except Exception as e:
                return False, f"Cannot create directory: {e}"
        
        # Check if it's a directory
        if not dir_path.is_dir():
            return False, f"Path is not a directory: {dir_path}"
        
        # Check write permissions by creating a test file
        test_file = dir_path / f".nautilus_write_test_{filename}"
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            return False, f"Permission denied: Cannot write to {dir_path}"
        except Exception as e:
            return False, f"Cannot write to directory: {e}"
        
        return True, None
    except Exception as e:
        return False, f"Invalid path: {e}"


def check_disk_space(path: str, required_mb: int = 500) -> Tuple[bool, Optional[str]]:
    """
    Check if there's enough disk space for download.
    
    Args:
        path: Directory path to check
        required_mb: Minimum required space in MB (default 500MB)
    
    Returns:
        (has_space, warning_message)
    """
    try:
        dir_path = Path(path).resolve()
        
        # Ensure directory exists
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Get disk usage
        usage = shutil.disk_usage(dir_path)
        free_mb = usage.free / (1024 * 1024)
        
        if free_mb < required_mb:
            free_gb = free_mb / 1024
            required_gb = required_mb / 1024
            return False, f"Insufficient disk space: {free_gb:.1f}GB available, {required_gb:.1f}GB recommended"
        
        # Warning if less than 1GB
        if free_mb < 1024:
            return True, f"Low disk space: {free_mb:.0f}MB available"
        
        return True, None
    except Exception as e:
        # Don't fail on disk check errors, just warn
        return True, f"Could not check disk space: {e}"


def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate filename for filesystem compatibility.
    
    Returns:
        (is_valid, error_message)
    """
    if not filename or not filename.strip():
        return False, "Filename cannot be empty"
    
    # Check for invalid characters (Windows + Unix)
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    if re.search(invalid_chars, filename):
        return False, "Filename contains invalid characters"
    
    # Check for reserved names (Windows)
    reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved:
        return False, f"Filename '{filename}' uses a reserved system name"
    
    # Check length (max 255 for most filesystems)
    if len(filename) > 255:
        return False, "Filename is too long (max 255 characters)"
    
    return True, None


def sanitize_filename(title: str, max_length: int = 200) -> str:
    """
    Sanitize title for use as filename.
    
    Args:
        title: Original title
        max_length: Maximum filename length
    
    Returns:
        Safe filename string
    """
    # Remove invalid characters
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
    
    # Replace multiple spaces with single space
    safe = ' '.join(safe.split())
    
    # Trim to max length
    if len(safe) > max_length:
        safe = safe[:max_length].rsplit(' ', 1)[0]  # Break at word boundary
    
    # Ensure not empty
    return safe.strip() or "nautilus_download"


def validate_provider_name(provider: str) -> Tuple[bool, Optional[str]]:
    """
    Validate provider name format.
    
    Returns:
        (is_valid, error_message)
    """
    if not provider or not provider.strip():
        return False, "Provider name cannot be empty"
    
    # Provider should be alphanumeric with optional spaces/dashes
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\s\-]*$', provider):
        return False, "Provider name must be alphanumeric (spaces and dashes allowed)"
    
    if len(provider) > 50:
        return False, "Provider name is too long (max 50 characters)"
    
    return True, None


def validate_quality(quality: str) -> Tuple[bool, Optional[str]]:
    """
    Validate video quality setting.
    
    Returns:
        (is_valid, error_message)
    """
    valid_qualities = ['360', '480', '720', '1080', '1440', '2160', '4k']
    
    if not quality or not quality.strip():
        return False, "Quality cannot be empty"
    
    quality_lower = quality.lower().strip()
    
    if quality_lower not in valid_qualities:
        return False, f"Invalid quality: {quality}. Valid options: {', '.join(valid_qualities)}"
    
    return True, None
