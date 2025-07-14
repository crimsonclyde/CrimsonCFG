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

class AuthManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
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
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>CrimsonCFG</span>")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_valign(Gtk.Align.CENTER)
        title_box.pack_start(title_label, False, False, 0)
        
        # Subtitle - App & Customization Selector
        subtitle_label = Gtk.Label()
        subtitle_label.set_markup("<span size='medium'>App &amp; Customization Selector</span>")
        subtitle_label.set_halign(Gtk.Align.START)
        subtitle_label.set_valign(Gtk.Align.CENTER)
        title_box.pack_start(subtitle_label, False, False, 0)
        
        header_box.pack_start(title_box, False, False, 0)
        
        # Logo (right side)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        logo_box.set_halign(Gtk.Align.CENTER)
        
        # Try to load logo
        logo_path = os.path.join("files", "com.crimson.cfg.logo.png")
        if os.path.exists(logo_path):
            try:
                # Resize logo to a smaller size (150px max width)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(logo_path, 150, -1)
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
        self.main_window.window.destroy()
        
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
            
        # Test password
        if self.debug:
            print("Testing sudo password...")
        self.status_label.set_text("Validating password...")
        self.main_window.window.queue_draw()
        
        if self.test_sudo_password(password):
            if self.debug:
                print("Password validated successfully!")
            self.status_label.set_text("Password validated successfully!")
            self.main_window.window.queue_draw()
            self.main_window.sudo_password = password
            
            # Regenerate GUI config from playbooks
            self.main_window.config_manager.regenerate_gui_config()
            
            # Transition to main interface
            if self.debug:
                print("Transitioning to main interface...")
            self.main_window.gui_builder.show_main_interface()
        else:
            if self.debug:
                print("Password validation failed!")
            self.status_label.set_text("Invalid password. Please try again.")
            self.password_entry.set_text("")
            self.password_entry.grab_focus()
            
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