#!/usr/bin/env python3
"""
CrimsonCFG Authentication Manager
Handles sudo password prompts and validation
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk  # type: ignore
import os
import subprocess
import yaml
from pathlib import Path
import threading
import secrets
import string
from ruamel.yaml import YAML

class AuthManager:
    def __init__(self, main_window, on_success=None):
        self.main_window = main_window
        self.debug = getattr(main_window, 'debug', False)
        self.on_success = on_success
        
    def check_and_create_admin_password(self):
        """Check if admin_password is set in local.yml, create one if not, and show to user"""
        if self.debug:
            print("check_and_create_admin_password: Starting...")
            
        # Load local.yml
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        
        if not local_file.exists():
            if self.debug:
                print("check_and_create_admin_password: local.yml does not exist")
            return False
            
        try:
            # Use ruamel.yaml to preserve comments and formatting
            yaml_ruamel = YAML()
            yaml_ruamel.preserve_quotes = True
            
            with open(local_file, 'r') as f:
                local_config = yaml_ruamel.load(f) or {}
                
            admin_password = local_config.get('admin_password', '')
            
            # Check if admin_password is set and not the default
            if not admin_password or admin_password == '3HeaddedMonkey':
                if self.debug:
                    print("check_and_create_admin_password: Admin password not set or is default, creating new one")
                
                # Generate a secure password
                new_password = self._generate_secure_password()
                
                # Update local.yml with new password
                local_config['admin_password'] = new_password
                
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(local_config, f)
                
                if self.debug:
                    print("check_and_create_admin_password: New admin password saved to local.yml")
                
                # Show password to user
                self._show_admin_password_dialog(new_password)
                return True
            else:
                if self.debug:
                    print("check_and_create_admin_password: Admin password already set")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"check_and_create_admin_password: Error: {e}")
            return False
    
    def _generate_secure_password(self, length=12):
        """Generate a secure random password"""
        # Use a mix of letters, digits, and symbols
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def _show_admin_password_dialog(self, password):
        """Show dialog with the new admin password"""
        if self.debug:
            print("_show_admin_password_dialog: Creating dialog...")
            
        # Create dialog
        dialog = Gtk.Dialog(title="Admin Password Created", parent=self.main_window.window)
        dialog.set_modal(True)
        dialog.set_size_request(500, 300)
        dialog.set_resizable(False)
        
        # Get content area
        content_area = dialog.get_content_area()
        content_area.set_spacing(20)
        content_area.set_margin_start(20)
        content_area.set_margin_end(20)
        content_area.set_margin_top(20)
        content_area.set_margin_bottom(20)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='large' weight='bold'>Admin Password Created</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        content_area.pack_start(title_label, False, False, 0)
        
        # Description
        desc_label = Gtk.Label()
        desc_label.set_markup(
            "A new admin password has been created for CrimsonCFG.\n"
            "Please write it down in a secure location.\n"
            "You can change this password later in the Admin menu."
        )
        desc_label.set_line_wrap(True)
        desc_label.set_halign(Gtk.Align.CENTER)
        desc_label.set_justify(Gtk.Justification.CENTER)
        content_area.pack_start(desc_label, False, False, 0)
        
        # Password frame
        password_frame = Gtk.Frame()
        password_frame.set_margin_top(20)
        password_frame.set_margin_bottom(20)
        
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        password_box.set_margin_start(15)
        password_box.set_margin_end(15)
        password_box.set_margin_top(15)
        password_box.set_margin_bottom(15)
        
        password_label = Gtk.Label(label="Your Admin Password:")
        password_label.set_halign(Gtk.Align.CENTER)
        password_box.pack_start(password_label, False, False, 0)
        
        # Password entry (read-only)
        password_entry = Gtk.Entry()
        password_entry.set_text(password)
        password_entry.set_editable(False)
        password_entry.set_can_focus(False)
        password_entry.set_size_request(300, -1)
        password_entry.set_halign(Gtk.Align.CENTER)
        password_box.pack_start(password_entry, False, False, 0)
        
        # Copy button
        copy_button = Gtk.Button(label="Copy to Clipboard")
        copy_button.set_halign(Gtk.Align.CENTER)
        def on_copy_clicked(button):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(password, -1)
            copy_button.set_label("Copied!")
            # Reset button label after 2 seconds
            def reset_label():
                copy_button.set_label("Copy to Clipboard")
            from gi.repository import GLib
            GLib.timeout_add(2000, reset_label)
        copy_button.connect("clicked", on_copy_clicked)
        password_box.pack_start(copy_button, False, False, 0)
        
        password_frame.add(password_box)
        content_area.pack_start(password_frame, False, False, 0)
        
        # Warning
        warning_label = Gtk.Label()
        warning_label.set_markup("<span foreground='orange'><b>Important:</b> Write this password down now!</span>")
        warning_label.set_halign(Gtk.Align.CENTER)
        content_area.pack_start(warning_label, False, False, 0)
        
        # OK button
        ok_button = Gtk.Button(label="I've Written It Down")
        ok_button.set_halign(Gtk.Align.CENTER)
        ok_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.OK))
        content_area.pack_start(ok_button, False, False, 0)
        
        # Show dialog
        dialog.show_all()
        dialog.run()
        dialog.destroy()
        
        if self.debug:
            print("_show_admin_password_dialog: Dialog closed")

    def show_sudo_prompt(self):
        """Show sudo password prompt in the main window"""
        if self.debug:
            print("show_sudo_prompt: Starting...")
        # Clear main container
        for child in self.main_window.main_container.get_children():
            self.main_window.main_container.remove(child)
            
        # Apply CSS styling first
        if self.debug:
            print("show_sudo_prompt: Applying CSS...")
        self.main_window.gui_builder.apply_css()
            
        # Create header first (same as main interface)
        if self.debug:
            print("show_sudo_prompt: Creating header...")
        header_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_container.set_hexpand(True)
        header_container.set_margin_top(15)
        header_container.set_margin_bottom(15)
        
        # Apply CSS class for header styling
        header_style_context = header_container.get_style_context()
        header_style_context.add_class("header-box")
        
        # Header content (full width)
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        header_box.set_hexpand(True)
        header_container.pack_start(header_box, True, True, 0)
        
        # Add expander to push content to the right
        expander = Gtk.Box()
        expander.set_hexpand(True)
        header_box.pack_start(expander, True, True, 0)
        
        # Title and subtitle (right side)
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        title_box.set_halign(Gtk.Align.START)
        title_box.set_valign(Gtk.Align.CENTER)
        
        # Main title - CrimsonCFG
        try:
            # Load local.yml
            local_config = {}
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
            
            # Use only local_config
            app_name = local_config.get('app_name', 'CrimsonCFG')
            app_subtitle = local_config.get('app_subtitle', 'System Configuration Manager')
            app_logo = local_config.get('app_logo', os.path.join("files", "app", "com.crimson.cfg.icon.png"))
        except Exception:
            app_name = 'CrimsonCFG'
            app_subtitle = 'System Configuration Manager'
            app_logo = os.path.join("files", "app", "com.crimson.cfg.icon.png")
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='x-large' weight='bold'>{app_name}</span>")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_valign(Gtk.Align.CENTER)
        title_box.pack_start(title_label, False, False, 0)
        subtitle_label = Gtk.Label()
        subtitle_label.set_markup(f"<span size='medium'>{app_subtitle}</span>")
        subtitle_label.set_halign(Gtk.Align.START)
        subtitle_label.set_valign(Gtk.Align.CENTER)
        title_box.pack_start(subtitle_label, False, False, 0)
        
        header_box.pack_start(title_box, False, False, 0)
        
        # Logo (right side)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        logo_box.set_halign(Gtk.Align.CENTER)
        if os.path.exists(app_logo):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(app_logo, 150, -1)
                logo_image = Gtk.Image.new_from_pixbuf(pixbuf)
                logo_box.pack_start(logo_image, False, False, 0)
            except Exception as e:
                logo_label = Gtk.Label(label="[Logo failed to load]")
                logo_box.pack_start(logo_label, False, False, 0)
        else:
            logo_label = Gtk.Label(label="[Logo not found]")
            logo_box.pack_start(logo_label, False, False, 0)
            
        header_box.pack_start(logo_box, False, False, 0)
        
        # Add header to main container
        self.main_window.main_container.pack_start(header_container, False, False, 0)
            
        # Create sudo prompt content (centered)
        if self.debug:
            print("show_sudo_prompt: Creating content area...")
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        content_box.set_margin_start(100)
        content_box.set_margin_end(100)
        content_box.set_margin_top(100)
        content_box.set_margin_bottom(100)
        content_box.set_halign(Gtk.Align.CENTER)
        content_box.set_valign(Gtk.Align.CENTER)
        
        # Main title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='xx-large' weight='bold'>Setup Required</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        
        # Create background event box for title
        title_background = Gtk.EventBox()
        title_background.set_visible_window(True)
        title_background.set_margin_bottom(20)
        title_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.8))
        # Add title label to event box
        title_box_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title_box_inner.pack_start(title_label, True, True, 10)
        title_background.add(title_box_inner)
        content_box.pack_start(title_background, False, False, 0)
        
        # Description
        desc_label = Gtk.Label()
        desc_label.set_markup(
            "CrimsonCFG requires administrator privileges to install packages and configure your system.\n"
            "Please enter your sudo password to continue.\n"
        )
        desc_label.set_line_wrap(True)
        desc_label.set_halign(Gtk.Align.CENTER)
        desc_label.set_justify(Gtk.Justification.CENTER)
        desc_label.set_margin_top(20)
        
        # Create background event box for description
        desc_background = Gtk.EventBox()
        desc_background.set_visible_window(True)
        desc_background.set_margin_bottom(20)
        desc_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.8))
        # Add description label to event box
        desc_box_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desc_box_inner.pack_start(desc_label, True, True, 10)
        desc_background.add(desc_box_inner)
        content_box.pack_start(desc_background, False, False, 0)
        
        # Password entry frame
        if self.debug:
            print("show_sudo_prompt: Creating password entry...")
        password_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        password_frame.set_margin_top(40)
        password_frame.set_halign(Gtk.Align.CENTER)
        
        password_label = Gtk.Label(label="Sudo Password:")
        password_label.set_halign(Gtk.Align.CENTER)
        password_frame.pack_start(password_label, False, False, 0)
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text("Enter your sudo password")
        self.password_entry.set_margin_top(10)
        self.password_entry.set_size_request(300, -1)
        password_frame.pack_start(self.password_entry, False, False, 0)
        if self.debug:
            print("show_sudo_prompt: Password entry created and added to frame")
        
        # Status label
        self.status_label = Gtk.Label(label="")
        self.status_label.set_margin_top(10)
        password_frame.pack_start(self.status_label, False, False, 0)
        
        content_box.pack_start(password_frame, False, False, 0)
        
        # Buttons
        if self.debug:
            print("show_sudo_prompt: Creating buttons...")
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(40)
        
        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        button_box.pack_start(self.cancel_button, False, False, 0)
        
        self.ok_button = Gtk.Button(label="Continue")
        self.ok_button.connect("clicked", self.on_sudo_ok_clicked)
        button_box.pack_start(self.ok_button, False, False, 0)
        
        content_box.pack_start(button_box, False, False, 0)
        
        # Add to main container
        if self.debug:
            print("show_sudo_prompt: Adding content to main container...")
        self.main_window.main_container.pack_start(content_box, True, True, 0)
        
        # Focus on password entry
        if self.debug:
            print("show_sudo_prompt: Setting focus on password entry...")
        self.password_entry.grab_focus()
        
        # Connect enter key
        self.password_entry.connect("activate", self.on_sudo_ok_clicked)
        
        if self.debug:
            print("show_sudo_prompt: Complete - all widgets should be visible")
        # Force a redraw
        self.main_window.window.queue_draw()
        if self.debug:
            print("show_sudo_prompt: Window redraw queued")
        self.main_window.window.show_all()
        
    def on_cancel_clicked(self, button):
        """Handle cancel button click"""
        # Use application quit instead of window destroy
        self.main_window.application.quit()
        
    def on_sudo_ok_clicked(self, button):
        """Handle sudo OK button click"""
        if self.debug:
            print("Sudo OK button clicked")
        password = self.password_entry.get_text()
        
        if not password:
            if self.debug:
                print("No password entered")
            self.status_label.set_text("Please enter your sudo password.")
            return
        
        # Set status and start validation in a thread
        self.status_label.set_text("Validating password...")
        self.main_window.window.queue_draw()
        def validate():
            result = self.test_sudo_password(password)
            def after():
                if result:
                    if self.debug:
                        print("Password validated successfully!")
                    self.status_label.set_text("Password validated successfully!")
                    self.main_window.window.queue_draw()
                    self.main_window.sudo_password = password
                    # Regenerate GUI config from playbooks
                    self.main_window.config_manager.regenerate_gui_config()
                    self.main_window.config = self.main_window.config_manager.load_config()
                    # Transition to main interface
                    if self.debug:
                        print("Transitioning to main interface...")
                    if self.on_success:
                        self.on_success()
                else:
                    if self.debug:
                        print("Password validation failed!")
                    self.status_label.set_text("Invalid password. Please try again.")
                    self.password_entry.set_text("")
                    self.password_entry.grab_focus()
                return False  # Stop idle_add
            from gi.repository import GLib
            GLib.idle_add(after)
        threading.Thread(target=validate, daemon=True).start()
            
    def test_sudo_password(self, password) -> bool:
        """Test if the provided sudo password is valid"""
        if self.debug:
            print("Testing sudo password...")
        try:
            result = subprocess.run(
                ["sudo", "-k", "-S", "whoami"],
                input=f"{password}\n",
                capture_output=True,
                text=True,
                timeout=10
            )
            if self.debug:
                print(f"Sudo test result: {result.returncode}")
            return result.returncode == 0
        except Exception as e:
            if self.debug:
                print(f"Sudo test exception: {e}")
            return False 