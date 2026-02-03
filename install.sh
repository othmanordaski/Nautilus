#!/bin/bash
# Nautilus Installation Script for Linux/macOS
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

# Check for pip module (more reliable than checking pip command)
if python3 -m pip --version &> /dev/null; then
    echo "✓ Found pip module"
    PIP_CMD="python3 -m pip"
else
    echo "❌ pip module is not installed."
    echo "   Installing pip..."
    python3 -m ensurepip --user || {
        echo "   Failed to install pip automatically."
        echo "   Please install manually:"
        echo "     Ubuntu/Debian: sudo apt install python3-pip"
        echo "     macOS: brew install python3"
        exit 1
    }
    PIP_CMD="python3 -m pip"
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
$PIP_CMD install --user -e .

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
    echo "   Install: $PIP_CMD install --user yt-dlp"
fi

if command -v aria2c &> /dev/null; then
    echo "✓ aria2c found"
else
    echo "ℹ️  aria2c not found (optional, for 10x faster downloads)"
    echo "   Install: sudo apt install aria2  (Ubuntu/Debian)"
    echo "            brew install aria2      (macOS)"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  nautilus                    # Start interactive search"
echo "  nautilus 'Breaking Bad'     # Search directly"
echo "  nautilus -c                 # Continue watching"
echo "  nautilus -d                 # Download mode"
echo ""
echo "Configuration: ~/.config/nautilus/config.yaml"
echo ""
