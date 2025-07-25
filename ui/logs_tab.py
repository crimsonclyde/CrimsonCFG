#!/usr/bin/env python3
"""
LogsTab: Encapsulates the Logs tab UI and logic for CrimsonCFG
"""
from gi.repository import Gtk, Gdk

class LogsTab(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_window = main_window
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.1, 0.1, 0.1, 0.3))
        self.set_margin_top(15)
        self._build_tab()

    def _build_tab(self):
        # Debug controls
        debug_frame = Gtk.Frame(label="Debug Controls")
        debug_background = Gtk.EventBox()
        debug_background.set_visible_window(True)
        debug_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        debug_frame.add(debug_background)
        debug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        debug_box.set_margin_start(15)
        debug_box.set_margin_end(15)
        debug_box.set_margin_top(15)
        debug_box.set_margin_bottom(15)
        debug_background.add(debug_box)
        self.pack_start(debug_frame, False, False, 0)
        # Debug checkbox
        self.main_window.debug_checkbox = Gtk.CheckButton(label="Enable Debug Mode")
        self.main_window.debug_checkbox.set_active(self.main_window.debug)
        self.main_window.debug_checkbox.connect("toggled", self.main_window.on_debug_toggled)
        debug_box.pack_start(self.main_window.debug_checkbox, False, False, 0)
        # Clear logs button
        clear_logs_btn = Gtk.Button(label="Clear Logs")
        clear_logs_btn.connect("clicked", self.main_window.clear_logs)
        debug_box.pack_start(clear_logs_btn, False, False, 0)
        # Copy logs button
        copy_logs_btn = Gtk.Button(label="Copy Logs")
        def on_copy_logs_clicked(btn):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            start_iter = self.main_window.logs_buffer.get_start_iter()
            end_iter = self.main_window.logs_buffer.get_end_iter()
            text = self.main_window.logs_buffer.get_text(start_iter, end_iter, True)
            clipboard.set_text(text, -1)
        copy_logs_btn.connect("clicked", on_copy_logs_clicked)
        debug_box.pack_start(copy_logs_btn, False, False, 0)
        # Logs text view
        logs_frame = Gtk.Frame(label="Application Logs")
        logs_background = Gtk.EventBox()
        logs_background.set_visible_window(True)
        logs_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.6))
        logs_frame.add(logs_background)
        logs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        logs_box.set_margin_start(15)
        logs_box.set_margin_end(15)
        logs_box.set_margin_top(15)
        logs_box.set_margin_bottom(15)
        logs_background.add(logs_box)
        self.pack_start(logs_frame, True, True, 0)
        # Logs scrolled window
        logs_scrolled = Gtk.ScrolledWindow()
        logs_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        logs_box.pack_start(logs_scrolled, True, True, 0)
        # Logs text buffer
        self.main_window.logs_buffer = Gtk.TextBuffer()
        self.main_window.logs_textview = Gtk.TextView(buffer=self.main_window.logs_buffer)
        self.main_window.logs_textview.set_editable(False)
        self.main_window.logs_textview.set_monospace(True)
        self.main_window.logs_textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 1.0))
        css = b"""
        textview text selection {
            background-color: #4a9eff;
            color: #181a20;
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        self.main_window.logs_textview.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        logs_scrolled.add(self.main_window.logs_textview)
        # Initialize logs
        self.main_window.logger.log_message("CrimsonCFG started")
        if self.main_window.debug:
            self.main_window.logger.log_message("Debug mode enabled") 