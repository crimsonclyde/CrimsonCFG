#!/usr/bin/env python3
"""
CrimsonCFG Installer Module
Handles Ansible installation and playbook execution
"""

import os
import subprocess
import threading
from typing import Dict, List
from gi.repository import GLib

class Installer:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
    def setup_ansible_environment(self):
        """Setup Ansible directory and inventory file"""
        try:
            # Create Ansible directory if it doesn't exist
            if not os.path.exists(self.main_window.ansible_folder):
                os.makedirs(self.main_window.ansible_folder, exist_ok=True)
                if self.debug:
                    print(f"Created Ansible directory: {self.main_window.ansible_folder}")
            
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
                
    def run_playbook(self, playbook: Dict) -> bool:
        """Run a single playbook"""
        try:
            # Check if inventory file exists
            if not os.path.exists(self.main_window.inventory_file):
                GLib.idle_add(self.main_window.logger.log_message, f"Error: Inventory file not found at {self.main_window.inventory_file}")
                return False
                
            # Check if playbook file exists (in original location)
            playbook_path = playbook['path']
            if not os.path.exists(playbook_path):
                GLib.idle_add(self.main_window.logger.log_message, f"Error: Playbook file not found at {playbook_path}")
                return False
                
            cmd = [
                "ansible-playbook",
                "-i", self.main_window.inventory_file,
                playbook_path,
                "--extra-vars", f"user={self.main_window.user} user_home={self.main_window.user_home} ansible_folder={self.main_window.ansible_folder}"
            ]
            
            # Add additional variables for specific playbooks
            if playbook['name'] == 'Git':
                cmd.extend(["--extra-vars", f"git_username={self.main_window.user} git_email={self.main_window.config.get('settings', {}).get('git_email', 'user@example.com')}"])
            
            env = os.environ.copy()
            if self.main_window.sudo_password:
                env["ANSIBLE_BECOME_PASS"] = self.main_window.sudo_password
            env["ANSIBLE_BECOME"] = "true"
            
            GLib.idle_add(self.main_window.logger.log_message, f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
            GLib.idle_add(self.main_window.logger.log_message, f"Playbook {playbook['name']} completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            GLib.idle_add(self.main_window.logger.log_message, f"Playbook {playbook['name']} failed with error: {e}")
            GLib.idle_add(self.main_window.logger.log_message, f"Error output: {e.stderr}")
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