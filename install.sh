#!/bin/bash
# _________      _____                               __________________________
# __  ____/_________(_)______ _________________________  ____/__  ____/_  ____/
# _  /    __  ___/_  /__  __ `__ \_  ___/  __ \_  __ \  /    __  /_   _  / __  
# / /___  _  /   _  / _  / / / / /(__  )/ /_/ /  / / / /___  _  __/   / /_/ /  
# \____/  /_/    /_/  /_/ /_/ /_//____/ \____//_/ /_/\____/  /_/      \____/  
#
#
# Installation Script
# This script installs all dependencies and sets up CrimsonCFG
#
# ------------------------------------------------------------------------------------

# Exit on errors
set -e

##################
# Variables
##################
REPO_URL="https://github.com/crimsonclyde/CrimsonCFG.git"
REPO_NAME="CrimsonCFG"
INSTALL_DIR="/opt"

##################
# Functions
##################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}┌───────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│ [INFO]   ${NC}$1"
    echo -e "${BLUE}└───────────────────────────────────────────────┘${NC}"
}

print_success() {
    echo -e "${GREEN}┌───────────────────────────────────────────────┐${NC}"
    echo -e "${GREEN}│ [SUCCESS]${NC} $1"
    echo -e "${GREEN}└───────────────────────────────────────────────┘${NC}"
}

print_warning() {
    echo -e "${YELLOW}┌───────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│ [WARNING]${NC} $1"
    echo -e "${YELLOW}└───────────────────────────────────────────────┘${NC}"
}

print_error() {
    echo -e "${RED}┌───────────────────────────────────────────────┐${NC}"
    echo -e "${RED}│ [ERROR]  ${NC}$1"
    echo -e "${RED}└───────────────────────────────────────────────┘${NC}"
}

##################
# Main
##################

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root. Please run as a regular user."
    exit 1
fi

# Print ASCII art
print_status "\n$(figlet CrimsonCFG)\n"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install system dependencies
print_status "Installing dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    python3-yaml \
    python3-ruamel.yaml \
    ansible \
    git \
    curl \
    wget

# Create necessary directories
print_status "Setting up directories..."
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.local/share/icons/hicolor/48x48/apps"
mkdir -p "$HOME/.local/share/icons/hicolor/64x64/apps"
mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"
mkdir -p "$HOME/.local/share/icons/hicolor/256x256/apps"

# Install application icon
if [ -f "files/com.crimson.cfg.dock.png" ]; then
    print_status "Installing application icon..."
    cp "files/com.crimson.cfg.dock.png" "$HOME/.local/share/icons/hicolor/48x48/apps/com.crimson.cfg.png"
    cp "files/com.crimson.cfg.dock.png" "$HOME/.local/share/icons/hicolor/64x64/apps/com.crimson.cfg.png"
    cp "files/com.crimson.cfg.dock.png" "$HOME/.local/share/icons/hicolor/128x128/apps/com.crimson.cfg.png"
    cp "files/com.crimson.cfg.dock.png" "$HOME/.local/share/icons/hicolor/256x256/apps/com.crimson.cfg.png"
    
    # Update icon cache
    print_status "Updating icon cache..."
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
else
    print_warning "Icon file not found. Application will use default icon."
fi

# Install desktop entry
print_status "Installing desktop entry..."
# Create desktop file with correct path
cat > "$HOME/.local/share/applications/com.crimson.cfg.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=CrimsonCFG
Comment=App & Customization Selector
Exec=python3 /opt/CrimsonCFG/crimson.cfg.main.py
Icon=com.crimson.cfg
Categories=System;Settings;
Terminal=false
StartupNotify=true
EOF

# Update desktop database
print_status "Updating desktop database..."
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

# Clear caches
print_status "Clearing caches..."
rm -rf "$HOME/.cache/icon-cache.kcache" 2>/dev/null || true
rm -rf "$HOME/.cache/gnome-icon-cache" 2>/dev/null || true
rm -rf "$HOME/.cache/gnome-shell" 2>/dev/null || true
rm -rf "$HOME/.cache/gnome-session" 2>/dev/null || true
rm -rf "$HOME/.cache/gnome-control-center" 2>/dev/null || true

# Force desktop environment refresh
if command -v gsettings &> /dev/null; then
    print_status "Refreshing desktop environment..."
    gsettings set org.gnome.desktop.interface enable-hot-corners false 2>/dev/null || true
    gsettings set org.gnome.desktop.interface enable-hot-corners true 2>/dev/null || true
fi

# Add to favorites (GNOME)
if command -v gsettings &> /dev/null; then
    print_status "Adding to favorites..."
    # Get current favorites
    current_favorites=$(gsettings get org.gnome.shell favorite-apps 2>/dev/null || echo "[]")
    
    # Check if already in favorites
    if [[ ! "$current_favorites" == *"com.crimson.cfg.desktop"* ]]; then
        # Add to favorites
        new_favorites=$(echo "$current_favorites" | sed 's/]$/, "com.crimson.cfg.desktop"]/')
        gsettings set org.gnome.shell favorite-apps "$new_favorites" 2>/dev/null || true
        print_success "Added CrimsonCFG to favorites"
    else
        print_status "CrimsonCFG is already in favorites"
    fi
fi

print_success "Installation completed successfully!"
print_status "\n --------------------------------------------------------------------------------------\n Options:\n  - Launch CrimsonCFG from the Applications menu\n  - Find it in your favorites/dock\n  - Run it directly with: python3 $SCRIPT_DIR/crimson.cfg.main.py\n --------------------------------------------------------------------------------------"