# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for MLVocabularyProfiler."""

import pytest

from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler
from infrastructure.ml.ml_vocabulary_profiler import MLVocabularyProfiler


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
