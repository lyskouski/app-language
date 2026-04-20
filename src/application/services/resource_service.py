# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from domain.repositories.resource_repository import IResourceRepository
from l18n.labels import labels


class LocalizationService:
    """
    Application Service for localization.
    Single Responsibility: Handle translation and locale management.
    """

    def __init__(self):
        self._labels = labels

    def translate(self, key: str, locale: str) -> str:
        """
        Translate a key to the specified locale.
        Falls back to English if locale not found, then to key if not found.
        """
        locale_labels = self._labels.get(locale, self._labels.get('EN', {}))
        return locale_labels.get(key, f'[{key}]')

    def get_available_locales(self) -> list:
        """Get list of available locales."""
        return list(self._labels.keys())


class ResourceService:
    """
    Application Service for resource management.
    Single Responsibility: Handle resource paths and directories.
    """

    def __init__(self, repository: IResourceRepository):
        self._repository = repository

    def find_resource(self, path: str) -> str:
        """Find a resource by path."""
        return self._repository.find_resource(path)

    def get_audio_directory(self, locale: str) -> str:
        """Get audio directory for a locale."""
        return self._repository.get_audio_dir(locale)

    def get_image_directory(self, locale: str) -> str:
        """Get image directory for a locale."""
        return self._repository.get_image_dir(locale)

    def get_path_with_home(self, file_path: str) -> str:
        """Get path relative to home directory."""
        return self._repository.get_path_with_home_dir(file_path)
