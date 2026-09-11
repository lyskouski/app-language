# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Unicode-script-aware font resolution.

Kivy's SDL2 text provider renders a whole Label with a single font, so a
string mixing Latin text with a non-Latin script (e.g. "PA - ਪੰਜਾਬੀ") must
pick one font capable of rendering every character it contains. This module
inspects the codepoints of a string and returns the registered font name
whose script covers the most specific (non-Latin) range found, falling back
to the default UI font for plain Latin/Cyrillic/Greek text already covered
by it.
"""

# (first codepoint, last codepoint, registered font name), ordered by script.
_SCRIPT_RANGES = (
    (0x0600, 0x06FF, 'Noto Sans Arabic'),       # Arabic (also covers Urdu)
    (0x0700, 0x074F, 'Noto Sans Arabic'),       # Syriac supplement block overlap safeguard
    (0x0900, 0x097F, 'Noto Sans Devanagari'),   # Devanagari (Marathi, Nepali, Sanskrit, Hindi)
    (0x0980, 0x09FF, 'Noto Sans Bengali'),      # Bengali
    (0x0A00, 0x0A7F, 'Noto Sans Gurmukhi'),     # Gurmukhi (Punjabi)
    (0x0A80, 0x0AFF, 'Noto Sans Gujarati'),     # Gujarati
    (0x0B80, 0x0BFF, 'Noto Sans Tamil'),        # Tamil
    (0x0C00, 0x0C7F, 'Noto Sans Telugu'),       # Telugu
    (0x0C80, 0x0CFF, 'Noto Sans Kannada'),      # Kannada
    (0x0D00, 0x0D7F, 'Noto Sans Malayalam'),    # Malayalam
    (0x0E00, 0x0E7F, 'Noto Sans Thai'),         # Thai
    (0x10A0, 0x10FF, 'Noto Sans Georgian'),     # Georgian
    (0x1200, 0x137F, 'Noto Sans Ethiopic'),     # Ethiopic (Amharic)
    (0x1780, 0x17FF, 'Noto Sans Khmer'),        # Khmer
    (0x4E00, 0x9FFF, 'Noto Sans CJK SC'),       # CJK Unified Ideographs
    (0x3040, 0x30FF, 'Noto Sans CJK SC'),       # Hiragana/Katakana
    (0xAC00, 0xD7A3, 'Noto Sans CJK SC'),       # Hangul syllables
)

_DEFAULT_FONT = 'DejaVu Sans'


def font_for_text(text):
    """Return the registered font name able to render every character in `text`."""
    if not text:
        return _DEFAULT_FONT

    for character in text:
        codepoint = ord(character)
        for start, end, font_name in _SCRIPT_RANGES:
            if start <= codepoint <= end:
                return font_name

    return _DEFAULT_FONT
