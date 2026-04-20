# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from abc import ABC, abstractmethod
from typing import Optional


class IResourceRepository(ABC):
    """
    Repository interface for resource management (files, paths, etc.).
    """

    @abstractmethod
    def find_resource(self, path: str) -> Optional[str]:
        """Find a resource by path, checking user directory and application resources."""
        pass

    @abstractmethod
    def get_home_dir(self) -> str:
        """Get the application home directory."""
        pass

    @abstractmethod
    def get_path_with_home_dir(self, file_path: str) -> str:
        """Get a path relative to home directory, creating directories as needed."""
        pass

    @abstractmethod
    def get_audio_dir(self, locale: str) -> str:
        """Get the audio directory for a specific locale."""
        pass

    @abstractmethod
    def get_image_dir(self, locale: str) -> str:
        """Get the image directory for a specific locale."""
        pass
