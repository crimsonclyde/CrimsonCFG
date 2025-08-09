#!/usr/bin/env python3
"""
CrimsonCFG GUI Builder
Handles main interface construction and styling
"""

import gi
import os
import getpass
import yaml
from pathlib import Path
import json
# Add ruamel.yaml import
from ruamel.yaml import YAML
from .admin_tab import AdminTab
from .logs_tab import LogsTab
from .config_tab import ConfigTab
from .main_tab import MainTab
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk  # type: ignore

class GUIBuilder:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        self.notebook = None
        
    def apply_css(self):
        """Apply custom CSS styling"""
        try:
            if self.debug:
                print("GUIBuilder: Starting apply_css...")
            
            # Load user config for background image and color
            config_dir = Path.home() / ".config/com.mdm.manager.cfg"
            local_file = config_dir / "local.yml"
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
                    app_background_image = local_config.get("app_background_image", None)
                    background_color = local_config.get("background_color", "#181a20")
            else:
                app_background_image = None
                background_color = "#181a20"
                
            if self.debug:
                print(f"GUIBuilder: Background image: {app_background_image}")
                print(f"GUIBuilder: Background color: {background_color}")
            
            if app_background_image:
                css_data = f"""
                window, .main-window {{
                    background-image: url('{app_background_image}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    color: #ffffff;
                }}
                """
                if self.debug:
                    print(f"GUIBuilder: Applied background image CSS")
            else:
                css_data = f"""
                window, .main-window {{
                    background-color: {background_color};
                    color: #ffffff;
                }}
                """
                if self.debug:
                    print(f"GUIBuilder: Applied background color CSS")
            
            css_data += """
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
                background-color: transparent;
            }
            .main-window notebook tab {
                background-color: rgba(0.2, 0.2, 0.2, 0.9);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 8px 16px;
            }
            .main-window button.selected {
                border: 3px solid #4a9eff;
                border-radius: 8px;
                background: linear-gradient(135deg, #4a4a4a 0%, #555555 100%);
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
            
            style_context = self.main_window.window.get_style_context()
            # Remove previous provider if present
            if hasattr(self, '_css_provider') and self._css_provider is not None:
                style_context.remove_provider(self._css_provider)
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(css_data.encode())
            style_context.add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            self._css_provider = css_provider
            
            if self.debug:
                print("GUIBuilder: CSS applied successfully")
                
        except Exception as e:
            print(f"CSS loading failed: {e}")
            # Continue without CSS styling
        
    def show_main_interface(self):
        """Show the main application interface"""
        if self.debug:
            print("GUIBuilder: Starting show_main_interface...")
        # Clear main container
        for child in self.main_window.main_container.get_children():
            self.main_window.main_container.remove(child)
            
        # Apply CSS styling
        if self.debug:
            print("GUIBuilder: Applying CSS...")
        self.apply_css()
        
        # Create the main interface content
        if self.debug:
            print("GUIBuilder: Setting up GUI...")
        self.setup_gui()
        
        if self.debug:
            print("GUIBuilder: Main interface setup complete")
        self.main_window.window.show_all()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        if self.debug:
            print("GUIBuilder: setup_gui: Starting...")
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.main_window.main_container.pack_start(main_box, True, True, 0)
        
        if self.debug:
            print("GUIBuilder: setup_gui: Creating header...")
        # Header container (full width)
        header_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_container.set_hexpand(True)
        header_container.set_margin_top(6)
        header_container.set_margin_bottom(6)
        
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
        app_name = self.main_window.config.get('settings', {}).get('app_name')
        if not app_name:
            try:
                # Load local.yml
                local_config = {}
                config_dir = Path.home() / ".config/com.mdm.manager.cfg"
                local_file = config_dir / "local.yml"
                if local_file.exists():
                    with open(local_file, 'r') as f:
                        local_config = yaml.safe_load(f) or {}
                
                # Merge configurations (local overrides all)
                merged_config = local_config
                app_name = merged_config.get('app_name', 'CrimsonCFG')
            except Exception:
                app_name = 'CrimsonCFG'
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='x-large' weight='bold'>{app_name}</span>")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_valign(Gtk.Align.CENTER)
        title_box.pack_start(title_label, False, False, 0)
        app_subtitle = self.main_window.config.get('settings', {}).get('app_subtitle')
        if not app_subtitle:
            try:
                # Load local.yml
                local_config = {}
                config_dir = Path.home() / ".config/com.mdm.manager.cfg"
                local_file = config_dir / "local.yml"
                if local_file.exists():
                    with open(local_file, 'r') as f:
                        local_config = yaml.safe_load(f) or {}
                # Merge configurations (local overrides all)
                merged_config = local_config
                app_subtitle = merged_config.get('app_subtitle', 'System Configuration Manager')
            except Exception:
                app_subtitle = 'System Configuration Manager'
        subtitle_label = Gtk.Label()
        subtitle_label.set_markup(f"<span size='medium'>{app_subtitle}</span>")
        subtitle_label.set_halign(Gtk.Align.START)
        subtitle_label.set_valign(Gtk.Align.CENTER)
        title_box.pack_start(subtitle_label, False, False, 0)
        
        header_box.pack_start(title_box, False, False, 0)
        
        if self.debug:
            print("GUIBuilder: setup_gui: Loading logo...")
        # Logo (right side)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        logo_box.set_halign(Gtk.Align.CENTER)
        
        # Try to load logo
        try:
            # Load local.yml
            local_config = {}
            config_dir = Path.home() / ".config/com.mdm.manager.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
            
            # Merge configurations (local overrides all)
            merged_config = local_config
            logo_path = merged_config.get('app_logo', os.path.join("files", "app", "com.crimson.cfg.icon.png"))
        except Exception:
            logo_path = os.path.join("files", "app", "com.crimson.cfg.icon.png")
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
            print("GUIBuilder: setup_gui: Creating content area...")
        # Content container with margins
        content_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_container.set_margin_start(8)
        content_container.set_margin_end(8)
        content_container.set_margin_bottom(8)
        main_box.pack_start(content_container, True, True, 0)
        
        # Create notebook for tabs
        self.notebook = Gtk.Notebook()
        
        # Style the notebook tab area to have a transparent background
        self.notebook.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 0.3))
        
        if self.debug:
            print("GUIBuilder: Notebook background set with 0.3 opacity")
        
        content_container.pack_start(self.notebook, True, True, 0)
        
        # Add spacing between tab headers and content
        self.notebook.set_margin_top(16)
        
        # Main tab - Use MainTab class
        main_tab = MainTab(self.main_window)
        self.notebook.append_page(main_tab, Gtk.Label(label="Main"))
        
        # Progress section (outside of tabs, in main container)
        progress_frame = Gtk.Frame(label="Progress")
        
        # Add background to progress
        progress_background = Gtk.EventBox()
        progress_background.set_visible_window(True)
        progress_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.2))
        progress_frame.add(progress_background)
        
        if self.debug:
            print("GUIBuilder: Progress background set with 0.2 opacity")
        
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        progress_box.set_margin_start(15)
        progress_box.set_margin_end(15)
        progress_box.set_margin_top(15)
        progress_box.set_margin_bottom(15)
        progress_background.add(progress_box)
        
        self.main_window.progress_bar = Gtk.ProgressBar()
        progress_box.pack_start(self.main_window.progress_bar, False, False, 0)
        
        self.main_window.status_label = Gtk.Label(label="Ready")
        progress_box.pack_start(self.main_window.status_label, False, False, 0)
        
        main_box.pack_start(progress_frame, False, False, 0)
        
        # Logs tab - Use LogsTab class
        logs_tab = LogsTab(self.main_window)
        self.notebook.append_page(logs_tab, Gtk.Label(label="Logs"))
        
        # Configuration tab - Use ConfigTab class
        config_tab = ConfigTab(self.main_window)
        self.notebook.append_page(config_tab, Gtk.Label(label="Configuration"))
        
        # Administration tab - Use AdminTab class
        admin_tab = AdminTab(self.main_window)
        self.notebook.append_page(admin_tab, Gtk.Label(label="Administration"))
        
        # Initialize the playbook list
        self.main_window.update_playbook_list()
        
        # Automatically select essential playbooks
        self.main_window.select_essential_playbooks()
        
        if self.debug:
            print("GUIBuilder: setup_gui: Complete")
        
        # Connect window close event - let the application handle cleanup
        self.main_window.window.connect("delete-event", self.main_window.on_window_delete_event) 