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
from . import external_repo_manager
from .debug_manager import DebugManager

class CrimsonCFGGUI:
    def __init__(self, application, initial_config=None):
        # Load debug setting early from user's local.yml and command line arguments
        self.debug = False
        try:
            import yaml
            from pathlib import Path
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
                    self.debug = local_config.get("debug", 0) == 1
            
            # Override with command line debug setting if present
            if initial_config and 'settings' in initial_config:
                cmdline_debug = initial_config['settings'].get('debug', 0)
                if cmdline_debug == 1:
                    self.debug = True
        except Exception as e:
            # We'll use DebugManager later when it's available
            self.debug = False
            
        # Create debug manager
        self.debug_manager = DebugManager()
        
        if self.debug:
            self.debug_manager.print("CrimsonCFGGUI.__init__ starting")
        # Request dark theme for the application
        settings = Gtk.Settings.get_default()
        if settings is not None:
            settings.set_property('gtk-application-prefer-dark-theme', True)
        self.application = application
        self.sudo_password = None
        
        # Store initial config for use in icon setting
        self.initial_config = initial_config
        
        if self.debug:
            self.debug_manager.print("Initializing CrimsonCFGGUI...")
            self.debug_manager.print("Creating window...")
        self.window = Gtk.ApplicationWindow(application=application)
        self.application.add_window(self.window)
        self.window.set_title("CrimsonCFG - App &amp; Customization Selector")
        self.window.set_default_size(1400, 900)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        # Set maximum height to prevent overflow on smaller screens
        self.window.set_size_request(800, 600)  # Minimum size
        self.window.set_resizable(True)
        # Set maximum size using geometry hints
        geometry = Gdk.Geometry()
        geometry.max_width = 1600
        geometry.max_height = 1000
        geometry.min_width = 800
        geometry.min_height = 600
        self.window.set_geometry_hints(self.window, geometry, Gdk.WindowHints.MAX_SIZE | Gdk.WindowHints.MIN_SIZE)
        if self.debug:
            self.debug_manager.print("Window created successfully")
        
        # Set application icon using template-based config
        self._set_application_icon()
        
        # Apply CSS class for styling
        style_context = self.window.get_style_context()
        style_context.add_class("main-window")
        
        # Initialize managers first
        self.config_manager = ConfigManager()
        self.config_manager.debug = self.debug  # Set debug in config manager
        
        # Load config
        if self.debug:
            self.debug_manager.print("Loading config...")
        self.config = self.config_manager.load_config()
        if self.debug:
            self.debug_manager.print(f"Config loaded: {len(self.config.get('categories', {}))} categories")
            self.debug_manager.print("Config loading completed")
        
        # Keep debug setting from early load (don't override it)
        self.config_manager.debug = self.debug  # Ensure debug flag is consistent
        
        # Initialize remaining managers (after debug is set)
        self.auth_manager = AuthManager(self, on_success=self.on_auth_success)
        self.gui_builder = GUIBuilder(self)
        if self.debug:
            self.debug_manager.print("GUIBuilder initialized")
        self.installer = Installer(self)
        self.logger = Logger(self)
        self.playbook_manager = PlaybookManager(self)
        if self.debug:
            self.debug_manager.print("All managers initialized")
        # Variables (after config is loaded)
        self.user = self.config.get("settings", {}).get("default_user", "user")
        self.user_home = f"/home/{self.user}"
        self.working_directory = self.config.get("settings", {}).get("working_directory", "/opt/CrimsonCFG")
        if "{{ user_home }}" in self.working_directory:
            self.working_directory = self.working_directory.replace("{{ user_home }}", self.user_home)
        self.inventory_file = f"{self.working_directory}/hosts.ini"
        self.selected_playbooks = set()
        self.installation_running = False
        
        if self.debug:
            self.debug_manager.print("About to show main interface")
        # Create main container and add to window before showing main interface
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.main_container)
        if self.debug:
            self.debug_manager.print("main_container created and added to window")
        # Show the sudo prompt first
        self.auth_manager.show_sudo_prompt()
        if self.debug:
            self.debug_manager.print("Sudo prompt should now be visible")
        
        # Setup Ansible environment
        self.installer.setup_ansible_environment()
        
        # Connect window close signal
        self.window.connect("destroy", self.on_window_destroy)
        
    def _set_application_icon(self):
        """Set application icon using template-based config"""
        if self.debug:
            self.debug_manager.print("Setting application icon...")
        
        # Get app name and subtitle from initial config
        app_name = 'CrimsonCFG'
        app_subtitle = 'System Configuration Manager'
        app_logo = None
        
        if self.initial_config and 'local_config' in self.initial_config:
            local_config = self.initial_config['local_config']
            app_name = local_config.get('app_name', 'CrimsonCFG')
            app_subtitle = local_config.get('app_subtitle', 'System Configuration Manager')
            app_logo = local_config.get('app_logo', None)
        
        self.window.set_title(f"{app_name} - {app_subtitle}")
        
        # Use template-based icon logic
        icon_set = False
        
        # 1. Try app_logo from template (if exists and file exists)
        if app_logo and os.path.exists(app_logo):
            if self.debug:
                self.debug_manager.print(f"Setting icon from template app_logo: {app_logo}")
            self.window.set_icon_from_file(app_logo)
            icon_set = True
        else:
            # Get working directory from template config
            working_dir = "/opt/CrimsonCFG"  # Default fallback
            if self.initial_config and 'settings' in self.initial_config:
                working_dir = self.initial_config['settings'].get('working_directory', '/opt/CrimsonCFG')
            
            if self.debug:
                self.debug_manager.print(f"Using working directory from template: {working_dir}")
            
            # 2. Try com.crimson.cfg.icon.png (primary fallback)
            try:
                fallback_icon = os.path.join(working_dir, 'files', 'app', 'com.crimson.cfg.icon.png')
                if os.path.exists(fallback_icon):
                    if self.debug:
                        self.debug_manager.print(f"Setting icon from primary fallback: {fallback_icon}")
                    self.window.set_icon_from_file(fallback_icon)
                    icon_set = True
                # 3. Try com.crimson.cfg.icon.png (worst case fallback)
                elif os.path.exists(os.path.join(working_dir, 'files', 'app', 'com.crimson.cfg.icon.png')):
                    if self.debug:
                        self.debug_manager.print(f"Setting icon from worst case fallback: {os.path.join(working_dir, 'files', 'app', 'com.crimson.cfg.icon.png')}")
                    self.window.set_icon_from_file(os.path.join(working_dir, 'files', 'app', 'com.crimson.cfg.icon.png'))
                    icon_set = True
            except Exception as e:
                if self.debug:
                    self.debug_manager.print(f"Error setting icon: {e}")
                pass
        
        # 4. Final fallback to icon name
        if not icon_set:
            if self.debug:
                self.debug_manager.print("Setting icon name fallback: com.crimson.cfg")
            self.window.set_icon_name("com.crimson.cfg")
        
        if self.debug:
            self.debug_manager.print("Application icon setting completed")
        
    def on_window_delete_event(self, widget, event):
        """Handle window close event"""
        if self.debug:
            self.debug_manager.print("Window close event received")
        # Properly handle window close with application lifecycle
        # Remove the window from the application first
        self.application.remove_window(self.window)
        # Then signal the application to quit
        self.application.quit()
        return True  # Prevent default handling
        
    def on_window_destroy(self, widget):
        """Handle window destroy event"""
        if self.debug:
            self.debug_manager.print("Window destroy event received")
        # Signal the application to quit
        self.application.quit()
        
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
        
    def remove_all(self, button):
        return self.playbook_manager.remove_all(button)
        
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
            self.gui_builder.notebook.set_current_page(4)  # Logs tab is now at index 4 (5th tab)
        
        # Log the selected playbooks
        self.logger.log_message("=== INSTALLATION STARTED ===")
        self.logger.log_message(f"Selected playbooks ({len(selected_sorted)}):")
        for playbook in selected_sorted:
            essential_mark = " (Essential)" if playbook["essential"] else ""
            # Display category name in uppercase for better UI presentation
            display_category = playbook['category'].upper() if playbook['category'].startswith("dep:") else playbook['category']
            self.logger.log_message(f"  • {display_category}: {playbook['name']}{essential_mark}")
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

    def update_playbooks(self, button):
        """Update playbooks from external repository and refresh the list"""
        try:
            if self.debug:
                self.debug_manager.print("Update playbooks button clicked")
            
            # Check if external repository is configured
            repo_url = external_repo_manager.get_external_repo_url()
            if not repo_url:
                self.status_label.set_text("No external repository configured. Use Administration tab to set one up.")
                return
            
            # Show status message
            self.status_label.set_text("Updating playbooks from external repository...")
            
            # Update external repository if configured
            success = external_repo_manager.update_external_repo_sync(self.sudo_password, self.logger)
            
            if not success:
                self.status_label.set_text("Failed to update external repository. Check logs for details.")
                if self.debug:
                    self.debug_manager.print("Failed to update external repository")
                return
            
            # Regenerate config and update playbook list
            self.config_manager.regenerate_gui_config()
            self.config = self.config_manager.load_config()
            self.update_playbook_list()
            
            # Show success message
            self.status_label.set_text("Playbooks updated successfully!")
            
            if self.debug:
                self.debug_manager.print("Playbooks updated successfully")
                
        except Exception as e:
            error_msg = f"Error updating playbooks: {e}"
            self.status_label.set_text(error_msg)
            if self.debug:
                self.debug_manager.print(f"Error updating playbooks: {e}")

 

    def on_auth_success(self):
        # Check and create admin password if needed
        self.auth_manager.check_and_create_admin_password()
        
        # Update external repository if configured
        if self.debug:
            self.debug_manager.print("[DEBUG] Updating external repository...")
        try:
            external_repo_manager.update_external_repo_sync(self.sudo_password, self.logger)
            if self.debug:
                self.debug_manager.print("[DEBUG] External repository updated successfully")
        except Exception as e:
            if self.debug:
                self.debug_manager.print(f"[DEBUG] Error updating external repository: {e}")
        
        self.gui_builder.show_main_interface()
        
        # Refresh System tab button states after authentication
        if hasattr(self, 'system_tab'):
            self.system_tab.refresh_button_states() 