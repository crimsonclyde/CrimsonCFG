#!/usr/bin/env python3
"""
ConfigTab: Refactored for new structure and instant/apply/save logic
"""
from gi.repository import Gtk, Gdk, GLib
from ruamel.yaml import YAML
import getpass
from pathlib import Path
import os
import yaml
from gi.repository import GdkPixbuf

class ConfigTab(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_window = main_window
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        self.set_margin_top(15)
        self._build_tab()
        


    def _build_tab(self):
        config_frame = Gtk.Frame(label="Current Configuration")
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
        self.pack_start(config_frame, True, True, 0)

        config_notebook = Gtk.Notebook()
        config_box.pack_start(config_notebook, True, True, 0)

        # --- User Configuration Tab (instant) ---
        user_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        user_tab.set_margin_start(10)
        user_tab.set_margin_end(10)
        user_tab.set_margin_top(10)
        user_tab.set_margin_bottom(10)
        # Lightning bolt unicode: \u26A1
        instant_icon = Gtk.Label(label="\u26A1")
        instant_icon.set_tooltip_text("Instantly applied")
        def add_instant_row(label_text, key, default):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            label = Gtk.Label(label=label_text)
            label.set_xalign(0)
            entry = Gtk.Entry()
            entry.set_text(self._get_config_value(key, default))
            row.pack_start(label, False, False, 0)
            row.pack_start(entry, True, True, 0)
            icon = Gtk.Label(label="\u26A1")
            icon.set_tooltip_text("Instantly applied")
            row.pack_start(icon, False, False, 0)
            def on_changed(widget):
                self._set_config_value(key, widget.get_text())
            entry.connect("changed", on_changed)
            user_tab.pack_start(row, False, False, 0)
        add_instant_row("System User:", "user", getpass.getuser())
        add_instant_row("User Home Directory:", "user_home", os.path.expanduser("~"))
        add_instant_row("Git Username:", "git_username", "")
        add_instant_row("Git Email Address:", "git_email", "")
        # --- User Image Upload ---
        img_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        img_label = Gtk.Label(label="User Avatar Image:")
        img_label.set_xalign(0)
        img_row.pack_start(img_label, False, False, 0)
        img_chooser = Gtk.FileChooserButton(title="Select User Image", action=Gtk.FileChooserAction.OPEN)
        img_chooser.set_width_chars(30)
        img_chooser.set_tooltip_text("Please select a PNG file. Other formats may not work as a Gnome avatar.")
        img_row.pack_start(img_chooser, False, False, 0)
        # Image preview
        user_img_path = self._get_config_value("user_avatar", "")
        if user_img_path and os.path.exists(user_img_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(user_img_path, 64, 64)
            img_preview = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            img_preview = Gtk.Image()
        img_row.pack_start(img_preview, False, False, 0)
        # Remove Avatar button
        remove_avatar_btn = Gtk.Button(label="Remove Avatar")
        def on_remove_avatar(btn):
            user_home = self._get_config_value("user_home", os.path.expanduser("~"))
            dest_path = os.path.join(user_home, "Pictures", "user_img.png")
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
            self._set_config_value("user_avatar", "")
            img_preview.clear()
        remove_avatar_btn.connect("clicked", on_remove_avatar)
        img_row.pack_start(remove_avatar_btn, False, False, 0)
        # Add lightning bolt symbol for instantly applied setting
        instant_icon = Gtk.Label(label="\u26A1")
        instant_icon.set_tooltip_text("Instantly applied")
        img_row.pack_start(instant_icon, False, False, 0)
        def on_img_file_set(widget):
            selected_path = img_chooser.get_filename()
            if selected_path:
                user_home = self._get_config_value("user_home", os.path.expanduser("~"))
                pictures_dir = os.path.join(user_home, "Pictures")
                if not os.path.exists(pictures_dir):
                    os.makedirs(pictures_dir)
                dest_path = os.path.join(pictures_dir, "user_img.png")
                import shutil
                try:
                    shutil.copyfile(selected_path, dest_path)
                except Exception as e:
                    print(f"Failed to copy avatar image: {e}")
                self._set_config_value("user_avatar", dest_path)
                # Update preview
                if os.path.exists(dest_path):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(dest_path, 64, 64)
                    img_preview.set_from_pixbuf(pixbuf)
                else:
                    img_preview.clear()
                # Set as Gnome avatar using dbus-send
                import subprocess
                try:
                    subprocess.run([
                        'dbus-send', '--system', '--print-reply',
                        '--dest=org.freedesktop.Accounts',
                        f'/org/freedesktop/Accounts/User{os.getuid()}',
                        'org.freedesktop.Accounts.User.SetIconFile',
                        f'string:{dest_path}'
                    ], check=True)
                except Exception as e:
                    print(f"Failed to set Gnome avatar: {e}")
        img_chooser.connect("file-set", on_img_file_set)
        user_tab.pack_start(img_row, False, False, 0)
        config_notebook.append_page(user_tab, Gtk.Label(label="User Configuration"))

        # --- Application Tab (save) ---
        app_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        app_tab.set_margin_start(10)
        app_tab.set_margin_end(10)
        app_tab.set_margin_top(10)
        app_tab.set_margin_bottom(10)
        # Application Background Image Section
        bg_label = Gtk.Label(label="Application Background Image:")
        bg_label.set_xalign(0)
        app_tab.pack_start(bg_label, False, False, 0)
        
        # Background previews - using FlowBox for dynamic layout
        bg_scroll = Gtk.ScrolledWindow()
        bg_scroll.set_min_content_height(150)
        bg_scroll.set_max_content_height(200)
        
        # Use FlowBox for dynamic grid layout
        bg_flowbox = Gtk.FlowBox()
        bg_flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        bg_flowbox.set_min_children_per_line(3)
        bg_flowbox.set_homogeneous(True)
        bg_flowbox.set_row_spacing(8)
        bg_flowbox.set_column_spacing(8)
        
        bg_scroll.add(bg_flowbox)
        app_tab.pack_start(bg_scroll, True, True, 0)
        
        # Load background images from working_directory/files/app/background
        working_directory = self._get_config_value("working_directory", "/opt/CrimsonCFG")
        bg_images_dir = os.path.join(working_directory, "files", "app", "background")
        bg_image_files = []
        if os.path.exists(bg_images_dir):
            for file in os.listdir(bg_images_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    bg_image_files.append(file)
        
        # Create clickable previews for background images
        current_bg_image = self._get_config_value("app_background_image", "")
        selected_bg_path = None
        bg_buttons = []
        
        def on_bg_image_clicked(widget, bg_path, button_index):
            nonlocal selected_bg_path
            selected_bg_path = bg_path
            self._set_config_value("app_background_image", bg_path)
            
            # Update visual selection - highlight selected button
            for i, btn in enumerate(bg_buttons):
                if i == button_index:
                    btn.get_style_context().add_class("selected")
                else:
                    btn.get_style_context().remove_class("selected")
            
            # Reload config and apply CSS
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
            
            print(f"Selected background image: {bg_path}")
        
        # Also handle FlowBox selection changes
        def on_bg_flowbox_selection_changed(flowbox):
            selected_child = flowbox.get_selected_child()
            if selected_child:
                # Find the button index
                for i, btn in enumerate(bg_buttons):
                    if btn == selected_child.get_child():
                        on_bg_image_clicked(btn, bg_buttons[i], i)
                        break
        
        # Create grid of background image previews
        for i, bg_file in enumerate(bg_image_files):
            bg_path = os.path.join(bg_images_dir, bg_file)
            
            # Create container for button content
            button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            button_box.set_margin_start(4)
            button_box.set_margin_end(4)
            button_box.set_margin_top(4)
            button_box.set_margin_bottom(4)
            
            # Create clickable button with preview
            bg_button = Gtk.Button()
            bg_button.set_relief(Gtk.ReliefStyle.NONE)
            bg_button.set_can_focus(False)
            
            # Add some padding and styling
            bg_button.set_margin_start(2)
            bg_button.set_margin_end(2)
            bg_button.set_margin_top(2)
            bg_button.set_margin_bottom(2)
            
            # Create image preview
            try:
                # Larger preview for better visibility
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(bg_path, 140, 95)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                button_box.pack_start(image, False, False, 0)
            except Exception as e:
                # Fallback if image can't be loaded
                fallback_label = Gtk.Label(label=bg_file[:15] + "..." if len(bg_file) > 15 else bg_file)
                button_box.pack_start(fallback_label, False, False, 0)
            
            # Add filename label
            filename_label = Gtk.Label(label=bg_file[:20] + "..." if len(bg_file) > 20 else bg_file)
            filename_label.set_line_wrap(True)
            filename_label.set_line_wrap_mode(2)
            filename_label.set_max_width_chars(20)
            filename_label.set_justify(Gtk.Justification.CENTER)
            button_box.pack_start(filename_label, False, False, 0)
            
            bg_button.add(button_box)
            
            # Check if this is the currently selected background image
            if bg_path == current_bg_image:
                bg_button.get_style_context().add_class("selected")
            
            bg_buttons.append(bg_button)
            bg_button.connect("clicked", on_bg_image_clicked, bg_path, len(bg_buttons) - 1)
            bg_flowbox.add(bg_button)
        
        # Connect FlowBox selection signal
        bg_flowbox.connect("selected-children-changed", on_bg_flowbox_selection_changed)
        

        
        # Clear Background Image button
        bg_clear_btn = Gtk.Button(label="Clear Background Image")
        def on_clear_bg(btn):
            if self.main_window.debug:
                print(f"ConfigTab: Clearing background image")
            self._set_config_value("app_background_image", "")
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
        bg_clear_btn.connect("clicked", on_clear_bg)
        app_tab.pack_start(bg_clear_btn, False, False, 0)
        # Background Color
        color_label = Gtk.Label(label="Background Color:")
        color_label.set_xalign(0)
        color_btn = Gtk.ColorButton()
        default_color = self._get_config_value("background_color", "#181a20")
        try:
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse(default_color)
            color_btn.set_rgba(gdk_rgba)
        except Exception:
            pass
        
        # Add color-set signal to save instantly
        def on_color_set(widget):
            rgba = widget.get_rgba()
            hex_color = "#%02x%02x%02x" % (int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))
            if self.main_window.debug:
                print(f"ConfigTab: Color changed to: '{hex_color}'")
            self._set_config_value("background_color", hex_color)
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
        color_btn.connect("color-set", on_color_set)
        
        app_tab.pack_start(color_label, False, False, 0)
        app_tab.pack_start(color_btn, False, False, 0)
        # Restore Reset Color to Default button
        color_reset_btn = Gtk.Button(label="Reset Color to Default")
        def on_reset_color(btn):
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse("#181a20")
            color_btn.set_rgba(gdk_rgba)
            if self.main_window.debug:
                print(f"ConfigTab: Resetting color to default")
            self._set_config_value("background_color", "#181a20")
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
        color_reset_btn.connect("clicked", on_reset_color)
        app_tab.pack_start(color_reset_btn, False, False, 0)

        config_notebook.append_page(app_tab, Gtk.Label(label="Application"))

        # --- Web Browser Tab (playbook-only) ---
        # Create a scrolled window for the browser tab content
        browser_scrolled = Gtk.ScrolledWindow()
        browser_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        browser_scrolled.set_vexpand(True)
        browser_scrolled.set_hexpand(True)
        
        browser_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        browser_tab.set_margin_start(10)
        browser_tab.set_margin_end(10)
        browser_tab.set_margin_top(10)
        browser_tab.set_margin_bottom(10)
        
        browser_info = Gtk.InfoBar()
        browser_info.set_message_type(Gtk.MessageType.INFO)
        browser_info_label = Gtk.Label(label="This setting is only applied when the corresponding playbook is run: App/Chromium")
        browser_info.get_content_area().pack_start(browser_info_label, True, True, 0)
        browser_info.show_all()
        browser_tab.pack_start(browser_info, False, False, 0)
        chromium_label = Gtk.Label(label="Default Chromium URL:")
        chromium_entry = Gtk.Entry()
        chromium_entry.set_text(self._get_config_value("chromium_homepage_url", ""))
        browser_tab.pack_start(chromium_label, False, False, 0)
        browser_tab.pack_start(chromium_entry, False, False, 0)
        def on_browser_changed(widget):
            self._set_config_value("chromium_homepage_url", chromium_entry.get_text())
        chromium_entry.connect("changed", on_browser_changed)
        
        # Chromium Profile 1 Name
        profile1_label = Gtk.Label(label="Chromium Profile 1 Name:")
        profile1_label.set_xalign(0)
        profile1_entry = Gtk.Entry()
        profile1_entry.set_text(self._get_config_value("chromium_profile1_name", "downloads"))
        browser_tab.pack_start(profile1_label, False, False, 0)
        browser_tab.pack_start(profile1_entry, False, False, 0)
        def on_profile1_changed(widget):
            self._set_config_value("chromium_profile1_name", profile1_entry.get_text())
        profile1_entry.connect("changed", on_profile1_changed)
        
        # Configure Chromium Policies (Collapsible)
        policies_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        policies_header_box.set_margin_bottom(5)
        
        policies_toggle_btn = Gtk.ToggleButton(label="Configure chromium_policy")
        policies_toggle_btn.set_active(False)  # Start collapsed
        policies_header_box.pack_start(policies_toggle_btn, False, False, 0)
        
        # Add a small arrow indicator
        policies_arrow_label = Gtk.Label(label="▼")
        policies_arrow_label.set_margin_start(5)
        policies_header_box.pack_start(policies_arrow_label, False, False, 0)
        
        browser_tab.pack_start(policies_header_box, False, False, 0)
        
        # Create the revealer for policies
        policies_revealer = Gtk.Revealer()
        policies_revealer.set_reveal_child(False)  # Start hidden
        browser_tab.pack_start(policies_revealer, False, False, 0)
        
        policies_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        policies_box.set_margin_start(10)
        policies_box.set_margin_end(10)
        policies_box.set_margin_top(10)
        policies_box.set_margin_bottom(10)
        policies_revealer.add(policies_box)
        
        # Handle policies toggle button clicks
        def on_policies_toggle(button):
            is_active = button.get_active()
            policies_revealer.set_reveal_child(is_active)
            policies_arrow_label.set_text("▲" if is_active else "▼")
        
        policies_toggle_btn.connect("toggled", on_policies_toggle)
        
        # Chromium Policies Editor
        policies_label = Gtk.Label(label="Chromium Policies (JSON):")
        policies_label.set_xalign(0)
        policies_box.pack_start(policies_label, False, False, 0)
        
        # Create scrolled window for policies editor
        policies_scrolled = Gtk.ScrolledWindow()
        policies_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        policies_scrolled.set_size_request(-1, 300)  # Fixed height to prevent UI expansion
        
        policies_buffer = Gtk.TextBuffer()
        # Load current policies content
        policies_content = self._get_chromium_policies_content()
        policies_buffer.set_text(policies_content)
        
        policies_view = Gtk.TextView(buffer=policies_buffer)
        policies_view.set_monospace(True)
        policies_view.set_wrap_mode(Gtk.WrapMode.NONE)
        policies_view.set_hexpand(True)
        policies_view.set_vexpand(True)
        
        policies_scrolled.add(policies_view)
        policies_box.pack_start(policies_scrolled, True, True, 0)
        
        # Save button for policies
        policies_save_btn = Gtk.Button(label="Save Chromium Policies")
        def on_policies_save(btn):
            start, end = policies_buffer.get_bounds()
            content = policies_buffer.get_text(start, end, True)
            self._save_chromium_policies_content(content)
        policies_save_btn.connect("clicked", on_policies_save)
        policies_box.pack_start(policies_save_btn, False, False, 0)
        
        # Configure Master Preferences (Collapsible)
        master_prefs_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        master_prefs_header_box.set_margin_top(5)  # Small gap from previous section
        master_prefs_header_box.set_margin_bottom(5)
        
        master_prefs_toggle_btn = Gtk.ToggleButton(label="Configure master_preferences")
        master_prefs_toggle_btn.set_active(False)  # Start collapsed
        master_prefs_header_box.pack_start(master_prefs_toggle_btn, False, False, 0)
        
        # Add a small arrow indicator
        master_prefs_arrow_label = Gtk.Label(label="▼")
        master_prefs_arrow_label.set_margin_start(5)
        master_prefs_header_box.pack_start(master_prefs_arrow_label, False, False, 0)
        
        browser_tab.pack_start(master_prefs_header_box, False, False, 0)
        
        # Create the revealer for master preferences
        master_prefs_revealer = Gtk.Revealer()
        master_prefs_revealer.set_reveal_child(False)  # Start hidden
        browser_tab.pack_start(master_prefs_revealer, False, False, 0)
        
        master_prefs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        master_prefs_box.set_margin_start(10)
        master_prefs_box.set_margin_end(10)
        master_prefs_box.set_margin_top(10)
        master_prefs_box.set_margin_bottom(10)
        master_prefs_revealer.add(master_prefs_box)
        
        # Handle master preferences toggle button clicks
        def on_master_prefs_toggle(button):
            is_active = button.get_active()
            master_prefs_revealer.set_reveal_child(is_active)
            master_prefs_arrow_label.set_text("▲" if is_active else "▼")
        
        master_prefs_toggle_btn.connect("toggled", on_master_prefs_toggle)
        
        # Master Preferences Editor
        master_prefs_label = Gtk.Label(label="Master Preferences (JSON):")
        master_prefs_label.set_xalign(0)
        master_prefs_box.pack_start(master_prefs_label, False, False, 0)
        
        # Create scrolled window for master preferences editor
        master_prefs_scrolled = Gtk.ScrolledWindow()
        master_prefs_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        master_prefs_scrolled.set_size_request(-1, 200)  # Smaller height for master preferences
        
        master_prefs_buffer = Gtk.TextBuffer()
        # Load current master preferences content
        master_prefs_content = self._get_master_preferences_content()
        master_prefs_buffer.set_text(master_prefs_content)
        
        master_prefs_view = Gtk.TextView(buffer=master_prefs_buffer)
        master_prefs_view.set_monospace(True)
        master_prefs_view.set_wrap_mode(Gtk.WrapMode.NONE)
        master_prefs_view.set_hexpand(True)
        master_prefs_view.set_vexpand(True)
        
        master_prefs_scrolled.add(master_prefs_view)
        master_prefs_box.pack_start(master_prefs_scrolled, True, True, 0)
        
        # Save button for master preferences
        master_prefs_save_btn = Gtk.Button(label="Save Master Preferences")
        def on_master_prefs_save(btn):
            start, end = master_prefs_buffer.get_bounds()
            content = master_prefs_buffer.get_text(start, end, True)
            self._save_master_preferences_content(content)
        master_prefs_save_btn.connect("clicked", on_master_prefs_save)
        master_prefs_box.pack_start(master_prefs_save_btn, False, False, 0)
        
        # Add the browser tab content to the scrolled window
        browser_scrolled.add(browser_tab)
        
        config_notebook.append_page(browser_scrolled, Gtk.Label(label="Web Browser (Chromium)"))

        # --- SSH Tab (playbook-only) ---
        ssh_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        ssh_tab.set_margin_start(10)
        ssh_tab.set_margin_end(10)
        ssh_tab.set_margin_top(10)
        ssh_tab.set_margin_bottom(10)
        ssh_info = Gtk.InfoBar()
        ssh_info.set_message_type(Gtk.MessageType.INFO)
        ssh_info_label = Gtk.Label(label="These settings are only applied when the corresponding playbook is run: Customisation/SSH Keys + SSH Config")
        ssh_info.get_content_area().pack_start(ssh_info_label, True, True, 0)
        ssh_info.show_all()
        ssh_tab.pack_start(ssh_info, False, False, 0)
        # (Reuse the SSH fields from previous implementation)
        priv_key_name_label = Gtk.Label(label="Private Key Name:")
        priv_key_name_label.set_xalign(0)
        priv_key_name_entry = Gtk.Entry()
        priv_key_name_entry.set_text(self._get_config_value("ssh_private_key_name", "id_rsa"))
        def on_priv_key_name_changed(widget):
            self._set_config_value("ssh_private_key_name", widget.get_text())
        priv_key_name_entry.connect("changed", on_priv_key_name_changed)
        ssh_tab.pack_start(priv_key_name_label, False, False, 0)
        ssh_tab.pack_start(priv_key_name_entry, False, False, 0)
        ssh_priv_frame = Gtk.Frame(label="SSH Private Key")
        ssh_priv_frame.set_margin_bottom(8)
        ssh_priv_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ssh_priv_box.set_margin_start(8)
        ssh_priv_box.set_margin_end(8)
        ssh_priv_box.set_margin_top(8)
        ssh_priv_box.set_margin_bottom(8)
        ssh_priv_buffer = Gtk.TextBuffer()
        ssh_priv_buffer.set_text(self._get_config_value("ssh_private_key_content", ""))
        ssh_priv_view = Gtk.TextView(buffer=ssh_priv_buffer)
        ssh_priv_view.set_monospace(True)
        ssh_priv_view.set_wrap_mode(Gtk.WrapMode.WORD)
        ssh_priv_view.set_hexpand(True)
        ssh_priv_view.set_vexpand(True)
        ssh_priv_view.set_size_request(-1, 80)
        def on_ssh_priv_changed(buffer):
            start, end = buffer.get_bounds()
            content = buffer.get_text(start, end, True)
            self._set_config_value("ssh_private_key_content", content)
        ssh_priv_buffer.connect("changed", on_ssh_priv_changed)
        ssh_priv_box.pack_start(ssh_priv_view, True, True, 0)
        ssh_priv_frame.add(ssh_priv_box)
        ssh_tab.pack_start(ssh_priv_frame, False, False, 0)
        pub_key_name_label = Gtk.Label(label="Public Key Name:")
        pub_key_name_label.set_xalign(0)
        pub_key_name_entry = Gtk.Entry()
        pub_key_name_entry.set_text(self._get_config_value("ssh_public_key_name", "id_rsa.pub"))
        def on_pub_key_name_changed(widget):
            self._set_config_value("ssh_public_key_name", widget.get_text())
        pub_key_name_entry.connect("changed", on_pub_key_name_changed)
        ssh_tab.pack_start(pub_key_name_label, False, False, 0)
        ssh_tab.pack_start(pub_key_name_entry, False, False, 0)
        ssh_pub_frame = Gtk.Frame(label="SSH Public Key")
        ssh_pub_frame.set_margin_bottom(8)
        ssh_pub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ssh_pub_box.set_margin_start(8)
        ssh_pub_box.set_margin_end(8)
        ssh_pub_box.set_margin_top(8)
        ssh_pub_box.set_margin_bottom(8)
        ssh_pub_buffer = Gtk.TextBuffer()
        ssh_pub_buffer.set_text(self._get_config_value("ssh_public_key_content", ""))
        ssh_pub_view = Gtk.TextView(buffer=ssh_pub_buffer)
        ssh_pub_view.set_monospace(True)
        ssh_pub_view.set_wrap_mode(Gtk.WrapMode.WORD)
        ssh_pub_view.set_hexpand(True)
        ssh_pub_view.set_vexpand(True)
        ssh_pub_view.set_size_request(-1, 40)
        def on_ssh_pub_changed(buffer):
            start, end = buffer.get_bounds()
            content = buffer.get_text(start, end, True)
            self._set_config_value("ssh_public_key_content", content)
        ssh_pub_buffer.connect("changed", on_ssh_pub_changed)
        ssh_pub_box.pack_start(ssh_pub_view, True, True, 0)
        ssh_pub_frame.add(ssh_pub_box)
        ssh_tab.pack_start(ssh_pub_frame, False, False, 0)
        ssh_cfg_frame = Gtk.Frame(label="SSH Config File (~/.ssh/config)")
        ssh_cfg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ssh_cfg_box.set_margin_start(8)
        ssh_cfg_box.set_margin_end(8)
        ssh_cfg_box.set_margin_top(8)
        ssh_cfg_box.set_margin_bottom(8)
        ssh_cfg_buffer = Gtk.TextBuffer()
        ssh_cfg_buffer.set_text(self._get_config_value("ssh_config_content", ""))
        ssh_cfg_view = Gtk.TextView(buffer=ssh_cfg_buffer)
        ssh_cfg_view.set_monospace(True)
        ssh_cfg_view.set_wrap_mode(Gtk.WrapMode.WORD)
        ssh_cfg_view.set_hexpand(True)
        ssh_cfg_view.set_vexpand(True)
        ssh_cfg_view.set_size_request(-1, 80)
        def on_ssh_cfg_changed(buffer):
            start, end = buffer.get_bounds()
            content = buffer.get_text(start, end, True)
            self._set_config_value("ssh_config_content", content)
        ssh_cfg_buffer.connect("changed", on_ssh_cfg_changed)
        ssh_cfg_box.pack_start(ssh_cfg_view, True, True, 0)
        ssh_cfg_frame.add(ssh_cfg_box)
        ssh_tab.pack_start(ssh_cfg_frame, False, False, 0)
        config_notebook.append_page(ssh_tab, Gtk.Label(label="SSH"))

        # --- Gnome Tab (playbook-only) ---
        gnome_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        gnome_tab.set_margin_start(10)
        gnome_tab.set_margin_end(10)
        gnome_tab.set_margin_top(10)
        gnome_tab.set_margin_bottom(10)
        gnome_info = Gtk.InfoBar()
        gnome_info.set_message_type(Gtk.MessageType.INFO)
        gnome_info_label = Gtk.Label(label="This setting is only applied when the corresponding playbook is run: Customisation/Configure Gnome Settings")
        gnome_info.get_content_area().pack_start(gnome_info_label, True, True, 0)
        gnome_info.show_all()
        gnome_tab.pack_start(gnome_info, False, False, 0)
        
        # Wallpaper Section
        wallpaper_label = Gtk.Label(label="Gnome Wallpaper:")
        wallpaper_label.set_xalign(0)
        gnome_tab.pack_start(wallpaper_label, False, False, 0)
        
        # Wallpaper previews - using FlowBox for dynamic layout
        wallpaper_scroll = Gtk.ScrolledWindow()
        wallpaper_scroll.set_min_content_height(200)
        wallpaper_scroll.set_max_content_height(300)
        
        # Use FlowBox for dynamic grid layout (like Android's RecyclerView)
        wallpaper_flowbox = Gtk.FlowBox()
        wallpaper_flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        wallpaper_flowbox.set_min_children_per_line(3)  # Minimum 3 per line
        wallpaper_flowbox.set_homogeneous(True)  # All items same size
        wallpaper_flowbox.set_row_spacing(8)
        wallpaper_flowbox.set_column_spacing(8)
        
        wallpaper_scroll.add(wallpaper_flowbox)
        gnome_tab.pack_start(wallpaper_scroll, True, True, 0)
        
        # Load wallpapers from working_directory/files/system/gnome/wallpapers
        working_directory = self._get_config_value("working_directory", "/opt/CrimsonCFG")
        wallpapers_dir = os.path.join(working_directory, "files", "system", "gnome", "wallpapers")
        wallpaper_files = []
        if os.path.exists(wallpapers_dir):
            for file in os.listdir(wallpapers_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    wallpaper_files.append(file)
        
        # Create clickable previews
        current_wallpaper = self._get_config_value("gnome_background_image", "")
        selected_wallpaper_path = None
        wallpaper_buttons = []  # Store references to buttons for selection highlighting
        
        def on_wallpaper_clicked(widget, wallpaper_path, button_index):
            nonlocal selected_wallpaper_path
            selected_wallpaper_path = wallpaper_path
            self._set_config_value("gnome_background_image", wallpaper_path)
            
            # Update visual selection - highlight selected button
            for i, btn in enumerate(wallpaper_buttons):
                if i == button_index:
                    btn.get_style_context().add_class("selected")
                else:
                    btn.get_style_context().remove_class("selected")
            
            # Update file chooser button text
            update_file_chooser_text()
            
            print(f"Selected wallpaper: {wallpaper_path}")
        
        # Also handle FlowBox selection changes
        def on_flowbox_selection_changed(flowbox):
            selected_child = flowbox.get_selected_child()
            if selected_child:
                # Find the button index
                for i, btn in enumerate(wallpaper_buttons):
                    if btn == selected_child.get_child():
                        on_wallpaper_clicked(btn, wallpaper_buttons[i], i)
                        break
        
        # Create grid of wallpaper previews
        # FlowBox will automatically calculate optimal layout
        for i, wallpaper_file in enumerate(wallpaper_files):
            wallpaper_path = os.path.join(wallpapers_dir, wallpaper_file)
            
            # Create container for button content
            button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            button_box.set_margin_start(4)
            button_box.set_margin_end(4)
            button_box.set_margin_top(4)
            button_box.set_margin_bottom(4)
            
            # Create clickable button with preview
            wallpaper_button = Gtk.Button()
            wallpaper_button.set_relief(Gtk.ReliefStyle.NONE)
            wallpaper_button.set_can_focus(False)
            
            # Add some padding and styling
            wallpaper_button.set_margin_start(2)
            wallpaper_button.set_margin_end(2)
            wallpaper_button.set_margin_top(2)
            wallpaper_button.set_margin_bottom(2)
            
            # Create image preview
            try:
                # Larger preview for better visibility
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wallpaper_path, 140, 95)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                button_box.pack_start(image, False, False, 0)
            except Exception as e:
                # Fallback if image can't be loaded
                fallback_label = Gtk.Label(label=wallpaper_file[:15] + "..." if len(wallpaper_file) > 15 else wallpaper_file)
                button_box.pack_start(fallback_label, False, False, 0)
            
            # Add filename label
            filename_label = Gtk.Label(label=wallpaper_file[:20] + "..." if len(wallpaper_file) > 20 else wallpaper_file)
            filename_label.set_line_wrap(True)
            filename_label.set_line_wrap_mode(2)  # PANGO_WRAP_WORD_CHAR
            filename_label.set_max_width_chars(20)
            filename_label.set_justify(Gtk.Justification.CENTER)
            button_box.pack_start(filename_label, False, False, 0)
            
            wallpaper_button.add(button_box)
            
            # Check if this is the currently selected wallpaper
            if wallpaper_path == current_wallpaper:
                wallpaper_button.get_style_context().add_class("selected")
            
            wallpaper_buttons.append(wallpaper_button)
            wallpaper_button.connect("clicked", on_wallpaper_clicked, wallpaper_path, len(wallpaper_buttons) - 1)
            wallpaper_flowbox.add(wallpaper_button)
        
        # Connect FlowBox selection signal
        wallpaper_flowbox.connect("selected-children-changed", on_flowbox_selection_changed)
        
        # Custom wallpaper file chooser
        gnome_bg_file_chooser = Gtk.FileChooserButton(title="Browse for Custom Wallpaper", action=Gtk.FileChooserAction.OPEN)
        gnome_bg_file_chooser.set_width_chars(50)
        
        # Set the file chooser to open in user's Pictures directory
        user_home = self._get_config_value("user_home", os.path.expanduser("~"))
        pictures_dir = os.path.join(user_home, "Pictures")
        if os.path.exists(pictures_dir):
            gnome_bg_file_chooser.set_current_folder(pictures_dir)
        
        # Function to update button text based on current selection
        def update_file_chooser_text():
            current_selection = self._get_config_value("gnome_background_image", "")
            if current_selection and os.path.exists(current_selection):
                # Show just the filename, not the full path
                filename = os.path.basename(current_selection)
                gnome_bg_file_chooser.set_title(f"Custom: {filename}")
            else:
                gnome_bg_file_chooser.set_title("Browse for Custom Wallpaper")
        
        # Set current selection if exists
        if current_wallpaper and os.path.exists(current_wallpaper):
            gnome_bg_file_chooser.set_filename(current_wallpaper)
            update_file_chooser_text()
        
        # Add label for custom wallpaper section
        custom_wallpaper_label = Gtk.Label(label="Or choose a custom wallpaper:")
        custom_wallpaper_label.set_xalign(0)
        custom_wallpaper_label.set_margin_top(10)
        gnome_tab.pack_start(custom_wallpaper_label, False, False, 0)
        gnome_tab.pack_start(gnome_bg_file_chooser, False, False, 0)
        
        def on_gnome_bg_changed(widget):
            self._set_config_value("gnome_background_image", gnome_bg_file_chooser.get_filename() or "")
            update_file_chooser_text()
        gnome_bg_file_chooser.connect("file-set", on_gnome_bg_changed)
        
        # Theme Mode Switch
        theme_label = Gtk.Label(label="Theme Mode:")
        theme_label.set_xalign(0)
        theme_combo = Gtk.ComboBoxText()
        theme_combo.append_text("System Default")
        theme_combo.append_text("Light")
        theme_combo.append_text("Dark")
        theme_combo.set_active(0)
        current_theme = self._get_config_value("theme_mode", "")
        if current_theme == "light":
            theme_combo.set_active(1)
        elif current_theme == "dark":
            theme_combo.set_active(2)
        else:
            theme_combo.set_active(0)
        def on_theme_changed(combo):
            idx = combo.get_active()
            if idx == 1:
                self._set_config_value("theme_mode", "light")
            elif idx == 2:
                self._set_config_value("theme_mode", "dark")
            else:
                self._set_config_value("theme_mode", "")
        theme_combo.connect("changed", on_theme_changed)
        gnome_tab.pack_start(theme_label, False, False, 0)
        gnome_tab.pack_start(theme_combo, False, False, 0)
        
        config_notebook.append_page(gnome_tab, Gtk.Label(label="Gnome"))

        # --- VPN Tab (playbook-only) ---
        vpn_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vpn_tab.set_margin_start(10)
        vpn_tab.set_margin_end(10)
        vpn_tab.set_margin_top(10)
        vpn_tab.set_margin_bottom(10)
        vpn_info = Gtk.InfoBar()
        vpn_info.set_message_type(Gtk.MessageType.INFO)
        vpn_info_label = Gtk.Label(label="Pre-Requirement: Install Apps/Tailscale")
        vpn_info.get_content_area().pack_start(vpn_info_label, True, True, 0)
        vpn_info.show_all()
        vpn_tab.pack_start(vpn_info, False, False, 0)
        
        # Tailscale Authentication Section
        vpn_auth_frame = Gtk.Frame(label="Tailscale Authentication")
        vpn_auth_frame.set_margin_bottom(8)
        vpn_auth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vpn_auth_box.set_margin_start(8)
        vpn_auth_box.set_margin_end(8)
        vpn_auth_box.set_margin_top(8)
        vpn_auth_box.set_margin_bottom(8)
        
        # Status label
        self.vpn_status_label = Gtk.Label(label="Ready to authenticate with Tailscale")
        self.vpn_status_label.set_halign(Gtk.Align.CENTER)
        vpn_auth_box.pack_start(self.vpn_status_label, False, False, 0)
        
        # Authentication button
        self.vpn_auth_button = Gtk.Button(label="Start Tailscale Authentication")
        self.vpn_auth_button.connect("clicked", self.on_vpn_auth_clicked)
        vpn_auth_box.pack_start(self.vpn_auth_button, False, False, 0)
        
        vpn_auth_frame.add(vpn_auth_box)
        vpn_tab.pack_start(vpn_auth_frame, False, False, 0)
        
        config_notebook.append_page(vpn_tab, Gtk.Label(label="VPN"))

    def on_vpn_auth_clicked(self, button):
        """Handle VPN authentication button click"""
        print("DEBUG: VPN authentication button clicked")
        self.main_window.logger.log_message("DEBUG: VPN authentication button clicked")
        
        # Check if we have sudo password
        if not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
            print("DEBUG: No sudo password available")
            self.main_window.logger.log_message("ERROR: No sudo password available. Please authenticate first.")
            return
        
        print("DEBUG: Sudo password available, starting Tailscale")
        self.main_window.logger.log_message("DEBUG: Sudo password available, starting Tailscale")
        
        # Update status
        self.vpn_status_label.set_text("Starting Tailscale connection...")
        self.vpn_auth_button.set_sensitive(False)
        
        # Run authentication in a separate thread
        import threading
        import subprocess
        import re
        
        def run_auth():
            try:
                # Run tailscale up and capture the URL line by line (like the shell script)
                self.main_window.logger.log_message("Running: sudo tailscale up")
                
                # Start the process
                process = subprocess.Popen(
                    ["sudo", "-S", "tailscale", "up"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Combine stdout and stderr
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True
                )
                
                # Send password
                process.stdin.write(f"{self.main_window.sudo_password}\n")
                process.stdin.flush()
                
                # Read output line by line until we find the URL
                auth_url = None
                try:
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break
                        
                        # Log each line
                        self.main_window.logger.log_message(f"Tailscale: {line.strip()}")
                        
                        # Check for login URL
                        if "https://login.tailscale.com" in line:
                            url_match = re.search(r'https://login\.tailscale\.com/[^\s]+', line)
                            if url_match:
                                auth_url = url_match.group(0)
                                self.main_window.logger.log_message(f"FOUND LOGIN URL: {auth_url}")
                                break
                except Exception as e:
                    self.main_window.logger.log_message(f"Error reading output: {e}")
                
                # Update UI with the result (on main thread)
                def update_ui():
                    if auth_url:
                        self.vpn_status_label.set_text(f"Login URL: {auth_url}")
                        self.vpn_auth_button.set_sensitive(True)
                        self.vpn_auth_button.set_label("URL Found")
                        
                        # Open browser with the login URL
                        try:
                            self.main_window.logger.log_message(f"Opening browser with URL: {auth_url}")
                            # Try Chromium first (pre-configured to avoid OOBE issues)
                            subprocess.Popen(["snap", "run", "chromium", auth_url])
                        except Exception as e:
                            self.main_window.logger.log_message(f"Failed to open Chromium: {e}")
                            # Fallback to microsoft-edge
                            try:
                                subprocess.Popen(["microsoft-edge", auth_url])
                                self.main_window.logger.log_message("Opened with Microsoft Edge fallback")
                            except Exception as e2:
                                self.main_window.logger.log_message(f"Failed to open Microsoft Edge: {e2}")
                                # Final fallback to xdg-open
                                try:
                                    subprocess.Popen(["xdg-open", auth_url])
                                    self.main_window.logger.log_message("Opened with xdg-open fallback")
                                except Exception as e3:
                                    self.main_window.logger.log_message(f"Failed to open browser with all fallbacks: {e3}")
                        
                        # Let the process continue in background
                        def background_auth():
                            try:
                                process.wait(timeout=60)  # Wait up to 60 seconds for completion
                                self.main_window.logger.log_message("Tailscale authentication completed")
                            except subprocess.TimeoutExpired:
                                self.main_window.logger.log_message("Tailscale authentication still in progress")
                            except Exception as e:
                                self.main_window.logger.log_message(f"Background auth error: {e}")
                        
                        threading.Thread(target=background_auth, daemon=True).start()
                    else:
                        self.vpn_status_label.set_text("No login URL found - check logs for details")
                        self.vpn_auth_button.set_sensitive(True)
                        self.vpn_auth_button.set_label("Check Logs")
                
                GLib.idle_add(update_ui)
                    
            except Exception as e:
                self.main_window.logger.log_message(f"ERROR: Tailscale exception: {str(e)}")
                def update_error():
                    self.vpn_status_label.set_text("Connection error occurred")
                    self.vpn_auth_button.set_sensitive(True)
                GLib.idle_add(update_error)
        
        threading.Thread(target=run_auth, daemon=True).start()

    def _get_config_value(self, key, default=None):
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        if not local_file.exists():
            # If the file doesn't exist, create it from the template using ruamel.yaml to preserve comments
            template_path = os.path.join(os.path.dirname(__file__), '../templates/local.yml.j2')
            if os.path.exists(template_path):
                from jinja2 import Template
                with open(template_path, 'r') as f:
                    template_content = f.read()
                # Render the template with all required variables
                template = Template(template_content)
                context = {
                    "system_user": getpass.getuser(),
                    "user_home": os.path.expanduser("~"),
                    "git_username": os.environ.get("GIT_USERNAME", getpass.getuser()),
                    "git_email": os.environ.get("GIT_EMAIL", "user@example.com"),
                    "working_directory": "/opt/CrimsonCFG",
                    "appimg_directory": f"/home/{getpass.getuser()}/AppImages",
                    "app_directory": "/opt/CrimsonCFG/app"
                }
                rendered = template.render(**context)
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                template_map = yaml_ruamel.load(rendered)
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(template_map, f)
            else:
                return default
        yaml_ruamel = YAML()
        yaml_ruamel.preserve_quotes = True
        with open(local_file, 'r') as f:
            try:
                local_config = yaml_ruamel.load(f) or {}
            except Exception:
                return default
        return local_config.get(key, default)

    def _set_config_value(self, key, value):
        if self.main_window.debug:
            print(f"ConfigTab: _set_config_value called with key='{key}', value='{value}'")
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        yaml_ruamel = YAML()
        yaml_ruamel.preserve_quotes = True
        # If the file doesn't exist, create it from the template using ruamel.yaml
        if not local_file.exists():
            if self.main_window.debug:
                print(f"ConfigTab: Creating local.yml from template")
            template_path = os.path.join(os.path.dirname(__file__), '../templates/local.yml.j2')
            if os.path.exists(template_path):
                from jinja2 import Template
                with open(template_path, 'r') as f:
                    template_content = f.read()
                template = Template(template_content)
                context = {
                    "system_user": getpass.getuser(),
                    "user_home": os.path.expanduser("~"),
                    "git_username": os.environ.get("GIT_USERNAME", getpass.getuser()),
                    "git_email": os.environ.get("GIT_EMAIL", "user@example.com"),
                    "working_directory": "/opt/CrimsonCFG",
                    "appimg_directory": f"/home/{getpass.getuser()}/AppImages",
                    "app_directory": "/opt/CrimsonCFG/app"
                }
                rendered = template.render(**context)
                template_map = yaml_ruamel.load(rendered)
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(template_map, f)
            else:
                local_config = yaml_ruamel.load('{}')
        # Now always load as CommentedMap
        with open(local_file, 'r') as f:
            try:
                local_config = yaml_ruamel.load(f) or yaml_ruamel.load('{}')
            except Exception as e:
                if self.main_window.debug:
                    print(f"ConfigTab: Error loading local.yml: {e}")
                local_config = yaml_ruamel.load('{}')
        local_config[key] = value
        if self.main_window.debug:
            print(f"ConfigTab: Writing to {local_file}")
        with open(local_file, 'w') as f:
            yaml_ruamel.dump(local_config, f)
        if self.main_window.debug:
            print(f"ConfigTab: Successfully wrote to local.yml")
        self._reload_main_config()
        # Refresh playbook list to update requirement status
        if hasattr(self.main_window, 'playbook_manager'):
            self.main_window.playbook_manager.update_playbook_list()

    def _get_chromium_policies_content(self):
        """Load the current chromium policies template content"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), '../templates/chromium_policies.j2')
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    return f.read()
            else:
                return "// Template file not found"
        except Exception as e:
            return f"// Error loading template: {e}"

    def _save_chromium_policies_content(self, content):
        """Save the chromium policies content back to the template file"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), '../templates/chromium_policies.j2')
            with open(template_path, 'w') as f:
                f.write(content)
            if self.main_window.debug:
                print(f"ConfigTab: Saved chromium policies to {template_path}")
        except Exception as e:
            if self.main_window.debug:
                print(f"ConfigTab: Error saving chromium policies: {e}")
            # Show error dialog to user
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Saving Chromium Policies",
                secondary_text=f"Failed to save the policies file: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _get_master_preferences_content(self):
        """Load the current master preferences template content"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), '../templates/master_preferences')
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    return f.read()
            else:
                return "// Template file not found"
        except Exception as e:
            return f"// Error loading template: {e}"

    def _save_master_preferences_content(self, content):
        """Save the master preferences content back to the template file"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), '../templates/master_preferences')
            with open(template_path, 'w') as f:
                f.write(content)
            if self.main_window.debug:
                print(f"ConfigTab: Saved master preferences to {template_path}")
        except Exception as e:
            if self.main_window.debug:
                print(f"ConfigTab: Error saving master preferences: {e}")
            # Show error dialog to user
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Saving Master Preferences",
                secondary_text=f"Failed to save the master preferences file: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _reload_main_config(self):
        self.main_window.config = self.main_window.config_manager.load_config()
        self.main_window.user = self.main_window.config.get("settings", {}).get("default_user", "user")
        self.main_window.user_home = f"/home/{self.main_window.user}"
        self.main_window.working_directory = self.main_window.config.get("settings", {}).get("working_directory", f"{self.main_window.user_home}/CrimsonCFG")
        if "{{ user_home }}" in self.main_window.working_directory:
            self.main_window.working_directory = self.main_window.working_directory.replace("{{ user_home }}", self.main_window.user_home)
        self.main_window.inventory_file = f"{self.main_window.working_directory}/hosts.ini" 