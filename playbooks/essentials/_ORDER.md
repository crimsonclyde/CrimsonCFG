# Running Order for Essential Playbooks


|Task No|Playbook|Description|
|---|---|---|
|1| update_upgrade.yml | Updates pkg cache and upgrade apt/snap |
|2| timeshift.yml| Installs timeshift + UI and creates a basic first snapshot |
|3| basic_apps.yml | Installs basic apps not entire applications more helpers |
|4| ufw.yml | Activates UFW with no rules so far |
|5| tailscale.yml | Install our main tailscale VPN|
|6| super-upgrade.yml | Installs the super-upgrade feature |
|7| login-update-check.yml | Runs a full system upgrade on login |
|8|||
|9|||
|10| chromium.yml | Installs chromium, profiles, and default extensions |
|11| bitwarden.yml | Install bitwarden our companies personal password manager |
|12|||