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
        self._build_tab()

    def _build_tab(self):
        # Password protection state
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
            # ... (continue with other admin sub-tabs and controls as in gui_builder.py) ...
        # Password prompt and authentication logic would also be ported here
        # For now, just show the content (no password protection)
        show_admin_content() 