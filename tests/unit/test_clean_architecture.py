# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Example tests for the Clean Architecture implementation.
These tests demonstrate how to test each layer independently.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List

# Domain layer tests - Pure unit tests, no dependencies
from domain.entities.vocabulary_item import VocabularyItem
from domain.entities.user_settings import UserSettings


class TestVocabularyItem:
    """Test domain entity VocabularyItem."""

    def test_create_vocabulary_item(self):
        """Test creating a valid vocabulary item."""
        item = VocabularyItem(
            origin="hello",
            translation="hola",
            sound="hello.mp3",
            image="hello.jpg"
        )

        assert item.origin == "hello"
        assert item.translation == "hola"
        assert item.sound == "hello.mp3"
        assert item.image == "hello.jpg"

    def test_vocabulary_item_immutable(self):
        """Test that vocabulary items are immutable."""
        item = VocabularyItem("hello", "hola")

        with pytest.raises(Exception):  # FrozenInstanceError
            item.origin = "hi"

    def test_vocabulary_item_requires_origin(self):
        """Test that origin is required."""
        with pytest.raises(ValueError):
            VocabularyItem("", "hola")

    def test_vocabulary_item_requires_translation(self):
        """Test that translation is required."""
        with pytest.raises(ValueError):
            VocabularyItem("hello", "")

    def test_has_audio(self):
        """Test audio detection."""
        item_with_audio = VocabularyItem("hello", "hola", sound="hello.mp3")
        item_without_audio = VocabularyItem("hello", "hola")

        assert item_with_audio.has_audio() is True
        assert item_without_audio.has_audio() is False

    def test_has_image(self):
        """Test image detection."""
        item_with_image = VocabularyItem("hello", "hola", image="hello.jpg")
        item_without_image = VocabularyItem("hello", "hola")

        assert item_with_image.has_image() is True
        assert item_without_image.has_image() is False


class TestUserSettings:
    """Test domain entity UserSettings."""

    def test_create_user_settings(self):
        """Test creating user settings."""
        settings = UserSettings(
            interface_locale="EN",
            locale_from="EN",
            locale_to="ES"
        )

        assert settings.interface_locale == "EN"
        assert settings.locale_from == "EN"
        assert settings.locale_to == "ES"

    def test_has_locale_configured(self):
        """Test locale configuration check."""
        configured = UserSettings(interface_locale="EN")
        not_configured = UserSettings()

        assert configured.has_locale_configured() is True
        assert not_configured.has_locale_configured() is False

    def test_has_language_pair_configured(self):
        """Test language pair configuration check."""
        configured = UserSettings(locale_from="EN", locale_to="ES")
        partially_configured = UserSettings(locale_from="EN")
        not_configured = UserSettings()

        assert configured.has_language_pair_configured() is True
        assert partially_configured.has_language_pair_configured() is False
        assert not_configured.has_language_pair_configured() is False


# Use case tests - With mocked dependencies
from domain.use_cases.vocabulary_use_cases import LoadVocabularyUseCase, ShuffleVocabularyUseCase
from domain.repositories.vocabulary_repository import IVocabularyRepository


class TestLoadVocabularyUseCase:
    """Test LoadVocabularyUseCase with mocked repository."""

    def test_execute_loads_from_repository(self):
        """Test that use case delegates to repository."""
        # Arrange
        mock_repo = Mock(spec=IVocabularyRepository)
        test_items = [
            VocabularyItem("hello", "hola"),
            VocabularyItem("world", "mundo")
        ]
        mock_repo.load_from_file.return_value = test_items

        use_case = LoadVocabularyUseCase(mock_repo)

        # Act
        result = use_case.execute("test.txt")

        # Assert
        assert result == test_items
        mock_repo.load_from_file.assert_called_once_with("test.txt")


class TestShuffleVocabularyUseCase:
    """Test ShuffleVocabularyUseCase."""

    def test_execute_returns_shuffled_items(self):
        """Test that items are shuffled."""
        # Arrange
        items = [VocabularyItem(f"word{i}", f"palabra{i}") for i in range(100)]
        use_case = ShuffleVocabularyUseCase()

        # Act
        result = use_case.execute(items, limit=100)

        # Assert
        assert len(result) == 100
        assert set(result) == set(items)  # Same items, different order (likely)

    def test_execute_respects_limit(self):
        """Test that limit is respected."""
        items = [VocabularyItem(f"word{i}", f"palabra{i}") for i in range(100)]
        use_case = ShuffleVocabularyUseCase()

        result = use_case.execute(items, limit=25)

        assert len(result) == 25


# Service tests - Integration tests
from application.services.vocabulary_service import VocabularyService


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


# Repository tests - Test infrastructure implementations
from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository
import tempfile
import os


class TestFileVocabularyRepository:
    """Test file-based vocabulary repository."""

    def test_load_from_file(self):
        """Test loading vocabulary from file."""
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


# Tests for adapter pattern moved to legacy
# StoreControllerAdapter has been removed and replaced with direct service usage
# Original tests archived along with the adapter implementation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
