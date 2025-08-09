#!/usr/bin/env python3
"""
Debug Manager for CrimsonCFG
Centralized debug functionality and logging
"""

import os
from pathlib import Path
from typing import Optional

class DebugManager:
    """Centralized debug management for CrimsonCFG"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize debug manager
        
        Args:
            config: Configuration dictionary containing debug settings
        """
        self.debug = False
        self.config = config
        
        if config:
            self._load_debug_from_config(config)
        else:
            self._load_debug_from_file()
    
    def _load_debug_from_config(self, config: dict):
        """Load debug setting from config dictionary"""
        try:
            self.debug = config.get("settings", {}).get("debug", 0) == 1
        except Exception:
            self.debug = False
    
    def _load_debug_from_file(self):
        """Load debug setting from local.yml file"""
        try:
            import yaml
            config_dir = Path.home() / ".config/com.mdm.manager.cfg"
            local_file = config_dir / "local.yml"
            
            if local_file.exists():
                with open(local_file, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
                    self.debug = local_config.get("debug", 0) == 1
            else:
                self.debug = False
        except Exception:
            self.debug = False
    
    def print(self, message: str):
        """Print debug message if debug is enabled"""
        if self.debug:
            print(f"App: {message}")
    
    def print_error(self, message: str):
        """Print error message (always shown, regardless of debug setting)"""
        print(f"App: ERROR - {message}")
    
    def print_warning(self, message: str):
        """Print warning message (always shown, regardless of debug setting)"""
        print(f"App: WARNING - {message}")
    
    def print_success(self, message: str):
        """Print success message (always shown, regardless of debug setting)"""
        print(f"App: SUCCESS - {message}")
    
    def print_info(self, message: str):
        """Print info message (always shown, regardless of debug setting)"""
        print(f"App: INFO - {message}")
    
    def is_debug_enabled(self) -> bool:
        """Check if debug is enabled"""
        return self.debug
    
    def set_debug(self, enabled: bool):
        """Set debug state"""
        self.debug = enabled
    
    def update_from_config(self, config: dict):
        """Update debug setting from new config"""
        self.config = config
        self._load_debug_from_config(config)
    
    def log_function_call(self, function_name: str, *args, **kwargs):
        """Log function call with arguments if debug is enabled"""
        if self.debug:
            args_str = ", ".join([str(arg) for arg in args])
            kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))
            print(f"App: DEBUG - Calling {function_name}({all_args})")
    
    def log_function_return(self, function_name: str, return_value=None):
        """Log function return value if debug is enabled"""
        if self.debug:
            if return_value is not None:
                print(f"App: DEBUG - {function_name} returned: {return_value}")
            else:
                print(f"App: DEBUG - {function_name} completed")
    
    def log_variable(self, variable_name: str, value):
        """Log variable value if debug is enabled"""
        if self.debug:
            print(f"App: DEBUG - {variable_name} = {value}")
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True):
        """Log file operations if debug is enabled"""
        if self.debug:
            status = "SUCCESS" if success else "FAILED"
            print(f"App: DEBUG - File {operation}: {file_path} - {status}")
    
    def log_config_loading(self, config_path: str, success: bool = True):
        """Log config loading operations if debug is enabled"""
        if self.debug:
            status = "SUCCESS" if success else "FAILED"
            print(f"App: DEBUG - Config loading: {config_path} - {status}")
    
    def log_icon_setting(self, icon_path: str, success: bool = True):
        """Log icon setting operations if debug is enabled"""
        if self.debug:
            status = "SUCCESS" if success else "FAILED"
            print(f"App: DEBUG - Icon setting: {icon_path} - {status}")
    
    def log_application_lifecycle(self, stage: str):
        """Log application lifecycle stages if debug is enabled"""
        if self.debug:
            print(f"App: DEBUG - Application lifecycle: {stage}")
    
    def log_window_operations(self, operation: str, window_name: str = "main"):
        """Log window operations if debug is enabled"""
        if self.debug:
            print(f"App: DEBUG - Window {operation}: {window_name}")
    
    def log_manager_initialization(self, manager_name: str, success: bool = True):
        """Log manager initialization if debug is enabled"""
        if self.debug:
            status = "SUCCESS" if success else "FAILED"
            print(f"App: DEBUG - Manager initialization: {manager_name} - {status}")
    
    def log_template_rendering(self, template_path: str, success: bool = True):
        """Log template rendering operations if debug is enabled"""
        if self.debug:
            status = "SUCCESS" if success else "FAILED"
            print(f"App: DEBUG - Template rendering: {template_path} - {status}")
    
    def log_environment_check(self, check_name: str, result: bool):
        """Log environment checks if debug is enabled"""
        if self.debug:
            status = "PASS" if result else "FAIL"
            print(f"App: DEBUG - Environment check {check_name}: {status}")
    
    def log_performance(self, operation: str, duration_ms: float):
        """Log performance metrics if debug is enabled"""
        if self.debug:
            print(f"App: DEBUG - Performance: {operation} took {duration_ms:.2f}ms")
    
    def log_memory_usage(self, component: str, memory_mb: float):
        """Log memory usage if debug is enabled"""
        if self.debug:
            print(f"App: DEBUG - Memory usage: {component} using {memory_mb:.2f}MB")
    
    def log_network_operation(self, operation: str, url: str, success: bool = True):
        """Log network operations if debug is enabled"""
        if self.debug:
            status = "SUCCESS" if success else "FAILED"
            print(f"App: DEBUG - Network {operation}: {url} - {status}")
    
    def log_user_action(self, action: str, details: str = ""):
        """Log user actions if debug is enabled"""
        if self.debug:
            if details:
                print(f"App: DEBUG - User action: {action} - {details}")
            else:
                print(f"App: DEBUG - User action: {action}")
    
    def log_error_with_traceback(self, error: Exception, context: str = ""):
        """Log error with traceback if debug is enabled"""
        if self.debug:
            import traceback
            print(f"App: DEBUG - Error in {context}: {error}")
            traceback.print_exc()
    
    def log_config_change(self, key: str, old_value, new_value):
        """Log configuration changes if debug is enabled"""
        if self.debug:
            print(f"App: DEBUG - Config change: {key} = {old_value} -> {new_value}")
    
    def log_feature_usage(self, feature: str, details: str = ""):
        """Log feature usage if debug is enabled"""
        if self.debug:
            if details:
                print(f"App: DEBUG - Feature usage: {feature} - {details}")
            else:
                print(f"App: DEBUG - Feature usage: {feature}")
    
    def log_security_event(self, event: str, details: str = ""):
        """Log security events if debug is enabled"""
        if self.debug:
            if details:
                print(f"App: DEBUG - Security event: {event} - {details}")
            else:
                print(f"App: DEBUG - Security event: {event}")
    
    def log_system_info(self):
        """Log system information if debug is enabled"""
        if self.debug:
            import platform
            import sys
            print(f"App: DEBUG - System: {platform.system()} {platform.release()}")
            print(f"App: DEBUG - Python: {sys.version}")
            print(f"App: DEBUG - Working directory: {os.getcwd()}")
            print(f"App: DEBUG - User: {os.getenv('USER', 'unknown')}")
            print(f"App: DEBUG - Display: {os.getenv('DISPLAY', 'none')}")
    
    def log_dependencies(self):
        """Log dependency information if debug is enabled"""
        if self.debug:
            try:
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                print(f"App: DEBUG - GTK version: {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")
            except Exception as e:
                print(f"App: DEBUG - GTK version check failed: {e}")
            
            try:
                import yaml
                print(f"App: DEBUG - PyYAML available: {yaml.__version__}")
            except Exception as e:
                print(f"App: DEBUG - PyYAML version check failed: {e}")
    
    def log_startup_sequence(self):
        """Log startup sequence if debug is enabled"""
        if self.debug:
            print("App: DEBUG - Starting application...")
            print("App: DEBUG - Loading configuration...")
            print("App: DEBUG - Initializing managers...")
            print("App: DEBUG - Creating GUI...")
            print("App: DEBUG - Application startup complete")
    
    def log_shutdown_sequence(self):
        """Log shutdown sequence if debug is enabled"""
        if self.debug:
            print("App: DEBUG - Starting application shutdown...")
            print("App: DEBUG - Cleaning up resources...")
            print("App: DEBUG - Saving configuration...")
            print("App: DEBUG - Application shutdown complete") 