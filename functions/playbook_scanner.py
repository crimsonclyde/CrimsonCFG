#!/usr/bin/env python3
"""
CrimsonCFG Playbook Scanner
Scans playbook directories and generates gui_config.json from metadata comments.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional

class PlaybookScanner:
    def __init__(self, base_dir: str = ".", external_repo_path: str = None, debug: bool = False):
        self.base_dir = Path(base_dir)
        self.external_repo_path = Path(external_repo_path) if external_repo_path else None
        self.debug = debug
        
    def parse_metadata(self, filepath: Path, rel_base: Path = None, is_external: bool = False) -> Optional[Dict]:
        """Parse CrimsonCFG metadata comments from a playbook file."""
        if rel_base is None:
            rel_base = self.base_dir
        meta = {
            "name": None,
            "description": None, 
            "essential": False,
            "path": str(filepath.relative_to(rel_base)),
            "source": "External" if is_external else "Built-in"
        }
        # Only set for essential playbooks
        essential_order = None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 10:  # Only scan first 10 lines
                        break
                    if not line.startswith('#'):
                        break
                    line = line.strip()
                    if "CrimsonCFG-Name:" in line:
                        meta["name"] = line.split(":", 1)[1].strip()
                    elif "CrimsonCFG-Description:" in line:
                        meta["description"] = line.split(":", 1)[1].strip()
                    elif "CrimsonCFG-Essential:" in line:
                        value = line.split(":", 1)[1].strip().lower()
                        meta["essential"] = value == "true"
                    elif "CrimsonCFG-Essential-Order:" in line:
                        try:
                            essential_order = int(line.split(":", 1)[1].strip())
                        except Exception:
                            essential_order = None
                    elif "CrimsonCFG-RequiredVars:" in line:
                        value = line.split(":", 1)[1].strip().lower()
                        meta["required_vars"] = value == "true"
            if "required_vars" not in meta:
                meta["required_vars"] = False
            if meta["essential"] and essential_order is not None:
                meta["essential_order"] = essential_order
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
        # Only return if we have at least a name
        return meta if meta["name"] else None
        
    def scan_playbooks(self) -> Dict:
        """Scan all playbook directories and build configuration."""
        all_playbooks = {}
        
        # Scan all subfolders in playbooks directory (both built-in and external)
        self._scan_playbook_directories(all_playbooks)
        
        # Scan department playbooks
        self._scan_department_playbooks(all_playbooks)
        
        return {"categories": all_playbooks}
    
    def _scan_playbook_directories(self, all_playbooks: Dict):
        """Scan all subfolders in playbooks directory to create categories dynamically."""
        # Get all subfolders in built-in playbooks directory
        built_in_playbooks_dir = self.base_dir / "playbooks"
        if built_in_playbooks_dir.exists():
            for subdir in built_in_playbooks_dir.iterdir():
                if subdir.is_dir() and subdir.name != "departments":  # Skip departments, handled separately
                    category = subdir.name.capitalize()
                    playbooks = []
                    
                    if self.debug:
                        print(f"Scanning built-in playbooks in {subdir}")
                    
                    for yml_file in subdir.glob("*.yml"):
                        meta = self.parse_metadata(yml_file, rel_base=self.base_dir, is_external=False)
                        if meta:
                            playbooks.append(meta)
                            if self.debug:
                                print(f"App: Found built-in playbook: {meta['name']} in {category}")
                        else:
                            if self.debug:
                                print(f"App: Skipping built-in {yml_file.name} - no valid metadata")
                    
                    if playbooks:
                        all_playbooks[category] = {
                            "description": f"{category} applications and configurations",
                            "playbooks": playbooks
                        }
        
        # Scan external repository playbooks
        if self.external_repo_path:
            external_playbooks_dir = self.external_repo_path / "playbooks"
            if external_playbooks_dir.exists():
                for subdir in external_playbooks_dir.iterdir():
                    if subdir.is_dir() and subdir.name != "departments":  # Skip departments, handled separately
                        category = subdir.name.capitalize()
                        playbooks = []
                        
                        if self.debug:
                            print(f"Scanning external playbooks in {subdir}")
                        
                        for yml_file in subdir.glob("*.yml"):
                            meta = self.parse_metadata(yml_file, rel_base=self.external_repo_path, is_external=True)
                            if meta:
                                playbooks.append(meta)
                                if self.debug:
                                    print(f"App: Found external playbook: {meta['name']} in {category}")
                            else:
                                if self.debug:
                                    print(f"App: Skipping external {yml_file.name} - no valid metadata")
                        
                        # Merge with existing category or create new one
                        if playbooks:
                            if category in all_playbooks:
                                # Merge with existing built-in playbooks
                                all_playbooks[category]["playbooks"].extend(playbooks)
                                if self.debug:
                                    print(f"App: Merged {len(playbooks)} external playbooks into existing {category} category")
                            else:
                                # Create new category
                                all_playbooks[category] = {
                                    "description": f"{category} applications and configurations",
                                    "playbooks": playbooks
                                }
    
    def _scan_department_playbooks(self, all_playbooks: Dict):
        """Scan department playbooks from both built-in and external repositories."""
        # Scan built-in department playbooks
        built_in_dept_path = self.base_dir / "playbooks" / "departments"
        if built_in_dept_path.exists():
            if self.debug:
                print(f"Scanning built-in department playbooks in {built_in_dept_path}")
            self._scan_department_directory(built_in_dept_path, all_playbooks, is_external=False)
        elif self.debug:
            print(f"Built-in department path does not exist: {built_in_dept_path}")
        
        # Scan external department playbooks if external repo is set (deployment setup)
        if self.external_repo_path:
            external_dept_path = self.external_repo_path / "playbooks" / "departments"
            if self.debug:
                print(f"Checking external repository path: {self.external_repo_path}")
                print(f"Checking external department path: {external_dept_path}")
                print(f"External department path exists: {external_dept_path.exists()}")
            if external_dept_path.exists():
                if self.debug:
                    print(f"Scanning external department playbooks in {external_dept_path}")
                self._scan_department_directory(external_dept_path, all_playbooks, is_external=True)
            elif self.debug:
                print(f"External department path does not exist: {external_dept_path}")
                # List contents of external repo to help debug
                if self.external_repo_path.exists():
                    print(f"External repo contents: {list(self.external_repo_path.iterdir())}")
                    playbooks_dir = self.external_repo_path / "playbooks"
                    if playbooks_dir.exists():
                        print(f"Playbooks directory contents: {list(playbooks_dir.iterdir())}")
        elif self.debug:
            print("No external repository path configured")
    
    def _scan_department_directory(self, dept_path: Path, all_playbooks: Dict, is_external: bool):
        """Scan a department directory and add playbooks to the appropriate categories."""
        rel_base = self.external_repo_path if is_external else self.base_dir
        
        for dept_dir in dept_path.iterdir():
            if dept_dir.is_dir():
                dept_name = dept_dir.name.capitalize()
                category_name = f"Dep: {dept_name}"
                
                if category_name not in all_playbooks:
                    all_playbooks[category_name] = {
                        "description": f"{dept_name} department specific playbooks",
                        "playbooks": []
                    }
                
                # Scan playbooks in this department directory
                for yml_file in dept_dir.glob("*.yml"):
                    meta = self.parse_metadata(yml_file, rel_base=rel_base, is_external=is_external)
                    if meta:
                        all_playbooks[category_name]["playbooks"].append(meta)
                        if self.debug:
                            print(f"App: Found department playbook: {meta['name']} in {category_name}")
                    else:
                        if self.debug:
                            print(f"App: Skipping department {yml_file.name} - no valid metadata")
    
    def generate_config(self, output_path: str = "", external_repo_path: str = None) -> bool:
        """Generate gui_config.json from scanned playbooks, supporting external repo."""
        try:
            import os
            import json
            from pathlib import Path
            if not output_path:
                config_dir = Path.home() / ".config/com.mdm.manager.cfg"
                if not config_dir.exists():
                    config_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(config_dir / "gui_config.json")
            else:
                if output_path.startswith("conf/"):
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Use external repo if provided
            if external_repo_path:
                scanner = PlaybookScanner(self.base_dir, external_repo_path)
            else:
                scanner = self
            config = scanner.scan_playbooks()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            if self.debug:
                print(f"App: Generated {output_path} with {len(config['categories'])} categories")
            return True
        except Exception as e:
            print(f"App:Error generating config: {e}")
            return False

def main():
    """Main function for standalone execution."""
    scanner = PlaybookScanner()
    success = scanner.generate_config()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 