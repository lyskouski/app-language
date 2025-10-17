#!/usr/bin/env python3

# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import sys
import re
import argparse
from pathlib import Path

def extract_labels_from_file(file_path):
    """Extract labels dictionary from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the dictionary definition using regex
        # Pattern matches: variable_name = { ... }
        pattern = r'labels_\w+\s*=\s*\{([^}]+)\}'
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            print(f"Warning: No labels dictionary found in {file_path.name}")
            return {}

        dict_content = match.group(1)
        labels = {}

        # Extract key-value pairs
        # Pattern matches: "key": "value",
        pair_pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
        pairs = re.findall(pair_pattern, dict_content)

        for key, value in pairs:
            # Unescape common escape sequences
            value = value.replace('\\"', '"').replace('\\\\', '\\')
            labels[key] = value

        return labels

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return {}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Export language labels to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python tools\\labels_export.py                    # Export all languages (be,en,ru,uk)
  python tools\\labels_export.py --export en,ru     # Export only English and Russian
  python tools\\labels_export.py --export be        # Export only Belarusian
        '''
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Comma-separated list of languages to export (e.g., en,ru,uk). Default: all languages'
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent  # Go up to project root
    l18n_dir = project_root / 'src' / 'l18n'

    if not l18n_dir.exists():
        print(f"Error: Directory {l18n_dir} does not exist")
        sys.exit(1)

    # Find all labels files
    labels_files = list(l18n_dir.glob('labels_*.py'))

    if not labels_files:
        print(f"No labels_*.py files found in {l18n_dir}")
        return

    # Define available languages and determine which to export
    all_available_languages = ['be', 'en', 'ru', 'uk']

    if args.export:
        # Parse the export argument
        requested_languages = [lang.strip().lower() for lang in args.export.split(',')]

        # Validate requested languages
        invalid_languages = [lang for lang in requested_languages if lang not in all_available_languages]
        if invalid_languages:
            print(f"Error: Invalid language codes: {', '.join(invalid_languages)}")
            print(f"Available languages: {', '.join(all_available_languages)}")
            sys.exit(1)

        language_order = requested_languages
        print(f"Exporting languages: {', '.join(language_order)}")
    else:
        language_order = all_available_languages
        print("Exporting all languages")

    # Load all label dictionaries
    all_labels = {}

    for labels_file in labels_files:
        # Extract language code from filename (e.g., labels_be.py -> be)
        lang_match = re.match(r'labels_(\w+)\.py', labels_file.name)
        if not lang_match:
            print(f"Warning: Cannot extract language code from {labels_file.name}")
            continue

        lang_code = lang_match.group(1)

        # Only process languages that are requested for export
        if lang_code not in language_order:
            print(f"Skipping {labels_file.name} (not in export list)")
            continue

        print(f"Processing {labels_file.name}...")
        labels = extract_labels_from_file(labels_file)

        if labels:
            all_labels[lang_code] = labels
            print(f"  Loaded {len(labels)} labels for {lang_code}")

    if not all_labels:
        print("No labels were loaded from any file")
        return

    # Get all unique keys from all languages
    all_keys = set()
    for labels in all_labels.values():
        all_keys.update(labels.keys())

    # Sort keys alphabetically
    sorted_keys = sorted(all_keys)

    # Prepare CSV content with dynamic header
    header = "key;" + ";".join(language_order)
    csv_lines = [header]

    for key in sorted_keys:
        row = [key]

        # Add values for each language in the specified order
        for lang in language_order:
            if lang in all_labels and key in all_labels[lang]:
                # Escape semicolons and quotes for CSV
                value = all_labels[lang][key]
                value = value.replace('"', '""')  # Escape quotes
                if ';' in value or '"' in value or '\n' in value:
                    value = f'"{value}"'  # Quote if contains delimiter or quotes
                row.append(value)
            else:
                row.append("")  # Empty if translation missing

        csv_lines.append(";".join(row))

    # Save to file with dynamic filename
    if len(language_order) == len(all_available_languages):
        output_file = project_root / 'labels_export.csv'
    else:
        langs_suffix = "_".join(language_order)
        output_file = project_root / f'labels_export_{langs_suffix}.csv'

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(csv_lines))
        print(f"\nCSV file saved to: {output_file}")
    except Exception as e:
        print(f"Warning: Could not save CSV file: {e}")

    # Print summary
    print("\n" + "="*50)
    print("Summary:")
    print(f"Total keys: {len(sorted_keys)}")
    print(f"Exported languages: {', '.join(language_order)}")
    for lang in language_order:
        if lang in all_labels:
            print(f"Language {lang}: {len(all_labels[lang])} translations")
        else:
            print(f"Language {lang}: File not found or not processed")

if __name__ == "__main__":
    main()
