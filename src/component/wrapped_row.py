# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class WrappedLabel(Label):
    """Label that wraps its text within its width instead of overflowing neighbours (narrow portrait rows)."""

    def __init__(self, **kwargs):
        kwargs.setdefault('halign', 'center')
        super(WrappedLabel, self).__init__(**kwargs)
        self.bind(width=self._wrap)

    def _wrap(self, *_):
        self.text_size = (self.width, None)

class WrappedRow(BoxLayout):
    """Horizontal row that keeps `min_height` but grows when a wrapped label inside needs more room."""
    min_height = NumericProperty(0)

    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        super(WrappedRow, self).__init__(**kwargs)
        self.bind(min_height=self._fit_height)
        self._fit_height()

    def add_widget(self, widget, *args, **kwargs):
        super(WrappedRow, self).add_widget(widget, *args, **kwargs)
        if isinstance(widget, Label) and not isinstance(widget, Button):
            widget.bind(texture_size=self._fit_height)
        self._fit_height()

    def _fit_height(self, *_):
        tallest = max(
            (child.texture_size[1] for child in self.children
             if isinstance(child, Label) and not isinstance(child, Button)),
            default=0,
        )
        self.height = max(self.min_height, tallest + 8)
