#!/usr/bin/env python3
"""
ConfigTab: Refactored for new structure and instant/apply/save logic
"""
from gi.repository import Gtk, Gdk
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
        wd_label = Gtk.Label(label="Working Directory (user override, see docs):")
        wd_label.set_xalign(0)
        wd_entry = Gtk.Entry()
        wd_entry.set_text(self._get_config_value("working_directory", ""))
        
        # Add changed signal to save working directory instantly
        def on_wd_changed(widget):
            new_wd = widget.get_text()
            if self.main_window.debug:
                print(f"ConfigTab: Working directory changed to: '{new_wd}'")
            self._set_config_value("working_directory", new_wd)
        wd_entry.connect("changed", on_wd_changed)
        
        app_tab.pack_start(wd_label, False, False, 0)
        app_tab.pack_start(wd_entry, False, False, 0)
        # Background Image (optional)
        bg_label = Gtk.Label(label="Background Image (optional):")
        bg_label.set_xalign(0)
        bg_file_chooser = Gtk.FileChooserButton(title="Select Background Image", action=Gtk.FileChooserAction.OPEN)
        bg_file_chooser.set_width_chars(40)
        bg_filename = self._get_config_value("app_background_image", "")
        if self.main_window.debug:
            print(f"ConfigTab: Setting background filename to: '{bg_filename}'")
        if bg_filename and os.path.exists(bg_filename):
            bg_file_chooser.set_filename(bg_filename)
            # Also set the current folder to help with display
            bg_file_chooser.set_current_folder(os.path.dirname(bg_filename))
        else:
            bg_file_chooser.unselect_all()
        
        # Add file-set signal to save instantly
        def on_bg_file_set(widget):
            selected_path = widget.get_filename() or ""
            if self.main_window.debug:
                print(f"ConfigTab: Background file selected: '{selected_path}'")
            self._set_config_value("app_background_image", selected_path)
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
        bg_file_chooser.connect("file-set", on_bg_file_set)
        
        app_tab.pack_start(bg_label, False, False, 0)
        app_tab.pack_start(bg_file_chooser, False, False, 0)
        # Restore Clear Background Image button
        bg_clear_btn = Gtk.Button(label="Clear Background Image")
        def on_clear_bg(btn):
            bg_file_chooser.unselect_all()
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
        gnome_bg_label = Gtk.Label(label="Gnome Background Image:")
        gnome_bg_label.set_xalign(0)
        gnome_bg_file_chooser = Gtk.FileChooserButton(title="Select Gnome Background Image", action=Gtk.FileChooserAction.OPEN)
        gnome_bg_file_chooser.set_width_chars(40)
        gnome_bg_file_chooser.set_filename(self._get_config_value("gnome_background_image", ""))
        gnome_tab.pack_start(gnome_bg_label, False, False, 0)
        gnome_tab.pack_start(gnome_bg_file_chooser, False, False, 0)
        def on_gnome_bg_changed(widget):
            self._set_config_value("gnome_background_image", gnome_bg_file_chooser.get_filename() or "")
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