#!/usr/bin/env python3
"""
AdminTab: Encapsulates the Administration tab UI and logic for CrimsonCFG
"""
from gi.repository import Gtk, GLib
import getpass
import yaml
import os
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
            repo_url_entry.set_placeholder_text("https://github.com/crimsonclyde/CrimsonCFG-Playbooks.git")
            repo_url_entry.set_tooltip_text("ℹ️ Enter the URL of your external playbook repository (e.g., https://github.com/username/repo.git)")
            external_repo_box.pack_start(repo_url_entry, False, False, 0)
            
            # Status label
            repo_status_label = Gtk.Label(label="")
            external_repo_box.pack_start(repo_status_label, False, False, 0)
            
            # Save external repo settings
            save_repo_btn = Gtk.Button(label="Save External Repository URL")
            save_repo_btn.set_tooltip_text("ℹ️ Save the repository URL and clone the external repository")
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
            
            # Refresh playbooks button
            refresh_btn = Gtk.Button(label="Refresh Playbooks")
            refresh_btn.set_tooltip_text("ℹ️ Pull latest changes from external repository and refresh playbooks from all sources")
            
            # Refresh playbooks handler
            def on_refresh_playbooks(btn):
                try:
                    repo_status_label.set_text("Refreshing playbooks from all sources...")
                    
                    # Update external repository if configured
                    from . import external_repo_manager
                    sudo_password = getattr(self.main_window, 'sudo_password', None)
                    external_repo_manager.update_external_repo_sync(sudo_password)
                    
                    # Regenerate config and update playbook list
                    self.main_window.config_manager.regenerate_gui_config()
                    self.main_window.config = self.main_window.config_manager.load_config()
                    self.main_window.update_playbook_list()
                    repo_status_label.set_text("Playbooks refreshed successfully!")
                except Exception as e:
                    repo_status_label.set_text(f"Error refreshing playbooks: {e}")
            
            refresh_btn.connect("clicked", on_refresh_playbooks)
            external_repo_box.pack_start(refresh_btn, False, False, 0)
            
            admin_notebook.append_page(external_repo_box, Gtk.Label(label="External Repository"))

            # --- Application Tab ---
            application_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            application_box.set_margin_start(15)
            application_box.set_margin_end(15)
            application_box.set_margin_top(15)
            application_box.set_margin_bottom(15)
            
            # === Working Directory Frame ===
            working_dir_frame = Gtk.Frame()
            working_dir_frame.set_label("Working Directory")
            working_dir_frame.set_label_widget(Gtk.Label(label="Working Directory"))
            
            working_dir_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
            working_dir_box.set_margin_start(15)
            working_dir_box.set_margin_end(15)
            working_dir_box.set_margin_top(15)
            working_dir_box.set_margin_bottom(15)
            
            # Working directory label and entry
            wd_label = Gtk.Label(label="Working Directory (user override, see docs):")
            wd_label.set_xalign(0)
            wd_entry = Gtk.Entry()
            wd_entry.set_text(local_config.get('working_directory', '/opt/CrimsonCFG'))
            
            # Add changed signal to save working directory instantly
            def on_wd_changed(widget):
                new_wd = widget.get_text()
                if self.main_window.debug:
                    print(f"AdminTab: Working directory changed to: '{new_wd}'")
                local_config['working_directory'] = new_wd
                yaml_ruamel = YAML()
                yaml_ruamel.preserve_quotes = True
                with open(local_file, 'w') as f:
                    yaml_ruamel.dump(local_config, f)
            wd_entry.connect("changed", on_wd_changed)
            
            working_dir_box.pack_start(wd_label, False, False, 0)
            working_dir_box.pack_start(wd_entry, False, False, 0)
            
            working_dir_frame.add(working_dir_box)
            application_box.pack_start(working_dir_frame, False, False, 0)
            
            # === Application Management Frame ===
            app_management_frame = Gtk.Frame()
            app_management_frame.set_label("Application Management")
            app_management_frame.set_label_widget(Gtk.Label(label="Application Management"))
            
            app_management_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
            app_management_box.set_margin_start(15)
            app_management_box.set_margin_end(15)
            app_management_box.set_margin_top(15)
            app_management_box.set_margin_bottom(15)
            
            # Folder and config buttons in a grid for better layout
            buttons_grid = Gtk.Grid()
            buttons_grid.set_column_spacing(10)
            buttons_grid.set_row_spacing(10)
            
            # Show Config Folder button
            show_config_btn = Gtk.Button(label="Show Config Folder")
            show_config_btn.set_tooltip_text("ℹ️ Open the configuration folder in file manager")
            def on_show_config_folder(btn):
                config_dir = Path.home() / ".config/com.crimson.cfg"
                if config_dir.exists():
                    os.system(f"xdg-open '{config_dir}'")
                else:
                    # Create directory if it doesn't exist
                    config_dir.mkdir(parents=True, exist_ok=True)
                    os.system(f"xdg-open '{config_dir}'")
            show_config_btn.connect("clicked", on_show_config_folder)
            buttons_grid.attach(show_config_btn, 0, 0, 1, 1)
            
            # Show Application Folder button
            show_app_btn = Gtk.Button(label="Show Application Folder")
            show_app_btn.set_tooltip_text("ℹ️ Open the application folder in file manager")
            def on_show_app_folder(btn):
                app_dir = "/opt/CrimsonCFG"
                if os.path.exists(app_dir):
                    os.system(f"xdg-open '{app_dir}'")
            show_app_btn.connect("clicked", on_show_app_folder)
            buttons_grid.attach(show_app_btn, 1, 0, 1, 1)
            
            # Edit local settings button
            edit_local_btn = Gtk.Button(label="Edit Local Settings")
            edit_local_btn.set_tooltip_text("ℹ️ Open local.yml configuration file in text editor")
            def on_edit_local_settings(btn):
                config_dir = Path.home() / ".config/com.crimson.cfg"
                local_file = config_dir / "local.yml"
                if local_file.exists():
                    # Try to open with default text editor
                    os.system(f"xdg-open '{local_file}'")
                else:
                    # Create the file if it doesn't exist
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(local_file, 'w') as f:
                        f.write("# Local configuration file\n")
                    os.system(f"xdg-open '{local_file}'")
            edit_local_btn.connect("clicked", on_edit_local_settings)
            buttons_grid.attach(edit_local_btn, 2, 0, 1, 1)
            
            app_management_box.pack_start(buttons_grid, False, False, 0)
            app_management_frame.add(app_management_box)
            application_box.pack_start(app_management_frame, False, False, 0)
            
            # === Update Management Frame ===
            update_frame = Gtk.Frame()
            update_frame.set_label("Update Management")
            update_frame.set_label_widget(Gtk.Label(label="Update Management"))
            
            update_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
            update_box.set_margin_start(15)
            update_box.set_margin_end(15)
            update_box.set_margin_top(15)
            update_box.set_margin_bottom(15)
            
            # Version information section
            version_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            
            # Get version information
            from . import version_manager
            version_mgr = version_manager.VersionManager()
            version_info = version_mgr.get_version_info()
            
            # Current commit label
            current_commit_label = Gtk.Label(label=f"Current Commit: {version_mgr.format_version_for_display(version_info['installed_version'])}")
            current_commit_label.set_xalign(0)
            current_commit_label.set_margin_bottom(5)
            version_info_box.pack_start(current_commit_label, False, False, 0)
            
            # Remote commit label (will be updated when checking for updates)
            remote_commit_label = Gtk.Label(label="Remote Commit: Checking...")
            remote_commit_label.set_xalign(0)
            remote_commit_label.set_margin_bottom(15)
            version_info_box.pack_start(remote_commit_label, False, False, 0)
            
            # Function to check for updates automatically
            def check_for_updates_auto():
                # Import update manager
                from . import update_manager
                
                # Get config from main window
                config = getattr(self.main_window, 'config', {})
                
                # Create update manager
                update_mgr = update_manager.UpdateManager(config, self.main_window)
                
                # Check for updates
                update_info = update_mgr.check_for_updates()
                
                if update_info.get('error'):
                    remote_commit_label.set_text("Remote Commit: Error")
                    return
                
                remote_commit = update_info.get('remote_commit', 'Unknown')
                
                # Update remote commit label
                remote_commit_label.set_text(f"Remote Commit: {remote_commit}")
            
            # Check for updates automatically after a short delay
            GLib.timeout_add_seconds(1, check_for_updates_auto)
            
            update_box.pack_start(version_info_box, False, False, 0)
            
            # Update buttons
            update_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            # Check for updates button
            check_update_btn = Gtk.Button(label="Check for Updates")
            check_update_btn.set_tooltip_text("ℹ️ Check if a newer version is available")
            
            # Update button
            update_btn = Gtk.Button(label="Update Application")
            update_btn.set_tooltip_text("ℹ️ Pull latest changes from git repository")
            
            # Git pull button (simple direct pull)
            git_pull_btn = Gtk.Button(label="Git Pull")
            git_pull_btn.set_tooltip_text("ℹ️ Simple git pull to get latest changes")
            
            # Progress bar for update
            update_progress = Gtk.ProgressBar()
            update_progress.set_visible(False)
            
            # Status label for update
            update_status_label = Gtk.Label(label="")
            update_status_label.set_visible(False)
            
            def on_update_progress(percentage, message):
                update_progress.set_fraction(percentage / 100.0)
                update_status_label.set_text(message)
                update_progress.set_visible(True)
                update_status_label.set_visible(True)
                return False
            
            def on_update_complete(success, message):
                update_status_label.set_text(message)
                update_progress.set_visible(False)
                if success:
                    update_status_label.set_text("Update completed successfully! Please restart the application.")
                return False
            
            def on_check_for_updates(btn):
                # Import update manager
                from . import update_manager
                
                # Get config from main window
                config = getattr(self.main_window, 'config', {})
                
                # Create update manager
                update_mgr = update_manager.UpdateManager(config, self.main_window)
                
                # Show checking status
                update_status_label.set_text("Checking for updates...")
                remote_version_label.set_text("Remote Version: Checking...")
                
                # Check for updates
                update_info = update_mgr.check_for_updates()
                
                if update_info.get('error'):
                    update_status_label.set_text(f"Error checking for updates: {update_info['error']}")
                    remote_commit_label.set_text("Remote Commit: Error")
                    return
                
                current_commit = update_info.get('current_commit', 'Unknown')
                remote_commit = update_info.get('remote_commit', 'Unknown')
                
                # Update remote commit label
                remote_commit_label.set_text(f"Remote Commit: {remote_commit}")
                
                if update_info.get('is_reinstall'):
                    update_status_label.set_text(f"Current commit: {current_commit}. No new changes available.")
                elif update_info.get('available'):
                    update_status_label.set_text(f"Update available: {current_commit} → {remote_commit}")
                else:
                    update_status_label.set_text(f"Current commit: {current_commit}. No updates available.")
            
            def on_update_application(btn):
                # Import update manager
                from . import update_manager
                
                # Get config from main window
                config = getattr(self.main_window, 'config', {})
                
                # Create update manager
                update_mgr = update_manager.UpdateManager(config, self.main_window)
                
                # Check for updates first
                update_info = update_mgr.check_for_updates()
                
                if update_info.get('error'):
                    update_status_label.set_text(f"Error checking for updates: {update_info['error']}")
                    return
                
                if not update_info.get('available') and not update_info.get('is_reinstall'):
                    update_status_label.set_text("No updates available. You have the latest changes.")
                    return
                
                # Prepare confirmation message
                current_commit = update_info.get('current_commit', 'Unknown')
                remote_commit = update_info.get('remote_commit', 'Unknown')
                
                if update_info.get('is_reinstall'):
                    message = f"Pull latest changes?\n\nThis will pull the latest changes from the repository. Your settings will not be affected."
                    title = "Pull Latest Changes"
                else:
                    message = f"Update from commit {current_commit} to {remote_commit}?\n\nThis will pull the latest changes from the repository. Your settings will not be affected."
                    title = "Update Application"
                
                # Show confirmation dialog
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_toplevel(),
                    flags=Gtk.DialogFlags.MODAL,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text=title,
                    secondary_text=message
                )
                
                response = dialog.run()
                dialog.destroy()
                
                if response == Gtk.ResponseType.YES:
                    # Start update process
                    update_mgr.download_update(
                        progress_callback=on_update_progress,
                        completion_callback=on_update_complete
                    )
                    
                    # Disable button during update
                    update_btn.set_sensitive(False)
                    update_btn.set_label("Updating...")
                    
                    # Re-enable button after completion
                    def re_enable_button():
                        update_btn.set_sensitive(True)
                        update_btn.set_label("Update Application")
                    
                    # Schedule re-enabling after 5 seconds
                    GLib.timeout_add_seconds(5, re_enable_button)
                else:
                    update_status_label.set_text("Update cancelled.")
            
            check_update_btn.connect("clicked", on_check_for_updates)
            update_btn.connect("clicked", on_update_application)
            
            # Simple git pull handler
            def on_git_pull(btn):
                try:
                    update_status_label.set_text("Performing git pull...")
                    update_status_label.set_visible(True)
                    
                    # Get sudo password from main window
                    sudo_password = getattr(self.main_window, 'sudo_password', None)
                    if not sudo_password:
                        update_status_label.set_text("Error: No sudo password available. Please provide sudo password in the admin tab.")
                        return
                    
                    # Run git pull with sudo
                    import subprocess
                    result = subprocess.run(
                        ["sudo", "-k", "-S", "git", "pull", "origin", "main"],
                        input=f"{sudo_password}\n",
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd="/opt/CrimsonCFG"
                    )
                    
                    if result.returncode == 0:
                        update_status_label.set_text("Git pull completed successfully!")
                        
                        # Update commit information
                        from . import version_manager
                        version_mgr = version_manager.VersionManager()
                        new_commit = version_mgr.get_installed_version()
                        if new_commit:
                            current_commit_label.set_text(f"Current Commit: {version_mgr.format_version_for_display(new_commit)}")
                    else:
                        update_status_label.set_text(f"Git pull failed: {result.stderr}")
                        
                except Exception as e:
                    update_status_label.set_text(f"Error during git pull: {str(e)}")
            
            git_pull_btn.connect("clicked", on_git_pull)
            
            update_buttons_box.pack_start(check_update_btn, True, True, 0)
            update_buttons_box.pack_start(update_btn, True, True, 0)
            update_buttons_box.pack_start(git_pull_btn, True, True, 0)
            update_box.pack_start(update_buttons_box, False, False, 0)
            
            # Progress and status
            update_box.pack_start(update_progress, False, False, 0)
            update_box.pack_start(update_status_label, False, False, 0)
            
            update_frame.add(update_box)
            application_box.pack_start(update_frame, False, False, 0)
            
            admin_notebook.append_page(application_box, Gtk.Label(label="Application"))
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