#!/usr/bin/env python3
"""
MainTab: Handles the main playbook selection interface
"""
from gi.repository import Gtk, Gdk
import os
import yaml
from pathlib import Path

class MainTab(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.main_window = main_window
        self.debug = main_window.debug
        self.set_margin_top(6)
        
        # Remove the opaque background - let the main window background show through
        # self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        
        if self.debug:
            print("MainTab: Initialized with transparent background")
        
        self._build_tab()
        
    def _build_tab(self):
        """Build the main tab content"""
        if self.debug:
            print("MainTab: Building main tab content...")
            
        # Main content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        self.pack_start(content_box, True, True, 0)
        
        if self.debug:
            print("MainTab: Creating left panel...")
        # Left column container
        left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_box.pack_start(left_column, False, False, 0)
        
        # Categories frame (80% height)
        left_frame = Gtk.Frame(label="Categories")
        left_column.pack_start(left_frame, True, True, 0)  # Expand and fill
        
        # Add background to categories
        left_background = Gtk.EventBox()
        left_background.set_visible_window(True)
        left_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        left_frame.add(left_background)
        
        if self.debug:
            print("MainTab: Left panel background set with 0.3 opacity")
        
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
            print(f"MainTab: Found {len(categories)} categories: {categories}")
        if categories:
            self.main_window.current_category = categories[0]
            
        # Create radio button group
        radio_group = None
        
        for category in categories:
            cat_info = self.main_window.config["categories"][category]
            
            # Category button - first one sets the group, others join it
            # Display category name in uppercase for better UI presentation
            display_name = category.upper() if category.startswith("dep:") else category
            btn = Gtk.RadioButton(label=display_name, group=radio_group)
            if radio_group is None:
                radio_group = btn
            btn.connect("toggled", self.main_window.on_category_changed, category)
            if category == self.main_window.current_category:
                btn.set_active(True)
            left_box.pack_start(btn, False, False, 0)
            self.main_window.category_buttons[category] = btn
            
        if self.debug:
            print("MainTab: Creating center panel...")
        # Center panel - Playbooks
        center_frame = Gtk.Frame(label="Available Playbooks")
        center_frame.set_margin_end(15)
        content_box.pack_start(center_frame, True, True, 0)
        
        # Add background to available playbooks
        center_background = Gtk.EventBox()
        center_background.set_visible_window(True)
        center_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        center_frame.add(center_background)
        
        if self.debug:
            print("MainTab: Center panel background set with 0.3 opacity")
        
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        center_box.set_margin_start(15)
        center_box.set_margin_end(15)
        center_box.set_margin_top(15)
        center_box.set_margin_bottom(15)
        center_background.add(center_box)
        
        # Playbook tree
        self.main_window.playbook_store = Gtk.ListStore(str, str, str, bool, bool, str, str)  # name, essential, description, selected, disabled, require_config_icon, source
        self.main_window.playbook_tree = Gtk.TreeView(model=self.main_window.playbook_store)
        
        # Columns
        renderer = Gtk.CellRendererText()
        col1 = Gtk.TreeViewColumn("Playbook", renderer)
        col1.set_cell_data_func(renderer, lambda col, cell, model, iter, data: cell.set_property('text', model[iter][0]) or cell.set_property('foreground', '#888' if model[iter][4] else None))
        col1.set_expand(True)
        col1.set_resizable(True)
        col1.set_min_width(150)
        col1.set_fixed_width(200)
        self.main_window.playbook_tree.append_column(col1)
        
        renderer2 = Gtk.CellRendererText()
        col2 = Gtk.TreeViewColumn("Essential", renderer2)
        col2.set_cell_data_func(renderer2, lambda col, cell, model, iter, data: cell.set_property('text', model[iter][1]) or cell.set_property('foreground', '#888' if model[iter][4] else None))
        col2.set_expand(False)
        col2.set_resizable(True)
        col2.set_min_width(60)
        col2.set_fixed_width(80)
        self.main_window.playbook_tree.append_column(col2)

        # Require Config Icon column
        renderer_icon = Gtk.CellRendererPixbuf()
        col_icon = Gtk.TreeViewColumn("Require Config", renderer_icon)
        def icon_data_func(col, cell, model, iter, data):
            icon_name = model[iter][5]
            if icon_name:
                cell.set_property('icon-name', icon_name)
            else:
                cell.set_property('icon-name', None)
        col_icon.set_cell_data_func(renderer_icon, icon_data_func)
        col_icon.set_expand(False)
        col_icon.set_resizable(True)
        col_icon.set_min_width(80)
        col_icon.set_fixed_width(100)
        self.main_window.playbook_tree.append_column(col_icon)
        
        # Source column
        renderer4 = Gtk.CellRendererText()
        col4 = Gtk.TreeViewColumn("Source", renderer4)
        col4.set_cell_data_func(renderer4, lambda col, cell, model, iter, data: cell.set_property('text', model[iter][6]) or cell.set_property('foreground', '#888' if model[iter][4] else None))
        col4.set_expand(False)
        col4.set_resizable(True)
        col4.set_min_width(70)
        col4.set_fixed_width(90)
        self.main_window.playbook_tree.append_column(col4)
        
        renderer3 = Gtk.CellRendererText()
        col3 = Gtk.TreeViewColumn("Description", renderer3)
        col3.set_cell_data_func(renderer3, lambda col, cell, model, iter, data: cell.set_property('text', model[iter][2]) or cell.set_property('foreground', '#888' if model[iter][4] else None))
        col3.set_expand(True)
        col3.set_resizable(True)
        col3.set_min_width(200)
        self.main_window.playbook_tree.append_column(col3)
        
        # Selection and double-click
        self.main_window.playbook_tree.get_selection().connect("changed", self.main_window.on_playbook_selection_changed)
        self.main_window.playbook_tree.connect("row-activated", self.main_window.playbook_manager.on_playbook_row_activated)
        
        # Scrollable tree
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.main_window.playbook_tree)
        scrolled_window.set_tooltip_text("Double-click on a playbook to add/remove it from selection")
        center_box.pack_start(scrolled_window, True, True, 0)
        
        # Playbook Management frame (20% height, at bottom)
        management_frame = Gtk.Frame(label="Playbook Management")
        left_column.pack_start(management_frame, False, False, 0)  # Don't expand, stay at bottom
        
        # Add background to playbook management
        management_background = Gtk.EventBox()
        management_background.set_visible_window(True)
        management_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        management_frame.add(management_background)
        
        if self.debug:
            print("MainTab: Playbook Management frame background set with 0.3 opacity")
        
        # Management buttons
        management_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        management_box.set_margin_start(15)
        management_box.set_margin_end(15)
        management_box.set_margin_top(15)
        management_box.set_margin_bottom(15)
        management_background.add(management_box)
        
        update_playbooks_btn = Gtk.Button(label="Update Playbooks")
        update_playbooks_btn.set_tooltip_text("Update playbooks from the repository")
        update_playbooks_btn.connect("clicked", self.main_window.update_playbooks)
        management_box.pack_start(update_playbooks_btn, False, False, 0)
        
        if self.debug:
            print("MainTab: Creating right panel...")
        # Right panel - Controls and details
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_box.pack_start(right_box, False, False, 0)
        
        # Selection controls
        controls_frame = Gtk.Frame(label="Selection Controls")
        
        # Add background to selection controls
        controls_background = Gtk.EventBox()
        controls_background.set_visible_window(True)
        controls_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        controls_frame.add(controls_background)
        
        if self.debug:
            print("MainTab: Controls background set with 0.3 opacity")
        
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        controls_box.set_margin_start(15)
        controls_box.set_margin_end(15)
        controls_box.set_margin_top(15)
        controls_box.set_margin_bottom(15)
        controls_background.add(controls_box)
        
        remove_essential_btn = Gtk.Button(label="Remove Essentials")
        remove_essential_btn.set_tooltip_text("Remove all essential playbooks (shows warning dialog)")
        remove_essential_btn.connect("clicked", self.main_window.remove_essential)
        controls_box.pack_start(remove_essential_btn, False, False, 0)
        
        remove_non_essentials_btn = Gtk.Button(label="Remove non-essentials")
        remove_non_essentials_btn.set_tooltip_text("Remove all non-essential playbooks from selection (keeps essential playbooks)")
        remove_non_essentials_btn.connect("clicked", self.main_window.remove_all)
        controls_box.pack_start(remove_non_essentials_btn, False, False, 0)
        
        right_box.pack_start(controls_frame, False, False, 0)
        
        # Selected items
        selected_frame = Gtk.Frame(label="Selected Items")
        
        # Add background to selected items
        selected_background = Gtk.EventBox()
        selected_background.set_visible_window(True)
        selected_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        selected_frame.add(selected_background)
        
        if self.debug:
            print("MainTab: Selected items background set with 0.3 opacity")
        
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
        
        # Add double-click handler for selected items
        self.main_window.selected_tree.connect("row-activated", self.main_window.playbook_manager.on_selected_item_row_activated)
        
        selected_scrolled = Gtk.ScrolledWindow()
        selected_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        selected_scrolled.add(self.main_window.selected_tree)
        selected_scrolled.set_tooltip_text("Double-click on a non-essential playbook to remove it from selection")
        selected_box.pack_start(selected_scrolled, True, True, 0)
        
        right_box.pack_start(selected_frame, True, True, 0)
        
        # Action buttons
        action_frame = Gtk.Frame(label="Actions")
        
        # Add background to actions
        action_background = Gtk.EventBox()
        action_background.set_visible_window(True)
        action_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        action_frame.add(action_background)
        
        if self.debug:
            print("MainTab: Actions background set with 0.3 opacity")
        
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
        
        if self.debug:
            print("MainTab: Main tab content built successfully") 