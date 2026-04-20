# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for vocabulary use cases."""

import pytest
from unittest.mock import Mock

from domain.entities.vocabulary_item import VocabularyItem
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
