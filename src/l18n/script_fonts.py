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

Script fonts carry no Latin letters, so a mixed string still needs one font
per run of characters (the way Flutter falls back per glyph through
`fontFamilyFallback`). `install_script_fallback` splits such text into
`[font=...]` markup runs before Kivy lays it out.
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


def _script_font(character):
    codepoint = ord(character)
    for start, end, font_name in _SCRIPT_RANGES:
        if start <= codepoint <= end:
            return font_name
    return None


def script_runs(text):
    """Split `text` into (font name, chunk) runs; whitespace stays with the preceding run."""
    runs = []
    for character in text:
        font_name = _script_font(character) or _DEFAULT_FONT
        if runs and (character.isspace() or runs[-1][0] == font_name):
            runs[-1][1] += character
        else:
            runs.append([font_name, character])
    return [(font_name, chunk) for font_name, chunk in runs]


def needs_fallback(text):
    """True when `text` mixes a non-Latin script with characters its font lacks."""
    if not text or not any(_script_font(character) for character in text):
        return False
    return len({font_name for font_name, chunk in script_runs(text) if chunk.strip()}) > 1


def split_markup_items(items):
    """Wrap text items of split Kivy markup into per-script `[font=...]` runs.

    Text already inside an explicit `[font=...]` tag (e.g. icon glyphs) is left untouched.
    """
    result = []
    font_depth = 0
    for item in items:
        if item.startswith('[') and item.endswith(']'):
            if item.startswith('[font='):
                font_depth += 1
            elif item == '[/font]':
                font_depth = max(0, font_depth - 1)
            result.append(item)
        elif font_depth:
            result.append(item)
        else:
            for font_name, chunk in script_runs(item):
                result.extend(('[font={}]'.format(font_name), chunk, '[/font]'))
    return result


def install_script_fallback():
    """Patch Kivy labels to render mixed-script text with a font per script run."""
    from kivy.core.text import Label as CoreLabel
    from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
    from kivy.uix.label import Label

    markup_items = CoreMarkupLabel.markup.fget

    def markup(self):
        items = markup_items(self)
        return split_markup_items(items) if needs_fallback(self.label) else items

    CoreMarkupLabel.markup = property(markup)

    class ScriptFallbackLabel(CoreMarkupLabel):
        """Plain (non-markup) text rendered through markup runs."""

        @property
        def markup(self):
            text = self.label.replace('&', '&amp;').replace('[', '&bl;').replace(']', '&br;')
            return split_markup_items([text]) if text else []

    def use_core_label(widget, text):
        cls = ScriptFallbackLabel if needs_fallback(text) else CoreLabel
        if widget.markup or widget._label.__class__ is cls:
            return
        options = {name: getattr(widget, name) for name in widget._font_properties}
        options['usersize'] = widget.text_size
        if widget.disabled:
            options['color'] = widget.disabled_color
            options['outline_color'] = widget.disabled_outline_color
        widget._label = cls(**options)

    create_label = Label._create_label
    trigger_texture_update = Label._trigger_texture_update

    def _create_label(self):
        create_label(self)
        use_core_label(self, self.text)

    def _trigger_texture_update(self, name=None, source=None, value=None):
        if name == 'text' and source:
            use_core_label(self, value)
        trigger_texture_update(self, name, source, value)

    Label._create_label = _create_label
    Label._trigger_texture_update = _trigger_texture_update
