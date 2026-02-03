# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-03

### Added
- 🎯 Full packaging support with `pyproject.toml`
- 📦 Automated installation scripts for Windows (`install.bat`) and Linux/macOS (`install.sh`)
- 🚀 CLI command `nautilus` - installable via pip
- 🔍 Dependency checking before operations (mpv, ffmpeg, yt-dlp, aria2c)
- 📝 CHANGELOG.md for tracking releases
- 📄 MIT License
- 🎨 Professional README with multiple installation methods
- ⚡ Ultra-fast downloads with yt-dlp + aria2c (5-10x faster)
- 📺 Subtitle embedding support (download with yt-dlp, mux with ffmpeg)
- 🎬 Interactive arrow-key navigation
- 💾 Watch history and continue watching
- 🌐 Multiple provider support (Vidcloud, UpCloud, etc.)
- 🎥 mpv integration for playback
- 📥 Download support with progress tracking
- 🔄 Resume playback from last position
- 🌍 Multi-language subtitle support
- 📊 Clean single-line download progress
- ⚙️ YAML configuration file support

### Fixed
- ❌ Removed invalid `--sub-file` option from yt-dlp
- 🔧 Fixed module import errors for CLI entry point
- 🧹 Cleaned up duplicate error handling
- 📦 Updated .gitignore for build artifacts and media files

### Changed
- 🎯 yt-dlp now primary downloader (was limited to non-subtitle downloads)
- 📝 Updated README config documentation from JSON to YAML format
- 🚀 Improved download speed with optimized yt-dlp + aria2c settings

## [Unreleased]

### Planned
- 🧪 Unit tests and CI/CD pipeline
- 🐳 Docker container support
- 🌐 Web interface option
- 📱 Mobile companion app
- 🔐 User authentication for multi-user setups

---

[1.0.0]: https://github.com/othmanordaski/Nautilus/releases/tag/v1.0.0
