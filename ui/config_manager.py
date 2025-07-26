#!/usr/bin/env python3
"""
CrimsonCFG Configuration Manager
Handles loading and managing configuration files
"""

import json
from ruamel.yaml import YAML
import getpass
from pathlib import Path
from typing import Dict
import shutil
import os
from jinja2 import Template
from . import external_repo_manager

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
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        
    def load_config(self) -> Dict:
        """Load configuration from YAML files"""
        # Load local configuration (user-specific overrides)
        local_config = {}
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        
        if not local_file.exists():
            # Load template and render with variables
            template_file = Path("templates/local.yml.j2")
            if template_file.exists():
                with open(template_file, 'r') as f:
                    template_content = f.read()
                
                # Prepare context with resolved values
                context = {
                    "system_user": getpass.getuser(),
                    "user_home": os.path.expanduser("~"),
                    "git_username": self.get_git_config_value("user.name") or os.environ.get("GIT_USERNAME", getpass.getuser()),
                    "git_email": self.get_git_config_value("user.email") or os.environ.get("GIT_EMAIL", "user@example.com"),
                    "working_directory": "/opt/CrimsonCFG",
                    "appimg_directory": "/home/" + getpass.getuser() + "/AppImages"
                }
                
                # Render template
                template = Template(template_content)
                rendered = template.render(**context)
                
                # Save as local.yml
                with open(local_file, 'w') as f:
                    f.write(rendered)
            else:
                # Fallback to empty config if template doesn't exist
                initial_local_config = {}
            
        if local_file.exists():
            with open(local_file, 'r') as f:
                local_config = self.yaml.load(f) or {}
            
            # Process the loaded configuration to resolve any remaining template variables
            local_config = self._process_config_variables(local_config)
        
        # Get actual system user
        system_user = getpass.getuser()
        
        # Convert to expected format
        config = {
            "categories": self.load_categories_from_yaml(),
            "settings": {
                "default_user": system_user,
                "working_directory": local_config.get("working_directory", "/opt/CrimsonCFG"),
                "inventory_file": f"/opt/CrimsonCFG/hosts.ini",
                "log_directory": f"/opt/CrimsonCFG/log",
                "debug": local_config.get("debug", 0),
                "git_username": local_config.get("git_username", system_user),
                "git_email": local_config.get("git_email", f"{system_user}@example.com")
            }
        }
        return config
            
    def regenerate_gui_config(self):
        """Regenerate gui_config.json from playbook metadata, supporting external repo."""
        try:
            if PlaybookScanner is not None:
                config_dir = Path.home() / ".config/com.crimson.cfg"
                user_gui_config = config_dir / "gui_config.json"
                if not config_dir.exists():
                    config_dir.mkdir(parents=True, exist_ok=True)
                # Use external repo path if configured
                external_repo_url = external_repo_manager.get_external_repo_url()
                external_repo_path = None
                if external_repo_url:
                    external_repo_path = external_repo_manager.get_external_playbooks_path()
                success = PlaybookScanner().generate_config(str(user_gui_config), external_repo_path=external_repo_path)
                if success:
                    # Reload the config
                    return self.load_config()
                else:
                    print("Failed to regenerate GUI config")
            else:
                print("PlaybookScanner not available, skipping config regeneration")
        except Exception as e:
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

    def _process_config_variables(self, config: Dict) -> Dict:
        """Process configuration to resolve any remaining template variables."""
        import getpass
        system_user = getpass.getuser()
        user_home = os.path.expanduser("~")
        working_directory = "/opt/CrimsonCFG"
        appimg_directory = f"/home/{system_user}/AppImages"
        app_directory = f"{working_directory}/app"
        
        # Define replacements
        replacements = {
            "{{ system_user }}": system_user,
            "{{ user_home }}": user_home,
            "{{ working_directory }}": working_directory,
            "{{ appimg_directory }}": appimg_directory,
            "{{ app_directory }}": app_directory,
            "{{ git_username }}": os.environ.get("GIT_USERNAME", system_user),
            "{{ git_email }}": os.environ.get("GIT_EMAIL", f"{system_user}@example.com")
        }
        
        def process_value(value):
            """Recursively process values to replace template variables."""
            if isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(v) for v in value]
            elif isinstance(value, str):
                result = value
                for template_var, replacement in replacements.items():
                    if template_var in result:
                        result = result.replace(template_var, str(replacement))
                return result
            else:
                return value
        
        return process_value(config)

    def get_git_config_value(self, key: str) -> str:
        """Get a git config --global value for a given key, or None if not set."""
        import subprocess
        try:
            value = subprocess.check_output([
                "git", "config", "--global", key
            ], stderr=subprocess.DEVNULL, text=True).strip()
            return value if value else None
        except Exception:
            return None 