# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from domain.entities.ui_theme import UITheme
from domain.services.theme_provider import IThemeProvider


class ThemeService:
    """Application service for retrieving UI theme definitions."""

    def __init__(self, theme_provider: IThemeProvider):
        self._theme_provider = theme_provider

    def set_mode(self, mode: str) -> None:
        self._theme_provider.set_mode(mode)

    def get_mode(self) -> str:
        return self._theme_provider.get_mode()

    def get_theme(self) -> UITheme:
        return self._theme_provider.get_theme()
