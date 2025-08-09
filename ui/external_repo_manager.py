import os
import threading
import subprocess
import getpass
from ruamel.yaml import YAML

CONFIG_DIR = os.path.expanduser(os.path.join(os.path.expanduser("~"), ".config/com.mdm.manager.cfg"))
LOCAL_YML_PATH = os.path.join(CONFIG_DIR, "local.yml")
EXTERNAL_REPO_DIR = "/opt/MDM-Manager/external_src"

def get_local_yml_path():
    return LOCAL_YML_PATH

def get_external_repo_url():
    """Get the external playbook repo URL from local.yml."""
    yaml = YAML()
    try:
        with open(LOCAL_YML_PATH, 'r') as f:
            config = yaml.load(f) or {}
        return config.get('external_playbook_repo_url', None)
    except Exception:
        return None

def set_external_repo_url(url):
    """Set the external playbook repo URL in local.yml."""
    yaml = YAML()
    try:
        with open(LOCAL_YML_PATH, 'r') as f:
            config = yaml.load(f) or {}
    except Exception:
        config = {}
    config['external_playbook_repo_url'] = url
    with open(LOCAL_YML_PATH, 'w') as f:
        yaml.dump(config, f)

def get_external_playbooks_path():
    """Return the local path where external playbooks are stored."""
    return EXTERNAL_REPO_DIR

def ensure_external_repo_dir(sudo_password=None):
    import subprocess
    import getpass
    if not os.path.exists(EXTERNAL_REPO_DIR):
        try:
            os.makedirs(EXTERNAL_REPO_DIR, exist_ok=True)
        except PermissionError:
            # Try to create with sudo using provided password
            try:
                if sudo_password:
                    # Use the authenticated password
                    subprocess.run(['sudo', '-k', '-S', 'mkdir', '-p', EXTERNAL_REPO_DIR], 
                                 input=f"{sudo_password}\n", text=True, check=True)
                    subprocess.run(['sudo', '-k', '-S', 'chown', f'{getpass.getuser()}:{getpass.getuser()}', EXTERNAL_REPO_DIR], 
                                 input=f"{sudo_password}\n", text=True, check=True)
                else:
                    # Fallback to direct sudo (will prompt)
                    subprocess.run(['sudo', 'mkdir', '-p', EXTERNAL_REPO_DIR], check=True)
                    subprocess.run(['sudo', 'chown', f'{getpass.getuser()}:{getpass.getuser()}', EXTERNAL_REPO_DIR], check=True)
            except Exception as e:
                print(f"Failed to create {EXTERNAL_REPO_DIR} with sudo: {e}")
                return False
    return True

def _clone_or_pull_repo(repo_url, sudo_password=None):
    if not repo_url:
        return True
    if not ensure_external_repo_dir(sudo_password):
        print(f"Cannot clone external repo: insufficient permissions for {EXTERNAL_REPO_DIR}")
        return False
    
    try:
        if not os.path.exists(EXTERNAL_REPO_DIR) or not os.listdir(EXTERNAL_REPO_DIR):
            # Clone the repository
            result = subprocess.run(['git', 'clone', repo_url, EXTERNAL_REPO_DIR], 
                                  capture_output=True, text=True, check=True)
            print(f"Successfully cloned repository: {repo_url}")
            return True
        else:
            # Pull latest changes
            result = subprocess.run(['git', '-C', EXTERNAL_REPO_DIR, 'pull'], 
                                  capture_output=True, text=True, check=True)
            print(f"Successfully pulled latest changes from repository")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        print(f"Git stdout: {e.stdout}")
        print(f"Git stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error during git operation: {e}")
        return False

def update_external_repo_async(sudo_password=None):
    """Clone or pull the external repo asynchronously."""
    repo_url = get_external_repo_url()
    if not repo_url:
        return
    thread = threading.Thread(target=_clone_or_pull_repo, args=(repo_url, sudo_password))
    thread.daemon = True
    thread.start()

def update_external_repo_sync(sudo_password=None):
    """Clone or pull the external repo synchronously."""
    repo_url = get_external_repo_url()
    if not repo_url:
        return True
    return _clone_or_pull_repo(repo_url, sudo_password) 