#!/usr/bin/env python3
"""
Update Manager for MDM Manager
Handles updating the application using git operations
"""

import os
import sys
import subprocess
import time
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
        self.app_dir = "/opt/CrimsonCFG"
        # Use the actual app directory for updates (requires sudo)
        self.working_dir = self.config.get('settings', {}).get('working_directory', self.app_dir)
        
        # Get current version from version manager
        from . import version_manager
        self.version_mgr = version_manager.VersionManager(config)
        self.current_version = self.version_mgr.get_installed_version()
        
        # Git repository information
        self.repo_url = "https://github.com/crimsonclyde/CrimsonCFG.git"
        self.branch = "main"  # Default branch
        
    def check_for_updates(self):
        """
        Check if updates are available by fetching from remote repository
        
        Returns:
            dict: Update information including availability
        """
        try:
            # Check if we have sudo access
            if not self._check_sudo_access():
                return {
                    'available': False,
                    'error': 'Cannot access application directory. Please provide sudo password in the admin tab.'
                }
            
            # Fetch latest changes from remote
            if not self._run_git_command(["fetch", "origin"]):
                return {
                    'available': False,
                    'error': 'Failed to fetch updates from remote repository'
                }
            
            # Get current commit hash
            current_commit = self._get_git_commit_hash()
            if not current_commit:
                return {
                    'available': False,
                    'error': 'Failed to get current commit hash'
                }
            
            # Get remote commit hash
            remote_commit = self._get_remote_commit_hash()
            if not remote_commit:
                return {
                    'available': False,
                    'error': 'Failed to get remote commit hash'
                }
            
            # Check if remote is ahead
            if current_commit == remote_commit:
                return {
                    'available': False,
                    'is_reinstall': True,
                    'current_commit': current_commit,
                    'remote_commit': remote_commit
                }
            
            return {
                'available': True,
                'current_commit': current_commit,
                'remote_commit': remote_commit,
                'is_reinstall': False
            }
            
        except Exception as e:
            self.debug_manager.print_error(f"Failed to check for updates: {str(e)}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def download_update(self, progress_callback=None, completion_callback=None):
        """
        Update the application using git pull
        
        Args:
            progress_callback: Function to call with progress updates (percentage, message)
            completion_callback: Function to call when update completes (success, message)
        """
        def update_thread():
            try:
                if progress_callback:
                    GLib.idle_add(progress_callback, 0, "Starting git update...")
                
                # Check if we have sudo access
                if not self._check_sudo_access():
                    raise PermissionError("Cannot access application directory. Please provide sudo password in the admin tab.")
                
                if progress_callback:
                    GLib.idle_add(progress_callback, 25, "Fetching latest changes...")
                
                # Fetch latest changes
                if not self._run_git_command(["fetch", "origin"]):
                    raise Exception("Failed to fetch updates from remote repository")
                
                if progress_callback:
                    GLib.idle_add(progress_callback, 50, "Pulling latest changes...")
                
                # Pull latest changes
                if not self._run_git_command(["pull", "origin", self.branch]):
                    raise Exception("Failed to pull latest changes")
                
                if progress_callback:
                    GLib.idle_add(progress_callback, 75, "Setting permissions...")
                
                # Set proper permissions
                self._run_sudo_command(["chown", "-R", "root:root", self.working_dir])
                self._run_sudo_command(["chmod", "-R", "a+rX", self.working_dir])
                
                # Make main script executable
                main_script = os.path.join(self.working_dir, "main.py")
                if os.path.exists(main_script):
                    self._run_sudo_command(["chmod", "+x", main_script])
                
                if progress_callback:
                    GLib.idle_add(progress_callback, 90, "Updating version information...")
                
                # Update completed successfully
                
                if progress_callback:
                    GLib.idle_add(progress_callback, 100, "Update completed!")
                
                if completion_callback:
                    GLib.idle_add(completion_callback, True, "Update completed successfully!")
                    
            except Exception as e:
                self.debug_manager.print_error(f"Update failed: {str(e)}")
                if completion_callback:
                    GLib.idle_add(completion_callback, False, f"Update failed: {str(e)}")
        
        # Start update in background thread
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
    
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
                timeout=30,
                cwd=self.working_dir
            )
            if result.returncode != 0:
                self.debug_manager.print_error(f"Sudo command failed: {' '.join(cmd_args)}")
                self.debug_manager.print_error(f"Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            self.debug_manager.print_error(f"Sudo command exception: {str(e)}")
            return False
    
    def _run_git_command(self, cmd_args):
        """
        Run a git command in the application directory with sudo
        
        Args:
            cmd_args: List of git command arguments
            
        Returns:
            bool: True if command succeeded
        """
        try:
            # Check if we have sudo access
            if not self.main_window or not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
                self.debug_manager.print_error("No sudo password available for git operations")
                return False
            
            # First, ensure the directory is marked as safe
            safe_result = subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", self.working_dir],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Don't fail if this command fails, it might already be set
            
            # Set git to work with the directory
            env = os.environ.copy()
            env['GIT_SAFE_DIRECTORY'] = self.working_dir
            
            # Run git command with sudo
            result = subprocess.run(
                ["sudo", "-k", "-S"] + ["git"] + cmd_args,
                input=f"{self.main_window.sudo_password}\n",
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.working_dir,
                env=env
            )
            if result.returncode != 0:
                self.debug_manager.print_error(f"Git command failed: sudo git {' '.join(cmd_args)}")
                self.debug_manager.print_error(f"Error: {result.stderr}")
                # Try to provide more helpful error messages
                if "fatal: unsafe repository" in result.stderr:
                    self.debug_manager.print_error("Git safe directory issue detected. Try running: git config --global --add safe.directory /opt/CrimsonCFG")
                return False
            return True
        except Exception as e:
            self.debug_manager.print_error(f"Git command exception: {str(e)}")
            return False
    
    def _get_git_commit_hash(self):
        """
        Get the current commit hash
        
        Returns:
            str: Commit hash or None if failed
        """
        try:
            # Check if we have sudo access
            if not self.main_window or not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
                self.debug_manager.print_error("No sudo password available for git operations")
                return None
            
            result = subprocess.run(
                ["sudo", "-k", "-S", "git", "rev-parse", "HEAD"],
                input=f"{self.main_window.sudo_password}\n",
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.working_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            self.debug_manager.print_error(f"Failed to get commit hash: {str(e)}")
            return None
    
    def _get_remote_commit_hash(self):
        """
        Get the remote commit hash for the current branch
        
        Returns:
            str: Remote commit hash or None if failed
        """
        try:
            # Check if we have sudo access
            if not self.main_window or not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
                self.debug_manager.print_error("No sudo password available for git operations")
                return None
            
            result = subprocess.run(
                ["sudo", "-k", "-S", "git", "rev-parse", f"origin/{self.branch}"],
                input=f"{self.main_window.sudo_password}\n",
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.working_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            self.debug_manager.print_error(f"Failed to get remote commit hash: {str(e)}")
            return None
    

    
    def discover_available_versions(self):
        """
        Discover available commits by checking git log
        
        Returns:
            list: List of recent commits
        """
        try:
            # Check if we have sudo access
            if not self.main_window or not hasattr(self.main_window, 'sudo_password') or not self.main_window.sudo_password:
                self.debug_manager.print_error("No sudo password available for git operations")
                return []
            
            # Get recent commits
            result = subprocess.run(
                ["sudo", "-k", "-S", "git", "log", "--oneline", "-10"],
                input=f"{self.main_window.sudo_password}\n",
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.working_dir
            )
            
            if result.returncode != 0:
                return []
            
            # Parse commits
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            
            self.debug_manager.print(f"Found {len(commits)} recent commits")
            return commits
            
        except Exception as e:
            self.debug_manager.print_error(f"Failed to discover commits: {str(e)}")
            return [] 