# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Unit tests for Application Layer.
Tests application services that orchestrate business logic.
"""

import pytest
import os
from unittest.mock import Mock, patch

from domain.entities.vocabulary_item import VocabularyItem
from domain.entities.user_settings import UserSettings
from domain.repositories.vocabulary_repository import IVocabularyRepository
from domain.use_cases.vocabulary_use_cases import LoadVocabularyUseCase, ShuffleVocabularyUseCase
from application.services.vocabulary_service import VocabularyService


# ========== Application Services Tests ==========

class TestVocabularyService:
    """Integration tests for VocabularyService."""

    def test_load_and_prepare_study_set(self):
        """Test loading vocabulary and preparing study set."""
        # Arrange
        mock_repo = Mock(spec=IVocabularyRepository)
        test_items = [VocabularyItem(f"word{i}", f"palabra{i}") for i in range(50)]
        mock_repo.load_from_file.return_value = test_items

        load_use_case = LoadVocabularyUseCase(mock_repo)
        shuffle_use_case = ShuffleVocabularyUseCase()

        service = VocabularyService(load_use_case, shuffle_use_case)

        # Act
        service.load_vocabulary("test.txt")
        study_set = service.prepare_study_set(limit=25)

        # Assert
        assert len(study_set) == 25
        assert all(isinstance(item, VocabularyItem) for item in study_set)

    def test_get_current_study_set(self):
        """Test getting the current study set."""
        mock_repo = Mock(spec=IVocabularyRepository)
        test_items = [VocabularyItem("hello", "hola")]
        mock_repo.load_from_file.return_value = test_items

        load_use_case = LoadVocabularyUseCase(mock_repo)
        shuffle_use_case = ShuffleVocabularyUseCase()

        service = VocabularyService(load_use_case, shuffle_use_case)
        service.load_vocabulary("test.txt")
        service.prepare_study_set(limit=10)

        result = service.get_current_study_set()

        assert len(result) == 1
        assert result[0].origin == "hello"

    def test_mark_item_correct_with_profiler(self):
        """Test marking item correct when profiler is available."""
        mock_repo = Mock(spec=IVocabularyRepository)
        mock_profiler = Mock()

        load_use_case = LoadVocabularyUseCase(mock_repo)
        shuffle_use_case = ShuffleVocabularyUseCase()

        service = VocabularyService(load_use_case, shuffle_use_case, mock_profiler)

        item = VocabularyItem("hello", "hola")
        service.mark_item_correct(item)

        mock_profiler.mark_positive.assert_called_once_with(item)

    def test_prepare_study_set_with_force_shuffle(self):
        """Test force shuffle bypasses ML profiler."""
        mock_repo = Mock(spec=IVocabularyRepository)
        mock_profiler = Mock()
        test_items = [VocabularyItem(f"word{i}", f"palabra{i}") for i in range(50)]
        mock_repo.load_from_file.return_value = test_items

        load_use_case = LoadVocabularyUseCase(mock_repo)
        shuffle_use_case = ShuffleVocabularyUseCase()

        service = VocabularyService(load_use_case, shuffle_use_case, mock_profiler)
        service.load_vocabulary("test.txt")

        # Act with force_shuffle=True
        study_set = service.prepare_study_set(limit=25, force_shuffle=True)

        # Assert profiler was NOT called
        mock_profiler.get_prioritized_items.assert_not_called()
        assert len(study_set) == 25

    def test_prepare_study_set_with_profiler(self):
        """Test ML profiler is used when available and not forced to shuffle."""
        mock_repo = Mock(spec=IVocabularyRepository)
        mock_profiler = Mock()
        test_items = [VocabularyItem(f"word{i}", f"palabra{i}") for i in range(50)]
        mock_repo.load_from_file.return_value = test_items
        mock_profiler.get_prioritized_items.return_value = test_items[:25]

        load_use_case = LoadVocabularyUseCase(mock_repo)
        shuffle_use_case = ShuffleVocabularyUseCase()

        service = VocabularyService(load_use_case, shuffle_use_case, mock_profiler)
        service.load_vocabulary("test.txt")

        # Act with force_shuffle=False (default)
        study_set = service.prepare_study_set(limit=25, force_shuffle=False)

        # Assert profiler WAS called
        mock_profiler.get_prioritized_items.assert_called_once_with(test_items, 25)
        assert len(study_set) <= 25


class TestMediaService:
    """Test media service."""

    @pytest.fixture
    def media_service(self, tmp_path):
        """Create a media service instance for testing."""
        from application.services.media_service import MediaService
        audio_dir = str(tmp_path / "audio")
        os.makedirs(audio_dir, exist_ok=True)
        return MediaService('en', audio_dir)

    def test_set_language(self, media_service):
        """Test setting language."""
        media_service.set_language('es')
        assert media_service._lang == 'es'

    def test_set_audio_directory(self, media_service, tmp_path):
        """Test setting audio directory."""
        new_dir = str(tmp_path / "new_audio")
        media_service.set_audio_directory(new_dir)
        assert media_service._audio_dir == new_dir

    @patch('application.services.media_service.requests.post')
    def test_get_audio_file_generates_tts(self, mock_post, media_service):
        """Test that TTS is generated when file doesn't exist."""
        # Mock successful TTS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "//OEtlc3Q="  # Base64 encoded "test"
        mock_post.return_value = mock_response

        result = media_service.get_audio_file("hello")

        # Should call TTS generation
        assert mock_post.called
        # Result should be a path
        assert result is not None


class TestRecorderService:
    """Test recorder service."""

    @pytest.fixture
    def mock_controller(self):
        """Create a mock recorder controller."""
        controller = Mock()
        controller.get_initial_status.return_value = "Ready"
        controller.start_recording.return_value = "Recording..."
        controller.stop_recording.return_value = "/path/to/recording.mp3"
        return controller

    @pytest.fixture
    def recorder_service(self, mock_controller):
        """Create a recorder service instance for testing."""
        from application.services.recorder_service import RecorderService
        return RecorderService(mock_controller)

    def test_get_initial_status(self, recorder_service, mock_controller):
        """Test getting initial status."""
        result = recorder_service.get_initial_status()

        assert result == "Ready"
        mock_controller.get_initial_status.assert_called_once()

    def test_start_recording(self, recorder_service, mock_controller):
        """Test starting recording."""
        result = recorder_service.start_recording()

        assert result == "Recording..."
        assert recorder_service.is_recording() is True
        mock_controller.start_recording.assert_called_once()

    def test_stop_recording(self, recorder_service, mock_controller):
        """Test stopping recording."""
        recorder_service.start_recording()
        result = recorder_service.stop_recording()

        assert result == "/path/to/recording.mp3"
        assert recorder_service.is_recording() is False
        mock_controller.stop_recording.assert_called_once()


# ========== Settings Service Tests ==========

from domain.use_cases.settings_use_cases import (
    LoadSettingsUseCase,
    UpdateLocaleUseCase,
    UpdateLanguagePairUseCase
)
from application.services.settings_service import SettingsService


class TestSettingsService:
    """Test settings service."""

    @pytest.fixture
    def mock_use_cases(self):
        """Create mock use cases."""
        load = Mock(spec=LoadSettingsUseCase)
        update_locale = Mock(spec=UpdateLocaleUseCase)
        update_pair = Mock(spec=UpdateLanguagePairUseCase)
        return load, update_locale, update_pair

    @pytest.fixture
    def settings_service(self, mock_use_cases):
        """Create settings service instance."""
        load, update_locale, update_pair = mock_use_cases
        return SettingsService(load, update_locale, update_pair)

    def test_load_settings(self, settings_service, mock_use_cases):
        """Test loading settings."""
        load_use_case = mock_use_cases[0]
        expected_settings = UserSettings(interface_locale="EN")
        load_use_case.execute.return_value = expected_settings

        result = settings_service.load_settings()

        assert result == expected_settings
        assert settings_service.get_current_settings() == expected_settings
        load_use_case.execute.assert_called_once()

    def test_get_current_settings(self, settings_service):
        """Test getting current settings."""
        result = settings_service.get_current_settings()

        assert isinstance(result, UserSettings)

    def test_update_interface_locale(self, settings_service, mock_use_cases):
        """Test updating interface locale."""
        update_locale_use_case = mock_use_cases[1]

        settings_service.update_interface_locale("ES")

        update_locale_use_case.execute.assert_called_once_with("ES")
        assert settings_service.get_current_settings().interface_locale == "ES"

    def test_update_language_pair(self, settings_service, mock_use_cases):
        """Test updating language pair."""
        update_pair_use_case = mock_use_cases[2]

        settings_service.update_language_pair("EN", "ES")

        update_pair_use_case.execute.assert_called_once_with("EN", "ES")
        current = settings_service.get_current_settings()
        assert current.locale_from == "EN"
        assert current.locale_to == "ES"

    def test_should_show_language_selection(self, settings_service, mock_use_cases):
        """Test language selection screen logic."""
        # No locale configured
        assert settings_service.should_show_language_selection() is True

        # Locale configured
        settings_service.update_interface_locale("EN")
        assert settings_service.should_show_language_selection() is False


# ========== Resource Service Tests ==========

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
