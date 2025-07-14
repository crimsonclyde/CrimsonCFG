#!/usr/bin/env python3
"""
CrimsonCFG GUI Builder
Handles main interface construction and styling
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk  # type: ignore
import os

class GUIBuilder:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
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
            style_context = self.main_window.window.get_style_context()
            style_context.add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
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
        self.main_window.notebook = Gtk.Notebook()
        
        # Style the notebook tab area to have a background
        self.main_window.notebook.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 0.9))
        
        content_container.pack_start(self.main_window.notebook, True, True, 0)
        
        # Add spacing between tab headers and content
        self.main_window.notebook.set_margin_top(45)
        
        # Main tab
        main_tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        main_tab.set_margin_top(15)
        
        # Add Material Design background to main tab
        main_tab.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        
        self.main_window.notebook.append_page(main_tab, Gtk.Label(label="Main"))
        
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
        
        self.main_window.notebook.append_page(logs_tab, Gtk.Label(label="Logs"))
        
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
        
        self.main_window.notebook.append_page(config_tab, Gtk.Label(label="Configuration"))
        
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
        config_scrolled = Gtk.ScrolledWindow()
        config_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        config_box.pack_start(config_scrolled, True, True, 0)
        
        # Configuration text buffer
        self.main_window.config_buffer = Gtk.TextBuffer()
        self.main_window.config_textview = Gtk.TextView(buffer=self.main_window.config_buffer)
        self.main_window.config_textview.set_editable(False)
        self.main_window.config_textview.set_monospace(True)
        
        # Add solid background to config text view
        self.main_window.config_textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 1.0))
        
        config_scrolled.add(self.main_window.config_textview)
        
        # Populate configuration display
        self.update_config_display()
        
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
        
    def update_config_display(self):
        """Update the configuration display with current settings"""
        import json
        from pathlib import Path
        
        config_text = "=== CRIMSONCFG CONFIGURATION ===\n\n"
        
        # System Information
        config_text += "🔧 SYSTEM INFORMATION:\n"
        config_text += f"  • Current User: {self.main_window.user}\n"
        config_text += f"  • User Home: {self.main_window.user_home}\n"
        config_text += f"  • Ansible Folder: {self.main_window.ansible_folder}\n"
        config_text += f"  • Inventory File: {self.main_window.inventory_file}\n"
        config_text += f"  • Debug Mode: {'Enabled' if self.debug else 'Disabled'}\n\n"
        
        # Configuration Files
        config_text += "📁 CONFIGURATION FILES:\n"
        all_file = Path("group_vars/all.yml")
        local_file = Path("group_vars/local.yml")
        gui_config_file = Path("conf/gui_config.json")
        
        config_text += f"  • Global Config: {'✅ Found' if all_file.exists() else '❌ Not found'} ({all_file})\n"
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
        config_text += "  1. Edit group_vars/all.yml for global settings\n"
        config_text += "  2. Edit group_vars/local.yml for user-specific settings\n"
        config_text += "  3. Local settings override global settings\n"
        config_text += "  4. Restart CrimsonCFG after making changes\n\n"
        
        # Example Configuration
        config_text += "💡 EXAMPLE CONFIGURATION (group_vars/local.yml):\n"
        config_text += "```yaml\n"
        config_text += "# User-specific configuration\n"
        config_text += "git_username: your_github_username\n"
        config_text += "git_email: your.email@example.com\n"
        config_text += "debug: 1  # Enable debug mode\n"
        config_text += "```\n\n"
        
        # File Locations
        config_text += "📂 FILE LOCATIONS:\n"
        config_text += f"  • Working Directory: {Path.cwd()}\n"
        config_text += f"  • Ansible Directory: {self.main_window.ansible_folder}\n"
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
        self.update_config_display()
        
        # Log the refresh
        self.main_window.logger.log_message("Configuration display refreshed")
        
        if self.debug:
            print("Configuration display refreshed successfully") 