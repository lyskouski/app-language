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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
