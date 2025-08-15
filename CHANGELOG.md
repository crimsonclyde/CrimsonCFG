# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2025-08-14

### Added
- New SSH management tab with comprehensive SSH key and host management
- SSH key creation with passphrase validation against haveibeenpwned database
- SSH key deletion functionality
- SSH key listing in card view format
- SSH host entry management (create/update/delete) for .ssh/config
- SSH host listing in card view format

### Changed
- Moved "Logs" tab to the end of the interface
- Moved playbooks: super-upgrade and login-upgrade-check to essentials folder

### Deprecated
- SSH keys in local.yml

### Removed

### Fixed
- "Install selected" playbooks now correctly switches to logs tab instead of system tab

### Security
- Removed SSH key fields from local.yml
- No more private keys stored in insecure settings files


## [0.2.2] - 2025-08-13

### Added
- Changelog file for better project documentation
- System tab with comprehensive system information display
- Super-Upgrade functionality integrated into UI
- Quick-Update functionality integrated into UI
- System Information panel with detailed system metrics
- `super-upgrade.yml` playbook added to main repository
- `login_update-check.yml` playbook added for login update verification

### Changed
- Updated essential file `_ORDER.md` for improved playbook organization

### Deprecated

### Removed
- `gui_config.json` file - no longer necessary due to improved configuration management


### Fixed

### Security

## [0.2.1] - 2025-07-01

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 1984-01-01

### Added
- Initial beta release of CrimsonCFG (OctoRhino)
- GTK3-based GUI application for system configuration management
- Ansible playbook integration and management
- External repository support for custom playbooks
- Authentication system with admin privileges
- Wallpaper management functionality
- System information display
- Debug mode with comprehensive logging
- Version management system
- Update mechanism for the application
- Support for Ubuntu 24.04

### Features
- **Main Interface**: Central dashboard for managing system configurations
- **Playbook Management**: Browse, select, and execute Ansible playbooks
- **External Repositories**: Add custom playbook repositories via Git URLs
- **System Customization**: GNOME theme and wallpaper management
- **Administrative Tools**: User management and system administration features
- **Logging System**: Comprehensive logging located in `/var/log/CrimsonCFG/`
- **Debug Mode**: Enhanced debugging capabilities with `--debug` flag

### Technical Details
- **Platform**: GTK3 application for GNOME
- **Language**: Python with YAML and Shell integration
- **Backend**: Ansible-based automation
- **Installation**: Microsoft Intune deployment
- **License**: GNU Affero General Public License v3.0

### Known Issues
- Updater functionality needs further testing and improvements
- Wallpaper manager: Visual feedback issue when selecting pictures
- Debug messages need formatting improvements
- SSH private key security needs enhancement

### Todo
- Secure SSH private key implementation
- Fix debug message formatting (`[Debug] Filename - Group - Message`)
- Improve updater reliability
- Enhance wallpaper manager visual feedback

---

## Version History

- **0.2.2**: Major UI enhancements with System tab, upgrade functionality, and improved configuration management
- **0.2.1**: Previous version (details lost in time and space)
- **0.2.0**: Initial beta release with core functionality
- **Future versions**: Will be documented here as they are released

## Contributing

When contributing to this project, please update this changelog with any significant changes, following the format above.

## Notes

- This project is currently in **early beta** status
- Use at your own risk - no warranty provided
- See [LICENSE](LICENSE) file for complete terms
- For installation instructions, see the [README](README.md)
