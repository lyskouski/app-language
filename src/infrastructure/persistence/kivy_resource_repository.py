# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
from typing import Optional
from domain.repositories.resource_repository import IResourceRepository
import kivy.resources


class KivyResourceRepository(IResourceRepository):
    """
    Kivy-based implementation of resource repository.
    Encapsulates Kivy framework dependencies.
    """

    def __init__(self, user_data_dir: str):
        self._user_data_dir = user_data_dir
        self._home_dir = os.path.join(user_data_dir, ".terCAD", "app-language")
        os.makedirs(self._home_dir, exist_ok=True)

    def find_resource(self, path: str) -> Optional[str]:
        """Find a resource, checking user directory first."""
        user_path = os.path.join(self._home_dir, path)
        if os.path.exists(user_path):
            return user_path
        return kivy.resources.resource_find(path)

    def get_home_dir(self) -> str:
        """Get the application home directory."""
        return self._home_dir

    def get_path_with_home_dir(self, file_path: str) -> str:
        """Get a path relative to home directory, creating directories as needed."""
        path = os.path.join(self._home_dir, file_path)
        dir_path = os.path.dirname(path) if os.path.splitext(file_path)[1] else path
        os.makedirs(dir_path, exist_ok=True)
        return path

    def get_audio_dir(self, locale: str) -> str:
        """Get the audio directory for a specific locale."""
        path = os.path.join(self._home_dir, "assets", "data", locale, "audio")
        os.makedirs(path, exist_ok=True)
        return path

    def get_image_dir(self, locale: str) -> str:
        """Get the image directory for a specific locale."""
        path = os.path.join(self._home_dir, "assets", "data", locale, "images")
        os.makedirs(path, exist_ok=True)
        return f'assets/data/{locale}/images'
