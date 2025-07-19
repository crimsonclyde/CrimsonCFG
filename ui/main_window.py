#!/usr/bin/env python3
"""
CrimsonCFG Main Window Module
Core GUI window and initialization
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk  # type: ignore
import os
import threading
from typing import Dict, List

from .auth_manager import AuthManager
from .config_manager import ConfigManager
from .gui_builder import GUIBuilder
from .installer import Installer
from .logger import Logger
from .playbook_manager import PlaybookManager

class CrimsonCFGGUI:
    def __init__(self, application):
        # Request dark theme for the application
        settings = Gtk.Settings.get_default()
        if settings is not None:
            settings.set_property('gtk-application-prefer-dark-theme', True)
        self.application = application
        self.sudo_password = None
        
        # Set default debug value early
        self.debug = False
        
        if self.debug:
            print("Initializing CrimsonCFGGUI...")
            print("Creating window...")
        self.window = Gtk.ApplicationWindow(application=application)
        self.application.add_window(self.window)
        self.window.set_title("CrimsonCFG - App & Customization Selector")
        self.window.set_default_size(1400, 900)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        if self.debug:
            print("Window created successfully")
        
        # Set application icon
        import yaml
        from pathlib import Path
        try:
            # Load all.yml
            all_config = {}
            all_file = Path("group_vars/all.yml")
            if all_file.exists():
                with open(all_file, 'r') as f:
                    all_config = yaml.safe_load(f) or {}
            
            # Load local.yml
            local_config = {}
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
            
            # Merge configurations (local overrides all)
            merged_config = {**all_config, **local_config}
            
            app_name = merged_config.get('app_name', 'CrimsonCFG')
            app_subtitle = merged_config.get('app_subtitle', 'App & Customization Selector')
            app_logo = merged_config.get('app_logo', None)
        except Exception:
            app_name = 'CrimsonCFG'
            app_subtitle = 'App & Customization Selector'
            app_logo = None
        self.window.set_title(f"{app_name} - {app_subtitle}")
        if app_logo and os.path.exists(app_logo):
            self.window.set_icon_from_file(app_logo)
        else:
            self.window.set_icon_name("com.crimson.cfg")
        
        # Apply CSS class for styling
        style_context = self.window.get_style_context()
        style_context.add_class("main-window")
        
        # Initialize managers first
        self.config_manager = ConfigManager()
        self.config_manager.debug = self.debug  # Set debug in config manager
        
        # Load config
        if self.debug:
            print("Loading config...")
        self.config = self.config_manager.load_config()
        if self.debug:
            print(f"Config loaded: {len(self.config.get('categories', {}))} categories")
            print("Config loading completed")
        
        # Initialize debug setting (override default)
        self.debug = self.config.get("settings", {}).get("debug", 0) == 1
        
        # Initialize remaining managers (after debug is set)
        self.auth_manager = AuthManager(self)
        self.gui_builder = GUIBuilder(self)
        self.installer = Installer(self)
        self.logger = Logger(self)
        self.playbook_manager = PlaybookManager(self)
        
        # Variables (after config is loaded)
        self.user = self.config.get("settings", {}).get("default_user", "user")
        self.user_home = f"/home/{self.user}"
        self.ansible_folder = self.config.get("settings", {}).get("ansible_folder", f"{self.user_home}/Ansible")
        if "{{ user_home }}" in self.ansible_folder:
            self.ansible_folder = self.ansible_folder.replace("{{ user_home }}", self.user_home)
        self.inventory_file = f"{self.ansible_folder}/hosts.ini"
        self.selected_playbooks = set()
        self.installation_running = False
        
        # Setup Ansible environment
        self.installer.setup_ansible_environment()
        
        # Create main container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.main_container)
        
        # Show the window
        if self.debug:
            print("Showing window...")
        self.window.show_all()
        if self.debug:
            print("Window shown successfully")
        
        # Connect to window close event
        self.window.connect("delete-event", self.on_window_delete_event)
        
        # Start with sudo password prompt
        if self.debug:
            print("Showing sudo prompt...")
        self.auth_manager.show_sudo_prompt()
        if self.debug:
            print("CrimsonCFGGUI initialization complete")
        
    def on_window_delete_event(self, widget, event):
        """Handle window close event"""
        if self.debug:
            print("Window close event received")
        # Release the application hold
        self.application.release()
        return False  # Allow the window to close
        
    def run(self):
        """Show the window and start the main loop"""
        # The window is already shown in __init__, and the application manages the main loop
        pass
        
    # Delegate playbook management methods
    def on_category_changed(self, button, category):
        return self.playbook_manager.on_category_changed(button, category)
        
    def update_playbook_list(self):
        return self.playbook_manager.update_playbook_list()
        
    def on_playbook_selection_changed(self, selection):
        return self.playbook_manager.on_playbook_selection_changed(selection)
        
    def select_all(self, button):
        return self.playbook_manager.select_all(button)
        
    def deselect_all(self, button):
        return self.playbook_manager.deselect_all(button)
        
    def select_essential_playbooks(self):
        return self.playbook_manager.select_essential_playbooks()
        
    def remove_essential(self, button):
        return self.playbook_manager.remove_essential(button)
        
    def select_essential(self, button):
        return self.playbook_manager.select_essential(button)
        
    def select_none(self, button):
        return self.playbook_manager.select_none(button)
        
    def update_selected_display(self):
        return self.playbook_manager.update_selected_display()
        
    def get_selected_playbooks(self):
        return self.playbook_manager.get_selected_playbooks()
        
    def install_selected(self, button):
        """Install the selected playbooks"""
        if self.installation_running:
            info_dialog = Gtk.MessageDialog(
                transient_for=self.window,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Installation is already running. Please wait."
            )
            info_dialog.run()
            info_dialog.destroy()
            return
            
        # Check if confirmation checkbox is checked
        if not self.confirm_checkbox.get_active():  # type: ignore
            warning_dialog = Gtk.MessageDialog(  # type: ignore
                transient_for=self.window,
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="Please check the confirmation checkbox to proceed with installation."
            )
            warning_dialog.run()
            warning_dialog.destroy()
            return
            
        selected = self.get_selected_playbooks()
        if not selected:
            warning_dialog = Gtk.MessageDialog(
                transient_for=self.window,
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="No playbooks selected!"
            )
            warning_dialog.run()
            warning_dialog.destroy()
            return

        # --- ENFORCE BASICS ORDER ---
        def playbook_sort_key(pb):
            # Basics essential playbooks: sort by essential_order (as int, fallback to 999)
            if pb["category"].lower() == "basics" and pb.get("essential", False):
                try:
                    return (0, int(pb.get("essential_order", 999)))
                except Exception:
                    return (0, 999)
            # All others after
            return (1, 0)
        selected_sorted = sorted(selected, key=playbook_sort_key)

        # Switch to logs tab to show installation progress
        if self.gui_builder.notebook is not None:
            self.gui_builder.notebook.set_current_page(1)
        
        # Log the selected playbooks
        self.logger.log_message("=== INSTALLATION STARTED ===")
        self.logger.log_message(f"Selected playbooks ({len(selected_sorted)}):")
        for playbook in selected_sorted:
            essential_mark = " (Essential)" if playbook["essential"] else ""
            self.logger.log_message(f"  • {playbook['category']}: {playbook['name']}{essential_mark}")
        self.logger.log_message("=== BEGINNING INSTALLATION ===")
        
        # Start installation in a separate thread
        self.installation_running = True
        self.install_btn.set_sensitive(False)  # type: ignore
        thread = threading.Thread(target=self.installer.run_installation, args=(selected_sorted,))
        thread.daemon = True
        thread.start()
        
    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
        
    def show_success_dialog(self, message):
        """Show success dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
        
    def clear_logs(self, button):
        """Clear the logs display"""
        return self.logger.clear_logs(button)
        
    def on_debug_toggled(self, checkbox):
        """Handle debug checkbox toggle"""
        self.debug = checkbox.get_active()
        if self.debug:
            self.logger.log_message("Debug mode enabled")
        else:
            self.logger.log_message("Debug mode disabled") 