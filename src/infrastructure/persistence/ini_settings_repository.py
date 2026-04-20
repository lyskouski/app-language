# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from domain.entities.user_settings import UserSettings
from domain.repositories.settings_repository import ISettingsRepository
from lib.ini_config_parser import IniConfigParser


class IniSettingsRepository(ISettingsRepository):
    """
    INI file-based implementation of settings repository.
    Adapter pattern: adapts IniConfigParser to ISettingsRepository interface.
    """

    def __init__(self, config_parser: IniConfigParser):
        self._config = config_parser

    def load(self) -> UserSettings:
        """Load user settings from INI file."""
        return UserSettings(
            interface_locale=self._config.get(IniConfigParser.INTERFACE_LOCALE, ''),
            locale_from=self._config.get('locale_from', ''),
            locale_to=self._config.get('locale_to', '')
        )

    def save(self, settings: UserSettings) -> None:
        """Save user settings to INI file."""
        self._config.save(IniConfigParser.INTERFACE_LOCALE, settings.interface_locale)
        self._config.save('locale_from', settings.locale_from)
        self._config.save('locale_to', settings.locale_to)

    def get_setting(self, key: str, default: str = '') -> str:
        """Get a specific setting value."""
        return self._config.get(key, default)

    def set_setting(self, key: str, value: str) -> None:
        """Set a specific setting value."""
        self._config.save(key, value)
