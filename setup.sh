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
echo -en "${BLUE}│${NC} Enter your git username: "
read gituser
git config --global user.name "$gituser"

echo -en "${BLUE}│${NC} Enter your git email: "
read gitemail
git config --global user.email "$gitemail"

print_status "Creating $INSTALL_DIR directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d "$REPO_NAME" ]; then
    print_status "Cloning repository..."
    git clone "$REPO_URL"
else
    print_status "Repository already exists, pulling latest changes..."
    cd "$REPO_NAME"
    git pull
    cd ..
fi

cd "$REPO_NAME"

print_status "Making installer executable..."
chmod +x install.sh

print_status "Running installer..."
bash install.sh
