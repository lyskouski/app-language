# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for FileVocabularyRepository."""

import pytest
import tempfile
import os

from domain.entities.vocabulary_item import VocabularyItem
from infrastructure.persistence.file_vocabulary_repository import FileVocabularyRepository


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

    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file returns empty list."""
        repo = FileVocabularyRepository()
        items = repo.load_from_file("/nonexistent/path/file.txt")

        assert items == []

    def test_load_file_with_malformed_lines(self):
        """Test loading file with malformed lines."""
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
