#!/usr/bin/env python3
"""
SystemTab: Handles system-related controls and utilities
"""
from gi.repository import Gtk, Gdk, Pango
import os
import subprocess
import threading
from gi.repository import GLib

class SystemTab(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_window = main_window
        self.debug = main_window.debug
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_margin_start(15)
        self.set_margin_end(15)
        
        if self.debug:
            print("SystemTab: Initialized")
        
        self._build_tab()
        
    def _build_tab(self):
        """Build the system tab content"""
        if self.debug:
            print("SystemTab: Building system tab content...")
            
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>System Controls</span>")
        title_label.set_halign(Gtk.Align.START)
        self.pack_start(title_label, False, False, 0)
        
        # Description
        desc_label = Gtk.Label()
        desc_label.set_markup("<span size='medium'>Manage system updates and maintenance tasks</span>")
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_margin_bottom(20)
        self.pack_start(desc_label, False, False, 0)
        
        # Main content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.pack_start(content_box, True, True, 0)
        
        # Left column - System Updates
        left_frame = Gtk.Frame(label="System Updates")
        left_frame.set_hexpand(True)
        content_box.pack_start(left_frame, True, True, 0)
        
        # Add background to left frame
        left_background = Gtk.EventBox()
        left_background.set_visible_window(True)
        left_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        left_frame.add(left_background)
        
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_box.set_margin_start(20)
        left_box.set_margin_end(20)
        left_box.set_margin_top(20)
        left_box.set_margin_bottom(20)
        left_background.add(left_box)
        
        # Super Upgrade Frame
        super_upgrade_frame = Gtk.Frame(label="🔄 Super Upgrade")
        super_upgrade_frame.set_margin_bottom(15)
        left_box.pack_start(super_upgrade_frame, False, False, 0)
        
        # Super Upgrade content
        super_upgrade_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        super_upgrade_box.set_margin_start(15)
        super_upgrade_box.set_margin_end(15)
        super_upgrade_box.set_margin_top(15)
        super_upgrade_box.set_margin_bottom(15)
        super_upgrade_frame.add(super_upgrade_box)
        
        # Super Upgrade row
        super_upgrade_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        super_upgrade_box.pack_start(super_upgrade_row, False, False, 0)
        
        # Super Upgrade button
        self.super_upgrade_btn = Gtk.Button(label="Run Super Upgrade")
        self.super_upgrade_btn.set_tooltip_text("Update all system packages (APT, Flatpak, Snap)")
        self.super_upgrade_btn.connect("clicked", self.run_super_upgrade)
        super_upgrade_row.pack_start(self.super_upgrade_btn, False, False, 0)
        
        # Super Upgrade description
        super_upgrade_desc = Gtk.Label()
        super_upgrade_desc.set_markup("Comprehensive system update (APT, Flatpak, Snap)")
        super_upgrade_desc.set_halign(Gtk.Align.START)
        super_upgrade_desc.set_line_wrap(True)
        super_upgrade_desc.set_tooltip_text("Updates all system packages including:\n• APT packages (system updates)\n• Flatpak applications (if installed)\n• Snap packages (if installed)")
        super_upgrade_row.pack_start(super_upgrade_desc, True, True, 0)
        
        # Super Upgrade status label
        self.super_upgrade_status = Gtk.Label()
        self.super_upgrade_status.set_halign(Gtk.Align.START)
        super_upgrade_box.pack_start(self.super_upgrade_status, False, False, 0)
        
        # Quick Update Frame
        quick_update_frame = Gtk.Frame(label="⚡ Quick Update")
        left_box.pack_start(quick_update_frame, False, False, 0)
        
        # Quick Update content
        quick_update_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        quick_update_box.set_margin_start(15)
        quick_update_box.set_margin_end(15)
        quick_update_box.set_margin_top(15)
        quick_update_box.set_margin_bottom(15)
        quick_update_frame.add(quick_update_box)
        
        # Quick Update row
        quick_update_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        quick_update_box.pack_start(quick_update_row, False, False, 0)
        
        # Quick Update button
        self.quick_update_btn = Gtk.Button(label="Run Quick Update")
        self.quick_update_btn.set_tooltip_text("Update APT packages only")
        self.quick_update_btn.connect("clicked", self.run_quick_update)
        quick_update_row.pack_start(self.quick_update_btn, False, False, 0)
        
        # Quick Update description
        quick_update_desc = Gtk.Label()
        quick_update_desc.set_markup("Fast APT-only update")
        quick_update_desc.set_halign(Gtk.Align.START)
        quick_update_desc.set_line_wrap(True)
        quick_update_desc.set_tooltip_text("Updates only APT packages (system packages)")
        quick_update_row.pack_start(quick_update_desc, True, True, 0)
        
        # Quick Update status label
        self.quick_update_status = Gtk.Label()
        self.quick_update_status.set_halign(Gtk.Align.START)
        quick_update_box.pack_start(self.quick_update_status, False, False, 0)
        
        # Right column - System Information
        right_frame = Gtk.Frame(label="System Information")
        right_frame.set_hexpand(True)
        content_box.pack_start(right_frame, True, True, 0)
        
        # Add background to right frame
        right_background = Gtk.EventBox()
        right_background.set_visible_window(True)
        right_background.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.24, 0.24, 0.24, 0.3))
        right_frame.add(right_background)
        
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        right_box.set_margin_start(20)
        right_box.set_margin_end(20)
        right_box.set_margin_top(20)
        right_box.set_margin_bottom(20)
        right_background.add(right_box)
        
        # System info label
        system_info_label = Gtk.Label()
        system_info_label.set_markup("<span size='large' weight='bold'>📊 System Status</span>")
        system_info_label.set_halign(Gtk.Align.START)
        right_box.pack_start(system_info_label, False, False, 0)
        
        # Create scrolled window for system info
        system_info_scrolled = Gtk.ScrolledWindow()
        system_info_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        system_info_scrolled.set_min_content_height(250)
        system_info_scrolled.set_max_content_height(400)
        right_box.pack_start(system_info_scrolled, True, True, 0)
        
        # System info grid container
        self.system_info_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.system_info_container.set_margin_start(10)
        self.system_info_container.set_margin_end(10)
        self.system_info_container.set_margin_top(10)
        self.system_info_container.set_margin_bottom(10)
        system_info_scrolled.add(self.system_info_container)
        
        # Refresh system info button
        self.refresh_info_btn = Gtk.Button(label="Refresh System Info")
        self.refresh_info_btn.set_tooltip_text("Update system information display")
        self.refresh_info_btn.connect("clicked", self.refresh_system_info)
        right_box.pack_start(self.refresh_info_btn, False, False, 0)
        
        # Load initial system info
        self.refresh_system_info(None)
        
        if self.debug:
            print("SystemTab: System tab content built successfully")
    
    def run_super_upgrade(self, button):
        """Run the super upgrade with proper sudo password handling"""
        try:
            if self.debug:
                print("SystemTab: Super upgrade button clicked")
            
            # Check if user is authenticated
            if not self.main_window.sudo_password:
                self.main_window.show_error_dialog("Please authenticate first by clicking 'Authenticate' in the Administration tab.")
                return
            
            # Show confirmation dialog
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Super Upgrade Confirmation",
                secondary_text="This will update all system packages (APT, Flatpak, Snap) and may take several minutes. Do you want to continue?"
            )
            
            response = dialog.run()
            dialog.destroy()
            
            if response != Gtk.ResponseType.YES:
                return
            
            # Show status message
            self.main_window.status_label.set_text("Running Super Upgrade... This may take several minutes.")
            
            # Run super upgrade in background thread
            def run_upgrade():
                try:
                    # Execute the super-upgrade function using the cached sudo password
                    cmd = f'echo "{self.main_window.sudo_password}" | sudo -S bash -c "source ~/.bashrc && super-upgrade"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        GLib.idle_add(self.main_window.status_label.set_text, "Super Upgrade completed successfully!")
                        GLib.idle_add(self.main_window.show_success_dialog, "Super Upgrade completed successfully!\n\nAll system packages have been updated.")
                    else:
                        error_msg = f"Super Upgrade failed. Error: {result.stderr}"
                        GLib.idle_add(self.main_window.status_label.set_text, "Super Upgrade failed. Check logs for details.")
                        GLib.idle_add(self.main_window.show_error_dialog, f"Super Upgrade failed.\n\nError: {result.stderr}\n\nCheck the logs in /var/log/CrimsonCFG/super-upgrade/ for details.")
                        
                except Exception as e:
                    error_msg = f"Error during super upgrade: {e}"
                    GLib.idle_add(self.main_window.status_label.set_text, error_msg)
                    GLib.idle_add(self.main_window.show_error_dialog, error_msg)
            
            thread = threading.Thread(target=run_upgrade)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            error_msg = f"Error starting super upgrade: {e}"
            self.main_window.status_label.set_text(error_msg)
            if self.debug:
                print(f"SystemTab: Error starting super upgrade: {e}")
    
    def run_quick_update(self, button):
        """Run a quick APT-only update"""
        try:
            if self.debug:
                print("SystemTab: Quick update button clicked")
            
            # Check if user is authenticated
            if not self.main_window.sudo_password:
                self.main_window.show_error_dialog("Please authenticate first by clicking 'Authenticate' in the Administration tab.")
                return
            
            # Show confirmation dialog
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window.window,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Quick Update Confirmation",
                secondary_text="This will update APT packages only. Do you want to continue?"
            )
            
            response = dialog.run()
            dialog.destroy()
            
            if response != Gtk.ResponseType.YES:
                return
            
            # Show status message
            self.main_window.status_label.set_text("Running Quick Update...")
            
            # Run quick update in background thread
            def run_update():
                try:
                    # Execute APT update using the cached sudo password
                    cmd = f'echo "{self.main_window.sudo_password}" | sudo -S apt-get update && echo "{self.main_window.sudo_password}" | sudo -S apt-get full-upgrade -y'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        GLib.idle_add(self.main_window.status_label.set_text, "Quick Update completed successfully!")
                        GLib.idle_add(self.main_window.show_success_dialog, "Quick Update completed successfully!\n\nAPT packages have been updated.")
                    else:
                        error_msg = f"Quick Update failed. Error: {result.stderr}"
                        GLib.idle_add(self.main_window.status_label.set_text, "Quick Update failed. Check logs for details.")
                        GLib.idle_add(self.main_window.show_error_dialog, f"Quick Update failed.\n\nError: {result.stderr}")
                        
                except Exception as e:
                    error_msg = f"Error during quick update: {e}"
                    GLib.idle_add(self.main_window.status_label.set_text, error_msg)
                    GLib.idle_add(self.main_window.show_error_dialog, error_msg)
            
            thread = threading.Thread(target=run_update)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            error_msg = f"Error starting quick update: {e}"
            self.main_window.status_label.set_text(error_msg)
            if self.debug:
                print(f"SystemTab: Error starting quick update: {e}")
    
    def refresh_system_info(self, button):
        """Refresh system information display"""
        try:
            if self.debug:
                print("SystemTab: Refreshing system info...")
            
            # Clear existing content
            for child in self.system_info_container.get_children():
                self.system_info_container.remove(child)
            
            # System information data
            system_data = {}
            
            # Hostname
            try:
                result = subprocess.run(['hostname'], capture_output=True, text=True)
                if result.returncode == 0:
                    system_data['hostname'] = result.stdout.strip()
                else:
                    system_data['hostname'] = "Unknown"
            except:
                system_data['hostname'] = "Unknown"
            
            # OS information
            try:
                result = subprocess.run(['lsb_release', '-d'], capture_output=True, text=True)
                if result.returncode == 0:
                    os_info = result.stdout.strip().split(':', 1)[1].strip()
                    system_data['os'] = os_info
                else:
                    system_data['os'] = "Unknown"
            except:
                system_data['os'] = "Unknown"
            
            # Kernel version
            try:
                result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
                if result.returncode == 0:
                    system_data['kernel'] = result.stdout.strip()
                else:
                    system_data['kernel'] = "Unknown"
            except:
                system_data['kernel'] = "Unknown"
            
            # RAM information
            try:
                result = subprocess.run(['free', '-h'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        mem_line = lines[1].split()
                        if len(mem_line) >= 2:
                            system_data['ram'] = mem_line[1]
                        else:
                            system_data['ram'] = "Unknown"
                    else:
                        system_data['ram'] = "Unknown"
                else:
                    system_data['ram'] = "Unknown"
            except:
                system_data['ram'] = "Unknown"
            
            # HDD information
            try:
                result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        disk_line = lines[1].split()
                        if len(disk_line) >= 5:
                            total_disk = disk_line[1]
                            used_disk = disk_line[2]
                            available_disk = disk_line[3]
                            usage_percent = disk_line[4]
                            system_data['hdd'] = {
                                'total': total_disk,
                                'available': available_disk,
                                'used': used_disk,
                                'usage_percent': usage_percent
                            }
                        else:
                            system_data['hdd'] = None
                    else:
                        system_data['hdd'] = None
                else:
                    system_data['hdd'] = None
            except:
                system_data['hdd'] = None
            
            # IP addresses with interfaces
            try:
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    interface_ips = []
                    current_interface = ""
                    
                    for line in lines:
                        line = line.strip()
                        # Check if this is an interface line (e.g., "1: lo: <LOOPBACK,UP,LOWER_UP>")
                        if line and line[0].isdigit() and ':' in line:
                            # Extract interface name (e.g., "lo" from "1: lo:")
                            interface_part = line.split(':')[1].strip()
                            if interface_part != 'lo':  # Skip loopback
                                current_interface = interface_part
                        elif line.startswith('inet ') and not line.startswith('inet6 '):
                            # Extract IPv4 address
                            parts = line.split()
                            if len(parts) >= 2 and current_interface:
                                ip = parts[1].split('/')[0]  # Remove CIDR notation
                                # Get friendly interface name
                                friendly_name = self._get_friendly_interface_name(current_interface)
                                interface_ips.append((friendly_name, ip))
                    
                    # WAN IP address
                    try:
                        result = subprocess.run(['curl', '-s', '--max-time', '5', 'ifconfig.me'], capture_output=True, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            wan_ip = result.stdout.strip()
                            interface_ips.append(("WAN IP", wan_ip))
                    except:
                        pass  # Skip WAN IP if it fails
                    
                    if interface_ips:
                        system_data['ips'] = interface_ips  # Store as list of tuples
                    else:
                        system_data['ips'] = []
                else:
                    system_data['ips'] = []
            except:
                system_data['ips'] = []
            
            # Package managers
            system_data['package_managers'] = {}
            system_data['package_managers']['apt'] = subprocess.run(['which', 'apt-get'], capture_output=True).returncode == 0
            system_data['package_managers']['snap'] = subprocess.run(['which', 'snap'], capture_output=True).returncode == 0
            system_data['package_managers']['flatpak'] = subprocess.run(['which', 'flatpak'], capture_output=True).returncode == 0
            
            # Create UI elements
            self._create_system_info_ui(system_data)
            
            # Check super-upgrade function availability for button state
            super_upgrade_available = subprocess.run(['bash', '-c', 'command -v super-upgrade'], capture_output=True).returncode == 0
            self.update_super_upgrade_status(super_upgrade_available)
            
            # Check sudo access for Quick Update
            sudo_available = self.main_window.sudo_password is not None
            self.update_quick_update_status(sudo_available)
            
            if self.debug:
                print("SystemTab: System info refreshed successfully")
                
        except Exception as e:
            if self.debug:
                print(f"SystemTab: Error refreshing system info: {e}")
            # Show error in UI
            error_label = Gtk.Label()
            error_label.set_markup(f"<span foreground='red'>Error loading system information: {e}</span>")
            error_label.set_halign(Gtk.Align.START)
            self.system_info_container.pack_start(error_label, False, False, 0)
    
    def _create_system_info_ui(self, system_data):
        """Create UI elements for system information display"""
        
        # System information grid
        info_grid = Gtk.Grid()
        info_grid.set_row_spacing(8)
        info_grid.set_column_spacing(15)
        info_grid.set_column_homogeneous(False)
        self.system_info_container.pack_start(info_grid, False, False, 0)
        
        # System information items (excluding IPs and HDD which will be handled separately)
        info_items = [
            ("🖥️", "Hostname", system_data['hostname']),
            ("💻", "OS", system_data['os']),
            ("⚙️", "Kernel", system_data['kernel']),
            ("💾", "RAM", system_data['ram'])
        ]
        
        row = 0
        for icon, label, value in info_items:
            # Icon and label
            icon_label = Gtk.Label()
            icon_label.set_markup(f"<span size='medium'>{icon}</span>")
            icon_label.set_halign(Gtk.Align.START)
            icon_label.set_margin_end(5)
            info_grid.attach(icon_label, 0, row, 1, 1)
            
            label_widget = Gtk.Label()
            label_widget.set_markup(f"<b>{label}:</b>")
            label_widget.set_halign(Gtk.Align.START)
            label_widget.set_margin_end(10)
            info_grid.attach(label_widget, 1, row, 1, 1)
            
            # Value (with word wrap for long values)
            value_label = Gtk.Label()
            value_label.set_text(value)
            value_label.set_halign(Gtk.Align.START)
            value_label.set_line_wrap(True)
            value_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            value_label.set_hexpand(True)
            info_grid.attach(value_label, 2, row, 1, 1)
            
            row += 1
        
        # HDD information section (separate rows for each metric)
        if system_data['hdd']:
            # Add HDD section header
            hdd_header_label = Gtk.Label()
            hdd_header_label.set_markup("<span size='medium' weight='bold'>💿 Disk Usage</span>")
            hdd_header_label.set_halign(Gtk.Align.START)
            hdd_header_label.set_margin_top(10)
            self.system_info_container.pack_start(hdd_header_label, False, False, 0)
            
            # Create HDD grid
            hdd_grid = Gtk.Grid()
            hdd_grid.set_row_spacing(5)
            hdd_grid.set_column_spacing(15)
            hdd_grid.set_column_homogeneous(False)
            self.system_info_container.pack_start(hdd_grid, False, False, 0)
            
            hdd_row = 0
            hdd_items = [
                ("Total:", system_data['hdd']['total']),
                ("Available:", system_data['hdd']['available']),
                ("Used:", f"{system_data['hdd']['used']} ({system_data['hdd']['usage_percent']})")
            ]
            
            for label, value in hdd_items:
                # Label
                hdd_label = Gtk.Label()
                hdd_label.set_markup(f"<b>{label}</b>")
                hdd_label.set_halign(Gtk.Align.START)
                hdd_label.set_margin_end(10)
                hdd_grid.attach(hdd_label, 0, hdd_row, 1, 1)
                
                # Value
                hdd_value = Gtk.Label()
                hdd_value.set_text(value)
                hdd_value.set_halign(Gtk.Align.START)
                hdd_value.set_hexpand(True)
                hdd_grid.attach(hdd_value, 1, hdd_row, 1, 1)
                
                hdd_row += 1
        else:
            # No HDD info found
            hdd_header_label = Gtk.Label()
            hdd_header_label.set_markup("<span size='medium' weight='bold'>💿 Disk Usage</span>")
            hdd_header_label.set_halign(Gtk.Align.START)
            hdd_header_label.set_margin_top(10)
            self.system_info_container.pack_start(hdd_header_label, False, False, 0)
            
            hdd_value = Gtk.Label()
            hdd_value.set_text("Unable to determine")
            hdd_value.set_halign(Gtk.Align.START)
            self.system_info_container.pack_start(hdd_value, False, False, 0)
        
        # IP addresses section (separate rows for each interface)
        if system_data['ips']:
            # Add IPs section header
            ip_header_label = Gtk.Label()
            ip_header_label.set_markup("<span size='medium' weight='bold'>🌐 Network Interfaces</span>")
            ip_header_label.set_halign(Gtk.Align.START)
            ip_header_label.set_margin_top(10)
            self.system_info_container.pack_start(ip_header_label, False, False, 0)
            
            # Create IP grid
            ip_grid = Gtk.Grid()
            ip_grid.set_row_spacing(5)
            ip_grid.set_column_spacing(15)
            ip_grid.set_column_homogeneous(False)
            self.system_info_container.pack_start(ip_grid, False, False, 0)
            
            ip_row = 0
            for friendly_name, ip in system_data['ips']:
                # Interface name
                interface_label = Gtk.Label()
                interface_label.set_markup(f"<b>{friendly_name}:</b>")
                interface_label.set_halign(Gtk.Align.START)
                interface_label.set_margin_end(10)
                ip_grid.attach(interface_label, 0, ip_row, 1, 1)
                
                # IP address
                ip_label = Gtk.Label()
                ip_label.set_text(ip)
                ip_label.set_halign(Gtk.Align.START)
                ip_label.set_hexpand(True)
                ip_grid.attach(ip_label, 1, ip_row, 1, 1)
                
                ip_row += 1
        else:
            # No IPs found
            no_ip_label = Gtk.Label()
            no_ip_label.set_markup("<span size='medium' weight='bold'>🌐 Network Interfaces</span>")
            no_ip_label.set_halign(Gtk.Align.START)
            no_ip_label.set_margin_top(10)
            self.system_info_container.pack_start(no_ip_label, False, False, 0)
            
            no_ip_value = Gtk.Label()
            no_ip_value.set_text("None found")
            no_ip_value.set_halign(Gtk.Align.START)
            self.system_info_container.pack_start(no_ip_value, False, False, 0)
        
        # Package managers section
        pkg_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        pkg_separator.set_margin_top(15)
        pkg_separator.set_margin_bottom(15)
        self.system_info_container.pack_start(pkg_separator, False, False, 0)
        
        pkg_label = Gtk.Label()
        pkg_label.set_markup("<span size='medium' weight='bold'>📦 Package Managers</span>")
        pkg_label.set_halign(Gtk.Align.START)
        self.system_info_container.pack_start(pkg_label, False, False, 0)
        
        pkg_grid = Gtk.Grid()
        pkg_grid.set_row_spacing(5)
        pkg_grid.set_column_spacing(10)
        self.system_info_container.pack_start(pkg_grid, False, False, 0)
        
        pkg_row = 0
        for pkg_name, is_available in system_data['package_managers'].items():
            # Package name
            pkg_name_label = Gtk.Label()
            pkg_name_label.set_markup(f"<b>{pkg_name.upper()}:</b>")
            pkg_name_label.set_halign(Gtk.Align.START)
            pkg_grid.attach(pkg_name_label, 0, pkg_row, 1, 1)
            
            # Status
            status_label = Gtk.Label()
            if is_available:
                status_label.set_markup("<span foreground='green'>✅ Available</span>")
            else:
                status_label.set_markup("<span foreground='red'>❌ Not available</span>")
            status_label.set_halign(Gtk.Align.START)
            pkg_grid.attach(status_label, 1, pkg_row, 1, 1)
            
            pkg_row += 1
    
    def _get_friendly_interface_name(self, interface):
        """Convert interface names to user-friendly names"""
        friendly_names = {
            'eth0': 'Ethernet',
            'eth1': 'Ethernet 2',
            'wlan0': 'WiFi',
            'wlan1': 'WiFi 2',
            'wlp': 'WiFi',
            'enp': 'Ethernet',
            'ens': 'Ethernet',
            'eno': 'Ethernet',
            'tailscale0': 'Tailscale',
            'tun0': 'VPN',
            'tun1': 'VPN 2',
            'ppp0': 'PPP',
            'pppoe': 'PPPoE'
        }
        
        # Check for exact matches first
        if interface in friendly_names:
            return friendly_names[interface]
        
        # Check for partial matches (e.g., enp0s3 -> Ethernet)
        for prefix, friendly_name in friendly_names.items():
            if interface.startswith(prefix):
                return friendly_name
        
        # For numbered interfaces, try to make them more readable
        if interface.startswith('en') and len(interface) > 2:
            return f"Ethernet {interface[2:]}"
        elif interface.startswith('wl') and len(interface) > 2:
            return f"WiFi {interface[2:]}"
        
        # Return the original name if no match found
        return interface
    
    def update_super_upgrade_status(self, is_available):
        """Update the Super Upgrade button state and status message"""
        if is_available:
            # Enable the button
            self.super_upgrade_btn.set_sensitive(True)
            self.super_upgrade_btn.set_tooltip_text("Update all system packages (APT, Flatpak, Snap)")
            self.super_upgrade_status.set_markup("<span foreground='green'>✅ Super Upgrade function is available</span>")
        else:
            # Disable the button
            self.super_upgrade_btn.set_sensitive(False)
            self.super_upgrade_btn.set_tooltip_text("Super Upgrade function not installed. Install the 'Super Upgrade Function' playbook first.")
            self.super_upgrade_status.set_markup(
                "<span foreground='orange'>⚠️ Super Upgrade function not installed</span>\n"
                "<span size='small'>To enable this feature, install the 'Super Upgrade Function' playbook from the Main tab → Customisation category</span>"
            )
    
    def update_quick_update_status(self, sudo_available):
        """Update the Quick Update button state and status message"""
        if sudo_available:
            # Enable the button
            self.quick_update_btn.set_sensitive(True)
            self.quick_update_btn.set_tooltip_text("Update APT packages only")
            self.quick_update_status.set_markup("")
        else:
            # Disable the button
            self.quick_update_btn.set_sensitive(False)
            self.quick_update_btn.set_tooltip_text("Please authenticate first by clicking 'Authenticate' in the Administration tab.")
            self.quick_update_status.set_markup(
                "<span foreground='orange'>⚠️ Authentication required</span>\n"
                "<span size='small'>Please authenticate in the Administration tab to enable Quick Update</span>"
            )
    
    def refresh_button_states(self):
        """Refresh button states when authentication status changes"""
        if self.debug:
            print("SystemTab: Refreshing button states...")
        
        # Check super-upgrade function availability
        super_upgrade_available = subprocess.run(['bash', '-c', 'command -v super-upgrade'], capture_output=True).returncode == 0
        self.update_super_upgrade_status(super_upgrade_available)
        
        # Check sudo access
        sudo_available = self.main_window.sudo_password is not None
        self.update_quick_update_status(sudo_available) 