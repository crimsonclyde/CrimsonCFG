#!/usr/bin/env python3
"""
Update Manager for MDM Manager
Handles downloading and updating the application from the web URL
"""

import os
import sys
import shutil
import tempfile
import zipfile
import requests
import time
import subprocess
from pathlib import Path
from gi.repository import GLib
import threading
from .debug_manager import DebugManager

class UpdateManager:
    def __init__(self, config=None, main_window=None):
        self.config = config or {}
        self.main_window = main_window
        self.debug_manager = DebugManager(config)
        
        # Application paths
        self.app_dir = "/opt/MDM-Manager"
        # Use the actual app directory for updates (requires sudo)
        self.working_dir = self.config.get('settings', {}).get('working_directory', self.app_dir)
        self.base_url = "https://setup.atix.dev/linux/mdmm"
        
        # Get current version from version manager
        from . import version_manager
        self.version_mgr = version_manager.VersionManager(config)
        self.current_version = self.version_mgr.get_installed_version()
        
        # Available versions will be discovered dynamically
        self.latest_version = None
        self.available_versions = []
        self.extracted_name = "mdm-manager-main"
        
    def download_update(self, progress_callback=None, completion_callback=None):
        """
        Download the latest version of the application
        
        Args:
            progress_callback: Function to call with progress updates (percentage, message)
            completion_callback: Function to call when download completes (success, message)
        """
        def download_thread():
            try:
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                download_path = os.path.join(temp_dir, self.package_name)
                
                # Download URL
                download_url = f"{self.base_url}/{self.package_name}"
                
                self.debug_manager.print(f"Starting download from: {download_url}")
                if progress_callback:
                    GLib.idle_add(progress_callback, 0, "Starting download...")
                
                # Download with progress
                try:
                    # Get authentication credentials from server auth manager
                    from . import server_auth_manager
                    auth_mgr = server_auth_manager.ServerAuthManager(self.config)
                    username, password = auth_mgr.get_auth_credentials()
                    
                    if username and password:
                        response = requests.get(download_url, auth=(username, password), stream=True, timeout=30)
                    else:
                        # Fallback to unauthenticated request
                        response = requests.get(download_url, stream=True, timeout=30)
                    
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    raise Exception(f"Failed to download from {download_url}: {str(e)}")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0 and progress_callback:
                                percentage = int((downloaded / total_size) * 100)
                                GLib.idle_add(progress_callback, percentage, f"Downloading... {percentage}%")
                
                self.debug_manager.print("Download completed successfully")
                
                # Extract and update
                if progress_callback:
                    GLib.idle_add(progress_callback, 100, "Extracting update...")
                
                success = self._extract_and_update(download_path, progress_callback)
                
                # Cleanup
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                if completion_callback:
                    if success:
                        GLib.idle_add(completion_callback, True, "Update completed successfully!")
                    else:
                        GLib.idle_add(completion_callback, False, "Update failed during extraction")
                        
            except Exception as e:
                self.debug_manager.print_error(f"Download failed: {str(e)}")
                if completion_callback:
                    GLib.idle_add(completion_callback, False, f"Download failed: {str(e)}")
        
        # Start download in background thread
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
    
    def _extract_and_update(self, download_path, progress_callback=None):
        """
        Extract the downloaded package and update the application
        
        Args:
            download_path: Path to the downloaded zip file
            progress_callback: Function to call with progress updates
            
        Returns:
            bool: True if update was successful
        """
        backup_dir = None
        try:
            # Check if we have sudo access
            if not self._check_sudo_access():
                raise PermissionError(f"Cannot access {self.working_dir} with sudo. Please provide sudo password in the admin tab.")
            
            # Ensure working directory exists with sudo
            self._run_sudo_command(["mkdir", "-p", self.working_dir])
            
            # Create backup with sudo
            backup_dir = f"/tmp/mdm-manager_backup_{int(time.time())}"
            if os.path.exists(self.working_dir):
                self._run_sudo_command(["cp", "-r", self.working_dir, backup_dir])
                self.debug_manager.print(f"Created backup at: {backup_dir}")
            
            # Remove current working directory with sudo
            if os.path.exists(self.working_dir):
                self._run_sudo_command(["rm", "-rf", self.working_dir])
                self.debug_manager.print(f"Removed current working directory: {self.working_dir}")
            
            if progress_callback:
                GLib.idle_add(progress_callback, 100, "Extracting files...")
            
            # Extract the zip file to temp location first
            temp_extract_dir = f"/tmp/mdm-manager-extract-{int(time.time())}"
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            # Move extracted files to working directory with sudo
            extracted_path = os.path.join(temp_extract_dir, self.extracted_name)
            if os.path.exists(extracted_path):
                self._run_sudo_command(["mv", extracted_path, self.working_dir])
                self.debug_manager.print(f"Moved extracted directory to: {self.working_dir}")
            
            # Set proper permissions with sudo
            self._run_sudo_command(["chown", "-R", "root:root", self.working_dir])
            self._run_sudo_command(["chmod", "-R", "a+rX", self.working_dir])
            
            # Make main script executable with sudo
            main_script = os.path.join(self.working_dir, "main.py")
            if os.path.exists(main_script):
                self._run_sudo_command(["chmod", "+x", main_script])
            
            # Clean up temp directory
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
            
            # Update version.txt with new version
            version_file = Path.home() / ".config/com.mdm.manager.cfg/version.txt"
            version_file.parent.mkdir(parents=True, exist_ok=True)
            with open(version_file, 'w') as f:
                f.write(self.latest_version)
            
            self.debug_manager.print(f"Update completed successfully. Version updated to {self.latest_version}")
            return True
            
        except Exception as e:
            self.debug_manager.print_error(f"Extraction failed: {str(e)}")
            
            # Restore from backup if available
            if backup_dir and os.path.exists(backup_dir):
                try:
                    if os.path.exists(self.working_dir):
                        self._run_sudo_command(["rm", "-rf", self.working_dir])
                    self._run_sudo_command(["cp", "-r", backup_dir, self.working_dir])
                    self.debug_manager.print("Restored from backup")
                except Exception as restore_error:
                    self.debug_manager.print_error(f"Failed to restore from backup: {str(restore_error)}")
            
            return False
    
    def _check_sudo_access(self):
        """
        Check if we have sudo access using cached password
        
        Returns:
            bool: True if sudo access is available
        """
        if not self.main_window or not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
            self.debug_manager.print_warning("No sudo password available. Please provide sudo password in the admin tab.")
            return False
        
        try:
            result = subprocess.run(
                ["sudo", "-k", "-S", "test", "-w", self.working_dir],
                input=f"{self.main_window.sudo_password}\n",
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.debug_manager.print_error(f"Sudo access check failed: {str(e)}")
            return False
    
    def _run_sudo_command(self, cmd_args):
        """
        Run a command with sudo using cached password
        
        Args:
            cmd_args: List of command arguments
            
        Returns:
            bool: True if command succeeded
        """
        if not self.main_window or not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
            raise PermissionError("No sudo password available")
        
        try:
            result = subprocess.run(
                ["sudo", "-k", "-S"] + cmd_args,
                input=f"{self.main_window.sudo_password}\n",
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.debug_manager.print_error(f"Sudo command failed: {' '.join(cmd_args)}")
                self.debug_manager.print_error(f"Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            self.debug_manager.print_error(f"Sudo command exception: {str(e)}")
            return False
    
    def discover_available_versions(self):
        """
        Discover available versions by checking the server directory
        
        Returns:
            list: List of available version strings
        """
        try:
            # Get authentication credentials from server auth manager
            from . import server_auth_manager
            auth_mgr = server_auth_manager.ServerAuthManager(self.config)
            username, password = auth_mgr.get_auth_credentials()
            
            # Get directory listing from server with authentication
            if username and password:
                response = requests.get(self.base_url, auth=(username, password), timeout=10)
            else:
                # Fallback to unauthenticated request
                response = requests.get(self.base_url, timeout=10)
            
            response.raise_for_status()
            
            # Parse HTML to find zip files
            import re
            zip_pattern = r'mdm-manager-(\d+\.\d+\.\d+)\.zip'
            matches = re.findall(zip_pattern, response.text)
            
            # Convert to version objects and sort
            versions = []
            for match in matches:
                try:
                    version_parts = [int(x) for x in match.split('.')]
                    versions.append({
                        'version': match,
                        'parts': version_parts,
                        'package': f"mdm-manager-{match}.zip"
                    })
                except ValueError:
                    continue
            
            # Sort by version parts (newest first)
            versions.sort(key=lambda x: x['parts'], reverse=True)
            
            self.available_versions = versions
            if versions:
                self.latest_version = versions[0]['version']
                self.package_name = versions[0]['package']
            
            self.debug_manager.print(f"Discovered {len(versions)} available versions: {[v['version'] for v in versions]}")
            return versions
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.debug_manager.print_warning("Server requires authentication for directory listing. Using fallback version list.")
                return self._get_fallback_versions()
            else:
                self.debug_manager.print_error(f"HTTP error discovering versions: {str(e)}")
                return self._get_fallback_versions()
        except Exception as e:
            self.debug_manager.print_error(f"Failed to discover versions: {str(e)}")
            return self._get_fallback_versions()
    
    def _get_fallback_versions(self):
        """
        Get fallback version list when server discovery fails
        
        Returns:
            list: List of available version strings
        """
        # Manual list of known versions - update this when new versions are released
        fallback_versions = [
            {'version': '0.2.0', 'parts': [0, 2, 0], 'package': 'mdm-manager-0.2.0.zip'},
            {'version': '0.1.0', 'parts': [0, 1, 0], 'package': 'mdm-manager-0.1.0.zip'},
        ]
        
        # Sort by version parts (newest first)
        fallback_versions.sort(key=lambda x: x['parts'], reverse=True)
        
        self.available_versions = fallback_versions
        if fallback_versions:
            self.latest_version = fallback_versions[0]['version']
            self.package_name = fallback_versions[0]['package']
        
        self.debug_manager.print(f"Using fallback version list with {len(fallback_versions)} versions")
        return fallback_versions
    
    def check_for_updates(self):
        """
        Check if updates are available
        
        Returns:
            dict: Update information including version and availability
        """
        try:
            # Discover available versions
            available_versions = self.discover_available_versions()
            
            if not available_versions:
                return {
                    'available': False,
                    'error': 'No versions found on server'
                }
            
            latest_version = available_versions[0]['version']
            is_newer = self.version_mgr.is_version_newer(latest_version, self.current_version)
            
            return {
                'available': is_newer,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'url': f"{self.base_url}/{self.package_name}",
                'is_reinstall': latest_version == self.current_version
            }
            
        except Exception as e:
            self.debug_manager.print_error(f"Failed to check for updates: {str(e)}")
            return {
                'available': False,
                'error': str(e)
            } 