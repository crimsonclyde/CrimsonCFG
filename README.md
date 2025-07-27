# CrimsonCFG - System Configuration Manager

![Main Window Screenshot](/files/screenshots/com.crimson.cfg_main.png)

> **Note:**  
> CrimsonCFG is currently in early beta. You may encounter bugs or incomplete features.
> 
> **Disclaimer:**  
> This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**. See the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) for more details.
> 
> Use at your own risk!

## Exordium

CrimsonCFG is a powerful, user-friendly system configuration manager designed to help you get your system up and running quickly—especially after a fresh install or on new machines. With CrimsonCFG, you can prepare your Ansible playbooks in advance and apply them with just a few clicks, automating the setup of essential applications, settings, and customizations in no time. It's ideal for both personal use and managed desktop (MDM) environments, making it easy to standardize and streamline system provisioning across multiple devices.

### Platform

GTK3 application for Gnome. Written with Python, YAML and Shell. Based on Ansible. Made with 🖤 for open source!

### Supported Systems

|OS|Version|
|---|---|
|Ubuntu|22.04|

### Info

This was "written" with the help of Cursor AI. Don't expect nice code - but due to time limitations - and for personal training it's a fun project.  
Don't hate the player - hate the game!

## 🚀 Quick Start

### 📦 Installation

Run as your normal user:

```bash
cd ~ && wget https://github.com/crimsonclyde/CrimsonCFG/raw/main/setup.sh -O setup.sh && chmod +x setup.sh && bash setup.sh
```

### 🗑️ Uninstall

```bash
cd ~ && sudo chmod +x /opt/CrimsonCFG/uninstall/uninstall.sh && sudo bash /opt/CrimsonCFG/uninstall/uninstall.sh
```

### 🔄 Update

```bash
cd /opt/CrimsonCFG/ && sudo git pull
```

### 🐛 Debug

1. Open `~/.config/com.crimson.cfg/local.yml`
2. Set debug to 1
3. Start CrimsonCFG in a terminal

  ```bash
  cd /opt/CrimsonCFG && python3 crimson.cfg.main.py
  ```

## 🔗 External Playbook Repository

CrimsonCFG allows you to use your own external repository for custom and apps playbooks. This lets you keep your personal or organization-specific playbooks separate from the built-in ones.

### How to Add an External Repository

1. **Go to the Administration tab in the CrimsonCFG UI.**
2. **Open the 'External Repository' tab.**
3. **Paste the URL of your Git repository** (e.g., `https://github.com/yourusername/your-playbooks-repo.git`) into the field provided.
4. **Click 'Save External Repository Settings'** to save the URL and clone the repository.
5. **Click 'Refresh Playbooks'** to update the playbook list and load your playbooks.

> **Warning:** Only use repositories you own and trust. Running untrusted playbooks can compromise your system.

### Repository Structure

Your external repository should have the following structure:

```text
playbooks/
  apps/
    your_app_playbook.yml
  customisation/
    your_custom_playbook.yml
```

- Place your application playbooks in `playbooks/apps/`.
- Place your customization playbooks in `playbooks/customisation/`.
- Each playbook should start with CrimsonCFG metadata comments, for example:

```yaml
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
- External playbooks are stored in `/opt/CrimsonCFG/external_src/` and are automatically cloned/pulled when you save the repository URL.

### Example

```text
my-playbooks-repo/
└── playbooks/
    ├── apps/
    │   └── my_app.yml
    └── customisation/
        └── my_customisation.yml
```

After adding your repo and refreshing, your playbooks will appear in the CrimsonCFG UI under the appropriate categories with a "External" source indicator.

### Example Repository

You can use the official CrimsonCFG-Playbooks repository as a boilerplate to get started:

```bash
git clone https://github.com/crimsonclyde/CrimsonCFG-Playbooks.git
```

This repository contains example playbooks that demonstrate the proper structure and metadata format. You can clone it, modify the playbooks to suit your needs, and then use your own repository URL in CrimsonCFG.

## Bugs / Todo / Improve

### 🐛 Bugs

- Main Window "Select None" removes all apps including essential ones  
  Essential apps should only be removed when pressing "Remove essentials" because there is a warning!  
  Rename to "Remove all keep essentials"
- "Deselect" behaves unexpectedly  
  Improve by making double-click on a single app remove it from "Selected playbooks"  
- "Select All" missleading since it selects all from the current choosesn category

### 📝 Todo

- Secure SSH private key
- Fix debug messages  
  `[Debug] Filename - Group - Message`

### 🔧 Improve
  
- Debug Messages  
  Debug messages should be visible in the log window - currently they only appear on CLI

## ✨ Features

- **Modern GTK3 Interface**: Clean, dark-themed UI with Material Design elements
- **Modular Architecture**: Well-organized, maintainable codebase with separate components
- **Ansible Integration**: Uses Ansible playbooks for reliable system configuration
- **Package Management**: Install APT and Snap packages through the GUI
- **Customization**: Configure SSH, pinned applications, and corporate identity
- **User-Specific Configuration**: Local overrides for user-modifiable settings
- **Real-time Logging**: Live installation progress and debugging information
- **External Repository Support**: Use your own custom playbook repositories
- **Tabbed Interface**: Organized into Main, Configuration, Administration, and Logs tabs

## 🏗️ Architecture

CrimsonCFG uses a clean, modular architecture with separate components for different concerns:

### Core Components

- **`main_window.py`**: Core window management and application lifecycle
- **`gui_builder.py`**: GUI construction and tab orchestration
- **`auth_manager.py`**: Authentication and sudo password handling
- **`config_manager.py`**: Configuration file management
- **`installer.py`**: Ansible playbook execution
- **`logger.py`**: Logging functionality
- **`playbook_manager.py`**: Playbook selection and management

### Tab Components

- **`main_tab.py`**: Main playbook selection interface
- **`config_tab.py`**: Configuration editing interface
- **`admin_tab.py`**: Administration and external repository management
- **`logs_tab.py`**: Real-time logging and debug controls

### Utility Components

- **`external_repo_manager.py`**: External repository management

## 🔧 Development

### Project Structure

```text
CrimsonCFG/
├── ui/                     # Modular UI components
│   ├── main_window.py     # Core window management
│   ├── gui_builder.py     # GUI construction & orchestration
│   ├── main_tab.py        # Main playbook selection interface
│   ├── config_tab.py      # Configuration interface
│   ├── admin_tab.py       # Administration interface
│   ├── logs_tab.py        # Logs interface
│   ├── auth_manager.py    # Authentication handling
│   ├── config_manager.py  # Configuration management
│   ├── installer.py       # Installation logic
│   ├── logger.py          # Logging functionality
│   ├── playbook_manager.py # Playbook management
│   └── external_repo_manager.py # External repository management
├── playbooks/             # Ansible playbooks
├── functions/             # Utility functions
├── templates/             # Configuration templates
├── files/                 # Application assets
└── archive/               # Archived legacy files
```

### Key Features

- **Modular Design**: Each component has a single responsibility
- **Clean Architecture**: Clear separation of concerns
- **Maintainable Code**: Well-organized and documented
- **Extensible**: Easy to add new features and tabs

## 📝 License

This project is licensed under the GNU Affero General Public License v3. See the [LICENSE](LICENSE) file for complete terms.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## ⚠️ Disclaimer

**THERE IS NO WARRANTY** for this software or its installation process. The software is provided 'AS IS' without warranty of any kind. The entire risk as to the quality and performance is with you. You assume all responsibility for any damages, data loss, or system issues. No copyright holder or contributor can be held liable for any damages. You are solely responsible for backing up your system before installation. Installation may modify system files and could potentially break your system.