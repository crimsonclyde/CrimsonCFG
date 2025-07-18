#!/usr/bin/env python3
"""
CrimsonCFG Main Launcher
Main entry point that ties together the sudo handler and UI
"""

import os
import sys
import yaml
import importlib.util

# Change to the directory where this script is located
# This ensures relative paths work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load debug setting from YAML
debug = False
try:
    with open("group_vars/all.yml", 'r') as f:
        yaml_config = yaml.safe_load(f)
        debug = yaml_config.get("debug", 0) == 1
except:
    debug = False

if debug:
    print("Starting CrimsonCFG application...")
    print(f"Working directory: {os.getcwd()}")

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio  # type: ignore

if debug:
    print("GTK imported successfully")

# Import the UI module from the new modular structure
try:
    from ui import CrimsonCFGGUI
    if debug:
        print("CrimsonCFGGUI imported successfully from ui module")
except ImportError as e:
    if debug:
        print(f"Failed to import from ui module: {e}")
    # Fallback to old import method
    import importlib.util
    spec = importlib.util.spec_from_file_location("crimson_cfg_ui", "crimson.cfg.ui.py")
    if spec and spec.loader:
        crimson_cfg_ui = importlib.util.module_from_spec(spec)
        sys.modules["crimson_cfg_ui"] = crimson_cfg_ui
        spec.loader.exec_module(crimson_cfg_ui)
        CrimsonCFGGUI = crimson_cfg_ui.CrimsonCFGGUI
        if debug:
            print("CrimsonCFGGUI imported successfully from legacy file")
    else:
        raise ImportError("Could not load crimson.cfg.ui.py")

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

    def do_activate(self):
        if debug:
            print("=== do_activate called ===")
            print("Activating application...")
        try:
            self.main_ui = CrimsonCFGGUI(self)
            if debug:
                print("CrimsonCFGGUI created successfully")
            self.main_ui.window.present()
            if debug:
                print("Window presented")
            self.add_window(self.main_ui.window)
            if debug:
                print("Window added to application")
            self.hold()
            if debug:
                print("Application held")
        except Exception as e:
            if debug:
                print(f"Error in do_activate: {e}")
                import traceback
                traceback.print_exc()

def main():
    """Main entry point"""
    app = CrimsonCFGApplication()
    app.run(sys.argv)

if __name__ == "__main__":
    main() 