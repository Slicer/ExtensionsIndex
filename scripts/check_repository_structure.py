#!/usr/bin/env python

"""
Python script for validating repository file structure.
Checks for unexpected files and directories in the extension repository.
"""

import argparse
import sys
from pathlib import Path


def check_filenames():
    """Check for unexpected files in the repository."""
    # Get the repository root directory (parent of scripts directory)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    # Define allowed directories
    allowed_directories = {
        '.circleci',
        '.idea',
        '.github',
        '.git',
        'ARCHIVE',
        'scripts',
        'schemas',
        '.venv',          # Python virtual environment
        'venv',           # Alternative venv name
        '__pycache__',    # Python cache
        '.pytest_cache'   # Pytest cache
    }

    # Define allowed files (exact names)
    allowed_files = {
        '.pre-commit-config.yaml',
        '.prettierrc.js',
        '.git-blame-ignore-revs',
        'README.md'
    }

    # Define allowed file patterns (extensions)
    allowed_extensions = {
        '.json'
    }

    def is_file_allowed(file_path):
        """Check if a file is allowed based on name or extension."""
        # Check exact filename
        if file_path.name in allowed_files:
            return True

        # Check file extension
        if file_path.suffix in allowed_extensions:
            return True

        return False

    unexpected_files = []

    # Walk through all files and directories in the root
    for item in root_dir.iterdir():
        if item.is_dir():
            # Check if directory is allowed
            if item.name not in allowed_directories:
                unexpected_files.append(str(item.relative_to(root_dir)))
        elif item.is_file():
            # Check if file is allowed
            if not is_file_allowed(item):
                unexpected_files.append(str(item.relative_to(root_dir)))

    return unexpected_files


def main():
    parser = argparse.ArgumentParser(
        description='Validate repository file structure.')
    args = parser.parse_args()

    unexpected_files = check_filenames()

    print("# Check repository structure\n")

    print(f"Total unexpected files/directories found: {len(unexpected_files)}\n")

    if not unexpected_files:
        print(":white_check_mark: **Repository structure validation passed!**\n")
        print("All files and directories in the repository follow the expected structure.")
    else:
        print(":x: **Repository structure issues found**\n")
        print("The following unexpected files or directories were found:\n")
        for unexpected_file in unexpected_files:
            print(f"- :x: `{unexpected_file}`")

    # Exit with error code if issues found
    sys.exit(len(unexpected_files))


if __name__ == "__main__":
    main()
