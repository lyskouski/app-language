#!/usr/bin/env python3

# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import sys
import csv
import argparse
from pathlib import Path

def parse_csv_file(csv_file_path):
    """Parse CSV file and return dictionary of languages and their labels."""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # Use semicolon as delimiter
            reader = csv.reader(f, delimiter=';')

            # Read header row
            header = next(reader)
            if not header or header[0] != 'key':
                print(f"Error: Invalid CSV format in {csv_file_path}. Expected 'key' as first column.")
                return None

            # Extract language codes from header (skip 'key' column)
            languages = header[1:]
            print(f"Found languages in CSV: {', '.join(languages)}")

            # Initialize dictionaries for each language
            all_labels = {lang: {} for lang in languages}

            # Read data rows
            for row_num, row in enumerate(reader, start=2):
                if not row or len(row) < 2:
                    continue

                key = row[0].strip()
                if not key:
                    continue

                # Process each language column
                for i, lang in enumerate(languages):
                    if i + 1 < len(row):
                        value = row[i + 1].strip()
                        # Handle quoted values (CSV escaping)
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1].replace('""', '"')
                        all_labels[lang][key] = value

            return all_labels

    except Exception as e:
        print(f"Error reading CSV file {csv_file_path}: {e}")
        return None

def generate_python_labels_content(labels_dict, lang_code):
    """Generate Python file content for labels dictionary."""
    variable_name = f"labels_{lang_code}"

    # Sort keys alphabetically DESC
    sorted_keys = sorted(labels_dict.keys(), reverse=True)

    lines = [f"{variable_name} = {{"]

    for key in sorted_keys:
        value = labels_dict[key]
        # Escape quotes and backslashes for Python string
        value = value.replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'    "{key}": "{value}",')

    lines.append("}")

    return "\n".join(lines) + "\n"

def update_labels_file(labels_dict, lang_code, l18n_dir, dry_run=False):
    """Update or create a labels_*.py file with new content."""
    labels_file = l18n_dir / f"labels_{lang_code}.py"

    # Generate new content
    new_content = generate_python_labels_content(labels_dict, lang_code)

    if dry_run:
        print(f"[DRY RUN] Would update {labels_file} with {len(labels_dict)} labels")
        return True

    try:
        # Write the new content
        with open(labels_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ Updated {labels_file} with {len(labels_dict)} labels")
        return True

    except Exception as e:
        print(f"❌ Error updating {labels_file}: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Import CSV labels and update Python label files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python tools\\labels_import.py labels_export.csv                    # Import all languages from CSV
  python tools\\labels_import.py labels_export_en_ru.csv             # Import specific languages from CSV
  python tools\\labels_import.py labels_export.csv --dry-run         # Preview changes without writing files
  python tools\\labels_import.py labels_export.csv --languages en,ru # Import only specific languages
        '''
    )
    parser.add_argument(
        'csv_file',
        help='Path to the CSV file to import (e.g., labels_export.csv)'
    )
    parser.add_argument(
        '--languages',
        type=str,
        help='Comma-separated list of languages to import (e.g., en,ru). Default: all languages in CSV'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually writing files'
    )

    args = parser.parse_args()

    # Resolve CSV file path
    csv_file_path = Path(args.csv_file)
    if not csv_file_path.is_absolute():
        # If relative path, assume it's relative to project root
        project_root = Path(__file__).parent.parent
        csv_file_path = project_root / csv_file_path

    if not csv_file_path.exists():
        print(f"Error: CSV file {csv_file_path} does not exist")
        sys.exit(1)

    # Parse CSV file
    print(f"Reading CSV file: {csv_file_path}")
    all_labels = parse_csv_file(csv_file_path)

    if not all_labels:
        print("Failed to parse CSV file")
        sys.exit(1)

    # Determine which languages to import
    available_languages = list(all_labels.keys())

    if args.languages:
        requested_languages = [lang.strip().lower() for lang in args.languages.split(',')]

        # Validate requested languages
        invalid_languages = [lang for lang in requested_languages if lang not in available_languages]
        if invalid_languages:
            print(f"Error: Invalid language codes: {', '.join(invalid_languages)}")
            print(f"Available languages in CSV: {', '.join(available_languages)}")
            sys.exit(1)

        languages_to_import = requested_languages
        print(f"Importing languages: {', '.join(languages_to_import)}")
    else:
        languages_to_import = available_languages
        print(f"Importing all languages: {', '.join(languages_to_import)}")

    # Find l18n directory
    project_root = Path(__file__).parent.parent
    l18n_dir = project_root / 'src' / 'l18n'

    if not l18n_dir.exists():
        print(f"Error: Directory {l18n_dir} does not exist")
        sys.exit(1)

    # Process each language
    success_count = 0
    total_count = len(languages_to_import)

    if args.dry_run:
        print("\n" + "="*50)
        print("DRY RUN MODE - No files will be modified")
        print("="*50)

    for lang_code in languages_to_import:
        if lang_code in all_labels and all_labels[lang_code]:
            if update_labels_file(all_labels[lang_code], lang_code, l18n_dir, args.dry_run):
                success_count += 1
        else:
            print(f"⚠️  No labels found for language: {lang_code}")

    # Print summary
    print("\n" + "="*50)
    print("Import Summary:")
    print(f"Total languages processed: {success_count}/{total_count}")

    for lang_code in languages_to_import:
        if lang_code in all_labels:
            label_count = len(all_labels[lang_code])
            print(f"Language {lang_code}: {label_count} labels")
        else:
            print(f"Language {lang_code}: No data")

    if args.dry_run:
        print("\nDRY RUN completed. Use without --dry-run to apply changes.")
    elif success_count == total_count:
        print("\n✅ All languages imported successfully!")
    else:
        print(f"\n⚠️  {total_count - success_count} languages failed to import")

if __name__ == "__main__":
    main()
