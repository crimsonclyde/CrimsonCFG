# Functions Directory

This directory contains utility functions and scripts for CrimsonCFG.

## Files

- **playbook_scanner.py** - Main scanner that discovers playbooks and generates GUI configuration
- **test_scanner.py** - Test script to verify the scanner works correctly

## Usage

### Testing the Scanner

```bash
python3 functions/test_scanner.py
```

### Manual Config Generation

```bash
python3 functions/playbook_scanner.py
```

## Integration

The scanner is automatically integrated into the CrimsonCFG UI and runs after successful sudo authentication.
