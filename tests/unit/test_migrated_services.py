# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Unit tests for migrated services and infrastructure components.
Tests the Clean Architecture implementation for audio and ML components.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler
from domain.services.audio_comparator import IAudioComparator


class TestMLVocabularyProfiler:
    """Test ML vocabulary profiler implementation."""

    @pytest.fixture
    def temp_paths(self, tmp_path):
        """Create temporary paths for profiler data."""
        profile_path = tmp_path / "profile.json"
        model_path = tmp_path / "model.pkl"
        return str(profile_path), str(model_path)

    @pytest.fixture
    def profiler(self, temp_paths):
        """Create a profiler instance for testing."""
        from infrastructure.ml.ml_vocabulary_profiler import MLVocabularyProfiler
        profile_path, model_path = temp_paths
        return MLVocabularyProfiler(profile_path, model_path)

    def test_implements_interface(self, profiler):
        """Test that profiler implements IVocabularyProfiler."""
        assert isinstance(profiler, IVocabularyProfiler)

    def test_mark_positive(self, profiler):
        """Test marking an item as correctly answered."""
        item = VocabularyItem("hello", "hola")

        profiler.mark_positive(item)

        assert "hello" in profiler.user_history
        assert profiler.user_history["hello"]["correct"] == 1
        assert profiler.user_history["hello"]["incorrect"] == 0

    def test_mark_negative(self, profiler):
        """Test marking an item as incorrectly answered."""
        item = VocabularyItem("world", "mundo")

        profiler.mark_negative(item)

        assert "world" in profiler.user_history
        assert profiler.user_history["world"]["correct"] == 0
        assert profiler.user_history["world"]["incorrect"] == 1

    def test_get_prioritized_items_empty_list(self, profiler):
        """Test prioritization with empty list."""
        items = []
        result = profiler.get_prioritized_items(items, 10)

        assert result == []

    def test_get_prioritized_items_respects_limit(self, profiler):
        """Test that prioritization respects the limit."""
        items = [
            VocabularyItem(f"word{i}", f"palabra{i}")
            for i in range(50)
        ]

        result = profiler.get_prioritized_items(items, 10)

        assert len(result) == 10

    def test_prioritizes_difficult_words(self, profiler):
        """Test that difficult words are prioritized."""
        # Short easy word
        easy_item = VocabularyItem("hi", "hola")
        # Long difficult word
        hard_item = VocabularyItem("pharmaceutical", "farmacéutico")

        items = [easy_item, hard_item]
        result = profiler.get_prioritized_items(items, 2)

        # Hard item should be first (higher difficulty)
        assert result[0] == hard_item
        assert result[1] == easy_item

    def test_persistence(self, temp_paths):
        """Test that user history is persisted."""
        from infrastructure.ml.ml_vocabulary_profiler import MLVocabularyProfiler
        profile_path, model_path = temp_paths

        # Create first profiler and mark items
        profiler1 = MLVocabularyProfiler(profile_path, model_path)
        item = VocabularyItem("test", "prueba")
        profiler1.mark_positive(item)
        profiler1._save_user_profile()

        # Create second profiler and check history loaded
        profiler2 = MLVocabularyProfiler(profile_path, model_path)
        assert "test" in profiler2.user_history
        assert profiler2.user_history["test"]["correct"] == 1


class TestLibrosaAudioComparator:
    """Test audio comparator implementation."""

    @pytest.fixture
    def comparator(self):
        """Create a comparator instance for testing."""
        from infrastructure.audio.librosa_audio_comparator import LibrosaAudioComparator
        return LibrosaAudioComparator()

    def test_implements_interface(self, comparator):
        """Test that comparator implements IAudioComparator."""
        assert isinstance(comparator, IAudioComparator)

    def test_is_available(self, comparator):
        """Test availability check."""
        # Should return bool based on dependencies
        result = comparator.is_available()
        assert isinstance(result, bool)

    def test_compare_audio_without_dependencies(self, comparator):
        """Test audio comparison when dependencies are unavailable."""
        with patch('infrastructure.audio.librosa_audio_comparator.HAS_NUMPY', False):
            comparator_no_deps = comparator
            result = comparator_no_deps.compare_audio("fake1.mp3", "fake2.mp3")

            assert isinstance(result, list)
            assert len(result) > 0
            assert "feedback" in result[0]


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


class TestDependencyInjection:
    """Test dependency injection container."""

    @pytest.fixture
    def container(self, tmp_path):
        """Create a DI container instance for testing."""
        from infrastructure.di.container import DependencyContainer
        return DependencyContainer(str(tmp_path))

    def test_vocabulary_repository_singleton(self, container):
        """Test that vocabulary repository is a singleton."""
        repo1 = container.vocabulary_repository()
        repo2 = container.vocabulary_repository()

        assert repo1 is repo2

    def test_settings_service_singleton(self, container):
        """Test that settings service is a singleton."""
        service1 = container.settings_service()
        service2 = container.settings_service()

        assert service1 is service2

    def test_media_service_creates_new_instance(self, container):
        """Test that media service creates new instances."""
        service1 = container.media_service('en', '/path1')
        service2 = container.media_service('es', '/path2')

        # Different instances with different configs
        assert service1 is not service2

    def test_audio_comparator_available(self, container):
        """Test that audio comparator can be created."""
        comparator = container.audio_comparator()

        assert comparator is not None
        assert hasattr(comparator, 'compare_audio')

    def test_recorder_service_available(self, container):
        """Test that recorder service can be created."""
        service = container.recorder_service()

        assert service is not None
        assert hasattr(service, 'start_recording')
        assert hasattr(service, 'stop_recording')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
