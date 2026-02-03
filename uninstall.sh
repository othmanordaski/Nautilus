#!/bin/bash
# Nautilus Uninstall Script

echo "🌊 NAUTILUS Uninstall Script"
echo "============================"
echo ""

# Check if installed via pipx
if command -v pipx &> /dev/null && pipx list | grep -q "nautilus-stream"; then
    echo "📦 Removing Nautilus (pipx installation)..."
    pipx uninstall nautilus-stream
    echo "✅ Uninstalled successfully"
    
# Check if installed via pip user
elif [ -f "$HOME/.local/bin/nautilus" ]; then
    echo "📦 Removing Nautilus (pip installation)..."
    
    # Remove symlink
    rm -f "$HOME/.local/bin/nautilus"
    
    # Remove virtual environment
    VENV_DIR="$HOME/.local/share/nautilus-venv"
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi
    
    echo "✅ Uninstalled successfully"
    
else
    echo "⚠️  Nautilus installation not found"
    echo ""
    echo "Manual cleanup (if needed):"
    echo "  - Remove: $HOME/.local/bin/nautilus"
    echo "  - Remove: $HOME/.local/share/nautilus-venv"
    echo "  - Config: $HOME/.config/nautilus/"
    echo "  - Database: $HOME/.local/share/nautilus.db"
fi

# Ask about config and data
echo ""
read -p "Do you want to remove config and database? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.config/nautilus"
    rm -f "$HOME/.local/share/nautilus.db"
    rm -f "nautilus.db"
    echo "✅ Removed config and database"
fi

echo ""
echo "Uninstall complete. Thank you for using Nautilus! 🌊"
