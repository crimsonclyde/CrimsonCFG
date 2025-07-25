#!/usr/bin/env python3
"""
AdminTab: Encapsulates the Administration tab UI and logic for CrimsonCFG
"""
from gi.repository import Gtk
import getpass
import yaml
from pathlib import Path

class AdminTab(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_window = main_window
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_margin_start(15)
        self.set_margin_end(15)
        self._admin_authenticated = getattr(self, '_admin_authenticated', False)
        self._tab_built = False
        # Only build the tab when shown
        self.connect('show', self._on_show)

    def _on_show(self, *args):
        if not self._tab_built:
            self._build_tab()
            self._tab_built = True

    def _build_tab(self):
        def show_admin_content():
            for child in self.get_children():
                self.remove(child)
            local_config = {}
            config_dir = Path.home() / ".config/com.crimson.cfg"
            local_file = config_dir / "local.yml"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
            admin_notebook = Gtk.Notebook()
            self.pack_start(admin_notebook, True, True, 0)
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

            # --- Corporate Identity Tab ---
            ci_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            ci_box.set_margin_start(10)
            ci_box.set_margin_end(10)
            ci_box.set_margin_top(10)
            ci_box.set_margin_bottom(10)
            ci_label = Gtk.Label(label="Corporate Identity:")
            ci_box.pack_start(ci_label, False, False, 0)
            # App Title
            title_label = Gtk.Label(label="App Title:")
            title_entry = Gtk.Entry()
            title_entry.set_text(local_config.get('app_name', 'CrimsonCFG'))
            ci_box.pack_start(title_label, False, False, 0)
            ci_box.pack_start(title_entry, False, False, 0)
            # App Subtitle
            subtitle_label = Gtk.Label(label="App Subtitle:")
            subtitle_entry = Gtk.Entry()
            subtitle_entry.set_text(local_config.get('app_subtitle', 'System Configuration Manager'))
            ci_box.pack_start(subtitle_label, False, False, 0)
            ci_box.pack_start(subtitle_entry, False, False, 0)
            # App Logo
            logo_label = Gtk.Label(label="App Logo:")
            logo_chooser = Gtk.FileChooserButton(title="Select App Logo", action=Gtk.FileChooserAction.OPEN)
            logo_chooser.set_filename(local_config.get('app_logo', ''))
            ci_box.pack_start(logo_label, False, False, 0)
            ci_box.pack_start(logo_chooser, False, False, 0)
            # Save Button
            save_btn = Gtk.Button(label="Save Corporate Identity")
            def on_save_ci(btn):
                local_config['app_name'] = title_entry.get_text()
                local_config['app_subtitle'] = subtitle_entry.get_text()
                local_config['app_logo'] = logo_chooser.get_filename() or ''
                with open(local_file, 'w') as f:
                    yaml.safe_dump(local_config, f)
            save_btn.connect("clicked", on_save_ci)
            ci_box.pack_start(save_btn, False, False, 0)
            admin_notebook.append_page(ci_box, Gtk.Label(label="Corporate Identity"))
            self.show_all()

        def show_password_prompt():
            for child in self.get_children():
                self.remove(child)
            prompt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            prompt_box.set_margin_top(40)
            prompt_box.set_margin_bottom(40)
            prompt_box.set_margin_start(40)
            prompt_box.set_margin_end(40)
            label = Gtk.Label(label="Enter admin password:")
            prompt_box.pack_start(label, False, False, 0)
            entry = Gtk.Entry()
            entry.set_visibility(False)
            prompt_box.pack_start(entry, False, False, 0)
            status_label = Gtk.Label(label="")
            prompt_box.pack_start(status_label, False, False, 0)
            btn = Gtk.Button(label="Unlock")
            def on_unlock(_btn=None):
                config_dir = Path.home() / ".config/com.crimson.cfg"
                local_file = config_dir / "local.yml"
                admin_password = None
                if local_file.exists():
                    with open(local_file, 'r') as f:
                        local_config = yaml.safe_load(f) or {}
                        admin_password = local_config.get('admin_password', None)
                if entry.get_text() == (admin_password or ""):
                    self._admin_authenticated = True
                    show_admin_content()
                else:
                    status_label.set_text("Incorrect password.")
            btn.connect("clicked", on_unlock)
            entry.connect("activate", on_unlock)
            prompt_box.pack_start(btn, False, False, 0)
            self.pack_start(prompt_box, True, True, 0)
            self.show_all()

        if not self._admin_authenticated:
            show_password_prompt()
        else:
            show_admin_content() 