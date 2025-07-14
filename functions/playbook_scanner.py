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
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.playbook_dirs = [
            "playbooks/apps",
            "playbooks/customisation", 
            "playbooks/basics"
        ]
        
    def parse_metadata(self, filepath: Path) -> Optional[Dict]:
        """Parse CrimsonCFG metadata comments from a playbook file."""
        meta = {
            "name": None,
            "description": None, 
            "essential": False,
            "path": str(filepath.relative_to(self.base_dir))
        }
        
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
                        
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
            
        # Only return if we have at least a name
        return meta if meta["name"] else None
        
    def scan_playbooks(self) -> Dict:
        """Scan all playbook directories and build configuration."""
        all_playbooks = {}
        
        for dir_path in self.playbook_dirs:
            full_path = self.base_dir / dir_path
            if not full_path.exists():
                print(f"Warning: Directory {dir_path} does not exist")
                continue
                
            category = full_path.name.capitalize()
            playbooks = []
            
            for yml_file in full_path.glob("*.yml"):
                meta = self.parse_metadata(yml_file)
                if meta:
                    playbooks.append(meta)
                    print(f"Found playbook: {meta['name']} in {category}")
                else:
                    print(f"Skipping {yml_file.name} - no valid metadata")
                    
            if playbooks:
                all_playbooks[category] = {
                    "description": f"{category} applications and configurations",
                    "playbooks": playbooks
                }
                
        return {"categories": all_playbooks}
        
    def generate_config(self, output_path: str = "conf/gui_config.json") -> bool:
        """Generate gui_config.json from scanned playbooks."""
        try:
            # Ensure conf directory exists
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            config = self.scan_playbooks()
            
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