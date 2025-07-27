#!/usr/bin/env python3
"""
AdminTab: Encapsulates the Administration tab UI and logic for CrimsonCFG
"""
from gi.repository import Gtk
import getpass
import yaml
from pathlib import Path
from ruamel.yaml import YAML

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
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                with open(local_file, 'r') as f:
                    local_config = yaml_ruamel.load(f) or {}
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
            # Save APT packages button
            save_apt_btn = Gtk.Button(label="Save APT Packages")
            def on_save_apt(btn):
                apt_packages = []
                for row in apt_store:
                    if row[0].strip():  # Only add non-empty packages
                        apt_packages.append(row[0].strip())
                local_config['apt_packages'] = apt_packages
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(local_config, f)
                # Refresh playbook list to update requirement status
                if hasattr(self.main_window, 'playbook_manager'):
                    self.main_window.playbook_manager.update_playbook_list()
            save_apt_btn.connect("clicked", on_save_apt)
            default_apps_box.pack_start(save_apt_btn, False, False, 0)
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
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(local_config, f)
                # Refresh playbook list to update requirement status
                if hasattr(self.main_window, 'playbook_manager'):
                    self.main_window.playbook_manager.update_playbook_list()
            save_btn.connect("clicked", on_save_ci)
            ci_box.pack_start(save_btn, False, False, 0)
            admin_notebook.append_page(ci_box, Gtk.Label(label="Corporate Identity"))

            # --- Admin Password Tab ---
            password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            password_box.set_margin_start(10)
            password_box.set_margin_end(10)
            password_box.set_margin_top(10)
            password_box.set_margin_bottom(10)
            
            password_label = Gtk.Label(label="Admin Password Management:")
            password_box.pack_start(password_label, False, False, 0)
            
            # Current password display
            current_password_label = Gtk.Label(label="Current Admin Password:")
            password_box.pack_start(current_password_label, False, False, 0)
            
            current_password_entry = Gtk.Entry()
            current_password_entry.set_visibility(False)
            current_password_entry.set_text(local_config.get('admin_password', ''))
            current_password_entry.set_editable(False)
            current_password_entry.set_can_focus(False)
            password_box.pack_start(current_password_entry, False, False, 0)
            
            # New password section
            new_password_label = Gtk.Label(label="New Admin Password:")
            password_box.pack_start(new_password_label, False, False, 0)
            
            new_password_entry = Gtk.Entry()
            new_password_entry.set_visibility(False)
            new_password_entry.set_placeholder_text("Enter new password")
            password_box.pack_start(new_password_entry, False, False, 0)
            
            # Confirm new password
            confirm_password_label = Gtk.Label(label="Confirm New Password:")
            password_box.pack_start(confirm_password_label, False, False, 0)
            
            confirm_password_entry = Gtk.Entry()
            confirm_password_entry.set_visibility(False)
            confirm_password_entry.set_placeholder_text("Confirm new password")
            password_box.pack_start(confirm_password_entry, False, False, 0)
            
            # Status label
            password_status_label = Gtk.Label(label="")
            password_box.pack_start(password_status_label, False, False, 0)
            
            # Change password button
            change_password_btn = Gtk.Button(label="Change Admin Password")
            def on_change_password(btn):
                new_password = new_password_entry.get_text()
                confirm_password = confirm_password_entry.get_text()
                
                if not new_password:
                    password_status_label.set_text("Please enter a new password.")
                    return
                
                if new_password != confirm_password:
                    password_status_label.set_text("Passwords do not match.")
                    return
                
                if len(new_password) < 8:
                    password_status_label.set_text("Password must be at least 8 characters long.")
                    return
                
                # Update local.yml with new password
                local_config['admin_password'] = new_password
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(local_config, f)
                
                # Update the current password display
                current_password_entry.set_text(new_password)
                
                # Clear the new password fields
                new_password_entry.set_text("")
                confirm_password_entry.set_text("")
                
                password_status_label.set_text("Admin password updated successfully!")
                
            change_password_btn.connect("clicked", on_change_password)
            password_box.pack_start(change_password_btn, False, False, 0)
            
            admin_notebook.append_page(password_box, Gtk.Label(label="Admin Password"))

            # --- External Repository Tab ---
            external_repo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            external_repo_box.set_margin_start(10)
            external_repo_box.set_margin_end(10)
            external_repo_box.set_margin_top(10)
            external_repo_box.set_margin_bottom(10)
            
            external_repo_label = Gtk.Label(label="External Repository Management:")
            external_repo_box.pack_start(external_repo_label, False, False, 0)
            
            # External repository URL entry
            repo_url_label = Gtk.Label(label="Repository URL:")
            repo_url_label.set_xalign(0)
            external_repo_box.pack_start(repo_url_label, False, False, 0)
            
            repo_url_entry = Gtk.Entry()
            repo_url_entry.set_text(local_config.get('external_playbook_repo_url', ''))
            repo_url_entry.set_tooltip_text("Enter the URL of your external playbook repository (e.g., https://github.com/username/repo.git)")
            external_repo_box.pack_start(repo_url_entry, False, False, 0)
            
            # Refresh playbooks button
            refresh_btn = Gtk.Button(label="Refresh Playbooks")
            refresh_btn.set_tooltip_text("Refresh playbooks from all sources (including external repository)")
            external_repo_box.pack_start(refresh_btn, False, False, 0)
            
            # Status label
            repo_status_label = Gtk.Label(label="")
            external_repo_box.pack_start(repo_status_label, False, False, 0)
            
            # Save external repo settings
            save_repo_btn = Gtk.Button(label="Save External Repository Settings")
            def on_save_repo(btn):
                repo_url = repo_url_entry.get_text().strip()
                local_config['external_playbook_repo_url'] = repo_url
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(local_config, f)
                
                # Update external repository using authenticated sudo password
                from . import external_repo_manager
                external_repo_manager.set_external_repo_url(repo_url)
                # Use the authenticated sudo password from main window
                sudo_password = getattr(self.main_window, 'sudo_password', None)
                external_repo_manager.update_external_repo_async(sudo_password)
                
                repo_status_label.set_text("External repository settings saved successfully!")
                
            save_repo_btn.connect("clicked", on_save_repo)
            external_repo_box.pack_start(save_repo_btn, False, False, 0)
            
            # Refresh playbooks handler
            def on_refresh_playbooks(btn):
                try:
                    repo_status_label.set_text("Refreshing playbooks from all sources...")
                    self.main_window.config_manager.regenerate_gui_config()
                    self.main_window.config = self.main_window.config_manager.load_config()
                    self.main_window.update_playbook_list()
                    repo_status_label.set_text("Playbooks refreshed successfully!")
                except Exception as e:
                    repo_status_label.set_text(f"Error refreshing playbooks: {e}")
            
            refresh_btn.connect("clicked", on_refresh_playbooks)
            
            admin_notebook.append_page(external_repo_box, Gtk.Label(label="External Repository"))
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
                    yaml_ruamel = YAML()
                    yaml_ruamel.preserve_quotes = True
                    with open(local_file, 'r') as f:
                        local_config = yaml_ruamel.load(f) or {}
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