#!/usr/bin/env python3
"""
CrimsonCFG Installer Module
Handles Ansible installation and playbook execution
"""

import os
import subprocess
import threading
from typing import Dict, List
from gi.repository import GLib  # type: ignore
import json
from pathlib import Path
from datetime import datetime

class Installer:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
    def setup_ansible_environment(self):
        """Setup Ansible directory and inventory file"""
        try:
            # Create Ansible directory if it doesn't exist
            if not os.path.exists(self.main_window.working_directory):
                os.makedirs(self.main_window.working_directory, exist_ok=True)
                if self.debug:
                    print(f"Created Working Directory: {self.main_window.working_directory}")
            
            # Create inventory file if it doesn't exist
            if not os.path.exists(self.main_window.inventory_file):
                inventory_content = f"""[all]
localhost ansible_connection=local ansible_user={self.main_window.user}

[local]
localhost
"""
                with open(self.main_window.inventory_file, 'w') as f:
                    f.write(inventory_content)
                if self.debug:
                    print(f"Created inventory file: {self.main_window.inventory_file}")
                    
        except Exception as e:
            if self.debug:
                print(f"Error setting up Ansible environment: {e}")
                
    def install_ansible(self) -> bool:
        """Install Ansible if not present"""
        try:
            result = subprocess.run(["ansible", "--version"], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(["sudo", "-S", "apt-get", "update"], 
                             input=f"{self.main_window.sudo_password}\n".encode(), check=True)
                subprocess.run(["sudo", "-S", "apt-get", "install", "-y", "ansible"], 
                             input=f"{self.main_window.sudo_password}\n".encode(), check=True)
                return True
            except subprocess.CalledProcessError:
                return False
                
    def _mark_playbook_installed(self, playbook_name: str):
        """Mark a playbook as installed in installed_playbooks.json with a timestamp."""
        config_dir = Path.home() / ".config/com.crimson.cfg"
        state_file = config_dir / "installed_playbooks.json"
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        try:
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
            else:
                state = {}
        except Exception:
            state = {}
        state[playbook_name] = datetime.now().isoformat()
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def run_playbook(self, playbook: Dict) -> bool:
        """Run a single playbook"""
        try:
            # Check if inventory file exists
            if not os.path.exists(self.main_window.inventory_file):
                GLib.idle_add(self.main_window.logger.log_message, f"Error: Inventory file not found at {self.main_window.inventory_file}")
                return False
                
            # Check if playbook file exists (determine path based on source)
            playbook_path = playbook['path']
            source = playbook.get('source', 'Built-in')
            
            # Determine the correct playbook path based on source
            if not os.path.isabs(playbook_path):
                # Remove leading 'playbooks/' if present
                if playbook_path.startswith('playbooks/'):
                    playbook_path = playbook_path[len('playbooks/'):]
                
                if source == 'External':
                    # External playbooks are in external_src/playbooks
                    playbook_path = os.path.join(self.main_window.working_directory, 'external_src', 'playbooks', playbook_path)
                else:
                    # Built-in playbooks are in playbooks
                    playbook_path = os.path.join(self.main_window.working_directory, 'playbooks', playbook_path)
            
            # Expand Jinja2 variables if present
            if "{{ working_directory }}" in playbook_path:
                playbook_path = playbook_path.replace("{{ working_directory }}", self.main_window.working_directory)
            
            if not os.path.exists(playbook_path):
                GLib.idle_add(self.main_window.logger.log_message, f"Error: Playbook file not found at {playbook_path}")
                GLib.idle_add(self.main_window.logger.log_message, f"Source: {source}")
                return False
                
            # Set templates directory based on playbook source
            if source == 'External':
                templates_directory = os.path.join(self.main_window.working_directory, 'external_src', 'templates')
            else:
                templates_directory = os.path.join(self.main_window.working_directory, 'templates')
            
            cmd = [
                "ansible-playbook",
                "-b",  # Add become for privilege escalation
                "-i", self.main_window.inventory_file,
                "-e", f"templates_directory={templates_directory}",
                playbook_path
            ]
            
            GLib.idle_add(self.main_window.logger.log_message, f"Running command: {' '.join(cmd)}")
            
            # Determine the project root (directory containing the playbook)
            playbook_dir = os.path.dirname(os.path.abspath(playbook_path))

            if self.main_window.sudo_password:
                try:
                    # Remove pexpect logic, use subprocess with ANSIBLE_BECOME_PASS
                    env = os.environ.copy()
                    env["ANSIBLE_BECOME"] = "true"
                    env["ANSIBLE_BECOME_PASS"] = self.main_window.sudo_password
                    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=playbook_dir)
                    GLib.idle_add(self.main_window.logger.log_message, f"Subprocess stdout for {playbook['name']}:\n{proc.stdout}")
                    GLib.idle_add(self.main_window.logger.log_message, f"Subprocess stderr for {playbook['name']}:\n{proc.stderr}")
                    if proc.returncode == 0:
                        GLib.idle_add(self.main_window.logger.log_message, f"Playbook {playbook['name']} completed successfully (env password)")
                        result = True
                    else:
                        GLib.idle_add(self.main_window.logger.log_message, f"Playbook {playbook['name']} failed with return code: {proc.returncode}")
                        result = False
                except Exception as e:
                    GLib.idle_add(self.main_window.logger.log_message, f"Subprocess error: {e}")
                    result = False
            else:
                # Fallback to subprocess if no sudo password is provided
                env = os.environ.copy()
                env["ANSIBLE_BECOME"] = "true"
                result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True, cwd=playbook_dir)
                GLib.idle_add(self.main_window.logger.log_message, f"Playbook {playbook['name']} completed successfully")
                result = True
            
            if result:  # Only mark as installed if successful
                self._mark_playbook_installed(playbook['name'])
            return result
            
        except subprocess.CalledProcessError as e:
            GLib.idle_add(self.main_window.logger.log_message, f"Playbook {playbook['name']} failed with error: {e}")
            GLib.idle_add(self.main_window.logger.log_message, f"Return code: {e.returncode}")
            GLib.idle_add(self.main_window.logger.log_message, f"Error output (stderr): {e.stderr}")
            GLib.idle_add(self.main_window.logger.log_message, f"Output (stdout): {e.stdout}")
            return False
            
    def run_installation(self, selected_playbooks):
        """Run the installation process"""
        try:
            GLib.idle_add(self.main_window.logger.log_message, "Starting installation process...")
            GLib.idle_add(self.main_window.status_label.set_text, "Installing Ansible...")
            GLib.idle_add(self.main_window.progress_bar.set_fraction, 0.1)
            
            # Install Ansible if needed
            if not self.install_ansible():
                GLib.idle_add(self.main_window.logger.log_message, "Failed to install Ansible")
                GLib.idle_add(self.main_window.status_label.set_text, "Failed to install Ansible")
                GLib.idle_add(self.main_window.show_error_dialog, "Failed to install Ansible")
                return
                
            GLib.idle_add(self.main_window.progress_bar.set_fraction, 0.2)
            GLib.idle_add(self.main_window.status_label.set_text, "Installing selected playbooks...")
            
            # Run each playbook
            total_playbooks = len(selected_playbooks)
            for i, playbook in enumerate(selected_playbooks):
                progress = 0.2 + (i / total_playbooks) * 0.7
                GLib.idle_add(self.main_window.progress_bar.set_fraction, progress)
                GLib.idle_add(self.main_window.status_label.set_text, f"Installing {playbook['name']}...")
                GLib.idle_add(self.main_window.logger.log_message, f"Installing {playbook['name']}...")
                
                if not self.run_playbook(playbook):
                    GLib.idle_add(self.main_window.logger.log_message, f"Failed to install {playbook['name']}")
                    GLib.idle_add(self.main_window.status_label.set_text, f"Failed to install {playbook['name']}")
                    GLib.idle_add(self.main_window.show_error_dialog, f"Failed to install {playbook['name']}")
                    return
                    
            GLib.idle_add(self.main_window.progress_bar.set_fraction, 1.0)
            GLib.idle_add(self.main_window.status_label.set_text, "Installation completed successfully!")
            GLib.idle_add(self.main_window.logger.log_message, "Installation completed successfully!")
            GLib.idle_add(self.main_window.show_success_dialog, "All selected playbooks have been installed successfully!")
            
        except Exception as e:
            GLib.idle_add(self.main_window.logger.log_message, f"Installation failed: {e}")
            GLib.idle_add(self.main_window.status_label.set_text, f"Installation failed: {e}")
            GLib.idle_add(self.main_window.show_error_dialog, f"Installation failed: {e}")
        finally:
            GLib.idle_add(self.main_window.install_btn.set_sensitive, True)
            GLib.idle_add(setattr, self.main_window, 'installation_running', False) 