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
# Load local.yml
# Determine the real user (not root) and their home directory
REAL_USER="${SUDO_USER:-$USER}"
REAL_USER_HOME=$(eval echo "~$REAL_USER")
LOCAL_YML="$REAL_USER_HOME/.config/com.crimson.cfg/local.yml"
USER_HOME=""
WORKING_DIRECTORY=""

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

load_local_yml() {
if [ -f "$LOCAL_YML" ]; then
    USER_HOME=$(grep -E '^user_home:' "$LOCAL_YML" | awk '{print $2}' | sed 's/^"//;s/"$//')
    if [ -z "$USER_HOME" ]; then
        print_warning "user_home not set in local.yml. Defaulting to /home/$(logname)"
        USER_HOME="/home/$(logname)"
    fi
    WORKING_DIRECTORY=$(grep -E '^working_directory:' "$LOCAL_YML" | awk '{print $2}' | sed 's/^"//;s/"$//')
    if [ -z "$WORKING_DIRECTORY" ]; then
        print_warning "working_directory not set in local.yml."
    fi
else
    print_warning "local.yml not found. Defaulting to /home/$(logname)"
    USER_HOME="/home/$(logname)"
fi
}

validate_vars() {
    if [ -z "$USER_HOME" ]; then
        print_error "USER_HOME is empty. Aborting to prevent dangerous operations."
        exit 1
    fi
    if [ -z "$WORKING_DIRECTORY" ]; then
        print_error "WORKING_DIRECTORY is empty. Aborting to prevent dangerous operations."
        exit 1
    fi
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

# Load local.yml (we need that before we uninstall anything)
load_local_yml

# Validate critical variables before proceeding
validate_vars

# Remove the application
print_status "Removing application..."

INSTALL_DIR="/opt/CrimsonCFG"

if [ -n "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "/" ] && [ -d "$INSTALL_DIR" ]; then
    if sudo rm -rf "$INSTALL_DIR/"; then
        print_success "Removed $INSTALL_DIR/"
    else
        print_error "Failed to remove $INSTALL_DIR/"
    fi
else
    print_warning "INSTALL_DIR is not set correctly or does not exist. Skipping."
fi

# Remove config directory
if [ -d "$USER_HOME/.config/com.crimson.cfg/" ]; then
    if sudo rm -r "$USER_HOME/.config/com.crimson.cfg/"; then
        print_success "Removed $USER_HOME/.config/com.crimson.cfg/"
    else
        print_error "Failed to remove $USER_HOME/.config/com.crimson.cfg/"
    fi
else
    print_warning "$USER_HOME/.config/com.crimson.cfg/ does not exist. Skipping."
fi

# Remove desktop entry
if [ -f "$USER_HOME/.local/share/applications/com.crimson.cfg.desktop" ]; then
    if sudo rm -f "$USER_HOME/.local/share/applications/com.crimson.cfg.desktop"; then
        print_success "Removed $USER_HOME/.local/share/applications/com.crimson.cfg.desktop"
    else
        print_error "Failed to remove $USER_HOME/.local/share/applications/com.crimson.cfg.desktop"
    fi
else
    print_warning "$USER_HOME/.local/share/applications/com.crimson.cfg.desktop does not exist. Skipping."
fi

print_success "CrimsonCFG has been uninstalled"
print_status "Thank you for using CrimsonCFG!"