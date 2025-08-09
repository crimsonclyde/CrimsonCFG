#!/usr/bin/env python3
"""
Main Launcher
Main entry point that ties together the sudo handler and UI
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

# Change to the directory where this script is located
# This ensures relative paths work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Import config_manager early to use its template rendering
from ui.config_manager import ConfigManager
from ui.debug_manager import DebugManager

# Import the UI module from the modular structure
from ui import CrimsonCFGGUI

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio  # type: ignore

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MDM Manager - System Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py              # Start normally
  python3 main.py --debug      # Start with debug mode enabled
  python3 main.py -d           # Short form for debug mode
        """
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode (overrides local.yml debug setting)'
    )
    
    # Get installed version from version manager
    from ui import version_manager
    version_mgr = version_manager.VersionManager()
    installed_version = version_mgr.get_installed_version()
    display_version = version_mgr.format_version_for_display(installed_version) or 'MDM Manager v0.2.0'
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=display_version
    )
    
    return parser.parse_args()

def ensure_local_config_exists():
    """Ensure local.yml exists before starting the application"""
    # Use config_manager to create the initial config
    config_manager = ConfigManager()
    
    # This will create local.yml if it doesn't exist
    initial_config = config_manager.load_config()
    
    # Create debug manager
    debug_manager = DebugManager(initial_config)
    debug_manager.print("Ensuring local.yml exists")
    debug_manager.print("Initial config ensured")

def load_initial_config(force_debug=False):
    """Load initial configuration from local.yml"""
    # Use config_manager to load the config
    config_manager = ConfigManager()
    
    # Load the config (this will also create it if needed)
    config = config_manager.load_config()
    
    # Override debug setting if --debug was specified
    if force_debug:
        config['settings']['debug'] = 1
        config['local_config']['debug'] = 1
    
    # Create debug manager
    debug_manager = DebugManager(config)
    debug_manager.print("Load initial configuration")
    debug_manager.log_variable("working_directory", config['settings']['working_directory'])
    
    return config

class CrimsonCFGApplication(Gtk.Application):
    def __init__(self, initial_config):
        # Create debug manager
        self.debug_manager = DebugManager(initial_config)
        
        self.debug_manager.print("Initializing Application...")
        Gtk.Application.__init__(
            self,
            application_id="com.crimson.cfg",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.initial_config = initial_config
        self.debug_manager.print("Application initialized")
        # Note: Gtk.Application does not support set_icon_name or set_icon_from_file.
        # The icon must be set on the main window (Gtk.ApplicationWindow) for dock/taskbar icon.
        
    def do_window_added(self, window):
        """App: Handle window added to application"""
        self.debug_manager.log_window_operations("added")
            
    def do_window_removed(self, window):
        """App: Handle window removed from application"""
        self.debug_manager.log_window_operations("removed")
        # If this was the last window, quit the application
        if len(self.get_windows()) == 0:
            self.debug_manager.print("No more windows, quitting application")
            self.quit()

    def do_activate(self):
        self.debug_manager.log_application_lifecycle("do_activate")
        try:
            self.debug_manager.print("Creating GUI...")
            self.main_ui = CrimsonCFGGUI(self, self.initial_config)
            self.debug_manager.print("GUI created successfully")
            self.debug_manager.print("Presenting window...")
            self.main_ui.window.present()
            self.debug_manager.print("Window presented")
            self.debug_manager.print("Adding window to application...")
            self.add_window(self.main_ui.window)
            self.debug_manager.print("Window added to application")
            self.debug_manager.print("Holding application...")
            self.hold()
            self.debug_manager.print("Application held")
            self.debug_manager.print("do_activate completed successfully")
        except Exception as e:
            self.debug_manager.log_error_with_traceback(e, "do_activate")
            
    def do_startup(self):
        self.debug_manager.log_application_lifecycle("do_startup")
        Gtk.Application.do_startup(self)
        self.debug_manager.print("do_startup completed")
            
    def do_shutdown(self):
        """App: Handle application shutdown"""
        self.debug_manager.log_application_lifecycle("do_shutdown")
        # Release the application hold
        self.release()
        self.debug_manager.print("Application released")
        Gtk.Application.do_shutdown(self)
        self.debug_manager.print("do_shutdown completed")

def main():
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # 1. Create local.yml first using config_manager
        ensure_local_config_exists()
        
        # 2. Load initial config using config_manager
        initial_config = load_initial_config(force_debug=args.debug)
        
        # Create debug manager
        debug_manager = DebugManager(initial_config)
        debug_manager.log_application_lifecycle("main")
        
        # Log command line arguments if debug is enabled
        if args.debug:
            debug_manager.print("Debug mode enabled via command line argument")
        
        # 3. Start application with config
        app = CrimsonCFGApplication(initial_config)
        debug_manager.print("CrimsonCFGApplication created")
        debug_manager.print("Starting GTK application...")
        # Check if we're running in a headless environment
        if not os.environ.get('DISPLAY'):
            debug_manager.print_error("No DISPLAY environment variable found. Running in headless mode.")
            return 0
        debug_manager.print("Running GTK application...")
        
        # Filter out our custom arguments before passing to GTK
        gtk_args = []
        skip_next = False
        for arg in sys.argv:
            if skip_next:
                skip_next = False
                continue
            if arg in ['--debug', '-d', '--version', '-v', '--help', '-h']:
                continue
            gtk_args.append(arg)
        
        app.run(gtk_args)
        debug_manager.print("GTK application run completed")
        debug_manager.print("Application run completed")
    except Exception as e:
        debug_manager = DebugManager()
        debug_manager.log_error_with_traceback(e, "main")

if __name__ == "__main__":
    main() 