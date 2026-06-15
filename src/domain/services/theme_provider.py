# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod

from domain.entities.ui_theme import UITheme


class IThemeProvider(ABC):
    """Domain port for obtaining the active UI theme."""

    @abstractmethod
    def set_mode(self, mode: str) -> None:
        """Set active theme mode ('light' or 'dark')."""
        raise NotImplementedError

    @abstractmethod
    def get_mode(self) -> str:
        """Get active theme mode."""
        raise NotImplementedError

    @abstractmethod
    def get_theme(self) -> UITheme:
        """Return active theme tokens."""
        raise NotImplementedError
