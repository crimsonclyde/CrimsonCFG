#!/usr/bin/env python3
"""
CrimsonCFG UI Module
Main GTK3 GUI interface for CrimsonCFG
"""

# Define module name for import compatibility
__name__ = "crimson_cfg_ui"

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk  # type: ignore
import json
import os
import subprocess
import threading
import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Import the playbook scanner
try:
    from functions.playbook_scanner import PlaybookScanner
    print("PlaybookScanner imported successfully")
except ImportError as e:
    # Fallback if scanner module is not available
    print(f"PlaybookScanner import failed: {e}")
    PlaybookScanner = None

class CrimsonCFGGUI:
    def __init__(self, application):
        print("Initializing CrimsonCFGGUI...")
        self.application = application
        self.sudo_password = None
        print("Creating window...")
        self.window = Gtk.ApplicationWindow(application=application)
        self.application.add_window(self.window)
        self.window.set_title("CrimsonCFG - App & Customization Selector")
        self.window.set_default_size(1400, 900)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        print("Window created successfully")
        
        # Set application icon
        self.window.set_icon_name("com.crimson.cfg")
        
        # Apply CSS class for styling
        style_context = self.window.get_style_context()
        style_context.add_class("main-window")
        
        # Load config first
        print("Loading config...")
        self.config = self.load_config()
        print(f"Config loaded: {len(self.config.get('categories', {}))} categories")
        print("Config loading completed")
        
        # Initialize debug setting
        self.debug = self.config.get("settings", {}).get("debug", 0) == 1
        
        # Variables (after config is loaded)
        self.user = self.config.get("settings", {}).get("default_user", "user")
        self.user_home = f"/home/{self.user}"
        self.ansible_folder = f"{self.user_home}/Ansible"
        self.inventory_file = f"{self.ansible_folder}/hosts.ini"
        self.selected_playbooks = set()
        self.installation_running = False
        
        # Setup Ansible environment
        self.setup_ansible_environment()
        
        # Create main container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.main_container)
        
        # Show the window
        print("Showing window...")
        self.window.show_all()
        print("Window shown successfully")
        
        # Connect to window close event
        self.window.connect("delete-event", self.on_window_delete_event)
        
        # Start with sudo password prompt
        if self.debug:
            print("Showing sudo prompt...")
        self.show_sudo_prompt()
        if self.debug:
            print("CrimsonCFGGUI initialization complete")
        
    def show_sudo_prompt(self):
        """Show sudo password prompt in the main window"""
        if self.debug:
            print("show_sudo_prompt: Starting...")
        # Clear main container
        for child in self.main_container.get_children():
            self.main_container.remove(child)
            
        # Apply CSS styling first
        if self.debug:
            print("show_sudo_prompt: Applying CSS...")
        self.apply_css()
            
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
        self.main_container.pack_start(header_container, False, False, 0)
            
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
        self.main_container.pack_start(content_box, True, True, 0)
        
        # Focus on password entry
        if self.debug:
            print("show_sudo_prompt: Setting focus on password entry...")
        self.password_entry.grab_focus()
        
        # Connect enter key
        self.password_entry.connect("activate", self.on_sudo_ok_clicked)
        
        if self.debug:
            print("show_sudo_prompt: Complete - all widgets should be visible")
        # Force a redraw
        self.window.queue_draw()
        if self.debug:
            print("show_sudo_prompt: Window redraw queued")
        self.window.show_all()
        
    def on_cancel_clicked(self, button):
        """Handle cancel button click"""
        self.window.destroy()
        
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
        self.window.queue_draw()
        
        if self.test_sudo_password(password):
            if self.debug:
                print("Password validated successfully!")
            self.status_label.set_text("Password validated successfully!")
            self.window.queue_draw()
            self.sudo_password = password
            
            # Regenerate GUI config from playbooks
            self.regenerate_gui_config()
            
            # Transition to main interface
            if self.debug:
                print("Transitioning to main interface...")
            self.show_main_interface()
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
            import subprocess
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
            
    def show_main_interface(self):
        """Show the main application interface"""
        if self.debug:
            print("Starting show_main_interface...")
        # Clear main container
        for child in self.main_container.get_children():
            self.main_container.remove(child)
            
        # Apply CSS styling
        if self.debug:
            print("Applying CSS...")
        self.apply_css()
        
        # Create the main interface content
        if self.debug:
            print("Setting up GUI...")
        self.setup_gui()
        
        if self.debug:
            print("Main interface setup complete")
        self.window.show_all()
        
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
            with open(local_file, 'w') as f:
                yaml.safe_dump({}, f)
        if local_file.exists():
            with open(local_file, 'r') as f:
                local_config = yaml.safe_load(f) or {}
        
        # Merge configurations (local overrides global)
        merged_config = {**all_config, **local_config}
        
        # Get actual system user
        import getpass
        system_user = getpass.getuser()
        
        # Convert to expected format
        config = {
            "categories": self.load_categories_from_yaml(),
            "settings": {
                "default_user": system_user,
                "ansible_folder": f"/home/{system_user}/Ansible",
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
                    self.config = self.load_config()
                else:
                    if self.debug:
                        print("Failed to regenerate GUI config")
            else:
                if self.debug:
                    print("PlaybookScanner not available, skipping config regeneration")
        except Exception as e:
            if self.debug:
                print(f"Error regenerating GUI config: {e}")
            
    def load_categories_from_yaml(self) -> Dict:
        """Load categories from gui_config.json (keeping the GUI structure separate)"""
        config_file = Path("conf/gui_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                json_config = json.load(f)
                return json_config.get("categories", {})
        else:
            return {}
            
    def apply_css(self):
        """Apply custom CSS styling"""
        try:
            css_data = """
            window {
                background-image: url('files/com.crimson.cfg.background.png');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                color: #ffffff;
            }
        
            .main-window {
                background-image: url('files/com.crimson.cfg.background.png');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                color: #ffffff;
            }
        
        .main-window label {
            color: #ffffff;
        }
        
        .main-window button {
            background: linear-gradient(135deg, #3c3c3c 0%, #4a4a4a 100%);
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        .main-window button:hover {
            background: linear-gradient(135deg, #4a4a4a 0%, #555555 100%);
            border-color: #666666;
        }
        
        .main-window button:active {
            background: linear-gradient(135deg, #555555 0%, #666666 100%);
        }
        
        .main-window treeview {
            background-color: rgba(60, 60, 60, 0.8);
            color: #ffffff;
            border-radius: 4px;
        }
        
        .main-window treeview:selected {
            background-color: #4a9eff;
        }
        
        .main-window frame {
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background-color: transparent;
        }
        
        .main-window frame > label {
            color: #ffffff;
            font-weight: bold;
        }
        
        .main-window .header-box {
            background-color: rgba(60, 60, 60, 0.4);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 15px;
            margin-left: 15px;
            margin-right: 15px;
        }
        
        .main-window progressbar {
            background-color: rgba(60, 60, 60, 0.8);
            color: #4a9eff;
            border-radius: 4px;
        }
        
        .main-window progressbar progress {
            background: linear-gradient(90deg, #4a9eff 0%, #5bb0ff 100%);
            border-radius: 4px;
        }
        
        .main-window listbox {
            background-color: rgba(60, 60, 60, 0.8);
            color: #ffffff;
            border-radius: 4px;
        }
        
        .main-window listbox row:selected {
            background-color: #4a9eff;
        }
        
        .main-window scrolledwindow {
            background-color: transparent;
        }
        
        .main-window scrolledwindow viewport {
            background-color: transparent;
        }
        
        .main-window notebook {
            background-color: rgba(0.2, 0.2, 0.2, 0.9);
        }
        
        .main-window notebook tab {
            background-color: rgba(0.2, 0.2, 0.2, 0.9);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            padding: 8px 16px;
        }
        
        .main-window notebook tab:active {
            background-color: rgba(0.3, 0.3, 0.3, 0.95);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        .main-window notebook tab label {
            color: #ffffff;
            font-weight: bold;
        }
        
        .rounded-background {
            background-color: rgba(60, 60, 60, 0.8);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        """
        
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(css_data.encode())
            
            # Apply CSS only to our window, not the entire screen
            style_context = self.window.get_style_context()
            style_context.add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"CSS loading failed: {e}")
            # Continue without CSS styling
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        if self.debug:
            print("setup_gui: Starting...")
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_container.pack_start(main_box, True, True, 0)
        
        if self.debug:
            print("setup_gui: Creating header...")
        # Header container (full width)
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
        
        if self.debug:
            print("setup_gui: Loading logo...")
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
                if self.debug:
                    print(f"Logo loading failed: {e}")
                logo_label = Gtk.Label(label="[Logo failed to load]")
                logo_box.pack_start(logo_label, False, False, 0)
        else:
            if self.debug:
                print(f"Logo not found at: {logo_path}")
            logo_label = Gtk.Label(label="[Logo not found]")
            logo_box.pack_start(logo_label, False, False, 0)
            
        header_box.pack_start(logo_box, False, False, 0)
        
        main_box.pack_start(header_container, False, False, 0)
        
        if self.debug:
            print("setup_gui: Creating content area...")
        # Content container with margins
        content_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_container.set_margin_start(15)
        content_container.set_margin_end(15)
        content_container.set_margin_bottom(15)
        main_box.pack_start(content_container, True, True, 0)
        
        # Create notebook for tabs
        self.notebook = Gtk.Notebook()
        
        # Style the notebook tab area to have a background
        self.notebook.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 0.9))
        
        content_container.pack_start(self.notebook, True, True, 0)
        
        # Add spacing between tab headers and content
        self.notebook.set_margin_top(45)
        
        # Main tab
        main_tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        main_tab.set_margin_top(15)
        
        # Add Material Design background to main tab
        main_tab.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        
        self.notebook.append_page(main_tab, Gtk.Label(label="Main"))
        
        # Main content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        main_tab.pack_start(content_box, True, True, 0)
        
        if self.debug:
            print("setup_gui: Creating left panel...")
        # Left panel - Categories
        left_frame = Gtk.Frame(label="Categories")
        left_frame.set_margin_end(15)
        content_box.pack_start(left_frame, False, False, 0)
        
        # Add background to categories
        left_background = Gtk.EventBox()
        left_background.set_visible_window(True)
        left_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        left_frame.add(left_background)
        
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        left_box.set_margin_start(15)
        left_box.set_margin_end(15)
        left_box.set_margin_top(15)
        left_box.set_margin_bottom(15)
        left_background.add(left_box)
        
        # Category buttons
        self.category_buttons = {}
        categories = list(self.config["categories"].keys())
        if self.debug:
            print(f"setup_gui: Found {len(categories)} categories: {categories}")
        if categories:
            self.current_category = categories[0]
            
        # Create radio button group
        radio_group = None
        
        for category in categories:
            cat_info = self.config["categories"][category]
            
            # Category button - first one sets the group, others join it
            btn = Gtk.RadioButton(label=category, group=radio_group)
            if radio_group is None:
                radio_group = btn
            btn.connect("toggled", self.on_category_changed, category)
            if category == self.current_category:
                btn.set_active(True)
            left_box.pack_start(btn, False, False, 0)
            self.category_buttons[category] = btn
            
            # Description
            if "description" in cat_info:
                desc_label = Gtk.Label(label=cat_info["description"])
                desc_label.set_line_wrap(True)
                desc_label.set_margin_start(25)
                desc_label.set_margin_top(5)
                left_box.pack_start(desc_label, False, False, 0)
                
        if self.debug:
            print("setup_gui: Creating center panel...")
        # Center panel - Playbooks
        center_frame = Gtk.Frame(label="Available Playbooks")
        center_frame.set_margin_end(15)
        content_box.pack_start(center_frame, True, True, 0)
        
        # Add background to available playbooks
        center_background = Gtk.EventBox()
        center_background.set_visible_window(True)
        center_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        center_frame.add(center_background)
        
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        center_box.set_margin_start(15)
        center_box.set_margin_end(15)
        center_box.set_margin_top(15)
        center_box.set_margin_bottom(15)
        center_background.add(center_box)
        
        # Playbook tree
        self.playbook_store = Gtk.ListStore(str, str, str, bool)  # name, essential, description, selected
        self.playbook_tree = Gtk.TreeView(model=self.playbook_store)
        
        # Columns
        renderer = Gtk.CellRendererText()
        col1 = Gtk.TreeViewColumn("Playbook", renderer, text=0)
        col1.set_expand(True)
        self.playbook_tree.append_column(col1)
        
        renderer2 = Gtk.CellRendererText()
        col2 = Gtk.TreeViewColumn("Essential", renderer2, text=1)
        col2.set_expand(False)
        self.playbook_tree.append_column(col2)
        
        renderer3 = Gtk.CellRendererText()
        col3 = Gtk.TreeViewColumn("Description", renderer3, text=2)
        col3.set_expand(True)
        self.playbook_tree.append_column(col3)
        
        # Selection
        self.playbook_tree.get_selection().connect("changed", self.on_playbook_selection_changed)
        
        # Scrollable tree
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.playbook_tree)
        center_box.pack_start(scrolled_window, True, True, 0)
        
        if self.debug:
            print("setup_gui: Creating right panel...")
        # Right panel - Controls and details
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_box.pack_start(right_box, False, False, 0)
        
        # Selection controls
        controls_frame = Gtk.Frame(label="Selection Controls")
        
        # Add background to selection controls
        controls_background = Gtk.EventBox()
        controls_background.set_visible_window(True)
        controls_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        controls_frame.add(controls_background)
        
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        controls_box.set_margin_start(15)
        controls_box.set_margin_end(15)
        controls_box.set_margin_top(15)
        controls_box.set_margin_bottom(15)
        controls_background.add(controls_box)
        
        select_all_btn = Gtk.Button(label="Select All")
        select_all_btn.connect("clicked", self.select_all)
        controls_box.pack_start(select_all_btn, False, False, 0)
        
        deselect_all_btn = Gtk.Button(label="Deselect All")
        deselect_all_btn.connect("clicked", self.deselect_all)
        controls_box.pack_start(deselect_all_btn, False, False, 0)
        
        select_essential_btn = Gtk.Button(label="Remove Essential")
        select_essential_btn.connect("clicked", self.remove_essential)
        controls_box.pack_start(select_essential_btn, False, False, 0)
        
        select_none_btn = Gtk.Button(label="Select None")
        select_none_btn.connect("clicked", self.select_none)
        controls_box.pack_start(select_none_btn, False, False, 0)
        
        right_box.pack_start(controls_frame, False, False, 0)
        
        # Selected items
        selected_frame = Gtk.Frame(label="Selected Items")
        
        # Add background to selected items
        selected_background = Gtk.EventBox()
        selected_background.set_visible_window(True)
        selected_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        selected_frame.add(selected_background)
        
        selected_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        selected_box.set_margin_start(15)
        selected_box.set_margin_end(15)
        selected_box.set_margin_top(15)
        selected_box.set_margin_bottom(15)
        selected_background.add(selected_box)
        
        self.selected_store = Gtk.ListStore(str)
        self.selected_tree = Gtk.TreeView(model=self.selected_store)
        
        renderer4 = Gtk.CellRendererText()
        col4 = Gtk.TreeViewColumn("Selected Playbooks", renderer4, text=0)
        self.selected_tree.append_column(col4)
        
        selected_scrolled = Gtk.ScrolledWindow()
        selected_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        selected_scrolled.add(self.selected_tree)
        selected_box.pack_start(selected_scrolled, True, True, 0)
        
        right_box.pack_start(selected_frame, True, True, 0)
        
        # Action buttons
        action_frame = Gtk.Frame(label="Actions")
        
        # Add background to actions
        action_background = Gtk.EventBox()
        action_background.set_visible_window(True)
        action_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        action_frame.add(action_background)
        
        action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        action_box.set_margin_start(15)
        action_box.set_margin_end(15)
        action_box.set_margin_top(15)
        action_box.set_margin_bottom(15)
        action_background.add(action_box)
        
        # Confirmation checkbox
        self.confirm_checkbox = Gtk.CheckButton(label="Accept and agree to the policy (see tooltip)")
        self.confirm_checkbox.set_tooltip_text("By checking this box, you acknowledge that:\n\n• THERE IS NO WARRANTY for this software or its installation process\n• The software is provided 'AS IS' without warranty of any kind\n• The entire risk as to the quality and performance is with you\n• You assume all responsibility for any damages, data loss, or system issues\n• No copyright holder or contributor can be held liable for any damages\n• You are solely responsible for backing up your system before installation\n• Installation may modify system files and could potentially break your system\n\nThis software is distributed under the GNU Affero General Public License v3. See LICENSE file for complete terms.")
        action_box.pack_start(self.confirm_checkbox, False, False, 0)
        
        self.install_btn = Gtk.Button(label="Install Selected")
        self.install_btn.connect("clicked", self.install_selected)
        action_box.pack_start(self.install_btn, False, False, 0)
        
        right_box.pack_start(action_frame, False, False, 0)
        
        # Progress section
        progress_frame = Gtk.Frame(label="Progress")
        
        # Add background to progress
        progress_background = Gtk.EventBox()
        progress_background.set_visible_window(True)
        progress_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.2))
        progress_frame.add(progress_background)
        
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        progress_box.set_margin_start(15)
        progress_box.set_margin_end(15)
        progress_box.set_margin_top(15)
        progress_box.set_margin_bottom(15)
        progress_background.add(progress_box)
        
        self.progress_bar = Gtk.ProgressBar()
        progress_box.pack_start(self.progress_bar, False, False, 0)
        
        self.status_label = Gtk.Label(label="Ready")
        progress_box.pack_start(self.status_label, False, False, 0)
        
        main_box.pack_start(progress_frame, False, False, 0)
        
        if self.debug:
            print("setup_gui: Creating logs tab...")
        # Logs tab
        logs_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        
        # Add Material Design background to logs tab
        logs_tab.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        logs_tab.set_margin_top(15)
        
        self.notebook.append_page(logs_tab, Gtk.Label(label="Logs"))
        
        # Debug controls
        debug_frame = Gtk.Frame(label="Debug Controls")
        
        # Add background to debug controls with same transparency as main interface
        debug_background = Gtk.EventBox()
        debug_background.set_visible_window(True)
        debug_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        debug_frame.add(debug_background)
        
        debug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        debug_box.set_margin_start(15)
        debug_box.set_margin_end(15)
        debug_box.set_margin_top(15)
        debug_box.set_margin_bottom(15)
        debug_background.add(debug_box)
        
        logs_tab.pack_start(debug_frame, False, False, 0)
        
        # Debug checkbox
        self.debug_checkbox = Gtk.CheckButton(label="Enable Debug Mode")
        self.debug_checkbox.set_active(self.debug)
        self.debug_checkbox.connect("toggled", self.on_debug_toggled)
        debug_box.pack_start(self.debug_checkbox, False, False, 0)
        
        # Clear logs button
        clear_logs_btn = Gtk.Button(label="Clear Logs")
        clear_logs_btn.connect("clicked", self.clear_logs)
        debug_box.pack_start(clear_logs_btn, False, False, 0)
        
        # Logs text view
        logs_frame = Gtk.Frame(label="Application Logs")
        
        # Add background to logs frame with same transparency as main interface
        logs_background = Gtk.EventBox()
        logs_background.set_visible_window(True)
        logs_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        logs_frame.add(logs_background)
        
        logs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        logs_box.set_margin_start(15)
        logs_box.set_margin_end(15)
        logs_box.set_margin_top(15)
        logs_box.set_margin_bottom(15)
        logs_background.add(logs_box)
        
        logs_tab.pack_start(logs_frame, True, True, 0)
        
        # Logs scrolled window
        logs_scrolled = Gtk.ScrolledWindow()
        logs_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        logs_box.pack_start(logs_scrolled, True, True, 0)
        
        # Logs text buffer
        self.logs_buffer = Gtk.TextBuffer()
        self.logs_textview = Gtk.TextView(buffer=self.logs_buffer)
        self.logs_textview.set_editable(False)
        self.logs_textview.set_monospace(True)
        
        # Add solid background to logs text view (no transparency)
        self.logs_textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 1.0))
        
        logs_scrolled.add(self.logs_textview)
        
        # Initialize logs
        self.log_message("CrimsonCFG started")
        if self.debug:
            self.log_message("Debug mode enabled")
        
        if self.debug:
            print("setup_gui: Initializing playbook list...")
        # Initialize the playbook list
        self.update_playbook_list()
        
        # Automatically select essential playbooks
        self.select_essential_playbooks()
        
        if self.debug:
            print("setup_gui: Complete")
        
        # Connect window close event
        self.window.connect("destroy", Gtk.main_quit)
        
    def on_category_changed(self, button, category):
        """Handle category selection change"""
        if button.get_active():
            self.current_category = category
            self.update_playbook_list()
            
    def update_playbook_list(self):
        """Update the playbook list based on selected category"""
        # Clear existing items
        self.playbook_store.clear()
        
        if self.current_category not in self.config["categories"]:
            return
            
        cat_info = self.config["categories"][self.current_category]
        for playbook in cat_info["playbooks"]:
            essential = "✓" if playbook.get("essential", False) else ""
            description = playbook.get("description", "")
            playbook_key = f"{self.current_category}:{playbook['name']}"
            selected = playbook_key in self.selected_playbooks
            
            self.playbook_store.append([
                playbook["name"],
                essential,
                description,
                selected
            ])
            
    def on_playbook_selection_changed(self, selection):
        """Handle playbook selection change"""
        model, treeiter = selection.get_selected()
        if treeiter:
            playbook_name = model[treeiter][0]
            playbook_key = f"{self.current_category}:{playbook_name}"
            
            if playbook_key in self.selected_playbooks:
                self.selected_playbooks.remove(playbook_key)
                model[treeiter][3] = False
            else:
                self.selected_playbooks.add(playbook_key)
                model[treeiter][3] = True
                
            self.update_selected_display()
            
    def select_all(self, button):
        """Select all playbooks in current category"""
        if self.current_category not in self.config["categories"]:
            return
            
        for playbook in self.config["categories"][self.current_category]["playbooks"]:
            playbook_key = f"{self.current_category}:{playbook['name']}"
            self.selected_playbooks.add(playbook_key)
            
        self.update_playbook_list()
        self.update_selected_display()
        
    def deselect_all(self, button):
        """Deselect all playbooks in current category"""
        if self.current_category not in self.config["categories"]:
            return
            
        for playbook in self.config["categories"][self.current_category]["playbooks"]:
            playbook_key = f"{self.current_category}:{playbook['name']}"
            self.selected_playbooks.discard(playbook_key)
            
        self.update_playbook_list()
        self.update_selected_display()
        
    def select_essential_playbooks(self):
        """Automatically select all essential playbooks across all categories"""
        for category, cat_info in self.config["categories"].items():
            for playbook in cat_info["playbooks"]:
                if playbook.get("essential", False):
                    playbook_key = f"{category}:{playbook['name']}"
                    self.selected_playbooks.add(playbook_key)
                    
        self.update_playbook_list()
        self.update_selected_display()
        
    def remove_essential(self, button):
        """Remove all essential playbooks with warning"""
        # Show warning dialog
        warning_dialog = Gtk.MessageDialog(
            transient_for=self.window,
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
            for category, cat_info in self.config["categories"].items():
                for playbook in cat_info["playbooks"]:
                    if playbook.get("essential", False):
                        playbook_key = f"{category}:{playbook['name']}"
                        self.selected_playbooks.discard(playbook_key)
                        
            self.update_playbook_list()
            self.update_selected_display()
            
    def select_essential(self, button):
        """Select all essential playbooks across all categories"""
        for category, cat_info in self.config["categories"].items():
            for playbook in cat_info["playbooks"]:
                if playbook.get("essential", False):
                    playbook_key = f"{category}:{playbook['name']}"
                    self.selected_playbooks.add(playbook_key)
                    
        self.update_playbook_list()
        self.update_selected_display()
        
    def select_none(self, button):
        """Deselect all playbooks"""
        self.selected_playbooks.clear()
        self.update_playbook_list()
        self.update_selected_display()
        
    def update_selected_display(self):
        """Update the selected items display"""
        self.selected_store.clear()
        
        for playbook_key in sorted(self.selected_playbooks):
            category, name = playbook_key.split(":", 1)
            self.selected_store.append([f"{category}: {name}"])
            
    def get_selected_playbooks(self) -> List[Dict]:
        """Get list of selected playbooks with their details"""
        selected = []
        for playbook_key in self.selected_playbooks:
            category, name = playbook_key.split(":", 1)
            if category in self.config["categories"]:
                for playbook in self.config["categories"][category]["playbooks"]:
                    if playbook["name"] == name:
                        selected.append({
                            "category": category,
                            "name": playbook["name"],
                            "path": playbook["path"],
                            "description": playbook.get("description", ""),
                            "essential": playbook.get("essential", False)
                        })
                        break
        return selected
        

        
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
        if not self.confirm_checkbox.get_active():
            warning_dialog = Gtk.MessageDialog(
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
            
        # Switch to logs tab to show installation progress
        self.notebook.set_current_page(1)  # Switch to logs tab (index 1)
        
        # Log the selected playbooks
        self.log_message("=== INSTALLATION STARTED ===")
        self.log_message(f"Selected playbooks ({len(selected)}):")
        for playbook in selected:
            essential_mark = " (Essential)" if playbook["essential"] else ""
            self.log_message(f"  • {playbook['category']}: {playbook['name']}{essential_mark}")
        self.log_message("=== BEGINNING INSTALLATION ===")
        
        # Start installation in a separate thread
        self.installation_running = True
        self.install_btn.set_sensitive(False)
        thread = threading.Thread(target=self.run_installation, args=(selected,))
        thread.daemon = True
        thread.start()
            
    def run_installation(self, selected_playbooks):
        """Run the installation process"""
        try:
            GLib.idle_add(self.log_message, "Starting installation process...")
            GLib.idle_add(self.status_label.set_text, "Installing Ansible...")
            GLib.idle_add(self.progress_bar.set_fraction, 0.1)
            
            # Install Ansible if needed
            if not self.install_ansible():
                GLib.idle_add(self.log_message, "Failed to install Ansible")
                GLib.idle_add(self.status_label.set_text, "Failed to install Ansible")
                GLib.idle_add(self.show_error_dialog, "Failed to install Ansible")
                return
                
            GLib.idle_add(self.progress_bar.set_fraction, 0.2)
            GLib.idle_add(self.status_label.set_text, "Installing selected playbooks...")
            
            # Run each playbook
            total_playbooks = len(selected_playbooks)
            for i, playbook in enumerate(selected_playbooks):
                progress = 0.2 + (i / total_playbooks) * 0.7
                GLib.idle_add(self.progress_bar.set_fraction, progress)
                GLib.idle_add(self.status_label.set_text, f"Installing {playbook['name']}...")
                GLib.idle_add(self.log_message, f"Installing {playbook['name']}...")
                
                if not self.run_playbook(playbook):
                    GLib.idle_add(self.log_message, f"Failed to install {playbook['name']}")
                    GLib.idle_add(self.status_label.set_text, f"Failed to install {playbook['name']}")
                    GLib.idle_add(self.show_error_dialog, f"Failed to install {playbook['name']}")
                    return
                    
            GLib.idle_add(self.progress_bar.set_fraction, 1.0)
            GLib.idle_add(self.status_label.set_text, "Installation completed successfully!")
            GLib.idle_add(self.log_message, "Installation completed successfully!")
            GLib.idle_add(self.show_success_dialog, "All selected playbooks have been installed successfully!")
            
        except Exception as e:
            GLib.idle_add(self.log_message, f"Installation failed: {e}")
            GLib.idle_add(self.status_label.set_text, f"Installation failed: {e}")
            GLib.idle_add(self.show_error_dialog, f"Installation failed: {e}")
        finally:
            GLib.idle_add(self.install_btn.set_sensitive, True)
            GLib.idle_add(setattr, self, 'installation_running', False)
            
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
            
    def install_ansible(self) -> bool:
        """Install Ansible if not present"""
        try:
            result = subprocess.run(["ansible", "--version"], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(["sudo", "-S", "apt-get", "update"], 
                             input=f"{self.sudo_password}\n".encode(), check=True)
                subprocess.run(["sudo", "-S", "apt-get", "install", "-y", "ansible"], 
                             input=f"{self.sudo_password}\n".encode(), check=True)
                return True
            except subprocess.CalledProcessError:
                return False
                
    def run_playbook(self, playbook: Dict) -> bool:
        """Run a single playbook"""
        try:
            # Check if inventory file exists
            if not os.path.exists(self.inventory_file):
                GLib.idle_add(self.log_message, f"Error: Inventory file not found at {self.inventory_file}")
                return False
                
            # Check if playbook file exists (in original location)
            playbook_path = playbook['path']
            if not os.path.exists(playbook_path):
                GLib.idle_add(self.log_message, f"Error: Playbook file not found at {playbook_path}")
                return False
                
            cmd = [
                "ansible-playbook",
                "-i", self.inventory_file,
                playbook_path,
                "--extra-vars", f"user={self.user} user_home={self.user_home} ansible_folder={self.ansible_folder}"
            ]
            
            # Add additional variables for specific playbooks
            if playbook['name'] == 'Git':
                cmd.extend(["--extra-vars", f"git_username={self.user} git_email={self.config.get('settings', {}).get('git_email', 'user@example.com')}"])
            
            env = os.environ.copy()
            if self.sudo_password:
                env["ANSIBLE_BECOME_PASS"] = self.sudo_password
            env["ANSIBLE_BECOME"] = "true"
            
            GLib.idle_add(self.log_message, f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
            GLib.idle_add(self.log_message, f"Playbook {playbook['name']} completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            GLib.idle_add(self.log_message, f"Playbook {playbook['name']} failed with error: {e}")
            GLib.idle_add(self.log_message, f"Error output: {e.stderr}")
            return False
            
    def setup_ansible_environment(self):
        """Setup Ansible directory and inventory file"""
        try:
            # Create Ansible directory if it doesn't exist
            if not os.path.exists(self.ansible_folder):
                os.makedirs(self.ansible_folder, exist_ok=True)
                if self.debug:
                    print(f"Created Ansible directory: {self.ansible_folder}")
            
            # Create inventory file if it doesn't exist
            if not os.path.exists(self.inventory_file):
                inventory_content = f"""[all]
localhost ansible_connection=local ansible_user={self.user}

[local]
localhost
"""
                with open(self.inventory_file, 'w') as f:
                    f.write(inventory_content)
                if self.debug:
                    print(f"Created inventory file: {self.inventory_file}")
                    
        except Exception as e:
            if self.debug:
                print(f"Error setting up Ansible environment: {e}")
    
    def log_message(self, message):
        """Add a message to the logs"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to text buffer
        self.logs_buffer.insert_at_cursor(log_entry)
        
        # Auto-scroll to bottom
        self.logs_textview.scroll_to_iter(self.logs_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        
        # Also print to console if debug is enabled
        if self.debug:
            print(f"LOG: {message}")
    
    def clear_logs(self, button):
        """Clear the logs display"""
        self.logs_buffer.set_text("")
        self.log_message("Logs cleared")
    
    def on_debug_toggled(self, checkbox):
        """Handle debug checkbox toggle"""
        self.debug = checkbox.get_active()
        if self.debug:
            self.log_message("Debug mode enabled")
        else:
            self.log_message("Debug mode disabled")
        
    def on_window_delete_event(self, widget, event):
        """Handle window close event"""
        print("Window close event received")
        # Release the application hold
        self.application.release()
        return False  # Allow the window to close
        
    def run(self):
        """Show the window and start the main loop"""
        # The window is already shown in __init__, and the application manages the main loop
        pass 