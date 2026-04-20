# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""Tests for VocabularyItem entity."""

import pytest
from domain.entities.vocabulary_item import VocabularyItem


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
