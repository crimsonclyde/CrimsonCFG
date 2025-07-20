#!/bin/bash
# _________      _____                               __________________________
# __  ____/_________(_)______ _________________________  ____/__  ____/_  ____/
# _  /    __  ___/_  /__  __ `__ \_  ___/  __ \_  __ \  /    __  /_   _  / __  
# / /___  _  /   _  / _  / / / / /(__  )/ /_/ /  / / / /___  _  __/   / /_/ /  
# \____/  /_/    /_/  /_/ /_/ /_//____/ \____//_/ /_/\____/  /_/      \____/  
#
#
# Setup Script
# This script removes all traces of CrimsonCFG from the system
#
# ------------------------------------------------------------------------------------

# Exit on errors
set -e

##################
# Variables
##################
# Default install dir
INSTALL_DIR="/opt/CrimsonCFG"

# Try to read working_directory from local.yml if it exists
LOCAL_YML="$HOME/.config/com.crimson.cfg/local.yml"
if [ -f "$LOCAL_YML" ]; then
    # Extract working_directory using grep/sed/awk (YAML, so simple key: value)
    WD_LINE=$(grep '^working_directory:' "$LOCAL_YML" | head -n1)
    if [ -n "$WD_LINE" ]; then
        # Remove key and possible quotes/spaces
        WD_VALUE=$(echo "$WD_LINE" | sed "s/^working_directory:[ ]*//;s/[\"']//g")
        if [ -n "$WD_VALUE" ]; then
            INSTALL_DIR="$WD_VALUE"
        fi
    fi
fi

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
# Print ASCII art
print_status "\n$(figlet CrimsonCFG)\n"
print_status "Uninstall the entire application but doesn't touch the dependencies!"

# Check for root, re-exec with sudo if not
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;33m[INFO]\033[0m This script needs to run as root. Elevating with sudo..."
    exec sudo bash "$0" "$@"
fi

# Ask for confirmation
read -p "If you uninstall me, at least take me out to dinner first (y/n): " confirm
if [ "$confirm" != "y" ]; then
    print_error "Uninstall cancelled"
    exit 1
fi

# Remove the application
print_status "Removing application..."

# Remove INSTALL_DIR
if sudo rm -rf "$INSTALL_DIR/"; then
    print_success "Removed $INSTALL_DIR/"
else
    print_error "Failed to remove $INSTALL_DIR/"
fi

# Remove config directory
if sudo rm -rf ~/.config/com.crimson.cfg/; then
    print_success "Removed ~/.config/com.crimson.cfg/"
else
    print_error "Failed to remove ~/.config/com.crimson.cfg/"
fi

# Remove desktop entry
if sudo rm -f ~/.local/share/applications/com.crimson.cfg.desktop; then
    print_success "Removed ~/.local/share/applications/com.crimson.cfg.desktop"
else
    print_error "Failed to remove ~/.local/share/applications/com.crimson.cfg.desktop"
fi

print_success "CrimsonCFG has been uninstalled"
print_status "Thank you for using CrimsonCFG!"