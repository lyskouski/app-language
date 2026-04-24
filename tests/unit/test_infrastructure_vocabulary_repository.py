# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for SQLiteVocabularyRepository."""

import pytest

from domain.entities.vocabulary_item import VocabularyItem
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.persistence.sqlite_vocabulary_repository import SQLiteVocabularyRepository


class TestSQLiteVocabularyRepository:
    """Test SQLite-based vocabulary repository."""

    @pytest.fixture
    def db_connection(self, tmp_path):
        """Create a temporary database connection for testing."""
        db_path = str(tmp_path / "test_tlum.db")
        return DatabaseConnection(db_path)

    @pytest.fixture
    def repository(self, db_connection):
        """Create a repository instance for testing."""
        return SQLiteVocabularyRepository(db_connection)

    def test_load_by_language_pair(self, repository, db_connection):
        """Test loading vocabulary by language pair."""
        # Arrange - Insert test data
        items = [
            VocabularyItem("hello", "hola", "hello.mp3", "hello.jpg"),
            VocabularyItem("world", "mundo"),
            VocabularyItem("good", "bueno", "good.mp3")
        ]
        repository.save_vocabulary_items("EN", "ES", items)

        # Act
        loaded_items = repository.load_by_language_pair("EN", "ES")

        # Assert
        assert len(loaded_items) == 3
        assert loaded_items[0].origin == "hello"
        assert loaded_items[0].translation == "hola"
        assert loaded_items[0].sound == "hello.mp3"
        assert loaded_items[0].image == "hello.jpg"

        assert loaded_items[1].origin == "world"
        assert loaded_items[1].translation == "mundo"
        assert loaded_items[1].sound is None
        assert loaded_items[1].image is None

    def test_save_vocabulary_items(self, repository):
        """Test saving vocabulary items to database."""
        # Arrange
        items = [
            VocabularyItem("cat", "gato"),
            VocabularyItem("dog", "perro", "dog.mp3")
        ]

        # Act
        repository.save_vocabulary_items("EN", "ES", items)

        # Assert - reload and verify
        loaded_items = repository.load_by_language_pair("EN", "ES")
        assert len(loaded_items) == 2
        assert loaded_items[0].origin == "cat"
        assert loaded_items[1].origin == "dog"
        assert loaded_items[1].sound == "dog.mp3"

    def test_load_from_file_path(self, repository):
        """Test loading from file path (extracts locales from path)."""
        # Arrange - Save some items
        items = [VocabularyItem("test", "prueba")]
        repository.save_vocabulary_items("EN", "PL", items)

        # Act - Load using file path format
        loaded_items = repository.load_from_file("assets/data/PL/EN/store.txt")

        # Assert
        assert len(loaded_items) == 1
        assert loaded_items[0].origin == "test"

    def test_replace_existing_items(self, repository):
        """Test replacing existing vocabulary items."""
        # Arrange - Initial data
        initial_items = [
            VocabularyItem("old1", "viejo1"),
            VocabularyItem("old2", "viejo2")
        ]
        repository.save_vocabulary_items("EN", "ES", initial_items, replace=True)

        # Act - Replace with new data
        new_items = [VocabularyItem("new1", "nuevo1")]
        repository.save_vocabulary_items("EN", "ES", new_items, replace=True)

        # Assert
        loaded_items = repository.load_by_language_pair("EN", "ES")
        assert len(loaded_items) == 1
        assert loaded_items[0].origin == "new1"

    def test_load_file_with_malformed_path(self, repository):
        """Test loading from nonexistent path returns empty list."""
        items = repository.load_from_file("/nonexistent/path/file.txt")
        assert items == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
