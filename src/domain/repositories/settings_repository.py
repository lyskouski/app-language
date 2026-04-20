# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod
from domain.entities.user_settings import UserSettings


class ISettingsRepository(ABC):
    """
    Repository interface for settings persistence.
    """

    @abstractmethod
    def load(self) -> UserSettings:
        """Load user settings."""
        pass

    @abstractmethod
    def save(self, settings: UserSettings) -> None:
        """Save user settings."""
        pass

    @abstractmethod
    def get_setting(self, key: str, default: str = '') -> str:
        """Get a specific setting value."""
        pass

    @abstractmethod
    def set_setting(self, key: str, value: str) -> None:
        """Set a specific setting value."""
        pass
