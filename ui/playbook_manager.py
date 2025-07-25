#!/usr/bin/env python3
"""
CrimsonCFG Playbook Manager
Handles playbook selection and management logic
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # type: ignore
from typing import Dict, List
import json
from pathlib import Path

class PlaybookManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
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
                # For now, only check SSH key requirements
                priv = local_config.get("ssh_private_key_content", "")
                pub = local_config.get("ssh_public_key_content", "")
                if not priv or not pub:
                    disabled = True
                    selected = False
                    require_config_icon = 'process-stop-symbolic'  # stop sign
                else:
                    require_config_icon = 'emblem-ok-symbolic'  # checkmark
            self.main_window.playbook_store.append([
                playbook["name"],
                essential,
                description,
                selected,
                disabled,
                require_config_icon
            ])
            
    def on_playbook_selection_changed(self, selection):
        """Handle playbook selection change"""
        model, treeiter = selection.get_selected()
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
            self.main_window.selected_store.append([f"{category}: {name}"])
            
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
                            "essential_order": essential_order
                        })
                        break
        return selected 