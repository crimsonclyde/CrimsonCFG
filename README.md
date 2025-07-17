# CrimsonCFG

## Exordium
CrimsonCFG is a configuration manager designed for both mobile device management (MDM) and general system automation. It can be used to run Ansible scripts, manage application and system configurations, and is fully customizable. Future editions will support advanced CI (Corporate Identity) changes and allow you to use your own repositories for scripts.

## Features
- Mobile device management (MDM) capabilities
- Run and manage Ansible playbooks with a graphical interface
- Fully customizable configuration and UI
- Corporate Identity (CI) branding and customization
- Designed for extensibility and future integration with custom script repositories

## Installation (Setup)
To setup CrimsonCFG, download and run the setup with this one-liner:

```sh
wget https://github.com/crimsonclyde/CrimsonCFG/raw/main/setup.sh -O install.sh && chmod +x setup.sh && bash setup.sh
```

This will set up all required dependencies and launch the application and starts the installation of CrimsonCFG.

**GitHub Repository:** [https://github.com/crimsonclyde/CrimsonCFG](https://github.com/crimsonclyde/CrimsonCFG)

## Getting Started
After installation, launch the application and follow the on-screen instructions to configure your system or manage devices. You can customize settings, run playbooks, and adjust CI branding from the graphical interface.

## Requirements
- Python 3.7+
- GTK 3
- Ansible
- (Other dependencies are installed automatically by `install.sh`)

## License
See [LICENSE](LICENSE) for details. 