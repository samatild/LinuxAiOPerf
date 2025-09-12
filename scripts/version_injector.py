#!/usr/bin/env python3
"""
Version Injector Script
This script injects version information into various components of the
LinuxAiOPerf project. It reads the version from the VERSION file and
updates placeholders in the codebase.
"""

import re
import sys
from pathlib import Path


def read_version():
    """Read version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if not version_file.exists():
        raise FileNotFoundError(f"VERSION file not found at {version_file}")

    with open(version_file, 'r') as f:
        version = f.read().strip()

    return version


def inject_script_version(version):
    """Inject version into the shell script."""
    script_path = (Path(__file__).parent.parent / "build" /
                   "linux_aio_perfcheck.sh")

    if not script_path.exists():
        print(f"Warning: Script not found at {script_path}")
        return

    with open(script_path, 'r') as f:
        content = f.read()

    # Replace VERSION_PLACEHOLDER or any existing version pattern
    patterns_replacements = [
        # Header comment version
        (r'# version: (?:VERSION_PLACEHOLDER|\d+\.\d+\.\d+)',
         f'# version: {version}'),
        # --version command output
        (r'echo "Linux All-in-One Performance Collector, version '
         r'(?:VERSION_PLACEHOLDER|\d+\.\d+\.\d+)"',
         f'echo "Linux All-in-One Performance Collector, version {version}"')
    ]

    for pattern, replacement in patterns_replacements:
        content = re.sub(pattern, replacement, content)

    with open(script_path, 'w') as f:
        f.write(content)

    print(f"✓ Updated script version to {version}")


def inject_webapp_version(version):
    """Inject version into webapp components."""
    webapp_path = Path(__file__).parent.parent / "webapp"

    # Files to update with their specific patterns
    files_patterns = [
        {
            "file": "domains/htmlgeneration/html_generator.py",
            "patterns": [
                (r'script_version = "(?:VERSION_PLACEHOLDER|\d+\.\d+\.\d+)"',
                 f'script_version = "{version}"')
            ]
        },
        {
            "file": "domains/webapp/execution/linuxaioperf.py",
            "patterns": [
                (r'Version: (?:VERSION_PLACEHOLDER|\d+\.\d+\.\d+)',
                 f'Version: {version}')
            ]
        },
        {
            "file": "domains/htmlgeneration/template.html",
            "patterns": [
                (r'Version: (?:VERSION_PLACEHOLDER|\d+\.\d+\.\d+)',
                 f'Version: {version}')
            ]
        }
    ]

    for file_info in files_patterns:
        file_path = file_info["file"]
        patterns = file_info["patterns"]
        full_path = webapp_path / file_path

        if not full_path.exists():
            print(f"Warning: File not found at {full_path}")
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        # Apply all patterns for this file
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        with open(full_path, 'w') as f:
            f.write(content)

        print(f"✓ Updated {file_path} version to {version}")


def main():
    """Main function to inject version into all components."""
    try:
        version = read_version()
        print(f"Injecting version {version} into components...")

        inject_script_version(version)
        inject_webapp_version(version)

        print("✓ Version injection completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
