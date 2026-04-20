# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from domain.entities.user_settings import UserSettings
from domain.use_cases.settings_use_cases import (
    LoadSettingsUseCase,
    UpdateLocaleUseCase,
    UpdateLanguagePairUseCase
)


class SettingsService:
    """
    Application Service for managing user settings.
    Coordinates settings-related use cases.
    """

    def __init__(
        self,
        load_use_case: LoadSettingsUseCase,
        update_locale_use_case: UpdateLocaleUseCase,
        update_language_pair_use_case: UpdateLanguagePairUseCase
    ):
        self._load_use_case = load_use_case
        self._update_locale_use_case = update_locale_use_case
        self._update_language_pair_use_case = update_language_pair_use_case
        self._current_settings: UserSettings = UserSettings()

    def load_settings(self) -> UserSettings:
        """Load and cache user settings."""
        self._current_settings = self._load_use_case.execute()
        return self._current_settings

    def get_current_settings(self) -> UserSettings:
        """Get the currently loaded settings."""
        return self._current_settings

    def update_interface_locale(self, locale: str) -> None:
        """Update the interface locale."""
        self._update_locale_use_case.execute(locale)
        self._current_settings.interface_locale = locale

    def update_language_pair(self, locale_from: str, locale_to: str) -> None:
        """Update the language learning pair."""
        self._update_language_pair_use_case.execute(locale_from, locale_to)
        self._current_settings.locale_from = locale_from
        self._current_settings.locale_to = locale_to

    def should_show_language_selection(self) -> bool:
        """Determine if language selection screen should be shown."""
        return not self._current_settings.has_locale_configured()
