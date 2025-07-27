# CrimsonCFG - System Configuration Manager

A modern, user-friendly GUI application for managing system configuration and application installation using Ansible playbooks.

![Main Window Screenshot](/files/screenshots/com.crimson.cfg_main.png)

> **Note:**  
> CrimsonCFG is currently in early beta. You may encounter bugs or incomplete features.
> 
> **Disclaimer:**  
> This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**. See the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) for more details.
> 
> Use at your own risk!


## 🚀 Quick Start

### Installation

Run as your normal user:

```bash
cd ~ && wget https://github.com/crimsonclyde/CrimsonCFG/raw/main/setup.sh -O setup.sh && chmod +x setup.sh && bash setup.sh
```

### Uninstall

```bash
cd ~ && sudo chmod +x /opt/CrimsonCFG/uninstall/uninstall.sh && sudo bash /opt/CrimsonCFG/uninstall/uninstall.sh
```

### Update

```bash
cd /opt/CrimsonCFG/ && sudo git pull
```

### Debug

1. Open`~/.config/com.crimson.cfg/local.yml`
2. Set debug to 1
3. Start CrimsonCFG in a terminal

  ```bash
  cd /opt/CrimsonCFG && python3 crimson.cfg.main.py
  ```

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

## ⚙️ Configuration Structure

CrimsonCFG uses a two-tier configuration system:

### Local Configuration (`~/.config/com.crimson.cfg/local.yml`)

Contains user-modifiable settings that override global defaults:

```yaml
# User Configuration (instantly applied)
user: "your_username"
user_home: "/home/your_username"
git_username: "your_git_username"
git_email: "your_email@example.com"

# Application Configuration (save required)
working_directory: "/opt/CrimsonCFG"
background_image: "/path/to/background.png"
background_color: "#181a20"

# Package Lists
apt_packages:
  - firefox
  - vlc
snap_packages:
  - spotify

# Application Branding
app_name: "MyCompanyCFG"
app_subtitle: "Custom Configuration Manager"
app_logo: "/path/to/logo.png"

# Playbook-specific Settings
chromium_homepage_url: "https://example.com"
ssh_private_key_name: "id_rsa"
ssh_private_key_content: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  ...
  -----END OPENSSH PRIVATE KEY-----
ssh_public_key_name: "id_rsa.pub"
ssh_public_key_content: "ssh-rsa ..."
ssh_config_content: |
  Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
```

### Configuration Priority

1. Local settings (`~/.config/com.crimson.cfg/local.yml`) override global settings
2. Changes made through the UI are saved to the user's local.yml
3. The application can be installed in `/opt/` without permission issues

## 🔗 External Playbook Repository

CrimsonCFG allows you to use your own external repository for custom and apps playbooks. This lets you keep your personal or organization-specific playbooks separate from the built-in ones.

### How to Add an External Repository

1. **Go to the Administration tab in the CrimsonCFG UI.**
2. **Open the 'External Playbooks' tab.**
3. **Paste the URL of your Git repository** (e.g., `https://github.com/yourusername/your-playbooks-repo.git`) into the field provided.
4. **Click 'Refresh Playbooks'** to clone or update the repository and load your playbooks.

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

### Example

```text
my-playbooks-repo/
└── playbooks/
    ├── apps/
    │   └── my_app.yml
    └── customisation/
        └── my_customisation.yml
```

After adding your repo and refreshing, your playbooks will appear in the CrimsonCFG UI under the appropriate categories.

## 🎯 Usage

### Main Tab

- **Select Categories**: Choose from Basics, Apps, Customisation, or Security
- **Browse Playbooks**: View available playbooks with descriptions and requirements
- **Select Playbooks**: Choose which playbooks to install
- **Install**: Run the selected playbooks with Ansible

### Configuration Tab

- **User Settings**: Configure user information, Git credentials, and avatar
- **Application Settings**: Set working directory, background image, and colors
- **Browser Settings**: Configure Chromium homepage (applied when Chromium playbook runs)
- **SSH Settings**: Configure SSH keys and config (applied when SSH playbooks run)
- **Gnome Settings**: Configure theme and background (applied when Gnome playbook runs)

### Administration Tab

- **External Repositories**: Add and manage custom playbook repositories
- **System Administration**: Advanced system management features

### Logs Tab

- **Real-time Logs**: View installation progress and debug information
- **Debug Controls**: Enable/disable debug mode and manage logs
- **Copy Logs**: Copy log content to clipboard for troubleshooting

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