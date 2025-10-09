#!/usr/bin/env python3

# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Script to sort all label files in descending order by key.
This ensures consistent ordering across all language files.
"""

import sys
import re
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    current_dir = Path(__file__).parent
    return current_dir.parent

def read_labels_file(file_path):
    """Read a labels file and extract the dictionary content"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find the dictionary definition
    dict_match = re.search(r'(labels_\w+)\s*=\s*\{([^}]*)\}', content, re.DOTALL)
    if not dict_match:
        raise ValueError(f"Could not find labels dictionary in {file_path}")

    dict_name = dict_match.group(1)
    dict_content = dict_match.group(2)

    # Extract key-value pairs
    labels_dict = {}
    for line in dict_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Match key-value pairs: "key": "value",
        match = re.match(r'"([^"]+)":\s*"([^"]*)"', line)
        if match:
            key, value = match.groups()
            labels_dict[key] = value

    return dict_name, labels_dict, content

def write_labels_file(file_path, dict_name, labels_dict, original_content):
    """Write the sorted labels dictionary back to file"""
    # Sort keys in descending order
    sorted_keys = sorted(labels_dict.keys(), reverse=True)

    # Build the new dictionary content
    dict_lines = []
    for key in sorted_keys:
        value = labels_dict[key]
        dict_lines.append(f'    "{key}": "{value}",')

    # Remove trailing comma from last line
    if dict_lines:
        dict_lines[-1] = dict_lines[-1].rstrip(',')

    new_dict_content = '\r\n'.join(dict_lines)

    # Replace the dictionary in the original content
    new_content = re.sub(
        r'(labels_\w+\s*=\s*\{)[^}]*(\})',
        f'\\1\r\n{new_dict_content}\r\n\\2',
        original_content,
        flags=re.DOTALL
    )

    # Write back to file with consistent line endings
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        file.write(new_content)

def sort_labels_files():
    """Sort all labels files in the project"""
    project_root = get_project_root()
    l18n_dir = project_root / 'src' / 'l18n'

    if not l18n_dir.exists():
        print(f"Error: l18n directory not found at {l18n_dir}")
        return False

    # Find all labels files
    labels_files = list(l18n_dir.glob('labels_*.py'))

    if not labels_files:
        print(f"Error: No labels_*.py files found in {l18n_dir}")
        return False

    print(f"Found {len(labels_files)} labels files to sort:")

    for labels_file in labels_files:
        try:
            print(f"  Processing {labels_file.name}...")

            # Read and parse the file
            dict_name, labels_dict, original_content = read_labels_file(labels_file)

            print(f"    Found {len(labels_dict)} labels in {dict_name}")

            # Check if already sorted
            current_keys = list(labels_dict.keys())
            sorted_keys = sorted(current_keys, reverse=True)

            if current_keys == sorted_keys:
                print(f"    ✅ {labels_file.name} is already sorted in descending order")
            else:
                # Sort and write back
                write_labels_file(labels_file, dict_name, labels_dict, original_content)
                print(f"    ✅ {labels_file.name} sorted successfully ({len(labels_dict)} keys)")

        except Exception as e:
            print(f"    ❌ Error processing {labels_file.name}: {e}")
            return False

    print("\n🎉 All labels files have been sorted in descending order!")
    return True

def main():
    """Main entry point"""
    print("🔄 Sorting labels files in descending order...\n")

    try:
        success = sort_labels_files()
        if success:
            print("\n✅ Labels sorting completed successfully!")
            print("\n💡 You can now run the tests to verify the ordering:")
            print("   python -m pytest tests/unit/l18n/test_labels.py::LabelsTestCase::test_ordering")
        else:
            print("\n❌ Labels sorting failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()