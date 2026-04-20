# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from domain.entities.user_settings import UserSettings
from domain.repositories.settings_repository import ISettingsRepository


class LoadSettingsUseCase:
    """
    Use Case: Load user settings.
    """

    def __init__(self, repository: ISettingsRepository):
        self._repository = repository

    def execute(self) -> UserSettings:
        """Load and return user settings."""
        return self._repository.load()


class UpdateLocaleUseCase:
    """
    Use Case: Update the interface locale setting.
    Single Responsibility: Only handles locale updates.
    """

    def __init__(self, repository: ISettingsRepository):
        self._repository = repository

    def execute(self, locale: str) -> None:
        """Update the interface locale."""
        settings = self._repository.load()
        settings.interface_locale = locale
        self._repository.save(settings)


class UpdateLanguagePairUseCase:
    """
    Use Case: Update the language learning pair.
    """

    def __init__(self, repository: ISettingsRepository):
        self._repository = repository

    def execute(self, locale_from: str, locale_to: str) -> None:
        """Update the language pair for learning."""
        settings = self._repository.load()
        settings.locale_from = locale_from
        settings.locale_to = locale_to
        self._repository.save(settings)
