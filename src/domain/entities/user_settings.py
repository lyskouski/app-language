# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserSettings:
    """
    Domain Entity representing user settings.
    """
    interface_locale: str = ''
    locale_from: str = ''
    locale_to: str = ''

    def has_locale_configured(self) -> bool:
        """Check if user has configured their interface locale."""
        return bool(self.interface_locale)

    def has_language_pair_configured(self) -> bool:
        """Check if user has configured their learning language pair."""
        return bool(self.locale_from) and bool(self.locale_to)
