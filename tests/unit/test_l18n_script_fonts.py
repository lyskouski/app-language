# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import unittest

from l18n.script_fonts import font_for_text, font_lacks_text, needs_fallback, script_runs, split_markup_items


class ScriptFontsTestCase(unittest.TestCase):

    def test_font_for_text(self):
        """Test that the most specific script font is resolved"""
        self.assertEqual(font_for_text('Polski'), 'DejaVu Sans')
        self.assertEqual(font_for_text('Русский'), 'DejaVu Sans')
        self.assertEqual(font_for_text('العربية'), 'Noto Sans Arabic')

    def test_script_runs(self):
        """Test that mixed text is split into runs with whitespace kept in the preceding run"""
        self.assertEqual(script_runs('AR-PL (العربية - Polski)'), [
            ('DejaVu Sans', 'AR-PL ('),
            ('Noto Sans Arabic', 'العربية '),
            ('DejaVu Sans', '- Polski)'),
        ])

    def test_needs_fallback(self):
        """Test that only text mixing a script font with other characters needs fallback"""
        self.assertFalse(needs_fallback(''))
        self.assertFalse(needs_fallback('EN-PL (English - Polski)'))
        self.assertFalse(needs_fallback('ქართული ენა'))
        self.assertTrue(needs_fallback('KA-PL (ქართული - Polski)'))
        self.assertTrue(needs_fallback('HI-PL (हिन्दी - Polski)'))

    def test_font_lacks_text(self):
        """Test that substrings are checked against the input font, ignoring foreign fonts"""
        self.assertTrue(font_lacks_text('Noto Sans Arabic', 'Deutsch'))
        self.assertTrue(font_lacks_text('DejaVu Sans', 'العربية'))
        self.assertFalse(font_lacks_text('Noto Sans Arabic', 'العربية '))
        self.assertFalse(font_lacks_text('DejaVu Sans', 'Deutsch'))
        self.assertFalse(font_lacks_text('icons.ttf', 'Deutsch'))

    def test_split_markup_items(self):
        """Test that text runs are wrapped while explicit font regions stay untouched"""
        items = ['[font=icons.ttf]', '\uf0415', '[/font]', ' ქართული Polski']
        self.assertEqual(split_markup_items(items), [
            '[font=icons.ttf]', '\uf0415', '[/font]',
            '[font=DejaVu Sans]', ' ', '[/font]',
            '[font=Noto Sans Georgian]', 'ქართული ', '[/font]',
            '[font=DejaVu Sans]', 'Polski', '[/font]',
        ])
