# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from domain.entities.ui_theme import UITheme
from domain.services.theme_provider import IThemeProvider


class Material3ThemeProvider(IThemeProvider):
    """Infrastructure provider for default Material 3 theme tokens."""

    @staticmethod
    def _argb_to_rgba(argb: int):
        a = ((argb >> 24) & 0xFF) / 255.0
        r = ((argb >> 16) & 0xFF) / 255.0
        g = ((argb >> 8) & 0xFF) / 255.0
        b = (argb & 0xFF) / 255.0
        return [r, g, b, a]

    def get_theme(self) -> UITheme:
        primary = self._argb_to_rgba(0xFF912391)
        secondary = self._argb_to_rgba(0xFFDCA3BC)

        return UITheme(
            md3_primary=primary,
            md3_secondary=secondary,
            md3_surface=[0.98, 0.97, 0.98, 1.0],
            md3_surface_container=[0.94, 0.91, 0.94, 1.0],
            md3_surface_variant=[0.90, 0.86, 0.90, 1.0],
            md3_outline=[0.57, 0.46, 0.56, 1.0],
            md3_on_primary=[1.0, 1.0, 1.0, 1.0],
            md3_on_secondary=[0.20, 0.08, 0.18, 1.0],
            md3_on_surface=[0.16, 0.10, 0.16, 1.0],
            md3_on_surface_variant=[0.36, 0.28, 0.35, 1.0],
            md3_button_height=48,
            md3_textinput_height=48,
        )
