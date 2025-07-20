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
            # Load user config for background image and color
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
            if not local_file.exists():
                with open(local_file, 'w') as f:
                    yaml.safe_dump({}, f)
            background_image = None
            background_color = "#181a20"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
                    background_image = local_config.get("background_image", None)
                    background_color = local_config.get("background_color", "#181a20")
            if background_image:
                css_data = f"""
                window, .main-window {{
                    background-image: url('{background_image}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    color: #ffffff;
                }}
                """
            else:
                css_data = f"""
                window, .main-window {{
                    background-color: {background_color};
                    color: #ffffff;
                }}
                """
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
        except Exception as e:
            print(f"CSS loading failed: {e}")
            # Continue without CSS styling
        
    def show_main_interface(self):
        """Show the main application interface"""
        if self.debug:
            print("Starting show_main_interface...")
        # Clear main container
        for child in self.main_window.main_container.get_children():
            self.main_window.main_container.remove(child)
            
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
        self.main_window.window.show_all()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        if self.debug:
            print("setup_gui: Starting...")
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_window.main_container.pack_start(main_box, True, True, 0)
        
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
        app_name = self.main_window.config.get('settings', {}).get('app_name')
        if not app_name:
            try:
                # Load local.yml
                local_config = {}
                config_dir = Path.home() / ".config/com.crimson.cfg"
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
                config_dir = Path.home() / ".config/com.crimson.cfg"
                local_file = config_dir / "local.yml"
                if local_file.exists():
                    with open(local_file, 'r') as f:
                        local_config = yaml.safe_load(f) or {}
                
                # Merge configurations (local overrides all)
                merged_config = local_config
                app_subtitle = merged_config.get('app_subtitle', 'App &amp; Customization Selector')
            except Exception:
                app_subtitle = 'App &amp; Customization Selector'
        subtitle_label = Gtk.Label()
        subtitle_label.set_markup(f"<span size='medium'>{app_subtitle}</span>")
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
        try:
            # Load local.yml
            local_config = {}
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
            
            # Merge configurations (local overrides all)
            merged_config = local_config
            logo_path = merged_config.get('app_logo', os.path.join("files", "com.crimson.cfg.logo.png"))
        except Exception:
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
        self.main_window.category_buttons = {}
        categories = list(self.main_window.config["categories"].keys())
        if self.debug:
            print(f"setup_gui: Found {len(categories)} categories: {categories}")
        if categories:
            self.main_window.current_category = categories[0]
            
        # Create radio button group
        radio_group = None
        
        for category in categories:
            cat_info = self.main_window.config["categories"][category]
            
            # Category button - first one sets the group, others join it
            btn = Gtk.RadioButton(label=category, group=radio_group)
            if radio_group is None:
                radio_group = btn
            btn.connect("toggled", self.main_window.on_category_changed, category)
            if category == self.main_window.current_category:
                btn.set_active(True)
            left_box.pack_start(btn, False, False, 0)
            self.main_window.category_buttons[category] = btn
            

                
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
        self.main_window.playbook_store = Gtk.ListStore(str, str, str, bool)  # name, essential, description, selected
        self.main_window.playbook_tree = Gtk.TreeView(model=self.main_window.playbook_store)
        
        # Columns
        renderer = Gtk.CellRendererText()
        col1 = Gtk.TreeViewColumn("Playbook", renderer, text=0)
        col1.set_expand(True)
        self.main_window.playbook_tree.append_column(col1)
        
        renderer2 = Gtk.CellRendererText()
        col2 = Gtk.TreeViewColumn("Essential", renderer2, text=1)
        col2.set_expand(False)
        self.main_window.playbook_tree.append_column(col2)
        
        renderer3 = Gtk.CellRendererText()
        col3 = Gtk.TreeViewColumn("Description", renderer3, text=2)
        col3.set_expand(True)
        self.main_window.playbook_tree.append_column(col3)
        
        # Selection
        self.main_window.playbook_tree.get_selection().connect("changed", self.main_window.on_playbook_selection_changed)
        
        # Scrollable tree
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.main_window.playbook_tree)
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
        select_all_btn.connect("clicked", self.main_window.select_all)
        controls_box.pack_start(select_all_btn, False, False, 0)
        
        deselect_all_btn = Gtk.Button(label="Deselect All")
        deselect_all_btn.connect("clicked", self.main_window.deselect_all)
        controls_box.pack_start(deselect_all_btn, False, False, 0)
        
        select_essential_btn = Gtk.Button(label="Remove Essential")
        select_essential_btn.connect("clicked", self.main_window.remove_essential)
        controls_box.pack_start(select_essential_btn, False, False, 0)
        
        select_none_btn = Gtk.Button(label="Select None")
        select_none_btn.connect("clicked", self.main_window.select_none)
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
        
        self.main_window.selected_store = Gtk.ListStore(str)
        self.main_window.selected_tree = Gtk.TreeView(model=self.main_window.selected_store)
        
        renderer4 = Gtk.CellRendererText()
        col4 = Gtk.TreeViewColumn("Selected Playbooks", renderer4, text=0)
        self.main_window.selected_tree.append_column(col4)
        
        selected_scrolled = Gtk.ScrolledWindow()
        selected_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        selected_scrolled.add(self.main_window.selected_tree)
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
        self.main_window.confirm_checkbox = Gtk.CheckButton(label="Accept and agree to the policy (see tooltip)")
        self.main_window.confirm_checkbox.set_tooltip_text("By checking this box, you acknowledge that:\n\n• THERE IS NO WARRANTY for this software or its installation process\n• The software is provided 'AS IS' without warranty of any kind\n• The entire risk as to the quality and performance is with you\n• You assume all responsibility for any damages, data loss, or system issues\n• No copyright holder or contributor can be held liable for any damages\n• You are solely responsible for backing up your system before installation\n• Installation may modify system files and could potentially break your system\n\nThis software is distributed under the GNU Affero General Public License v3. See LICENSE file for complete terms.")
        action_box.pack_start(self.main_window.confirm_checkbox, False, False, 0)
        
        self.main_window.install_btn = Gtk.Button(label="Install Selected")
        self.main_window.install_btn.connect("clicked", self.main_window.install_selected)
        action_box.pack_start(self.main_window.install_btn, False, False, 0)
        
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
        
        self.main_window.progress_bar = Gtk.ProgressBar()
        progress_box.pack_start(self.main_window.progress_bar, False, False, 0)
        
        self.main_window.status_label = Gtk.Label(label="Ready")
        progress_box.pack_start(self.main_window.status_label, False, False, 0)
        
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
        self.main_window.debug_checkbox = Gtk.CheckButton(label="Enable Debug Mode")
        self.main_window.debug_checkbox.set_active(self.debug)
        self.main_window.debug_checkbox.connect("toggled", self.main_window.on_debug_toggled)
        debug_box.pack_start(self.main_window.debug_checkbox, False, False, 0)
        
        # Clear logs button
        clear_logs_btn = Gtk.Button(label="Clear Logs")
        clear_logs_btn.connect("clicked", self.main_window.clear_logs)
        debug_box.pack_start(clear_logs_btn, False, False, 0)

        # Copy logs button
        copy_logs_btn = Gtk.Button(label="Copy Logs")
        def on_copy_logs_clicked(btn):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            start_iter = self.main_window.logs_buffer.get_start_iter()
            end_iter = self.main_window.logs_buffer.get_end_iter()
            text = self.main_window.logs_buffer.get_text(start_iter, end_iter, True)
            clipboard.set_text(text, -1)
        copy_logs_btn.connect("clicked", on_copy_logs_clicked)
        debug_box.pack_start(copy_logs_btn, False, False, 0)
        
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
        self.main_window.logs_buffer = Gtk.TextBuffer()
        self.main_window.logs_textview = Gtk.TextView(buffer=self.main_window.logs_buffer)
        self.main_window.logs_textview.set_editable(False)
        self.main_window.logs_textview.set_monospace(True)
        
        # Add solid background to logs text view (no transparency)
        self.main_window.logs_textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 1.0))
        # Improve selection color for visibility
        css = b"""
        textview text selection {
            background-color: #4a9eff;
            color: #181a20;
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        self.main_window.logs_textview.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        logs_scrolled.add(self.main_window.logs_textview)
        
        # Initialize logs
        self.main_window.logger.log_message("CrimsonCFG started")
        if self.debug:
            self.main_window.logger.log_message("Debug mode enabled")
        
        if self.debug:
            print("setup_gui: Creating configuration tab...")
        # Configuration tab
        config_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        
        # Add Material Design background to config tab
        config_tab.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        config_tab.set_margin_top(15)
        
        self.notebook.append_page(config_tab, Gtk.Label(label="Configuration"))
        
        # Configuration frame
        config_frame = Gtk.Frame(label="Current Configuration")
        
        # Add background to config frame
        config_background = Gtk.EventBox()
        config_background.set_visible_window(True)
        config_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        config_frame.add(config_background)
        
        config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        config_box.set_margin_start(15)
        config_box.set_margin_end(15)
        config_box.set_margin_top(15)
        config_box.set_margin_bottom(15)
        config_background.add(config_box)
        
        config_tab.pack_start(config_frame, True, True, 0)
        
        # Configuration controls
        config_controls_frame = Gtk.Frame(label="Configuration Controls")
        
        # Add background to config controls
        config_controls_background = Gtk.EventBox()
        config_controls_background.set_visible_window(True)
        config_controls_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        config_controls_frame.add(config_controls_background)
        
        config_controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        config_controls_box.set_margin_start(15)
        config_controls_box.set_margin_end(15)
        config_controls_box.set_margin_top(15)
        config_controls_box.set_margin_bottom(15)
        config_controls_background.add(config_controls_box)
        
        config_tab.pack_start(config_controls_frame, False, False, 0)
        
        # Refresh button
        refresh_config_btn = Gtk.Button(label="Refresh Configuration")
        refresh_config_btn.connect("clicked", self.refresh_config_display)
        config_controls_box.pack_start(refresh_config_btn, False, False, 0)
        
        # Configuration scrolled window
        # config_scrolled = Gtk.ScrolledWindow()
        # config_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        # config_box.pack_start(config_scrolled, True, True, 0)
        
        # # Configuration text buffer
        # self.main_window.config_buffer = Gtk.TextBuffer()
        # self.main_window.config_textview = Gtk.TextView(buffer=self.main_window.config_buffer)
        # self.main_window.config_textview.set_editable(False)
        # self.main_window.config_textview.set_monospace(True)
        
        # # Add solid background to config text view
        # self.main_window.config_textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 1.0))
        
        # config_scrolled.add(self.main_window.config_textview)
        
        # # Populate configuration display
        # self.update_config_display()

        # --- BEGIN: Editable Configuration Form ---
        import subprocess
        
        # Load current config from local.yml
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        if not local_file.exists():
            with open(local_file, 'w') as f:
                yaml.safe_dump({}, f)
        # Use ruamel.yaml for comment preservation
        yaml_ruamel = YAML()
        yaml_ruamel.preserve_quotes = True
        with open(local_file, 'r') as f:
            try:
                local_config = yaml_ruamel.load(f) or {}
            except Exception:
                local_config = {}

        # Ensure user and user_home are set in local_config
        system_user = getpass.getuser()
        updated = False
        
        # Initialize all user-modifiable variables if they don't exist
        default_vars = {
            "user": system_user,
            "user_home": f"/home/{system_user}",
            "apt_packages": [],
            "snap_packages": [],
            "app_name": "CrimsonCFG",
            "app_subtitle": "App & Customization Selector",
            "background_color": "#181a20",
            "debug": 0,
            "git_username": "",
            "git_email": "",
            "ssh_private_key_name": "id_rsa",
            "ssh_public_key_name": "id_rsa.pub",
            "ssh_private_key_content": "",
            "ssh_public_key_content": "",
            "ssh_config_content": "",
            "chromium_homepage_url": "",
            "working_directory": f"/home/{system_user}/Ansible"
        }
        
        for var_name, default_value in default_vars.items():
            if var_name not in local_config:
                local_config[var_name] = default_value
                updated = True
        
        if updated:
            with open(local_file, 'w') as f:
                yaml_ruamel.dump(local_config, f)
        
        def get_git_config(key):
            try:
                return subprocess.check_output(["git", "config", "--global", key], text=True).strip()
            except Exception:
                return ""
        
        def get_val(key, default=""):
            val = local_config.get(key, None)
            if val is not None:
                return val
            # For git_username and git_email, try system git config
            if key == "git_username":
                return get_git_config("user.name") or default
            if key == "git_email":
                return get_git_config("user.email") or default
            return default
        
        # Create a scrolled window for the config notebook
        config_form_scrolled = Gtk.ScrolledWindow()
        config_form_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        config_form_scrolled.set_min_content_height(400)
        config_form_scrolled.set_min_content_width(600)
        config_box.pack_start(config_form_scrolled, True, True, 0)
        
        # Create the notebook (tabs)
        config_notebook = Gtk.Notebook()
        config_form_scrolled.add(config_notebook)
        
        # --- Git Tab ---
        git_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        git_box.set_margin_start(10)
        git_box.set_margin_end(10)
        git_box.set_margin_top(10)
        git_box.set_margin_bottom(10)
        
        git_username_label = Gtk.Label(label="Git Username:")
        git_username_entry = Gtk.Entry()
        git_username_entry.set_text(get_val("git_username"))
        git_box.pack_start(git_username_label, False, False, 0)
        git_box.pack_start(git_username_entry, False, False, 0)
        
        git_email_label = Gtk.Label(label="Git Email:")
        git_email_entry = Gtk.Entry()
        git_email_entry.set_text(get_val("git_email"))
        git_box.pack_start(git_email_label, False, False, 0)
        git_box.pack_start(git_email_entry, False, False, 0)
        
        config_notebook.append_page(git_box, Gtk.Label(label="Git"))
        
        # --- SSH Tab ---
        ssh_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        ssh_box.set_margin_start(10)
        ssh_box.set_margin_end(10)
        ssh_box.set_margin_top(10)
        ssh_box.set_margin_bottom(10)

        # Private Key Name
        priv_key_name_label = Gtk.Label(label="Private Key Name:")
        priv_key_name_label.set_xalign(0)
        ssh_box.pack_start(priv_key_name_label, False, False, 0)
        priv_key_name_entry = Gtk.Entry()
        priv_key_name_entry.set_text(get_val("ssh_private_key_name", "id_rsa"))
        ssh_box.pack_start(priv_key_name_entry, False, False, 0)

        # SSH Private Key Frame
        ssh_priv_frame = Gtk.Frame(label="SSH Private Key")
        ssh_priv_frame.set_margin_bottom(8)
        ssh_priv_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ssh_priv_box.set_margin_start(8)
        ssh_priv_box.set_margin_end(8)
        ssh_priv_box.set_margin_top(8)
        ssh_priv_box.set_margin_bottom(8)
        ssh_priv_buffer = Gtk.TextBuffer()
        ssh_priv_buffer.set_text(get_val("ssh_private_key_content"))
        ssh_priv_view = Gtk.TextView(buffer=ssh_priv_buffer)
        ssh_priv_view.set_monospace(True)
        ssh_priv_view.set_wrap_mode(Gtk.WrapMode.WORD)
        ssh_priv_view.set_hexpand(True)
        ssh_priv_view.set_vexpand(True)
        ssh_priv_view.set_size_request(-1, 80)
        ssh_priv_box.pack_start(ssh_priv_view, True, True, 0)
        ssh_priv_frame.add(ssh_priv_box)
        ssh_box.pack_start(ssh_priv_frame, False, False, 0)

        # Public Key Name
        pub_key_name_label = Gtk.Label(label="Public Key Name:")
        pub_key_name_label.set_xalign(0)
        ssh_box.pack_start(pub_key_name_label, False, False, 0)
        pub_key_name_entry = Gtk.Entry()
        pub_key_name_entry.set_text(get_val("ssh_public_key_name", "id_rsa.pub"))
        ssh_box.pack_start(pub_key_name_entry, False, False, 0)

        # SSH Public Key Frame
        ssh_pub_frame = Gtk.Frame(label="SSH Public Key")
        ssh_pub_frame.set_margin_bottom(8)
        ssh_pub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ssh_pub_box.set_margin_start(8)
        ssh_pub_box.set_margin_end(8)
        ssh_pub_box.set_margin_top(8)
        ssh_pub_box.set_margin_bottom(8)
        ssh_pub_buffer = Gtk.TextBuffer()
        ssh_pub_buffer.set_text(get_val("ssh_public_key_content"))
        ssh_pub_view = Gtk.TextView(buffer=ssh_pub_buffer)
        ssh_pub_view.set_monospace(True)
        ssh_pub_view.set_wrap_mode(Gtk.WrapMode.WORD)
        ssh_pub_view.set_hexpand(True)
        ssh_pub_view.set_vexpand(True)
        ssh_pub_view.set_size_request(-1, 40)
        ssh_pub_box.pack_start(ssh_pub_view, True, True, 0)
        ssh_pub_frame.add(ssh_pub_box)
        ssh_box.pack_start(ssh_pub_frame, False, False, 0)

        # SSH Config File Frame
        ssh_cfg_frame = Gtk.Frame(label="SSH Config File (~/.ssh/config)")
        ssh_cfg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ssh_cfg_box.set_margin_start(8)
        ssh_cfg_box.set_margin_end(8)
        ssh_cfg_box.set_margin_top(8)
        ssh_cfg_box.set_margin_bottom(8)
        ssh_cfg_buffer = Gtk.TextBuffer()
        # Load from local_config if present
        ssh_cfg_buffer.set_text(local_config.get("ssh_config_content", ""))
        ssh_cfg_view = Gtk.TextView(buffer=ssh_cfg_buffer)
        ssh_cfg_view.set_monospace(True)
        ssh_cfg_view.set_wrap_mode(Gtk.WrapMode.WORD)
        ssh_cfg_view.set_hexpand(True)
        ssh_cfg_view.set_vexpand(True)
        ssh_cfg_view.set_size_request(-1, 80)
        ssh_cfg_box.pack_start(ssh_cfg_view, True, True, 0)
        ssh_cfg_frame.add(ssh_cfg_box)
        ssh_box.pack_start(ssh_cfg_frame, False, False, 0)

        ssh_scrolled = Gtk.ScrolledWindow()
        ssh_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        ssh_scrolled.set_min_content_height(300)
        ssh_scrolled.set_min_content_width(500)
        ssh_scrolled.add(ssh_box)
        config_notebook.append_page(ssh_scrolled, Gtk.Label(label="SSH"))
        
        # --- Browser Tab ---
        browser_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        browser_box.set_margin_start(10)
        browser_box.set_margin_end(10)
        browser_box.set_margin_top(10)
        browser_box.set_margin_bottom(10)
        
        chromium_label = Gtk.Label(label="Chromium Homepage URL:")
        chromium_entry = Gtk.Entry()
        chromium_entry.set_text(get_val("chromium_homepage_url"))
        browser_box.pack_start(chromium_label, False, False, 0)
        browser_box.pack_start(chromium_entry, False, False, 0)
        
        config_notebook.append_page(browser_box, Gtk.Label(label="Browser"))
        
        # --- User Info Tab ---
        userinfo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        userinfo_box.set_margin_start(10)
        userinfo_box.set_margin_end(10)
        userinfo_box.set_margin_top(10)
        userinfo_box.set_margin_bottom(10)

        user_label = Gtk.Label(label="System User:")
        user_label.set_xalign(0)
        userinfo_box.pack_start(user_label, False, False, 0)
        user_entry = Gtk.Entry()
        user_entry.set_text(get_val("user", getpass.getuser() or ""))
        userinfo_box.pack_start(user_entry, False, False, 0)

        user_home_label = Gtk.Label(label="User Home Directory:")
        user_home_label.set_xalign(0)
        userinfo_box.pack_start(user_home_label, False, False, 0)
        user_home_entry = Gtk.Entry()
        user_home_entry.set_text(get_val("user_home", os.path.expanduser("~")))
        userinfo_box.pack_start(user_home_entry, False, False, 0)

        working_directory_label = Gtk.Label(label="Working Directory (user override, see docs):")
        working_directory_label.set_tooltip_text("This value is loaded from ~/.config/com.crimson.cfg/local.yml if present.")
        working_directory_label.set_xalign(0)
        userinfo_box.pack_start(working_directory_label, False, False, 0)
        working_directory_entry = Gtk.Entry()
        working_directory_entry.set_text(get_val("working_directory", "{{ user_home }}/CrimsonCFG"))
        userinfo_box.pack_start(working_directory_entry, False, False, 0)

        config_notebook.append_page(userinfo_box, Gtk.Label(label="User Info"))

        # --- Background Tab ---
        background_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        background_box.set_margin_start(10)
        background_box.set_margin_end(10)
        background_box.set_margin_top(10)
        background_box.set_margin_bottom(10)

        bg_label = Gtk.Label(label="Background Image (optional):")
        bg_label.set_xalign(0)
        background_box.pack_start(bg_label, False, False, 0)
        bg_file_chooser = Gtk.FileChooserButton(title="Select Background Image", action=Gtk.FileChooserAction.OPEN)
        bg_file_chooser.set_width_chars(40)
        bg_file_chooser.set_filename(local_config.get("background_image", "") or "")
        background_box.pack_start(bg_file_chooser, False, False, 0)
        bg_clear_btn = Gtk.Button(label="Clear Background Image")
        background_box.pack_start(bg_clear_btn, False, False, 0)

        # Color Picker
        color_label = Gtk.Label(label="Background Color (used if no image):")
        color_label.set_xalign(0)
        background_box.pack_start(color_label, False, False, 0)
        default_color = local_config.get("background_color", "#181a20")
        color_btn = Gtk.ColorButton()
        try:
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse(default_color)
            color_btn.set_rgba(gdk_rgba)
        except Exception:
            pass
        background_box.pack_start(color_btn, False, False, 0)
        color_reset_btn = Gtk.Button(label="Reset Color to Default")
        background_box.pack_start(color_reset_btn, False, False, 0)

        config_notebook.append_page(background_box, Gtk.Label(label="Background"))
        
        # --- Save Button (global) ---
        save_btn = Gtk.Button(label="Save Configuration")
        def on_save_clicked(btn):
            # Load the template as a dict
            from jinja2 import Template
            template_path = os.path.join(os.path.dirname(__file__), '../templates/local.yml.j2')
            with open(template_path, 'r') as f:
                template_content = f.read()
            # Render the template minimally (no variables, just as YAML)
            template = Template(template_content)
            rendered = template.render(system_user=getpass.getuser(), git_email='', git_username='')
            template_dict = yaml.safe_load(rendered) or {}
            # Load the user's current local.yml as a ruamel CommentedMap
            with open(local_file, 'r') as f:
                try:
                    user_config = yaml_ruamel.load(f) or {}
                except Exception:
                    user_config = {}
            # Merge template and user config (user values take precedence)
            merged_config = template_dict.copy()
            merged_config.update(user_config)
            # Only update the keys that are present in the form
            updates = {
                "git_username": git_username_entry.get_text(),
                "git_email": git_email_entry.get_text(),
                "chromium_homepage_url": chromium_entry.get_text(),
                # User info
                "user": user_entry.get_text(),
                "user_home": user_home_entry.get_text(),
                "working_directory": working_directory_entry.get_text(),
                # SSH key names
                "ssh_private_key_name": priv_key_name_entry.get_text(),
                "ssh_public_key_name": pub_key_name_entry.get_text(),
            }
            # SSH private key
            start, end = ssh_priv_buffer.get_bounds()
            updates["ssh_private_key_content"] = ssh_priv_buffer.get_text(start, end, True)
            # SSH public key
            start, end = ssh_pub_buffer.get_bounds()
            updates["ssh_public_key_content"] = ssh_pub_buffer.get_text(start, end, True)
            # SSH config content (store in local.yml)
            start, end = ssh_cfg_buffer.get_bounds()
            updates["ssh_config_content"] = ssh_cfg_buffer.get_text(start, end, True)
            # Background image
            bg_path = bg_file_chooser.get_filename()
            if bg_path:
                updates["background_image"] = bg_path
            # Background color
            rgba = color_btn.get_rgba()
            hex_color = "#%02x%02x%02x" % (int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))
            updates["background_color"] = hex_color
            # Update only the relevant keys in user_config (CommentedMap)
            for k, v in updates.items():
                user_config[k] = v
            # Write the updated config back, preserving comments
            with open(local_file, 'w') as f:
                yaml_ruamel.dump(user_config, f)
            # Reload config and update main_window variables
            self.main_window.config = self.main_window.config_manager.load_config()
            self.main_window.user = self.main_window.config.get("settings", {}).get("default_user", "user")
            self.main_window.user_home = f"/home/{self.main_window.user}"
            self.main_window.working_directory = self.main_window.config.get("settings", {}).get("working_directory", f"{self.main_window.user_home}/CrimsonCFG")
            if "{{ user_home }}" in self.main_window.working_directory:
                self.main_window.working_directory = self.main_window.working_directory.replace("{{ user_home }}", self.main_window.user_home)
            self.main_window.inventory_file = f"{self.main_window.working_directory}/hosts.ini"
            # Optionally, show a dialog or status update
            dialog = Gtk.MessageDialog(parent=self.main_window.window, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Configuration saved!")
            dialog.run()
            dialog.destroy()
        save_btn.connect("clicked", on_save_clicked)
        def on_clear_bg(btn):
            bg_file_chooser.unselect_all()
            local_config.pop("background_image", None)
            with open(local_file, 'w') as f:
                yaml_ruamel.dump(local_config, f)
            self.apply_css()
        bg_clear_btn.connect("clicked", on_clear_bg)
        def on_reset_color(btn):
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse("#181a20")
            color_btn.set_rgba(gdk_rgba)
            local_config["background_color"] = "#181a20"
            with open(local_file, 'w') as f:
                yaml_ruamel.dump(local_config, f)
            self.apply_css()
        color_reset_btn.connect("clicked", on_reset_color)
        def on_color_set(btn):
            # Use the color from the event, not from config
            rgba = btn.get_rgba()
            hex_color = "#%02x%02x%02x" % (int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))
            local_config["background_color"] = hex_color
            with open(local_file, 'w') as f:
                yaml_ruamel.dump(local_config, f)
            self.apply_css()
        color_btn.connect("color-set", on_color_set)
        def on_bg_file_set(btn):
            # Use the filename from the event, not from config
            bg_path = btn.get_filename()
            if bg_path:
                local_config["background_image"] = bg_path
            else:
                local_config.pop("background_image", None)
            with open(local_file, 'w') as f:
                yaml_ruamel.dump(local_config, f)
            self.apply_css()
        bg_file_chooser.connect("file-set", on_bg_file_set)
        config_box.pack_start(save_btn, False, False, 10)
        # --- END: Editable Configuration Form ---
        
        # --- Administration Tab (with password protection) ---
        admin_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        admin_tab.set_margin_top(15)
        admin_tab.set_margin_bottom(15)
        admin_tab.set_margin_start(15)
        admin_tab.set_margin_end(15)

        # Password protection state
        self._admin_authenticated = getattr(self, '_admin_authenticated', False)
        def show_admin_content():
            # Clear admin_tab
            for child in admin_tab.get_children():
                admin_tab.remove(child)

            # Load local.yml
            local_config = {}
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}

            # Admin notebook
            admin_notebook = Gtk.Notebook()
            admin_tab.pack_start(admin_notebook, True, True, 0)
            # --- Default Apps Tab (APT) ---
            default_apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            default_apps_box.set_margin_start(10)
            default_apps_box.set_margin_end(10)
            default_apps_box.set_margin_top(10)
            default_apps_box.set_margin_bottom(10)
            apt_label = Gtk.Label(label="APT Packages:")
            default_apps_box.pack_start(apt_label, False, False, 0)
            apt_store = Gtk.ListStore(str)
            for pkg in local_config.get('apt_packages', []):
                apt_store.append([pkg])
            apt_view = Gtk.TreeView(model=apt_store)
            renderer = Gtk.CellRendererText()
            renderer.set_property('editable', True)
            def on_apt_edited(cell, path, new_text):
                apt_store[path][0] = new_text
            renderer.connect('edited', on_apt_edited)
            col = Gtk.TreeViewColumn("Package", renderer, text=0)
            apt_view.append_column(col)
            default_apps_box.pack_start(apt_view, True, True, 0)
            apt_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            add_apt_btn = Gtk.Button(label="Add")
            def on_add_apt(btn):
                apt_store.append([""])
            add_apt_btn.connect("clicked", on_add_apt)
            remove_apt_btn = Gtk.Button(label="Remove Selected")
            def on_remove_apt(btn):
                selection = apt_view.get_selection()
                model, treeiter = selection.get_selected()
                if treeiter:
                    model.remove(treeiter)
            remove_apt_btn.connect("clicked", on_remove_apt)
            apt_btn_box.pack_start(add_apt_btn, False, False, 0)
            apt_btn_box.pack_start(remove_apt_btn, False, False, 0)
            default_apps_box.pack_start(apt_btn_box, False, False, 0)
            admin_notebook.append_page(default_apps_box, Gtk.Label(label="APT Packages"))
            # --- Snap Packages Tab ---
            snap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            snap_box.set_margin_start(10)
            snap_box.set_margin_end(10)
            snap_box.set_margin_top(10)
            snap_box.set_margin_bottom(10)
            snap_label = Gtk.Label(label="Snap Packages:")
            snap_box.pack_start(snap_label, False, False, 0)
            snap_store = Gtk.ListStore(str)
            for pkg in local_config.get('snap_packages', []):
                snap_store.append([pkg])
            snap_view = Gtk.TreeView(model=snap_store)
            snap_renderer = Gtk.CellRendererText()
            snap_renderer.set_property('editable', True)
            def on_snap_edited(cell, path, new_text):
                snap_store[path][0] = new_text
            snap_renderer.connect('edited', on_snap_edited)
            snap_col = Gtk.TreeViewColumn("Package", snap_renderer, text=0)
            snap_view.append_column(snap_col)
            snap_box.pack_start(snap_view, True, True, 0)
            snap_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            add_snap_btn = Gtk.Button(label="Add")
            def on_add_snap(btn):
                snap_store.append([""])
            add_snap_btn.connect("clicked", on_add_snap)
            remove_snap_btn = Gtk.Button(label="Remove Selected")
            def on_remove_snap(btn):
                selection = snap_view.get_selection()
                model, treeiter = selection.get_selected()
                if treeiter:
                    model.remove(treeiter)
            remove_snap_btn.connect("clicked", on_remove_snap)
            snap_btn_box.pack_start(add_snap_btn, False, False, 0)
            snap_btn_box.pack_start(remove_snap_btn, False, False, 0)
            snap_box.pack_start(snap_btn_box, False, False, 0)
            admin_notebook.append_page(snap_box, Gtk.Label(label="Snap Packages"))
            # --- Corporate Identity (CI) Tab ---
            ci_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            ci_box.set_margin_start(10)
            ci_box.set_margin_end(10)
            ci_box.set_margin_top(10)
            ci_box.set_margin_bottom(10)
            ci_label = Gtk.Label(label="Corporate Identity (CI):")
            ci_box.pack_start(ci_label, False, False, 0)
            # App Name
            app_name_label = Gtk.Label(label="Application Name:")
            app_name_entry = Gtk.Entry()
            app_name_entry.set_text(local_config.get('app_name', 'CrimsonCFG'))
            ci_box.pack_start(app_name_label, False, False, 0)
            ci_box.pack_start(app_name_entry, False, False, 0)
            # App Subtitle
            app_subtitle_label = Gtk.Label(label="Application Subtitle:")
            app_subtitle_entry = Gtk.Entry()
            app_subtitle_entry.set_text(local_config.get('app_subtitle', 'App &amp; Customization Selector'))
            ci_box.pack_start(app_subtitle_label, False, False, 0)
            ci_box.pack_start(app_subtitle_entry, False, False, 0)
            # App Logo
            app_logo_label = Gtk.Label(label="Application Logo (base working dir):")
            ci_box.pack_start(app_logo_label, False, False, 0)
            # Show the current working directory for user reference
            working_dir = str(self.main_window.working_directory) if hasattr(self.main_window, 'working_directory') else os.getcwd()
            working_dir_label = Gtk.Label(label=f"Current working dir: {working_dir}")
            working_dir_label.set_xalign(0)
            ci_box.pack_start(working_dir_label, False, False, 0)
            app_logo_entry = Gtk.Entry()
            app_logo_entry.set_text(local_config.get('app_logo', 'files/com.crimson.cfg.logo.png'))
            ci_box.pack_start(app_logo_entry, False, False, 0)
            admin_notebook.append_page(ci_box, Gtk.Label(label="Corporate Identity"))
            # Save button for admin changes (update to save CI as well)
            def on_save_admin(btn):
                # Save user-modifiable variables to user's local.yml
                config_dir = Path.home() / ".config/com.crimson.cfg"
                local_file = config_dir / "local.yml"
                if not config_dir.exists():
                    config_dir.mkdir(parents=True, exist_ok=True)
                
                # Load existing local config
                local_config = {}
                if local_file.exists():
                    with open(local_file, 'r') as f:
                        local_config = yaml.safe_load(f) or {}
                
                # Update user-modifiable variables
                local_config['apt_packages'] = [row[0] for row in apt_store]
                local_config['snap_packages'] = [row[0] for row in snap_store]
                local_config['app_name'] = app_name_entry.get_text()
                local_config['app_subtitle'] = app_subtitle_entry.get_text()
                local_config['app_logo'] = app_logo_entry.get_text()
                
                # Save to user's local.yml
                with open(local_file, 'w') as f:
                    yaml.safe_dump(local_config, f, default_flow_style=False, allow_unicode=True)
                # Update header in UI immediately
                self.main_window.config = self.main_window.config_manager.load_config()
                self.apply_css()
                self.show_main_interface()
                dialog = Gtk.MessageDialog(parent=self.main_window.window, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Admin settings saved!")
                dialog.run()
                dialog.destroy()
            save_admin_btn = Gtk.Button(label="Save Changes")
            save_admin_btn.connect("clicked", on_save_admin)
            admin_tab.pack_start(save_admin_btn, False, False, 10)
            admin_tab.show_all()
        def show_admin_password_prompt():
            # Clear admin_tab
            for child in admin_tab.get_children():
                admin_tab.remove(child)
            # TODO: This is insecure and just a proof of concept. Do not use plaintext admin passwords in production.
            try:
                config_dir = Path.home() / ".config/com.crimson.cfg"
                local_file = config_dir / "local.yml"
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
                admin_password = local_config['admin_password']
                password_missing = False
            except Exception:
                admin_password = None
                password_missing = True
            pw_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            pw_box.set_margin_top(30)
            pw_label = Gtk.Label(label="Enter admin password to access administration features:")
            pw_box.pack_start(pw_label, False, False, 0)
            mask_btn = Gtk.Button(label="Show")
            pw_entry = Gtk.Entry()
            pw_entry.set_visibility(False)
            def on_mask_toggle(btn):
                if pw_entry.get_visibility():
                    pw_entry.set_visibility(False)
                    mask_btn.set_label("Show")
                else:
                    pw_entry.set_visibility(True)
                    mask_btn.set_label("Hide")
            mask_btn.connect("clicked", on_mask_toggle)
            mask_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            mask_box.pack_start(pw_entry, True, True, 0)
            mask_box.pack_start(mask_btn, False, False, 0)
            pw_box.pack_start(mask_box, False, False, 0)
            status_label = Gtk.Label()
            pw_box.pack_start(status_label, False, False, 0)
            def on_pw_submit(entry):
                if password_missing or admin_password is None:
                    status_label.set_text("Admin password is not set in local.yml. Access denied.")
                    return
                if pw_entry.get_text() == admin_password:
                    self._admin_authenticated = True
                    show_admin_content()
                    admin_tab.show_all()
                    return
                status_label.set_text("Incorrect password.")
            pw_entry.connect("activate", on_pw_submit)
            if password_missing or admin_password is None:
                status_label.set_text("Admin password is not set in local.yml. Access denied.")
                pw_entry.set_sensitive(False)
                mask_btn.set_sensitive(False)
            admin_tab.pack_start(pw_box, True, True, 0)
        if self._admin_authenticated:
            show_admin_content()
        else:
            show_admin_password_prompt()
        self.notebook.append_page(admin_tab, Gtk.Label(label="Administration"))
        
        # Add to the admin or settings tab (after other controls)
        def on_reset_installed_playbooks(btn):
            config_dir = Path.home() / ".config/com.crimson.cfg"
            state_file = config_dir / "installed_playbooks.json"
            if state_file.exists():
                state_file.unlink()
            # Optionally, re-select essentials after reset
            self.main_window.select_essential_playbooks()
            self.main_window.show_success_dialog("Installed playbook state has been reset. Essentials will be pre-selected again.")
        reset_btn = Gtk.Button(label="Reset Installed Playbooks State")
        reset_btn.set_tooltip_text("Clear the record of installed playbooks so essentials will be pre-selected again.")
        reset_btn.connect("clicked", on_reset_installed_playbooks)
        # Add this button to the right panel or admin tab (choose appropriate location)
        # For example, add to right_box if present:
        if hasattr(self, 'right_box'):
            self.right_box.pack_start(reset_btn, False, False, 0)
        # Or add to admin_tab if present
        # ... existing code ...
        
        if self.debug:
            print("setup_gui: Initializing playbook list...")
        # Initialize the playbook list
        self.main_window.update_playbook_list()
        
        # Automatically select essential playbooks
        self.main_window.select_essential_playbooks()
        
        if self.debug:
            print("setup_gui: Complete")
        
        # Connect window close event
        self.main_window.window.connect("destroy", Gtk.main_quit)
        
    def update_config_display(self, button):
        """Update the configuration display with current settings"""
        import json
        
        config_text = "=== CRIMSONCFG CONFIGURATION ===\n\n"
        
        # System Information
        config_text += "🔧 SYSTEM INFORMATION:\n"
        config_text += f"  • Current User: {self.main_window.user}\n"
        config_text += f"  • User Home: {self.main_window.user_home}\n"
        config_text += f"  • Working Directory: {self.main_window.working_directory}\n"
        config_text += f"  • Inventory File: {self.main_window.inventory_file}\n"
        config_text += f"  • Debug Mode: {'Enabled' if self.debug else 'Disabled'}\n\n"
        
        # Configuration Files
        config_text += "📁 CONFIGURATION FILES:\n"
        local_file = Path.home() / ".config/com.crimson.cfg/local.yml"
        gui_config_file = Path.home() / ".config/com.crimson.cfg/gui_config.json"
        
        config_text += f"  • Local Config: {'✅ Found' if local_file.exists() else '❌ Not found'} ({local_file})\n"
        config_text += f"  • GUI Config: {'✅ Found' if gui_config_file.exists() else '❌ Not found'} ({gui_config_file})\n\n"
        
        # Current Settings
        config_text += "⚙️ CURRENT SETTINGS:\n"
        settings = self.main_window.config.get("settings", {})
        for key, value in settings.items():
            config_text += f"  • {key}: {value}\n"
        config_text += "\n"
        
        # Categories and Playbooks
        config_text += "📦 AVAILABLE CATEGORIES:\n"
        categories = self.main_window.config.get("categories", {})
        for category_name, category_info in categories.items():
            config_text += f"  • {category_name}: {len(category_info.get('playbooks', []))} playbooks\n"
            if "description" in category_info:
                config_text += f"    Description: {category_info['description']}\n"
        config_text += "\n"
        
        # Important Variables to Configure
        config_text += "⚠️ IMPORTANT VARIABLES TO CONFIGURE:\n"
        config_text += "  • git_username: Your Git username (currently: "
        config_text += f"{settings.get('git_username', 'NOT SET')})\n"
        config_text += "  • git_email: Your Git email (currently: "
        config_text += f"{settings.get('git_email', 'NOT SET')})\n"
        config_text += "  • debug: Enable debug mode (currently: "
        config_text += f"{settings.get('debug', 0)})\n\n"
        
        # Configuration Instructions
        config_text += "📝 HOW TO CONFIGURE:\n"
        config_text += "  1. Edit ~/.config/com.crimson.cfg/local.yml for user-specific settings\n"
        config_text += "  2. Local settings override global settings\n"
        config_text += "  3. Restart CrimsonCFG after making changes\n\n"
        
        # Example Configuration
        config_text += "\ud83d\udca1 EXAMPLE CONFIGURATION (~/.config/com.crimson.cfg/local.yml):\n"
        config_text += "```yaml\n"
        config_text += "# User-specific configuration\n"
        config_text += "apt_packages:\n"
        config_text += "  - firefox\n"
        config_text += "  - vlc\n"
        config_text += "snap_packages:\n"
        config_text += "  - spotify\n"
        config_text += "app_name: MyCompanyCFG\n"
        config_text += "app_subtitle: Custom Configuration Manager\n"
        config_text += "```\n\n"
        
        # File Locations
        config_text += "�� FILE LOCATIONS:\n"
        config_text += f"  • Working Directory: {Path.cwd()}\n"
        config_text += f"  • Application Directory: {self.main_window.working_directory}\n"
        config_text += f"  • Inventory File: {self.main_window.inventory_file}\n"
        config_text += f"  • Log Directory: {settings.get('log_directory', 'Not set')}\n"
        
        # Update the text buffer
        self.main_window.config_buffer.set_text(config_text)
        
    def refresh_config_display(self, button):
        """Refresh the configuration display"""
        if self.debug:
            print("Refreshing configuration display...")
        
        # Reload configuration
        self.main_window.config = self.main_window.config_manager.load_config()
        
        # Update debug setting
        self.main_window.debug = self.main_window.config.get("settings", {}).get("debug", 0) == 1
        
        # Update the display
        self.update_config_display(button)
        
        # Log the refresh
        self.main_window.logger.log_message("Configuration display refreshed")
        
        if self.debug:
            print("Configuration display refreshed successfully") 