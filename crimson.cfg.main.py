#!/usr/bin/env python3
"""
CrimsonCFG Main Launcher
Main entry point that ties together the sudo handler and UI
"""

import os
import sys
import yaml
from pathlib import Path

# Change to the directory where this script is located
# This ensures relative paths work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load debug setting from user's local.yml
debug = False
try:
    config_dir = Path.home() / ".config/com.crimson.cfg"
    local_file = config_dir / "local.yml"
    if local_file.exists():
        with open(local_file, 'r') as f:
            yaml_config = yaml.safe_load(f)
            debug = yaml_config.get("debug", 0) == 1
except Exception as e:
    print(f"Failed to load debug setting from local.yml: {e}")
    debug = False

if debug:
    print("Starting CrimsonCFG application...")
    print(f"Working directory: {os.getcwd()}")

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio  # type: ignore

if debug:
    print("GTK imported successfully")

# Import the UI module from the modular structure
from ui import CrimsonCFGGUI
if debug:
    print("CrimsonCFGGUI imported successfully from ui module")

if debug:
    print("CrimsonCFGGUI imported successfully")

class CrimsonCFGApplication(Gtk.Application):
    def __init__(self):
        if debug:
            print("Initializing CrimsonCFGApplication...")
        Gtk.Application.__init__(
            self,
            application_id="com.crimson.cfg",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        if debug:
            print("CrimsonCFGApplication initialized")
        # Note: Gtk.Application does not support set_icon_name or set_icon_from_file.
        # The icon must be set on the main window (Gtk.ApplicationWindow) for dock/taskbar icon.
        
    def do_window_added(self, window):
        """Handle window added to application"""
        if debug:
            print("Window added to application")
            
    def do_window_removed(self, window):
        """Handle window removed from application"""
        if debug:
            print("Window removed from application")
        # If this was the last window, quit the application
        if len(self.get_windows()) == 0:
            if debug:
                print("No more windows, quitting application")
            self.quit()

    def do_activate(self):
        if debug:
            print("=== do_activate called ===")
        try:
            if debug:
                print("Creating CrimsonCFGGUI...")
            self.main_ui = CrimsonCFGGUI(self)
            if debug:
                print("CrimsonCFGGUI created successfully")
            if debug:
                print("Presenting window...")
            self.main_ui.window.present()
            if debug:
                print("Window presented")
            if debug:
                print("Adding window to application...")
            self.add_window(self.main_ui.window)
            if debug:
                print("Window added to application")
            if debug:
                print("Holding application...")
            self.hold()
            if debug:
                print("Application held")
            if debug:
                print("do_activate completed successfully")
        except Exception as e:
            print(f"Error in do_activate: {e}")
            import traceback
            traceback.print_exc()
            
    def do_startup(self):
        if debug:
            print("=== do_startup called ===")
        Gtk.Application.do_startup(self)
        if debug:
            print("do_startup completed")

def main():
    if debug:
        print("=== main() called ===")
    try:
        app = CrimsonCFGApplication()
        if debug:
            print("CrimsonCFGApplication created")
        if debug:
            print("Starting GTK application...")
        # Check if we're running in a headless environment
        if not os.environ.get('DISPLAY'):
            print("No DISPLAY environment variable found. Running in headless mode.")
            return 0
        if debug:
            print("Running GTK application...")
        app.run(sys.argv)
        if debug:
            print("GTK application run completed")
        if debug:
            print("App run completed")
    except Exception as e:
        print(f"Error in main(): {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 