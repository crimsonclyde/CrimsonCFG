#!/usr/bin/env python3
"""
CrimsonCFG Playbook Manager
Handles playbook selection and management logic
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # type: ignore
from typing import Dict, List
import json
from pathlib import Path

class PlaybookManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
    def _check_playbook_requirements(self, playbook_name: str, local_config: Dict) -> tuple[bool, str]:
        """
        Check if a playbook's requirements are met.
        Returns (requirements_met, icon_name)
        """
        # Define requirements for each playbook
        requirements_map = {
            "SSH Key": {
                "variables": ["ssh_private_key_content", "ssh_public_key_content"],
                "check": lambda config: (config.get("ssh_private_key_content", "") and 
                                       config.get("ssh_public_key_content", ""))
            },
            "Set GNOME Wallpaper": {
                "variables": ["gnome_background_image"],
                "check": lambda config: config.get("gnome_background_image", "")
            },
            "Set GNOME Theme": {
                "variables": ["theme_mode"],
                "check": lambda config: config.get("theme_mode", "") in ["light", "dark"]
            },
            "Chromium": {
                "variables": ["chromium_homepage_url", "chromium_profile1_name"],
                "check": lambda config: (
                    config.get("chromium_homepage_url", "") and 
                    config.get("chromium_profile1_name", "") and
                    self._check_chromium_files_exist()
                )
            }
        }
        
        if playbook_name not in requirements_map:
            return True, 'emblem-ok-symbolic'  # No requirements, always available
            
        requirement = requirements_map[playbook_name]
        requirements_met = requirement["check"](local_config)
        
        if requirements_met:
            return True, 'emblem-ok-symbolic'
        else:
            return False, 'process-stop-symbolic'
        
    def on_category_changed(self, button, category):
        """Handle category selection change"""
        if button.get_active():
            self.main_window.current_category = category
            self.update_playbook_list()
            
    def update_playbook_list(self):
        """Update the playbook list based on selected category"""
        # Clear existing items
        self.main_window.playbook_store.clear()
        
        if self.main_window.current_category not in self.main_window.config["categories"]:
            return
            
        cat_info = self.main_window.config["categories"][self.main_window.current_category]
        # Load local.yml config for checking required vars
        from ruamel.yaml import YAML
        from pathlib import Path
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        local_config = {}
        if local_file.exists():
            with open(local_file, 'r') as f:
                local_config = YAML().load(f) or {}
        for playbook in cat_info["playbooks"]:
            # Parse CrimsonCFG-RequiredVars from playbook YAML header if not already set
            if "required_vars" not in playbook:
                playbook_path = playbook.get("path")
                if playbook_path:
                    try:
                        with open(playbook_path, "r") as f:
                            for _ in range(10):  # Only check first 10 lines
                                line = f.readline()
                                if not line or line.strip() == "---":
                                    break
                                if line.strip().startswith("# CrimsonCFG-RequiredVars:"):
                                    value = line.split(":", 1)[1].strip().lower()
                                    playbook["required_vars"] = value == "true"
                                    break
                    except Exception:
                        pass
            essential = "✓" if playbook.get("essential", False) else ""
            description = playbook.get("description", "")
            playbook_key = f"{self.main_window.current_category}:{playbook['name']}"
            selected = playbook_key in self.main_window.selected_playbooks
            # Check if playbook should be disabled
            disabled = False
            require_config_icon = ''
            if playbook.get("required_vars", False):
                # Check specific requirements for this playbook
                requirements_met, icon = self._check_playbook_requirements(playbook['name'], local_config)
                if not requirements_met:
                    disabled = True
                    selected = False
                    require_config_icon = icon
                else:
                    require_config_icon = icon
            # Get source information (default to "Built-in" if not specified)
            source = playbook.get("source", "Built-in")
            
            self.main_window.playbook_store.append([
                playbook["name"],
                essential,
                description,
                selected,
                disabled,
                require_config_icon,
                source
            ])
            
    def on_playbook_selection_changed(self, selection):
        """Handle playbook selection change (single click - just highlight)"""
        # This method now only handles selection highlighting, not adding/removing
        pass
        
    def on_playbook_row_activated(self, treeview, path, column):
        """Handle row activation (double-click) on playbook to add/remove from selection"""
        model = treeview.get_model()
        treeiter = model.get_iter(path)
        if treeiter:
            playbook_name = model[treeiter][0]
            disabled = model[treeiter][4]
            if disabled:
                return  # Prevent selection if disabled
            playbook_key = f"{self.main_window.current_category}:{playbook_name}"
            
            if playbook_key in self.main_window.selected_playbooks:
                self.main_window.selected_playbooks.remove(playbook_key)
                model[treeiter][3] = False
            else:
                self.main_window.selected_playbooks.add(playbook_key)
                model[treeiter][3] = True
                
            self.update_selected_display()
            
    def select_all(self, button):
        """Select all playbooks in current category"""
        if self.main_window.current_category not in self.main_window.config["categories"]:
            return
            
        for playbook in self.main_window.config["categories"][self.main_window.current_category]["playbooks"]:
            playbook_key = f"{self.main_window.current_category}:{playbook['name']}"
            self.main_window.selected_playbooks.add(playbook_key)
            
        self.update_playbook_list()
        self.update_selected_display()
        
    def deselect_all(self, button):
        """Deselect all playbooks in current category"""
        if self.main_window.current_category not in self.main_window.config["categories"]:
            return
            
        for playbook in self.main_window.config["categories"][self.main_window.current_category]["playbooks"]:
            playbook_key = f"{self.main_window.current_category}:{playbook['name']}"
            self.main_window.selected_playbooks.discard(playbook_key)
            
        self.update_playbook_list()
        self.update_selected_display()
        
    def _get_installed_playbooks(self):
        """Return a set of installed playbook names from installed_playbooks.json."""
        config_dir = Path.home() / ".config/com.crimson.cfg"
        state_file = config_dir / "installed_playbooks.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                return set(state.keys())
            except Exception:
                return set()
        return set()

    def select_essential_playbooks(self):
        """Automatically select all essential playbooks across all categories that are not already installed."""
        installed = self._get_installed_playbooks()
        for category, cat_info in self.main_window.config["categories"].items():
            for playbook in cat_info["playbooks"]:
                if playbook.get("essential", False) and playbook["name"] not in installed:
                    playbook_key = f"{category}:{playbook['name']}"
                    self.main_window.selected_playbooks.add(playbook_key)
        self.update_playbook_list()
        self.update_selected_display()
        
    def remove_essential(self, button):
        """Remove all essential playbooks with warning"""
        # Show warning dialog
        warning_dialog = Gtk.MessageDialog(
            transient_for=self.main_window.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Warning: Removing Essential Playbooks",
            secondary_text="Essential playbooks are mandatory for proper system functionality. Removing them may cause issues with your system setup.\n\nAre you sure you want to remove all essential playbooks?"
        )
        
        response = warning_dialog.run()
        warning_dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            # Remove all essential playbooks
            for category, cat_info in self.main_window.config["categories"].items():
                for playbook in cat_info["playbooks"]:
                    if playbook.get("essential", False):
                        playbook_key = f"{category}:{playbook['name']}"
                        self.main_window.selected_playbooks.discard(playbook_key)
                        
            self.update_playbook_list()
            self.update_selected_display()
            
    def select_essential(self, button):
        """Select all essential playbooks across all categories that are not already installed."""
        installed = self._get_installed_playbooks()
        for category, cat_info in self.main_window.config["categories"].items():
            for playbook in cat_info["playbooks"]:
                if playbook.get("essential", False) and playbook["name"] not in installed:
                    playbook_key = f"{category}:{playbook['name']}"
                    self.main_window.selected_playbooks.add(playbook_key)
        self.update_playbook_list()
        self.update_selected_display()
        
    def remove_all(self, button):
        """Remove all non-essential playbooks from selection"""
        # Only remove non-essential playbooks, keep essential ones
        playbooks_to_remove = set()
        for playbook_key in self.main_window.selected_playbooks:
            category, name = playbook_key.split(":", 1)
            if category in self.main_window.config["categories"]:
                for playbook in self.main_window.config["categories"][category]["playbooks"]:
                    if playbook["name"] == name and not playbook.get("essential", False):
                        playbooks_to_remove.add(playbook_key)
                        break
        
        # Remove non-essential playbooks
        for playbook_key in playbooks_to_remove:
            self.main_window.selected_playbooks.discard(playbook_key)
            
        self.update_playbook_list()
        self.update_selected_display()
        
    def select_none(self, button):
        """Deselect all playbooks"""
        self.main_window.selected_playbooks.clear()
        self.update_playbook_list()
        self.update_selected_display()
        
    def update_selected_display(self):
        """Update the selected items display"""
        self.main_window.selected_store.clear()
        
        for playbook_key in sorted(self.main_window.selected_playbooks):
            category, name = playbook_key.split(":", 1)
            # Display category name in uppercase for better UI presentation
            display_category = category.upper() if category.startswith("dep:") else category
            self.main_window.selected_store.append([f"{display_category}: {name}"])
            
    def on_selected_item_row_activated(self, treeview, path, column):
        """Handle row activation (double-click) on selected item to remove it (only for non-essential)"""
        model = treeview.get_model()
        treeiter = model.get_iter(path)
        if treeiter:
            display_name = model[treeiter][0]  # Format: "category: name"
            display_category, name = display_name.split(": ", 1)
            # Convert display category back to original format for internal use
            category = display_category.lower() if display_category.startswith("DEP:") else display_category
            playbook_key = f"{category}:{name}"
            
            # Check if this is an essential playbook
            is_essential = False
            if category in self.main_window.config["categories"]:
                for playbook in self.main_window.config["categories"][category]["playbooks"]:
                    if playbook["name"] == name and playbook.get("essential", False):
                        is_essential = True
                        break
            
            # Only allow removal of non-essential playbooks
            if not is_essential:
                self.main_window.selected_playbooks.discard(playbook_key)
                self.update_playbook_list()
                self.update_selected_display()
            
    def get_selected_playbooks(self) -> List[Dict]:
        """Get list of selected playbooks with their details, including essential_order if present"""
        selected = []
        for playbook_key in self.main_window.selected_playbooks:
            category, name = playbook_key.split(":", 1)
            if category in self.main_window.config["categories"]:
                for playbook in self.main_window.config["categories"][category]["playbooks"]:
                    if playbook["name"] == name:
                        # Try to get essential_order from playbook metadata, default to None
                        essential_order = playbook.get("essential_order")
                        # Also support YAML comment key if present
                        if essential_order is None:
                            # Try alternate keys for compatibility
                            essential_order = playbook.get("essential-order") or playbook.get("order")
                        selected.append({
                            "category": category,
                            "name": playbook["name"],
                            "path": playbook["path"],
                            "description": playbook.get("description", ""),
                            "essential": playbook.get("essential", False),
                            "essential_order": essential_order,
                            "source": playbook.get("source", "Built-in")
                        })
                        break
        return selected

    def _check_chromium_files_exist(self) -> bool:
        """Check if the required Chromium template files exist"""
        try:
            from pathlib import Path
            import os
            
            # Check if templates directory exists
            templates_dir = Path("templates")
            if not templates_dir.exists():
                return False
            
            # Check if chromium_policies.j2 exists
            policies_file = templates_dir / "chromium_policies.j2"
            if not policies_file.exists():
                return False
            
            # Check if master_preferences exists
            master_prefs_file = templates_dir / "master_preferences"
            if not master_prefs_file.exists():
                return False
            
            return True
        except Exception:
            return False 