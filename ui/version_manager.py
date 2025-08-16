#!/usr/bin/env python3
"""
Version Manager for MDM Manager
Provides centralized version management functionality
"""

import os
from pathlib import Path
from .debug_manager import DebugManager

class VersionManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.debug_manager = DebugManager(config)
        self.version_file = Path.home() / ".config/com.crimson.cfg/version.txt"
        
    def get_installed_version(self):
        """
        Get the current commit hash from git
        
        Returns:
            str: Commit hash or None if not found
        """
        try:
            import subprocess
            import os
            
            # Check if we're in a git repository
            app_dir = "/opt/CrimsonCFG"
            if os.path.exists(os.path.join(app_dir, ".git")):
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=app_dir
                )
                if result.returncode == 0:
                    commit_hash = result.stdout.strip()
                    self.debug_manager.print(f"Current commit: {commit_hash}")
                    return commit_hash
            else:
                self.debug_manager.print_warning("Not in a git repository")
                return None
        except Exception as e:
            self.debug_manager.print_error(f"Error getting commit hash: {str(e)}")
            return None
    
    def get_version_info(self):
        """
        Get comprehensive version information
        
        Returns:
            dict: Version information including current commit
        """
        current_commit = self.get_installed_version()
        
        return {
            'installed_version': current_commit,
            'is_git_repo': current_commit is not None
        }
    
    def format_version_for_display(self, commit_hash):
        """
        Format commit hash for display purposes
        
        Args:
            commit_hash (str): Commit hash string
            
        Returns:
            str: Formatted commit hash
        """
        if not commit_hash:
            return "Unknown"
        
        # Clean the commit hash string
        commit_hash = commit_hash.strip()
        
        return f"Commit: {commit_hash}"
    
    def is_commit_different(self, new_commit, current_commit):
        """
        Compare two commit hashes to determine if they are different
        
        Args:
            new_commit (str): New commit hash to compare
            current_commit (str): Current commit hash to compare against
            
        Returns:
            bool: True if commits are different
        """
        if not current_commit:
            return True  # If no current commit, any commit is different
        
        return new_commit != current_commit
    
 