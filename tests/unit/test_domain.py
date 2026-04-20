# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Unit tests for Domain Layer.
Tests domain entities and use cases (core business logic).
"""

import pytest
from unittest.mock import Mock

from domain.entities.vocabulary_item import VocabularyItem
from domain.entities.user_settings import UserSettings
from domain.use_cases.vocabulary_use_cases import LoadVocabularyUseCase, ShuffleVocabularyUseCase
from domain.repositories.vocabulary_repository import IVocabularyRepository


# ========== Domain Entities Tests ==========

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


# ========== Domain Use Cases Tests ==========

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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
