# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Unit tests for Infrastructure Layer.
Tests infrastructure implementations (persistence, ML, audio, DI).
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler
from domain.services.audio_comparator import IAudioComparator


# ========== Persistence Tests ==========

class TestFileVocabularyRepository:
    """Test file-based vocabulary repository."""

    def test_load_from_file(self):
        """Test loading vocabulary from file."""
        from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository

        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("hello;hola;hello.mp3;hello.jpg\n")
            f.write("world;mundo\n")
            f.write("good;bueno;good.mp3\n")
            temp_path = f.name

        try:
            repo = FileVocabularyRepository()

            # Act
            items = repo.load_from_file(temp_path)

            # Assert
            assert len(items) == 3

            assert items[0].origin == "hello"
            assert items[0].translation == "hola"
            assert items[0].sound == "hello.mp3"
            assert items[0].image == "hello.jpg"

            assert items[1].origin == "world"
            assert items[1].translation == "mundo"
            assert items[1].sound is None
            assert items[1].image is None

            assert items[2].origin == "good"
            assert items[2].translation == "bueno"
            assert items[2].sound == "good.mp3"
            assert items[2].image is None

        finally:
            os.unlink(temp_path)

    def test_save_to_file(self):
        """Test saving vocabulary to file."""
        from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            temp_path = f.name

        try:
            repo = FileVocabularyRepository()
            items = [
                VocabularyItem("hello", "hola", "hello.mp3", "hello.jpg"),
                VocabularyItem("world", "mundo"),
                VocabularyItem("good", "bueno", "good.mp3")
            ]

            # Act
            repo.save_to_file(temp_path, items)

            # Assert - read back and verify
            loaded_items = repo.load_from_file(temp_path)
            assert len(loaded_items) == 3
            assert loaded_items[0].origin == "hello"
            assert loaded_items[0].sound == "hello.mp3"

        finally:
            os.unlink(temp_path)


# ========== ML Tests ==========

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


# ========== Audio Tests ==========

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


# ========== Dependency Injection Tests ==========

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
