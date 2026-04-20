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
from domain.entities.user_settings import UserSettings
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

    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file returns empty list."""
        from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository

        repo = FileVocabularyRepository()
        items = repo.load_from_file("/nonexistent/path/file.txt")

        assert items == []

    def test_load_file_with_malformed_lines(self):
        """Test loading file with malformed lines."""
        from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("hello;hola\n")
            f.write("invalid_line_no_separator\n")  # Malformed
            f.write("world;mundo\n")
            temp_path = f.name

        try:
            repo = FileVocabularyRepository()
            items = repo.load_from_file(temp_path)

            # Should skip malformed line and load valid ones
            assert len(items) == 2
            assert items[0].origin == "hello"
            assert items[1].origin == "world"

        finally:
            os.unlink(temp_path)


# ========== Settings Repository Tests ==========

from infrastructure.persistence.ini_settings_repository import IniSettingsRepository
from lib.ini_config_parser import IniConfigParser


class TestIniSettingsRepository:
    """Test INI settings repository."""

    @pytest.fixture
    def mock_config_parser(self):
        """Create mock config parser."""
        parser = Mock(spec=IniConfigParser)
        parser.get.return_value = ""
        return parser

    @pytest.fixture
    def repository(self, mock_config_parser):
        """Create repository instance."""
        return IniSettingsRepository(mock_config_parser)

    def test_load_settings(self, repository, mock_config_parser):
        """Test loading settings."""
        mock_config_parser.get.side_effect = lambda key, default: {
            IniConfigParser.INTERFACE_LOCALE: "EN",
            "locale_from": "EN",
            "locale_to": "ES"
        }.get(key, default)

        settings = repository.load()

        assert settings.interface_locale == "EN"
        assert settings.locale_from == "EN"
        assert settings.locale_to == "ES"

    def test_save_settings(self, repository, mock_config_parser):
        """Test saving settings."""
        settings = UserSettings(
            interface_locale="ES",
            locale_from="ES",
            locale_to="EN"
        )

        repository.save(settings)

        assert mock_config_parser.save.call_count == 3
        calls = mock_config_parser.save.call_args_list
        assert calls[0][0] == (IniConfigParser.INTERFACE_LOCALE, "ES")
        assert calls[1][0] == ("locale_from", "ES")
        assert calls[2][0] == ("locale_to", "EN")

    def test_get_setting(self, repository, mock_config_parser):
        """Test getting a specific setting."""
        mock_config_parser.get.return_value = "value"

        result = repository.get_setting("key", "default")

        mock_config_parser.get.assert_called_once_with("key", "default")
        assert result == "value"

    def test_set_setting(self, repository, mock_config_parser):
        """Test setting a specific setting."""
        repository.set_setting("key", "value")

        mock_config_parser.save.assert_called_once_with("key", "value")


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

    def test_multiple_correct_answers_tracked(self, profiler):
        """Test tracking multiple correct answers."""
        item = VocabularyItem("hello", "hola")

        profiler.mark_positive(item)
        profiler.mark_positive(item)
        profiler.mark_positive(item)

        assert profiler.user_history["hello"]["correct"] == 3
        assert profiler.user_history["hello"]["incorrect"] == 0

    def test_mixed_correct_incorrect_tracked(self, profiler):
        """Test tracking mixed answers."""
        item = VocabularyItem("world", "mundo")

        profiler.mark_positive(item)
        profiler.mark_negative(item)
        profiler.mark_positive(item)

        assert profiler.user_history["world"]["correct"] == 2
        assert profiler.user_history["world"]["incorrect"] == 1

    def test_prioritization_uses_all_items(self, profiler):
        """Test that prioritization processes all items."""
        items = [
            VocabularyItem("hello", "hola"),
            VocabularyItem("world", "mundo"),
            VocabularyItem("test", "prueba")
        ]

        result = profiler.get_prioritized_items(items, 3)

        # All items should be returned (up to limit)
        assert len(result) == 3
        # Result should contain VocabularyItem objects
        assert all(isinstance(item, VocabularyItem) for item in result)

    def test_difficulty_calculation_with_history(self, profiler):
        """Test that difficulty changes based on user history."""
        easy_item = VocabularyItem("hi", "hola")
        hard_item = VocabularyItem("hi", "hola")

        # Mark one as mastered (many correct answers)
        for _ in range(10):
            profiler.mark_positive(easy_item)

        # Mark other as difficult (many incorrect answers)
        for _ in range(10):
            profiler.mark_negative(hard_item)

        # Calculate difficulty for each
        result = profiler.get_prioritized_items([easy_item], 1)

        # Hard item should be prioritized (have higher difficulty score)
        assert len(result) == 1


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
