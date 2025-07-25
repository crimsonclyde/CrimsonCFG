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
        app_tab.pack_start(wd_label, False, False, 0)
        app_tab.pack_start(wd_entry, False, False, 0)
        # Background Image (optional)
        bg_label = Gtk.Label(label="Background Image (optional):")
        bg_label.set_xalign(0)
        bg_file_chooser = Gtk.FileChooserButton(title="Select Background Image", action=Gtk.FileChooserAction.OPEN)
        bg_file_chooser.set_width_chars(40)
        bg_file_chooser.set_filename(self._get_config_value("background_image", ""))
        app_tab.pack_start(bg_label, False, False, 0)
        app_tab.pack_start(bg_file_chooser, False, False, 0)
        # Restore Clear Background Image button
        bg_clear_btn = Gtk.Button(label="Clear Background Image")
        def on_clear_bg(btn):
            bg_file_chooser.unselect_all()
            self._set_config_value("background_image", "")
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
        app_tab.pack_start(color_label, False, False, 0)
        app_tab.pack_start(color_btn, False, False, 0)
        # Restore Reset Color to Default button
        color_reset_btn = Gtk.Button(label="Reset Color to Default")
        def on_reset_color(btn):
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse("#181a20")
            color_btn.set_rgba(gdk_rgba)
            self._set_config_value("background_color", "#181a20")
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
        color_reset_btn.connect("clicked", on_reset_color)
        app_tab.pack_start(color_reset_btn, False, False, 0)
        save_btn = Gtk.Button(label="Save Application Settings")
        def on_save_app(btn):
            self._set_config_value("working_directory", wd_entry.get_text())
            self._set_config_value("background_image", bg_file_chooser.get_filename() or "")
            rgba = color_btn.get_rgba()
            hex_color = "#%02x%02x%02x" % (int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))
            self._set_config_value("background_color", hex_color)
            self._reload_main_config()
            self.main_window.gui_builder.apply_css()
        save_btn.connect("clicked", on_save_app)
        app_tab.pack_start(save_btn, False, False, 0)
        config_notebook.append_page(app_tab, Gtk.Label(label="Application"))

        # --- Web Browser Tab (playbook-only) ---
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
        config_notebook.append_page(browser_tab, Gtk.Label(label="Web Browser (Chromium)"))

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
        ssh_priv_box.pack_start(ssh_priv_view, True, True, 0)
        ssh_priv_frame.add(ssh_priv_box)
        ssh_tab.pack_start(ssh_priv_frame, False, False, 0)
        pub_key_name_label = Gtk.Label(label="Public Key Name:")
        pub_key_name_label.set_xalign(0)
        pub_key_name_entry = Gtk.Entry()
        pub_key_name_entry.set_text(self._get_config_value("ssh_public_key_name", "id_rsa.pub"))
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
                # Render the template minimally (no variables, just as YAML)
                template = Template(template_content)
                rendered = template.render(system_user=getpass.getuser(), git_email='', git_username='')
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
        config_dir = Path.home() / ".config/com.crimson.cfg"
        local_file = config_dir / "local.yml"
        yaml_ruamel = YAML()
        yaml_ruamel.preserve_quotes = True
        # If the file doesn't exist, create it from the template using ruamel.yaml
        if not local_file.exists():
            template_path = os.path.join(os.path.dirname(__file__), '../templates/local.yml.j2')
            if os.path.exists(template_path):
                from jinja2 import Template
                with open(template_path, 'r') as f:
                    template_content = f.read()
                template = Template(template_content)
                rendered = template.render(system_user=getpass.getuser(), git_email='', git_username='')
                template_map = yaml_ruamel.load(rendered)
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(template_map, f)
            else:
                local_config = yaml_ruamel.load('{}')
        # Now always load as CommentedMap
        with open(local_file, 'r') as f:
            try:
                local_config = yaml_ruamel.load(f) or yaml_ruamel.load('{}')
            except Exception:
                local_config = yaml_ruamel.load('{}')
        local_config[key] = value
        with open(local_file, 'w') as f:
            yaml_ruamel.dump(local_config, f)
        self._reload_main_config()

    def _reload_main_config(self):
        self.main_window.config = self.main_window.config_manager.load_config()
        self.main_window.user = self.main_window.config.get("settings", {}).get("default_user", "user")
        self.main_window.user_home = f"/home/{self.main_window.user}"
        self.main_window.working_directory = self.main_window.config.get("settings", {}).get("working_directory", f"{self.main_window.user_home}/CrimsonCFG")
        if "{{ user_home }}" in self.main_window.working_directory:
            self.main_window.working_directory = self.main_window.working_directory.replace("{{ user_home }}", self.main_window.user_home)
        self.main_window.inventory_file = f"{self.main_window.working_directory}/hosts.ini" 