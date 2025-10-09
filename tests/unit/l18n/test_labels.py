# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import unittest
import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..', '..')
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from l18n.labels import labels

class LabelsTestCase(unittest.TestCase):
    app = None

    def setUp(self):
        pass

    def test_consistency(self):
        """Test that all labels are consistent across all language scopes"""
        # Get all available languages
        all_languages = list(labels.keys())
        self.assertGreater(len(all_languages), 1, "Should have at least 2 languages")

        # Use the first language as reference (typically "BE")
        reference_lang = all_languages[0]
        reference_labels = labels[reference_lang]
        other_languages = [lang for lang in all_languages if lang != reference_lang]

        # Check that all keys from reference language exist in all other languages
        for key in reference_labels.keys():
            for lang in other_languages:
                with self.subTest(key=key, from_lang=reference_lang, to_lang=lang):
                    self.assertIn(key, labels[lang],
                                f"Key '{key}' from {reference_lang} is missing in {lang}")

        # Check reverse: all keys from other languages should exist in reference
        for lang in other_languages:
            for key in labels[lang].keys():
                with self.subTest(key=key, from_lang=lang, to_lang=reference_lang):
                    self.assertIn(key, reference_labels,
                                f"Key '{key}' from {lang} is missing in {reference_lang}")

        # Verify we have some labels to test
        self.assertGreater(len(reference_labels), 0, f"{reference_lang} labels should not be empty")

    def test_ordering(self):
        """Test that all labels are ordered in DESC order of keys"""
        # Get all available languages
        all_languages = list(labels.keys())
        self.assertGreater(len(all_languages), 1, "Should have at least 2 languages")

        # Check that keys in each language are in descending order
        for lang in all_languages:
            lang_labels = labels[lang]
            lang_keys = list(lang_labels.keys())
            sorted_keys_desc = sorted(lang_keys, reverse=True)

            with self.subTest(language=lang):
                if lang_keys != sorted_keys_desc:
                    # Find problematic keys that are not in proper position
                    problematic_keys = []
                    for i, (actual, expected) in enumerate(zip(lang_keys, sorted_keys_desc)):
                        if actual != expected:
                            problematic_keys.append(f"Position {i}: got '{actual}', expected '{expected}'")

                    self.fail(f"Keys in {lang} are not in descending order. "
                             f"Problematic positions:\n{"\n".join(problematic_keys[:10])}")  # Show max 10 issues

        # Verify we have some labels to test
        self.assertGreater(len(labels[all_languages[0]]), 0, "Labels should not be empty")
