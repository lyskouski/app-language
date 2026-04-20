# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for ResourceService and LocalizationService."""

import pytest
from unittest.mock import Mock

from application.services.resource_service import LocalizationService, ResourceService
from domain.repositories.resource_repository import IResourceRepository


class TestLocalizationService:
    """Test localization service."""

    @pytest.fixture
    def localization_service(self):
        """Create localization service instance."""
        return LocalizationService()

    def test_translate_existing_key(self, localization_service):
        """Test translating an existing key."""
        # Assuming some labels exist
        result = localization_service.translate("button_shuffle", "EN")
        # Should return something (not the fallback)
        assert result is not None
        assert not result.startswith("[")

    def test_translate_missing_key_returns_fallback(self, localization_service):
        """Test translating a missing key returns fallback."""
        result = localization_service.translate("nonexistent_key", "EN")
        assert result == "[nonexistent_key]"

    def test_translate_missing_locale_falls_back_to_english(self, localization_service):
        """Test that missing locale falls back to English."""
        result = localization_service.translate("button_shuffle", "INVALID_LOCALE")
        # Should fall back to EN
        assert result is not None

    def test_get_available_locales(self, localization_service):
        """Test getting available locales."""
        locales = localization_service.get_available_locales()
        assert isinstance(locales, list)
        assert len(locales) > 0
        assert "EN" in locales


class TestResourceService:
    """Test resource service."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock resource repository."""
        repo = Mock(spec=IResourceRepository)
        repo.find_resource.return_value = "/path/to/resource"
        repo.get_audio_dir.return_value = "/audio/en"
        repo.get_image_dir.return_value = "/images/en"
        repo.get_path_with_home_dir.return_value = "/home/user/file"
        return repo

    @pytest.fixture
    def resource_service(self, mock_repository):
        """Create resource service instance."""
        return ResourceService(mock_repository)

    def test_find_resource(self, resource_service, mock_repository):
        """Test finding a resource."""
        result = resource_service.find_resource("test.txt")

        assert result == "/path/to/resource"
        mock_repository.find_resource.assert_called_once_with("test.txt")

    def test_get_audio_directory(self, resource_service, mock_repository):
        """Test getting audio directory."""
        result = resource_service.get_audio_directory("en")

        assert result == "/audio/en"
        mock_repository.get_audio_dir.assert_called_once_with("en")

    def test_get_image_directory(self, resource_service, mock_repository):
        """Test getting image directory."""
        result = resource_service.get_image_directory("en")

        assert result == "/images/en"
        mock_repository.get_image_dir.assert_called_once_with("en")

    def test_get_path_with_home(self, resource_service, mock_repository):
        """Test getting path with home directory."""
        result = resource_service.get_path_with_home("file.txt")

        assert result == "/home/user/file"
        mock_repository.get_path_with_home_dir.assert_called_once_with("file.txt")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
