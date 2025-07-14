#!/usr/bin/env python3
"""
CrimsonCFG Logger Module
Handles logging functionality
"""

import datetime

class Logger:
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = main_window.debug
        
    def log_message(self, message):
        """Add a message to the logs"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to text buffer
        self.main_window.logs_buffer.insert_at_cursor(log_entry)
        
        # Auto-scroll to bottom
        self.main_window.logs_textview.scroll_to_iter(self.main_window.logs_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        
        # Also print to console if debug is enabled
        if self.debug:
            print(f"LOG: {message}")
    
    def clear_logs(self, button):
        """Clear the logs display"""
        self.main_window.logs_buffer.set_text("")
        self.log_message("Logs cleared") 