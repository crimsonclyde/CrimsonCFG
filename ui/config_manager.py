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
        
        # Load local configuration (user-specific)
        local_config = {}
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        if not local_file.exists():
            # Create an empty local.yml if it doesn't exist
            with open(local_file, 'w') as f:
                yaml.safe_dump({}, f)
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
                "ansible_folder": merged_config.get("ansible_folder", f"/home/{system_user}/Ansible"),
                "inventory_file": f"/home/{system_user}/Ansible/hosts.ini",
                "log_directory": f"/home/{system_user}/Ansible/log",
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
                scanner = PlaybookScanner()
                success = scanner.generate_config("conf/gui_config.json")
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
        config_file = Path("conf/gui_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                json_config = json.load(f)
                return json_config.get("categories", {})
        else:
            return {} 