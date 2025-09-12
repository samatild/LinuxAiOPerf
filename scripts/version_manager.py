#!/usr/bin/env python3
"""
Unified Version Manager
This script handles all version management tasks: check, update, validate.
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


def write_version(version):
    """Write version to VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    with open(version_file, 'w') as f:
        f.write(version)
    print(f"✓ Updated VERSION file to: {version}")


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
        (r'# version: (?:VERSION_PLACEHOLDER|\d+\.\d+\.\d+)',
         f'# version: {version}'),
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


def check_versions(version):
    """Check if all components have the correct version."""
    print(f"Checking version consistency for: {version}")
    print("=" * 50)

    all_correct = True

    # Check script
    script_path = (Path(__file__).parent.parent / "build" /
                   "linux_aio_perfcheck.sh")

    if script_path.exists():
        with open(script_path, 'r') as f:
            content = f.read()

        if (f'version: {version}' not in content or
                f'version {version}' not in content):
            print(f"❌ Script version mismatch. Expected: {version}")
            all_correct = False
        else:
            print(f"✓ Script version correct: {version}")
    else:
        print(f"❌ Script not found at {script_path}")
        all_correct = False

    # Check webapp files
    webapp_path = Path(__file__).parent.parent / "webapp"
    files_to_check = [
        "domains/htmlgeneration/html_generator.py",
        "domains/webapp/execution/linuxaioperf.py",
        "domains/htmlgeneration/template.html"
    ]

    for file_path in files_to_check:
        full_path = webapp_path / file_path
        if not full_path.exists():
            print(f"❌ File not found at {full_path}")
            all_correct = False
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        if version not in content:
            print(f"❌ Version {version} not found in {file_path}")
            all_correct = False
        else:
            print(f"✓ {file_path} version correct: {version}")

    print("=" * 50)
    return all_correct


def get_new_version():
    """Ask user for new version."""
    current_version = read_version()
    print(f"Current version: {current_version}")
    while True:
        new_version = input(
            "Enter new version (or press Enter to keep current): "
        ).strip()

        if not new_version:
            return current_version

        # Basic version format validation
        if re.match(r'^\d+\.\d+\.\d+$', new_version):
            return new_version
        else:
            print("Invalid format. Please use format: X.Y.Z (e.g., 1.43.1)")


def show_menu():
    """Show the main menu."""
    print("\n" + "=" * 50)
    print("           LinuxAiOPerf Version Manager")
    print("=" * 50)
    print("1. Check current version status")
    print("2. Update version and inject into all components")
    print("3. Exit")
    print("=" * 50)


def main():
    """Main function."""
    try:
        while True:
            show_menu()
            choice = input("Choose an option (1-3): ").strip()

            if choice == "1":
                # Check current version
                current_version = read_version()
                check_versions(current_version)

            elif choice == "2":
                # Update version and inject
                new_version = get_new_version()
                write_version(new_version)
                print(f"Injecting version {new_version} into components...")
                inject_script_version(new_version)
                inject_webapp_version(new_version)
                print("✓ Version update and injection completed!")

            elif choice == "3":
                print("Goodbye!")
                break

            else:            
                print("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
