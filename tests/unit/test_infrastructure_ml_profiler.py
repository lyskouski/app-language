# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for SQLiteMLVocabularyProfiler."""

import pytest

from domain.entities.vocabulary_item import VocabularyItem
from domain.services import IVocabularyProfiler
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.persistence.sqlite_vocabulary_repository import SQLiteVocabularyRepository
from infrastructure.ml.sqlite_ml_vocabulary_profiler import SQLiteMLVocabularyProfiler


class TestMLVocabularyProfiler:
    """Test SQLite ML vocabulary profiler implementation."""

    @pytest.fixture
    def db_connection(self, tmp_path):
        """Create a temporary database connection for testing."""
        db_path = str(tmp_path / "test_profiler.db")
        return DatabaseConnection(db_path)
    
    @pytest.fixture
    def repository(self, db_connection):
        """Create vocabulary repository for test data."""
        return SQLiteVocabularyRepository(db_connection)

    @pytest.fixture
    def profiler(self, db_connection, repository):
        """Create a profiler instance for testing."""
        # Setup test vocabulary data
        items = [
            VocabularyItem("hello", "hola"),
            VocabularyItem("world", "mundo"),
            VocabularyItem("pharmaceutical", "farmacéutico")
        ]
        repository.save_vocabulary_items("EN", "ES", items)
        
        return SQLiteMLVocabularyProfiler(db_connection, "EN", "ES")

    def test_implements_interface(self, profiler):
        """Test that profiler implements IVocabularyProfiler."""
        assert isinstance(profiler, IVocabularyProfiler)

    def test_mark_positive(self, profiler):
        """Test marking an item as correctly answered."""
        item = VocabularyItem("hello", "hola")

        profiler.mark_positive(item)

        # Verify in database
        score = profiler._get_history_score("hello")
        assert score < 0.5  # Low score indicates good performance

    def test_mark_negative(self, profiler):
        """Test marking an item as incorrectly answered."""
        item = VocabularyItem("world", "mundo")

        profiler.mark_negative(item)

        # Verify in database
        score = profiler._get_history_score("world")
        assert score > 0.5  # High score indicates difficulty

    def test_get_prioritized_items_empty_list(self, profiler):
        """Test prioritization with empty list."""
        items = []
        result = profiler.get_prioritized_items(items, 10)

        assert result == []

    def test_get_prioritized_items_respects_limit(self, profiler, repository):
        """Test that prioritization respects the limit."""
        items = [
            VocabularyItem(f"word{i}", f"palabra{i}")
            for i in range(50)
        ]
        repository.save_vocabulary_items("EN", "ES", items, replace=False)

        result = profiler.get_prioritized_items(items, 10)

        assert len(result) <= 10

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

    def test_multiple_correct_answers_tracked(self, profiler, db_connection):
        """Test tracking multiple correct answers."""
        item = VocabularyItem("hello", "hola")

        profiler.mark_positive(item)
        profiler.mark_positive(item)
        profiler.mark_positive(item)

        # Verify in database
        row = db_connection.fetchone(
            """SELECT correct_count, incorrect_count 
               FROM learning_progress lp
               JOIN vocabulary_items v ON lp.vocabulary_item_id = v.id
               WHERE v.origin = 'hello'"""
        )
        assert row is not None
        assert row['correct_count'] == 3
        assert row['incorrect_count'] == 0

    def test_mixed_correct_incorrect_tracked(self, profiler, db_connection):
        """Test tracking mixed answers."""
        item = VocabularyItem("world", "mundo")

        profiler.mark_positive(item)
        profiler.mark_negative(item)
        profiler.mark_positive(item)

        # Verify in database
        row = db_connection.fetchone(
            """SELECT correct_count, incorrect_count 
               FROM learning_progress lp
               JOIN vocabulary_items v ON lp.vocabulary_item_id = v.id
               WHERE v.origin = 'world'"""
        )
        assert row is not None
        assert row['correct_count'] == 2
        assert row['incorrect_count'] == 1

    def test_prioritization_uses_all_items(self, profiler):
        """Test that prioritization processes all items."""
        items = [
            VocabularyItem("hello", "hola"),
            VocabularyItem("world", "mundo"),
            VocabularyItem("pharmaceutical", "farmacéutico")
        ]

        result = profiler.get_prioritized_items(items, 3)

        # All items should be returned (up to limit)
        assert len(result) == 3
        # Result should contain VocabularyItem objects
        assert all(isinstance(item, VocabularyItem) for item in result)

    def test_difficulty_calculation_with_history(self, profiler):
        """Test that difficulty changes based on user history."""
        easy_item = VocabularyItem("hello", "hola")

        # Mark as mastered (many correct answers)
        for _ in range(10):
            profiler.mark_positive(easy_item)

        # Check difficulty score decreased
        difficulty = profiler._get_history_score("hello")
        assert difficulty < 0.2  # Should be very low for mastered words


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
