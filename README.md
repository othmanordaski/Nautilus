# 🌊 NAUTILUS

<div align="center">

**航海** · _kōkai_ · voyage

*A Japanese minimalist media streaming engine*

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: zen](https://img.shields.io/badge/code%20style-zen-blueviolet.svg)](https://github.com/othmanordaski/Nautilus)

</div>

---

## ✨ Philosophy

Nautilus embodies the principles of **和 (wa - harmony)**:

- **Ma (間)** - Embrace negative space, let content breathe
- **Kanso (簡素)** - Simplicity without sacrifice
- **Shibui (渋い)** - Subtle, unobtrusive elegance
- **Seijaku (静寂)** - Stillness and calm in motion

## 🎯 Features

- 🎬 **Seamless Streaming** - Movies and TV shows with one command
- ⌨️ **Arrow Key Navigation** - Intuitive interface, no number typing
- 🎨 **Minimalist UI** - Japanese-inspired design with indigo accents
- 📍 **Breadcrumb Navigation** - Always know where you are
- 💾 **Watch History** - Continue where you left off
- 🎥 **Multiple Providers** - Vidcloud, UpCloud, and more
- 📥 **Download Support** - Save videos with ffmpeg
- 🔄 **Resume Playback** - Pick up from last position
- 🌐 **Subtitle Support** - Multiple languages available

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **mpv player** (for playback)
- **ffmpeg** (optional, for downloads)

### Installation

```bash
# Clone the repository
git clone https://github.com/othmanordaski/Nautilus.git
cd Nautilus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Nautilus
python app.py
```

## 📖 Usage

### Basic Search
```bash
python app.py
# Follow the prompts: Search → Select → Watch
```

### With Query
```bash
python app.py dexter
```

### Continue Watching
```bash
python app.py -c
```

### Get Stream Link Only
```bash
python app.py -l
```

### Download Video
```bash
python app.py -d
# Or specify path
python app.py -d ~/Downloads
```

### Advanced Options
```bash
python app.py -p UpCloud -q 720 -n  # Provider, quality, no subs
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate options |
| `↵` | Select/Confirm |
| `^C` | Cancel/Exit |

## 🎨 UI Showcase

```
            N A U T I L U S
              航 海  ·  v1.0
──────────────────────────────────

  → Search Results
──────────────────────────────────
  ↑↓ navigate  ·  ↵ select  ·  ^C cancel

→ Select
  ◦  1    Dexter: Resurrection    · TV
  ◦  2    Dexter                  · TV
  ◦  3    Dexter's Laboratory     · TV
```

## 🛠️ Configuration

Edit `nautilus_config.json` or use `python app.py -e`:

```json
{
  "base_url": "https://flixhq.to",
  "decrypt_api": "https://dec.eatmynerds.live",
  "player": "mpv",
  "provider": "Vidcloud",
  "quality": "1080",
  "subs_language": "english",
  "history_db": "nautilus.db",
  "watchlater_dir": "/tmp/nautilus_watchlater",
  "download_dir": "."
}
```

## 📋 Command Line Options

```
python app.py [OPTIONS] [QUERY]

Options:
  -c, --continue         Continue from history
  -l, --link            Only print stream URL (for VLC)
  -j, --json            Output JSON and exit
  -p, --provider        Provider (default: Vidcloud)
  -q, --quality         Quality (1080, 720, etc.)
  -n, --no-subs         Disable subtitles
  -d, --download [PATH] Download video
  -e, --edit            Edit config file
```

## 🏗️ Architecture

```
Nautilus/
├── app.py              # Main application flow
├── ui.py               # Japanese minimalist UI
├── core/
│   ├── scraper.py      # Web scraping logic
│   ├── player.py       # mpv integration
│   └── database.py     # SQLite history
├── models/
│   └── media.py        # Data models
└── utils/
    ├── config.py       # Configuration management
    └── theme.py        # Design system
```

## 🎨 Design System

### Color Palette
- **Indigo** (`#5c6bc0`) - Primary accent
- **Grey70** (`#b3b3b3`) - Primary text
- **Grey50** (`#808080`) - Secondary text
- **Grey35** (`#595959`) - Muted elements
- **Sakura** (`#e8b4b8`) - Success states
- **Vermillion** (`#d45d49`) - Errors

### Typography
- Monospace fonts for consistency
- Generous spacing (ma - negative space)
- Subtle separators: `·` `→` `◦`

## 🤝 Contributing

Contributions are welcome! Please follow the zen principles:

1. Keep it simple
2. Embrace negative space
3. Maintain the aesthetic
4. Test thoroughly

```bash
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
git commit -m "feat: Add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open a Pull Request
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by **Lobster** - The original media streaming CLI
- **Rich** - Beautiful terminal formatting
- **Questionary** - Elegant prompts
- Japanese design philosophy - Ma, Kanso, Shibui, Seijaku

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/othmanordaski/Nautilus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/othmanordaski/Nautilus/discussions)

---

<div align="center">

**Made with 和 (harmony) and ❤️**

*"Simplicity is the ultimate sophistication"* - Leonardo da Vinci

</div>
