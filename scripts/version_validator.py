#!/usr/bin/env python3
"""
Version Validator Script
This script validates that all components have consistent version information.
"""

from pathlib import Path


def read_version():
    """Read version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if not version_file.exists():
        raise FileNotFoundError(f"VERSION file not found at {version_file}")

    with open(version_file, 'r') as f:
        version = f.read().strip()

    return version


def validate_script_version(version):
    """Validate version in the shell script."""
    script_path = (Path(__file__).parent.parent / "build" /
                   "linux_aio_perfcheck.sh")

    if not script_path.exists():
        print(f"❌ Script not found at {script_path}")
        return False

    with open(script_path, 'r') as f:
        content = f.read()

    # Check if version is present and matches
    if f'version: {version}' not in content:
        print(f"❌ Script version mismatch. Expected: {version}")
        return False

    if f'version {version}' not in content:
        print(f"❌ Script --version output mismatch. Expected: {version}")
        return False

    print(f"✓ Script version validated: {version}")
    return True


def validate_webapp_version(version):
    """Validate version in webapp components."""
    webapp_path = Path(__file__).parent.parent / "webapp"

    # Files to validate
    files_to_validate = [
        "domains/htmlgeneration/html_generator.py",
        "domains/webapp/execution/linuxaioperf.py",
        "domains/htmlgeneration/template.html"
    ]

    all_valid = True

    for file_path in files_to_validate:
        full_path = webapp_path / file_path
        if not full_path.exists():
            print(f"❌ File not found at {full_path}")
            all_valid = False
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        # Check if version is present
        if version not in content:
            print(f"❌ Version {version} not found in {file_path}")
            all_valid = False
        else:
            print(f"✓ {file_path} version validated: {version}")

    return all_valid


def main():
    """Main function to validate version consistency."""
    try:
        version = read_version()
        print(f"Validating version {version} across all components...")

        script_valid = validate_script_version(version)
        webapp_valid = validate_webapp_version(version)

        if script_valid and webapp_valid:
            print(f"\n✅ All components have consistent version: {version}")
            return 0
        else:
            print("\n❌ Version validation failed!")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
