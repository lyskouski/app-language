# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for VocabularyService."""

import pytest
from unittest.mock import Mock

from domain.entities.vocabulary_item import VocabularyItem
from domain.repositories.vocabulary_repository import IVocabularyRepository
from domain.use_cases.vocabulary_use_cases import LoadVocabularyUseCase, ShuffleVocabularyUseCase
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
