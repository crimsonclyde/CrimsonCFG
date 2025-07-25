#!/bin/bash
# _________      _____                               __________________________
# __  ____/_________(_)______ _________________________  ____/__  ____/_  ____/
# _  /    __  ___/_  /__  __ `__ \_  ___/  __ \_  __ \  /    __  /_   _  / __  
# / /___  _  /   _  / _  / / / / /(__  )/ /_/ /  / / / /___  _  __/   / /_/ /  
# \____/  /_/    /_/  /_/ /_/ /_//____/ \____//_/ /_/\____/  /_/      \____/  
#
#
# Setup Script
# This script sets up the environment and clones CrimsonCFG repository
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

print_status "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y git curl figlet

print_status "Configuring git..."

# Check for existing global git username
gituser=$(git config --global user.name || true)
if [ -z "$gituser" ]; then
    echo -en "${BLUE}│${NC} Enter your git username: "
    read gituser
    git config --global user.name "$gituser"
else
    echo -e "${BLUE}│${NC} Using existing git username: $gituser"
fi

# Check for existing global git email
gitemail=$(git config --global user.email || true)
if [ -z "$gitemail" ]; then
    echo -en "${BLUE}│${NC} Enter your git email: "
    read gitemail
    git config --global user.email "$gitemail"
else
    echo -e "${BLUE}│${NC} Using existing git email: $gitemail"
fi

print_status "Creating $INSTALL_DIR directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d "$REPO_NAME" ]; then
    print_status "Cloning repository..."
    # Clone the repository
    sudo git clone "$REPO_URL" "$INSTALL_DIR/$REPO_NAME"

    # Set permissions so all users can run the app
    print_status "Setting permissions on $INSTALL_DIR/$REPO_NAME..."
    sudo chown -R root:root "$INSTALL_DIR/$REPO_NAME"
    sudo chmod -R a+rX "$INSTALL_DIR/$REPO_NAME"
else
    print_status "Repository already exists, pulling latest changes..."
    cd "$REPO_NAME"
    git pull
    cd ..
fi

cd "$INSTALL_DIR/$REPO_NAME"
print_status "Current directory: $(pwd)"

# Determine working_directory from YAML config (local overrides global)
WORKING_DIRECTORY=$(python3 -c '
import yaml
from pathlib import Path
import os
config_dir = os.path.expanduser("~/.config/com.crimson.cfg")
local = Path(config_dir) / "local.yml"
if local.exists():
    with open(local) as f:
        cfg = yaml.safe_load(f) or {}
        if "working_directory" in cfg:
            print(cfg["working_directory"]); exit()
print("/opt/CrimsonCFG")  # fallback
')

# Use $WORKING_DIRECTORY for any playbook directory setup below

print_status "Making installer executable..."
sudo chmod +x install.sh

print_status "Running installer..."
bash install.sh
