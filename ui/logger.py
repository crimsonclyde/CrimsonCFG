#!/usr/bin/env python3
"""
CrimsonCFG Logger Module
Handles logging functionality
"""

import datetime
from gi.repository import GLib  # type: ignore

class Logger:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
    def log_message(self, message):
        """Add a message to the logs"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Use GLib.idle_add to ensure thread safety when updating GTK widgets
        GLib.idle_add(self._add_log_entry, log_entry)
        
        # Also print to console if debug is enabled
        if self.debug:
            print(f"LOG: {message}")
    
    def _add_log_entry(self, log_entry):
        """Add a log entry to the text buffer (called on main thread)"""
        try:
            # Add to text buffer
            self.main_window.logs_buffer.insert_at_cursor(log_entry)
            
            # Auto-scroll to bottom
            self.main_window.logs_textview.scroll_to_iter(self.main_window.logs_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        except Exception as e:
            # Fallback to console if widget update fails
            print(f"Logger widget error: {e}")
            print(f"LOG: {log_entry.strip()}")
    
    def clear_logs(self, button):
        """Clear the logs display"""
        self.main_window.logs_buffer.set_text("")
        self.log_message("Logs cleared") 