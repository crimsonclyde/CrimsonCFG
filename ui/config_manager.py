#!/usr/bin/env python3
"""
CrimsonCFG Configuration Manager
Handles loading and managing configuration files
"""

import json
import yaml
import getpass
from pathlib import Path
from typing import Dict
import shutil
import os

# Import the playbook scanner
try:
    from functions.playbook_scanner import PlaybookScanner  # type: ignore
    print("PlaybookScanner imported successfully")
except ImportError as e:
    # Fallback if scanner module is not available
    print(f"PlaybookScanner import failed: {e}")
    PlaybookScanner = None

class ConfigManager:
    def __init__(self):
        self.debug = False  # Will be set by main window
        
    def load_config(self) -> Dict:
        """Load configuration from YAML files"""
        # Load global configuration
        all_config = {}
        all_file = Path("group_vars/all.yml")
        if all_file.exists():
            with open(all_file, 'r') as f:
                all_config = yaml.safe_load(f) or {}
        
        # Load local configuration (user-specific overrides)
        local_config = {}
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial local.yml if it doesn't exist
        if not local_file.exists():
            system_user = getpass.getuser()
            initial_local_config = {
                # User
                "user": system_user,
                "user_home": f"/home/{system_user}",
                "debug": 0,
                "working_directory": "/opt/CrimsonCFG",
                # Corporate Identity (CI)
                "app_name": "CrimsonCFG",
                "app_subtitle": "App &amp; Customization Selector",
                "background_color": "#181a20",
                # Basics 
                "apt_packages": [
                    "btop",
                    "mc",
                    "python3-venv",
                    "python3-tk",
                    "python3-psutil",
                    "libfuse2",
                    "gnome-tweaks",
                    "vlc",
                    "gufw",
                    "syncthing",
                    "syncthingtray",
                    "krita",
                    "filezilla",
                    "fuse3",
                    "nautilus",
                    "software-properties-common",
                    "flameshot"
                ],
                "snap_packages": [
                    "bitwarden"
                ],
                "pinned_apps": [
                    "chromium_chromium.desktop",
                    "codium_codium.desktop",
                    "nautilus.desktop",
                    "gnome-terminal.desktop",
                    "bitwarden_bitwarden.desktop",
                    "signal-desktop.desktop",
                    "gnome-boxes.desktop"
                ],
                # GIT
                "git_email": os.environ.get("GIT_EMAIL", "user@example.com"),
                "git_username": os.environ.get("GIT_USERNAME", system_user),
                # SSH
                "ssh_private_key_name": "id_rsa",
                "ssh_public_key_name": "id_rsa.pub",
                "ssh_private_key_content": "",
                "ssh_public_key_content": "",
                "ssh_config_content": "",
                # Browser
                "chromium_homepage_url": ""
            }
            with open(local_file, 'w') as f:
                yaml.safe_dump(initial_local_config, f, default_flow_style=False, allow_unicode=True)
            if self.debug:
                print(f"Created initial local.yml at {local_file}")
        
        if local_file.exists():
            with open(local_file, 'r') as f:
                local_config = yaml.safe_load(f) or {}
        
        # Merge configurations (local overrides global)
        merged_config = {**all_config, **local_config}
        
        # Get actual system user
        system_user = getpass.getuser()
        
        # Convert to expected format
        config = {
            "categories": self.load_categories_from_yaml(),
            "settings": {
                "default_user": system_user,
                "working_directory": merged_config.get("working_directory", "/opt/CrimsonCFG"),
                "inventory_file": f"/opt/CrimsonCFG/hosts.ini",
                "log_directory": f"/opt/CrimsonCFG/log",
                "debug": merged_config.get("debug", 0),
                "git_username": merged_config.get("git_username", system_user),
                "git_email": merged_config.get("git_email", f"{system_user}@example.com")
            }
        }
        return config
            
    def regenerate_gui_config(self):
        """Regenerate gui_config.json from playbook metadata"""
        if self.debug:
            print("Regenerating GUI config from playbooks...")
        try:
            if PlaybookScanner is not None:
                config_dir = Path.home() / ".config/com.crimson.cfg"
                user_gui_config = config_dir / "gui_config.json"
                if not config_dir.exists():
                    config_dir.mkdir(parents=True, exist_ok=True)
                success = PlaybookScanner().generate_config(str(user_gui_config))
                if success:
                    if self.debug:
                        print("GUI config regenerated successfully")
                    # Reload the config
                    return self.load_config()
                else:
                    if self.debug:
                        print("Failed to regenerate GUI config")
            else:
                if self.debug:
                    print("PlaybookScanner not available, skipping config regeneration")
        except Exception as e:
            if self.debug:
                print(f"Error regenerating GUI config: {e}")
        return None
            
    def load_categories_from_yaml(self) -> Dict:
        """Load categories from gui_config.json (keeping the GUI structure separate)"""
        import shutil
        config_dir = Path.home() / ".config/com.crimson.cfg"
        user_gui_config = config_dir / "gui_config.json"
        default_gui_config = Path("conf/gui_config.json")
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        if not user_gui_config.exists() and default_gui_config.exists():
            shutil.copy(default_gui_config, user_gui_config)
        if user_gui_config.exists():
            with open(user_gui_config, 'r') as f:
                json_config = json.load(f)
                return json_config.get("categories", {})
        else:
            return {} 