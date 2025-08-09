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
        self.version_file = Path.home() / ".config/com.mdm.manager.cfg/version.txt"
        
    def get_installed_version(self):
        """
        Get the currently installed version from version.txt
        
        Returns:
            str: Version string (e.g., "0.2.0") or None if not found
        """
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r') as f:
                    version = f.read().strip()
                    
                    # Validate version format (should be like "0.2.0")
                    import re
                    if re.match(r'^\d+\.\d+\.\d+$', version):
                        self.debug_manager.print(f"Installed version: {version}")
                        return version
                    else:
                        self.debug_manager.print_warning(f"Invalid version format in file: {version}")
                        return None
            else:
                self.debug_manager.print_warning("Version file not found")
                return None
        except Exception as e:
            self.debug_manager.print_error(f"Error reading version file: {str(e)}")
            return None
    
    def get_version_info(self):
        """
        Get comprehensive version information
        
        Returns:
            dict: Version information including installed version and update info
        """
        installed_version = self.get_installed_version()
        
        return {
            'installed_version': installed_version,
            'version_file_path': str(self.version_file),
            'has_version_file': self.version_file.exists()
        }
    
    def format_version_for_display(self, version):
        """
        Format version for display purposes
        
        Args:
            version (str): Version string
            
        Returns:
            str: Formatted version string
        """
        if not version:
            return "Unknown"
        
        # Clean the version string - remove any extra whitespace and ensure proper format
        version = version.strip()
        
        # Remove any 'v' prefix if present, then add it back consistently
        if version.startswith('v'):
            version = version[1:]
        
        return f"v{version}"
    
    def is_version_newer(self, new_version, current_version):
        """
        Compare two version strings to determine if new_version is newer
        
        Args:
            new_version (str): New version to compare
            current_version (str): Current version to compare against
            
        Returns:
            bool: True if new_version is newer than current_version
        """
        if not current_version:
            return True  # If no current version, any version is newer
        
        try:
            # Parse version strings (e.g., "0.2.0" -> [0, 2, 0])
            def parse_version(v):
                return [int(x) for x in v.split('.')]
            
            new_parts = parse_version(new_version)
            current_parts = parse_version(current_version)
            
            # Pad with zeros if needed
            max_len = max(len(new_parts), len(current_parts))
            new_parts.extend([0] * (max_len - len(new_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return new_parts > current_parts
            
        except Exception as e:
            self.debug_manager.print_error(f"Error comparing versions: {str(e)}")
            return False 