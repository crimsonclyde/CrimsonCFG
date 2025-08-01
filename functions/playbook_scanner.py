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
        self.playbook_dirs = [
            "playbooks/apps",
            "playbooks/customisation", 
            "playbooks/basics",
            "playbooks/security"
        ]
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
        
        for dir_path in self.playbook_dirs:
            category = dir_path.split("/", 1)[1].capitalize()
            playbooks = []
            
            # Always scan built-in playbooks first
            built_in_path = self.base_dir / dir_path
            if built_in_path.exists():
                if self.debug:
                    print(f"Scanning built-in playbooks in {built_in_path}")
                for yml_file in built_in_path.glob("*.yml"):
                    meta = self.parse_metadata(yml_file, rel_base=self.base_dir, is_external=False)
                    if meta:
                        playbooks.append(meta)
                        if self.debug:
                            print(f"Found built-in playbook: {meta['name']} in {category}")
                    else:
                        if self.debug:
                            print(f"Skipping built-in {yml_file.name} - no valid metadata")
            
            # Then scan external playbooks for apps and customisation if external repo is set
            if self.external_repo_path and ("apps" in dir_path or "customisation" in dir_path):
                subdir = dir_path.split("/", 1)[1]
                external_path = self.external_repo_path / "playbooks" / subdir
                if external_path.exists():
                    if self.debug:
                        print(f"Scanning external playbooks in {external_path}")
                    for yml_file in external_path.glob("*.yml"):
                        meta = self.parse_metadata(yml_file, rel_base=self.external_repo_path, is_external=True)
                        if meta:
                            playbooks.append(meta)
                            if self.debug:
                                print(f"Found external playbook: {meta['name']} in {category}")
                        else:
                            if self.debug:
                                print(f"Skipping external {yml_file.name} - no valid metadata")
                else:
                    if self.debug:
                        print(f"Warning: External directory {external_path} does not exist")
            
            if playbooks:
                all_playbooks[category] = {
                    "description": f"{category} applications and configurations",
                    "playbooks": playbooks
                }
        
        return {"categories": all_playbooks}
        
    def generate_config(self, output_path: str = "", external_repo_path: str = None) -> bool:
        """Generate gui_config.json from scanned playbooks, supporting external repo."""
        try:
            import os
            import json
            from pathlib import Path
            if not output_path:
                config_dir = Path.home() / ".config/com.crimson.cfg"
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
            print(f"Generated {output_path} with {len(config['categories'])} categories")
            return True
        except Exception as e:
            print(f"Error generating config: {e}")
            return False

def main():
    """Main function for standalone execution."""
    scanner = PlaybookScanner()
    success = scanner.generate_config()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 