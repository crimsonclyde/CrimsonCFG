#!/usr/bin/env python3
"""
Server Authentication Manager for MDM Manager
Provides centralized server authentication management
"""

import os
from pathlib import Path
from .debug_manager import DebugManager

class ServerAuthManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.debug_manager = DebugManager(config)
        self.auth_file = Path("/opt/MDM-Manager/.auth")
        
    def get_auth_credentials(self):
        """
        Get authentication credentials from .auth file
        
        Returns:
            tuple: (username, password) or (None, None) if not found
        """
        try:
            if self.auth_file.exists():
                with open(self.auth_file, 'r') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 2:
                        username = lines[0].strip()
                        password = lines[1].strip()
                        self.debug_manager.print(f"Loaded server auth credentials for user: {username}")
                        return username, password
                    else:
                        self.debug_manager.print_warning("Invalid .auth file format")
                        return None, None
            else:
                self.debug_manager.print_warning(".auth file not found")
                return None, None
        except Exception as e:
            self.debug_manager.print_error(f"Error reading .auth file: {str(e)}")
            return None, None
    
    def create_auth_file(self, username, password):
        """
        Create .auth file with credentials
        
        Args:
            username (str): Authentication username
            password (str): Authentication password
        """
        try:
            # Create auth file with restricted permissions
            with open(self.auth_file, 'w') as f:
                f.write(f"{username}\n{password}\n")
            
            # Set restrictive permissions (root only)
            os.chmod(self.auth_file, 0o600)
            
            self.debug_manager.print(f"Created .auth file with credentials for: {username}")
            return True
        except Exception as e:
            self.debug_manager.print_error(f"Error creating .auth file: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """
        Get authentication headers for requests
        
        Returns:
            dict: Authentication headers or empty dict if no credentials
        """
        username, password = self.get_auth_credentials()
        if username and password:
            return {'Authorization': f'Basic {self._encode_basic_auth(username, password)}'}
        return {}
    
    def _encode_basic_auth(self, username, password):
        """
        Encode username and password for Basic Auth
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            str: Base64 encoded credentials
        """
        import base64
        credentials = f"{username}:{password}"
        return base64.b64encode(credentials.encode()).decode() 