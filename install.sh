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

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi
echo "✓ Found pip3"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install --user -e .

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
    echo "   Install: pip3 install --user yt-dlp"
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
