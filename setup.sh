#!/bin/bash

set -e

echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y git curl

echo "Configuring git..."
read -p "Enter your git username: " gituser
git config --global user.name "$gituser"

read -p "Enter your git email: " gitemail
git config --global user.email "$gitemail"

echo "Creating ~/Ansible directory..."
mkdir -p ~/Ansible
cd ~/Ansible

REPO_URL="https://github.com/YOUR_USERNAME/YOUR_REPO.git"
REPO_NAME="YOUR_REPO"

if [ ! -d "$REPO_NAME" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL"
else
    echo "Repository already exists, pulling latest changes..."
    cd "$REPO_NAME"
    git pull
    cd ..
fi

cd "$REPO_NAME"

echo "Running test-install.sh..."
bash test-install.sh
