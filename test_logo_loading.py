#!/usr/bin/env python3
"""
Test script to verify logo loading logic
"""

import os
import yaml
from pathlib import Path

def test_logo_loading():
    """Test the logo loading logic"""
    
    # Test 1: Check if default icon exists
    working_dir = "/opt/CrimsonCFG"
    default_icon = os.path.join(working_dir, 'files', 'app', 'com.crimson.cfg.icon.png')
    print(f"Test 1: Checking if default icon exists at {default_icon}")
    print(f"Result: {os.path.exists(default_icon)}")
    
    # Test 2: Check local config
    config_dir = Path.home() / ".config/com.crimson.cfg"
    local_file = config_dir / "local.yml"
    print(f"\nTest 2: Checking local config at {local_file}")
    print(f"Local config exists: {local_file.exists()}")
    
    if local_file.exists():
        try:
            with open(local_file, 'r') as f:
                local_config = yaml.safe_load(f) or {}
            app_logo = local_config.get('app_logo', '')
            print(f"App logo from config: '{app_logo}'")
            
            if app_logo and os.path.exists(app_logo):
                print(f"Custom logo exists: {os.path.exists(app_logo)}")
            else:
                print("No custom logo or custom logo doesn't exist, should use default")
        except Exception as e:
            print(f"Error reading local config: {e}")
    
    # Test 3: Simulate the fallback logic
    print(f"\nTest 3: Simulating fallback logic")
    
    # Get logo path from config
    logo_path = ''
    if local_file.exists():
        try:
            with open(local_file, 'r') as f:
                local_config = yaml.safe_load(f) or {}
            logo_path = local_config.get('app_logo', '')
        except Exception:
            logo_path = ''
    
    # Check if custom logo exists
    logo_loaded = False
    if logo_path and os.path.exists(logo_path):
        print(f"Custom logo would be loaded: {logo_path}")
        logo_loaded = True
    else:
        print("Custom logo not available, checking default...")
        
        # Try default icon
        if os.path.exists(default_icon):
            print(f"Default icon would be loaded: {default_icon}")
            logo_loaded = True
        elif os.path.exists('/opt/CrimsonCFG/files/app/com.crimson.cfg.icon.png'):
            print("Default icon would be loaded: /opt/CrimsonCFG/files/app/com.crimson.cfg.icon.png")
            logo_loaded = True
        else:
            print("No logo would be loaded")
    
    print(f"\nFinal result: Logo would be loaded: {logo_loaded}")

if __name__ == "__main__":
    test_logo_loading() 