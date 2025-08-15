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
import requests
from gi.repository import GdkPixbuf
import hashlib

class ConfigTab(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_window = main_window
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        self.set_margin_top(15)
        
        # Store references to SSH key components for easy refresh
        self.ssh_key_frame = None
        self.ssh_key_box = None
        self.ssh_keys_flowbox = None
        
        self._build_tab()

    def _apply_gnome_wallpaper(self, wallpaper_path):
        """Apply wallpaper instantly using gsettings"""
        print(f"_apply_gnome_wallpaper: Starting with path: {wallpaper_path}")
        
        if not wallpaper_path or not os.path.exists(wallpaper_path):
            print(f"_apply_gnome_wallpaper: Path invalid or file doesn't exist: {wallpaper_path}")
            return False
        
        try:
            import subprocess
            # Set wallpaper for both light and dark modes
            wallpaper_uri = f"file://{wallpaper_path}"
            print(f"_apply_gnome_wallpaper: URI: {wallpaper_uri}")
            
            # Get current user's environment
            user_id = os.getuid()
            runtime_dir = f"/run/user/{user_id}"
            print(f"_apply_gnome_wallpaper: User ID: {user_id}, Runtime dir: {runtime_dir}")
            
            # Set light mode wallpaper
            print(f"_apply_gnome_wallpaper: Setting light mode wallpaper...")
            result = subprocess.run([
                'gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', wallpaper_uri
            ], check=True, env=dict(os.environ, XDG_RUNTIME_DIR=runtime_dir), capture_output=True, text=True)
            print(f"_apply_gnome_wallpaper: Light mode result: {result.returncode}")
            
            # Set dark mode wallpaper
            print(f"_apply_gnome_wallpaper: Setting dark mode wallpaper...")
            result = subprocess.run([
                'gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', wallpaper_uri
            ], check=True, env=dict(os.environ, XDG_RUNTIME_DIR=runtime_dir), capture_output=True, text=True)
            print(f"_apply_gnome_wallpaper: Dark mode result: {result.returncode}")
            
            print(f"Applied wallpaper: {wallpaper_path}")
            return True
        except Exception as e:
            print(f"Failed to apply wallpaper: {e}")
            return False

    def _apply_gnome_theme(self, theme_mode):
        """Apply theme instantly using gsettings"""
        try:
            import subprocess
            
            if theme_mode == "dark":
                color_scheme = "prefer-dark"
                gtk_theme = "Adwaita-dark"
            elif theme_mode == "light":
                color_scheme = "default"
                gtk_theme = "Adwaita"
            else:
                # System default - don't change anything
                return True
            
            # Get current user's environment
            user_id = os.getuid()
            runtime_dir = f"/run/user/{user_id}"
            
            # Set color scheme
            subprocess.run([
                'gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', color_scheme
            ], check=True, env=dict(os.environ, XDG_RUNTIME_DIR=runtime_dir))
            
            # Set GTK theme
            subprocess.run([
                'gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', gtk_theme
            ], check=True, env=dict(os.environ, XDG_RUNTIME_DIR=runtime_dir))
            
            print(f"Applied theme: {theme_mode}")
            return True
        except Exception as e:
            print(f"Failed to apply theme: {e}")
            return False
        


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
                
                # Check file size and resize if necessary
                try:
                    # Get original image info
                    original_pixbuf = GdkPixbuf.Pixbuf.new_from_file(selected_path)
                    original_width = original_pixbuf.get_width()
                    original_height = original_pixbuf.get_height()
                    file_size = os.path.getsize(selected_path)
                    
                    # GNOME avatar size limits (typically 512x512 pixels and ~100KB)
                    max_dimension = 512
                    max_file_size = 100 * 1024  # 100KB
                    
                    # Check if resizing is needed
                    needs_resize = (original_width > max_dimension or 
                                  original_height > max_dimension or 
                                  file_size > max_file_size)
                    
                    if needs_resize:
                        # Calculate new dimensions while maintaining aspect ratio
                        if original_width > original_height:
                            new_width = max_dimension
                            new_height = int((original_height * max_dimension) / original_width)
                        else:
                            new_height = max_dimension
                            new_width = int((original_width * max_dimension) / original_height)
                        
                        # Resize the image
                        resized_pixbuf = original_pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
                        
                        # Save the resized image
                        resized_pixbuf.savev(dest_path, "png", [], [])
                        
                        # Show info message to user
                        self._show_info_dialog(
                            "Avatar Image Resized",
                            f"Your avatar image was automatically resized from {original_width}x{original_height} to {new_width}x{new_height} pixels to meet GNOME's requirements."
                        )
                    else:
                        # Copy original file if no resizing needed
                        import shutil
                        shutil.copyfile(selected_path, dest_path)
                        
                except Exception as e:
                    print(f"Failed to process avatar image: {e}")
                    # Try to copy original file as fallback
                    try:
                        import shutil
                        shutil.copyfile(selected_path, dest_path)
                    except Exception as copy_error:
                        print(f"Failed to copy avatar image: {copy_error}")
                        self._show_error_dialog("Avatar Error", f"Failed to process avatar image: {copy_error}")
                        return
                
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
                    result = subprocess.run([
                        'dbus-send', '--system', '--print-reply',
                        '--dest=org.freedesktop.Accounts',
                        f'/org/freedesktop/Accounts/User{os.getuid()}',
                        'org.freedesktop.Accounts.User.SetIconFile',
                        f'string:{dest_path}'
                    ], check=True, capture_output=True, text=True)
                    print("Avatar set successfully")
                except subprocess.CalledProcessError as e:
                    error_msg = f"Failed to set GNOME avatar: {e.stderr.strip() if e.stderr else str(e)}"
                    print(error_msg)
                    self._show_error_dialog("Avatar Error", error_msg)
                except Exception as e:
                    error_msg = f"Failed to set GNOME avatar: {e}"
                    print(error_msg)
                    self._show_error_dialog("Avatar Error", error_msg)
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
        bg_paths = []  # Store background paths separately
        
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
            selected_children = flowbox.get_selected_children()
            if selected_children:
                selected_child = selected_children[0]  # Get first selected child
                # Find the button index
                for i, btn in enumerate(bg_buttons):
                    if btn == selected_child.get_child():
                        on_bg_image_clicked(btn, bg_paths[i], i)
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
            bg_paths.append(bg_path)  # Store the background path
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
        
        # SSH Key Creation Section
        self.ssh_key_frame = Gtk.Frame(label="SSH Key Management")
        self.ssh_key_frame.set_margin_bottom(8)
        
        # Make SSH Key frame collapsible
        ssh_key_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ssh_key_header_box.set_margin_bottom(5)
        
        ssh_key_toggle_btn = Gtk.ToggleButton(label="SSH Key Management")
        ssh_key_toggle_btn.set_active(False)  # Start collapsed
        ssh_key_header_box.pack_start(ssh_key_toggle_btn, False, False, 0)
        
        # Add a small arrow indicator
        ssh_key_arrow_label = Gtk.Label(label="▼")
        ssh_key_arrow_label.set_margin_start(5)
        ssh_key_header_box.pack_start(ssh_key_arrow_label, False, False, 0)
        
        ssh_tab.pack_start(ssh_key_header_box, False, False, 0)
        
        # Create the revealer for SSH key management
        ssh_key_revealer = Gtk.Revealer()
        ssh_key_revealer.set_reveal_child(False)  # Start collapsed
        ssh_tab.pack_start(ssh_key_revealer, False, False, 0)
        
        self.ssh_key_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.ssh_key_box.set_margin_start(8)
        self.ssh_key_box.set_margin_end(8)
        self.ssh_key_box.set_margin_top(8)
        self.ssh_key_box.set_margin_bottom(8)
        
        # Check for existing SSH keys
        user_home = self._get_config_value("user_home", os.path.expanduser("~"))
        ssh_dir = os.path.join(user_home, ".ssh")
        existing_keys = []
        if os.path.exists(ssh_dir):
            for file in os.listdir(ssh_dir):
                if file.endswith(('.pub', '_rsa', '_ed25519', '_ecdsa')):
                    existing_keys.append(file)
        
        if existing_keys:
            # Show existing keys as cards
            keys_scrolled = Gtk.ScrolledWindow()
            keys_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            keys_scrolled.set_size_request(-1, 150)
            
            self.ssh_keys_flowbox = Gtk.FlowBox()
            self.ssh_keys_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
            self.ssh_keys_flowbox.set_min_children_per_line(2)
            self.ssh_keys_flowbox.set_homogeneous(False)
            self.ssh_keys_flowbox.set_row_spacing(4)
            self.ssh_keys_flowbox.set_column_spacing(4)
            
            for key_file in existing_keys:
                if key_file.endswith('.pub'):
                    # Create card for public key
                    card = self._create_ssh_key_card(key_file, ssh_dir)
                    self.ssh_keys_flowbox.add(card)
            
            keys_scrolled.add(self.ssh_keys_flowbox)
            self.ssh_key_box.pack_start(keys_scrolled, True, True, 0)
            
            bitwarden_info = Gtk.Label(label="💡 Tip: You can store your SSH keys securely in Bitwarden app")
            bitwarden_info.set_line_wrap(True)
            self.ssh_key_box.pack_start(bitwarden_info, False, False, 0)
        else:
            # No keys found - show create button
            create_key_button = Gtk.Button(label="Create SSH Key")
            create_key_button.connect("clicked", self.on_create_ssh_key_clicked)
            self.ssh_key_box.pack_start(create_key_button, False, False, 0)
        
        self.ssh_key_frame.add(self.ssh_key_box)
        ssh_key_revealer.add(self.ssh_key_frame)
        
        # SSH Config Management Section
        ssh_manage_frame = Gtk.Frame(label="Manage SSH Config")
        
        # Make SSH Manage frame collapsible
        ssh_manage_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ssh_manage_header_box.set_margin_bottom(5)
        
        ssh_manage_toggle_btn = Gtk.ToggleButton(label="Manage SSH Config")
        ssh_manage_toggle_btn.set_active(False)  # Start collapsed
        ssh_manage_header_box.pack_start(ssh_manage_toggle_btn, False, False, 0)
        
        # Add a small arrow indicator
        ssh_manage_arrow_label = Gtk.Label(label="▼")
        ssh_manage_arrow_label.set_margin_start(5)
        ssh_manage_header_box.pack_start(ssh_manage_arrow_label, False, False, 0)
        
        ssh_tab.pack_start(ssh_manage_header_box, False, False, 0)
        
        # Create the revealer for SSH config management
        ssh_manage_revealer = Gtk.Revealer()
        ssh_manage_revealer.set_reveal_child(False)  # Start collapsed
        ssh_tab.pack_start(ssh_manage_revealer, False, False, 0)
        
        ssh_manage_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)  # Reduced from 8
        ssh_manage_box.set_margin_start(6)   # Reduced from 8
        ssh_manage_box.set_margin_end(6)     # Reduced from 8
        ssh_manage_box.set_margin_top(6)     # Reduced from 8
        ssh_manage_box.set_margin_bottom(6)  # Reduced from 8
        
        # Add Host button
        add_host_button = Gtk.Button(label="Add Host")
        add_host_button.connect("clicked", lambda btn: self._show_ssh_host_dialog())
        ssh_manage_box.pack_start(add_host_button, False, False, 0)
        
        # Loading indicator
        self.ssh_loading_label = Gtk.Label(label="Loading SSH configuration...")
        self.ssh_loading_label.set_halign(Gtk.Align.CENTER)
        ssh_manage_box.pack_start(self.ssh_loading_label, False, False, 0)
        
        # Scrolled window for host cards
        self.ssh_hosts_scrolled = Gtk.ScrolledWindow()
        self.ssh_hosts_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.ssh_hosts_scrolled.set_size_request(-1, 200)  # Reduced from 300 to 200
        
        # FlowBox for host cards
        self.ssh_hosts_flowbox = Gtk.FlowBox()
        self.ssh_hosts_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.ssh_hosts_flowbox.set_min_children_per_line(3)  # Increased from 2 to 3 for more compact layout
        self.ssh_hosts_flowbox.set_homogeneous(False)
        self.ssh_hosts_flowbox.set_row_spacing(4)  # Reduced from 8 to 4
        self.ssh_hosts_flowbox.set_column_spacing(4)  # Reduced from 8 to 4
        
        self.ssh_hosts_scrolled.add(self.ssh_hosts_flowbox)
        ssh_manage_box.pack_start(self.ssh_hosts_scrolled, True, True, 0)
        
        ssh_manage_frame.add(ssh_manage_box)
        ssh_manage_revealer.add(ssh_manage_frame)
        
        # Accordion-style behavior - only one section open at a time
        def on_ssh_key_toggle(button):
            is_active = button.get_active()
            ssh_key_revealer.set_reveal_child(is_active)
            ssh_key_arrow_label.set_text("▲" if is_active else "▼")
            
            # Close other sections if this one is opening
            if is_active:
                ssh_manage_toggle_btn.set_active(False)
        
        def on_ssh_manage_toggle(button):
            is_active = button.get_active()
            if self.main_window.debug:
                print(f"ConfigTab: SSH Manage toggle clicked, active: {is_active}")
            ssh_manage_revealer.set_reveal_child(is_active)
            ssh_manage_arrow_label.set_text("▲" if is_active else "▼")
            
            # Close other sections if this one is opening
            if is_active:
                ssh_key_toggle_btn.set_active(False)
                # Load SSH config when expanding this section
                if self.main_window.debug:
                    print(f"ConfigTab: Loading SSH hosts asynchronously")
                self._load_ssh_hosts_async()
        
        ssh_key_toggle_btn.connect("toggled", on_ssh_key_toggle)
        ssh_manage_toggle_btn.connect("toggled", on_ssh_manage_toggle)
        
        config_notebook.append_page(ssh_tab, Gtk.Label(label="SSH"))

        # --- Gnome Tab (instant) ---
        gnome_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        gnome_tab.set_margin_start(10)
        gnome_tab.set_margin_end(10)
        gnome_tab.set_margin_top(10)
        gnome_tab.set_margin_bottom(10)
        
        # Wallpaper Section
        wallpaper_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        wallpaper_label = Gtk.Label(label="Gnome Wallpaper:")
        wallpaper_label.set_xalign(0)
        wallpaper_row.pack_start(wallpaper_label, False, False, 0)
        # Lightning bolt unicode: \u26A1
        instant_icon = Gtk.Label(label="\u26A1")
        instant_icon.set_tooltip_text("Instantly applied")
        wallpaper_row.pack_start(instant_icon, False, False, 0)
        gnome_tab.pack_start(wallpaper_row, False, False, 0)
        
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
            
            # Apply wallpaper instantly
            print(f"ConfigTab: About to apply wallpaper: {wallpaper_path}")
            success = self._apply_gnome_wallpaper(wallpaper_path)
            print(f"ConfigTab: Wallpaper application {'successful' if success else 'failed'}")
            
            print(f"Selected and applied wallpaper: {wallpaper_path}")
        
        # Also handle FlowBox selection changes
        def on_flowbox_selection_changed(flowbox):
            selected_children = flowbox.get_selected_children()
            if selected_children:
                # Get the first selected child (FlowBox typically allows single selection)
                selected_child = selected_children[0]
                # Find the button index
                for i, btn in enumerate(wallpaper_buttons):
                    if btn == selected_child.get_child():
                        # Get the wallpaper path for this button index
                        wallpaper_path = os.path.join(wallpapers_dir, wallpaper_files[i])
                        on_wallpaper_clicked(btn, wallpaper_path, i)
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
        custom_wallpaper_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        custom_wallpaper_label = Gtk.Label(label="Or choose a custom wallpaper:")
        custom_wallpaper_label.set_xalign(0)
        custom_wallpaper_row.pack_start(custom_wallpaper_label, False, False, 0)
        # Lightning bolt unicode: \u26A1
        instant_icon = Gtk.Label(label="\u26A1")
        instant_icon.set_tooltip_text("Instantly applied")
        custom_wallpaper_row.pack_start(instant_icon, False, False, 0)
        custom_wallpaper_row.set_margin_top(10)
        gnome_tab.pack_start(custom_wallpaper_row, False, False, 0)
        gnome_tab.pack_start(gnome_bg_file_chooser, False, False, 0)
        
        def on_gnome_bg_changed(widget):
            wallpaper_path = gnome_bg_file_chooser.get_filename() or ""
            self._set_config_value("gnome_background_image", wallpaper_path)
            update_file_chooser_text()
            
            # Apply wallpaper instantly
            if wallpaper_path:
                print(f"ConfigTab: About to apply custom wallpaper: {wallpaper_path}")
                success = self._apply_gnome_wallpaper(wallpaper_path)
                print(f"ConfigTab: Custom wallpaper application {'successful' if success else 'failed'}")
        gnome_bg_file_chooser.connect("file-set", on_gnome_bg_changed)
        
        # Theme Mode Switch
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        theme_label = Gtk.Label(label="Theme Mode:")
        theme_label.set_xalign(0)
        theme_row.pack_start(theme_label, False, False, 0)
        # Lightning bolt unicode: \u26A1
        instant_icon = Gtk.Label(label="\u26A1")
        instant_icon.set_tooltip_text("Instantly applied")
        theme_row.pack_start(instant_icon, False, False, 0)
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
                theme_mode = "light"
            elif idx == 2:
                theme_mode = "dark"
            else:
                theme_mode = ""
            
            self._set_config_value("theme_mode", theme_mode)
            
            # Apply theme instantly
            print(f"ConfigTab: About to apply theme: {theme_mode}")
            success = self._apply_gnome_theme(theme_mode)
            print(f"ConfigTab: Theme application {'successful' if success else 'failed'}")
        theme_combo.connect("changed", on_theme_changed)
        gnome_tab.pack_start(theme_row, False, False, 0)
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

    def on_create_ssh_key_clicked(self, button):
        """Handle SSH key creation button click"""
        import subprocess
        import threading
        
        def create_ssh_key():
            try:
                user_home = self._get_config_value("user_home", os.path.expanduser("~"))
                ssh_dir = os.path.join(user_home, ".ssh")
                
                # Create .ssh directory if it doesn't exist
                if not os.path.exists(ssh_dir):
                    os.makedirs(ssh_dir, mode=0o700)
                
                # Run ssh-keygen to create a new key
                key_path = os.path.join(ssh_dir, "id_ed25519")
                user = self._get_config_value("user", getpass.getuser())
                comment = f"{user}@CrimsonCFG.de"
                
                # Show a dialog asking for passphrase
                dialog = Gtk.Dialog(
                    title="SSH Key Passphrase",
                    transient_for=self.main_window.window,
                    modal=True,
                    destroy_with_parent=True
                )
                dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
                dialog.add_button("Create Key", Gtk.ResponseType.OK)
                
                # Add content
                content_area = dialog.get_content_area()
                content_area.set_spacing(10)
                content_area.set_margin_start(20)
                content_area.set_margin_end(20)
                content_area.set_margin_top(20)
                content_area.set_margin_bottom(20)
                
                info_label = Gtk.Label(label="Enter a passphrase for your SSH key (recommended for security):")
                info_label.set_line_wrap(True)
                content_area.pack_start(info_label, False, False, 0)
                

                
                passphrase_entry = Gtk.Entry()
                passphrase_entry.set_visibility(False)  # Hide the passphrase
                passphrase_entry.set_placeholder_text("Enter passphrase (minimum 8 characters)")
                content_area.pack_start(passphrase_entry, False, False, 0)
                
                confirm_entry = Gtk.Entry()
                confirm_entry.set_visibility(False)
                confirm_entry.set_placeholder_text("Confirm passphrase")
                content_area.pack_start(confirm_entry, False, False, 0)
                
                # Visual feedback indicators
                feedback_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                feedback_box.set_margin_start(10)
                feedback_box.set_margin_top(5)
                
                # Length indicator
                length_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                length_icon = Gtk.Label(label="⭕")
                length_label = Gtk.Label(label="At least 8 characters")
                length_row.pack_start(length_icon, False, False, 0)
                length_row.pack_start(length_label, False, False, 0)
                feedback_box.pack_start(length_row, False, False, 0)
                
                # Match indicator
                match_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                match_icon = Gtk.Label(label="⭕")
                match_label = Gtk.Label(label="Passphrases match")
                match_row.pack_start(match_icon, False, False, 0)
                match_row.pack_start(match_label, False, False, 0)
                feedback_box.pack_start(match_row, False, False, 0)
                
                # Breach indicator
                breach_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                breach_icon = Gtk.Label(label="⭕")
                breach_label = Gtk.Label(label="Not found in data breaches")
                breach_row.pack_start(breach_icon, False, False, 0)
                breach_row.pack_start(breach_label, False, False, 0)
                feedback_box.pack_start(breach_row, False, False, 0)
                
                content_area.pack_start(feedback_box, False, False, 0)
                
                dialog.show_all()
                
                def check_passphrase_strength(passphrase):
                    """Check passphrase strength and breach status"""
                    if len(passphrase) < 8:
                        return False, "❌ Passphrase must be at least 8 characters long", 0
                    
                    # Check against HaveIBeenPwned API (k-anonymity)
                    try:
                        # Hash the passphrase with SHA-1
                        sha1_hash = hashlib.sha1(passphrase.encode('utf-8')).hexdigest().upper()
                        prefix = sha1_hash[:5]
                        suffix = sha1_hash[5:]
                        
                        # Query HaveIBeenPwned API with timeout and error handling
                        url = f"https://api.pwnedpasswords.com/range/{prefix}"
                        response = requests.get(url, timeout=3)  # Reduced timeout
                        
                        if response.status_code == 200:
                            # Check if our hash suffix is in the response
                            for line in response.text.split('\n'):
                                if line.startswith(suffix):
                                    count = int(line.split(':')[1])
                                    return False, f"❌ This passphrase has been found in {count:,} data breaches", count
                        
                        return True, "✅ Passphrase meets security requirements", 0
                        
                    except ImportError:
                        # requests library not available
                        return True, "✅ Passphrase length OK (breach check unavailable)", 0
                    except Exception as e:
                        # Any other error (network, timeout, etc.)
                        if self.main_window.debug:
                            print(f"ConfigTab: Breach check error: {e}")
                        return True, "✅ Passphrase length OK (breach check unavailable)", 0
                
                def update_visual_feedback():
                    """Update all visual feedback indicators"""
                    passphrase = passphrase_entry.get_text()
                    confirm = confirm_entry.get_text()
                    
                    # Length check
                    if len(passphrase) >= 8:
                        length_icon.set_text("✅")
                        length_label.set_markup('<span color="green">At least 8 characters</span>')
                    else:
                        length_icon.set_text("❌")
                        length_label.set_markup('<span color="red">At least 8 characters</span>')
                    
                    # Match check
                    if passphrase and confirm:
                        if passphrase == confirm:
                            match_icon.set_text("✅")
                            match_label.set_markup('<span color="green">Passphrases match</span>')
                        else:
                            match_icon.set_text("❌")
                            match_label.set_markup('<span color="red">Passphrases match</span>')
                    else:
                        match_icon.set_text("⭕")
                        match_label.set_text("Passphrases match")
                    
                    # Breach check (only if passphrase is long enough)
                    if len(passphrase) >= 8:
                        try:
                            is_safe, message, breach_count = check_passphrase_strength(passphrase)
                            if is_safe:
                                breach_icon.set_text("✅")
                                breach_label.set_markup('<span color="green">Not found in data breaches</span>')
                            else:
                                breach_icon.set_text("❌")
                                breach_label.set_markup(f'<span color="red">Found in {breach_count:,} data breaches</span>')
                        except Exception as e:
                            # Fallback if breach check fails
                            if self.main_window.debug:
                                print(f"ConfigTab: Visual feedback breach check error: {e}")
                            breach_icon.set_text("⭕")
                            breach_label.set_text("Not found in data breaches")
                    else:
                        breach_icon.set_text("⭕")
                        breach_label.set_text("Not found in data breaches")
                
                def on_passphrase_changed(entry):
                    """Validate passphrase as user types"""
                    update_visual_feedback()
                
                def on_confirm_changed(entry):
                    """Validate confirmation as user types"""
                    update_visual_feedback()
                
                passphrase_entry.connect("changed", on_passphrase_changed)
                confirm_entry.connect("changed", on_confirm_changed)
                
                def on_dialog_response(dialog, response_id):
                    if response_id == Gtk.ResponseType.OK:
                        passphrase = passphrase_entry.get_text()
                        confirm = confirm_entry.get_text()
                        
                        if passphrase != confirm:
                            # Show error dialog
                            error_dialog = Gtk.MessageDialog(
                                transient_for=self.main_window.window,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.OK,
                                text="Passphrase Mismatch",
                                secondary_text="The passphrases do not match. Please try again."
                            )
                            error_dialog.run()
                            error_dialog.destroy()
                            return
                        
                        # Validate passphrase using visual feedback
                        if passphrase:
                            # Check length
                            if len(passphrase) < 8:
                                error_dialog = Gtk.MessageDialog(
                                    transient_for=self.main_window.window,
                                    message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.OK,
                                    text="Weak Passphrase",
                                    secondary_text="Passphrase must be at least 8 characters long.\n\nPlease choose a stronger passphrase."
                                )
                                error_dialog.run()
                                error_dialog.destroy()
                                return
                            
                            # Check breach status
                            is_safe, message, breach_count = check_passphrase_strength(passphrase)
                            if not is_safe:
                                error_dialog = Gtk.MessageDialog(
                                    transient_for=self.main_window.window,
                                    message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.OK,
                                    text="Compromised Passphrase",
                                    secondary_text=f"{message}\n\nPlease choose a different passphrase that hasn't been compromised."
                                )
                                error_dialog.run()
                                error_dialog.destroy()
                                return
                        
                        # Create the key with passphrase
                        try:
                            if passphrase:
                                # Use -N with passphrase and -C for comment
                                cmd = ["ssh-keygen", "-t", "ed25519", "-f", key_path, "-N", passphrase, "-C", comment]
                            else:
                                # Empty passphrase with comment
                                cmd = ["ssh-keygen", "-t", "ed25519", "-f", key_path, "-N", "", "-C", comment]
                            
                            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                            
                            # Show success dialog with backup reminder
                            success_dialog = Gtk.Dialog(
                                title="SSH Key Created",
                                transient_for=self.main_window.window,
                                modal=True,
                                destroy_with_parent=True
                            )
                            success_dialog.add_button("Close", Gtk.ResponseType.CLOSE)
                            
                            # Add content
                            content_area = success_dialog.get_content_area()
                            content_area.set_spacing(10)
                            content_area.set_margin_start(20)
                            content_area.set_margin_end(20)
                            content_area.set_margin_top(20)
                            content_area.set_margin_bottom(20)
                            
                            # Success message
                            success_label = Gtk.Label(label="🔐 SSH Key Created Successfully!")
                            success_label.set_markup('<span size="large" weight="bold">🔐 SSH Key Created Successfully!</span>')
                            content_area.pack_start(success_label, False, False, 0)
                            
                            # Backup reminder
                            backup_label = Gtk.Label(label="⚠️  Important: Please backup your SSH keys!")
                            backup_label.set_markup('<span color="orange" weight="bold">⚠️  Important: Please backup your SSH keys!</span>')
                            backup_label.set_line_wrap(True)
                            content_area.pack_start(backup_label, False, False, 0)
                            
                            # Key location info
                            location_label = Gtk.Label(label="Key location:")
                            location_label.set_halign(Gtk.Align.START)
                            content_area.pack_start(location_label, False, False, 0)
                            
                            # Read-only path display
                            path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                            path_entry = Gtk.Entry()
                            path_entry.set_text(key_path)
                            path_entry.set_editable(False)
                            path_entry.set_can_focus(False)  # Make it truly read-only
                            path_entry.set_size_request(300, -1)
                            
                            copy_button = Gtk.Button(label="Copy Path")
                            copy_button.connect("clicked", lambda btn: self._copy_to_clipboard(path_entry.get_text()))
                            
                            open_folder_button = Gtk.Button(label="Open .ssh Folder")
                            open_folder_button.connect("clicked", lambda btn: self._open_ssh_folder(ssh_dir))
                            
                            path_box.pack_start(path_entry, True, True, 0)
                            path_box.pack_start(copy_button, False, False, 0)
                            path_box.pack_start(open_folder_button, False, False, 0)
                            content_area.pack_start(path_box, False, False, 0)
                            
                            # Comment info
                            comment_label = Gtk.Label(label=f"Comment: {comment}")
                            comment_label.set_halign(Gtk.Align.START)
                            content_area.pack_start(comment_label, False, False, 0)
                            
                            # Bitwarden tip with glassy effect
                            tip_frame = Gtk.Frame()
                            tip_frame.set_margin_top(10)
                            tip_frame.set_margin_bottom(10)
                            
                            # Apply glassy styling
                            tip_style_context = tip_frame.get_style_context()
                            tip_style_context.add_class("tip-frame")
                            
                            tip_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                            tip_box.set_margin_start(10)
                            tip_box.set_margin_end(10)
                            tip_box.set_margin_top(10)
                            tip_box.set_margin_bottom(10)
                            
                            bitwarden_label = Gtk.Label(label="💡 Tip: Store your SSH keys securely in Bitwarden app for backup and access from other devices")
                            bitwarden_label.set_line_wrap(True)
                            tip_box.pack_start(bitwarden_label, False, False, 0)
                            
                            tip_frame.add(tip_box)
                            content_area.pack_start(tip_frame, False, False, 0)
                            
                            success_dialog.show_all()
                            
                            def on_success_dialog_response(dialog, response_id):
                                dialog.destroy()
                            
                            success_dialog.connect("response", on_success_dialog_response)
                            
                            # Refresh the SSH tab to show the new key
                            if self.main_window.debug:
                                print("ConfigTab: Refreshing SSH tab after key creation")
                            self._refresh_ssh_tab()
                            
                        except subprocess.CalledProcessError as e:
                            error_dialog = Gtk.MessageDialog(
                                transient_for=self.main_window.window,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.OK,
                                text="Error Creating SSH Key",
                                secondary_text=f"Failed to create SSH key:\n{e.stderr}"
                            )
                            error_dialog.run()
                            error_dialog.destroy()
                    
                    dialog.destroy()
                
                dialog.connect("response", on_dialog_response)
                
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self.main_window.window,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error Creating SSH Key",
                    secondary_text=f"An error occurred: {str(e)}"
                )
                error_dialog.run()
                error_dialog.destroy()
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=create_ssh_key, daemon=True).start()

    def _load_ssh_hosts_async(self):
        """Asynchronously load and parse SSH config file"""
        import threading
        
        def load_hosts():
            try:
                user_home = self._get_config_value("user_home", os.path.expanduser("~"))
                ssh_config_path = os.path.join(user_home, ".ssh", "config")
                
                if self.main_window.debug:
                    print(f"ConfigTab: Loading SSH config from {ssh_config_path}")
                
                hosts = []
                if os.path.exists(ssh_config_path):
                    with open(ssh_config_path, 'r') as f:
                        content = f.read()
                        if self.main_window.debug:
                            print(f"ConfigTab: SSH config content length: {len(content)}")
                        hosts = self._parse_ssh_config(content)
                        if self.main_window.debug:
                            print(f"ConfigTab: Parsed {len(hosts)} hosts")
                else:
                    if self.main_window.debug:
                        print(f"ConfigTab: SSH config file does not exist")
                
                # Update UI on main thread
                GLib.idle_add(self._update_ssh_hosts_display, hosts)
                
            except Exception as e:
                if self.main_window.debug:
                    print(f"ConfigTab: Error loading SSH hosts: {e}")
                GLib.idle_add(self._show_ssh_error, str(e))
        
        threading.Thread(target=load_hosts, daemon=True).start()

    def _parse_ssh_config(self, content):
        """Parse SSH config content and extract host entries"""
        if self.main_window.debug:
            print(f"ConfigTab: Parsing SSH config content")
        
        hosts = []
        lines = content.split('\n')
        current_host = None
        current_raw_lines = []
        
        if self.main_window.debug:
            print(f"ConfigTab: Processing {len(lines)} lines")
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if line_stripped.startswith('Host '):
                # Save previous host if exists
                if current_host:
                    current_host['raw_lines'] = current_raw_lines
                    hosts.append(current_host)
                    if self.main_window.debug:
                        print(f"ConfigTab: Added host: {current_host['host']}")
                
                # Start new host
                host_name = line_stripped[5:].strip()
                current_host = {
                    'host': host_name,
                    'hostname': '',
                    'port': '22',
                    'user': '',
                    'identityfile': '',
                    'identityagent': False,
                    'identitiesonly': 'no',
                    'proxycommand': '',
                    'proxycommand_enabled': False,
                    'raw_lines': []
                }
                current_raw_lines = [line]  # Include the original line with indentation
                if self.main_window.debug:
                    print(f"ConfigTab: Found new host: {host_name}")
            elif current_host and line_stripped:
                # Non-empty line for current host
                current_raw_lines.append(line)
                
                # Parse common SSH options
                if line_stripped.lower().startswith('hostname '):
                    current_host['hostname'] = line_stripped[9:].strip()
                elif line_stripped.lower().startswith('port '):
                    current_host['port'] = line_stripped[5:].strip()
                elif line_stripped.lower().startswith('user '):
                    current_host['user'] = line_stripped[5:].strip()
                elif line_stripped.lower().startswith('identityfile '):
                    current_host['identityfile'] = line_stripped[13:].strip()
                elif line_stripped.lower().startswith('identityagent none'):
                    current_host['identityagent'] = True
                elif line_stripped.lower().startswith('identitiesonly '):
                    current_host['identitiesonly'] = line_stripped[15:].strip()
                elif line_stripped.lower().startswith('proxycommand '):
                    current_host['proxycommand'] = line_stripped[13:].strip()
                    current_host['proxycommand_enabled'] = True
            elif current_host and not line_stripped:
                # Empty line - add to raw lines but don't parse
                current_raw_lines.append(line)
        
        # Add last host
        if current_host:
            current_host['raw_lines'] = current_raw_lines
            hosts.append(current_host)
            if self.main_window.debug:
                print(f"ConfigTab: Added final host: {current_host['host']}")
        
        if self.main_window.debug:
            print(f"ConfigTab: Parsing complete, found {len(hosts)} hosts")
        
        return hosts

    def _update_ssh_hosts_display(self, hosts):
        """Update the SSH hosts display with parsed hosts"""
        if self.main_window.debug:
            print(f"ConfigTab: Updating SSH hosts display with {len(hosts)} hosts")
        
        # Clear existing hosts
        for child in self.ssh_hosts_flowbox.get_children():
            self.ssh_hosts_flowbox.remove(child)
        
        if not hosts:
            if self.main_window.debug:
                print(f"ConfigTab: No hosts to display")
            self.ssh_loading_label.set_text("No SSH hosts configured")
            return
        
        self.ssh_loading_label.set_text(f"Found {len(hosts)} SSH host(s)")
        
        if self.main_window.debug:
            print(f"ConfigTab: Creating cards for {len(hosts)} hosts")
        
        # Create host cards
        for host in hosts:
            if self.main_window.debug:
                print(f"ConfigTab: Creating card for host: {host['host']}")
            card = self._create_ssh_host_card(host)
            self.ssh_hosts_flowbox.add(card)
        
        self.ssh_hosts_flowbox.show_all()
        
        if self.main_window.debug:
            print(f"ConfigTab: SSH hosts display updated successfully")

    def _create_ssh_host_card(self, host):
        """Create a card widget for an SSH host"""
        # Main card container with better styling
        card = Gtk.Frame()
        card.set_margin_start(2)  # Reduced from 4
        card.set_margin_end(2)    # Reduced from 4
        card.set_margin_top(2)    # Reduced from 4
        card.set_margin_bottom(2) # Reduced from 4
        
        # Apply CSS class for better styling
        style_context = card.get_style_context()
        style_context.add_class("ssh-host-card")
        
        # Card content
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)  # Reduced from 6
        card_box.set_margin_start(8)   # Reduced from 12
        card_box.set_margin_end(8)     # Reduced from 12
        card_box.set_margin_top(8)     # Reduced from 12
        card_box.set_margin_bottom(8)  # Reduced from 12
        
        # Host name header with file icon
        host_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)  # Reduced from 8
        
        # File icon (using unicode symbol)
        file_icon = Gtk.Label(label="📄")
        file_icon.set_margin_end(4)
        host_header.pack_start(file_icon, False, False, 0)
        
        # Host name
        host_name_label = Gtk.Label(label=f"<b>{host['host']}</b>")
        host_name_label.set_use_markup(True)
        host_name_label.set_xalign(0)
        host_name_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        host_name_label.set_max_width_chars(20)
        host_header.pack_start(host_name_label, True, True, 0)
        
        # Three-dots menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_relief(Gtk.ReliefStyle.NONE)
        menu_button.set_focus_on_click(False)
        
        # Create three-dots icon
        dots_label = Gtk.Label(label="⋮")
        dots_label.set_margin_start(4)
        dots_label.set_margin_end(4)
        menu_button.add(dots_label)
        
        # Create popup menu
        menu = Gtk.Menu()
        
        # Edit menu item
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.connect("activate", self.on_edit_ssh_host, host)
        menu.append(edit_item)
        
        # Separator
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Delete menu item
        delete_item = Gtk.MenuItem(label="Delete")
        delete_item.connect("activate", self.on_delete_ssh_host, host)
        menu.append(delete_item)
        
        menu.show_all()
        menu_button.set_popup(menu)
        
        host_header.pack_start(menu_button, False, False, 0)
        
        card_box.pack_start(host_header, False, False, 0)
        
        # Host details - only show hostname for compactness
        if host['hostname']:
            hostname_label = Gtk.Label(label=host['hostname'])
            hostname_label.set_xalign(0)
            hostname_label.set_line_wrap(True)
            hostname_label.set_max_width_chars(25)  # Limit width
            hostname_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
            card_box.pack_start(hostname_label, False, False, 0)
        
        card.add(card_box)
        
        return card

    def on_edit_ssh_host(self, button, host):
        """Handle editing an SSH host"""
        self._show_ssh_host_dialog(host, is_edit=True)

    def on_delete_ssh_host(self, button, host):
        """Handle deleting an SSH host"""
        dialog = Gtk.MessageDialog(
            transient_for=self.main_window.window,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Delete SSH Host",
            secondary_text=f"Are you sure you want to delete the SSH host '{host['host']}'?"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            self._delete_ssh_host(host)

    def _show_ssh_host_dialog(self, host=None, is_edit=False):
        """Show dialog for adding/editing SSH host"""
        dialog = Gtk.Dialog(
            title="Edit SSH Host" if is_edit else "Add SSH Host",
            transient_for=self.main_window.window,
            modal=True,
            destroy_with_parent=True
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.OK)
        
        # Add content
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_start(20)
        content_area.set_margin_end(20)
        content_area.set_margin_top(20)
        content_area.set_margin_bottom(20)
        
        # Form fields
        host_entry = Gtk.Entry()
        host_entry.set_placeholder_text("e.g., myserver, git-server")
        if host:
            host_entry.set_text(host['host'])
        
        hostname_entry = Gtk.Entry()
        hostname_entry.set_placeholder_text("IP address or DNS name")
        if host:
            hostname_entry.set_text(host['hostname'])
        
        port_entry = Gtk.Entry()
        port_entry.set_text(host['port'] if host else "22")
        
        user_entry = Gtk.Entry()
        user_entry.set_text(host['user'] if host else self._get_config_value("user", getpass.getuser()))
        
        identity_entry = Gtk.Entry()
        identity_entry.set_text(host['identityfile'] if host else "~/.ssh/id_ed25519")
        
        identity_agent_check = Gtk.CheckButton(label="IdentityAgent none")
        if host:
            identity_agent_check.set_active(host['identityagent'])
        
        identities_combo = Gtk.ComboBoxText()
        identities_combo.append_text("no")
        identities_combo.append_text("yes")
        identities_combo.set_active(0 if not host or host['identitiesonly'] == 'no' else 1)
        
        proxy_check = Gtk.CheckButton()
        proxy_entry = Gtk.Entry()
        proxy_entry.set_text(host['proxycommand'] if host else "ssh -q -W %h:%p gateway-name")
        if host:
            proxy_check.set_active(host['proxycommand_enabled'])
        
        # Layout form
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Host field
        host_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        host_label = Gtk.Label(label="Host:")
        host_label.set_xalign(0)
        host_label.set_size_request(120, -1)
        host_row.pack_start(host_label, False, False, 0)
        host_row.pack_start(host_entry, True, True, 0)
        form_box.pack_start(host_row, False, False, 0)
        
        # Hostname field
        hostname_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hostname_label = Gtk.Label(label="Hostname:")
        hostname_label.set_xalign(0)
        hostname_label.set_size_request(120, -1)
        hostname_row.pack_start(hostname_label, False, False, 0)
        hostname_row.pack_start(hostname_entry, True, True, 0)
        form_box.pack_start(hostname_row, False, False, 0)
        
        # Port field
        port_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        port_label = Gtk.Label(label="Port:")
        port_label.set_xalign(0)
        port_label.set_size_request(120, -1)
        port_row.pack_start(port_label, False, False, 0)
        port_row.pack_start(port_entry, True, True, 0)
        form_box.pack_start(port_row, False, False, 0)
        
        # User field
        user_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        user_label = Gtk.Label(label="User:")
        user_label.set_xalign(0)
        user_label.set_size_request(120, -1)
        user_row.pack_start(user_label, False, False, 0)
        user_row.pack_start(user_entry, True, True, 0)
        form_box.pack_start(user_row, False, False, 0)
        
        # IdentityFile field
        identity_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        identity_label = Gtk.Label(label="IdentityFile:")
        identity_label.set_xalign(0)
        identity_label.set_size_request(120, -1)
        identity_row.pack_start(identity_label, False, False, 0)
        identity_row.pack_start(identity_entry, True, True, 0)
        form_box.pack_start(identity_row, False, False, 0)
        
        # Options row
        options_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        options_row.pack_start(identity_agent_check, False, False, 0)
        
        identities_label = Gtk.Label(label="IdentitiesOnly:")
        options_row.pack_start(identities_label, False, False, 0)
        options_row.pack_start(identities_combo, False, False, 0)
        form_box.pack_start(options_row, False, False, 0)
        
        # ProxyCommand field
        proxy_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        proxy_label = Gtk.Label(label="ProxyCommand:")
        proxy_label.set_xalign(0)
        proxy_label.set_size_request(120, -1)
        proxy_row.pack_start(proxy_label, False, False, 0)
        proxy_row.pack_start(proxy_check, False, False, 0)
        proxy_row.pack_start(proxy_entry, True, True, 0)
        form_box.pack_start(proxy_row, False, False, 0)
        
        content_area.pack_start(form_box, False, False, 0)
        dialog.show_all()
        
        def on_dialog_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                # Get values
                new_host = {
                    'host': host_entry.get_text().strip(),
                    'hostname': hostname_entry.get_text().strip(),
                    'port': port_entry.get_text().strip(),
                    'user': user_entry.get_text().strip(),
                    'identityfile': identity_entry.get_text().strip(),
                    'identityagent': identity_agent_check.get_active(),
                    'identitiesonly': identities_combo.get_active_text(),
                    'proxycommand': proxy_entry.get_text().strip(),
                    'proxycommand_enabled': proxy_check.get_active()
                }
                
                if is_edit:
                    self._update_ssh_host(host, new_host)
                else:
                    self._add_ssh_host_from_dialog(new_host)
            
            dialog.destroy()
        
        dialog.connect("response", on_dialog_response)

    def _add_ssh_host_from_dialog(self, host_data):
        """Add SSH host from dialog"""
        # Validate required fields
        if not host_data['host'] or not host_data['hostname']:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Missing Required Fields",
                secondary_text="Host and Hostname are required fields."
            )
            dialog.run()
            dialog.destroy()
            return
        
        # Build SSH config entry
        config_entry = self._build_ssh_config_entry(host_data)
        
        # Write to SSH config file
        self._write_ssh_config_entry(config_entry)
        
        # Refresh the display
        self._load_ssh_hosts_async()

    def _update_ssh_host(self, old_host, new_host):
        """Update existing SSH host"""
        # Validate required fields
        if not new_host['host'] or not new_host['hostname']:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Missing Required Fields",
                secondary_text="Host and Hostname are required fields."
            )
            dialog.run()
            dialog.destroy()
            return
        
        # Read current SSH config
        user_home = self._get_config_value("user_home", os.path.expanduser("~"))
        ssh_config_path = os.path.join(user_home, ".ssh", "config")
        
        if not os.path.exists(ssh_config_path):
            return
        
        try:
            with open(ssh_config_path, 'r') as f:
                content = f.read()
            
            # Parse and find the host to replace
            hosts = self._parse_ssh_config(content)
            
            # Find and replace the old host
            new_content = content
            for host in hosts:
                if host['host'] == old_host['host']:
                    # Build new config entry
                    new_config_entry = self._build_ssh_config_entry(new_host)
                    
                    # Replace the old host block with new one
                    old_block = '\n'.join(host['raw_lines'])
                    new_content = new_content.replace(old_block, new_config_entry)
                    break
            
            # Write updated config
            with open(ssh_config_path, 'w') as f:
                f.write(new_content)
            
            # Refresh the display
            self._load_ssh_hosts_async()
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Updating SSH Host",
                secondary_text=f"Failed to update SSH host: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _delete_ssh_host(self, host):
        """Delete SSH host from config"""
        user_home = self._get_config_value("user_home", os.path.expanduser("~"))
        ssh_config_path = os.path.join(user_home, ".ssh", "config")
        
        if not os.path.exists(ssh_config_path):
            return
        
        try:
            with open(ssh_config_path, 'r') as f:
                content = f.read()
            
            # Parse and find the host to delete
            hosts = self._parse_ssh_config(content)
            
            # Find and remove the host
            new_content = content
            for h in hosts:
                if h['host'] == host['host']:
                    # Get the exact block to remove (including the blank line after)
                    old_block = '\n'.join(h['raw_lines'])
                    
                    # Try to find and remove the block with trailing newline
                    if old_block + '\n' in new_content:
                        new_content = new_content.replace(old_block + '\n', '')
                    elif old_block in new_content:
                        new_content = new_content.replace(old_block, '')
                    
                    # Clean up any double newlines that might be left
                    new_content = '\n'.join(line for line in new_content.split('\n') if line.strip() or line == '')
                    
                    # Ensure we end with a single newline
                    if new_content and not new_content.endswith('\n'):
                        new_content += '\n'
                    
                    break
            
            # Write updated config
            with open(ssh_config_path, 'w') as f:
                f.write(new_content)
            
            # Refresh the display
            self._load_ssh_hosts_async()
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Deleting SSH Host",
                secondary_text=f"Failed to delete SSH host: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _build_ssh_config_entry(self, host_data):
        """Build SSH config entry from host data"""
        config_entry = f"Host {host_data['host']}\n"
        config_entry += f"    Hostname {host_data['hostname']}\n"
        
        if host_data['port'] and host_data['port'] != "22":
            config_entry += f"    Port {host_data['port']}\n"
        
        if host_data['user']:
            config_entry += f"    User {host_data['user']}\n"
        
        if host_data['identityfile']:
            config_entry += f"    IdentityFile {host_data['identityfile']}\n"
        
        if host_data['identityagent']:
            config_entry += "    IdentityAgent none\n"
        
        if host_data['identitiesonly'] == "yes":
            config_entry += "    IdentitiesOnly yes\n"
        
        if host_data['proxycommand_enabled'] and host_data['proxycommand']:
            config_entry += f"    ProxyCommand {host_data['proxycommand']}\n"
        
        config_entry += "\n"
        return config_entry

    def _write_ssh_config_entry(self, config_entry):
        """Write SSH config entry to file"""
        user_home = self._get_config_value("user_home", os.path.expanduser("~"))
        ssh_dir = os.path.join(user_home, ".ssh")
        ssh_config_path = os.path.join(ssh_dir, "config")
        
        # Create .ssh directory if it doesn't exist
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, mode=0o700)
        
        # Read current SSH config content
        current_config = ""
        if os.path.exists(ssh_config_path):
            try:
                with open(ssh_config_path, 'r') as f:
                    current_config = f.read()
            except Exception as e:
                dialog = Gtk.MessageDialog(
                    transient_for=self.main_window.window,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error Reading SSH Config",
                    secondary_text=f"Failed to read existing SSH config: {e}"
                )
                dialog.run()
                dialog.destroy()
                return
        
        # Append new entry
        new_config = current_config + config_entry
        
        # Write the updated config
        try:
            with open(ssh_config_path, 'w') as f:
                f.write(new_config)
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Writing SSH Config",
                secondary_text=f"Failed to write SSH config: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _show_ssh_error(self, error_message):
        """Show SSH error message"""
        self.ssh_loading_label.set_text(f"Error: {error_message}")

    def _refresh_ssh_tab(self):
        """Refresh the SSH tab to show updated key status"""
        if self.main_window.debug:
            print("ConfigTab: Refreshing SSH tab using stored references")
        
        # Use stored references for direct refresh
        if self.ssh_key_frame and self.ssh_key_box:
            self._rebuild_ssh_key_section(self.ssh_key_frame)
        else:
            if self.main_window.debug:
                print("ConfigTab: Stored references not available, falling back to config reload")
            self._reload_main_config()
    
    def _rebuild_ssh_key_section(self, ssh_key_frame):
        """Rebuild the SSH key section with current keys"""
        if self.main_window.debug:
            print("ConfigTab: Rebuilding SSH key section")
        
        # Clear existing content
        for child in ssh_key_frame.get_children():
            ssh_key_frame.remove(child)
        
        # Rebuild the content
        ssh_key_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        ssh_key_box.set_margin_start(8)
        ssh_key_box.set_margin_end(8)
        ssh_key_box.set_margin_top(8)
        ssh_key_box.set_margin_bottom(8)
        
        # Check for existing SSH keys
        user_home = self._get_config_value("user_home", os.path.expanduser("~"))
        ssh_dir = os.path.join(user_home, ".ssh")
        existing_keys = []
        if os.path.exists(ssh_dir):
            for file in os.listdir(ssh_dir):
                if file.endswith(('.pub', '_rsa', '_ed25519', '_ecdsa')):
                    existing_keys.append(file)
        
        if self.main_window.debug:
            print(f"ConfigTab: Found {len(existing_keys)} SSH keys: {existing_keys}")
        
        if existing_keys:
            # Show existing keys as cards
            keys_scrolled = Gtk.ScrolledWindow()
            keys_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            keys_scrolled.set_size_request(-1, 150)
            
            keys_flowbox = Gtk.FlowBox()
            keys_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
            keys_flowbox.set_min_children_per_line(2)
            keys_flowbox.set_homogeneous(False)
            keys_flowbox.set_row_spacing(4)
            keys_flowbox.set_column_spacing(4)
            
            for key_file in existing_keys:
                if key_file.endswith('.pub'):
                    # Create card for public key
                    card = self._create_ssh_key_card(key_file, ssh_dir)
                    keys_flowbox.add(card)
                    if self.main_window.debug:
                        print(f"ConfigTab: Added card for {key_file}")
            
            keys_scrolled.add(keys_flowbox)
            ssh_key_box.pack_start(keys_scrolled, True, True, 0)
            
            bitwarden_info = Gtk.Label(label="💡 Tip: You can store your SSH keys securely in Bitwarden app")
            bitwarden_info.set_line_wrap(True)
            ssh_key_box.pack_start(bitwarden_info, False, False, 0)
        else:
            # No keys found - show create button
            create_key_button = Gtk.Button(label="Create SSH Key")
            create_key_button.connect("clicked", self.on_create_ssh_key_clicked)
            ssh_key_box.pack_start(create_key_button, False, False, 0)
            if self.main_window.debug:
                print("ConfigTab: No keys found, showing create button")
        
        ssh_key_frame.add(ssh_key_box)
        ssh_key_frame.show_all()
        
        if self.main_window.debug:
            print("ConfigTab: SSH key section rebuild complete") 

    def _create_ssh_key_card(self, key_file, ssh_dir):
        """Create a card widget for an SSH key"""
        card = Gtk.Frame()
        card.set_margin_start(4)
        card.set_margin_end(4)
        card.set_margin_top(4)
        card.set_margin_bottom(4)
        
        # Apply CSS styling
        style_context = card.get_style_context()
        style_context.add_class("ssh-host-card")
        
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card_box.set_margin_start(8)
        card_box.set_margin_end(8)
        card_box.set_margin_top(8)
        card_box.set_margin_bottom(8)
        
        # Header with icon and filename
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon_label = Gtk.Label(label="🔑")
        filename_label = Gtk.Label(label=key_file)
        filename_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        filename_label.set_max_width_chars(15)
        
        header_box.pack_start(icon_label, False, False, 0)
        header_box.pack_start(filename_label, True, True, 0)
        
        # Three-dots menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_label("⋯")
        menu_button.set_relief(Gtk.ReliefStyle.NONE)
        
        # Create menu
        menu = Gtk.Menu()
        
        # Copy public key item
        copy_item = Gtk.MenuItem(label="Copy Public Key")
        copy_item.connect("activate", self._copy_ssh_public_key, key_file, ssh_dir)
        menu.append(copy_item)
        
        # Show public key item
        show_item = Gtk.MenuItem(label="Show Public Key")
        show_item.connect("activate", self._show_ssh_public_key, key_file, ssh_dir)
        menu.append(show_item)
        
        # Separator
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Delete key item
        delete_item = Gtk.MenuItem(label="Delete SSH Key")
        delete_item.connect("activate", self._delete_ssh_key, key_file, ssh_dir)
        menu.append(delete_item)
        
        menu.show_all()
        menu_button.set_popup(menu)
        
        header_box.pack_start(menu_button, False, False, 0)
        card_box.pack_start(header_box, False, False, 0)
        
        # Key type indicator
        key_type = "ed25519" if "ed25519" in key_file else "RSA" if "rsa" in key_file else "ECDSA" if "ecdsa" in key_file else "Unknown"
        type_label = Gtk.Label(label=f"Type: {key_type}")
        type_label.set_halign(Gtk.Align.START)
        card_box.pack_start(type_label, False, False, 0)
        
        card.add(card_box)
        return card
    
    def _copy_ssh_public_key(self, menu_item, key_file, ssh_dir):
        """Copy SSH public key to clipboard"""
        try:
            key_path = os.path.join(ssh_dir, key_file)
            with open(key_path, 'r') as f:
                public_key = f.read().strip()
            
            # Get clipboard
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(public_key, -1)
            clipboard.store()
            
            # Show success message
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Public Key Copied",
                secondary_text=f"Public key from {key_file} has been copied to clipboard."
            )
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Copying Key",
                secondary_text=f"Failed to copy public key: {e}"
            )
            dialog.run()
            dialog.destroy()
    
    def _show_ssh_public_key(self, menu_item, key_file, ssh_dir):
        """Show SSH public key in a dialog"""
        try:
            key_path = os.path.join(ssh_dir, key_file)
            with open(key_path, 'r') as f:
                public_key = f.read().strip()
            
            # Create dialog
            dialog = Gtk.Dialog(
                title=f"Public Key: {key_file}",
                transient_for=self.main_window.window,
                modal=True,
                destroy_with_parent=True
            )
            dialog.add_button("Close", Gtk.ResponseType.CLOSE)
            dialog.add_button("Copy", Gtk.ResponseType.OK)
            
            # Add content
            content_area = dialog.get_content_area()
            content_area.set_spacing(10)
            content_area.set_margin_start(20)
            content_area.set_margin_end(20)
            content_area.set_margin_top(20)
            content_area.set_margin_bottom(20)
            
            # Key content
            key_text = Gtk.TextView()
            key_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            key_text.set_size_request(400, 100)
            key_buffer = key_text.get_buffer()
            key_buffer.set_text(public_key)
            
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled_window.add(key_text)
            content_area.pack_start(scrolled_window, True, True, 0)
            
            dialog.show_all()
            
            def on_dialog_response(dialog, response_id):
                if response_id == Gtk.ResponseType.OK:
                    # Copy to clipboard
                    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                    clipboard.set_text(public_key, -1)
                    clipboard.store()
                    
                    # Show success message
                    success_dialog = Gtk.MessageDialog(
                        transient_for=self.main_window.window,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text="Public Key Copied",
                        secondary_text="Public key has been copied to clipboard."
                    )
                    success_dialog.run()
                    success_dialog.destroy()
                
                dialog.destroy()
            
            dialog.connect("response", on_dialog_response)
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Reading Key",
                secondary_text=f"Failed to read public key: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)
            clipboard.store()
            
            # Show brief success message
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Path Copied",
                secondary_text="Path has been copied to clipboard."
            )
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Copying",
                secondary_text=f"Failed to copy to clipboard: {e}"
            )
            dialog.run()
            dialog.destroy()
    
    def _open_ssh_folder(self, ssh_dir):
        """Open SSH folder in file manager"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Linux":
                # Try different file managers on Linux
                file_managers = ["xdg-open", "nautilus", "dolphin", "thunar", "pcmanfm"]
                for fm in file_managers:
                    try:
                        subprocess.run([fm, ssh_dir], check=True)
                        return
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                # Fallback to xdg-open
                subprocess.run(["xdg-open", ssh_dir])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", ssh_dir])
            elif system == "Windows":
                subprocess.run(["explorer", ssh_dir])
            else:
                # Generic fallback
                subprocess.run(["xdg-open", ssh_dir])
                
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Opening Folder",
                secondary_text=f"Failed to open SSH folder: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _delete_ssh_key(self, menu_item, key_file, ssh_dir):
        """Delete SSH key with confirmation"""
        try:
            # Get the private key filename (remove .pub extension)
            private_key_file = key_file.replace('.pub', '')
            private_key_path = os.path.join(ssh_dir, private_key_file)
            public_key_path = os.path.join(ssh_dir, key_file)
            
            # Create comprehensive confirmation dialog
            dialog = Gtk.Dialog(
                title="Delete SSH Key",
                transient_for=self.main_window.window,
                modal=True,
                destroy_with_parent=True
            )
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Delete Key", Gtk.ResponseType.OK)
            
            # Style the delete button as destructive
            delete_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            if delete_button:
                delete_button.get_style_context().add_class("destructive")
            
            # Add content
            content_area = dialog.get_content_area()
            content_area.set_spacing(10)
            content_area.set_margin_start(20)
            content_area.set_margin_end(20)
            content_area.set_margin_top(20)
            content_area.set_margin_bottom(20)
            
            # Warning icon and title
            warning_label = Gtk.Label(label="⚠️  WARNING: This action cannot be undone!")
            warning_label.set_markup('<span size="large" weight="bold" color="red">⚠️  WARNING: This action cannot be undone!</span>')
            content_area.pack_start(warning_label, False, False, 0)
            
            # Key information
            key_info_label = Gtk.Label(label=f"You are about to delete the SSH key: {key_file}")
            key_info_label.set_markup(f'<span weight="bold">You are about to delete the SSH key: {key_file}</span>')
            content_area.pack_start(key_info_label, False, False, 0)
            
            # Files to be deleted
            files_label = Gtk.Label(label="The following files will be permanently deleted:")
            files_label.set_halign(Gtk.Align.START)
            content_area.pack_start(files_label, False, False, 0)
            
            files_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            files_box.set_margin_start(10)
            
            if os.path.exists(private_key_path):
                private_label = Gtk.Label(label=f"• {private_key_file} (private key)")
                private_label.set_halign(Gtk.Align.START)
                files_box.pack_start(private_label, False, False, 0)
            
            public_label = Gtk.Label(label=f"• {key_file} (public key)")
            public_label.set_halign(Gtk.Align.START)
            files_box.pack_start(public_label, False, False, 0)
            
            content_area.pack_start(files_box, False, False, 0)
            
            # Backup reminder
            backup_label = Gtk.Label(label="")
            backup_label.set_markup('<span color="orange" weight="bold">⚠️  IMPORTANT: Make sure you have a backup of this key before proceeding!</span>')
            backup_label.set_line_wrap(True)
            content_area.pack_start(backup_label, False, False, 0)
            
            # Confirmation checkbox
            confirm_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            confirm_check = Gtk.CheckButton(label="I have made a backup of this SSH key and understand this action cannot be undone")
            confirm_check.set_active(False)
            confirm_box.pack_start(confirm_check, False, False, 0)
            content_area.pack_start(confirm_box, False, False, 0)
            
            dialog.show_all()
            
            # Disable delete button until checkbox is checked
            delete_button.set_sensitive(False)
            
            def on_checkbox_toggled(checkbox):
                delete_button.set_sensitive(checkbox.get_active())
            
            confirm_check.connect("toggled", on_checkbox_toggled)
            
            def on_dialog_response(dialog, response_id):
                if response_id == Gtk.ResponseType.OK:
                    if not confirm_check.get_active():
                        # Show error if checkbox not checked
                        error_dialog = Gtk.MessageDialog(
                            transient_for=self.main_window.window,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text="Backup Confirmation Required",
                            secondary_text="You must confirm that you have made a backup before deleting the SSH key."
                        )
                        error_dialog.run()
                        error_dialog.destroy()
                        return
                    
                    # Proceed with deletion
                    try:
                        deleted_files = []
                        
                        # Delete private key
                        if os.path.exists(private_key_path):
                            os.remove(private_key_path)
                            deleted_files.append(private_key_file)
                        
                        # Delete public key
                        if os.path.exists(public_key_path):
                            os.remove(public_key_path)
                            deleted_files.append(key_file)
                        
                        # Refresh the SSH tab to update the display
                        if self.main_window.debug:
                            print("ConfigTab: Refreshing SSH tab after key deletion")
                        self._refresh_ssh_tab()
                        
                    except Exception as e:
                        error_dialog = Gtk.MessageDialog(
                            transient_for=self.main_window.window,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text="Error Deleting SSH Key",
                            secondary_text=f"Failed to delete SSH key: {e}"
                        )
                        error_dialog.run()
                        error_dialog.destroy()
                
                dialog.destroy()
            
            dialog.connect("response", on_dialog_response)
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error",
                secondary_text=f"An error occurred: {e}"
            )
            dialog.run()
            dialog.destroy()

    def _show_info_dialog(self, title, message):
        """Show info dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.main_window.window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.run()
        dialog.destroy()
        
    def _show_error_dialog(self, title, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.main_window.window,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.run()
        dialog.destroy()