#!/bin/bash
# Nautilus Installation Script for Linux/macOS
# Professional system-integrated installation using pipx

set -e

echo "🌊 NAUTILUS Installation Script"
echo "================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Detect installation method based on system
INSTALL_METHOD=""

# Check if pipx is available (BEST METHOD for CLI tools)
if command -v pipx &> /dev/null; then
    INSTALL_METHOD="pipx"
    echo "✓ Found pipx (recommended method)"
elif python3 -m pip --version &> /dev/null 2>&1; then
    echo "ℹ️  pipx not found, using pip with virtual environment"
    INSTALL_METHOD="pip"
else
    echo "❌ Neither pipx nor pip is available."
    echo ""
    echo "Please install pipx (recommended):"
    echo "  Ubuntu/Debian: sudo apt install pipx"
    echo "  macOS: brew install pipx"
    echo ""
    echo "Or install pip:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip python3-venv"
    exit 1
fi

echo ""
echo "📦 Installing Nautilus..."

if [ "$INSTALL_METHOD" = "pipx" ]; then
    # PROFESSIONAL METHOD: Use pipx for isolated, system-wide CLI tool
    pipx install -e .
    pipx ensurepath
    
    echo ""
    echo "✅ Installed via pipx (isolated environment)"
    echo "   Command available system-wide: nautilus"
    echo ""
    echo "ℹ️  To upgrade: pipx upgrade nautilus-stream"
    echo "ℹ️  To uninstall: pipx uninstall nautilus-stream"
    
else
    # FALLBACK: Use pip with user install
    # Create a local venv for the tool
    VENV_DIR="$HOME/.local/share/nautilus-venv"
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating isolated environment at $VENV_DIR..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Install into the venv
    "$VENV_DIR/bin/pip" install -e .
    
    # Create symlink in user's local bin
    mkdir -p "$HOME/.local/bin"
    ln -sf "$VENV_DIR/bin/nautilus" "$HOME/.local/bin/nautilus"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo ""
        echo "⚠️  Add to your shell profile (~/.bashrc or ~/.zshrc):"
        echo '   export PATH="$HOME/.local/bin:$PATH"'
        echo ""
        echo "Then run: source ~/.bashrc  (or restart terminal)"
    fi
    
    echo ""
    echo "✅ Installed in isolated environment"
    echo "   Virtual env: $VENV_DIR"
    echo "   Command: $HOME/.local/bin/nautilus"
fi

# Check for optional dependencies
echo ""
echo "🔍 Checking optional dependencies..."

if command -v mpv &> /dev/null; then
    echo "✓ mpv found"
else
    echo "⚠️  mpv not found (required for playback)"
    echo "   Install: sudo apt install mpv  (Ubuntu/Debian)"
    echo "            brew install mpv      (macOS)"
fi

if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg found"
else
    echo "⚠️  ffmpeg not found (optional, for downloads)"
    echo "   Install: sudo apt install ffmpeg  (Ubuntu/Debian)"
    echo "            brew install ffmpeg      (macOS)"
fi

if command -v yt-dlp &> /dev/null; then
    echo "✓ yt-dlp found"
else
    echo "⚠️  yt-dlp not found (optional, for fast downloads)"
    if [ "$INSTALL_METHOD" = "pipx" ]; then
        echo "   Install: pipx inject nautilus-stream yt-dlp"
        echo "   Or: pip install --user yt-dlp"
    else
        echo "   Install: pip install --user yt-dlp"
    fi
fi

if command -v aria2c &> /dev/null; then
    echo "✓ aria2c found"
else
    echo "ℹ️  aria2c not found (optional, for 10x faster downloads)"
    echo "   Install: sudo apt install aria2  (Ubuntu/Debian)"
    echo "            brew install aria2      (macOS)"
    echo "            snap install aria2c     (Snap)"
fi

echo ""
echo "✅ Installation complete!"
echo ""

# Remind user about PATH if using pipx
if [ "$INSTALL_METHOD" = "pipx" ]; then
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "⚠️  IMPORTANT: Run this command to activate nautilus:"
        echo "   source ~/.bashrc"
        echo ""
        echo "   Or open a new terminal window"
        echo ""
    fi
fi

echo "Usage:"
echo "  nautilus                    # Start interactive search"
echo "  nautilus 'Breaking Bad'     # Search directly"
echo "  nautilus -c                 # Continue watching"
echo "  nautilus -d                 # Download mode"
echo ""
echo "Configuration: nautilus_config.json in project directory"
echo ""
