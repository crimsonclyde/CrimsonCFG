# CrimsonCFG - App & Customization Selector

- [CrimsonCFG - App \& Customization Selector](#crimsoncfg---app--customization-selector)
  - [Exordium](#exordium)
  - [Installation](#installation)
  - [Features](#features)
  - [Configuration Structure](#configuration-structure)
    - [Global Configuration (`group_vars/all.yml`)](#global-configuration-group_varsallyml)
    - [Local Configuration (`~/.config/com.crimson.cfg/local.yml`)](#local-configuration-configcomcrimsoncfglocalyml)
    - [Configuration Priority](#configuration-priority)
  - [Usage](#usage)
  - [File Structure](#file-structure)
  - [Development](#development)
    - [Adding New Configuration Variables](#adding-new-configuration-variables)
    - [Adding New Playbooks](#adding-new-playbooks)
  - [Troubleshooting](#troubleshooting)
    - [Permission Issues](#permission-issues)
    - [Configuration Issues](#configuration-issues)
  - [Uninstallation](#uninstallation)
  - [License](#license)

## Exordium

A modern, user-friendly GUI application for managing system configuration and application installation using Ansible playbooks.

![Main Window Screenshot](/files/screenshots/com.crimson.cfg_main.png)

## Installation

```bash
wget https://github.com/crimsonclyde/CrimsonCFG/raw/main/setup.sh -O setup.sh && chmod +x setup.sh && bash setup.sh
```

## Features

- **Modern GTK3 Interface**: Clean, dark-themed UI with Material Design elements
- **Ansible Integration**: Uses Ansible playbooks for reliable system configuration
- **Package Management**: Install APT and Snap packages through the GUI
- **Customization**: Configure SSH, pinned applications, and corporate identity
- **User-Specific Configuration**: Local overrides for user-modifiable settings
- **Real-time Logging**: Live installation progress and debugging information

## Configuration Structure

CrimsonCFG uses a two-tier configuration system:

### Global Configuration (`group_vars/all.yml`)

Contains system-wide defaults and non-user-modifiable settings:

- System paths and directories
- Default application settings
- Ansible configuration
- System-wide package lists (read-only)

### Local Configuration (`~/.config/com.crimson.cfg/local.yml`)

Contains user-modifiable settings that override global defaults:

- **apt_packages**: List of APT packages to install
- **snap_packages**: List of Snap packages to install  
- **pinned_apps**: Applications to pin to the dock/launcher
- **app_name**: Application name for corporate branding
- **app_subtitle**: Application subtitle
- **app_logo**: Path to application logo
- **user**: Current user
- **working_directory**: Application root directory (default: /opt/CrimsonCFG)

### Configuration Priority

1. Local settings (`~/.config/com.crimson.cfg/local.yml`) override global settings
2. Changes made through the UI are saved to the user's local.yml
3. The application can be installed in `/opt/` without permission issues

## Usage

1. **Start the Application**: Run `python3 crimson.cfg.main.py`
2. **Enter Sudo Password**: Required for package installation
3. **Select Playbooks**: Choose from available categories
4. **Configure Settings**: Use the Administration tab to modify:
   - APT packages
   - Snap packages  
   - Pinned applications
   - Corporate identity
5. **Install**: Click "Install Selected" to run the playbooks

## File Structure

```text
CrimsonCFG/
├── group_vars/
│   └── all.yml          # System-wide defaults
├── playbooks/           # Ansible playbooks
├── ui/                  # GUI components
├── functions/           # Utility functions
└── templates/           # Jinja2 templates

User Configuration:
~/.config/com.crimson.cfg/
├── local.yml            # User-modifiable overrides
└── gui_config.json     # GUI configuration

Desktop .dotfile:
~/.local/share/applications/
├── com.crimson.cfg.desktop # Desktopfile
```

## Development

### Adding New Configuration Variables

1. **System-wide defaults**: Add to `group_vars/all.yml`
2. **User-modifiable**: Add to `~/.config/com.crimson.cfg/local.yml` and update UI save functions
3. **UI integration**: Update `ui/gui_builder.py` to read/write the variable

### Adding New Playbooks

1. Create playbook in appropriate category directory
2. Add metadata to `conf/gui_config.json`
3. Include essential variables in `group_vars/all.yml` or `group_vars/local.yml`

## Troubleshooting

### Permission Issues

- User-modifiable settings are now in `~/.config/com.crimson.cfg/local.yml`
- The UI can write to the user's local.yml without elevated privileges
- System-wide settings remain in `group_vars/all.yml`

### Configuration Issues

- Check both `all.yml` and `~/.config/com.crimson.cfg/local.yml` for variable definitions
- Local settings override global settings
- Restart the application after configuration changes

## Uninstallation

To completely remove CrimsonCFG from your system, run:

```bash
./uninstall/uninstall.sh
```

This will remove the application files, configuration, and desktop entry, but will not remove any dependencies installed by the application.

## License

CrimsonCFG is licensed under the GNU Affero General Public License v3.0 (AGPLv3). See the LICENSE file for details.
