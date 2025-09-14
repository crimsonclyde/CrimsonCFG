import os
import threading
import subprocess
import getpass
from ruamel.yaml import YAML

CONFIG_DIR = os.path.expanduser(os.path.join(os.path.expanduser("~"), ".config/com.crimson.cfg"))
LOCAL_YML_PATH = os.path.join(CONFIG_DIR, "local.yml")
EXTERNAL_REPO_DIR = "/opt/CrimsonCFG/external_src"

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
                    # Keep it owned by root for consistency with main repo
                    subprocess.run(['sudo', '-k', '-S', 'chown', 'root:root', EXTERNAL_REPO_DIR], 
                                 input=f"{sudo_password}\n", text=True, check=True)
                    subprocess.run(['sudo', '-k', '-S', 'chmod', '755', EXTERNAL_REPO_DIR], 
                                 input=f"{sudo_password}\n", text=True, check=True)
                else:
                    # Fallback to direct sudo (will prompt)
                    subprocess.run(['sudo', 'mkdir', '-p', EXTERNAL_REPO_DIR], check=True)
                    subprocess.run(['sudo', 'chown', 'root:root', EXTERNAL_REPO_DIR], check=True)
                    subprocess.run(['sudo', 'chmod', '755', EXTERNAL_REPO_DIR], check=True)
            except Exception as e:
                print(f"Failed to create {EXTERNAL_REPO_DIR} with sudo: {e}")
                return False
    return True

def _clone_or_pull_repo(repo_url, sudo_password=None, logger=None):
    if not repo_url:
        return True
    if not ensure_external_repo_dir(sudo_password):
        error_msg = f"Cannot clone external repo: insufficient permissions for {EXTERNAL_REPO_DIR}"
        print(error_msg)
        if logger:
            logger.log_message(error_msg)
        return False
    
    try:
        # Configure git safe directory for external repository
        subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', EXTERNAL_REPO_DIR], 
                      capture_output=True, text=True, timeout=10)
        
        if not os.path.exists(EXTERNAL_REPO_DIR) or not os.listdir(EXTERNAL_REPO_DIR):
            # Clone the repository
            if logger:
                logger.log_message(f"Cloning repository: {repo_url}")
            
            if sudo_password:
                # Use sudo for cloning
                result = subprocess.run(['sudo', '-k', '-S', 'git', 'clone', repo_url, EXTERNAL_REPO_DIR], 
                                      input=f"{sudo_password}\n", capture_output=True, text=True, check=True)
            else:
                # Fallback to direct sudo (will prompt)
                result = subprocess.run(['sudo', 'git', 'clone', repo_url, EXTERNAL_REPO_DIR], 
                                      capture_output=True, text=True, check=True)
            
            success_msg = f"Successfully cloned repository: {repo_url}"
            print(success_msg)
            if logger:
                logger.log_message(success_msg)
                if result.stdout:
                    logger.log_message(f"Clone output: {result.stdout.strip()}")
            return True
        else:
            # Use fetch and hard reset instead of pull to handle conflicts
            if logger:
                logger.log_message("Updating external repository...")
            
            # First, fetch all changes
            if sudo_password:
                fetch_result = subprocess.run(['sudo', '-k', '-S', 'sh', '-c', f'cd {EXTERNAL_REPO_DIR} && git fetch --all'], 
                                            input=f"{sudo_password}\n", capture_output=True, text=True, check=True)
            else:
                fetch_result = subprocess.run(['sudo', 'sh', '-c', f'cd {EXTERNAL_REPO_DIR} && git fetch --all'], 
                                            capture_output=True, text=True, check=True)
            
            if logger and fetch_result.stdout:
                logger.log_message(f"Fetch output: {fetch_result.stdout.strip()}")
            
            # Get current branch name
            if sudo_password:
                branch_result = subprocess.run(['sudo', '-k', '-S', 'sh', '-c', f'cd {EXTERNAL_REPO_DIR} && git rev-parse --abbrev-ref HEAD'], 
                                             input=f"{sudo_password}\n", capture_output=True, text=True, check=True)
            else:
                branch_result = subprocess.run(['sudo', 'sh', '-c', f'cd {EXTERNAL_REPO_DIR} && git rev-parse --abbrev-ref HEAD'], 
                                             capture_output=True, text=True, check=True)
            
            current_branch = branch_result.stdout.strip()
            
            # Hard reset to origin/branch to handle any conflicts
            if sudo_password:
                reset_result = subprocess.run(['sudo', '-k', '-S', 'sh', '-c', f'cd {EXTERNAL_REPO_DIR} && git reset --hard origin/{current_branch}'], 
                                            input=f"{sudo_password}\n", capture_output=True, text=True, check=True)
            else:
                reset_result = subprocess.run(['sudo', 'sh', '-c', f'cd {EXTERNAL_REPO_DIR} && git reset --hard origin/{current_branch}'], 
                                            capture_output=True, text=True, check=True)
            
            success_msg = f"Successfully updated repository to latest changes (branch: {current_branch})"
            print(success_msg)
            if logger:
                logger.log_message(success_msg)
                if reset_result.stdout:
                    logger.log_message(f"Reset output: {reset_result.stdout.strip()}")
            return True
    except subprocess.CalledProcessError as e:
        error_msg = f"Git operation failed: {e}"
        print(error_msg)
        if logger:
            logger.log_message(error_msg)
            if e.stdout:
                logger.log_message(f"Git stdout: {e.stdout}")
            if e.stderr:
                logger.log_message(f"Git stderr: {e.stderr}")
        # Check for specific git safe directory error
        if "dubious ownership" in e.stderr or "unsafe repository" in e.stderr:
            safe_dir_msg = f"Git safe directory issue detected. Try running: git config --global --add safe.directory {EXTERNAL_REPO_DIR}"
            print(safe_dir_msg)
            if logger:
                logger.log_message(safe_dir_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error during git operation: {e}"
        print(error_msg)
        if logger:
            logger.log_message(error_msg)
        return False

def update_external_repo_async(sudo_password=None):
    """Clone or pull the external repo asynchronously."""
    repo_url = get_external_repo_url()
    if not repo_url:
        return
    thread = threading.Thread(target=_clone_or_pull_repo, args=(repo_url, sudo_password))
    thread.daemon = True
    thread.start()

def update_external_repo_sync(sudo_password=None, logger=None):
    """Clone or pull the external repo synchronously."""
    repo_url = get_external_repo_url()
    if not repo_url:
        return True
    
    # Fix permissions on existing external repository if it exists
    if os.path.exists(EXTERNAL_REPO_DIR) and sudo_password:
        try:
            # Ensure proper ownership and permissions
            subprocess.run(['sudo', '-k', '-S', 'chown', '-R', 'root:root', EXTERNAL_REPO_DIR], 
                         input=f"{sudo_password}\n", text=True, check=True)
            subprocess.run(['sudo', '-k', '-S', 'chmod', '-R', '755', EXTERNAL_REPO_DIR], 
                         input=f"{sudo_password}\n", text=True, check=True)
        except Exception as e:
            warning_msg = f"Warning: Could not fix permissions on {EXTERNAL_REPO_DIR}: {e}"
            print(warning_msg)
            if logger:
                logger.log_message(warning_msg)
    
    return _clone_or_pull_repo(repo_url, sudo_password, logger) 