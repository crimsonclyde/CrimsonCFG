# CrimsonCFG - App & Customization Selector

- [CrimsonCFG - App \& Customization Selector](#crimsoncfg---app--customization-selector)
  - [Exordium](#exordium)
  - [Installation](#installation)
  - [Features](#features)
  - [Configuration Structure](#configuration-structure)
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

## External Playbook Repository

CrimsonCFG allows you to use your own external repository for custom and apps playbooks. This lets you keep your personal or organization-specific playbooks separate from the built-in ones.

### How to Add an External Repository

1. **Go to the Administration tab in the CrimsonCFG UI.**
2. **Open the 'External Playbooks' tab.**
3. **Paste the URL of your Git repository** (e.g., `https://github.com/yourusername/your-playbooks-repo.git`) into the field provided.
4. **Click 'Refresh Playbooks'** to clone or update the repository and load your playbooks.

> **Warning:** Only use repositories you own and trust. Running untrusted playbooks can compromise your system.

### Repository Structure

Your external repository should have the following structure:

```
playbooks/
  apps/
    your_app_playbook.yml
  customisation/
    your_custom_playbook.yml
```

- Place your application playbooks in `playbooks/apps/`.
- Place your customization playbooks in `playbooks/customisation/`.
- Each playbook should start with CrimsonCFG metadata comments, for example:

```
# CrimsonCFG-Name: My Custom App
# CrimsonCFG-Description: Installs my custom app
# CrimsonCFG-Essential: false
---
- name: Install my custom app
  hosts: all
  tasks:
    - name: Example task
      ...
```

- Only the `apps` and `customisation` categories are loaded from your external repo. Built-in `basics` and `security` playbooks remain protected.

### Example

```
my-playbooks-repo/
└── playbooks/
    ├── apps/
    │   └── my_app.yml
    └── customisation/
        └── my_customisation.yml
```

After adding your repo and refreshing, your playbooks will appear in the CrimsonCFG UI under the appropriate categories.

## Usage

1. **Start the Application**: Run `